import os
import re
import json
import tempfile
import subprocess
from pathlib import Path


TAU_BIN = Path("external/tau-lang/build-Release/tau").resolve()
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


def _sat_with_tau(tau: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".cmd", delete=False) as tf:
        # Stubs for First Law
        tf.write("injure[0](r,h) := F.\n")
        tf.write("risk_to[0](h) := T.\n")
        tf.write("can_prevent[0](r,h) := T.\n")
        tf.write("prevent_harm[0](r,h) := T.\n")
        tf.write(f"sat {tau}\n")
        tf.write("quit\n")
        tf.flush()
        cmd = tf.name
    try:
        proc = subprocess.run([str(TAU_BIN)], stdin=open(cmd, "r"), capture_output=True, text=True, timeout=30)
    finally:
        try:
            os.unlink(cmd)
        except OSError:
            pass
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    out_stripped = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", out)
    sat = re.findall(r"%\d+:\s*([TF])", out_stripped)
    return (bool(sat) and sat[-1] == 'T', out)


def test_first_law_prompt_to_tau_and_sat():
    prompt = "A robot may not injure a human or, through inaction, allow a human to come to harm."
    data = _call_api(prompt)
    tce = (data.get("tce") or "").strip()
    tau = (data.get("tau") or "").strip()
    assert tce.lower().startswith("at all times"), f"Bad TCE: {tce}"
    assert tau.lower().startswith("always ("), f"Bad Tau: {tau}"
    if TAU_BIN.exists():
        ok, out = _sat_with_tau(tau)
        assert ok, f"Tau UNSAT for First Law stubs:\n{out}\nTau: {tau}"


