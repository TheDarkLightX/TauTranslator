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

    # Use provider to generate a TCE-like candidate from the prompt
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

    tce = _sanitize_to_tce(raw, body.prompt)
    # Minimal repair rules
    if ':' in tce:
        tce = tce.replace(':', ' ')
    if not tce.endswith(')') and 'always (' in tce:
        tce = tce + ')'
    reasons = []
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
        success=tau is not None or not reasons,
        tce=tce,
        tau=tau,
        reasons=reasons,
        provenance={"mode": body.mode, "grammar_id": body.grammar_id, "version": body.grammar_version, "retrieval": top}
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

    explanation = _explain_spec_text(body.spec_text, body.spec_type)
    return SpecToPromptResponse(success=True, explanation=explanation, provenance={"spec_type": body.spec_type})


