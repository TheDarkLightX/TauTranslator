import os
import re
import subprocess
import tempfile
from pathlib import Path


TAU_BIN = Path("external/tau-lang/build-Release/tau").resolve()


def _sat_cmd(tau: str, defs: list[str] | None = None) -> tuple[bool, str]:
    defs = defs or []
    with tempfile.NamedTemporaryFile("w", suffix=".cmd", delete=False) as tf:
        for d in defs:
            tf.write(d + "\n")
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


def test_unsat_smoke():
    if not TAU_BIN.exists():
        import pytest
        pytest.skip("Tau binary not built")

    cases = [
        ("always (all x (p[0](x) && !p[0](x)))", ["p[0](x) := T."]),
        ("always (a[0]() && !a[0]())", ["a[0]() := T."]),
    ]
    for tau, defs in cases:
        ok, out = _sat_cmd(tau, defs)
        assert not ok, f"Expected UNSAT but got SAT: {tau}\n{out}"


