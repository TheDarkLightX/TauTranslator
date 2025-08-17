import os
import json
import subprocess

try:
    from hypothesis import given, settings, strategies as st
    HYP_AVAILABLE = True
except Exception:
    HYP_AVAILABLE = False


BASE = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")


def _call_api(prompt: str) -> dict:
    payload = json.dumps({"prompt": prompt, "mode": "assist"})
    res = subprocess.run(
        ["curl","-fsSL","-H","Content-Type: application/json","-X","POST", f"{BASE}/llm/prompt-to-spec","-d", payload],
        capture_output=True, text=True, timeout=45,
    )
    if res.returncode != 0:
        raise RuntimeError(f"HTTP call failed: {res.stderr}")
    return json.loads(res.stdout)


def _sig(data: dict) -> tuple[bool,bool]:
    na = data.get("nlp_analysis") or {}
    causal = bool(na.get("causality") or na.get("implication"))
    neg = bool(na.get("negation") or na.get("negate"))
    tau = (data.get("tau") or "").lower()
    if tau:
        causal = causal or ("->" in tau)
        neg = neg or ("!" in tau or " not " in tau)
    return causal, neg


def _shape_ok(data: dict) -> bool:
    tce = (data.get("tce") or "").strip()
    tau = (data.get("tau") or "").strip()
    if not tce.lower().startswith("at all times"): return False
    if not tau.lower().startswith("always ("): return False
    bal = 0
    for ch in tau:
        if ch == '(': bal += 1
        elif ch == ')': bal -= 1
        if bal < 0: return False
    return bal == 0


def _paraphrase(p: str) -> str:
    # simple paraphrase: case normalize and add a soft adverbial
    base = p.strip().capitalize()
    if base.endswith('.'):
        base = base[:-1]
    return f"Always, {base} please."


if HYP_AVAILABLE:

    @settings(max_examples=8, deadline=None)
    @given(
        st.sampled_from([
            "Never send data over the network.",
            "Do not process contraband bits.",
            "Every user must have a profile.",
            "There exists a session for each login.",
            "If a payment is approved then the order is shipped.",
            "If sensor is high or manual override is on then the alarm turns on, always.",
            "Output always equals input at each time step.",
        ])
    )
    def test_property_shape_and_stability(prompt: str):
        d1 = _call_api(prompt)
        d2 = _call_api(_paraphrase(prompt))
        assert _shape_ok(d1), f"bad shape: {d1}"
        assert _shape_ok(d2), f"bad shape: {d2}"
        c1, n1 = _sig(d1)
        c2, n2 = _sig(d2)
        # property: paraphrase should not flip core intent or negation
        assert c1 == c2, f"causal flip: {prompt} -> {_paraphrase(prompt)}"
        assert n1 == n2, f"negation flip: {prompt} -> {_paraphrase(prompt)}"
        # extra: diversity should not vanish entirely on paraphrase
        tau2 = (d2.get("tau") or "")
        has_logic = any(tok in tau2 for tok in ["->","!","&&","||","all ","ex ","=","!="]) 
        assert has_logic, f"tau lost logic tokens after paraphrase: {tau2}"
else:
    def test_hypothesis_not_installed_skip():
        import pytest
        pytest.skip("Hypothesis not installed")


