from __future__ import annotations

import re
from typing import Tuple, List


# Allow common Tau punctuation in fallback output too
# Allow time indices [t] and [t-1], logical connectives, commas, underscores, parentheses
ALLOWED_TOKENS = re.compile(r"^[A-Za-z0-9_\s(),:!\-\>\[\]=\&\|]+$")


def _balanced_parens(text: str) -> bool:
    depth = 0
    for ch in text:
        if ch == '(': depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def validate_tce_simple(text: str) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not text or not text.strip():
        errors.append("Empty input")
        return False, errors

    t = text.strip()
    # Allow trailing period or not
    if t.endswith('.'):
        t = t[:-1].strip()

    if ':' in t:
        errors.append("Colon ':' not allowed in TCE")
    if not _balanced_parens(t):
        errors.append("Unbalanced parentheses")
    if not t.lower().startswith("always (") or not t.endswith(')'):
        errors.append("TCE must start with 'always (' and end with ')'")
    if not ALLOWED_TOKENS.match(re.sub(r"\s+", " ", t)):
        errors.append("Contains unsupported characters")

    return (len(errors) == 0), errors


def translate_tce_to_tau_simple(text: str) -> Tuple[bool, str | None, List[str]]:
    valid, errs = validate_tce_simple(text)
    if not valid:
        return False, None, errs

    t = text.strip()
    if t.endswith('.'):
        t = t[:-1].strip()

    # Inside the always(...), replace simple connectives
    inner = t[len("always ("):-1]
    # If an implication is present, normalize each side to atoms name()
    # while avoiding variables (e.g., x) and time-indexed variables (i1[t])
    if "->" in inner:
        # split once on top-level '->'
        def _split_top_arrow(text: str) -> tuple[str,str] | None:
            depth = 0
            for i in range(len(text)):
                ch = text[i]
                if ch == '(': depth += 1
                elif ch == ')': depth -= 1
                if depth == 0 and text.startswith("->", i):
                    return text[:i].strip(), text[i+2:].strip()
            return None
        parts = _split_top_arrow(inner)
        if parts:
            lhs, rhs = parts
            def _atomize_side(side: str) -> str:
                # Replace bare words with name() unless they are T/F, quantifiers, or time-indexed tokens
                tokens = re.split(r"(\s+|\|\||&&|!|\(|\))", side)
                out: list[str] = []
                for tok in tokens:
                    if tok is None or tok == "":
                        continue
                    if re.fullmatch(r"\s+|\|\||&&|!|\(|\)", tok):
                        out.append(tok); continue
                    word = tok.strip()
                    low = word.lower()
                    if not word:
                        out.append(tok); continue
                    if low in {"t","f","all","ex","always"}:
                        out.append(word); continue
                    if re.search(r"\[t(?:-1)?\]", word):
                        out.append(word); continue
                    # already a ref like name(...)
                    if re.match(r"^[A-Za-z_][\w]*\s*\(", word):
                        out.append(word); continue
                    # single-letter variables common in quantifiers
                    if re.fullmatch(r"[a-z]", word):
                        out.append(word); continue
                    out.append(f"{word}()")
                return "".join(out)
            inner = f"({_atomize_side(lhs)} -> {_atomize_side(rhs)})"
    # Normalize spacing
    inner = re.sub(r"\s+", " ", inner).strip()
    # Basic replacements (favor Tau wff-level operators)
    inner = re.sub(r"\btrue\b", "T", inner, flags=re.IGNORECASE)
    inner = re.sub(r"\bfalse\b", "F", inner, flags=re.IGNORECASE)
    inner = re.sub(r"\bequals\b", "=", inner, flags=re.IGNORECASE)
    # Use logical connectives
    inner = re.sub(r"\band\b", "&&", inner, flags=re.IGNORECASE)
    inner = re.sub(r"\bor\b", "||", inner, flags=re.IGNORECASE)
    # not <expr> -> !<expr>
    inner = re.sub(r"\bnot\s+\(", "!(", inner, flags=re.IGNORECASE)
    inner = re.sub(r"\bnot\s+([a-zA-Z_][\w]*)", r"!\1", inner, flags=re.IGNORECASE)
    # if A then B -> A -> B (no else handling in fallback)
    inner = re.sub(r"\bif\s+(.+?)\s+then\s+(.+)$", r"(\1) -> (\2)", inner, flags=re.IGNORECASE)
    # Quantifiers: map TCE 'for all'/'forall' -> Tau 'all', 'there exists' -> 'ex'
    inner = re.sub(r"\b(for\s+all|forall)\s+([a-zA-Z_][\w]*)\s*\(", r"all \2 (", inner, flags=re.IGNORECASE)
    inner = re.sub(r"\b(there\s+exists|exists)\s+([a-zA-Z_][\w]*)\s*\(", r"ex \2 (", inner, flags=re.IGNORECASE)

    # Emit Tau as 'always ( ... )' with a space, per tau.tgf grammar
    tau = f"always ({inner})"
    # Ensure parentheses are balanced
    if not _balanced_parens(tau):
        # Try to close any missing )
        open_count = tau.count('(')
        close_count = tau.count(')')
        tau += ")" * max(0, open_count - close_count)
    return True, tau, []


