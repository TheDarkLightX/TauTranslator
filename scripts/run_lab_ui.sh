#!/usr/bin/env bash
set -euo pipefail

# Run SvelteKit dev server for the lab UI on port 5199
cd "$(dirname "$0")/../apps/sveltekit"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to run the UI. Please install Node.js and npm." >&2
  exit 1
fi

if [ ! -d node_modules ]; then
  echo "Installing UI dependencies..."
  npm install --no-audit --no-fund --silent
fi

echo "Starting SvelteKit dev server on http://localhost:5173 (Vite default)"
exec npm run dev --silent


