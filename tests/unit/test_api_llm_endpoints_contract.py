from fastapi.testclient import TestClient
from backend.api.server import app


def test_p2s_happy_path(monkeypatch):
    # Stub builder to avoid filesystem
    from backend.unified.api import llm_endpoints as mod
    from backend.unified.core.result_enhanced import Success

    class StubBuilder:
        def __init__(self, path): pass
        def build_minimal(self, gid, ver):
            return Success(object())

    def stub_retrieve(pack, prompt, k):
        return Success([{"name": "implication", "summary": "if A then B", "examples": ["always (A -> B)"]}])

    class StubProvider:
        def __init__(self): self.model = "stub"
        def generate(self, req):
            from backend.unified.core.result_enhanced import Success
            return Success(type("Resp", (), {"text": "always (payment_approved -> order_shipped)", "usage": {}})())

    monkeypatch.setattr(mod, "GrammarKnowledgePackBuilder", StubBuilder)
    monkeypatch.setattr(mod, "retrieve_top_k", lambda *a, **k: Success(stub_retrieve(None, None, None).unwrap()))
    monkeypatch.setattr(mod, "get_provider", lambda key, name=None: StubProvider())

    client = TestClient(app)
    r = client.post("/llm/prompt-to-spec", json={"prompt": "If a payment is approved then the order is shipped."}, headers={"X-OpenRouter-Key": "sk-or-xyz"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    tce_out = data.get("tce", "")
    assert (tce_out.lower().startswith("always (") or tce_out.lower().startswith("at all times"))


def test_p2s_constraints_prefix_and_colon(monkeypatch):
    from backend.unified.api import llm_endpoints as mod
    from backend.unified.core.result_enhanced import Success

    class StubBuilder:
        def __init__(self, path): pass
        def build_minimal(self, gid, ver):
            return Success(object())

    def stub_retrieve(pack, prompt, k):
        return Success([{"name": "implication", "summary": "if A then B", "examples": ["always (A -> B)"]}])

    class StubProvider:
        def generate(self, req):
            from backend.unified.core.result_enhanced import Success
            return Success(type("Resp", (), {"text": "User: X\nTCE: always (A: then B)", "usage": {}})())

    monkeypatch.setattr(mod, "GrammarKnowledgePackBuilder", StubBuilder)
    monkeypatch.setattr(mod, "retrieve_top_k", lambda *a, **k: Success(stub_retrieve(None, None, None).unwrap()))
    monkeypatch.setattr(mod, "get_provider", lambda key, name=None: StubProvider())

    client = TestClient(app)
    payload = {
        "prompt": "X",
        "constraints": {"require_prefix": "always ", "forbid_colon": True}
    }
    r = client.post("/llm/prompt-to-spec", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    # Colon should be removed and prefix applied
    assert ":" not in data["tce"]


def test_s2p_happy_path():
    client = TestClient(app)
    r = client.post("/llm/spec-to-prompt", json={"spec_text": "always (T)", "spec_type": "tau"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert isinstance(data.get("explanation"), str)


