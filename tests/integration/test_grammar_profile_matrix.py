import os
import json
import subprocess


BASE = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")


def _call_api(prompt: str, grammar_id: str, grammar_version: str) -> dict:
    payload = json.dumps({
        "prompt": prompt,
        "mode": "assist",
        "grammar_id": grammar_id,
        "grammar_version": grammar_version,
    })
    res = subprocess.run(
        [
            "curl","-fsSL","-H","Content-Type: application/json","-X","POST",
            f"{BASE}/llm/prompt-to-spec","-d",payload
        ], capture_output=True, text=True, timeout=45)
    if res.returncode != 0:
        raise RuntimeError(f"HTTP call failed: rc={res.returncode} err={res.stderr}")
    return json.loads(res.stdout)


def _assert_tce_tau_ok(data: dict, prompt: str):
    tce = (data.get("tce") or "").strip()
    tau = (data.get("tau") or "").strip()
    assert tce.lower().startswith("at all times"), f"Bad TCE: {tce} for {prompt}"
    assert tau.lower().startswith("always ("), f"Bad Tau: {tau} for {prompt}"


def test_grammar_profile_matrix_smoke():
    prompts = [
        "Never send data over the network.",
        "Every user must have a profile.",
        "If a payment is approved then the order is shipped.",
        "Output always equals input at each time step.",
    ]
    grammars = [("tce","v1"),("tce","v2")]
    checked = 0
    for gid, gver in grammars:
        for p in prompts:
            d = _call_api(p, gid, gver)
            _assert_tce_tau_ok(d, p)
            checked += 1
    assert checked == len(grammars)*len(prompts)


