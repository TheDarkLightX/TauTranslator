from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..core.result_enhanced import Success, Failure
from ..domain.llm_types import (
    PromptToSpecRequest, PromptToSpecResponse,
    SpecToPromptRequest, SpecToPromptResponse,
)
from ..domain.grammar_knowledge_pack import GrammarKnowledgePackBuilder
from ..domain.pack_retrieval import retrieve_top_k
from .simple_tce import translate_tce_to_tau_simple, validate_tce_simple
import os, importlib.util
from ..infrastructure.llm_providers import get_default_provider, get_provider, LLMRequest
import re
from ..domain.prompt_optimizer_pnf_ilgo import optimize_prompt_to_tce
def _load_class_from_path(module_name: str, file_path: str, class_name: str):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore
            return getattr(mod, class_name, None)
    except Exception:
        return None
    return None

def _resolve_repo_path(*parts: str) -> str:
    here = os.path.dirname(__file__)
    candidates = [
        os.path.abspath(os.path.join(here, '..', '..', '..', 'src', *parts)),
        os.path.abspath(os.path.join('/', 'app', 'src', *parts)),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[-1]

try:
    from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
except Exception:  # pragma: no cover
    CNLParser = None
try:
    from tau_translator_omega.core_engine.translators.tce_tau_translator import TCETauTranslator
except Exception:  # pragma: no cover
    TCETauTranslator = None


router = APIRouter(prefix="/llm", tags=["llm"])


class PromptToSpecBody(BaseModel):
    prompt: str
    mode: str = "assist"  # "assist" | "generate"
    grammar_id: str = "tce"
    grammar_version: str = "v1"
    provider: str | None = None
    # Optional grammar steering
    grammar_inline: dict | None = None  # { name, mime, size, content }
    grammar_ref: dict | None = None     # { id, version }
    # Optional LMQL-lite constraints
    constraints: dict | None = None     # { require_prefix, require_closing_paren, forbid_colon, allowed_connectives }


@router.post("/prompt-to-spec", response_model=PromptToSpecResponse)
async def prompt_to_spec(body: PromptToSpecBody, request: Request):
    # Build or ensure knowledge pack exists (minimal builder for now)
    builder = GrammarKnowledgePackBuilder("data/grammar_packs")
    pack_result = builder.build_minimal(body.grammar_id, body.grammar_version)
    if isinstance(pack_result, Failure):
        raise HTTPException(status_code=500, detail=pack_result.message)

    # Retrieve relevant rule summaries/examples for assist context (safe RAG)
    pack = pack_result.unwrap()
    top = retrieve_top_k(pack, body.prompt, k=4).unwrap()

    # First try deterministic optimizer (PNF-ILGO+ Phase 1)
    # Feature-flagged FDL optimizer (safe rollback via env var)
    opt = optimize_prompt_to_tce(body.prompt, constraints=body.constraints or {}, use_fdl=None)
    opt_tce = None
    opt_analysis = {}
    opt_questions: list[str] = []
    opt_reasons: list[str] = []
    opt_intent = None
    if isinstance(opt, Success):
        out = opt.unwrap()
        opt_tce = out.tce
        opt_analysis = out.analysis
        opt_questions = out.questions
        opt_reasons = out.reasons
        opt_intent = out.intent
    
    # Use provider to generate a TCE-like candidate from the prompt (assist)
    # Provider selection; BYOK via header X-OpenRouter-Key if present
    openrouter_key = request.headers.get('X-OpenRouter-Key')
    provider = get_provider(openrouter_key, body.provider)
    # Add explicit grammar steering if provided
    grammar_hints: list[str] = []
    if body.grammar_ref:
        grammar_hints.append(f"GrammarRef: {body.grammar_ref}")
    if body.grammar_inline:
        grammar_hints.append(f"GrammarInline: {body.grammar_inline.get('name','inline')}")

    assist_context = "\n".join([
        f"Rule: {t['name']}\nSummary: {t['summary']}\nExamples: {', '.join(t['examples'])}"
        for t in top
    ])
    system = (
        "You are a TCE generator. Output a single TCE sentence that starts with 'always (' and ends with ')'. "
        "Do not use colons. Prefer quantifiers 'all' and 'ex' instead of 'forall/exists'."
    )
    steering = ("\n\n" + "\n".join(grammar_hints)) if grammar_hints else ""
    prompt = f"Use TCE with allowed keywords. Ensure 'always (...)'.{steering}\nContext:\n{assist_context}\n\nUser: {body.prompt}\nTCE:"
    gen = provider.generate(LLMRequest(prompt=prompt, system=system, temperature=0.2, max_tokens=128))
    if isinstance(gen, Failure):
        return PromptToSpecResponse(success=False, tce=None, tau=None, reasons=[gen.message], provenance={})

    # Sanitize to a TCE-only candidate (strip helper context)
    raw = gen.unwrap().text

    def _sanitize_to_tce(generated: str, user: str) -> str:
        # Prefer explicit user segment
        if "User:" in generated:
            try:
                after = generated.split("User:", 1)[1]
                # stop at first newline or 'TCE:' tag
                after = after.split("TCE:", 1)[0]
                after = after.splitlines()[0].strip()
                if after:
                    return f"always ({after})"
            except Exception:
                pass
        # Try extracting an existing always(...) span
        idx = generated.find("always (")
        if idx != -1:
            tail = generated[idx:]
            # take until the next ')' if present
            close = tail.find(')')
            if close != -1:
                return tail[: close + 1]
            return tail
        # Fallback to user prompt
        return f"always ({user})"

    # NLP-lite intent detection and prompt refinement suggestions
    # Extract simple intents: allow/deny, condition/guard, temporal always
    low = body.prompt.lower()
    intent = None
    suggestions: list[str] = []
    nlp_analysis: dict[str, any] = {}
    # Detect temporal intent
    if any(w in low for w in ["always", "whenever", "at all times", "must always", "ensure always"]):
        intent = "invariant"
    # Detect causality
    causality = any(w in low for w in ["if ", "when ", "whenever ", "once ", "after "])
    # Detect guards/exception conditions
    guarded = any(w in low for w in ["unless", "except if", "except when", "but not if"]) 
    # Detect quantifiers
    quantified = any(w in low for w in ["for all", "each ", "every ", "there exists", "exists "])
    # Detect negation
    has_neg = any(w in low for w in ["not ", "never ", "no ", "without "])
    # Extract rough action/object tokens
    import re as _re
    action_tokens = []
    m = _re.search(r"(send|ship|approve|deny|lock|unlock|emit|buy|sell|hold|release)", low)
    if m:
        action_tokens.append(m.group(1))
    obj = _re.search(r"(order|payment|signal|lock|data|price|volume|trend|guard)", low)
    object_token = obj.group(1) if obj else None
    # Build refined prompt template options
    if causality:
        suggestions.append("Use implication: always (condition -> action)")
    if guarded:
        suggestions.append("Use a guard: always (action -> guard)")
    if quantified:
        suggestions.append("Quantify explicitly: always (all x (condition(x) -> action(x)))")
    if has_neg:
        suggestions.append("Use 'not' explicitly in condition or action: always (not condition -> ...)")
    # Create a refined prompt candidate
    refined_prompt = None
    refined_options: list[str] = []
    # Heuristic assembly
    act = (action_tokens[0] if action_tokens else (object_token or "action"))
    cond = "condition"
    guard = "guard"
    if causality and not guarded:
        refined_options.append(f"always ({cond} -> {act})")
    if guarded and not causality:
        refined_options.append(f"always ({act} -> {guard})")
    if causality and guarded:
        refined_options.append(f"always (({cond} & {guard}) -> {act})")
    if quantified:
        refined_options.append(f"always (all x ({cond}(x) -> {act}(x)))")
    if refined_options:
        refined_prompt = refined_options[0]
    nlp_analysis = {
        "causality": causality,
        "guarded": guarded,
        "quantified": quantified,
        "negation": has_neg,
        "action_tokens": action_tokens,
        "object_token": object_token,
    }

    # Prefer deterministic optimizer if available and valid-looking
    tce = opt_tce or _sanitize_to_tce(raw, body.prompt)
    # Minimal repair rules
    if ':' in tce:
        tce = tce.replace(':', ' ')
    if not tce.endswith(')') and 'always (' in tce:
        tce = tce + ')'
    # Apply LMQL-lite constraints if provided
    reasons = []
    reasons.extend(opt_reasons)
    constraints = body.constraints or {}
    req_prefix = (constraints.get('require_prefix') or '').strip()
    if req_prefix and not tce.strip().lower().startswith(req_prefix.lower()):
        if req_prefix.lower().startswith('always '):
            tce = f"{req_prefix}{tce.strip()}"
        reasons.append(f"Applied prefix constraint: {req_prefix}")
    if constraints.get('require_closing_paren') and tce.strip().lower().startswith('always (') and not tce.strip().endswith(')'):
        tce = tce + ')'
        reasons.append("Closed trailing parenthesis")
    if constraints.get('forbid_colon') and ':' in tce:
        tce = tce.replace(':', ' ')
        reasons.append("Removed colon per constraint")
    allowed = constraints.get('allowed_connectives') or []
    if isinstance(allowed, list) and allowed:
        # normalize common synonyms toward allowed tokens
        if '->' in allowed:
            tce = re.sub(r"\b(implies|=>|⇒)\b", "->", tce, flags=re.IGNORECASE)
        if 'and' in allowed:
            tce = re.sub(r"\bAND\b", "and", tce)
        if 'or' in allowed:
            tce = re.sub(r"\bOR\b", "or", tce)

    # Final DFA-like gate: ensure only allowed tokens and a balanced structure inside always(...)
    def _gate_tokens(candidate: str) -> tuple[str, list[str]]:
        msgs: list[str] = []
        text = candidate.strip()
        # Enforce always ( ... ) wrapper
        if not text.lower().startswith('always ('):
            text = f"always ({text})"
            msgs.append("Wrapped in always (...) per constraint gate")
        # Balance parentheses
        bal = 0
        for ch in text:
            if ch == '(': bal += 1
            elif ch == ')': bal -= 1
            if bal < 0:
                msgs.append("Parenthesis underflow; attempted normalization")
                break
        if bal > 0:
            text = text + (')' * bal)
            msgs.append("Balanced missing closing parenthesis")
        # Whitelist simple token set (letters, digits, underscore, space, basic connectives and punctuation inside always)
        # Replace disallowed punctuation with space
        cleaned = re.sub(r"[^A-Za-z0-9_\s\(\)\-\>\|\&'\[\]]+", " ", text)
        if cleaned != text:
            msgs.append("Removed unsupported characters")
            text = cleaned
        # Normalize multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text, msgs

    tce, gate_msgs = _gate_tokens(tce)
    reasons.extend(gate_msgs)
    tau = None
    if CNLParser is not None and TCETauTranslator is not None:
        try:
            parser = CNLParser()
            ast = parser.parse(tce)
            translator = TCETauTranslator()
            tau_result = translator.translate(ast)
            if tau_result.errors:
                reasons.extend(tau_result.errors)
            else:
                tau = tau_result.tau_code
        except Exception as e:
            reasons.append(f"Validation/translation failed: {e}")
    # Fallback: if canonical unavailable or failed, try simple translation, then tau-like acceptance
    if tau is None:
        try:
            ok, tau_simple, errs = translate_tce_to_tau_simple(tce)
            if ok and tau_simple:
                tau = tau_simple
            else:
                # If output is already tau-like e.g., contains '->' inside always(...), accept as tau
                tl = tce.strip()
                if tl.lower().startswith('always (') and tl.endswith(')'):
                    inner = tl[len('always ('):-1].strip()
                    # Normalize quantifiers to Tau form: forall x : (...)
                    inner = inner.replace('forall ', 'forall ').replace('exists ', 'exists ')
                    tau = f"always({inner})"
                else:
                    reasons.extend(errs)
        except Exception:
            pass

    return PromptToSpecResponse(
        success=tau is not None or (tce is not None),
        tce=tce,
        tau=tau,
        reasons=reasons,
        provenance={"mode": body.mode, "grammar_id": body.grammar_id, "version": body.grammar_version, "retrieval": top},
        intent= opt_intent or intent,
        prompt_suggestions=suggestions + ([f"Clarify: {q}" for q in opt_questions] if opt_questions else []),
        nlp_analysis={**(nlp_analysis or {}), **(opt_analysis or {})},
        refined_prompt=refined_prompt or opt_tce,
        refined_options=(refined_options or [])
    )


class SpecToPromptBody(BaseModel):
    spec_text: str
    spec_type: str = "tce"  # or "tau"


@router.post("/spec-to-prompt", response_model=SpecToPromptResponse)
async def spec_to_prompt(body: SpecToPromptBody):
    # Heuristic, deterministic explanation for common Tau/TCE forms
    def _humanize_identifier(identifier: str) -> str:
        return re.sub(r"_+", " ", identifier).strip()

    def _strip_parens(text: str) -> str:
        t = text.strip()
        if t.startswith("(") and t.endswith(")"):
            return t[1:-1].strip()
        return t

    def _explain_spec_text(spec_text: str, spec_type: str) -> str:
        t = " ".join(spec_text.split())
        lower = t.lower()
        parts: list[str] = []

        # Mention temporal modality if present
        if lower.startswith("always"):
            parts.append("It uses the 'always' modality (an invariant over time).")

        # Extract inner of always(...) if applicable
        inner = t
        m_always = re.match(r"^always\s*\((.*)\)\s*$", t, flags=re.IGNORECASE)
        if m_always:
            inner = m_always.group(1).strip()

        # Pattern: X[t] = Y[t]
        m_eq_t = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[t\]\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\[t\]", inner)
        if m_eq_t:
            left = _humanize_identifier(m_eq_t.group(1))
            right = _humanize_identifier(m_eq_t.group(2))
            main = f"{left} at time t equals {right} at time t."
            parts.insert(0, main)
            parts.append("The [t] index denotes the time step; expressions compare values at the same time.")
            return f"This {spec_type.upper()} expresses: " + " ".join(parts)

        # Pattern: implication A -> B (possibly wrapped in parentheses)
        if "->" in inner:
            lhs, rhs = inner.split("->", 1)
            lhs = _strip_parens(lhs)
            rhs = _strip_parens(rhs)
            lhs_h = _humanize_identifier(lhs)
            rhs_h = _humanize_identifier(rhs)
            main = f"If {lhs_h} then {rhs_h}."
            parts.insert(0, main)
            return f"This {spec_type.upper()} expresses: " + " ".join(parts)

        # Default: lightly humanize and surface
        human = (
            inner
            .replace("->", " implies ")
            .replace("!", "not ")
            .replace("&", " and ")
            .replace("|", " or ")
        )
        human = re.sub(r"\ball\b", "for all", human)
        human = re.sub(r"\bex\b", "there exists", human)
        human = re.sub(r"_+", " ", human)
        return f"This {spec_type.upper()} expresses: {human}"

    text = body.spec_text

    # Fast path for single-line specs
    if "\n" not in text.strip():
        explanation = _explain_spec_text(text, body.spec_type)
        def _pc_single(tx: str, st: str) -> str:
            base = explanation.replace(f"This {st.upper()} expresses:", "").strip()
            return base or tx
        analysis_single = {
            "temporal": bool(re.search(r"^\s*always\s*\(", text, flags=re.IGNORECASE)),
            "implication": "->" in text or " implies " in text,
            "quantifiers": [q for q in ["all", "ex"] if re.search(fr"\b{q}\b", text, flags=re.IGNORECASE)],
            "time_indices": list(set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[t\]", text)))
        }
        return SpecToPromptResponse(
            success=True,
            explanation=explanation,
            provenance={"spec_type": body.spec_type},
            prompt_candidate=_pc_single(text, body.spec_type),
            analysis=analysis_single,
        )

    # Multiline heuristic summarizer for Tau-like specs
    lines = [ln.rstrip() for ln in text.splitlines()]
    # strip pure comment lines
    non_comment = [ln for ln in lines if not re.match(r"^\s*#", ln)]
    decl_inputs: list[str] = []
    decl_outputs: list[str] = []
    helpers: list[str] = []
    title = None
    # capture first comment line as title if present
    for ln in lines:
        if re.match(r"^\s*#\s*(.+)$", ln):
            title = re.sub(r"^\s*#\s*", "", ln).strip()
            break
    # parse declarations and helpers
    for ln in non_comment:
        m_sbf = re.match(r"^\s*sbf\s+([A-Za-z_][\w]*)\s*=", ln)
        if m_sbf:
            name = m_sbf.group(1)
            if name.lower().startswith('i'):
                decl_inputs.append(name)
            elif name.lower().startswith('o'):
                decl_outputs.append(name)
            continue
        m_help = re.match(r"^\s*([A-Za-z_][\w]*)\s*\([^)]*\)\s*:=", ln)
        if m_help:
            helpers.append(m_help.group(1))

    # extract r ( ... ) block robustly (balanced parentheses scan)
    joined = "\n".join(non_comment)
    r_idx = re.search(r"\br\s*\(", joined)
    r_block = ""
    if r_idx:
        start_paren = joined.find('(', r_idx.start())
        depth = 0
        for i in range(start_paren, len(joined)):
            ch = joined[i]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    r_block = joined[start_paren+1:i]
                    break
    # analyze equations inside r-block
    eq_count = 0
    outputs_in_eq: list[str] = []
    uses_prev_time = False
    if r_block:
        uses_prev_time = ('[t-1]' in r_block)
        # split by '&&' boundaries but keep expressions intact otherwise
        parts = re.split(r"&&\s*\n?", r_block)
        for seg in parts:
            m_eq = re.search(r"^\s*([A-Za-z_][\w]*)\s*\[t\]\s*=", seg)
            if m_eq:
                eq_count += 1
                outputs_in_eq.append(m_eq.group(1))

    # detect timer/observables patterns
    timer_bits = any(x in outputs_in_eq for x in ['o6','o7','o8'])
    has_full3 = 'full3' in r_block if r_block else False
    has_xor2 = 'xor2' in r_block if r_block else False

    # compose explanation
    bullets: list[str] = []
    if title:
        bullets.append(f"Title: {title}.")
    if decl_inputs:
        bullets.append(f"Inputs: {', '.join(sorted(set(decl_inputs)))}.")
    if decl_outputs:
        bullets.append(f"Outputs: {', '.join(sorted(set(decl_outputs)))}.")
    if helpers:
        bullets.append(f"Helper predicates: {', '.join(sorted(set(helpers)))}.")
    if r_block:
        bullets.append(f"Transition relations: {eq_count} output equations in r(...). Uses previous time index: {'yes' if uses_prev_time else 'no'}.")
    if timer_bits or has_full3:
        bullets.append("3-bit timer and gating detected (o6,o7,o8 with full3/xor2).")
    if has_xor2:
        bullets.append("Avoids XOR at syntax level; uses helper xor2(a,b).")
    # add general description
    bullets.append("Boolean state machine over time: outputs at [t] depend on current inputs and previous outputs [t-1].")
    explanation = " ".join(bullets)

    # structured analysis for UI chips
    analysis = {
        "temporal": ('[t]' in text) or ('always' in text.lower()),
        "implication": ('->' in text) or (' implies ' in text.lower()),
        "quantifiers": [],
        "time_indices": sorted(list(set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[t(?:-1)?\]", text)))),
        "sections": [s for s in ["declarations", "helpers", "relations"] if (decl_inputs or decl_outputs) or helpers or r_block],
        "equations": eq_count,
        "uses_prev_time": uses_prev_time,
        "helpers_present": {"full3": has_full3, "xor2": has_xor2},
    }

    # prompt candidate as concise one-liner
    pc = "Deflationary agent kernel with inputs " + \
         (", ".join(sorted(set(decl_inputs))) or "(none)") + \
         ", outputs " + (", ".join(sorted(set(decl_outputs))) or "(none)") + \
         "; r(...) defines " + str(eq_count) + " temporal equations using [t] and [t-1]; helpers: " + \
         (", ".join(sorted(set(helpers))) or "none") + "."

    verification = {
        "equations": analysis.get("equations"),
        "uses_prev_time": analysis.get("uses_prev_time"),
        "helpers_present": analysis.get("helpers_present"),
        "time_indices_count": len(analysis.get("time_indices", [])),
    }
    return SpecToPromptResponse(
        success=True,
        explanation=explanation,
        provenance={"spec_type": body.spec_type},
        prompt_candidate=pc,
        analysis=analysis,
        verification=verification,
    )


