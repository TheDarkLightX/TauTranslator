import os
import json
import subprocess


BASE = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")


def _call_api(prompt: str) -> dict:
    payload = json.dumps({"prompt": prompt, "mode": "assist"})
    res = subprocess.run([
        "curl","-fsSL","-H","Content-Type: application/json","-X","POST",
        f"{BASE}/llm/prompt-to-spec","-d", payload
    ], capture_output=True, text=True, timeout=45)
    if res.returncode != 0:
        raise RuntimeError(f"HTTP call failed: {res.stderr}")
    return json.loads(res.stdout)


def _deterministic_path(prompt: str) -> dict:
    # Force constraints to reduce ambiguity; acts as a second path
    payload = json.dumps({
        "prompt": prompt,
        "mode": "assist",
        "constraints": {"require_prefix": "always ", "require_closing_paren": True, "forbid_colon": True}
    })
    res = subprocess.run([
        "curl","-fsSL","-H","Content-Type: application/json","-X","POST",
        f"{BASE}/llm/prompt-to-spec","-d", payload
    ], capture_output=True, text=True, timeout=45)
    if res.returncode != 0:
        raise RuntimeError(f"HTTP call failed: {res.stderr}")
    return json.loads(res.stdout)


def test_ambiguity_detection_branches():
    # Ambiguous negation scope example; ensure both paths agree or ambiguity is reported
    prompt = "Do not ship orders with risk."
    a = _call_api(prompt)
    b = _deterministic_path(prompt)
    # Accept if tau matches, or if ambiguity score is surfaced
    tau_a = (a.get("tau") or "").strip()
    tau_b = (b.get("tau") or "").strip()
    if tau_a and tau_b:
        assert tau_a.lower().startswith("always (") and tau_b.lower().startswith("always ("), "bad shape"
        if tau_a != tau_b:
            # require ambiguity score present in either path
            amb_a = a.get("ambiguity_score")
            amb_b = b.get("ambiguity_score")
            assert (amb_a is not None) or (amb_b is not None), f"disagreement without ambiguity surfaced: {tau_a} vs {tau_b}"
    else:
        assert a.get("ambiguity_score") is not None or b.get("ambiguity_score") is not None


