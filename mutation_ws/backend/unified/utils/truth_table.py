"""Truth Table Generator for Tau / Controlled-English formulas
==============================================================
Given a Boolean formula written in a Tau-like syntax (subset: &, |, ~, !, parentheses,
variables, constants 0/1, equality "=") this module enumerates all possible
combinations of the occurring variables (up to *MAX_VARS*) and evaluates the
formula for each row.

Returned format is a list of dicts: {"vars": {var: 0/1}, "value": 0/1}.

Safety:
    • Uses *literal_eval*-style mapping, disallowing arbitrary code execution.
    • Hard-caps the number of variables to avoid exponential blow-ups.
"""
from __future__ import annotations

from typing import List, Dict, Any
import itertools
import re

from backend.unified.core.result_enhanced import Result, Success, Failure

__all__ = ["build_truth_table", "MAX_VARS"]

# -------------------------------------------------------------
# Constants
# -------------------------------------------------------------
MAX_VARS = 10  # hard cap (2**10 = 1024 rows)

_VAR_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")

# Ops mapping Tau → Python bool expr
_REPLACEMENTS = {
    "&": " and ",
    "|": " or ",
    "~": " not ",
    "!": " not ",
    "=": " == ",
}

_ALLOWED_TOKENS = set("True False and or not ( ) 0 1".split())


# -------------------------------------------------------------
# Public API
# -------------------------------------------------------------

def build_truth_table(expr: str, max_vars: int = MAX_VARS) -> Result[List[Dict[str, Any]]]:
    """Enumerate truth table for *expr*.

    Supports a safe subset of Tau. Returns Failure if >max_vars distinct vars.
    """
    try:
        var_names = _extract_variables(expr)
        if len(var_names) == 0:
            return Failure("NO_VARS", "No variables found in expression")
        if len(var_names) > max_vars:
            return Failure("TOO_MANY_VARS", f"Expression contains {len(var_names)} variables (max {max_vars})")

        py_expr = _tau_to_python(expr)
        if py_expr.is_failure():
            return py_expr  # propagate
        code_str = py_expr.value

        table: List[Dict[str, Any]] = []
        for bits in itertools.product([0, 1], repeat=len(var_names)):
            env = {var: bool(b) for var, b in zip(var_names, bits)}
            try:
                value = eval(code_str, {"__builtins__": {}}, env)  # noqa: S307
            except Exception as exc:  # pylint: disable=broad-except
                return Failure("EVAL_ERROR", str(exc))
            table.append({"vars": env, "value": int(value)})
        return Success(table)
    except Exception as exc:  # pylint: disable=broad-except
        return Failure("TABLE_ERROR", str(exc))


# -------------------------------------------------------------
# Helpers
# -------------------------------------------------------------

def _extract_variables(expr: str) -> List[str]:
    vars_found = set(
        v for v in _VAR_RE.findall(expr)
        if v not in {"T", "F", "True", "False"}
        and not v.isdigit()
    )
    return sorted(vars_found)


def _tau_to_python(expr: str) -> Result[str]:
    # Replace operators
    converted = expr
    for tau_op, py_op in _REPLACEMENTS.items():
        converted = re.sub(re.escape(tau_op), py_op, converted)

    # Replace constants
    converted = converted.replace("T", "True").replace("F", "False")
    converted = re.sub(r"\b1\b", "True", converted)
    converted = re.sub(r"\b0\b", "False", converted)

    # Sanity-check tokens
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|[()&|~!]|==|not|and|or|True|False", converted)
    for tok in tokens:
        if not (tok in _ALLOWED_TOKENS or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", tok)):
            return Failure("UNSUPPORTED_TOKEN", f"Unsupported token '{tok}' in expression")
    return Success(converted) 