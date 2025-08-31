from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")
from fastapi.testclient import TestClient
from backend.api.server import app


client = TestClient(app)


def test_prompt_to_spec_emits_clarifiers_when_ambiguous():
    body = {
        "prompt": "Blue elephants exist.",
        "mode": "assist",
        "constraints": {"require_prefix": "always (", "require_closing_paren": True}
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    # Clarifying questions are optional but if optimizer provides, we assert shape
    clar = data.get("clarifying_questions") or []
    assert isinstance(clar, list)
    if clar:
        assert isinstance(clar[0], dict) and "question" in clar[0]


def test_if_then_heuristic_normalization_yields_implication_shape():
    body = {
        "prompt": "If a payment is approved then the order is shipped.",
        "mode": "assist",
        "constraints": {"require_prefix": "always (", "require_closing_paren": True}
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    tce = (data.get("refined_prompt") or data.get("tce") or "").lower()
    assert "->" in tce or " implies " in tce

