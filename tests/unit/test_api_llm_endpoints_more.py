from fastapi.testclient import TestClient
from backend.api.server import app


def _stub_builder(monkeypatch):
    from backend.unified.api import llm_endpoints as mod
    from backend.unified.core.result_enhanced import Success

    class StubBuilder:
        def __init__(self, path): pass
        def build_minimal(self, gid, ver):
            return Success(object())

    def stub_retrieve(pack, prompt, k):
        return Success([{"name": "implication", "summary": "if A then B", "examples": ["always (A -> B)"]}])

    monkeypatch.setattr(mod, "GrammarKnowledgePackBuilder", StubBuilder)
    monkeypatch.setattr(mod, "retrieve_top_k", lambda *a, **k: Success(stub_retrieve(None, None, None).unwrap()))
    return mod


def test_p2s_provider_failure(monkeypatch):
    mod = _stub_builder(monkeypatch)

    class FailProvider:
        def generate(self, req):
            from backend.unified.core.result_enhanced import Failure
            return Failure("OPENROUTER_HTTP_500", "oops")

    monkeypatch.setattr(mod, "get_provider", lambda key, name=None: FailProvider())
    client = TestClient(app)
    r = client.post("/llm/prompt-to-spec", json={"prompt": "X"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False


def test_p2s_synonym_and_constraints_normalization(monkeypatch):
    mod = _stub_builder(monkeypatch)

    class Prov:
        def __init__(self): self.model = "stub"
        def generate(self, req):
            from backend.unified.core.result_enhanced import Success
            # Embed synonyms and colon to exercise constraints
            txt = "always (A implies B AND C OR D):"
            return Success(type("Resp", (), {"text": txt, "usage": {}})())

    monkeypatch.setattr(mod, "get_provider", lambda key, name=None: Prov())
    client = TestClient(app)
    payload = {
        "prompt": "X",
        "constraints": {
            "forbid_colon": True,
            "allowed_connectives": ["->", "and", "or"],
        }
    }
    r = client.post("/llm/prompt-to-spec", json=payload)
    assert r.status_code == 200
    data = r.json()
    # Expect colon removed and tau output present
    assert ":" not in data.get("tce", "")
    tau = data.get("tau", "")
    # Structural check: tau-like always (...) even if synonyms normalized to atoms
    assert isinstance(tau, str) and tau.lower().startswith("always (") and tau.endswith(")")


