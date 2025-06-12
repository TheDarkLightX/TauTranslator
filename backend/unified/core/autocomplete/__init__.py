"""
Educational autocomplete system for TAU and TCE languages.

This package provides intelligent, context-aware suggestions that help users
learn and write formal specifications in TAU Language and TCE (Tau Controlled English).

Copyright: DarkLightX / Dana Edwards
"""

from .models import (
    EducationalSuggestion,
    SuggestionCategory,
    DifficultyLevel,
    SpecificationContext,
    LanguageMode,
    ContextType,
    CursorPosition,
    TauCode,
    SuggestionRequest,
    SuggestionResponse
)

from .tau_suggestion_engine import TauSuggestionEngine
from .tce_suggestion_engine import TceSuggestionEngine
from .educational_autocomplete_service import (
    EducationalAutocompleteService,
    AutocompleteConfiguration
)

__all__ = [
    'EducationalSuggestion',
    'SuggestionCategory',
    'DifficultyLevel',
    'SpecificationContext',
    'LanguageMode',
    'ContextType',
    'CursorPosition',
    'TauCode',
    'SuggestionRequest',
    'SuggestionResponse',
    'TauSuggestionEngine',
    'TceSuggestionEngine',
    'EducationalAutocompleteService',
    'AutocompleteConfiguration'
]