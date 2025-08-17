import os
import json
import subprocess

from tools.generate_prompt_corpus_large import _make_spec_drafts, _make_long_spec_drafts


BASE = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")


def _call_api(prompt: str) -> dict:
    payload = json.dumps({"prompt": prompt, "mode": "assist"})
    res = subprocess.run(
        [
            "curl","-fsSL","-H","Content-Type: application/json","-X","POST",
            f"{BASE}/llm/prompt-to-spec","-d",payload
        ], capture_output=True, text=True, timeout=60)
    if res.returncode != 0:
        raise RuntimeError(f"HTTP call failed: {res.stderr}")
    return json.loads(res.stdout)


def test_spec_drafts_multi_sentence_smoke():
    drafts = _make_spec_drafts()
    checked = 0
    for d in drafts:
        data = _call_api(d)
        tce = (data.get("tce") or "").strip()
        tau = (data.get("tau") or "").strip()
        assert tce.lower().startswith("at all times"), f"TCE not controlled-English: {tce} for {d}"
        assert tau.lower().startswith("always ("), f"Tau not always(...): {tau} for {d}"
        checked += 1
    assert checked == len(drafts)


def test_long_spec_drafts_with_structural_checks():
    drafts = _make_long_spec_drafts()
    checked = 0
    for d in drafts:
        data = _call_api(d)
        tce = (data.get("tce") or "").strip()
        tau = (data.get("tau") or "").strip()
        assert tce.lower().startswith("at all times"), f"TCE not controlled-English: {tce} for {d[:60]}..."
        assert tau.lower().startswith("always ("), f"Tau not always(...): {tau}"
        # Structural sanity: must include at least one implication or quantifier in long drafts
        has_op = any(tok in tau for tok in ["->","all ","ex ","&&","||"])
        assert has_op, f"Long spec Tau lacks structure: {tau}"
        checked += 1
    assert checked == len(drafts)


