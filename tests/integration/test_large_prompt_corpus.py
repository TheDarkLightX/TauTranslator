import os
import json
import subprocess
from tools.generate_prompt_corpus_large import as_dicts


BASE = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")


def _call_api(prompt: str) -> dict:
    payload = json.dumps({"prompt": prompt, "mode": "assist"})
    res = subprocess.run(
        [
            "curl",
            "-fsSL",
            "-H",
            "Content-Type: application/json",
            "-X",
            "POST",
            f"{BASE}/llm/prompt-to-spec",
            "-d",
            payload,
        ],
        capture_output=True,
        text=True,
        timeout=45,
    )
    if res.returncode != 0:
        raise RuntimeError(f"HTTP call failed: rc={res.returncode} err={res.stderr}")
    return json.loads(res.stdout)


def test_large_prompt_corpus_smoke():
    corpus = as_dicts(limit=5000)
    # Sample N prompts per category to keep runtime reasonable
    per_cat = 25
    buckets = {}
    for item in corpus:
        buckets.setdefault(item["category"], []).append(item)
    checked = 0
    for cat, items in buckets.items():
        for it in items[:per_cat]:
            data = _call_api(it["text"])  # live API
            tce = (data.get("tce") or "").strip()
            tau = (data.get("tau") or "").strip()
            assert tce.lower().startswith("at all times"), f"Bad TCE ({cat}): {tce} for {it['text']}"
            assert tau.lower().startswith("always ("), f"Bad Tau ({cat}): {tau} for {it['text']}"
            checked += 1
    assert checked >= per_cat * len(buckets)


