"""
Unit Tests for the Pattern-Based Translation Engine.
"""

import pytest
from backend.unified.translators.pattern_translator import PatternTranslationEngine
from backend.unified.core.engine_interface import TranslationDirection

class TestPatternTranslationEngine:
    """Tests for the PatternTranslationEngine."""

    @pytest.fixture
    def engine(self):
        """Provides a PatternTranslationEngine instance."""
        return PatternTranslationEngine()

    def test_initialization(self, engine):
        """Test that the engine initializes correctly."""
        assert engine.name == "pattern_based"
        assert len(engine.get_supported_directions()) > 0

    def test_translate_tce_to_tau_basic_expressions(self, engine):
        """Test translating basic TCE expressions to Tau."""
        # Test logical AND
        result = engine.translate("x and y", TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == "x & y"

        # Test logical OR
        result = engine.translate("x or y", TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == "x | y"

        # Test logical NOT
        result = engine.translate("not x", TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == "!x"

    def test_translate_tce_to_tau_definitions(self, engine):
        """Test translating TCE definitions to Tau."""
        tce_def = "define predicate p(x) as x > 0"
        result = engine.translate(tce_def, TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == "p(x) := x > 0"

    def test_translate_tau_to_tce_reverse(self, engine):
        """Test reverse translation from Tau to TCE."""
        # Test definition reverse
        tau_def = "p(x) := x > 0"
        result = engine.translate(tau_def, TranslationDirection.TO_TCE)
        assert result.success
        assert "define predicate p(x) as x > 0" in result.translated_text

        # Test simple expression
        tau_expr = "x & y"
        result = engine.translate(tau_expr, TranslationDirection.TO_TCE)
        assert result.success
        assert "x and y" in result.translated_text

    def test_translate_unsupported_tce(self, engine):
        """Test that unsupported TCE returns the original text with low confidence."""
        tce_text = "this is some complex narrative text that has no direct pattern."
        result = engine.translate(tce_text, TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == tce_text
        assert result.confidence < 0.1

    def test_translate_unsupported_tau(self, engine):
        """Test that unsupported Tau returns the original text with low confidence."""
        tau_text = "some_unfamiliar_tau_function(a, b, c)"
        result = engine.translate(tau_text, TranslationDirection.TO_TCE)
        assert result.success
        assert result.translated_text == tau_text
        assert result.confidence < 0.1

    def test_translate_implications(self, engine):
        """Test translating implications."""
        tce_text = "if x > 0 then x is positive"
        result = engine.translate(tce_text, TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == "(x > 0) -> (x is positive)"

    def test_translate_temporal_operators(self, engine):
        """Test translating temporal operators."""
        # Test always
        tce_always = "always x is true"
        result = engine.translate(tce_always, TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == "always(x is true)"

        # Test sometimes
        tce_sometimes = "sometimes x happens"
        result = engine.translate(tce_sometimes, TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text == "sometimes(x happens)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])