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
for _p in (_project_root, _src_path):
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