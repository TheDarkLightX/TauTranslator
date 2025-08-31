from __future__ import annotations

import random
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.unified.api.llm_endpoints import router as llm_router


EXISTENCE_PHRASES = [
    "blue elephants exist",
    "there exists a key",
    "some user exists",
    "exists solution",
]


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(llm_router)
    return TestClient(app)


def test_property_existence_prompts_atemporal_no_always():
    client = _client()
    for _ in range(6):
        prompt = random.choice(EXISTENCE_PHRASES)
        body = {"prompt": prompt, "temporal_mode": "atemporal"}
        r = client.post("/llm/prompt-to-spec", json=body)
        assert r.status_code == 200
        data = r.json()
        tau = (data.get("tau") or "").strip()
        assert not tau.lower().startswith("always (")


