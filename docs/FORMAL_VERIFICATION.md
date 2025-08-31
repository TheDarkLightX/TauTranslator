### Formal verification setup

- Required env vars:
  - `TAU_TGF_PATH`: Path to a Tau TGF grammar file supplied by the user
  - `TAU_BIN`: Path to the Tau executable (optional, only for end-to-end REPL checks)

- Policy:
  - We do not bundle or download IDNI Tau grammar/executable. Provide your own paths.
  - If `TAU_TGF_PATH` is missing, grammar-backed validation is disabled and the validator falls back to structural checks.

- Usage examples:
  - Syntax validation only:
    - `export TAU_TGF_PATH=/absolute/path/to/tau.tgf`
    - Run tests: `pytest -q tests/integration/test_p2s_tau_conformance.py`
  - REPL verification:
    - `export TAU_BIN=/absolute/path/to/tau`
    - `pytest -q tests/integration/test_formal_tau_checker.py`

- Notes:
  - See `.gitignore` for excluded IDNI asset paths. We only ignore IDNI-provided grammars/binaries; your own grammars are not ignored.
