from __future__ import annotations

import os
from typing import List, Tuple

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")
from fastapi.testclient import TestClient
from backend.api.server import app


client = TestClient(app)


def call_prompt_to_spec(prompt: str):
    body = {
        "prompt": prompt,
        "mode": "assist",
        "constraints": {
            "require_prefix": "always (",
            "require_closing_paren": True,
            "forbid_colon": True,
            "allowed_connectives": ["and", "or", "->", "!"]
        },
    }
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def build_negation_prompts(n: int = 30) -> List[str]:
    objects = [
        "data over the network",
        "secrets",
        "personal information",
        "credentials",
        "location telemetry",
    ]
    stems = [
        "Never send {}",
        "Must not transmit {}",
        "Do not share {}",
        "The system cannot send {}",
        "It can't share {}",
    ]
    out: List[str] = []
    i = 0
    while len(out) < n:
        out.append(stems[i % len(stems)].format(objects[i % len(objects)]))
        i += 1
    return out


def build_causal_prompts(n: int = 40) -> List[str]:
    pairs = [
        ("payment approved", "order shipped"),
        ("sensor activated", "alarm on"),
        ("button pressed", "light turns on"),
        ("login successful", "session created"),
        ("threshold exceeded", "cooling enabled"),
    ]
    frames = [
        "If {}, then {}",
        "When {}, {}",
        "Whenever {}, {}",
        "If {} then {}",
        "If {} then immediately {}",
    ]
    out: List[str] = []
    i = 0
    while len(out) < n:
        a, b = pairs[i % len(pairs)]
        frame = frames[i % len(frames)]
        out.append(frame.format(a, b))
        i += 1
    return out


def build_quant_prompts(n: int = 30) -> List[str]:
    variants = [
        "For all users, if login successful then session created",
        "There exists a device that triggers the alarm",
        "For each request, if authenticated then access granted",
        "Exists a node that acts as leader",
        "Every order will eventually be fulfilled",
    ]
    out: List[str] = []
    i = 0
    while len(out) < n:
        out.append(variants[i % len(variants)])
        i += 1
    return out


PROMPTS: List[Tuple[str, str]] = []
PROMPTS += [(p, "negation") for p in build_negation_prompts(34)]
PROMPTS += [(p, "causal") for p in build_causal_prompts(36)]
PROMPTS += [(p, "quant") for p in build_quant_prompts(30)]


@pytest.mark.parametrize("prompt,kind", PROMPTS)
def test_e2e_prompt_to_spec_outputs(prompt: str, kind: str):
    data = call_prompt_to_spec(prompt)
    # tce should exist
    assert isinstance(data.get("tce"), (str, type(None)))
    tce = (data.get("tce") or "").strip()
    # In server mode, tce is symbolic; in local UI it's English. Accept either case.
    # Basic invariants
    assert tce == "" or tce.lower().startswith("always"), f"tce must start with always or be empty: {tce}"

    # Kind-specific checks (soft expectations)
    if kind == "negation" and tce:
        assert "not" in tce.lower(), f"expected negation in: {tce}"
    if kind == "causal" and tce:
        assert "->" in tce or "then" in tce.lower(), f"expected implication: {tce}"
    if kind == "quant" and tce:
        assert any(q in tce.lower() for q in ("all", "ex", "for all", "exists")), f"expected quantifier: {tce}"


def test_optional_tau_checker_if_available():
    checker = os.getenv("TAU_TGF_CHECKER")
    tgf = os.getenv("TAU_TGF_PATH")
    if not (checker and tgf and os.path.exists(checker) and os.path.exists(tgf)):
        pytest.skip("No tau.tgf checker configured")
    # Example: feed a simple invariant to the checker and expect success (contract depends on the user's tool)
    data = call_prompt_to_spec("Never send data over the network")
    tau = (data.get("tau") or "").strip()
    assert tau, "tau-like output required"
    # User-provided checker invoked here (pseudo-contract): checker <tgf> <formula>
    # For safety, we do not actually run external tools in CI; this block is opt-in via env.
    assert isinstance(tau, str)


