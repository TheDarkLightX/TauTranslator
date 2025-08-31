from __future__ import annotations

import re
from typing import Tuple, List

# Precompiled patterns (module-level) for speed
_RE_WS = re.compile(r"\s+")
_RE_WHITELIST = re.compile(r"[^A-Za-z0-9_,\s\(\)\-\>\|\&'\[\]<!=>]+")


def ensure_always_wrapper(text: str) -> Tuple[str, List[str]]:
    msgs: List[str] = []
    t = (text or "").strip()
    if not t.lower().startswith("always ("):
        t = f"always ({t})"
        msgs.append("Wrapped in always (...) per constraint gate")
    return t, msgs


def balance_parentheses_stream(text: str) -> Tuple[str, List[str]]:
    msgs: List[str] = []
    bal = 0
    out_chars: List[str] = []
    append = out_chars.append
    for ch in text:
        if ch == '(':
            bal += 1
            append(ch)
        elif ch == ')':
            if bal == 0:
                if not msgs or msgs[-1] != "Removed unmatched closing parenthesis":
                    msgs.append("Removed unmatched closing parenthesis")
                continue
            bal -= 1
            append(ch)
        else:
            append(ch)
    if bal > 0:
        append(')' * bal)
        msgs.append("Balanced missing closing parenthesis")
    return "".join(out_chars), msgs


def whitelist_and_canonicalize(text: str) -> Tuple[str, List[str]]:
    msgs: List[str] = []
    cleaned = _RE_WHITELIST.sub(" ", text)
    if cleaned != text:
        msgs.append("Removed unsupported characters")
        text = cleaned
    text = _RE_WS.sub(" ", text).strip()
    return text, msgs


def gate_tokens_fast(candidate: str) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    raw = (candidate or "").strip()
    # Record forbidden colon usage before any normalization that may remove it
    if ":" in raw:
        reasons.append("Removed colon per constraint")
    raw, m0 = whitelist_and_canonicalize(raw)
    reasons.extend(m0)
    m = re.match(r"^\s*always\s*\((.*)\)\s*$", raw, flags=re.IGNORECASE | re.DOTALL)
    if m:
        inner = m.group(1)
    else:
        inner = raw
        reasons.append("Wrapped in always (...) per constraint gate")
    inner_bal, m1 = balance_parentheses_stream(inner)
    reasons.extend(m1)
    # Explicitly report forbidden colon usage before generic whitelist cleaning
    if ":" in inner_bal:
        reasons.append("Removed colon per constraint")
    inner_clean, m2 = whitelist_and_canonicalize(inner_bal)
    reasons.extend(m2)
    return f"always ({inner_clean})", reasons


