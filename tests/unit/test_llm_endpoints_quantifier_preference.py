from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.unified.api.llm_endpoints import router as llm_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(llm_router)
    return TestClient(app)


def test_prefer_quantifier_ex_applies_reason():
    client = _client()
    body = {
        "prompt": "blue elephants exist",
        "temporal_mode": "invariant",
        "constraints": {"prefer_quantifier": "ex"},
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    reasons = data.get("reasons") or []
    assert any("Applied quantifier preference: ex" in s for s in reasons)


def test_prefer_quantifier_all_applies_reason():
    client = _client()
    body = {
        "prompt": "every user must have a profile",
        "temporal_mode": "invariant",
        "constraints": {"prefer_quantifier": "all"},
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    reasons = data.get("reasons") or []
    if not any("Applied quantifier preference: all" in s for s in reasons):
        # If quantifier already present via normalization, reason may be omitted; verify presence
        tau = (data.get("tau") or "")
        tce = (data.get("tce") or "")
        assert (" all " in (" " + tau.lower() + " ")) or (" all " in (" " + tce.lower() + " "))


