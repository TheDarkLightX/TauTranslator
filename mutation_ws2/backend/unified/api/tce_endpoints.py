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
    # Optional temporal mode: "invariant" (default) wraps with always(...),
    # "atemporal" emits a bare WFF Tau without always.
    temporal_mode: str | None = None  # "invariant" | "atemporal"


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
    original_tce = body.tce
    temporal_mode = (body.temporal_mode or "invariant").lower()
    tce_for_translation = original_tce
    # In atemporal mode, allow bare WFF by internally wrapping for translation
    if temporal_mode == "atemporal":
        t = original_tce.strip()
        if not t.lower().startswith("always ("):
            tce_for_translation = f"always ({t})"
    if CNLParser is not None and TCETauTranslator is not None:
        try:
            parser = CNLParser()
            ast = parser.parse(tce_for_translation)
            translator = TCETauTranslator()
            tr = translator.translate(ast)
            if getattr(tr, 'errors', []):
                return TceToTauResponse(success=False, tau=None, errors=list(tr.errors))
            tau_code = getattr(tr, 'tau_code', '')
            # If atemporal requested, strip always wrapper if present
            if temporal_mode == "atemporal":
                m = None
                try:
                    import re
                    m = re.match(r"^\s*always\s*\((.*)\)\s*$", tau_code, flags=re.IGNORECASE | re.DOTALL)
                except Exception:
                    m = None
                if m:
                    tau_code = m.group(1).strip()
            return TceToTauResponse(success=True, tau=tau_code, errors=[])
        except Exception as e:
            # fall through to fallback
            pass
    # Fallback
    ok, tau, errs = translate_tce_to_tau_simple(tce_for_translation)
    if not ok:
        return TceToTauResponse(success=False, tau=None, errors=errs)
    # Strip always wrapper in atemporal mode
    if tau and temporal_mode == "atemporal":
        try:
            import re
            m = re.match(r"^\s*always\s*\((.*)\)\s*$", tau, flags=re.IGNORECASE | re.DOTALL)
            if m:
                tau = m.group(1).strip()
        except Exception:
            pass
    return TceToTauResponse(success=True, tau=tau, errors=[])
