from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .simple_tce import validate_tce_simple, translate_tce_to_tau_simple

# Try to load canonical Pratt parser + translator; fallback to None
try:
    from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser  # type: ignore
except Exception:
    CNLParser = None  # type: ignore
try:
    from tau_translator_omega.core_engine.translators.tce_tau_translator import TCETauTranslator  # type: ignore
except Exception:
    TCETauTranslator = None  # type: ignore


router = APIRouter(tags=["tce"])


class TCEBody(BaseModel):
    tce: str


class TCEValidateResponse(BaseModel):
    valid: bool
    errors: list[str] = []


class TceToTauResponse(BaseModel):
    success: bool
    tau: str | None = None
    errors: list[str] = []


@router.post("/validate/tce", response_model=TCEValidateResponse)
def validate_tce(body: TCEBody) -> TCEValidateResponse:
    # Canonical first
    if CNLParser is not None:
        try:
            parser = CNLParser()
            _ = parser.parse(body.tce)
            return TCEValidateResponse(valid=True, errors=[])
        except Exception as e:
            # fall through to simple with reason appended
            pass
    # Fallback
    valid, errs = validate_tce_simple(body.tce)
    return TCEValidateResponse(valid=valid, errors=errs)


@router.post("/translate/tce-to-tau", response_model=TceToTauResponse)
def tce_to_tau(body: TCEBody) -> TceToTauResponse:
    # Canonical first
    if CNLParser is not None and TCETauTranslator is not None:
        try:
            parser = CNLParser()
            ast = parser.parse(body.tce)
            translator = TCETauTranslator()
            tr = translator.translate(ast)
            if getattr(tr, 'errors', []):
                return TceToTauResponse(success=False, tau=None, errors=list(tr.errors))
            return TceToTauResponse(success=True, tau=getattr(tr, 'tau_code', ''), errors=[])
        except Exception as e:
            # fall through to fallback
            pass
    # Fallback
    ok, tau, errs = translate_tce_to_tau_simple(body.tce)
    return TceToTauResponse(success=ok, tau=tau, errors=errs)
