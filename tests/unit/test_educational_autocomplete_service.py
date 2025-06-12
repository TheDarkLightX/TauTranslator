"""
Integration tests for educational autocomplete service.

Tests the orchestration of TAU and TCE engines.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add the backend path to sys.path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.unified.core.autocomplete.models import (
    SpecificationContext,
    LanguageMode,
    ContextType,
    DifficultyLevel,
    CursorPosition,
    SuggestionRequest
)
from backend.unified.core.autocomplete.educational_autocomplete_service import (
    EducationalAutocompleteService,
    AutocompleteConfiguration
)


class TestEducationalAutocompleteService:
    """Test integrated autocomplete service."""
    
    def setup_method(self):
        """Initialize service for each test."""
        self.service = EducationalAutocompleteService()
    
    # =======================
    # TAU Language Tests
    # =======================
    
    def test_tau_suggestions_returned_for_tau_mode(self):
        """Test: TAU mode returns TAU-specific suggestions."""
        context = SpecificationContext(
            full_text="alw",
            cursor_position=CursorPosition(3),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.TEMPORAL_CONSTRAINT,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        request = SuggestionRequest(context=context)
        result = self.service.get_suggestions_async(request)
        
        assert result.is_success()
        response = result.value
        assert len(response.suggestions) > 0
        assert any("always" in s.text for s in response.suggestions)
    
    def test_tau_context_hints_provided(self):
        """Test: Context hints are provided for TAU editing."""
        context = SpecificationContext(
            full_text="solve ",
            cursor_position=CursorPosition(6),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.SOLVER_COMMAND,
            learning_level=DifficultyLevel.BEGINNER
        )
        
        request = SuggestionRequest(context=context)
        result = self.service.get_suggestions_async(request)
        
        assert result.is_success()
        response = result.value
        assert response.context_hint is not None
        assert "constraints" in response.context_hint
    
    # =======================
    # TCE Language Tests
    # =======================
    
    def test_tce_suggestions_returned_for_tce_mode(self):
        """Test: TCE mode returns controlled English suggestions."""
        context = SpecificationContext(
            full_text="for all",
            cursor_position=CursorPosition(7),
            language_mode=LanguageMode.TCE,
            context_type=ContextType.QUANTIFIER_EXPRESSION,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        request = SuggestionRequest(context=context)
        result = self.service.get_suggestions_async(request)
        
        assert result.is_success()
        response = result.value
        assert len(response.suggestions) > 0
        assert any("for all" in s.text for s in response.suggestions)
        # TCE suggestions should have TAU equivalents
        assert all(s.tau_equivalent is not None for s in response.suggestions)
    
    # =======================
    # Learning Features
    # =======================
    
    def test_learning_tips_adapt_to_level(self):
        """Test: Learning tips change based on user level."""
        # Beginner context
        beginner_context = SpecificationContext(
            full_text="",
            cursor_position=CursorPosition(0),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.LOGICAL_ASSERTION,
            learning_level=DifficultyLevel.BEGINNER
        )
        
        request = SuggestionRequest(context=beginner_context)
        beginner_result = self.service.get_suggestions_async(request)
        beginner_tip = beginner_result.value.learning_tip
        
        # Advanced context
        advanced_context = SpecificationContext(
            full_text="",
            cursor_position=CursorPosition(0),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.LOGICAL_ASSERTION,
            learning_level=DifficultyLevel.ADVANCED
        )
        
        request = SuggestionRequest(context=advanced_context)
        advanced_result = self.service.get_suggestions_async(request)
        advanced_tip = advanced_result.value.learning_tip
        
        # Tips should be different
        assert beginner_tip != advanced_tip
        assert "simple" in beginner_tip.lower()
        assert "advanced" in advanced_tip.lower()
    
    # =======================
    # Translation Features
    # =======================
    
    def test_tce_to_tau_translation(self):
        """Test: Can translate TCE phrases to TAU."""
        tce_text = "for all x such that x > 0"
        result = self.service.translate_selection_async(
            tce_text,
            LanguageMode.TCE,
            LanguageMode.TAU
        )
        
        assert result.is_success()
        tau_translation = result.value
        assert "forall" in tau_translation
    
    # =======================
    # Context Help
    # =======================
    
    def test_context_help_provides_guidance(self):
        """Test: Context help explains current editing context."""
        contexts = [
            (ContextType.SOLVER_COMMAND, "solver"),
            (ContextType.TEMPORAL_CONSTRAINT, "temporal"),
            (ContextType.QUANTIFIER_EXPRESSION, "quantifier"),
            (ContextType.STREAM_RULE, "stream"),
            (ContextType.FUNCTION_DEFINITION, "function")
        ]
        
        for context_type, expected_keyword in contexts:
            context = SpecificationContext(
                full_text="",
                cursor_position=CursorPosition(0),
                language_mode=LanguageMode.TAU,
                context_type=context_type,
                learning_level=DifficultyLevel.INTERMEDIATE
            )
            
            result = self.service.get_context_help_async(context)
            assert result.is_success()
            help_text = result.value
            assert expected_keyword in help_text.lower()
    
    # =======================
    # Configuration Tests
    # =======================
    
    def test_respects_max_suggestions_config(self):
        """Test: Service respects max suggestions configuration."""
        config = AutocompleteConfiguration(max_suggestions=3)
        service = EducationalAutocompleteService(config)
        
        context = SpecificationContext(
            full_text="",
            cursor_position=CursorPosition(0),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.LOGICAL_ASSERTION,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        request = SuggestionRequest(context=context, max_suggestions=10)
        result = service.get_suggestions_async(request)
        
        assert result.is_success()
        assert len(result.value.suggestions) <= 3