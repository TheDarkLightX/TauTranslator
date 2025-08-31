"""
Enhanced NLP endpoints with educational autocomplete support.

This module extends the existing NLP API with educational features
while maintaining full backward compatibility.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .nlp import (
    router,
    AutocompleteRequest as BaseAutocompleteRequest,
    CodeText,
    SuggestionText,
    create_success_response,
    create_error_response,
    _nlp_loader,
    _autocomplete_service
)
from ..core.autocomplete import (
    EducationalAutocompleteService,
    AutocompleteConfiguration,
    SuggestionRequest,
    SpecificationContext,
    LanguageMode as CoreLanguageMode,
    DifficultyLevel,
    ContextType,
    CursorPosition
)
from ..core.result_enhanced import Result, Success, Failure

import logging

logger = logging.getLogger(__name__)

# =======================
# Extended Domain Types
# =======================

class EducationalLanguageMode(str, Enum):
    """Language mode for autocomplete."""
    TAU = "TAU"
    TCE = "TCE"
    AUTO = "AUTO"

class LearningLevel(str, Enum):
    """User learning level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

# =======================
# Extended Request Model
# =======================

class EducationalAutocompleteRequest(BaseAutocompleteRequest):
    """Enhanced autocomplete request with educational features."""
    # All fields optional for backward compatibility
    language_mode: Optional[EducationalLanguageMode] = Field(
        default=None,
        description="Target language mode: TAU, TCE, or AUTO"
    )
    learning_level: Optional[LearningLevel] = Field(
        default=None,
        description="User's learning level"
    )
    include_examples: bool = Field(
        default=False,
        description="Include code examples in suggestions"
    )
    include_explanations: bool = Field(
        default=False,
        description="Include explanations for suggestions"
    )
    include_hints: bool = Field(
        default=False,
        description="Include contextual hints"
    )
    max_suggestions: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of suggestions to return"
    )

# =======================
# Educational Autocomplete Adapter
# =======================

