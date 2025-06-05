"""
Test parser-first, pattern-fallback translation integration.

This test suite verifies that:
1. Grammar parser is attempted first for translations
2. Pattern-based translation is used as fallback when parsing fails
3. The system correctly handles various edge cases

Author: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.manager import TranslationManager
from backend.unified.translators.grammar_translator import GrammarTranslationEngine
from backend.unified.translators.pattern_translator import PatternTranslationEngine
from backend.unified.translators.base import TranslationDirection


class TestParserPatternFallback:
    """Test the parser-first, pattern-fallback integration."""
    
    @pytest.fixture
    def translation_manager(self):
        """Create a translation manager with grammar and pattern engines."""
        manager = TranslationManager()
        
        # Register grammar engine as default
        grammar_engine = GrammarTranslationEngine()
        manager.register_engine(grammar_engine, is_default=True)
        
        # Register pattern engine as fallback
        pattern_engine = PatternTranslationEngine()
        manager.register_engine(pattern_engine, is_fallback=True)
        
        return manager
    
    def test_simple_tau_to_tce_grammar_success(self, translation_manager):
        """Test that simple Tau expressions use grammar parser successfully."""
        tau_expr = "x > 5 & y < 10"
        result = translation_manager.translate(tau_expr, TranslationDirection.TO_TCE)
        
        assert result.success
        assert result.translation_method == "grammar_aware"
        assert "engine_type" in result.metadata
        assert result.metadata["engine_type"] == "grammar_parser"
        assert result.confidence > 0.9  # Grammar parsing has high confidence
    
    def test_simple_tce_to_tau_grammar_success(self, translation_manager):
        """Test that simple TCE expressions use grammar parser successfully."""
        tce_expr = "x equals 5 and y equals 10"
        result = translation_manager.translate(tce_expr, TranslationDirection.TO_TAU)
        
        assert result.success
        assert result.translation_method == "grammar_aware"
        assert result.confidence > 0.9
    
    def test_malformed_expression_falls_back_to_pattern(self, translation_manager):
        """Test that malformed expressions fall back to pattern translation."""
        # This expression is intentionally malformed for the grammar parser
        malformed_expr = "x and and y or not z"
        result = translation_manager.translate(malformed_expr, TranslationDirection.TO_TAU)
        
        # Should still succeed due to pattern fallback
        assert result.success
        assert result.translation_method == "pattern_based"
        assert result.confidence < 0.96  # Pattern has lower confidence
        assert "x&&&y|!z" in result.translated_text or "x&&y|!z" in result.translated_text
    
    def test_complex_expression_parser_then_pattern(self, translation_manager):
        """Test complex expressions that might challenge the parser."""
        # Complex nested expression
        complex_expr = "if x > 5 then (y equals 10 or z equals 20) else w equals 30"
        result = translation_manager.translate(complex_expr, TranslationDirection.TO_TAU)
        
        # Either parser handles it or falls back to pattern
        assert result.success
        assert result.translation_method in ["grammar_aware", "pattern_based"]
        
        # Check that translation happened
        assert result.translated_text != complex_expr
    
    def test_empty_input_fails_both(self, translation_manager):
        """Test that empty input fails validation in both engines."""
        result = translation_manager.translate("", TranslationDirection.TO_TAU)
        
        assert not result.success
        assert "Empty input" in result.error_message
    
    def test_very_long_input_handling(self, translation_manager):
        """Test handling of very long inputs."""
        # Create a long but valid expression
        long_expr = " and ".join([f"x{i} equals {i}" for i in range(50)])
        result = translation_manager.translate(long_expr, TranslationDirection.TO_TAU)
        
        # Should handle long input
        assert result.success
        assert len(result.translated_text) > 0
    
    def test_unicode_and_special_chars(self, translation_manager):
        """Test handling of unicode and special characters."""
        unicode_expr = "x equals 5 € and y equals 10 °C"
        result = translation_manager.translate(unicode_expr, TranslationDirection.TO_TAU)
        
        # Should handle unicode gracefully
        assert result.success or (not result.success and result.error_message)
    
    def test_fallback_chain_statistics(self, translation_manager):
        """Test that fallback usage is tracked in statistics."""
        # Reset statistics
        translation_manager.reset_statistics()
        
        # Do some translations that should use grammar
        good_exprs = [
            "x equals 5",
            "y > 10",
            "a and b"
        ]
        
        for expr in good_exprs:
            translation_manager.translate(expr, TranslationDirection.TO_TAU)
        
        # Do some that might fall back to pattern
        tricky_exprs = [
            "malformed expression here",
            "another bad one",
        ]
        
        for expr in tricky_exprs:
            translation_manager.translate(expr, TranslationDirection.TO_TAU)
        
        stats = translation_manager.get_statistics()
        
        assert stats['total_translations'] == len(good_exprs) + len(tricky_exprs)
        assert stats['successful_translations'] > 0
        
        # Check engine usage
        assert 'grammar_aware' in stats['engine_usage'] or 'pattern_based' in stats['engine_usage']
    
    def test_parallel_translation_with_fallback(self, translation_manager):
        """Test parallel translation mode with both engines."""
        expr = "x equals 5 and y equals 10"
        results = translation_manager.translate_parallel(expr, TranslationDirection.TO_TAU)
        
        assert len(results) >= 2  # Should have results from both engines
        
        # Results should be sorted by confidence
        confidences = [r.confidence for r in results]
        assert confidences == sorted(confidences, reverse=True)
        
        # Grammar should have higher confidence than pattern
        grammar_results = [r for r in results if r.translation_method == "grammar_aware"]
        pattern_results = [r for r in results if r.translation_method == "pattern_based"]
        
        if grammar_results and pattern_results:
            assert grammar_results[0].confidence > pattern_results[0].confidence
    
    def test_engine_specific_translation(self, translation_manager):
        """Test requesting translation from specific engine."""
        expr = "x equals 5"
        
        # Force grammar engine
        grammar_result = translation_manager.translate(
            expr, 
            TranslationDirection.TO_TAU,
            engine_name="grammar_aware"
        )
        
        assert grammar_result.translation_method == "grammar_aware"
        
        # Force pattern engine
        pattern_result = translation_manager.translate(
            expr,
            TranslationDirection.TO_TAU, 
            engine_name="pattern_based"
        )
        
        assert pattern_result.translation_method == "pattern_based"
        
        # Grammar should generally produce different (better) results
        # but both should succeed
        assert grammar_result.success
        assert pattern_result.success
    
    def test_disable_fallback(self, translation_manager):
        """Test disabling fallback behavior."""
        # Use an expression that will fail grammar parsing
        bad_expr = "this is not valid tau or tce syntax at all!!!"
        
        # With fallback disabled, should fail
        result = translation_manager.translate(
            bad_expr,
            TranslationDirection.TO_TAU,
            use_fallback=False
        )
        
        # Should fail since grammar can't parse it and fallback is disabled
        assert not result.success
        assert "grammar_aware" in result.translation_method or "parse error" in result.error_message.lower()
    
    def test_tau_to_tce_round_trip(self, translation_manager):
        """Test round-trip translation from Tau to TCE and back."""
        original_tau = "x > 5 & y < 10"
        
        # Tau to TCE
        tce_result = translation_manager.translate(original_tau, TranslationDirection.TO_TCE)
        assert tce_result.success
        
        # TCE back to Tau
        tau_result = translation_manager.translate(
            tce_result.translated_text,
            TranslationDirection.TO_TAU
        )
        assert tau_result.success
        
        # Should be similar (might have minor formatting differences)
        assert tau_result.translated_text.replace(" ", "") == original_tau.replace(" ", "")
    
    def test_health_check_both_engines(self, translation_manager):
        """Test health check reports both engines correctly."""
        health = translation_manager.health_check()
        
        assert health['overall_status'] in ['healthy', 'degraded']
        assert 'grammar_aware' in health['engines']
        assert 'pattern_based' in health['engines']
        
        # Both engines should be available
        assert health['engines']['grammar_aware']['is_available']
        assert health['engines']['pattern_based']['is_available']
    
    def test_confidence_threshold(self, translation_manager):
        """Test that confidence threshold affects translation results."""
        # Set high confidence threshold
        translation_manager.set_confidence_threshold(0.95)
        
        # Pattern engine typically has confidence < 0.95
        # So if grammar fails, the overall result might not meet threshold
        expr = "simple expression"
        result = translation_manager.translate(expr, TranslationDirection.TO_TAU)
        
        # Should still get a result, but can check confidence
        if result.success:
            # If pattern was used, confidence might be below our threshold
            if result.translation_method == "pattern_based":
                assert result.confidence <= 0.95


class TestEdgeCases:
    """Test edge cases in the parser-pattern fallback system."""
    
    @pytest.fixture
    def translation_manager(self):
        """Create a translation manager with grammar and pattern engines."""
        manager = TranslationManager()
        grammar_engine = GrammarTranslationEngine()
        pattern_engine = PatternTranslationEngine()
        manager.register_engine(grammar_engine, is_default=True)
        manager.register_engine(pattern_engine, is_fallback=True)
        return manager
    
    def test_parser_timeout_falls_back_to_pattern(self, translation_manager):
        """Test that parser timeouts trigger pattern fallback."""
        # Create a potentially complex expression that might timeout
        complex_expr = " & ".join([f"(x{i} > {i} | y{i} < {i*2})" for i in range(100)])
        
        result = translation_manager.translate(complex_expr, TranslationDirection.TO_TCE)
        
        # Should get a result (either from parser or pattern)
        assert result.success or result.error_message
        assert result.processing_time < 35  # Should complete within timeout
    
    def test_mixed_language_input(self, translation_manager):
        """Test handling of mixed Tau/TCE input."""
        # Mix of Tau symbols and English words
        mixed_expr = "x > 5 and y < 10"  # 'and' is English, operators are Tau
        
        result = translation_manager.translate(mixed_expr, TranslationDirection.TO_TAU)
        
        # Should handle mixed input
        assert result.success
        assert "&" in result.translated_text  # 'and' should become '&'
    
    def test_whitespace_handling(self, translation_manager):
        """Test various whitespace scenarios."""
        whitespace_cases = [
            "x  equals   5",  # Multiple spaces
            "\tx equals 5\n",  # Tabs and newlines
            "  x equals 5  ",  # Leading/trailing spaces
            "x\tequals\t5",   # Tabs between words
        ]
        
        for expr in whitespace_cases:
            result = translation_manager.translate(expr, TranslationDirection.TO_TAU)
            assert result.success
            assert "x" in result.translated_text
            assert "5" in result.translated_text
    
    def test_case_sensitivity(self, translation_manager):
        """Test case handling in translations."""
        case_variants = [
            "X EQUALS 5",
            "x Equals 5", 
            "X equals 5",
            "x EQUALS 5"
        ]
        
        results = []
        for expr in case_variants:
            result = translation_manager.translate(expr, TranslationDirection.TO_TAU)
            assert result.success
            results.append(result.translated_text)
        
        # All should produce similar tau (modulo case)
        normalized = [r.lower().replace(" ", "") for r in results]
        assert len(set(normalized)) == 1  # All should be the same when normalized


if __name__ == "__main__":
    pytest.main([__file__, "-v"])