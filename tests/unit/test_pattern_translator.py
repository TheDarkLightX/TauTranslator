"""
Comprehensive unit tests for the pattern-based translation engine.

Author: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.pattern_translator import PatternTranslationEngine
from backend.unified.translators.base import TranslationDirection, TranslationResult


class TestPatternTranslationEngine:
    """Unit tests for PatternTranslationEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a pattern translation engine instance."""
        return PatternTranslationEngine()
    
    # Basic functionality tests
    
    def test_engine_initialization(self, engine):
        """Test engine initializes correctly."""
        assert engine.name == "pattern_based"
        assert engine.description == "Simple pattern-based translation with regex rules"
        assert engine.is_available == True
        assert len(engine.tce_to_tau_patterns) > 0
        assert len(engine.tau_to_tce_patterns) > 0
    
    def test_can_translate_valid_input(self, engine):
        """Test can_translate returns True for valid input."""
        assert engine.can_translate("x equals 5", TranslationDirection.TO_TAU)
        assert engine.can_translate("x > 5", TranslationDirection.TO_TCE)
    
    def test_can_translate_invalid_input(self, engine):
        """Test can_translate returns False for invalid input."""
        assert not engine.can_translate("", TranslationDirection.TO_TAU)
        assert not engine.can_translate(None, TranslationDirection.TO_TAU)
        assert not engine.can_translate("   ", TranslationDirection.TO_TCE)
    
    def test_supported_directions(self, engine):
        """Test engine reports correct supported directions."""
        directions = engine.get_supported_directions()
        assert TranslationDirection.TO_TAU in directions
        assert TranslationDirection.TO_TCE in directions
        assert len(directions) == 2
    
    # TCE to Tau translation tests
    
    def test_tce_to_tau_basic_operators(self, engine):
        """Test basic operator translations from TCE to Tau."""
        test_cases = [
            ("x equals 5", "x=5"),
            ("x plus y", "x+y"),
            ("x minus y", "x-y"),
            ("x times y", "x*y"),
            ("x divided by y", "x/y"),
        ]
        
        for tce, expected_tau in test_cases:
            result = engine.translate(tce, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected_tau
            assert result.confidence > 0
    
    def test_tce_to_tau_logical_operators(self, engine):
        """Test logical operator translations from TCE to Tau."""
        test_cases = [
            ("x and y", "x&y"),
            ("x or y", "x|y"),
            ("not x", "!x"),
            ("x and y or z", "x&y|z"),
            ("not x and y", "!x&y"),
        ]
        
        for tce, expected_tau in test_cases:
            result = engine.translate(tce, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected_tau
    
    def test_tce_to_tau_time_expressions(self, engine):
        """Test time expression translations."""
        test_cases = [
            ("x at time t", "x[t]"),
            ("x at time 5", "x[5]"),
            ("x equals 5 at time t", "x=5[t]"),
        ]
        
        for tce, expected_tau in test_cases:
            result = engine.translate(tce, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected_tau
    
    def test_tce_to_tau_removes_articles(self, engine):
        """Test that articles are removed during translation."""
        result = engine.translate("the x equals the y", TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == "x=y"
    
    # Tau to TCE translation tests
    
    def test_tau_to_tce_basic_operators(self, engine):
        """Test basic operator translations from Tau to TCE."""
        test_cases = [
            ("x=5", "x equals 5"),
            ("x+y", "x plus y"),
            ("x-y", "x minus y"),
            ("x*y", "x times y"),
            ("x/y", "x divided by y"),
        ]
        
        for tau, expected_tce in test_cases:
            result = engine.translate(tau, TranslationDirection.TO_TCE)
            assert result.success
            assert result.translated_text == expected_tce
    
    def test_tau_to_tce_logical_operators(self, engine):
        """Test logical operator translations from Tau to TCE."""
        test_cases = [
            ("x&y", "x and y"),
            ("x|y", "x or y"),
            ("!x", " not x"),  # Note: pattern adds space
            ("x&y|z", "x and y or z"),
        ]
        
        for tau, expected_tce in test_cases:
            result = engine.translate(tau, TranslationDirection.TO_TCE)
            assert result.success
            assert result.translated_text == expected_tce
    
    def test_tau_to_tce_time_expressions(self, engine):
        """Test time expression translations."""
        test_cases = [
            ("x[t]", "x at time t"),
            ("x[5]", "x at time 5"),
            ("y[now]", "y at time now"),
        ]
        
        for tau, expected_tce in test_cases:
            result = engine.translate(tau, TranslationDirection.TO_TCE)
            assert result.success
            assert result.translated_text == expected_tce
    
    # Edge cases and error handling
    
    def test_empty_input_handling(self, engine):
        """Test handling of empty input."""
        result = engine.translate("", TranslationDirection.TO_TAU)
        assert not result.success
        assert result.error_message == "Pattern engine cannot handle this translation"
    
    def test_whitespace_only_input(self, engine):
        """Test handling of whitespace-only input."""
        result = engine.translate("   \t\n  ", TranslationDirection.TO_TAU)
        assert not result.success
    
    def test_mixed_case_handling(self, engine):
        """Test case-insensitive pattern matching."""
        test_cases = [
            ("X EQUALS 5", "x=5"),
            ("X AND Y", "x&y"),
            ("NOT X", "!x"),
        ]
        
        for input_text, expected in test_cases:
            result = engine.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected
    
    def test_multiple_spaces_cleaned(self, engine):
        """Test that multiple spaces are cleaned up."""
        result = engine.translate("x    equals    5", TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == "x=5"
    
    def test_complex_nested_expressions(self, engine):
        """Test translation of complex nested expressions."""
        test_cases = [
            ("x and y or z and w", "x&y|z&w"),
            ("not x or not y", "!x|!y"),
            ("x plus y times z", "x+y*z"),
        ]
        
        for tce, expected_tau in test_cases:
            result = engine.translate(tce, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected_tau
    
    # Confidence calculation tests
    
    def test_confidence_calculation(self, engine):
        """Test confidence score calculation."""
        # Simple expression should have moderate confidence
        result1 = engine.translate("x equals 5", TranslationDirection.TO_TAU)
        assert 0.5 <= result1.confidence <= 0.95
        
        # Expression with operators should have higher confidence
        result2 = engine.translate("x and y or z", TranslationDirection.TO_TAU)
        assert result2.confidence > 0.5
        
        # Very short translation might have lower confidence
        result3 = engine.translate("x", TranslationDirection.TO_TAU)
        assert result3.confidence < 0.8
    
    def test_confidence_capped_at_95(self, engine):
        """Test that confidence is capped at 95% for pattern-based translation."""
        # Even perfect translations should not exceed 95% confidence
        result = engine.translate("x equals 5 and y equals 10", TranslationDirection.TO_TAU)
        assert result.success
        assert result.confidence <= 0.95
    
    # Metadata tests
    
    def test_result_metadata(self, engine):
        """Test that results include proper metadata."""
        result = engine.translate("x equals 5", TranslationDirection.TO_TAU)
        assert result.success
        assert "patterns_applied" in result.metadata
        assert result.metadata["patterns_applied"] > 0
        assert result.metadata["engine_type"] == "pattern_based"
    
    def test_processing_time_recorded(self, engine):
        """Test that processing time is recorded."""
        result = engine.translate("x equals 5", TranslationDirection.TO_TAU)
        assert result.success
        assert result.processing_time > 0
        assert result.processing_time < 1.0  # Should be fast
    
    # Pattern application tests
    
    def test_pattern_order_matters(self, engine):
        """Test that pattern order is preserved."""
        # 'and' should be replaced before cleaning spaces
        result = engine.translate("x and and y", TranslationDirection.TO_TAU)
        assert result.success
        # Should result in "x&&y" not "x&y"
        assert "&&" in result.translated_text
    
    def test_no_partial_word_replacement(self, engine):
        """Test that patterns don't replace parts of words."""
        # 'or' in 'order' should not be replaced
        result = engine.translate("order equals 5", TranslationDirection.TO_TAU)
        assert result.success
        assert "order" in result.translated_text
        assert "|der" not in result.translated_text
    
    # Special character handling
    
    def test_special_characters_preserved(self, engine):
        """Test that non-pattern special characters are preserved."""
        test_cases = [
            ("x > 5", "x > 5"),  # Comparison operators preserved
            ("x < 10", "x < 10"),
            ("x >= 5", "x >= 5"),
        ]
        
        for input_text, expected in test_cases:
            result = engine.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected
    
    def test_unicode_handling(self, engine):
        """Test handling of unicode characters."""
        result = engine.translate("x equals 5 € and y equals 10 °C", TranslationDirection.TO_TAU)
        assert result.success
        # Unicode should be preserved
        assert "€" in result.translated_text
        assert "°C" in result.translated_text


