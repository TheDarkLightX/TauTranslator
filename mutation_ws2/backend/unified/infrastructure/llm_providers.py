"""
LLM provider abstraction. Start with a stub provider; expand to OpenRouter/HF/local later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import httpx
import os
import hashlib
import time

from ..core.result_enhanced import Result, Success, Failure


@dataclass
class LLMRequest:
    prompt: str
    system: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 512


@dataclass
class LLMResponse:
    text: str
    usage: Dict[str, Any]


class LLMProvider:
    def generate(self, request: LLMRequest) -> Result[LLMResponse]:  # sync for minimal slice
        return Failure("NOT_IMPLEMENTED", "No provider configured")


class EchoProvider(LLMProvider):
    """Minimal provider for dev: mirrors prompt into a structured placeholder."""

    def generate(self, request: LLMRequest) -> Result[LLMResponse]:
        # Simulate returning a TCE-like response for simple prompts
        text = f"always ({request.prompt.strip()})"
        return Success(LLMResponse(text=text, usage={"prompt_tokens": len(request.prompt.split()), "completion_tokens": len(text.split())}))


class OpenRouterProvider(LLMProvider):
    """Minimal OpenRouter chat completions client (BYOK).

    Expects an API key and uses a safe default model.
    """

    def __init__(self, api_key: str, model: str = "openrouter/auto") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate(self, request: LLMRequest) -> Result[LLMResponse]:
        """Synchronous generate to avoid event-loop misuse inside FastAPI handlers."""
        try:
            return self._generate_sync(request)
        except Exception as e:
            return Failure("OPENROUTER_ERROR", str(e))

    # Shared sync client per process
    _CLIENT: Optional[httpx.Client] = None

    @classmethod
    def _get_client(cls) -> httpx.Client:
        if cls._CLIENT is None:
            limits = httpx.Limits(
                max_connections=int(os.getenv("TAU_HTTPX_MAX_CONN", "100")),
                max_keepalive_connections=int(os.getenv("TAU_HTTPX_MAX_KEEPALIVE", "20")),
            )
            timeout = httpx.Timeout(10.0, connect=5.0)
            # http2 disabled by default for sync Client; set explicitly for clarity
            cls._CLIENT = httpx.Client(http2=False, limits=limits, timeout=timeout)
        return cls._CLIENT

    def _generate_sync(self, request: LLMRequest) -> Result[LLMResponse]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.append({"role": "user", "content": request.prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        # Idempotency key to protect retries
        key_basis = f"{request.system or ''}||{request.prompt}"
        idem_key = hashlib.sha256(key_basis.encode("utf-8")).hexdigest()[:32]
        headers["Idempotency-Key"] = idem_key

        client = self._get_client()
        for attempt in range(2):
            try:
                resp = client.post(self.base_url, json=payload, headers=headers)
                if resp.status_code == 429 and attempt == 0:
                    time.sleep(1.0)
                    continue
                if resp.status_code >= 300:
                    return Failure(f"OPENROUTER_HTTP_{resp.status_code}", resp.text)
                data = resp.json()
                choice = (data.get("choices") or [{}])[0]
                text = ((choice.get("message") or {}).get("content")) or ""
                usage = data.get("usage") or {}
                return Success(LLMResponse(text=text, usage=usage))
            except httpx.TimeoutException:
                if attempt == 0:
                    time.sleep(0.5)
                    continue
                return Failure("OPENROUTER_TIMEOUT", "timeout")
            except Exception as e:
                return Failure("OPENROUTER_ERROR", str(e))
        return Failure("OPENROUTER_ERROR", "unreachable")


def get_default_provider() -> LLMProvider:
    return EchoProvider()


def get_provider(openrouter_api_key: Optional[str], provider_name: Optional[str] = None) -> LLMProvider:
    name = (provider_name or "").strip().lower()
    # Allow BYOK via header first; then fallback to server env secrets
    api_key = openrouter_api_key or os.getenv("OPENROUTER_KEY") or os.getenv("OPENROUTER_API_KEY") or os.getenv("TAU_OPENROUTER_KEY")
    if api_key:
        return OpenRouterProvider(api_key=api_key)
    # Default to echo if no provider selected or unsupported name
    if name == "echo" or not name:
        return EchoProvider()
    return EchoProvider()


