from fastapi.testclient import TestClient
from backend.api.server import app


def test_s2p_heuristic_fallback(monkeypatch):
    # Force fallback by raising during AST-driven path by patching source module
    import backend.unified.domain.spec_to_prompt_ast as spa
    def boom(*a, **k):
        raise RuntimeError("fail")
    monkeypatch.setattr(spa, "build_spec_to_prompt", boom, raising=True)
    client = TestClient(app)
    r = client.post("/llm/spec-to-prompt", json={"spec_text": "always (p -> q)", "spec_type": "tau"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "It uses the 'always' modality" in data.get("explanation", "")

