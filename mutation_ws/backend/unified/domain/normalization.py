"""
Normalization and gating utilities for TCE/Tau-friendly synthesis.
Small, pure functions for pipeline composition and unit testing.
"""

from __future__ import annotations

import re
from typing import Tuple, List


def ensure_always_wrapper(text: str) -> Tuple[str, List[str]]:
    msgs: List[str] = []
    t = (text or "").strip()
    if not t.lower().startswith("always ("):
        t = f"always ({t})"
        msgs.append("Wrapped in always (...) per constraint gate")
    return t, msgs


def balance_parentheses(text: str) -> Tuple[str, List[str]]:
    msgs: List[str] = []
    bal = 0
    out: list[str] = []
    for ch in text:
        if ch == '(':
            bal += 1
            out.append(ch)
        elif ch == ')':
            if bal == 0:
                # drop unmatched closing paren
                msgs.append("Removed unmatched closing parenthesis")
                continue
            bal -= 1
            out.append(ch)
        else:
            out.append(ch)
    if bal > 0:
        out.append(')' * bal)
        msgs.append("Balanced missing closing parenthesis")
    return "".join(out), msgs


def whitelist_and_canonicalize(text: str) -> Tuple[str, List[str]]:
    msgs: List[str] = []
    # Allow relational and negation operators and basic punctuation inside always(...)
    cleaned = re.sub(r"[^A-Za-z0-9_,\s\(\)\-\>\|\&'\[\]<!=>]+", " ", text)
    if cleaned != text:
        msgs.append("Removed unsupported characters")
        text = cleaned
    text = re.sub(r"\s+", " ", text).strip()
    return text, msgs


def gate_tokens(candidate: str) -> Tuple[str, List[str]]:
    """Strict gate that guarantees 'always ( ... )' with balanced parens and whitelisted tokens."""
    reasons: List[str] = []
    raw = (candidate or "").strip()
    # First pass: whitelist raw to avoid exotic chars early
    raw, m0 = whitelist_and_canonicalize(raw)
    reasons.extend(m0)
    # Extract inner if already wrapped
    m = re.match(r"^\s*always\s*\((.*)\)\s*$", raw, flags=re.IGNORECASE | re.DOTALL)
    if m:
        inner = m.group(1)
    else:
        inner = raw
        reasons.append("Wrapped in always (...) per constraint gate")
    # Balance and clean inner
    inner_bal, m1 = balance_parentheses(inner)
    reasons.extend(m1)
    inner_clean, m2 = whitelist_and_canonicalize(inner_bal)
    reasons.extend(m2)
    text = f"always ({inner_clean})"
    return text, reasons


def gate_tokens_atemporal(candidate: str) -> Tuple[str, List[str]]:
    """Gate for atemporal formulas: balance and whitelist without adding 'always'."""
    reasons: List[str] = []
    raw = (candidate or "").strip()
    raw, m0 = whitelist_and_canonicalize(raw)
    reasons.extend(m0)
    inner_bal, m1 = balance_parentheses(raw)
    reasons.extend(m1)
    inner_clean, m2 = whitelist_and_canonicalize(inner_bal)
    reasons.extend(m2)
    return inner_clean, reasons


def normalize_inner_from_prompt(orig_prompt_low: str, inner_or_full: str) -> str:
    """
    Best-effort normalization of the inner content of always(...)
    using prompt cues. Keeps logic identical to previous inlined version.
    """
    t = inner_or_full
    # truth literals and strong negation phrases
    t = re.sub(r"\b(always\s+true|true)\b", "T", t, flags=re.IGNORECASE)
    t = re.sub(r"\b(false)\b", "F", t, flags=re.IGNORECASE)
    t = re.sub(r"\bat\s+no\s+time\b", "never", t, flags=re.IGNORECASE)
    t = re.sub(r"\bunder\s+no\s+circumstances\b", "never", t, flags=re.IGNORECASE)
    # if ... then ...  →  (...) -> (...)
    t = re.sub(r"\bif\b\s+(.*?)\s+\bthen\b\s+(.*)$", r"(\1) -> (\2)", t, flags=re.IGNORECASE)
    # when/whenever/after X, Y → (X) -> (Y)
    t = re.sub(r"\bwhen\b\s+(.*?)[,;]\s*(.*)$", r"(\1) -> (\2)", t, flags=re.IGNORECASE)
    t = re.sub(r"\bwhenever\b\s+(.*?)[,;]\s*(.*)$", r"(\1) -> (\2)", t, flags=re.IGNORECASE)
    t = re.sub(r"\bafter\b\s+(.*?)[,;]\s*(.*)$", r"(\1) -> (\2)", t, flags=re.IGNORECASE)
    # implication/connectives/quantifiers
    t = re.sub(r"\b(implies|=>|⇒)\b", "->", t, flags=re.IGNORECASE)
    t = re.sub(r"\bAND\b", "&&", t)
    t = re.sub(r"\band\b", "&&", t)
    t = re.sub(r"\bOR\b", "||", t)
    t = re.sub(r"\bor\b", "||", t)
    t = re.sub(r"\b(for\s+all|forall)\b", "all", t, flags=re.IGNORECASE)
    t = re.sub(r"\b(there\s+exists|exists)\b", "ex", t, flags=re.IGNORECASE)
    return t.strip()


