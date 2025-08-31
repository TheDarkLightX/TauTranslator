from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.unified.api.llm_endpoints import router as llm_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(llm_router)
    return TestClient(app)


def test_sanitize_user_block_and_englishify():
    client = _client()
    # The default provider is EchoProvider which returns always(prompt),
    # so include an 'always (...)' style prompt to verify englishifying.
    body = {"prompt": "always (A -> B)"}
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    tce = (data.get("tce") or "")
    assert tce.startswith("At all times,")  # englishified TCE


def test_negation_contraband_bits_maps_to_universal_negation():
    client = _client()
    body = {"prompt": "Do not process any contraband bits"}
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    tau = (data.get("tau") or "")
    assert "process_contraband_bits" in tau
    assert tau.lower().startswith("always (")


def test_never_send_private_data_maps_to_send_over_network_negation():
    client = _client()
    body = {"prompt": "Never send private data over the network"}
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    tau = (data.get("tau") or "")
    assert "send_over_network" in tau


def test_exists_session_for_each_login_quantified_mapping():
    client = _client()
    body = {"prompt": "There exists a session for each login"}
    r = client.post("/llm/prompt-to-spec", json=body)
    assert r.status_code == 200
    data = r.json()
    tau = (data.get("tau") or "")
    # Accept variations, but ensure quantifiers appear
    assert ("all" in tau) or ("ex" in tau)


