"""FastAPI wrapper exposing English→Tau translation as a web service.

Run locally:
    uvicorn backend.api.server:app --reload

Endpoint:
    GET /translate?sentence=Every+user+... -> JSON {"tau": "..."}
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

try:
    from backend.unified.english_to_tau_translator import EnglishToTauTranslator
except ImportError as exc:  # fallback for src-layout execution inside container
    raise RuntimeError("Failed to import EnglishToTauTranslator. Did you install the project as a package?") from exc

translator = EnglishToTauTranslator()
# Enable CORS for PWA frontend
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Tau Translator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.tautranslator.ai",
        "https://thedarklightx.github.io",
        "https://thedarklightx.github.io/TauTranslator",
    ],
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-OpenRouter-Key"],
)

# Mount v2 functional endpoints
from backend.api.endpoints.translation_endpoints import router as translation_router
from backend.unified.api.llm_endpoints import router as llm_router
app.include_router(translation_router)
app.include_router(llm_router)


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


@app.get("/translate", response_model=TranslationResponse)
async def translate(sentence: str = Query(..., min_length=3, max_length=500)) -> TranslationResponse:
    """Translate an English sentence into Tau code.

    Returns JSON with `success`, `tau` (may be empty if failed) and intermediate `tce` text.
    """
    success, tau_code, tce = translator.translate_english_to_tau(sentence)
    if not success:
        raise HTTPException(status_code=422, detail="Translation failed for this sentence")
    return TranslationResponse(success=success, tau=tau_code, tce=tce)
