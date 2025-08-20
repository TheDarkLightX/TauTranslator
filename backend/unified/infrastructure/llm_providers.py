"""
LLM provider abstraction. Start with a stub provider; expand to OpenRouter/HF/local later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import asyncio
import httpx

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
        # Run sync wrapper around async httpx client for compatibility
        try:
            return asyncio.run(self._generate_async(request))
        except RuntimeError:
            # Already in an event loop; run nested
            return asyncio.get_event_loop().run_until_complete(self._generate_async(request))
        except Exception as e:
            return Failure("OPENROUTER_ERROR", str(e))

    async def _generate_async(self, request: LLMRequest) -> Result[LLMResponse]:
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
        timeout = httpx.Timeout(10.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # basic backoff (2 attempts)
            for attempt in range(2):
                try:
                    resp = await client.post(self.base_url, json=payload, headers=headers)
                    if resp.status_code == 429 and attempt == 0:
                        await asyncio.sleep(1.0)
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
                        await asyncio.sleep(0.5)
                        continue
                    return Failure("OPENROUTER_TIMEOUT", "timeout")
                except Exception as e:
                    return Failure("OPENROUTER_ERROR", str(e))
        return Failure("OPENROUTER_ERROR", "unreachable")


def get_default_provider() -> LLMProvider:
    return EchoProvider()


def get_provider(openrouter_api_key: Optional[str], provider_name: Optional[str] = None) -> LLMProvider:
    name = (provider_name or "").strip().lower()
    if openrouter_api_key:
        return OpenRouterProvider(api_key=openrouter_api_key)
    if name == "echo" or not name:
        return EchoProvider()
    return EchoProvider()


