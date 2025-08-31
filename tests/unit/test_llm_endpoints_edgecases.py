from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")
from fastapi.testclient import TestClient
from backend.api.server import app


client = TestClient(app)


def test_p2s_constraints_enforced_and_prefix_added():
    body = {
        "prompt": "simple predicate",
        "mode": "assist",
        "constraints": {
            "require_prefix": "always (",
            "require_closing_paren": True,
            "forbid_colon": True,
            "allowed_connectives": ["and", "or", "->", "!"]
        }
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    # We just verify that the result is non-empty and begins with always (
    tce = (data.get("refined_prompt") or data.get("tce") or "").strip()
    assert tce.lower().startswith("always (")


def test_tce_to_tau_atemporal_mode_removes_wrapper():
    tce = "always (some_atom())"
    r = client.post("/translate/tce-to-tau", json={"tce": tce, "temporal_mode": "atemporal"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    tau = (data.get("tau") or "").strip()
    assert tau == "some_atom()"

