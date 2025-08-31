#!/usr/bin/env python3
"""
TauTranslator Lab API (for UI/UX experimentation)
-------------------------------------------------

Minimal FastAPI app exposing the LLM endpoints under /llm with permissive CORS
so we can iterate on the frontend locally without touching the production server.

Usage (dev):
  python -m uvicorn backend.lab_api:app --host 127.0.0.1 --port 8010 --reload

This service is for local development only. Do NOT deploy.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    # Reuse the unified backend's LLM endpoints
    from backend.unified.api.llm_endpoints import router as llm_router
except Exception as e:  # pragma: no cover
    raise RuntimeError(f"Failed to import LLM endpoints: {e}")


app = FastAPI(
    title="TauTranslator Lab API",
    version="0.1.0",
    description="Local-only API for experimenting with the UI/UX",
)

# Permissive CORS for local dev (CM6, SvelteKit, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount LLM routes used by the UI (/llm/prompt-to-spec, /llm/spec-to-prompt, ...)
app.include_router(llm_router)


@app.get("/")
async def root():
    return {"service": "TauTranslator Lab API", "status": "ok"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "backend.lab_api:app",
        host="127.0.0.1",
        port=8010,
        reload=True,
        log_level="info",
    )


