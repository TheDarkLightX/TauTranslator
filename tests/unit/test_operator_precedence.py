from __future__ import annotations

import pytest
from backend.unified.domain.normalization_fast import gate_tokens_fast
from backend.unified.api.simple_tce import translate_tce_to_tau_simple


@pytest.mark.parametrize("expr", [
    # ! binds tighter than && which binds tighter than ||, etc.
    "always (!A && B)",
    "always (A || B && C)",
    # iff and only-if precedence vs implication
    "always ((A <-> B) -> C)",
    "always (A <- B)",
    # xor via expansion
    "always (((A || B) && !(A && B)))",
])
def test_precedence_forms_are_wff_and_translatable(expr: str):
    gated, reasons = gate_tokens_fast(expr)
    ok, tau, errs = translate_tce_to_tau_simple(gated)
    assert ok is True, f"Translation failed: {errs}"
    assert isinstance(tau, str) and tau


