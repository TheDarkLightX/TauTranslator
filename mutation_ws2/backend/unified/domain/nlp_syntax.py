from __future__ import annotations

"""
Tier-1 rule-based NLP syntax extractor (pure, dependency-free).

Goals:
- Identify clause structure: condition vs action (if/then/when/unless)
- Detect negation cues and scope candidates
- Extract head phrases for predicate synthesis (verb + key complements)
- Detect determiners/quantifiers and simple temporal cues

No third-party grammars; profile-agnostic. Designed as a best-effort
front-end feeding the intent lattice and predicate synthesis.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
import re


NEG_CUES = re.compile(r"\b(don't|do not|never|at no time|under no circumstances|must not|cannot|can not|can't|should not|shall not)\b", re.I)
IF_SPLIT = re.compile(r"\bif\b", re.I)
THEN_SPLIT = re.compile(r"\bthen\b", re.I)
WHEN_SPLIT = re.compile(r"\bwhen\b|\bwhenever\b", re.I)
UNLESS_SPLIT = re.compile(r"\bunless\b|\bexcept\s+(?:if|when)\b", re.I)
DET_ALL = re.compile(r"\b(all|every|each|any|for all)\b", re.I)
DET_EX = re.compile(r"\b(some|exists|there exists|at least one)\b", re.I)
TEMP_NEXT = re.compile(r"\b(next|immediately|at once|t\+1)\b", re.I)
TEMP_PREV = re.compile(r"\b(previous|before|t-1)\b", re.I)


@dataclass(frozen=True)
class ClauseRoles:
    condition: Optional[str]
    action: Optional[str]
    guard: Optional[str]
    negation: bool
    quant_all: bool
    quant_ex: bool
    temporal: List[str]


@dataclass(frozen=True)
class SyntaxDoc:
    text: str
    clauses: List[ClauseRoles]


def _strip_punc(s: str) -> str:
    return re.sub(r"[\s\.,;:!?]+$", "", s.strip())


def _phrase(head: str) -> str:
    # Minimal phrase compaction: collapse whitespace
    return re.sub(r"\s+", " ", head.strip())


def analyze_tier1(text: str) -> SyntaxDoc:
    s = text.strip()
    # Initial split for 'when' pattern
    cond, act, guard = None, None, None
    t_acc: List[str] = []
    # Universal requirement pattern: "every|each|all <noun> must/has/have ... <object>"
    m_univ = re.search(r"\b(every|each|all)\s+([A-Za-z_]+)\b.*?\b(must|should|shall|has|have)\b.*?\b(profile|account\s+profile|record)\b", s, re.I)
    if m_univ:
        subj = m_univ.group(2)
        cond = _phrase(subj)
        act = _phrase("has profile")
        qa = True
    else:
        qa = False
    # Temporal cues
    if TEMP_NEXT.search(s): t_acc.append("[t+1]")
    if TEMP_PREV.search(s): t_acc.append("[t-1]")
    # Guard via unless/except
    mg = UNLESS_SPLIT.split(s, maxsplit=1)
    if len(mg) == 2:
        # s = A unless G  → guard = G, main = A
        main, g = mg[0], mg[1]
        guard = _phrase(_strip_punc(g))
        s = main
    # If/then vs when
    if IF_SPLIT.search(s):
        # if X then Y; tolerate missing 'then'
        after_if = IF_SPLIT.split(s, maxsplit=1)[1]
        parts = THEN_SPLIT.split(after_if, maxsplit=1)
        cond = _phrase(_strip_punc(parts[0]))
        act = _phrase(_strip_punc(parts[1])) if len(parts) == 2 else None
    elif WHEN_SPLIT.search(s):
        # when X, Y
        parts = WHEN_SPLIT.split(s, maxsplit=1)
        tail = parts[1] if len(parts) == 2 else ''
        sub = tail.split(',', 1)
        cond = _phrase(_strip_punc(sub[0])) if sub and sub[0] else None
        act = _phrase(_strip_punc(sub[1])) if len(sub) > 1 else None
    else:
        act = _phrase(_strip_punc(s))
    # Negation detection primarily in action
    neg = bool(NEG_CUES.search(act or s))
    qa = qa or bool(DET_ALL.search(s))
    qx = bool(DET_EX.search(s))
    roles = ClauseRoles(condition=cond, action=act, guard=guard, negation=neg, quant_all=qa, quant_ex=qx, temporal=t_acc)
    return SyntaxDoc(text=text, clauses=[roles])


def extract_roles(text: str) -> ClauseRoles:
    doc = analyze_tier1(text)
    return doc.clauses[0] if doc.clauses else ClauseRoles(None, None, None, False, False, False, [])


