from __future__ import annotations

import re
import pytest

pytest.importorskip("backend.unified.domain.normalization_fast")
from backend.unified.domain.normalization_fast import gate_tokens_fast


@pytest.mark.parametrize("expr,ok", [
    ("always (A AND B)", True),
    ("always (A OR B)", True),
    ("always (A => B)", True),
    ("always (not (A))", True),
    ("always (A : B)", False),
])
def test_gate_tokens_fast_accepts_and_normalizes(expr: str, ok: bool):
    out, reasons = gate_tokens_fast(expr)
    if ok:
        assert out.lower().startswith("always (")
        assert not any(":" in r for r in reasons)
    else:
        # Colon forbidden should be reported in reasons
        assert any(":" in r.lower() or "colon" in r.lower() for r in reasons)

