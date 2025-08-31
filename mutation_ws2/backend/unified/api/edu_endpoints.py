from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.unified.core.autocomplete.models import (
    SpecificationContext as DSpecificationContext,
    SuggestionRequest as DSuggestionRequest,
    LanguageMode,
    ContextType,
    DifficultyLevel,
)
from backend.unified.core.autocomplete.educational_autocomplete_service import (
    EducationalAutocompleteService,
)
from backend.unified.core.result_enhanced import Failure


router = APIRouter(prefix="/edu", tags=["education"])


# -----------------------------
# Pydantic I/O Models
# -----------------------------

class SpecificationContext(BaseModel):
    full_text: str
    cursor_position: int = Field(ge=0)
    language_mode: str  # "TAU" | "TCE"
    context_type: str
    parent_constructs: List[str] = Field(default_factory=list)
    variables_in_scope: List[str] = Field(default_factory=list)
    learning_level: str = "intermediate"  # beginner|intermediate|advanced


class SuggestionsRequest(BaseModel):
    context: SpecificationContext
    max_suggestions: int = 10
    include_templates: bool = True
    include_examples: bool = True


class TranslateSelectionRequest(BaseModel):
    text: str
    from_language: str  # TAU|TCE
    to_language: str    # TAU|TCE


class SuggestionItem(BaseModel):
    text: str
    display: str
    category: str
    description: Optional[str] = None
    example: Optional[str] = None
    difficulty: str
    template: Optional[str] = None
    tau_equivalent: Optional[str] = None
    related_concepts: List[str] = []
    confidence: float


class SuggestionsResponse(BaseModel):
    suggestions: List[SuggestionItem]
    context_hint: Optional[str] = None
    learning_tip: Optional[str] = None


class ContextHelpRequest(BaseModel):
    context: SpecificationContext


class ContextHelpResponse(BaseModel):
    hint: Optional[str]


_service = EducationalAutocompleteService()


def _to_enum(value: str, enum_cls):
    v = (value or "").strip().upper()
    for member in enum_cls:
        if member.value.upper() == v:
            return member
    # Fallback: try name match
    try:
        return enum_cls[v]
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid value '{value}' for {enum_cls.__name__}")


def _to_context(dc: SpecificationContext) -> DSpecificationContext:
    lang = _to_enum(dc.language_mode, LanguageMode)
    # ContextType values are snake_case; accept flexible input by lowercasing
    ct_str = (dc.context_type or "").strip().lower()
    ct = None
    for member in ContextType:
        if member.value == ct_str:
            ct = member
            break
    if ct is None:
        raise HTTPException(status_code=400, detail=f"Invalid context_type '{dc.context_type}'")
    lvl_map = {
        "beginner": DifficultyLevel.BEGINNER,
        "intermediate": DifficultyLevel.INTERMEDIATE,
        "advanced": DifficultyLevel.ADVANCED,
    }
    lvl = lvl_map.get((dc.learning_level or "intermediate").strip().lower(), DifficultyLevel.INTERMEDIATE)
    return DSpecificationContext(
        full_text=dc.full_text,
        cursor_position=dc.cursor_position,
        language_mode=lang,
        context_type=ct,
        parent_constructs=list(dc.parent_constructs or []),
        variables_in_scope=list(dc.variables_in_scope or []),
        learning_level=lvl,
    )


@router.post("/suggestions", response_model=SuggestionsResponse)
def edu_suggestions(body: SuggestionsRequest) -> SuggestionsResponse:
    dctx = _to_context(body.context)
    dreq = DSuggestionRequest(
        context=dctx,
        max_suggestions=body.max_suggestions,
        include_templates=body.include_templates,
        include_examples=body.include_examples,
    )
    result = _service.get_suggestions_async(dreq)
    if isinstance(result, Failure):
        raise HTTPException(status_code=400, detail=result.message)
    resp = result.unwrap()
    items: List[SuggestionItem] = []
    for s in resp.suggestions:
        items.append(
            SuggestionItem(
                text=str(s.text),
                display=str(s.display),
                category=s.category.value,
                description=str(s.description) if s.description is not None else None,
                example=str(s.example) if s.example is not None else None,
                difficulty=s.difficulty.value,
                template=str(s.template) if s.template is not None else None,
                tau_equivalent=str(s.tau_equivalent) if s.tau_equivalent is not None else None,
                related_concepts=list(s.related_concepts or []),
                confidence=float(s.confidence),
            )
        )
    return SuggestionsResponse(
        suggestions=items,
        context_hint=str(resp.context_hint) if resp.context_hint is not None else None,
        learning_tip=str(resp.learning_tip) if resp.learning_tip is not None else None,
    )


@router.post("/translate-selection")
def edu_translate_selection(body: TranslateSelectionRequest) -> dict:
    frm = _to_enum(body.from_language, LanguageMode)
    to = _to_enum(body.to_language, LanguageMode)
    result = _service.translate_selection_async(body.text, frm, to)
    if isinstance(result, Failure):
        raise HTTPException(status_code=422, detail=result.message)
    return {"success": True, "translated": result.unwrap()}


@router.post("/context-help", response_model=ContextHelpResponse)
def edu_context_help(body: ContextHelpRequest) -> ContextHelpResponse:
    dctx = _to_context(body.context)
    result = _service.get_context_help_async(dctx)
    if isinstance(result, Failure):
        raise HTTPException(status_code=400, detail=result.message)
    hint = result.unwrap()
    return ContextHelpResponse(hint=str(hint) if hint is not None else None)


