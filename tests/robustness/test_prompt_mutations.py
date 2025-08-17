import os
import json
import re
import random
import subprocess


BASE = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")


def _call_api(prompt: str, constraints: dict | None = None) -> dict:
    body = {"prompt": prompt, "mode": "assist"}
    if constraints:
        body["constraints"] = constraints
    payload = json.dumps(body)
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


_SYNONYMS = {
    "never": ["at no time", "under no circumstances"],
    "send": ["transmit", "forward"],
    "data": ["information"],
    "process": ["handle", "compute"],
    "contraband": ["forbidden", "illicit"],
    "bits": ["bits"],
    "every": ["each", "all"],
    "user": ["user"],
    "profile": ["account profile", "profile"],
    "approved": ["authorized"],
    "shipped": ["dispatched"],
    "output": ["output"],
    "input": ["input"],
}


def _mutate(prompt: str) -> list[str]:
    variants: list[str] = []
    words = re.findall(r"\w+|[^\w\s]", prompt)
    # synonym replacements
    for i, w in enumerate(words):
        wl = w.lower()
        if wl in _SYNONYMS:
            for s in _SYNONYMS[wl]:
                nw = words.copy(); nw[i] = s
                variants.append("".join(nw))
    # punctuation/noise
    variants.append(prompt + "!")
    variants.append("  " + prompt + "  ")
    # case tweaks
    variants.append(prompt.lower())
    variants.append(prompt.upper())
    # reorder adverbials
    if "always" in prompt.lower():
        variants.append("Always, " + prompt.rstrip("."))
    # de-duplicate and trim
    out = []
    seen = set()
    for v in variants:
        vv = " ".join(v.split())
        if vv not in seen:
            out.append(vv)
            seen.add(vv)
    # sample up to N variants
    random.shuffle(out)
    return out[:8]


def _assert_tce_tau_ok(data: dict):
    tce = (data.get("tce") or "").strip()
    tau = (data.get("tau") or "").strip()
    assert tce.lower().startswith("at all times"), f"TCE English bad: {tce}"
    assert tau.lower().startswith("always ("), f"Tau must be always(...): {tau}"
    # Balanced parens
    bal = 0
    for ch in tau:
        if ch == '(': bal += 1
        elif ch == ')': bal -= 1
        assert bal >= 0, f"Parens underflow in: {tau}"
    assert bal == 0, f"Parens not balanced in: {tau}"
    # Logical tokens present for nontrivial forms
    assert any(tok in tau for tok in ["->", "!", "&&", "||", "all ", "ex ", "=", "!=", "["]), f"Tau lacks logical tokens: {tau}"


def test_prompt_mutations_robustness():
    bases = [
        "Never send data over the network.",
        "Don't process contraband bits.",
        "Every user must have a profile.",
        "If a payment is approved then the order is shipped.",
        "Output always equals input at each time step.",
    ]
    for p in bases:
        variants = [p] + _mutate(p)
        for v in variants:
            data = _call_api(v)
            _assert_tce_tau_ok(data)


