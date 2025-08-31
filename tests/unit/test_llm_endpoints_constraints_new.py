from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.unified.api.llm_endpoints import router as llm_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(llm_router)
    return TestClient(app)


def test_constraints_apply_and_messages_present():
    client = _client()
    body = {
        "prompt": "If payment is approved then the order is shipped:",
        "constraints": {
            "require_prefix": "always ",
            "require_closing_paren": True,
            "forbid_colon": True,
        },
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    # Endpoint returns English-ified TCE in 'tce', but reasons explicitly record gates applied.
    # Prefix and closing-paren may already be satisfied, but colon removal should apply.
    reasons = data.get("reasons") or []
    assert any("Removed colon per constraint" in s for s in reasons)
    # Tau should be non-empty (deterministic assist + acceptance fallback)
    tau = (data.get("tau") or "").strip()
    assert tau.startswith("always (")


def test_allowed_connectives_mapping_implies_and_or():
    client = _client()
    body = {
        "prompt": "if A implies B AND C OR D then proceed",
        "constraints": {
            "allowed_connectives": ["->", "and", "or"],
            "require_closing_paren": True,
        },
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    tau = (data.get("tau") or "")
    # Ensure normalization maps 'implies' → '->'
    assert "->" in tau


def test_prefix_does_not_break_when_already_wrapped():
    client = _client()
    body = {
        "prompt": "always (A -> B)",
        "constraints": {
            "require_prefix": "always ",
        },
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    # Even if prefix logic is lenient with spacing, result should still be a valid always(...)
    tau = (data.get("tau") or "")
    assert tau.lower().startswith("always (")


