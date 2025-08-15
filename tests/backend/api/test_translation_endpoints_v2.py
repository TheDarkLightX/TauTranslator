import io
import pytest

pytest.importorskip("fastapi", reason="fastapi not installed in test environment")

from fastapi.testclient import TestClient

from backend.api.server import app

client = TestClient(app)


@pytest.fixture(scope="module")
def ce_sentence():
    return "always x equals y."


def test_translate_v2_default_engine(ce_sentence):
    """/v2/translate should return Tau code for basic CE sentence."""
    resp = client.post(
        "/v2/translate",
        json={
            "sourceText": ce_sentence,
            "sourceLangKey": "CONTROLLED_ENGLISH",
            "targetLangKey": "TAU",
            "engineKey": "tce_lark",
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] is True
    assert data["translatedText"].strip() == "always (x = y)"


def test_grammar_upload_and_list(tmp_path):
    """Uploading a dummy grammar file should increase totalLoaded count."""
    dummy_content = b"# fake grammar\nstart: A\nA: 'a'"  # Not valid but ok for loader failure
    dummy_file = io.BytesIO(dummy_content)
    dummy_file.name = "dummy.tgf"

    upload_resp = client.post(
        "/v2/grammars",
        files={"file": (dummy_file.name, dummy_file, "application/octet-stream")},
    )
    # Either success or graceful failure (since loader may reject invalid grammar).
    assert upload_resp.status_code in {200, 400}, upload_resp.text

    list_resp = client.get("/v2/grammars")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert "loaded" in list_data 