from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Protocol, Sequence, Tuple


@dataclass(frozen=True)
class Constraints:
    """Constraints and preferences that may guide disambiguation.

    All fields are optional; callers pass only what they need. Keep this
    minimal and stable so it’s easy for junior developers to reason about.
    """

    prefer_quantifier: Optional[str] = None  # "all" | "ex"


def sanitize_to_tce(generated: str, user: str, temporal_mode: str | None) -> str:
    """Extract or construct a TCE-like string from LLM output.

    Behavior:
    - If a segment after "User:" appears, prefer it.
    - If we find an explicit "always ( ... )" span, return it; strip when atemporal.
    - Otherwise, fall back to user's prompt, wrapped only if invariant.
    """
    is_atemporal = (temporal_mode or "").lower() == "atemporal"
    text = generated or ""
    if "User:" in text:
        try:
            after = text.split("User:", 1)[1]
            after = after.split("TCE:", 1)[0]
            after = after.splitlines()[0].strip()
            if after:
                return after if is_atemporal else f"always ({after})"
        except Exception:
            pass
    idx = text.find("always (")
    if idx != -1:
        tail = text[idx:]
        close = tail.find(')')
        span = tail[: close + 1] if close != -1 else tail
        if is_atemporal:
            try:
                inner = span[len('always ('):-1] if span.endswith(')') else span
                return inner.strip()
            except Exception:
                return user
        return span
    return user if is_atemporal else f"always ({user})"


def infer_temporal_mode(prompt: str, explicit: Optional[str]) -> str:
    """Infer temporal mode from the prompt and an optional explicit override.

    Returns one of: "invariant" | "atemporal".
    - If an explicit mode is provided, it wins.
    - Otherwise, detect temporal keywords; default to atemporal.
    """

    if explicit:
        v = explicit.strip().lower()
        return v if v in {"invariant", "atemporal"} else "atemporal"
    low = (prompt or "").lower()
    if any(w in low for w in ["always", "whenever", "at all times", "must always"]):
        return "invariant"
    return "atemporal"


def choose_quantifier(prompt: str, inner: str, constraints: Constraints) -> Tuple[Optional[str], Optional[str]]:
    """Choose a quantifier when none is present, returning (quantifier, reason).

    - Honors constraints.prefer_quantifier if set.
    - Otherwise uses lightweight keyword cues (universal vs existential).
    - Returns (None, None) when no quantifier should be injected.
    """

    # If already quantified, do nothing
    if re.search(r"\b(all|ex)\b", inner, flags=re.IGNORECASE):
        return None, None
    pref = (constraints.prefer_quantifier or "").strip().lower() if constraints else ""
    if pref in {"all", "ex"}:
        return pref, f"Preference: {pref}"
    low = (prompt or "").lower()
    if re.search(r"\b(for\s+all|each|every|all)\b", low):
        return "all", "Detected universal cue"
    if re.search(r"\b(there\s+exists|exists|some|at\s+least\s+one)\b", low):
        return "ex", "Detected existential cue"
    return None, None


class NliReranker(Protocol):
    def rerank(self, premise: str, candidates: Sequence[str]) -> Tuple[str, List[str]]:  # (best, reasons)
        ...


class LexicalNliReranker:
    """Lightweight NLI-like reranker using Jaccard token overlap.

    This keeps offline performance predictable. It can be replaced by
    an ONNX-backed reranker via the same protocol.
    """

    TOKEN_RE = re.compile(r"[A-Za-z0-9]+")

    def _tok(self, s: str) -> set[str]:
        return set(self.TOKEN_RE.findall((s or "").lower()))

    def rerank(self, premise: str, candidates: Sequence[str]) -> Tuple[str, List[str]]:
        if not candidates:
            return "", []
        p = self._tok(premise)
        best_idx = 0
        best_score = -1.0
        for i, c in enumerate(candidates):
            t = self._tok(c)
            inter = len(p & t)
            union = max(1, len(p | t))
            score = inter / union
            if score > best_score:
                best_score = score
                best_idx = i
        return candidates[best_idx], [f"NLI-lite rerank on {len(candidates)} candidates"]


def get_nli_reranker() -> Optional[NliReranker]:
    """Return an NLI reranker if enabled, else None.

    - TAU_ENABLE_NLI=1 enables reranking.
    - If TAU_NLI_ONNX_PATH is set, a placeholder ONNX check is done but we
      still use the lexical reranker as default lightweight behavior.
    """

    if os.getenv("TAU_ENABLE_NLI", "0") != "1":
        return None
    # Best-effort ONNX availability check (kept simple to avoid heavy deps)
    onnx_path = os.getenv("TAU_NLI_ONNX_PATH", "").strip()
    if onnx_path and os.path.exists(onnx_path):
        # Future: return an OnnxNliReranker() here
        return LexicalNliReranker()
    return LexicalNliReranker()


def dictionary_entity_candidates(text: str, topk: int = 3) -> List[str]:
    """Return lightweight entity candidates from a small dictionary.

    Produces canonical predicate roots with a "_candidate" suffix so it’s
    obvious these are suggestions, not final names.
    """

    dictionary = [
        "user", "session", "login", "order", "payment", "signal", "sensor", "alarm", "data",
        "profile", "package", "network"
    ]
    words = set(re.findall(r"[A-Za-z]+", (text or "").lower()))
    cands = [w for w in dictionary if w in words]
    return [f"{c}_candidate" for c in cands][:max(1, min(topk, len(cands) or 0))]


