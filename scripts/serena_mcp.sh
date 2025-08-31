#!/usr/bin/env bash
set -euo pipefail

# Serena MCP launcher for this repo.
# Usage:
#   scripts/serena_mcp.sh start   # start in background
#   scripts/serena_mcp.sh stop    # stop background server
#   scripts/serena_mcp.sh status  # show status
#   scripts/serena_mcp.sh logs    # tail logs

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
SERENA_DIR="$ROOT_DIR/external/serena"
UV_BIN="${UV_BIN:-$HOME/.local/bin/uv}"
PID_FILE="$ROOT_DIR/serena_mcp.pid"
LOG_FILE="$ROOT_DIR/serena_mcp.log"

cmd="${1:-start}"

start() {
  if [[ ! -d "$SERENA_DIR" ]]; then
    echo "Serena repo not found at $SERENA_DIR. Clone it first:"
    echo "  git clone --depth 1 https://github.com/oraios/serena external/serena"
    exit 1
  fi
  if [[ ! -x "$UV_BIN" ]]; then
    echo "uv not found at $UV_BIN. Install uv: https://astral.sh/uv" >&2
  fi
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE" 2>/dev/null)" 2>/dev/null; then
    echo "Serena MCP already running (PID $(cat "$PID_FILE"))."
    exit 0
  fi
  cd "$SERENA_DIR"
  nohup "$UV_BIN" run -p 3.11 serena start-mcp-server > "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  sleep 1
  echo "Started Serena MCP (PID $(cat "$PID_FILE")). Logs: $LOG_FILE"
}

stop() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      echo "Stopped Serena MCP (PID $pid)."
    else
      echo "Stale PID file removed."
    fi
    rm -f "$PID_FILE"
  else
    echo "No PID file at $PID_FILE."
  fi
}

status() {
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE" 2>/dev/null)" 2>/dev/null; then
    echo "Serena MCP is running (PID $(cat "$PID_FILE"))."
  else
    echo "Serena MCP is not running."
  fi
}

logs() {
  touch "$LOG_FILE"
  echo "Tailing $LOG_FILE (Ctrl-C to exit)"
  tail -n 200 -f "$LOG_FILE"
}

case "$cmd" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  logs) logs ;;
  *) echo "Unknown command: $cmd"; exit 1 ;;
 esac
