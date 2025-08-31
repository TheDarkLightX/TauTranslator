set -euo pipefail
# Run Serena MCP server via uvx without touching project venv (needs Python 3.11)
if ! command -v uvx >/dev/null 2>&1; then
  echo 'uvx is required. Install with: pipx install uv' >&2
  exit 1
fi
exec uvx --from git+https://github.com/oraios/serena serena start-mcp-server
