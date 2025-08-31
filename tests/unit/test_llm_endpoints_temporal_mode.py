from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.unified.api.llm_endpoints import router as llm_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(llm_router)
    return TestClient(app)


def test_temporal_mode_atemporal_prevents_always_wrap_blue_elephants_exist():
    client = _client()
    body = {
        "prompt": "blue elephants exist",
        "temporal_mode": "atemporal",
        "constraints": {
            "forbid_colon": True,
            "require_closing_paren": False,
        },
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    # Tau (if present) must not be wrapped with always(...)
    tau = (data.get("tau") or "").strip()
    assert not tau.lower().startswith("always (")
    # Englishified TCE should not start with "At all times,"
    tce_en = (data.get("tce") or "").strip()
    assert not tce_en.startswith("At all times,")


def test_temporal_mode_invariant_keeps_always_for_implication():
    client = _client()
    body = {
        "prompt": "If payment is approved then the order is shipped",
        "temporal_mode": "invariant",
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    tau = (data.get("tau") or "").strip()
    # In invariant mode it's acceptable/preferred to have always(...)
    assert (tau == "") or tau.lower().startswith("always (")


