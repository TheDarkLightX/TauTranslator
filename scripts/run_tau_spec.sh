#!/usr/bin/env bash
set -euo pipefail

# Usage:
#  scripts/run_tau_spec.sh --wff "ex x (blue(x) && elephant(x))"
#  scripts/run_tau_spec.sh --wff "always (all u (p(u) -> q(u)))" --mode snf
#  scripts/run_tau_spec.sh --file /path/to/program.tau
#  scripts/run_tau_spec.sh --wff-file /path/to/wff.txt
# Options:
#  --tau-bin PATH   Override tau executable path (default: external/tau-lang/build-Release/tau)
#  --mode MODE      REPL command to apply to WFF: snf|pnf|nnf|run (default: snf)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_TAU_BIN="$REPO_ROOT/external/tau-lang/build-Release/tau"

TAU_BIN="${TAU_BIN:-$DEFAULT_TAU_BIN}"
MODE="snf"
WFF=""
FILE_INPUT=""
WFF_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tau-bin)
      TAU_BIN="$2"; shift 2;;
    --mode)
      MODE="$2"; shift 2;;
    --wff)
      WFF="$2"; shift 2;;
    --file)
      FILE_INPUT="$2"; shift 2;;
    --wff-file)
      WFF_FILE="$2"; shift 2;;
    -h|--help)
      echo "Usage: $0 [--tau-bin PATH] [--mode snf|pnf|nnf|run] --wff FORMULA | --file FILE | --wff-file FILE"; exit 0;;
    *)
      echo "Unknown option: $1" >&2; exit 2;;
  esac
done

if [[ ! -x "$TAU_BIN" ]]; then
  echo "Tau binary not executable: $TAU_BIN" >&2
  exit 3
fi

# Build payload to feed the REPL
PAYLOAD=""
if [[ -n "$WFF" ]]; then
  PAYLOAD+="$MODE $WFF. q\n"
elif [[ -n "$WFF_FILE" ]]; then
  if [[ ! -f "$WFF_FILE" ]]; then echo "No such wff file: $WFF_FILE" >&2; exit 4; fi
  mapfile -t lines < "$WFF_FILE"
  for ln in "${lines[@]}"; do
    [[ -z "$ln" ]] && continue
    PAYLOAD+="$MODE $ln.\n"
  done
  PAYLOAD+="q\n"
elif [[ -n "$FILE_INPUT" ]]; then
  if [[ ! -f "$FILE_INPUT" ]]; then echo "No such file: $FILE_INPUT" >&2; exit 5; fi
  # Pass file content as-is; ensure it ends with a quit (q) to exit
  if tail -n1 "$FILE_INPUT" | grep -Eq '^\s*(q|quit)\s*\.?\s*$'; then
    PAYLOAD+="$(cat "$FILE_INPUT")\n"
  else
    PAYLOAD+="$(cat "$FILE_INPUT")\nq\n"
  fi
else
  echo "Provide either --wff, --wff-file or --file." >&2
  exit 6
fi

# Run tau with payload via stdin
OUT="$(/usr/bin/env bash -lc "printf '%b' \"$PAYLOAD\" | \"$TAU_BIN\"")"
EC=$?

echo "$OUT"
echo "Exit code: $EC"

# Consider any 'Error' tokens as failure
LOW="$(printf '%s' "$OUT" | tr 'A-Z' 'a-z')"
if echo "$LOW" | grep -qE 'error|parse error|exception'; then
  exit 10
fi

exit $EC


