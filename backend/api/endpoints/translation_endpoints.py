from __future__ import annotations

"""Translation & Grammar Endpoints (Railway-Oriented)
====================================================
FastAPI APIRouter that exposes:
    • POST  /v2/translate      – bidirectional translation using active grammar
    • POST  /v2/grammars       – upload a .tgf / .lark grammar file
    • GET   /v2/grammars       – list loaded grammars + active one

All operations use the `Result` monad (backend.unified.core.result_enhanced)
to maintain functional, railway-oriented flow (no try/except pyramids).
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Any, Dict
from pathlib import Path

from backend.unified.core.result_enhanced import (
    Result,
    Success,
    Failure,
    try_catch,
)
from backend.unified.translators.tgf_grammar_loader_refactored import (
    get_tgf_grammar_loader,
)

# Registry & grammar loader
from backend.unified.core.translator_registry import TranslatorRegistry

# ---------------------------------------------------------------------------
# Router setup
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/v2", tags=["translation"])

# Directories
GRAMMAR_DIR = Path("data/grammars")
GRAMMAR_DIR.mkdir(parents=True, exist_ok=True)

registry = TranslatorRegistry.get_default()
loader = get_tgf_grammar_loader()

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class TranslateRequest(BaseModel):
    sourceText: str
    sourceLangKey: str = "PLAIN_ENGLISH"
    targetLangKey: str = "TAU"
    grammarFilename: Optional[str] = None  # If provided, switch active grammar
    engineKey: str = "auto"  # pattern | nlp | tce_lark | auto
    secure: Optional[bool] = False  # Reserved for future LLM secure mode

class TranslateResponse(BaseModel):
    success: bool
    translatedText: str = ""
    provider: str = "TauTranslator"
    intermediate: Optional[Dict[str, Any]] = None

class GrammarUploadResponse(BaseModel):
    success: bool
    filename: str
    totalLoaded: int

class GrammarListResponse(BaseModel):
    active: Optional[str]
    loaded: Dict[str, Any]

# ---------------------------------------------------------------------------
# Helper functions (functional style)
# ---------------------------------------------------------------------------

def _activate_grammar(filename: Optional[str]) -> Result[None]:
    if not filename:
        return Success(None)
    return loader.set_active_grammar_async(filename)


def _perform_translation(payload: TranslateRequest) -> Result[TranslateResponse]:
    """Translate according to requested direction. Only PE->Tau supported for now."""

    # Ensure grammar if requested
    grammar_result = _activate_grammar(payload.grammarFilename)
    if grammar_result.is_failure():
        return Failure("GRAMMAR_SWITCH_FAILED", f"Could not activate grammar: {payload.grammarFilename}")

    # Obtain translator
    try:
        engine = registry.get_engine(
            engine_key=payload.engineKey,
            source_lang=payload.sourceLangKey,
            target_lang=payload.targetLangKey,
        )
    except Exception as e:
        return Failure("ENGINE_LOAD_FAILED", str(e))

    # Execute translation
    try:
        trans_result = engine.translate(
            source=payload.sourceText,
            source_lang=payload.sourceLangKey,
            target_lang=payload.targetLangKey,
        )
    except Exception as e:
        return Failure("TRANSLATION_ERROR", str(e))

    if trans_result.is_failure():
        err: Failure = trans_result  # type: ignore
        return err

    tau_text = trans_result.value
    return Success(
        TranslateResponse(
            success=True,
            translatedText=tau_text,
            provider=payload.engineKey or "auto",
        )
    )

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@router.post("/translate", response_model=TranslateResponse)
async def translate_v2(payload: TranslateRequest):
    """Bidirectional translation endpoint (v2) using railway-oriented flow."""
    result = _perform_translation(payload)
    if result.is_success():
        return result.or_else(None)  # unwrap
    err: Failure = result  # type: ignore
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err.message)


@router.post("/grammars", response_model=GrammarUploadResponse)
async def upload_grammar(file: UploadFile = File(...)):
    """Upload a grammar file (.tgf/.lark) and load it into the grammar engine."""
    filename = file.filename
    save_path = GRAMMAR_DIR / filename

    # Read file bytes inside async context, then wrap sync write using try_catch
    content = await file.read()
    write_result = try_catch(lambda: save_path.write_bytes(content), "IO_ERROR")
    if write_result.is_failure():
        err: Failure = write_result  # type: ignore
        raise HTTPException(status_code=500, detail=err.message)

    load_result = loader.load_grammar_file_async(str(filename))
    if load_result.is_failure():
        err: Failure = load_result  # type: ignore
        raise HTTPException(status_code=400, detail=err.message)

    state = loader.get_loading_state()
    total = state.total_loaded if state else 0
    return GrammarUploadResponse(success=True, filename=filename, totalLoaded=total)


@router.get("/grammars", response_model=GrammarListResponse)
async def list_grammars():
    """Return active grammar and metadata of loaded grammars."""
    state = loader.get_loading_state()
    if not state:
        return GrammarListResponse(active=None, loaded={})
    return GrammarListResponse(active=str(state.active_grammar), loaded=state.to_summary_dict())
