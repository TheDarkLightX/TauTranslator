from __future__ import annotations

import re
from typing import Dict


def validate_tau_structure(tau: str) -> Dict[str, object]:
    """Lightweight validators over printed Tau strings.

    Returns a dict with counts and flags, including paren_balance_ok, has_implication, quant_all_count, quant_ex_count,
    negation_count, and predicate_arity_ok (best-effort). Intended for tests and debug logging.
    """
    info: Dict[str, object] = {}
    text = (tau or "").strip()
    # Paren balance
    bal = 0
    ok = True
    for ch in text:
        if ch == '(': bal += 1
        elif ch == ')': bal -= 1
        if bal < 0: ok = False; break
    if bal != 0: ok = False
    info["paren_balance_ok"] = ok
    # Operators/quantifiers
    info["has_implication"] = "->" in text
    info["quant_all_count"] = len(re.findall(r"\ball\s+[A-Za-z]", text))
    info["quant_ex_count"] = len(re.findall(r"\bex\s+[A-Za-z]", text))
    info["negation_count"] = len(re.findall(r"!\s*[A-Za-z_]", text))
    # Predicate arity quick check
    arity_ok = True
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\[0\]\(([^)]*)\)", text):
        args = m.group(2).strip()
        if args:
            # commas must separate args; disallow space-only separators
            if ',' not in args and ' ' in args:
                arity_ok = False; break
    info["predicate_arity_ok"] = arity_ok
    return info


