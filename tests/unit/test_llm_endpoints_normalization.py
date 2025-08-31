from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")
from fastapi.testclient import TestClient
from backend.api.server import app


client = TestClient(app)


@pytest.mark.parametrize("expr", [
    "always (A AND B)",
    "always (A OR B)",
    "always (A => B)",
    "always (not (A))",
])
def test_connective_normalization_acceptance(expr: str):
    # These are normalized in various ways by simple translator / fallback path
    r = client.post("/translate/tce-to-tau", json={"tce": expr})
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    tau = (data.get("tau") or "").lower()
    # Accept that tokens normalize to tau grammar equivalents
    assert "always (" in tau

