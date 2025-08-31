#!/usr/bin/env bash
set -euo pipefail

# Run the lab API (FastAPI + uvicorn) on port 8010
cd "$(dirname "$0")/.."

if ! command -v uvicorn >/dev/null 2>&1; then
  echo "uvicorn not found. Install deps in your venv (pip install -r requirements.txt)." >&2
  exit 1
fi

exec uvicorn backend.lab_api:app --host 127.0.0.1 --port 8010 --reload --log-level info