class EducationalAutocompleteAdapter:
    """Adapts educational autocomplete for API layer."""
    
    def __init__(self):
        """Initialize with educational autocomplete service."""
        config = AutocompleteConfiguration(
            enable_tau_suggestions=True,
            enable_tce_suggestions=True,
            include_educational_hints=True,
            include_examples=True
        )
        self._educational_service = EducationalAutocompleteService(config)
    
    async def process_request_async(
        self,
        request: EducationalAutocompleteRequest,
        nlp_service: Optional[Any]
    ) -> Result[Dict[str, Any]]:
        """Process autocomplete request with educational features."""
        # Transform to domain request
        domain_request = self._create_domain_request(request)
        
        # Get educational suggestions
        result = self._educational_service.get_suggestions_async(domain_request)
        
        if not result.is_success():
            return result
        
        # Transform response based on request mode
        response = result.value
        
        if self._is_educational_mode(request):
            return Success(self._format_educational_response(response, request, nlp_service))
        else:
            return Success(self._format_legacy_response(response, nlp_service))
    
    def _create_domain_request(self, request: EducationalAutocompleteRequest) -> SuggestionRequest:
        """Transform API request to domain request."""
        context = self._create_specification_context(request)
        
        return SuggestionRequest(
            context=context,
            max_suggestions=request.max_suggestions,
            include_examples=request.include_examples,
            include_explanations=request.include_explanations,
            include_hints=request.include_hints
        )
    
    def _create_specification_context(self, request: EducationalAutocompleteRequest) -> SpecificationContext:
        """Create specification context from request."""
        # Map language mode
        language_mode = self._map_language_mode(request.language_mode)
        
        # Map learning level
        learning_level = self._map_learning_level(request.learning_level)
        
        # Infer context type from text
        context_type = self._infer_context_type(request.text)
        
        return SpecificationContext(
            full_text=request.text,
            cursor_position=CursorPosition(request.position or len(request.text)),
            language_mode=language_mode,
            context_type=context_type,
            learning_level=learning_level,
            preceding_text=request.context if request.context else ""
        )
    
    def _map_language_mode(self, mode: Optional[EducationalLanguageMode]) -> CoreLanguageMode:
        """Map API language mode to core language mode."""
        if mode == EducationalLanguageMode.TAU:
            return CoreLanguageMode.TAU
        elif mode == EducationalLanguageMode.TCE:
            return CoreLanguageMode.TCE
        else:
            # Default to TAU for backward compatibility
            return CoreLanguageMode.TAU
    
    def _map_learning_level(self, level: Optional[LearningLevel]) -> DifficultyLevel:
        """Map API learning level to core difficulty level."""
        if level == LearningLevel.BEGINNER:
            return DifficultyLevel.BEGINNER
        elif level == LearningLevel.INTERMEDIATE:
            return DifficultyLevel.INTERMEDIATE
        elif level == LearningLevel.ADVANCED:
            return DifficultyLevel.ADVANCED
        else:
            # Default to intermediate
            return DifficultyLevel.INTERMEDIATE
    
    def _infer_context_type(self, text: str) -> ContextType:
        """Infer context type from text content."""
        text_lower = text.lower()
        
        if "solve" in text_lower:
            return ContextType.SOLVER_COMMAND
        elif any(kw in text_lower for kw in ["always", "sometimes", "eventually"]):
            return ContextType.TEMPORAL_CONSTRAINT
        elif any(kw in text_lower for kw in ["forall", "exists", "for all"]):
            return ContextType.QUANTIFIER_EXPRESSION
        elif "[t]" in text or "stream" in text_lower:
            return ContextType.STREAM_RULE
        elif "define" in text_lower or "function" in text_lower:
            return ContextType.FUNCTION_DEFINITION
        else:
            return ContextType.LOGICAL_ASSERTION
    
    def _is_educational_mode(self, request: EducationalAutocompleteRequest) -> bool:
        """Check if request wants educational features."""
        return (request.include_examples or 
                request.include_explanations or 
                request.include_hints or
                request.language_mode is not None or
                request.learning_level is not None)
    
    def _format_educational_response(
        self,
        response: Any,
        request: EducationalAutocompleteRequest,
        nlp_service: Optional[Any]
    ) -> Dict[str, Any]:
        """Format response with educational features."""
        suggestions = []
        
        for suggestion in response.suggestions[:request.max_suggestions]:
            suggestion_dict = {
                "text": suggestion.text,
                "display": suggestion.display,
                "category": suggestion.category.value,
                "difficulty": suggestion.difficulty.value
            }
            
            if request.include_explanations and suggestion.description:
                suggestion_dict["explanation"] = suggestion.description
            
            if request.include_examples and suggestion.example:
                suggestion_dict["example"] = suggestion.example
            
            if suggestion.tau_equivalent:
                suggestion_dict["tau_equivalent"] = suggestion.tau_equivalent
            
            suggestions.append(suggestion_dict)
        
        result = {
            "suggestions": suggestions,
            "source": "educational",
            "educational_mode": True
        }
        
        if request.language_mode:
            result["language_mode"] = request.language_mode.value
        
        if request.learning_level:
            result["learning_level"] = request.learning_level.value
        
        if request.include_hints and response.context_hint:
            result["context_hint"] = response.context_hint
        
        if response.learning_tip:
            result["learning_tip"] = response.learning_tip
        
        return result
    
    def _format_legacy_response(
        self,
        response: Any,
        nlp_service: Optional[Any]
    ) -> Dict[str, Any]:
        """Format backward-compatible response."""
        # Simple format for legacy clients
        suggestions = []
        
        for suggestion in response.suggestions[:10]:
            suggestions.append({
                "text": suggestion.text,
                "type": suggestion.category.value.lower(),
                "confidence": 1.0  # Default confidence
            })
        
        return {
            "suggestions": suggestions,
            "source": "nlp" if nlp_service else "basic"
        }

# =======================
# Initialize Adapter
# =======================

_educational_adapter = EducationalAutocompleteAdapter()

# =======================
# Enhanced Endpoint
# =======================

@router.post("/autocomplete/educational")
async def educational_autocomplete_async(request: EducationalAutocompleteRequest):
    """Provide educational autocomplete suggestions."""
    # Load NLP service
    nlp_result = _nlp_loader.load_nlp_service_async()
    nlp_service = nlp_result.value if nlp_result.is_success() else None
    
    # Process request
    result = await _educational_adapter.process_request_async(request, nlp_service)
    
    if result.is_success():
        return create_success_response(result.value)
    else:
        return create_error_response(f"Autocomplete failed: {result.message}")

# =======================
# Backward Compatible Override
# =======================

@router.post("/autocomplete", include_in_schema=False)
async def enhanced_autocomplete_async(request: EducationalAutocompleteRequest):
    """
    Enhanced autocomplete endpoint with backward compatibility.
    
    This overrides the basic endpoint to support educational features
    while maintaining full backward compatibility.
    """
    # If no educational features requested, use legacy service
    if not _educational_adapter._is_educational_mode(request):
        # Fallback to original implementation
        nlp_result = _nlp_loader.load_nlp_service_async()
        nlp_service = nlp_result.value if nlp_result.is_success() else None
        
        suggestions_result = await _autocomplete_service.get_suggestions_async(
            CodeText(request.text), 
            nlp_service
        )
        
        if suggestions_result.is_success():
            return create_success_response({
                "suggestions": [s.__dict__ for s in suggestions_result.value],
                "source": "nlp" if nlp_service else "basic"
            })
        else:
            return create_error_response(suggestions_result.message)
    
    # Use educational adapter
    return await educational_autocomplete_async(request)