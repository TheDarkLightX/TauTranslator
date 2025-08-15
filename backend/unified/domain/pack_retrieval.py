"""
Lightweight retrieval over KnowledgePack without external deps.
Uses simple token overlap scoring (Jaccard-like) to get top-k rules/examples.
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple

from ..core.result_enhanced import Result, Success
from .grammar_knowledge_pack import KnowledgePack, RuleSummary


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in text.replace("\n", " ").replace('(', ' ').replace(')', ' ').replace('[',' ').replace(']',' ').split() if t.strip()}


def _score(query: str, rule: RuleSummary) -> float:
    q = _tokenize(query)
    r = _tokenize(rule.summary + " " + " ".join(rule.examples) + " " + rule.name)
    if not q or not r:
        return 0.0
    inter = len(q & r)
    union = len(q | r)
    return inter / union if union else 0.0


def retrieve_top_k(pack: KnowledgePack, query: str, k: int = 4) -> Result[List[Dict[str, Any]]]:
    scored: List[Tuple[float, RuleSummary]] = [(_score(query, rs), rs) for rs in pack.rules]
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [
        {
            "name": rs.name,
            "summary": rs.summary,
            "examples": rs.examples,
            "score": round(s, 4),
        }
        for s, rs in scored[:k]
        if s > 0.0
    ]
    return Success(top)


