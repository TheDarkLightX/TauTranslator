"""
Unit tests for TAU suggestion engine following TDD principles.

Tests are written before implementation to drive the design.
Each test name describes the behavior being tested.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add the backend path to sys.path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.unified.core.autocomplete.models import (
    EducationalSuggestion,
    SuggestionCategory,
    DifficultyLevel,
    SpecificationContext,
    LanguageMode,
    ContextType,
    SuggestionText,
    DisplayText,
    HintText,
    ExampleCode,
    CursorPosition
)
from backend.unified.core.autocomplete.tau_suggestion_engine import TauSuggestionEngine


class TestTauSuggestionEngine:
    """Test TAU language suggestion generation."""
    
    def setup_method(self):
        """Initialize engine for each test."""
        self.engine = TauSuggestionEngine()
    
    # =======================
    # Basic Keyword Suggestions
    # =======================
    
    def test_suggests_temporal_keywords_from_prefix(self):
        """Test: typing 'alw' suggests 'always' with educational hint."""
        context = SpecificationContext(
            full_text="alw",
            cursor_position=CursorPosition(3),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.TEMPORAL_CONSTRAINT,
            learning_level=DifficultyLevel.BEGINNER
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        always_suggestion = next(
            (s for s in suggestions if s.text == "always"),
            None
        )
        assert always_suggestion is not None
        assert always_suggestion.category == SuggestionCategory.TEMPORAL
        assert "invariant" in always_suggestion.description.lower()
        assert always_suggestion.example == "always (x > 0)"
    
    def test_suggests_quantifiers_from_prefix(self):
        """Test: typing 'for' suggests 'forall' with template."""
        context = SpecificationContext(
            full_text="for",
            cursor_position=CursorPosition(3),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.QUANTIFIER_EXPRESSION,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        forall_suggestion = next(
            (s for s in suggestions if s.text == "forall"),
            None
        )
        assert forall_suggestion is not None
        assert forall_suggestion.template == "forall $var : $condition"
        assert forall_suggestion.category == SuggestionCategory.QUANTIFIER
    
    # =======================
    # Context-Aware Suggestions
    # =======================
    
    def test_suggests_equation_patterns_after_solve(self):
        """Test: after 'solve ' suggests equation patterns."""
        context = SpecificationContext(
            full_text="solve ",
            cursor_position=CursorPosition(6),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.SOLVER_COMMAND,
            learning_level=DifficultyLevel.BEGINNER
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        # Should suggest simple equation pattern
        equation_suggestion = next(
            (s for s in suggestions if "$var = $expr" in s.template),
            None
        )
        assert equation_suggestion is not None
        assert equation_suggestion.category == SuggestionCategory.PATTERN
        assert "equation" in equation_suggestion.description.lower()
    
    def test_suggests_temporal_indices_in_brackets(self):
        """Test: typing 'x[' suggests temporal indices."""
        context = SpecificationContext(
            full_text="x[",
            cursor_position=CursorPosition(2),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.STREAM_RULE,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        # Check for temporal index suggestions
        t_suggestion = next((s for s in suggestions if s.text == "t"), None)
        t_minus_1 = next((s for s in suggestions if s.text == "t-1"), None)
        
        assert t_suggestion is not None
        assert t_suggestion.description == "Current time"
        assert t_minus_1 is not None
        assert t_minus_1.description == "Previous time step"
    
    # =======================
    # Progressive Learning
    # =======================
    
    def test_beginner_mode_provides_simple_suggestions(self):
        """Test: beginner mode shows only basic constructs."""
        context = SpecificationContext(
            full_text="",
            cursor_position=CursorPosition(0),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.LOGICAL_ASSERTION,
            learning_level=DifficultyLevel.BEGINNER
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        # Should have some suggestions
        assert len(suggestions) > 0
        
        # Should not include advanced constructs like forall
        assert not any("forall" in s.text for s in suggestions)
        
        # Should include beginner-friendly constructs
        beginner_keywords = ["true", "false", "solve", "DEFINE"]
        assert any(s.text in beginner_keywords for s in suggestions)
    
    def test_advanced_mode_includes_complex_patterns(self):
        """Test: advanced mode shows complex constructs."""
        context = SpecificationContext(
            full_text="",
            cursor_position=CursorPosition(0),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.LOGICAL_ASSERTION,
            learning_level=DifficultyLevel.ADVANCED
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        # Should include advanced patterns
        advanced_suggestions = [s for s in suggestions 
                               if s.difficulty == DifficultyLevel.ADVANCED]
        assert len(advanced_suggestions) > 0
    
    # =======================
    # Template Generation
    # =======================
    
    def test_generates_function_definition_template(self):
        """Test: after 'DEFINE' suggests function templates."""
        context = SpecificationContext(
            full_text="DEFINE ",
            cursor_position=CursorPosition(7),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.FUNCTION_DEFINITION,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        function_template = next(
            (s for s in suggestions if "$name($args) :=" in s.template),
            None
        )
        assert function_template is not None
        assert function_template.category == SuggestionCategory.DEFINITION
    
    # =======================
    # Educational Content
    # =======================
    
    def test_all_suggestions_include_educational_content(self):
        """Test: every suggestion has description and example."""
        context = SpecificationContext(
            full_text="",
            cursor_position=CursorPosition(0),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.LOGICAL_ASSERTION,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        for suggestion in suggestions:
            assert suggestion.description != ""
            assert suggestion.example != ""
            assert suggestion.category is not None