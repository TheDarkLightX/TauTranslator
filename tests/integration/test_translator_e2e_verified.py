import os
import json
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

from tools.generate_tau_corpus import build_corpus


TAU_BIN = Path("external/tau-lang/build-Release/tau").resolve()


@pytest.mark.skipif(not TAU_BIN.exists(), reason="Tau binary not built")
def test_translator_matches_verified_tau_subset():
    corpus = build_corpus(max_entries=80)

    # Focus on entries that have at least one prompt and are expected SAT
    candidates = [e for e in corpus if e.prompts and e.expected_sat]
    assert candidates, "No corpus entries with prompts"

    # Translator endpoint (assumes local dev server or Fly.io): allow override by env
    base = os.environ.get("TRANSLATOR_BASE", "http://localhost:8000")
    url = f"{base}/llm/prompt-to-spec"

    # Use curl to avoid bringing HTTP libs; keep this lightweight
    checked = 0
    for entry in candidates[:20]:  # small subset for smoke
        prompt = entry.prompts[0]
        payload = json.dumps({"prompt": prompt, "mode": "assist"})

        proc = subprocess.run(
            ["curl", "-fsSL", "-H", "Content-Type: application/json", "-X", "POST", url, "-d", payload],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"HTTP call failed: {proc.stderr}"
        data = json.loads(proc.stdout)
        # Prefer tau; else take tce and convert simple normalization
        tau_out = data.get("tau") or ""
        tce_out = data.get("tce") or ""
        assert (tau_out or tce_out), f"No spec returned for prompt: {prompt} ({entry.id})"

        # Sat-check the translator's tau using REPL (if only TCE returned, rely on simple normalization in backend)
        translator_tau = tau_out.strip()
        if translator_tau:
            # Tau may be returned as always(...) or raw expression; keep it as-is
            with tempfile.NamedTemporaryFile("w", suffix=".cmd", delete=False) as tf:
                for d in entry.defs:
                    tf.write(d + "\n")
                tf.write(f"sat {translator_tau}\n")
                tf.write("quit\n")
                tf.flush()
                cmd_path = tf.name
            try:
                r = subprocess.run([str(TAU_BIN)], stdin=open(cmd_path, "r"), capture_output=True, text=True, timeout=25)
            finally:
                try:
                    os.unlink(cmd_path)
                except OSError:
                    pass
            out = (r.stdout or "") + "\n" + (r.stderr or "")
            out_stripped = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", out)
            ok = re.findall(r"%\d+:\s*([TF])", out_stripped)
            assert ok and ok[-1] == 'T', f"Translator Tau rejected by Tau:\n{out}\nInput prompt: {prompt}"

        # Optionally, we could compare structure equality with the verified ground truth, but
        # for now we ensure the translator emits a Tau that Tau itself accepts under the same defs.
        checked += 1

    assert checked > 0


