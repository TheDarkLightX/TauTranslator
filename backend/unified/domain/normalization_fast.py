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


def _split_top(text: str, token: str) -> list[str]:
    out = []
    buf = []
    depth = 0
    i = 0
    L = len(text)
    while i < L:
        ch = text[i]
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if depth == 0 and text.startswith(token, i):
            out.append(''.join(buf).strip()); buf = []
            i += len(token); continue
        buf.append(ch); i += 1
    out.append(''.join(buf).strip())
    return out


def _rewrite_biconditional_and_reverse(text: str) -> str:
    # First, rewrite simple parenthesized forms anywhere inside
    import re as _re
    prev = None
    out = text
    # (A <-> B) => ((A -> B) && (B -> A))
    pat_bi = _re.compile(r"\(([^()]+?)\)\s*<->\s*\(([^()]+?)\)")
    pat_bi_simple = _re.compile(r"\(([^()]+?)\s*<->\s*([^()]+?)\)")
    pat_rev = _re.compile(r"\(([^()]+?)\)\s*<-\s*\(([^()]+?)\)")
    pat_rev_simple = _re.compile(r"\(([^()]+?)\s*<-\s*([^()]+?)\)")
    for _ in range(4):  # few iterations to settle local rewrites
        prev = out
        out = pat_bi.sub(r"((\1 -> \2) && (\2 -> \1))", out)
        out = pat_bi_simple.sub(r"((\1 -> \2) && (\2 -> \1))", out)
        out = pat_rev.sub(r"(\2 -> \1)", out)
        out = pat_rev_simple.sub(r"(\2 -> \1)", out)
        if out == prev:
            break
    text = out
    # Rewrite X <-> Y  => (X -> Y) && (Y -> X) at top level
    parts = _split_top(text, '<->')
    if len(parts) == 2:
        left = parts[0].strip()
        right = parts[1].strip()
        return f"(({left} -> {right}) && ({right} -> {left}))"
    # Rewrite X <- Y => (Y -> X)
    parts2 = _split_top(text, '<-')
    if len(parts2) == 2:
        left = parts2[0].strip()
        right = parts2[1].strip()
        return f"({right} -> {left})"
    return text


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
    # Normalize top-level biconditional and reverse implication to supported forms
    inner_bal = _rewrite_biconditional_and_reverse(inner_bal)
    # Explicitly report forbidden colon usage before generic whitelist cleaning
    if ":" in inner_bal:
        reasons.append("Removed colon per constraint")
    inner_clean, m2 = whitelist_and_canonicalize(inner_bal)
    reasons.extend(m2)
    return f"always ({inner_clean})", reasons


