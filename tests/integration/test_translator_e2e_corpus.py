import os
import re
import json
import subprocess
import tempfile
from pathlib import Path

import pytest


TAU_BIN = Path("external/tau-lang/build-Release/tau").resolve()


def _call_api(base: str, prompt: str) -> dict:
    payload = json.dumps({"prompt": prompt, "mode": "assist"})
    res = subprocess.run(
        [
            "curl",
            "-fsSL",
            "-H",
            "Content-Type: application/json",
            "-X",
            "POST",
            f"{base}/llm/prompt-to-spec",
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


def _extract_predicates(tau_text: str):
    # Find occurrences of name[0](), name[0](x), name[0](x,y,...)
    preds = {}
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\[0\]\(([^)]*)\)", tau_text):
        name = m.group(1)
        args = m.group(2).strip()
        if not args:
            arity = 0
        else:
            arity = len([a for a in args.split(',') if a.strip()])
        preds[name] = max(preds.get(name, 0), arity)
    return preds  # {name: max_arity}


def _sat_with_tau(tau: str) -> tuple[bool, str]:
    # Define predicates to satisfy the formula when possible:
    # - Default True for positive invariants
    # - Set False for predicates that appear immediately under negation '!' to satisfy negated invariants
    defs = _extract_predicates(tau)
    # Collect negated predicate names
    negated: set[str] = set(re.findall(r"!\s*([A-Za-z_][A-Za-z0-9_]*)\[0\]\(", tau))
    with tempfile.NamedTemporaryFile("w", suffix=".cmd", delete=False) as tf:
        for name, ar in defs.items():
            val = "F" if name in negated else "T"
            if ar == 0:
                tf.write(f"{name}[0]() := {val}.\n")
            elif ar == 1:
                tf.write(f"{name}[0](x) := {val}.\n")
            elif ar == 2:
                tf.write(f"{name}[0](x,y) := {val}.\n")
            else:
                # Define up to 3 args; beyond 3, coerce to 3 for testing
                vars_ = ",".join([chr(120 + i) for i in range(min(3, ar))])
                tf.write(f"{name}[0]({vars_}) := {val}.\n")
        tf.write(f"sat {tau}\n")
        tf.write("quit\n")
        tf.flush()
        cmd = tf.name
    try:
        proc = subprocess.run(
            [str(TAU_BIN)],
            stdin=open(cmd, "r"),
            capture_output=True,
            text=True,
            timeout=30,
        )
    finally:
        try:
            os.unlink(cmd)
        except OSError:
            pass
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    out_stripped = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", out)
    sat = re.findall(r"%\d+:\s*([TF])", out_stripped)
    return (bool(sat) and sat[-1] == 'T', out)


@pytest.mark.skipif(not TAU_BIN.exists(), reason="Tau binary not built at external/tau-lang/build-Release/tau")
def test_e2e_prompt_corpus_expanded():
    base = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")
    prompts = [
        # Invariants (negation)
        "Don't process contraband bits.",
        "Never send data over the network.",
        "Must not accept expired tokens.",
        # Causal (implication)
        "If a payment is approved then the order is shipped.",
        "If sensor is high or manual override is on then the alarm turns on, always.",
        # Quantifiers
        "Every user must have a profile.",
        "There exists a session for each login.",
        # Temporal
        "After a failure, retry immediately.",
        "Before midnight, do not payout.",
        # Guards
        "If the system is live then process orders unless maintenance.",
        # Coordination
        "If the door is locked and a valid code is entered then the door unlocks.",
    ]

    for p in prompts:
        data = _call_api(base, p)
        tau = (data.get("tau") or "").strip()
        tce = (data.get("tce") or "").strip()
        # TCE is controlled English: should start with "At all times," and contain no symbolic tokens
        assert tce.lower().startswith("at all times"), f"TCE must be controlled English starting with 'At all times,': {tce} for prompt: {p}"
        assert all(sym not in tce for sym in ["->", "&&", "||", "always (", "(", ")", "!"]), f"TCE should not contain symbolic tokens: {tce}"
        assert tau, f"Tau missing for prompt: {p} (tce={tce})"
        # Shape checks
        assert tau.lower().startswith("always ("), f"Tau must be always(...): {tau}"
        # Balanced parens
        bal = 0
        for ch in tau:
            if ch == '(': bal += 1
            elif ch == ')': bal -= 1
            assert bal >= 0, f"Parens underflow in: {tau}"
        assert bal == 0, f"Parens not balanced in: {tau}"
        # Tokens sanity
        assert any(tok in tau for tok in ["->", "!", "&&", "||", "all ", "ex ", "=", "!=", "["]), f"No logical tokens found in Tau: {tau}"
        # Tau acceptance
        ok, out = _sat_with_tau(tau)
        assert ok, f"Tau rejected by Tau REPL for prompt: {p}\n{out}\nTau: {tau}"


