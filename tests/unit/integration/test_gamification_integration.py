"""
Integration tests for the gamification system with other components like autocomplete.

Copyright: DarkLightX / Dana Edwards
"""

import pytest

from backend.unified.domain.gamification_types import UserId
from backend.unified.core.gamified_autocomplete_app import GamifiedAutocompleteApplication
from src.tau_translator_omega.core_engine.result_enhanced import Success, Failure # Updated import


class TestGamificationIntegration:
    """Test integration with autocomplete."""
    
    def test_autocomplete_with_gamification(self):
        """Test autocomplete request with XP tracking."""
        app = GamifiedAutocompleteApplication(
            user_id=UserId("test_user"),
            username="Test User"
        )
        
        # Create autocomplete request
        from backend.unified.core.autocomplete.models import (
            SuggestionRequest, SpecificationContext, LanguageMode,
            ContextType, DifficultyLevel, CursorPosition
        )
        
        context = SpecificationContext(
            full_text="forall x : ",
            cursor_position=CursorPosition(11),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.QUANTIFIER_EXPRESSION,
            parent_constructs=[],
            variables_in_scope=["x"],
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        request = SuggestionRequest(
            context=context,
            max_suggestions=5
        )
        
        # Process request
        result = app.process_autocomplete_request(request)
        
        assert result.is_success()
        response = result.value
        assert len(response.suggestions) > 0
    
    def test_suggestion_usage_tracking(self):
        """Test XP gain from using suggestions."""
        app = GamifiedAutocompleteApplication(
            user_id=UserId("test_user"),
            username="Test User"
        )
        
        # Get initial XP
        initial_xp = app._profile.total_xp if app._profile else 0
        
        # Create mock suggestion
        from backend.unified.core.autocomplete.models import (
            EducationalSuggestion, SuggestionText, DisplayText,
            HintText, ExampleCode, SuggestionCategory, ConfidenceScore,
            SpecificationContext, LanguageMode, ContextType,
            DifficultyLevel, CursorPosition # Added missing CursorPosition
        )
        
        suggestion = EducationalSuggestion(
            text=SuggestionText("x > 0"),
            display=DisplayText("x > 0 - Positive constraint"),
            category=SuggestionCategory.PATTERN,
            description=HintText("Constrains x to positive values"),
            example=ExampleCode("forall x : x > 0 -> f(x) > 0"),
            difficulty=DifficultyLevel.BEGINNER,
            confidence=ConfidenceScore(0.9)
        )
        
        context = SpecificationContext(
            full_text="forall x : ",
            cursor_position=CursorPosition(11),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.QUANTIFIER_EXPRESSION,
            parent_constructs=[],
            variables_in_scope=["x"]
        )
        
        # Use suggestion
        result = app.use_suggestion(suggestion, context)
        assert result.is_success()
        
        # Check XP increased
        if app._profile:
            assert app._profile.total_xp > initial_xp
    
    def test_translation_tracking(self):
        """Test XP gain from translations."""
        app = GamifiedAutocompleteApplication(
            user_id=UserId("test_user"),
            username="Test User"
        )
        
        # Get initial XP
        initial_xp = app._profile.total_xp if app._profile else 0
        
        # Complete translation
        result = app.complete_translation(
            "for all x such that x > 0",
            "forall x : x > 0",
            "TCE",
            "TAU"
        )
        
        assert result.is_success()
        
        # Check XP increased (25 XP for translations)
        if app._profile:
            assert app._profile.total_xp >= initial_xp + 25
