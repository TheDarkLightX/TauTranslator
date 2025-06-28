#!/usr/bin/env bash
# Build docs locally; used by CI as well.
set -euo pipefail

# Ensure we run from repo root
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR/.."

# 1. Generate API reference with pdoc (output to docs/reference)
rm -rf docs/reference
pdoc src.tau_translator_omega.core_engine backend.api backend.security backend.tau_translator_server backend.main -o docs/reference

# 2. Build static site with MkDocs (outputs to site/)
mkdocs build --strict

echo "Docs generated successfully."
