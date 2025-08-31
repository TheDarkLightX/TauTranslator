from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.unified.api.llm_endpoints import router as llm_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(llm_router)
    return TestClient(app)


def test_atemporal_english_has_no_at_all_times_prefix():
    client = _client()
    body = {"prompt": "blue elephants exist", "temporal_mode": "atemporal"}
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    tce_en = (data.get("tce") or "").strip()
    assert not tce_en.startswith("At all times,")