class TestPatternTranslationEngineInternal:
    """Test internal methods of PatternTranslationEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a pattern translation engine instance."""
        return PatternTranslationEngine()
    
    def test_apply_patterns_method(self, engine):
        """Test the _apply_patterns internal method."""
        patterns = [("hello", "goodbye"), ("world", "universe")]
        result = engine._apply_patterns("hello world", patterns)
        assert result == "goodbye universe"
    
    def test_clean_translation_method(self, engine):
        """Test the _clean_translation internal method."""
        # Test multiple spaces
        assert engine._clean_translation("x  =  5", TranslationDirection.TO_TAU) == "x=5"
        
        # Test leading/trailing spaces
        assert engine._clean_translation("  x=5  ", TranslationDirection.TO_TAU) == "x=5"
        
        # Test spaces around operators
        assert engine._clean_translation("x & y | z", TranslationDirection.TO_TAU) == "x&y|z"
    
    def test_calculate_confidence_method(self, engine):
        """Test the _calculate_confidence internal method."""
        # Empty translation
        assert engine._calculate_confidence("test", "") == 0.0
        
        # Same length translation
        conf1 = engine._calculate_confidence("test", "abcd")
        assert 0 < conf1 < 1
        
        # Translation with operators (higher confidence)
        conf2 = engine._calculate_confidence("test", "a&b")
        assert conf2 > conf1
    
    def test_get_patterns_for_direction(self, engine):
        """Test the _get_patterns_for_direction internal method."""
        tau_patterns = engine._get_patterns_for_direction(TranslationDirection.TO_TAU)
        assert len(tau_patterns) > 0
        assert tau_patterns == engine.tce_to_tau_patterns
        
        tce_patterns = engine._get_patterns_for_direction(TranslationDirection.TO_TCE)
        assert len(tce_patterns) > 0
        assert tce_patterns == engine.tau_to_tce_patterns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])