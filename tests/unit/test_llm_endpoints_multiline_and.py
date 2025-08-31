from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")
from fastapi.testclient import TestClient
from backend.api.server import app


client = TestClient(app)


def test_p2s_multiline_and_conjoins_rules():
    body = {
        "prompt": "Never send data over the network.\nIf a payment is approved then the order is shipped.",
        "mode": "assist",
        "multiline_and": True,
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
    tce = (data.get("refined_prompt") or data.get("tce") or "").strip()
    assert tce.lower().startswith("always (")
    assert "&&" in tce or " and " in tce.lower()

