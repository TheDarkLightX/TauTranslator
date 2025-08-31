import httpx
import pytest

from backend.unified.infrastructure.llm_providers import OpenRouterProvider, LLMRequest


def _client_with_transport(handler):
    transport = httpx.MockTransport(handler)
    # Disable HTTP/2 in tests to avoid requiring 'h2' extra
    return httpx.Client(transport=transport, http2=False, timeout=httpx.Timeout(2.0))


def test_openrouter_success_and_idempotency(monkeypatch):
    seen_headers = {}

    def handler(request: httpx.Request):
        seen_headers['Idempotency-Key'] = request.headers.get('Idempotency-Key')
        data = {
            "choices": [
                {"message": {"content": "always (payment_approved -> order_shipped)"}}
            ],
            "usage": {"prompt_tokens": 3, "completion_tokens": 5},
        }
        return httpx.Response(200, json=data)

    prov = OpenRouterProvider(api_key="test-key")
    monkeypatch.setattr(OpenRouterProvider, "_CLIENT", _client_with_transport(handler))
    res = prov.generate(LLMRequest(prompt="User: test", system="sys"))
    assert res.is_success()
    out = res.unwrap()
    assert out.text.startswith("always (")
    assert seen_headers.get("Idempotency-Key") and len(seen_headers.get("Idempotency-Key")) == 32


def test_openrouter_retry_429(monkeypatch):
    calls = {"n": 0}

    def handler(request: httpx.Request):
        if calls["n"] == 0:
            calls["n"] += 1
            return httpx.Response(429, text="rate limited")
        data = {
            "choices": [
                {"message": {"content": "always (T)"}}
            ],
            "usage": {},
        }
        return httpx.Response(200, json=data)

    prov = OpenRouterProvider(api_key="test-key")
    monkeypatch.setattr(OpenRouterProvider, "_CLIENT", _client_with_transport(handler))
    res = prov.generate(LLMRequest(prompt="u", system=None))
    assert res.is_success()
    assert res.unwrap().text == "always (T)"


def test_openrouter_timeout(monkeypatch):
    def handler(request: httpx.Request):
        raise httpx.TimeoutException("timeout")

    prov = OpenRouterProvider(api_key="test-key")
    monkeypatch.setattr(OpenRouterProvider, "_CLIENT", _client_with_transport(handler))
    res = prov.generate(LLMRequest(prompt="u", system=None))
    assert res.is_failure()

