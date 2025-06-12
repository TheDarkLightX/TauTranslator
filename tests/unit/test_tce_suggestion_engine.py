"""
Unit tests for TCE (Tau Controlled English) suggestion engine.

Tests controlled English patterns that map to TAU syntax.
Following TDD principles - tests written before implementation.

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
    CursorPosition,
    TauCode
)
from backend.unified.core.autocomplete.tce_suggestion_engine import TceSuggestionEngine


class TestTceSuggestionEngine:
    """Test TCE (Controlled English) suggestion generation."""
    
    def setup_method(self):
        """Initialize engine for each test."""
        self.engine = TceSuggestionEngine()
    
    # =======================
    # Controlled English Patterns
    # =======================
    
    def test_suggests_universal_quantification_pattern(self):
        """Test: typing 'for all' suggests controlled English pattern."""
        context = SpecificationContext(
            full_text="for all",
            cursor_position=CursorPosition(7),
            language_mode=LanguageMode.TCE,
            context_type=ContextType.QUANTIFIER_EXPRESSION,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        forall_pattern = next(
            (s for s in suggestions if "for all" in s.text),
            None
        )
        assert forall_pattern is not None
        assert forall_pattern.tau_equivalent == "forall $objects : $condition"
        assert "Universal quantification" in forall_pattern.description
    
    def test_suggests_existence_pattern(self):
        """Test: typing 'there exists' suggests existence pattern."""
        context = SpecificationContext(
            full_text="there exists",
            cursor_position=CursorPosition(12),
            language_mode=LanguageMode.TCE,
            context_type=ContextType.QUANTIFIER_EXPRESSION,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        exists_pattern = next(
            (s for s in suggestions if "there exists" in s.text),
            None
        )
        assert exists_pattern is not None
        assert "exists $object : $property" in exists_pattern.tau_equivalent
    
    def test_suggests_temporal_patterns_in_english(self):
        """Test: typing 'it is always' suggests temporal pattern."""
        context = SpecificationContext(
            full_text="it is always",
            cursor_position=CursorPosition(12),
            language_mode=LanguageMode.TCE,
            context_type=ContextType.TEMPORAL_CONSTRAINT,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        always_pattern = next(
            (s for s in suggestions if "it is always the case that" in s.text),
            None
        )
        assert always_pattern is not None
        assert always_pattern.tau_equivalent == "always ($property)"
    
    def test_suggests_conditional_patterns(self):
        """Test: typing 'if' suggests conditional pattern."""
        context = SpecificationContext(
            full_text="if",
            cursor_position=CursorPosition(2),
            language_mode=LanguageMode.TCE,
            context_type=ContextType.LOGICAL_ASSERTION,
            learning_level=DifficultyLevel.BEGINNER
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        if_pattern = next(
            (s for s in suggestions if s.text.startswith("if")),
            None
        )
        assert if_pattern is not None
        assert "->" in if_pattern.tau_equivalent
        assert "implication" in if_pattern.description.lower()
    
    # =======================
    # Solution Finding Patterns
    # =======================
    
    def test_suggests_find_pattern_for_solving(self):
        """Test: typing 'find' suggests solution-finding pattern."""
        context = SpecificationContext(
            full_text="find",
            cursor_position=CursorPosition(4),
            language_mode=LanguageMode.TCE,
            context_type=ContextType.SOLVER_COMMAND,
            learning_level=DifficultyLevel.BEGINNER
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        find_pattern = next(
            (s for s in suggestions if "find a value" in s.text),
            None
        )
        assert find_pattern is not None
        assert "solve" in find_pattern.tau_equivalent
    
    # =======================
    # Stream Patterns
    # =======================
    
    def test_suggests_stream_patterns_in_english(self):
        """Test: typing 'output at' suggests stream pattern."""
        context = SpecificationContext(
            full_text="output at",
            cursor_position=CursorPosition(9),
            language_mode=LanguageMode.TCE,
            context_type=ContextType.STREAM_RULE,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        output_pattern = next(
            (s for s in suggestions if "output at time" in s.text),
            None
        )
        assert output_pattern is not None
        assert "[t]" in output_pattern.tau_equivalent
    
    # =======================
    # Learning Features
    # =======================
    
    def test_all_tce_suggestions_show_tau_equivalent(self):
        """Test: every TCE suggestion shows TAU equivalent."""
        context = SpecificationContext(
            full_text="",
            cursor_position=CursorPosition(0),
            language_mode=LanguageMode.TCE,
            context_type=ContextType.LOGICAL_ASSERTION,
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        # All TCE suggestions should have TAU equivalents
        for suggestion in suggestions:
            assert suggestion.tau_equivalent is not None
            assert len(suggestion.tau_equivalent) > 0
    
    def test_beginner_mode_shows_simple_english_patterns(self):
        """Test: beginner mode shows simple English patterns."""
        context = SpecificationContext(
            full_text="",
            cursor_position=CursorPosition(0),
            language_mode=LanguageMode.TCE,
            context_type=ContextType.LOGICAL_ASSERTION,
            learning_level=DifficultyLevel.BEGINNER
        )
        
        suggestions = self.engine.get_suggestions_for_context(context)
        
        # Should include simple patterns
        simple_patterns = ["if", "then", "equals", "is greater than"]
        suggestion_texts = [s.text for s in suggestions]
        assert any(pattern in text for pattern in simple_patterns 
                  for text in suggestion_texts)