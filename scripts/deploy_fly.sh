#!/usr/bin/env bash
set -euo pipefail

info(){ echo -e "\033[36m[info]\033[0m $*"; }
warn(){ echo -e "\033[33m[warn]\033[0m $*"; }
err(){ echo -e "\033[31m[err]\033[0m $*"; }

# Config (can override via env)
APP_NAME="${FLY_APP_NAME:-tau-translator-api}"
API_URL="${API_URL:-https://tau-translator-api.fly.dev}"

# Ensure flyctl is installed and in PATH
if ! command -v flyctl >/dev/null 2>&1; then
  info "Installing flyctl…"
  curl -L https://fly.io/install.sh | sh
  export PATH="$HOME/.fly/bin:$PATH"
else
  export PATH="$HOME/.fly/bin:$PATH"
fi

# Acquire Fly token: env → saved file → prompt (optional --save)
TOKEN="${FLY_API_TOKEN:-}"
if [[ -z "$TOKEN" && -f "$HOME/.secrets/fly_token" ]]; then
  TOKEN="$(tr -d '\r\n' < "$HOME/.secrets/fly_token")"
fi
if [[ -z "$TOKEN" ]]; then
  SAVE_FLAG="${1:-}"
  read -rsp "Enter Fly API token: " TOKEN
  echo
  if [[ "$SAVE_FLAG" == "--save" ]]; then
    mkdir -p "$HOME/.secrets"
    printf "%s" "$TOKEN" > "$HOME/.secrets/fly_token"
    chmod 600 "$HOME/.secrets/fly_token"
    info "Saved token to $HOME/.secrets/fly_token"
  fi
fi
export FLY_API_TOKEN="$TOKEN"

info "Authenticating to Fly…"
flyctl auth token "$FLY_API_TOKEN" >/dev/null

info "Deploying app: $APP_NAME"
flyctl deploy -a "$APP_NAME" --remote-only --verbose

# Helpers
curl_json(){
  local method="$1"; shift
  local url="$1"; shift
  info "Request: $method $url"
  set +e
  local resp
  resp="$(curl -sS -i -X "$method" "$url" "$@")"
  local code
  code="$(printf "%s" "$resp" | awk 'NR==1{print $2}')"
  printf "%s\n" "$resp"
  set -e
  if [[ "$code" -ge 400 ]]; then
    warn "Non-2xx response: $code"
  fi
}

# Verify health
curl_json GET "$API_URL/healthz"

# LLM chat without BYOK (Echo provider on server)
curl_json POST "$API_URL/llm/chat" \
  -H "Origin: http://127.0.0.1:8777" \
  -H "Content-Type: application/json" \
  --data '{"threadId":null,"messages":[{"role":"user","content":"test"}],"mode":"assist"}'

# LLM chat with BYOK if available
if [[ -n "${OPENROUTER_KEY:-}" ]]; then
  info "Testing LLM chat with BYOK…"
  curl_json POST "$API_URL/llm/chat" \
    -H "Origin: http://127.0.0.1:8777" \
    -H "Content-Type: application/json" \
    -H "X-OpenRouter-Key: ${OPENROUTER_KEY}" \
    --data '{"threadId":null,"messages":[{"role":"user","content":"test"}],"mode":"assist"}'
fi

info "Done."


