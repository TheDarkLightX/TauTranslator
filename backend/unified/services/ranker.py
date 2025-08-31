from __future__ import annotations

import re
from typing import List, Sequence, Tuple


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9]+", (text or "").lower())


def _cosine_like(a_tokens: List[str], b_tokens: List[str]) -> float:
    if not a_tokens or not b_tokens:
        return 0.0
    a = {}
    for t in a_tokens: a[t] = a.get(t, 0) + 1
    b = {}
    for t in b_tokens: b[t] = b.get(t, 0) + 1
    inter = set(a.keys()) & set(b.keys())
    dot = sum(a[t] * b[t] for t in inter)
    a_norm = sum(v*v for v in a.values()) ** 0.5
    b_norm = sum(v*v for v in b.values()) ** 0.5
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return float(dot) / float(a_norm * b_norm)


def _rule_score(prompt_low: str, cand_text_low: str) -> float:
    score = 0.0
    has_exist = bool(re.search(r"\b(there\s+exists|exists|some|at\s+least\s+one)\b", prompt_low))
    has_univ = bool(re.search(r"\b(for\s+all|each|every|all)\b", prompt_low))
    if has_exist and re.search(r"\bex\b", cand_text_low):
        score += 1.0
    if has_univ and re.search(r"\ball\b", cand_text_low):
        score += 1.0
    # Temporal penalty for always(...) when no explicit temporal cue
    has_temporal_cue = bool(re.search(r"\b(always|whenever|at\s+all\s+times)\b", prompt_low))
    if (not has_temporal_cue) and ("always (" in cand_text_low):
        score -= 0.2
    return score


def rank_candidates_by_rules_and_overlap(prompt: str, candidate_texts: Sequence[str]) -> List[int]:
    """Return indices of candidates sorted by (rule score + cosine overlap).

    - prompt: natural language prompt
    - candidate_texts: English-like texts (e.g., englishified TCEs)
    """
    p_low = (prompt or "").lower()
    p_tok = _tokenize(prompt)
    scored: List[Tuple[int, float]] = []
    for i, ct in enumerate(candidate_texts):
        ct_low = (ct or "").lower()
        rules = _rule_score(p_low, ct_low)
        sim = _cosine_like(p_tok, _tokenize(ct))
        scored.append((i, rules + sim))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [i for i, _ in scored]


