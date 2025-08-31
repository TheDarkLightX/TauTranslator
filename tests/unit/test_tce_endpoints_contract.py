from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")
from fastapi.testclient import TestClient
from backend.api.server import app


client = TestClient(app)


def test_validate_tce_simple_contract():
    body = {"tce": "always (a -> b)"}
    r = client.post("/validate/tce", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data.get("valid") in (True, False)


def test_tce_to_tau_invariant_and_atemporal():
    # invariant pass-through
    inv = client.post("/translate/tce-to-tau", json={"tce": "always (x())"})
    assert inv.status_code == 200
    invd = inv.json()
    assert invd.get("success") is True
    assert (invd.get("tau") or "").startswith("always (")
    # atemporal unwrap
    ate = client.post("/translate/tce-to-tau", json={"tce": "always (x())", "temporal_mode": "atemporal"})
    assert ate.status_code == 200
    ated = ate.json()
    assert ated.get("success") is True
    assert (ated.get("tau") or "") == "x()"

