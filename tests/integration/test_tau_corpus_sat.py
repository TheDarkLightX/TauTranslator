import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

from tools.generate_tau_corpus import build_corpus


TAU_BIN = Path("external/tau-lang/build-Release/tau").resolve()


@pytest.mark.skipif(not TAU_BIN.exists(), reason="Tau binary not built at external/tau-lang/build-Release/tau")
def test_corpus_sat_smoke():
    corpus = build_corpus(max_entries=120)
    assert len(corpus) > 0

    # Run a subset to keep CI time reasonable; expand locally as needed
    sample = corpus[:50]
    for entry in sample:
        with tempfile.NamedTemporaryFile("w", suffix=".cmd", delete=False) as tf:
            # Write definitions
            for d in entry.defs:
                tf.write(d + "\n")
            # Write sat check on entry.tau
            tf.write(f"sat {entry.tau}\n")
            tf.write("quit\n")
            tf.flush()
            cmd_path = tf.name

        try:
            proc = subprocess.run(
                [str(TAU_BIN)],
                stdin=open(cmd_path, "r"),
                capture_output=True,
                text=True,
                timeout=20,
            )
        finally:
            try:
                os.unlink(cmd_path)
            except OSError:
                pass

        # Tau returns lines like "%1: T" or "%2: F"; strip ANSI escapes and take last match
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        out_stripped = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", out)
        matches = re.findall(r"%\d+:\s*([TF])", out_stripped)
        ok = bool(matches) and matches[-1] == 'T'
        if entry.expected_sat:
            assert ok, f"Expected SAT for {entry.id}, got output:\n{out}"
        else:
            assert not ok, f"Expected UNSAT for {entry.id}, got output:\n{out}"


