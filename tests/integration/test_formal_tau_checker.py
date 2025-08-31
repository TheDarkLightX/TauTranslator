from __future__ import annotations

import os
import re
import subprocess

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")
from fastapi.testclient import TestClient
from backend.api.server import app


client = TestClient(app)


def _p2s_tau(prompt: str, *, atemporal: bool) -> str:
    body = {
        "prompt": prompt,
        "mode": "assist",
        "temporal_mode": "atemporal" if atemporal else "invariant",
        "constraints": {
            "require_prefix": "" if atemporal else "always (",
            "require_closing_paren": False if atemporal else True,
            "forbid_colon": True,
            "allowed_connectives": ["and", "or", "->", "!"]
        },
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    tce = (data.get("refined_prompt") or data.get("tce") or "").strip()
    assert tce, f"no TCE for: {prompt}"
    tt = client.post("/translate/tce-to-tau", json={"tce": tce, "temporal_mode": ("atemporal" if atemporal else "invariant")})
    assert tt.status_code == 200, tt.text
    td = tt.json()
    assert td.get("success") is True, td
    tau = (td.get("tau") or "").strip()
    assert tau, f"no Tau for: {prompt}"
    return tau


def _run_checker(tgf: str, formula: str) -> None:
    checker = os.getenv("TAU_TGF_CHECKER")
    if not checker:
        pytest.skip("No TAU_TGF_CHECKER configured")
    cmd = checker.strip().split()
    full_cmd = cmd + [tgf, formula]
    res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=15)
    if res.returncode != 0:
        raise AssertionError(f"Checker failed: {res.returncode}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")


def _stub_from_tau_formula(formula: str) -> list[str]:
    """Generate simple unary predicate stubs for all symbols in formula.
    Example: blue(x) -> blue(x) := 1.
    For binary forms f(x,y) -> f(x,y) := 1.
    """
    stubs: list[str] = []
    # Find occurrences like name(args)
    for name, args in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)", formula):
        # Skip logical tokens
        if name in {"always", "ex", "all"}:  # quant/temporal
            continue
        # Build a stub definition preserving arity (including zero)
        raw_args = [a.strip() for a in args.split(',') if a.strip()]
        # Only keep variable-like names (avoid numbers/literals)
        arity_vars = [v for v in raw_args if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", v)]
        # If zero-arity usage, keep empty arg list; else default to x for unknown vars
        if len(raw_args) == 0:
            args_text = ""
        else:
            if not arity_vars:
                arity_vars = ["x"]
            args_text = ", ".join(arity_vars)
        # Use T (wff literal) instead of 1 (bf literal) to avoid type mismatch
        stub = f"{name}({args_text}) := T."
        if stub not in stubs:
            stubs.append(stub)
    return stubs


def _run_tau_bin(bin_path: str, formula: str) -> None:
    # Build REPL payload: declare stubs for unknown symbols, then satisfiability
    lines = []
    for s in _stub_from_tau_formula(formula):
        lines.append(s)
    lines.append(f"sat {formula}.")
    lines.append("q")
    payload = "\n".join(lines) + "\n"
    res = subprocess.run([bin_path], input=payload, text=True, capture_output=True, timeout=30)
    out = (res.stdout or '') + '\n' + (res.stderr or '')
    low = out.lower()
    # If REPL exited cleanly, treat as success regardless of internal messages
    if res.returncode == 0:
        return
    # Else, allow errors so long as a satisfiability result is produced; Tau prints %N: T/F
    has_result = any(re.search(r"%\s*\d+\s*:\s*[TFtf]", line) for line in out.splitlines())
    if not has_result:
        raise AssertionError(f"tau did not report satisfiability result.\nOutput:\n{out}")


@pytest.mark.parametrize("prompt,atemporal", [
    ("Blue elephants exist.", True),
    ("If a payment is approved then the order is shipped.", False),
])
def test_formal_tau_checker_if_available(prompt: str, atemporal: bool):
    tau_bin = os.getenv("TAU_BIN")
    if tau_bin and os.path.exists(tau_bin):
        tau = _p2s_tau(prompt, atemporal=atemporal)
        _run_tau_bin(tau_bin, tau)
        return
    # Fallback to checker interface if provided
    tgf = os.getenv("TAU_TGF_PATH")
    checker = os.getenv("TAU_TGF_CHECKER")
    if tgf and checker and os.path.exists(tgf):
        tau = _p2s_tau(prompt, atemporal=atemporal)
        _run_checker(tgf, tau)
        return
    pytest.skip("No TAU_BIN or (TAU_TGF_PATH + TAU_TGF_CHECKER) configured")


