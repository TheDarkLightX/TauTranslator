"""FastAPI wrapper exposing English→Tau translation as a web service.

Run locally:
    uvicorn backend.api.server:app --reload

Endpoint:
    GET /translate?sentence=Every+user+... -> JSON {"tau": "..."}
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from importlib import import_module
from typing import Any, Optional

translator: Optional[Any] = None

def _get_translator() -> Optional[Any]:
    """Lazily import and instantiate the English→Tau translator.

    Returns None if unavailable so the API can still start (health, LLM endpoints).
    """
    global translator
    if translator is not None:
        return translator
    try:
        module = import_module("backend.unified.english_to_tau_translator")
        translator_class = getattr(module, "EnglishToTauTranslator")
        translator = translator_class()
        return translator
    except Exception:
        return None
# Enable CORS for PWA frontend
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import time
import os
from typing import Callable
import logging

app = FastAPI(title="Tau Translator API", version="0.1.0")

_DEFAULT_ORIGINS = [
    "https://www.tautranslator.ai",
    "https://tautranslator.ai",
    "https://thedarklightx.github.io",
    "https://thedarklightx.github.io/TauTranslator",
    # Local development/testing UIs
    "http://127.0.0.1:8766",
    "http://127.0.0.1:8777",
    "http://127.0.0.1:8888",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://localhost:8766",
    "http://localhost:8777",
    "http://localhost:8888",
]
try:
    _extra = os.getenv("TAU_CORS_EXTRA", "").strip()
    if _extra:
        for o in _extra.split(","):
            o = o.strip()
            if o:
                _DEFAULT_ORIGINS.append(o)
except Exception:
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=_DEFAULT_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next: Callable):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start = time.time()
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        response.headers["X-Response-Time"] = f"{(time.time()-start)*1000:.1f}ms"
        return response

app.add_middleware(RequestIdMiddleware)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory token bucket per IP for /llm/* endpoints.
    Not distributed; sufficient for single-machine Fly deployment.
    """

    _buckets = {}

    async def dispatch(self, request, call_next: Callable):
        path: str = request.url.path or ""
        if not path.startswith("/llm/"):
            return await call_next(request)

        try:
            limit = int(os.getenv("TAU_RATE_LIMIT_RPM", "60"))
        except Exception:
            limit = 60
        capacity = max(1, limit)
        refill_rate = capacity / 60.0  # tokens per second

        ip = (request.client.host if request.client else "0.0.0.0")
        key = (ip, "llm")
        now = time.time()
        bucket = self._buckets.get(key)
        if not bucket:
            bucket = {"tokens": float(capacity), "ts": now}
            self._buckets[key] = bucket
        # Refill
        elapsed = max(0.0, now - bucket["ts"])
        bucket["tokens"] = min(capacity, bucket["tokens"] + elapsed * refill_rate)
        bucket["ts"] = now
        if bucket["tokens"] < 1.0:
            from fastapi.responses import JSONResponse
            resp = JSONResponse(status_code=429, content={"error": "Rate limit exceeded", "retry_after": 1})
            resp.headers["Retry-After"] = "1"
            return resp
        # consume
        bucket["tokens"] -= 1.0
        return await call_next(request)

app.add_middleware(RateLimitMiddleware)


# Structured JSON logging (optional)
try:
    from pythonjsonlogger import jsonlogger
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    # Avoid duplicate handlers on reload
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(handler)
    root_logger.setLevel(os.getenv("TAU_LOG_LEVEL", "INFO"))
except Exception:
    pass


# Prometheus metrics (optional)
try:
    from prometheus_fastapi_instrumentator import Instrumentator

    instrumentator = Instrumentator().instrument(app)

    @app.on_event("startup")
    async def _startup_metrics():
        try:
            instrumentator.expose(app)
        except Exception:
            pass
except Exception:
    pass


# OpenTelemetry instrumentation (optional)
try:
    if os.getenv("TAU_ENABLE_OTEL", "0") == "1":
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
except Exception:
    pass


# Graceful shutdown: close shared HTTP clients
try:
    from backend.unified.infrastructure.llm_providers import OpenRouterProvider

    @app.on_event("shutdown")
    async def _shutdown_clients():
        try:
            client = getattr(OpenRouterProvider, "_CLIENT", None)
            if client is not None:
                await client.aclose()
        except Exception:
            pass
except Exception:
    pass

# Mount v2 functional endpoints
from backend.api.endpoints.translation_endpoints import router as translation_router
from backend.unified.api.llm_endpoints import router as llm_router
from backend.unified.api.edu_endpoints import router as edu_router
from backend.unified.api.tce_endpoints import router as tce_router
from backend.unified.api.llm_chat import router as chat_router
from backend.unified.api.assist_extract import router as assist_router
app.include_router(translation_router)
app.include_router(llm_router)
app.include_router(edu_router)
app.include_router(tce_router)
app.include_router(chat_router)
app.include_router(assist_router)


class TranslationResponse(BaseModel):
    tau: str
    tce: str
    success: bool


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


# Backwards-compat alias used by older PWA clients
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root landing for API to avoid default 404 at '/'."""
    return {
        "status": "ok",
        "name": "Tau Translator API",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/translate", response_model=TranslationResponse)
async def translate(sentence: str = Query(..., min_length=3, max_length=500)) -> TranslationResponse:
    """Translate an English sentence into Tau code.

    Returns JSON with `success`, `tau` (may be empty if failed) and intermediate `tce` text.
    """
    active_translator = _get_translator()
    if active_translator is None:
        raise HTTPException(status_code=503, detail="Translator engine unavailable on this deployment")
    success, tau_code, tce = active_translator.translate_english_to_tau(sentence)
    if not success:
        raise HTTPException(status_code=422, detail="Translation failed for this sentence")
    return TranslationResponse(success=success, tau=tau_code, tce=tce)
