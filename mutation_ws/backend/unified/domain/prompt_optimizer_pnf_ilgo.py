from __future__ import annotations

"""
PNF‑ILGO+ (Prompt Normal Form with Intent Lattice and Guarded Operators)
Experimental prompt optimizer to project ambiguous English prompts into
Tau Controlled English (TCE) deterministically.

This module is intentionally lightweight and self‑contained so it can run
client‑first or server‑side without heavy dependencies. It follows Railway
Oriented Programming (ROP) via Success/Failure and never raises on common
inputs.

Algorithm sketch implemented here (Phase 1):
- FST normalizer for operators/conditionals
- Typed pattern extractor for condition/action/guard/quantifiers/temporal
- Discrete intent lattice with a simple ambiguity score
- Constraint projection to TCE schema (always (...), allowed connectives)
- Minimal‑edit synthesis and token gate

Future phases (planned): version‑space clarification, operator‑tree
weighted edit distance, TF.js reranker (client), and canonical parser
validation.
"""

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..core.result_enhanced import Success, Failure, Result
from .gs_ir import build_from_features as gs_build_from_features, to_tce as gs_to_tce
from .nlp_syntax import extract_roles
from .alignment_cache import alignment_cache
from .fca import FormalContext
from .lattice import (
    ILGOBasis,
    build_default_basis,
    encode_bitset,
    decode_bitset,
    glb_with_constraints,
    lub,
)


@dataclass
class OptimizerOutput:
    """Deterministic output of the optimizer.

    Attributes:
        tce: Synthesized Tau Controlled English sentence (always (...)).
        prompt_candidate: A concise, normalized candidate prompt (same as tce).
        intent: One of {invariant, causal, equivalence, temporal} if detected.
        guards: Optional list of guard identifiers.
        quantifiers: Optional list like ["all x"], ["ex y"].
        temporal: Optional time hints (e.g., "[t]", "[t-1]").
        reasons: Human‑readable notes about transformations.
        analysis: Structured dict for UI and audits.
        questions: Suggested clarifying questions if ambiguity remains.
        ambiguity: Float in [0,1] estimating remaining ambiguity.
    """

    tce: str
    prompt_candidate: str
    intent: Optional[str]
    guards: List[str]
    quantifiers: List[str]
    temporal: List[str]
    reasons: List[str]
    analysis: Dict[str, Any]
    questions: List[str]
    ambiguity: float


_FST_REPLACEMENTS: Tuple[Tuple[re.Pattern, str], ...] = (
    # normalize conditionals and operators
    (re.compile(r"\biff\b", re.I), "if"),
    (re.compile(r"\bimplies\b|=>|⇒", re.I), "->"),
    (re.compile(r"\band\b|\&\&", re.I), "and"),
    (re.compile(r"\bor\b|\|\|", re.I), "or"),
    (re.compile(r"\bnot\b|!", re.I), "not"),
    (re.compile(r"\bforall\b", re.I), "all"),
    (re.compile(r"\bexists\b", re.I), "ex"),
)


