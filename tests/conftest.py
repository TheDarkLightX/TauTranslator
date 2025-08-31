"""Global pytest configuration for TauTranslator test suite.

This file ensures the TauTranslator source packages are importable during test
execution (both local and CI) and registers any custom pytest markers used by
our suite.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure project root and `src/` are on PYTHONPATH so backend & core packages
# such as `tau_translator_omega` import correctly even when the project has
# not been installed in editable mode inside the test virtualenv.
# ---------------------------------------------------------------------------
_project_root = Path(__file__).resolve().parents[1]
_src_path = _project_root / "src"

# When running under mutmut, tests are mirrored into <repo>/mutants/tests/...
# In that case, the real project root is two levels above this conftest.
_maybe_mutants_root = Path(__file__).resolve().parents
_real_root = None
try:
    if len(_maybe_mutants_root) >= 3 and _maybe_mutants_root[1].name == "tests" and _maybe_mutants_root[2].name == "mutants":
        _real_root = _maybe_mutants_root[3]
except Exception:
    _real_root = None

for _p in filter(None, {_project_root, _src_path, _real_root}):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# ---------------------------------------------------------------------------
# Register custom markers to avoid PytestUnknownMarkWarning
# ---------------------------------------------------------------------------

def pytest_configure(config):  # noqa: D401
    config.addinivalue_line(
        "markers",
        "complexity: marks tests belonging to the English→Tau translation complexity ladder",
    )


# If we later split common fixtures into separate modules we can list them here
pytest_plugins: list[str] = []


# ---------------------------------------------------------------------------
# Mutation-test friendly collection filter
# When running under mutmut (working dir contains 'mutants'), only keep a
# whitelisted subset of tests to avoid collecting legacy/experimental suites.
# ---------------------------------------------------------------------------
def pytest_collection_modifyitems(config, items):  # noqa: D401
    try:
        cwd_parts = set(str(Path.cwd()).split("/"))
        if "mutants" in cwd_parts:
            allowed_files = {
                "test_api_llm_chat_contract.py",
                "test_api_llm_endpoints_contract.py",
                "test_tce_endpoints_contract.py",
                "test_server_misc_endpoints.py",
                "test_llm_providers_openrouter.py",
                "test_subset.py",
            }
            kept = [it for it in items if it.location and it.location[0].split("/")[-1] in allowed_files]
            deselected = [it for it in items if it not in kept]
            if deselected:
                config.hook.pytest_deselected(items=deselected)
            items[:] = kept
    except Exception:
        # Never break collection due to filtering logic
        pass


def pytest_ignore_collect(path, config):  # noqa: D401
    # Prevent importing non-whitelisted tests when running inside mutmut's
    # working directory where all tests are mirrored (mutants/tests/...).
    try:
        cwd_parts = set(str(Path.cwd()).split("/"))
        if "mutants" not in cwd_parts:
            return False
        allowed_files = {
            "test_api_llm_chat_contract.py",
            "test_api_llm_endpoints_contract.py",
            "test_tce_endpoints_contract.py",
            "test_server_misc_endpoints.py",
            "test_llm_providers_openrouter.py",
            "test_subset.py",
        }
        p = Path(str(path))
        # Always allow our subset directory
        if "mutmut_subset" in p.parts:
            return False
        # For directories under mutants/tests, only traverse our subset dir
        if p.is_dir():
            return False if "mutmut_subset" in p.parts else True
        if p.suffix == ".py" and p.name not in allowed_files:
            return True
    except Exception:
        return False
    return False