"""
Tau runtime validation harness (external/optional).

This module lets our test suite validate Tau formulas or modules using an
external Tau interpreter without vendoring or linking to licensed code.

Usage contract (environment-driven):
- Set TAU_EVAL_CMD to a shell command that evaluates Tau input and returns
  exit code 0 on success (parse/validate) and non-zero on failure.
- The command may include a "{file}" placeholder. If present, the harness
  writes the input to a temporary file and substitutes its path.
- If no placeholder is present, the harness pipes the input via STDIN.

Examples:
- TAU_EVAL_CMD="/usr/local/bin/tau-eval --check -g /path/to/tau.tgf {file}"
- TAU_EVAL_CMD="docker run --rm -i my/tau:latest eval --check"

The harness only executes the user-provided command. It does not ship or
depend on Tau itself, preserving license boundaries.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class TauEvalResult:
    ok: bool
    returncode: int
    stdout: str
    stderr: str


def evaluate_with_tau(program_text: str, timeout_seconds: int = 15) -> TauEvalResult:
    """
    Evaluate Tau program/formula text using an external interpreter.

    The external command is read from the TAU_EVAL_CMD environment variable.
    See module docstring for the contract.
    """
    cmd = os.environ.get("TAU_EVAL_CMD", "").strip()
    if not cmd:
        raise RuntimeError(
            "TAU_EVAL_CMD is not set. Provide a command to evaluate Tau code."
        )

    uses_file = "{file}" in cmd
    if uses_file:
        with tempfile.NamedTemporaryFile("w", suffix=".tau", delete=False) as tf:
            tf.write(program_text)
            tf.flush()
            temp_path = tf.name
        try:
            replaced = cmd.replace("{file}", shlex.quote(temp_path))
            proc = subprocess.run(
                replaced,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
    else:
        proc = subprocess.run(
            cmd,
            shell=True,
            input=program_text,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

    ok = proc.returncode == 0
    return TauEvalResult(ok=ok, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def is_configured() -> bool:
    """Return True if TAU_EVAL_CMD is configured in the environment."""
    return bool(os.environ.get("TAU_EVAL_CMD", "").strip())


