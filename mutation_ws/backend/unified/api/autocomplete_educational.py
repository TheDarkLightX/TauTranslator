"""
Educational autocomplete API endpoints.

This module provides a clean integration of the educational autocomplete
service with the FastAPI framework, following the Intentional Disclosure Principle.

Copyright: DarkLightX / Dana Edwards
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

from ..core.responses import create_success_response, create_error_response
from ..core.autocomplete import (
    EducationalAutocompleteService,
    AutocompleteConfiguration,
    SuggestionRequest,
    SpecificationContext,
    LanguageMode,
    DifficultyLevel,
    ContextType,
    CursorPosition
)

import logging

logger = logging.getLogger(__name__)

# Create a separate router for educational autocomplete
educational_router = APIRouter(prefix="/educational", tags=["educational"])

# =======================
# Request/Response Models
# =======================

class LanguageModeAPI(str, Enum):
    """Language mode for autocomplete."""
    TAU = "TAU"
    TCE = "TCE"

class LearningLevelAPI(str, Enum):
    """User learning level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class EducationalAutocompleteRequest(BaseModel):
    """Request model for educational autocomplete."""
    text: str = Field(..., description="The text to autocomplete")
    cursor_position: Optional[int] = Field(None, description="Cursor position in text")
    language_mode: LanguageModeAPI = Field(LanguageModeAPI.TAU, description="Language mode")
    learning_level: LearningLevelAPI = Field(LearningLevelAPI.INTERMEDIATE, description="User learning level")
    max_suggestions: int = Field(10, ge=1, le=50, description="Maximum suggestions")
    include_examples: bool = Field(True, description="Include code examples")
    include_templates: bool = Field(True, description="Include templates")

class TranslationRequest(BaseModel):
    """Request model for translation between TAU and TCE."""
    text: str = Field(..., description="Text to translate")
    from_language: LanguageModeAPI = Field(..., description="Source language")
    to_language: LanguageModeAPI = Field(..., description="Target language")

# =======================
# Service Initialization
# =======================

_service_config = AutocompleteConfiguration(
    enable_tau_suggestions=True,
    enable_tce_suggestions=True,
    include_educational_hints=True,
    include_examples=True,
    max_suggestions=20
)

_educational_service = EducationalAutocompleteService(_service_config)

# =======================
# Service Adapter
# =======================

