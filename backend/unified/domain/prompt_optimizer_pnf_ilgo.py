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

    # intent detection
    if re.search(r"\balways\b|\bat all times\b|\bmust always\b", low):
        intent = "invariant"
    if re.search(r"\bif\b|\bwhen\b|\bwhenever\b|\bonce\b|\bafter\b", low):
        intent = intent or "causal"
    if re.search(r"\biff\b|\bequivalent\b|\bif and only if\b", low):
        intent = "equivalence"

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

    return {
        "intent": intent,
        "condition": cond,
        "action": act,
        "guards": guards,
        "quantifiers": quantifiers,
        "temporal": temporal,
    }


def _project_to_tce(features: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Project features to a normalized TCE template."""
    reasons: List[str] = []
    cond = features.get("condition") or "condition"
    act = features.get("action") or features.get("predicate") or "action"
    guards: List[str] = features.get("guards") or []
    quant: List[str] = features.get("quantifiers") or []

    body = None
    if features.get("intent") == "equivalence":
        body = f"({cond} -> {act}) and ({act} -> {cond})"
        reasons.append("Equivalence decomposed to implication pair")
    elif features.get("intent") == "causal":
        body = f"{cond} -> {act}"
    else:
        # default invariant form
        body = f"{act}"

    # apply guard as conjunction in antecedent when causal
    if guards:
        g = " and ".join(guards)
        if "->" in body:
            lhs, rhs = body.split("->", 1)
            body = f"({lhs.strip()} and not {g}) -> {rhs.strip()}"
            reasons.append("Applied guard as negative condition")
        else:
            body = f"({g} -> {body})"
            reasons.append("Applied guard implication around action")

    # add quantifier wrapper if detected
    qprefix = None
    for q in quant:
        if q.startswith("all"):
            qprefix = "all x"
            break
        if q.startswith("ex"):
            qprefix = "ex x"
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


def optimize_prompt_to_tce(
    prompt: str,
    constraints: Optional[Dict[str, Any]] = None,
    ambiguity_threshold: float = 0.25,
    use_fdl: Optional[bool] = None,
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
            # For Phase 1: allow all bits; future: derive constraint mask from policy
            allow_mask = (1 << 63) - 1  # effectively a wide all-ones mask for Python int
            bits = glb_with_constraints(bits, allow_mask)
            # No direct textual form from bits yet; still synthesize via current projector
            tce, proj_msgs = _project_to_tce(feats)
        else:
            tce, proj_msgs = _project_to_tce(feats)
        reasons.extend(proj_msgs)
        # optional constraints
        if constraints.get('forbid_colon') and ':' in tce:
            tce = tce.replace(':', ' ')
            reasons.append("Removed colon per constraint")
        if constraints.get('require_prefix') and not tce.lower().startswith(constraints['require_prefix'].lower()):
            tce = f"{constraints['require_prefix']}{tce.strip()}"
            reasons.append("Applied required prefix")
        tce, gate_msgs = _gate(tce)
        reasons.extend(gate_msgs)

        # ambiguity heuristics (FDL-aware generation of questions when enabled)
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
            if use_fdl_flag:
                # Map join-irreducibles to questions (guards/quantifiers/temporal)
                for g in sorted(set(feats.get('guards') or [])):
                    questions.append(f"Confirm guard applies: not {g}?")
                for q in sorted(set(feats.get('quantifiers') or [])):
                    questions.append(f"Confirm quantifier: {q}?")
                for t in sorted(set(feats.get('temporal') or [])):
                    questions.append(f"Confirm temporal reference: {t}?")
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


# ===== FDL (Finite Distributive Lattice) bitset core (Phase 2 scaffold) =====

@dataclass(frozen=True)
class ILGOBasis:
    """Join-irreducible basis for ILGO lattice as bit positions.

    intent_bits: mapping of specific intent irreducibles
    guard_bits: mapping of guard predicates
    quant_bits: mapping of quantifiers like 'all x', 'ex x'
    time_bits: mapping of temporal irreducibles (ordered chain)
    """
    intent_bits: Dict[str, int]
    guard_bits: Dict[str, int]
    quant_bits: Dict[str, int]
    time_bits: Dict[str, int]


def build_default_basis(guards: List[str], quants: List[str], times: List[str]) -> ILGOBasis:
    bit = 0
    intent_bits = {}
    for k in ["invariant", "causal", "equivalence", "temporal"]:
        intent_bits[k] = bit; bit += 1
    guard_bits = {g: (i+bit) for i, g in enumerate(sorted(set(guards)))}
    bit += len(guard_bits)
    quant_bits = {q: (i+bit) for i, q in enumerate(sorted(set(quants)))}
    bit += len(quant_bits)
    time_bits = {t: (i+bit) for i, t in enumerate(sorted(set(times), key=lambda s: (len(s), s)))}
    return ILGOBasis(intent_bits=intent_bits, guard_bits=guard_bits, quant_bits=quant_bits, time_bits=time_bits)


def encode_bitset(basis: ILGOBasis, feats: Dict[str, Any]) -> int:
    mask = 0
    intent = feats.get("intent")
    if intent and intent in basis.intent_bits:
        mask |= 1 << basis.intent_bits[intent]
    for g in feats.get("guards") or []:
        if g in basis.guard_bits: mask |= 1 << basis.guard_bits[g]
    for q in feats.get("quantifiers") or []:
        if q in basis.quant_bits: mask |= 1 << basis.quant_bits[q]
    for t in feats.get("temporal") or []:
        if t in basis.time_bits: mask |= 1 << basis.time_bits[t]
    return mask


def glb_with_constraints(bitset: int, constraint_mask: int) -> int:
    """Greatest lower bound under constraints is simply intersection (AND)."""
    return bitset & constraint_mask



