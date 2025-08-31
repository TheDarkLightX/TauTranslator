#!/usr/bin/env bash
set -euo pipefail

# Simple helper to run example Tau REPL commands from a file.
# Usage: scripts/tau_examples.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TAU_BIN_DEFAULT="$REPO_ROOT/external/tau-lang/build-Release/tau"
TAU_BIN="${TAU_BIN:-$TAU_BIN_DEFAULT}"

if [[ ! -x "$TAU_BIN" ]]; then
  echo "Tau binary not executable: $TAU_BIN" >&2
  exit 3
fi

TMP_FILE="$(mktemp /tmp/tau_examples.XXXXXX.tau)"
cat >"$TMP_FILE" <<'EOF'
# You can add REPL commands or WFFs here; each command/wff ends with a dot.
# Examples:
sat ex x (blue(x) && elephant(x)).
sat always (all u (payment_approved(u) -> order_shipped(u))).
q
EOF

echo "Running Tau with: $TMP_FILE"
"$TAU_BIN" < "$TMP_FILE"
EC=$?
echo "Exit code: $EC"
rm -f "$TMP_FILE"
exit $EC