class EducationalAutocompleteAdapter:
    """Adapts domain service for API layer."""
    
    def __init__(self, service: EducationalAutocompleteService):
        self._service = service
    
    def get_suggestions(self, request: EducationalAutocompleteRequest) -> Dict[str, Any]:
        """Get autocomplete suggestions."""
        # Create domain context
        context = self._create_context(request)
        
        # Create domain request
        domain_request = SuggestionRequest(
            context=context,
            max_suggestions=request.max_suggestions,
            include_templates=request.include_templates,
            include_examples=request.include_examples
        )
        
        # Get suggestions
        result = self._service.get_suggestions_async(domain_request)
        
        if result.is_success():
            return self._format_response(result.value, request)
        else:
            raise ValueError(f"Autocomplete failed: {result.message}")
    
    def translate(self, request: TranslationRequest) -> Dict[str, Any]:
        """Translate between TAU and TCE."""
        from_mode = self._map_language_mode(request.from_language)
        to_mode = self._map_language_mode(request.to_language)
        
        result = self._service.translate_selection_async(
            request.text,
            from_mode,
            to_mode
        )
        
        if result.is_success():
            return {
                "translation": result.value,
                "from": request.from_language,
                "to": request.to_language,
                "original": request.text
            }
        else:
            raise ValueError(f"Translation failed: {result.message}")
    
    def _create_context(self, request: EducationalAutocompleteRequest) -> SpecificationContext:
        """Create domain context from request."""
        return SpecificationContext(
            full_text=request.text,
            cursor_position=CursorPosition(request.cursor_position or len(request.text)),
            language_mode=self._map_language_mode(request.language_mode),
            context_type=self._infer_context_type(request.text),
            learning_level=self._map_learning_level(request.learning_level)
        )
    
    def _map_language_mode(self, mode: LanguageModeAPI) -> LanguageMode:
        """Map API language mode to domain."""
        return LanguageMode.TAU if mode == LanguageModeAPI.TAU else LanguageMode.TCE
    
    def _map_learning_level(self, level: LearningLevelAPI) -> DifficultyLevel:
        """Map API learning level to domain."""
        mapping = {
            LearningLevelAPI.BEGINNER: DifficultyLevel.BEGINNER,
            LearningLevelAPI.INTERMEDIATE: DifficultyLevel.INTERMEDIATE,
            LearningLevelAPI.ADVANCED: DifficultyLevel.ADVANCED
        }
        return mapping[level]
    
    def _infer_context_type(self, text: str) -> ContextType:
        """Infer context type from text."""
        text_lower = text.lower()
        
        if "solve" in text_lower:
            return ContextType.SOLVER_COMMAND
        elif any(kw in text_lower for kw in ["always", "sometimes", "eventually"]):
            return ContextType.TEMPORAL_CONSTRAINT
        elif any(kw in text_lower for kw in ["forall", "exists", "for all"]):
            return ContextType.QUANTIFIER_EXPRESSION
        elif "[t]" in text or "stream" in text_lower:
            return ContextType.STREAM_RULE
        elif "define" in text_lower:
            return ContextType.FUNCTION_DEFINITION
        else:
            return ContextType.LOGICAL_ASSERTION
    
    def _format_response(self, response: Any, request: EducationalAutocompleteRequest) -> Dict[str, Any]:
        """Format domain response for API."""
        suggestions = []
        
        for suggestion in response.suggestions[:request.max_suggestions]:
            item = {
                "text": suggestion.text,
                "display": suggestion.display,
                "category": suggestion.category.value,
                "difficulty": suggestion.difficulty.value,
                "description": suggestion.description
            }
            
            if request.include_examples and suggestion.example:
                item["example"] = suggestion.example
            
            if hasattr(suggestion, 'tau_equivalent') and suggestion.tau_equivalent:
                item["tau_equivalent"] = suggestion.tau_equivalent
            
            if hasattr(suggestion, 'template') and suggestion.template:
                item["template"] = suggestion.template
            
            suggestions.append(item)
        
        result = {
            "suggestions": suggestions,
            "total": len(suggestions),
            "language_mode": request.language_mode.value,
            "learning_level": request.learning_level.value
        }
        
        if response.context_hint:
            result["context_hint"] = response.context_hint
        
        if response.learning_tip:
            result["learning_tip"] = response.learning_tip
        
        return result

# Initialize adapter
_adapter = EducationalAutocompleteAdapter(_educational_service)

# =======================
# API Endpoints
# =======================

@educational_router.post("/autocomplete")
async def educational_autocomplete_async(request: EducationalAutocompleteRequest):
    """Get educational autocomplete suggestions."""
    try:
        response = _adapter.get_suggestions(request)
        return create_success_response(response)
    except Exception as e:
        logger.error(f"Educational autocomplete error: {str(e)}")
        return create_error_response(str(e))

@educational_router.post("/translate")
async def translate_async(request: TranslationRequest):
    """Translate between TAU and TCE."""
    try:
        response = _adapter.translate(request)
        return create_success_response(response)
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return create_error_response(str(e))

@educational_router.get("/help/{language}")
async def get_language_help_async(language: LanguageModeAPI):
    """Get help for a specific language."""
    help_content = {
        LanguageModeAPI.TAU: {
            "description": "TAU is a formal specification language for temporal logic",
            "basic_keywords": ["always", "sometimes", "eventually", "forall", "exists"],
            "operators": ["->", "<->", "&&", "||", "!"],
            "examples": [
                {"code": "always (x > 0)", "description": "x is always positive"},
                {"code": "forall x : P(x)", "description": "property P holds for all x"},
                {"code": "solve x = 0", "description": "find value of x that equals 0"}
            ]
        },
        LanguageModeAPI.TCE: {
            "description": "TCE (Tau Controlled English) is a natural language interface to TAU",
            "patterns": [
                "for all ... such that ...",
                "there exists ... such that ...",
                "it is always the case that ...",
                "if ... then ..."
            ],
            "examples": [
                {"tce": "for all x such that x > 0", "tau": "forall x : x > 0"},
                {"tce": "it is always the case that door is locked", "tau": "always (door_locked)"}
            ]
        }
    }
    
    return create_success_response(help_content.get(language, {}))