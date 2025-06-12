"""
Educational autocomplete service following the Intentional Disclosure Principle.

Orchestrates TAU and TCE suggestion engines to provide intelligent,
context-aware suggestions for formal specification writing.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Union
from dataclasses import dataclass
from .models import (
    EducationalSuggestion,
    SpecificationContext,
    LanguageMode,
    ContextType,
    SuggestionRequest,
    SuggestionResponse,
    HintText
)
from .tau_suggestion_engine import TauSuggestionEngine
from .tce_suggestion_engine import TceSuggestionEngine
from ..result_enhanced import Result, Success, Failure


@dataclass(frozen=True)
class AutocompleteConfiguration:
    """Configuration for autocomplete service."""
    enable_tau_suggestions: bool = True
    enable_tce_suggestions: bool = True
    max_suggestions: int = 10
    include_educational_hints: bool = True
    include_examples: bool = True


class EducationalAutocompleteService:
    """
    Orchestrates educational autocomplete for TAU and TCE languages.
    
    Follows Rule 2: Public methods orchestrate, private methods implement.
    This is the main entry point for autocomplete functionality.
    """
    
    def __init__(
        self,
        config: Optional[AutocompleteConfiguration] = None
    ):
        """Initialize with configuration and language engines."""
        self._config = config or AutocompleteConfiguration()
        self._tau_engine = TauSuggestionEngine()
        self._tce_engine = TceSuggestionEngine()
    
    # =======================
    # Public API Methods (Rule 2: Orchestration)
    # =======================
    
    def get_suggestions_async(
        self,
        request: SuggestionRequest
    ) -> Result[SuggestionResponse]:
        """
        Get educational autocomplete suggestions.
        
        Main entry point for autocomplete requests.
        Returns suggestions appropriate to language mode and context.
        """
        # Validate request
        validation_result = self._validate_request(request)
        if not validation_result.is_success():
            return validation_result
        
        # Get suggestions based on language mode
        suggestions = self._fetch_suggestions_for_language(request.context)
        
        # Apply educational enhancements
        enhanced_suggestions = self._enhance_suggestions_with_education(
            suggestions,
            request.context
        )
        
        # Create response with learning hints
        response = self._create_educational_response(
            enhanced_suggestions,
            request.context
        )
        
        return Success(response)
    
    def translate_selection_async(
        self,
        text: str,
        from_language: LanguageMode,
        to_language: LanguageMode
    ) -> Result[str]:
        """
        Translate between TAU and TCE.
        
        Helps users understand the mapping between languages.
        """
        if from_language == to_language:
            return Success(text)
        
        if from_language == LanguageMode.TCE and to_language == LanguageMode.TAU:
            return self._translate_tce_to_tau(text)
        elif from_language == LanguageMode.TAU and to_language == LanguageMode.TCE:
            return self._translate_tau_to_tce(text)
        else:
            return Failure("UNSUPPORTED_TRANSLATION", "Translation not supported")
    
    def get_context_help_async(
        self,
        context: SpecificationContext
    ) -> Result[HintText]:
        """
        Get contextual help for current editing position.
        
        Provides learning guidance based on what user is trying to write.
        """
        help_text = self._generate_context_help(context)
        return Success(help_text)
    
    # =======================
    # Private Implementation Methods
    # =======================
    
    def _validate_request(self, request: SuggestionRequest) -> Result[None]:
        """Validate autocomplete request."""
        if not request.context:
            return Failure("INVALID_REQUEST", "Context is required")
        
        if request.max_suggestions < 1:
            return Failure("INVALID_REQUEST", "Max suggestions must be positive")
        
        return Success(None)
    
    def _fetch_suggestions_for_language(
        self,
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """Fetch suggestions from appropriate engine."""
        if context.language_mode == LanguageMode.TAU:
            return self._tau_engine.get_suggestions_for_context(context)
        elif context.language_mode == LanguageMode.TCE:
            return self._tce_engine.get_suggestions_for_context(context)
        else:
            return []
    
    def _enhance_suggestions_with_education(
        self,
        suggestions: List[EducationalSuggestion],
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """Add educational enhancements to suggestions."""
        if not self._config.include_educational_hints:
            return suggestions
        
        # Suggestions already include educational content
        # Could add more enhancements here based on user progress
        return suggestions
    
    def _create_educational_response(
        self,
        suggestions: List[EducationalSuggestion],
        context: SpecificationContext
    ) -> SuggestionResponse:
        """Create response with educational metadata."""
        # Generate context hint
        context_hint = self._generate_context_hint(context)
        
        # Generate learning tip
        learning_tip = self._generate_learning_tip(suggestions, context)
        
        return SuggestionResponse(
            suggestions=suggestions[:self._config.max_suggestions],
            context_hint=context_hint,
            learning_tip=learning_tip
        )
    
    def _generate_context_hint(
        self,
        context: SpecificationContext
    ) -> Optional[HintText]:
        """Generate hint about current context."""
        hints = {
            ContextType.SOLVER_COMMAND: "Define constraints to find values that satisfy them",
            ContextType.TEMPORAL_CONSTRAINT: "Specify properties that hold over time",
            ContextType.QUANTIFIER_EXPRESSION: "Express properties for all or some values",
            ContextType.STREAM_RULE: "Define how streams transform over time",
            ContextType.FUNCTION_DEFINITION: "Create reusable functions or predicates"
        }
        
        hint = hints.get(context.context_type)
        return HintText(hint) if hint else None
    
    def _generate_learning_tip(
        self,
        suggestions: List[EducationalSuggestion],
        context: SpecificationContext
    ) -> Optional[HintText]:
        """Generate learning tip based on suggestions."""
        if not suggestions:
            return HintText("Start typing to see suggestions")
        
        # Provide tips based on difficulty level
        if context.learning_level.value == "beginner":
            return HintText("Try simple patterns first. Each suggestion includes an example.")
        elif context.learning_level.value == "intermediate":
            return HintText("Combine temporal and logical operators for complex specifications.")
        else:
            return HintText("Use nested quantifiers and advanced patterns for precise specifications.")
    
    def _translate_tce_to_tau(self, tce_text: str) -> Result[str]:
        """Translate TCE to TAU."""
        tau_code = self._tce_engine.get_tce_to_tau_mapping(tce_text)
        if tau_code:
            return Success(str(tau_code))
        
        # Try direct pattern matching for common cases
        simple_mappings = {
            "for all x such that x > 0": "forall x : x > 0",
            "there exists x such that": "exists x :",
            "it is always the case that": "always"
        }
        
        for tce_pattern, tau_pattern in simple_mappings.items():
            if tce_text.startswith(tce_pattern):
                return Success(tau_pattern)
        
        return Failure("TRANSLATION_FAILED", "Could not translate TCE to TAU")
    
    def _translate_tau_to_tce(self, tau_text: str) -> Result[str]:
        """Translate TAU to TCE."""
        # This would need implementation
        return Failure("NOT_IMPLEMENTED", "TAU to TCE translation not yet implemented")
    
    def _generate_context_help(
        self,
        context: SpecificationContext
    ) -> HintText:
        """Generate detailed help for current context."""
        help_templates = {
            ContextType.SOLVER_COMMAND: (
                "You're writing a solver command. Use 'solve' followed by "
                "constraints like 'x = 0' or 'x > 0 && y < 10'. "
                "You can also specify types: 'solve {x}:int x > 0'."
            ),
            ContextType.TEMPORAL_CONSTRAINT: (
                "You're specifying temporal properties. Use 'always' for "
                "invariants, 'sometimes' for possibilities, and 'eventually' "
                "for liveness properties. Example: 'always (safety_check)'."
            ),
            ContextType.QUANTIFIER_EXPRESSION: (
                "You're using quantifiers. 'forall x : P(x)' means P holds "
                "for all x. 'exists y : Q(y)' means there's at least one y "
                "where Q holds. Example: 'forall x : x > 0 -> f(x) > 0'."
            ),
            ContextType.STREAM_RULE: (
                "You're defining stream transformations. Use [t] for current "
                "time, [t-1] for previous. Example: 'r output[t] = input[t] & enable[t]'."
            ),
            ContextType.FUNCTION_DEFINITION: (
                "You're defining a function. Use 'DEFINE name(params) := body'. "
                "Example: 'DEFINE max(x, y) := x > y ? x : y'."
            )
        }
        
        help_text = help_templates.get(
            context.context_type,
            "Type to see context-aware suggestions."
        )
        
        return HintText(help_text)