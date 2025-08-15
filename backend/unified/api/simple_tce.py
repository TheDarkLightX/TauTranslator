from __future__ import annotations

import re
from typing import Tuple, List


# Allow common Tau punctuation in fallback output too
ALLOWED_TOKENS = re.compile(r"^[a-zA-Z0-9_\s(),:!\-\->\[\]]+$")


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
    # Normalize spacing
    inner = re.sub(r"\s+", " ", inner).strip()
    # Basic replacements
    inner = re.sub(r"\bequals\b", "=", inner, flags=re.IGNORECASE)
    inner = re.sub(r"\band\b", "&", inner, flags=re.IGNORECASE)
    inner = re.sub(r"\bor\b", "|", inner, flags=re.IGNORECASE)
    # not <expr> -> !<expr>
    inner = re.sub(r"\bnot\s+\(", "!(", inner, flags=re.IGNORECASE)
    inner = re.sub(r"\bnot\s+([a-zA-Z_][\w]*)", r"!\1", inner, flags=re.IGNORECASE)
    # if A then B -> A -> B (no else handling in fallback)
    inner = re.sub(r"\bif\s+(.+?)\s+then\s+(.+)$", r"(\1) -> (\2)", inner, flags=re.IGNORECASE)
    # Quantifiers: map TCE 'for all'/'forall' -> Tau 'all', 'there exists' -> 'ex'
    inner = re.sub(r"\b(for\s+all|forall)\s+([a-zA-Z_][\w]*)\s*\(", r"all \2 (", inner, flags=re.IGNORECASE)
    inner = re.sub(r"\b(there\s+exists|exists)\s+([a-zA-Z_][\w]*)\s*\(", r"ex \2 (", inner, flags=re.IGNORECASE)

    tau = f"always({inner})"
    # Ensure parentheses are balanced
    if not _balanced_parens(tau):
        # Try to close any missing )
        open_count = tau.count('(')
        close_count = tau.count(')')
        tau += ")" * max(0, open_count - close_count)
    return True, tau, []


