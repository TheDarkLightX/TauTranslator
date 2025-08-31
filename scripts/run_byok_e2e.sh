#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
Usage: scripts/run_byok_e2e.sh [--save] [--chat|--workflows|--all]

Prompts for your OpenRouter API key securely and runs the BYOK Playwright test.

Options:
  --save   Save the key to ~/.secrets/openrouter_key (permissions 600)
  --chat         Run chat-only BYOK test (default)
  --workflows    Run comprehensive BYOK p2s/s2p/chat workflows test
  --all          Run both chat and workflows tests

Notes:
  - The key is exported only for this subprocess (not persisted in your shell).
  - If OPENROUTER_KEY is already set in the environment, prompt is skipped.
EOF
}

SAVE=0
MODE="chat" # chat | workflows | all
for arg in "$@"; do
  case "$arg" in
    -h|--help) show_help; exit 0 ;;
    --save) SAVE=1 ;;
    --chat) MODE="chat" ;;
    --workflows) MODE="workflows" ;;
    --all) MODE="all" ;;
    *) echo "Unknown arg: $arg" >&2; show_help; exit 2 ;;
  esac
done

KEY="${OPENROUTER_KEY:-}"
if [[ -z "$KEY" && -f "$HOME/.secrets/openrouter_key" ]]; then
  KEY="$(cat "$HOME/.secrets/openrouter_key")"
fi
if [[ -z "$KEY" ]]; then
  if [[ -t 0 ]]; then
    read -r -s -p "Enter OpenRouter Key (input hidden): " KEY; echo
  else
    echo "Error: no key provided and no ~/.secrets/openrouter_key. Set OPENROUTER_KEY or run with --save interactively." >&2
    exit 1
  fi
fi

if [[ -z "$KEY" ]]; then
  echo "Error: no key provided." >&2
  exit 1
fi

if [[ $SAVE -eq 1 ]]; then
  mkdir -p "$HOME/.secrets"
  chmod 700 "$HOME/.secrets"
  printf '%s' "$KEY" > "$HOME/.secrets/openrouter_key"
  chmod 600 "$HOME/.secrets/openrouter_key"
  echo "Saved to ~/.secrets/openrouter_key"
fi

# Activate venv if available
if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

declare -a TESTS
case "$MODE" in
  chat) TESTS=(tests/e2e/ui/test_llm_byok_chat.py) ;;
  workflows) TESTS=(tests/e2e/ui/test_llm_byok_workflows.py) ;;
  all) TESTS=(tests/e2e/ui/test_llm_byok_chat.py tests/e2e/ui/test_llm_byok_workflows.py) ;;
esac

echo "Running BYOK E2E ($MODE)..."
OPENROUTER_KEY="$KEY" pytest -q "${TESTS[@]}" || {
  code=$?
  echo "Test failed with exit code $code" >&2
  exit $code
}

echo "Done."


