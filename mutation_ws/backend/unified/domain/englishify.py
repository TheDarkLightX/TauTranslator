from __future__ import annotations

import re


def to_english_phrase(expr: str) -> str:
    t = expr.strip()
    if t.startswith('(') and t.endswith(')'):
        depth = 0
        ok = True
        for i, ch in enumerate(t):
            if ch == '(': depth += 1
            elif ch == ')': depth -= 1
            if depth == 0 and i < len(t) - 1:
                ok = False; break
        if ok:
            t = t[1:-1].strip()

    def split_top(text: str, token: str):
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

    parts = split_top(t, '->')
    if len(parts) == 2:
        lhs = to_english_phrase(parts[0])
        rhs = to_english_phrase(parts[1])
        return f"if {lhs} then {rhs}"

    parts_and = split_top(t, '&&')
    if len(parts_and) > 1:
        return ' and '.join(to_english_phrase(p) for p in parts_and)
    parts_or = split_top(t, '||')
    if len(parts_or) > 1:
        return ' or '.join(to_english_phrase(p) for p in parts_or)

    if t.startswith('!'):
        return f"do not {to_english_phrase(t[1:].strip())}"
    m_not = re.match(r"^not\s+(.*)$", t, flags=re.IGNORECASE)
    if m_not:
        return f"do not {to_english_phrase(m_not.group(1).strip())}"

    m_all = re.match(r"^all\s+([A-Za-z])\s*\((.*)\)$", t, flags=re.IGNORECASE)
    if m_all:
        var = m_all.group(1)
        inner = to_english_phrase(m_all.group(2))
        return f"for every {var}, {inner}"
    m_ex = re.match(r"^ex\s+([A-Za-z])\s*\((.*)\)$", t, flags=re.IGNORECASE)
    if m_ex:
        var = m_ex.group(1)
        inner = to_english_phrase(m_ex.group(2))
        return f"there exists {var} such that {inner}"

    if '(' in t and ')' in t:
        base = t.split('(', 1)[0].strip()
        return re.sub(r"_+", " ", base).strip()
    return re.sub(r"_+", " ", t).strip()


def tce_to_english(tce: str) -> str:
    m = re.match(r"^\s*always\s*\((.*)\)\s*$", tce, flags=re.IGNORECASE | re.DOTALL)
    inner = m.group(1).strip() if m else tce.strip()
    phrase = to_english_phrase(inner)
    sent = f"At all times, {phrase}"
    sent = sent[0].upper() + sent[1:]
    if not sent.endswith('.'):
        sent += '.'
    return sent