def _slugify_phrase(text: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", text.lower())
    stop = {"the","a","an","to","and","or","of","for","in","on","over","under","with","without","if","then","when","whenever"}
    kept = [t for t in tokens if t not in stop]
    return "_".join(kept) or "predicate"


def _aligned_predicate_or_slug(phrase: str) -> str:
    aligned = alignment_cache.suggest_predicate(phrase)
    return aligned or _slugify_phrase(phrase)


def _fst_normalize(text: str) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    s = text
    for pat, repl in _FST_REPLACEMENTS:
        new = pat.sub(repl, s)
        if new != s:
            reasons.append(f"Normalized pattern to '{repl}'")
            s = new
    # strip trailing punctuation that can confuse synthesis
    new = s.strip().rstrip('.')
    if new != s:
        reasons.append("Trimmed trailing punctuation")
        s = new
    # remove filler polite tokens that can distort structure
    s2 = re.sub(r"\b(please|now|strictly)\b", " ", s, flags=re.I)
    s2 = re.sub(r"\b(ensure\s+that|make\s+sure\s+to)\b", " ", s2, flags=re.I)
    if s2 != s:
        reasons.append("Removed filler tokens (please/now/strictly/...)")
        s = s2
    return s, reasons


def _extract_typed(text: str) -> Dict[str, Any]:
    """Typed feature extraction using patterns; deterministic and permissive.

    Returns keys: intent, condition, action, guards, quantifiers, temporal.
    """
    low = text.lower()
    intent: Optional[str] = None
    guards: List[str] = []
    quantifiers: List[str] = []
    temporal: List[str] = []
    negate = False

    # intent detection
    has_always = re.search(r"\balways\b|\bat all times\b|\bmust always\b", low) is not None
    has_causal = re.search(r"\bif\b|\bwhen\b|\bwhenever\b|\bonce\b|\bafter\b", low) is not None
    has_equiv = re.search(r"\biff\b|\bequivalent\b|\bif and only if\b", low) is not None
    if has_causal:
        intent = "causal"
    elif has_equiv:
        intent = "equivalence"
    elif has_always:
        intent = "invariant"
    global_negate = False
    if re.search(r"\bnever\b|\bmust not\b|\bcannot\b|\bcan\s*not\b|\bcan't\b", low):
        intent = intent or "invariant"; negate = True; global_negate = True
    # Soft negation phrases that may require scope clarification
    soft_neg = re.search(r"\bdo not\b|\bdon't\b|\bshould not\b|\bshall not\b", low) is not None
    if soft_neg and not negate:
        negate = True

    # condition/action extraction (very shallow)
    # if X then Y / when X, Y  → condition=X action=Y
    cond, act = None, None
    m_if = re.search(r"\bif\s+(.+?)\s+(then\s+)?(.+)$", low)
    if m_if:
        cond = m_if.group(1).strip(', .')
        act = m_if.group(3).strip()
    else:
        # causal phrasing "when X, Y" or "whenever X, Y"
        m_when = re.search(r"\bwhen\s+(.+?),\s*(.+)$", low)
        if m_when:
            cond = m_when.group(1).strip()
            act = m_when.group(2).strip()

    # unless/except guards
    for gpat in [r"unless\s+([A-Za-z_][\w]*)", r"except\s+(if|when)\s+([A-Za-z_][\w]*)"]:
        mg = re.search(gpat, low)
        if mg:
            guard = mg.groups()[-1]
            guards.append(guard)

    # quantifiers (simple forms)
    if re.search(r"\bfor all\b|\beach\b|\bevery\b|\ball\b", low):
        quantifiers.append("all x")
    if re.search(r"\bthere exists\b|\bexists\b|\bex\b", low):
        quantifiers.append("ex x")

    # temporal cues
    if re.search(r"\bnext\b|\b[tT]\+1\b|\bafter\b", low):
        temporal.append("[t+1]")
    if re.search(r"\bprevious\b|\b[tT]-1\b|\bbefore\b", low):
        temporal.append("[t-1]")

    # domain phrase mapping for privacy/security example
    action_phrase = None
    if re.search(r"\bsend\b.*\bnetwork\b|\btransmit\b.*\bnetwork\b|\bshare\b.*\bnetwork\b", low):
        action_phrase = "send data over the network"

    return {
        "intent": intent,
        "condition": cond,
        "action": act or (action_phrase and _slugify_phrase(action_phrase)) or None,
        "guards": guards,
        "quantifiers": quantifiers,
        "temporal": temporal,
        "negate": negate,
        "global_negate": global_negate,
        "soft_negation": soft_neg,
    }


def _project_to_tce(features: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Project features to a normalized TCE template."""
    reasons: List[str] = []
    cond_raw = features.get("condition") or "condition"
    act_raw = features.get("action") or features.get("predicate") or "action"
    # strip filler polite tokens from phrases
    cond_raw = re.sub(r"\b(please|now|strictly)\b", " ", cond_raw, flags=re.I)
    cond_raw = re.sub(r"\b(ensure\s+that|make\s+sure\s+to)\b", " ", cond_raw, flags=re.I)
    act_raw = re.sub(r"\b(please|now|strictly)\b", " ", act_raw, flags=re.I)
    act_raw = re.sub(r"\b(ensure\s+that|make\s+sure\s+to)\b", " ", act_raw, flags=re.I)
    negate = bool(features.get("negate"))
    # Remove negation words from action phrase to avoid double negation in English
    if negate:
        act_raw = re.sub(r"\b(must not|do not|don't|cannot|can not|can't|never|at no time|under no circumstances|should not|shall not)\b\s*", "", act_raw, flags=re.IGNORECASE).strip()
    # Slugify phrases to canonical predicate symbols for Tau/TCE emission
    cond_sym = _aligned_predicate_or_slug(cond_raw)
    act_sym = _aligned_predicate_or_slug(act_raw)
    guards: List[str] = features.get("guards") or []
    quant: List[str] = features.get("quantifiers") or []

    body = None
    # Choose a canonical action term; default to unary arity for generality
    act_term = act_sym
    if not re.search(r"\(", act_term):
        act_term = f"{act_sym}(x)"
    if features.get("intent") == "equivalence":
        body = f"({cond_sym}(x) -> {act_term}) and ({act_term} -> {cond_sym}(x))"
        reasons.append("Equivalence decomposed to implication pair")
    elif features.get("intent") == "causal":
        # In causal form, keep condition as-is and use canonical action term
        body = f"{cond_sym}(x) -> {act_term}"
    else:
        # default invariant form
        body = f"{act_term}"
        if negate:
            body = f"not {act_term}"
            reasons.append("Detected negation from prompt (never/cannot)")

    # apply guard as conjunction in antecedent when causal
    if guards:
        g = " and ".join(_slugify_phrase(g) for g in guards)
        if "->" in body:
            lhs, rhs = body.split("->", 1)
            body = f"({lhs.strip()} and not {g}) -> {rhs.strip()}"
            reasons.append("Applied guard as negative condition")
        else:
            body = f"({g} -> {body})"
            reasons.append("Applied guard implication around action")

    # add quantifier wrapper if detected or inferred
    qprefix = None
    for q in quant:
        if q.startswith("all"):
            qprefix = "all x"
            break
        if q.startswith("ex"):
            qprefix = "ex x"
    # If negation applies to an action without an explicit condition/quantifiers, infer 'all x'
    if not qprefix and negate and not features.get("condition"):
        qprefix = "all x"
        reasons.append("Added implicit quantifier: all x")
    if qprefix:
        body = f"{qprefix} ({body})"
        reasons.append(f"Added quantifier: {qprefix}")

    tce = f"always ({body})"
    return tce, reasons


def _gate(candidate: str) -> Tuple[str, List[str]]:
    msgs: List[str] = []
    text = candidate.strip()
    if not text.lower().startswith("always ("):
        text = f"always ({text})"
        msgs.append("Wrapped in always (...) gate")
    # balance parens
    bal = 0
    for ch in text:
        if ch == '(': bal += 1
        elif ch == ')': bal -= 1
        if bal < 0:
            msgs.append("Parenthesis underflow; normalization applied")
            break
    if bal > 0:
        text = text + (')' * bal)
        msgs.append("Balanced missing closing parenthesis")
    # whitelist tokens
    cleaned = re.sub(r"[^A-Za-z0-9_\s\(\)\-\>\|\&'\[\]]+", " ", text)
    if cleaned != text:
        msgs.append("Removed unsupported characters")
        text = cleaned
    text = re.sub(r"\s+", " ", text).strip()
    return text, msgs


def _fdl_enabled_from_env() -> bool:
    v = os.getenv("TAU_OPTIMIZER_USE_FDL", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _gs_enabled_from_env() -> bool:
    v = os.getenv("TAU_OPTIMIZER_USE_GS", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def optimize_prompt_to_tce(
    prompt: str,
    constraints: Optional[Dict[str, Any]] = None,
    ambiguity_threshold: float = 0.25,
    use_fdl: Optional[bool] = None,
    use_gs: Optional[bool] = None,
) -> Result[OptimizerOutput]:
    """Optimize English prompt into TCE using deterministic synthesis.

    The ambiguity score is computed from the number of plausible intents and
    presence/absence of key roles. If ambiguity <= threshold, no questions are
    proposed.
    """
    try:
        constraints = constraints or {}
        s, reasons = _fst_normalize(prompt)
        feats = _extract_typed(s)
        # Tier-1 role extraction to improve predicate synthesis
        try:
            roles = extract_roles(prompt)
            # Prefer structured roles when present
            if roles.condition: feats["condition"] = roles.condition
            if roles.action: feats["action"] = roles.action
            if roles.guard: feats.setdefault("guards", []).append(roles.guard)
            if roles.negation: feats["negate"] = True
            if roles.quant_all and "all x" not in feats.get("quantifiers", []):
                feats.setdefault("quantifiers", []).append("all x")
            if roles.quant_ex and "ex x" not in feats.get("quantifiers", []):
                feats.setdefault("quantifiers", []).append("ex x")
            if roles.temporal:
                t = feats.get("temporal") or []
                feats["temporal"] = list(set(t + roles.temporal))
            reasons.append("Tier-1 roles extracted")
        except Exception:
            pass
        # Optional FDL projection (feature-flagged for safe rollback)
        use_fdl_flag = _fdl_enabled_from_env() if use_fdl is None else bool(use_fdl)
        if use_fdl_flag:
            reasons.append("FDL projection enabled")
            # Build a basis from observed features (guards/quantifiers/time)
            basis = build_default_basis(
                guards=list(set(feats.get("guards") or [])),
                quants=list(set(feats.get("quantifiers") or [])),
                times=list(set(feats.get("temporal") or [])),
            )
            bits = encode_bitset(basis, feats)
            # Apply policy constraints by meet (AND); default allow-all
            allow_mask = (1 << max(1, (
                list(basis.intent_bits.values())
                + list(basis.guard_bits.values())
                + list(basis.quant_bits.values())
                + list(basis.time_bits.values())
            ))[-1]) - 1 if (basis.intent_bits or basis.guard_bits or basis.quant_bits or basis.time_bits) else 0
            bits = glb_with_constraints(bits, allow_mask)
            # Decode constrained lattice element and merge into features
            feats_fd = decode_bitset(basis, bits)
            # Merge: constrained facets override detected when present
            if feats_fd.get("intent"): feats["intent"] = feats_fd["intent"]
            if feats_fd.get("guards"): feats["guards"] = feats_fd["guards"]
            if feats_fd.get("quantifiers"): feats["quantifiers"] = feats_fd["quantifiers"]
            if feats_fd.get("temporal"): feats["temporal"] = feats_fd["temporal"]
            tce, proj_msgs = _project_to_tce(feats)
        else:
            tce, proj_msgs = _project_to_tce(feats)
        reasons.extend(proj_msgs)

        # FCA attribute exploration (optional, data-driven implications)
        try:
            # Build a tiny formal context from current features and any temporal/quantifier defaults
            # Objects: single synthetic object for current prompt; Attributes: detected facet atoms
            det_attrs = set()
            if feats.get('intent'): det_attrs.add(f"intent:{feats['intent']}")
            det_attrs |= {f"guard:{g}" for g in (feats.get('guards') or [])}
            det_attrs |= {f"quant:{q}" for q in (feats.get('quantifiers') or [])}
            det_attrs |= {f"time:{t}" for t in (feats.get('temporal') or [])}
            all_attrs = sorted(det_attrs)
            ctx = FormalContext(all_attrs, [det_attrs])
            impls = ctx.generate_implications_via_closure(max_premise_size=2)
            # Use simple implications to recommend missing facets (if any)
            for imp in impls:
                lhs = set(imp.premise)
                rhs = set(imp.conclusion)
                if lhs.issubset(det_attrs) and not rhs.issubset(det_attrs):
                    reasons.append(f"FCA suggests: {str(imp)}")
        except Exception:
            pass

        # Optional GS/NSO clean-room synthesis (feature-flagged)
        use_gs_flag = _gs_enabled_from_env() if use_gs is None else bool(use_gs)
        if use_gs_flag:
            try:
                gs_ast = gs_build_from_features(
                    intent=feats.get("intent"),
                    condition=feats.get("condition"),
                    action=feats.get("action"),
                    guards=feats.get("guards") or [],
                    quantifiers=feats.get("quantifiers") or [],
                    temporal=feats.get("temporal") or [],
                )
                tce_gs = gs_to_tce(gs_ast)
                if tce_gs and tce_gs.lower().startswith("always ("):
                    tce = tce_gs
                    reasons.append("GS synthesis applied")
            except Exception as _e:
                reasons.append("GS synthesis skipped (error)")
        # optional constraints
        if constraints.get('forbid_colon') and ':' in tce:
            tce = tce.replace(':', ' ')
            reasons.append("Removed colon per constraint")
        if constraints.get('require_prefix') and not tce.lower().startswith(constraints['require_prefix'].lower()):
            tce = f"{constraints['require_prefix']}{tce.strip()}"
            reasons.append("Applied required prefix")
        tce, gate_msgs = _gate(tce)
        reasons.extend(gate_msgs)

        # ambiguity heuristics (FDL/GS-aware generation of questions when enabled)
        intents_detected = [k for k in [feats.get('intent')] if k]
        roles_missing = int(feats.get('condition') is None) + int(feats.get('action') is None)
        paths = max(1, len(intents_detected)) + roles_missing
        ambiguity = min(1.0, paths / 4.0)
        questions: List[str] = []
        if ambiguity > ambiguity_threshold:
            if feats.get('condition') is None:
                questions.append("What is the condition (e.g., payment_approved)?")
            if feats.get('action') is None:
                questions.append("What is the action (e.g., order_shipped)?")
            if not feats.get('intent'):
                questions.append("Is this an invariant or a causal rule (if X then Y)?")
            # Scope clarification for soft negation without explicit condition
            if feats.get('negate') and not feats.get('global_negate') and not feats.get('condition'):
                questions.append("Should this rule apply at all times (never), or only under specific conditions? If conditional, please specify the condition.")
            if use_fdl_flag:
                # Map join-irreducibles to questions (guards/quantifiers/temporal)
                for g in sorted(set(feats.get('guards') or [])):
                    questions.append(f"Confirm guard applies: not {g}?")
                for q in sorted(set(feats.get('quantifiers') or [])):
                    questions.append(f"Confirm quantifier: {q}?")
                for t in sorted(set(feats.get('temporal') or [])):
                    questions.append(f"Confirm temporal reference: {t}?")
            elif use_gs_flag:
                # Ask about structure relevant to GS normalization
                if feats.get('guards'):
                    questions.append("Should guards block the action when active?")
                if feats.get('quantifiers'):
                    questions.append("Should the rule hold for all entities or only some?")
            else:
                if not feats.get('guards'):
                    questions.append("Is there a guard/exception (e.g., unless maintenance)?")

        out = OptimizerOutput(
            tce=tce,
            prompt_candidate=tce,
            intent=feats.get('intent'),
            guards=feats.get('guards') or [],
            quantifiers=feats.get('quantifiers') or [],
            temporal=feats.get('temporal') or [],
            reasons=reasons,
            analysis=feats,
            questions=questions,
            ambiguity=ambiguity,
        )
        return Success(out)
    except Exception as e:  # pragma: no cover
        return Failure(f"Optimizer failed: {e}")


# FDL moved to domain.lattice (imported above)



