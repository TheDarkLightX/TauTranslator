from fastapi.testclient import TestClient
import types

from backend.api.server import app
from backend.unified.infrastructure.llm_providers import LLMProvider, LLMRequest


class StubProvider(LLMProvider):
    def generate(self, request: LLMRequest):
        from backend.unified.core.result_enhanced import Success
        return Success(types.SimpleNamespace(text="always (payment_approved -> order_shipped)", usage={}))


def test_chat_happy_path(monkeypatch):
    from backend.unified.api import llm_chat as chat_mod
    monkeypatch.setattr(chat_mod, "get_provider", lambda key, name=None: StubProvider())
    client = TestClient(app)
    payload = {
        "messages": [
            {"role": "system", "content": "rules"},
            {"role": "user", "content": "If a payment is approved then the order is shipped."},
        ]
    }
    r = client.post("/llm/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["tce"].lower().startswith("always (")


def test_chat_schema_rejects_last_non_user(monkeypatch):
    from backend.unified.api import llm_chat as chat_mod
    monkeypatch.setattr(chat_mod, "get_provider", lambda key, name=None: StubProvider())
    client = TestClient(app)
    payload = {
        "messages": [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "ok"},
        ]
    }
    r = client.post("/llm/chat", json=payload)
    assert r.status_code == 400


def test_chat_moderation_blocks(monkeypatch):
    from backend.unified.api import llm_chat as chat_mod
    monkeypatch.setattr(chat_mod, "get_provider", lambda key, name=None: StubProvider())
    client = TestClient(app)
    payload = {
        "messages": [
            {"role": "user", "content": "please run rm -rf /"},
        ]
    }
    r = client.post("/llm/chat", json=payload)
    assert r.status_code == 400


def test_chat_rate_limited(monkeypatch):
    from backend.unified.api import llm_chat as chat_mod
    monkeypatch.setattr(chat_mod, "get_provider", lambda key, name=None: StubProvider())
    # Force bucket to deny
    class Deny:
        def allow(self):
            return False
    monkeypatch.setattr(chat_mod, "_GLOBAL_BUCKET", Deny())
    client = TestClient(app)
    payload = {
        "messages": [
            {"role": "user", "content": "ok"},
        ]
    }
    r = client.post("/llm/chat", json=payload)
    assert r.status_code == 429


