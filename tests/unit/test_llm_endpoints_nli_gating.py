from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.unified.api.llm_endpoints import router as llm_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(llm_router)
    return TestClient(app)


def test_nli_gating_noop_when_disabled(monkeypatch):
    client = _client()
    # Ensure NLI is disabled
    monkeypatch.setenv('TAU_ENABLE_NLI', '0')
    monkeypatch.delenv('TAU_NLI_MODEL', raising=False)
    body = {"prompt": "blue elephants exist", "temporal_mode": "atemporal"}
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    # Should not crash and should not add NLI reason
    reasons = data.get("reasons") or []
    assert not any("NLI rerank applied" in s for s in reasons)


