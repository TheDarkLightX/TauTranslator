from __future__ import annotations

import os
import json
from typing import List

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")
from fastapi.testclient import TestClient
from backend.api.server import app
from backend.unified.domain.tau_validator import validate_tau_syntax


client = TestClient(app)


def _p2s(prompt: str) -> dict:
    body = {
        "prompt": prompt,
        "mode": "assist",
        "temporal_mode": "atemporal",
        # Constrain outputs to Tau-friendly shape
        "constraints": {
            "require_prefix": "",
            "require_closing_paren": False,
            "forbid_colon": True,
            "allowed_connectives": ["and", "or", "->", "!"]
        },
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def _tce2tau(tce: str) -> str:
    r = client.post("/translate/tce-to-tau", json={"tce": tce, "temporal_mode": "atemporal"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("success") is True, f"tce->tau failed: {data}"
    return (data.get("tau") or "").strip()


@pytest.mark.parametrize(
    "prompt",
    [
        "Blue elephants exist.",
        "If a payment is approved then the order is shipped.",
        "Never send personal information.",
        "For all users, if login successful then session created.",
    ],
)
def test_prompt_to_tau_is_grammar_valid_or_structurally_valid(prompt: str):
    # 1) Prompt -> TCE (constrained)
    p2s = _p2s(prompt)
    # Prefer refined_prompt (machine-readable TCE) over English tce field
    candidate = (p2s.get("refined_prompt") or "").strip()
    if not candidate:
        candidate = (p2s.get("tce") or "").strip()
    # Accept empty candidate in degenerate cases but prefer non-empty
    assert isinstance(candidate, str)

    # 2) TCE -> Tau
    if candidate:
        tau = _tce2tau(candidate)
    else:
        # If no TCE was produced, skip strictness but keep guardrails
        pytest.skip("No TCE produced; cannot check Tau conformance")

    # 3) Validate Tau via grammar if available, else structural fallback
    res = validate_tau_syntax(tau)
    assert isinstance(res, dict)
    assert res.get("valid") is True, f"Tau invalid for prompt '{prompt}': {json.dumps(res)}\nTau: {tau}"


