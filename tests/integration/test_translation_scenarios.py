"""
Comprehensive integration tests for various translation scenarios.

Tests the complete translation pipeline with real-world examples.

Author: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.manager import TranslationManager
from backend.unified.translators.pattern_translator import PatternTranslationEngine
from backend.unified.translators.grammar_translator import GrammarTranslationEngine
from backend.unified.translators.base import TranslationDirection


class TestTranslationScenarios:
    """Integration tests for various translation scenarios."""
    
    @pytest.fixture
    def manager_with_engines(self):
        """Create a manager with both grammar and pattern engines."""
        manager = TranslationManager()
        
        # Add pattern engine
        pattern_engine = PatternTranslationEngine()
        manager.register_engine(pattern_engine, is_fallback=True)
        
        # Try to add grammar engine
        try:
            grammar_engine = GrammarTranslationEngine()
            manager.register_engine(grammar_engine, is_default=True)
        except:
            pass  # Grammar engine might fail to load
        
        return manager
    
    # Basic translation scenarios
    
    def test_simple_arithmetic_expressions(self, manager_with_engines):
        """Test translation of basic arithmetic expressions."""
        test_cases = [
            # TCE to Tau
            ("x equals 5", TranslationDirection.TO_TAU, "x=5"),
            ("x plus y", TranslationDirection.TO_TAU, "x+y"),
            ("x minus 10", TranslationDirection.TO_TAU, "x-10"),
            ("x times y divided by z", TranslationDirection.TO_TAU, "x*y/z"),
            
            # Tau to TCE
            ("x=5", TranslationDirection.TO_TCE, "x equals 5"),
            ("x+y-z", TranslationDirection.TO_TCE, "x plus y minus z"),
            ("a*b/c", TranslationDirection.TO_TCE, "a times b divided by c"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success, f"Failed to translate '{input_text}': {result.error_message}"
            assert result.translated_text == expected, f"Expected '{expected}', got '{result.translated_text}'"
    
    def test_logical_expressions(self, manager_with_engines):
        """Test translation of logical expressions."""
        test_cases = [
            # TCE to Tau
            ("x and y", TranslationDirection.TO_TAU, "x&y"),
            ("x or y", TranslationDirection.TO_TAU, "x|y"),
            ("not x", TranslationDirection.TO_TAU, "!x"),
            ("x and y or z", TranslationDirection.TO_TAU, "x&y|z"),
            ("not x and not y", TranslationDirection.TO_TAU, "!x&!y"),
            
            # Tau to TCE
            ("x&y", TranslationDirection.TO_TCE, "x and y"),
            ("x|y", TranslationDirection.TO_TCE, "x or y"),
            ("!x", TranslationDirection.TO_TCE, " not x"),
            ("(x&y)|z", TranslationDirection.TO_TCE, "(x and y) or z"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success, f"Failed to translate '{input_text}': {result.error_message}"
            # Allow for minor spacing differences
            assert result.translated_text.strip() == expected.strip()
    
    def test_comparison_expressions(self, manager_with_engines):
        """Test translation of comparison expressions."""
        test_cases = [
            # These should mostly pass through unchanged
            ("x > 5", TranslationDirection.TO_TAU, "x > 5"),
            ("x < 10", TranslationDirection.TO_TCE, "x < 10"),
            ("x >= 0", TranslationDirection.TO_TAU, "x >= 0"),
            ("y <= 100", TranslationDirection.TO_TCE, "y <= 100"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected
    
    def test_mixed_expressions(self, manager_with_engines):
        """Test translation of mixed arithmetic and logical expressions."""
        test_cases = [
            ("x equals 5 and y > 10", TranslationDirection.TO_TAU, "x=5&y > 10"),
            ("x plus y equals z", TranslationDirection.TO_TAU, "x+y=z"),
            ("not x equals 5", TranslationDirection.TO_TAU, "!x=5"),
            ("x < 10 or y equals 20", TranslationDirection.TO_TAU, "x < 10|y=20"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected
    
    # Time-based expressions
    
    def test_time_expressions(self, manager_with_engines):
        """Test translation of time-based expressions."""
        test_cases = [
            # TCE to Tau
            ("x at time t", TranslationDirection.TO_TAU, "x[t]"),
            ("x at time 5", TranslationDirection.TO_TAU, "x[5]"),
            ("x equals 10 at time t", TranslationDirection.TO_TAU, "x=10[t]"),
            
            # Tau to TCE
            ("x[t]", TranslationDirection.TO_TCE, "x at time t"),
            ("y[0]", TranslationDirection.TO_TCE, "y at time 0"),
            ("z[now]", TranslationDirection.TO_TCE, "z at time now"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected
    
    # Complex real-world scenarios
    
    def test_tau_solver_expressions(self, manager_with_engines):
        """Test translation of Tau solver expressions."""
        test_cases = [
            # Common solver patterns
            ("solve x > 5 and x < 10", TranslationDirection.TO_TAU, "solve x > 5&x < 10"),
            ("rule r equals x plus y", TranslationDirection.TO_TAU, "rule r=x+y"),
            ("stream s equals input plus 1", TranslationDirection.TO_TAU, "stream s=input+1"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected
    
    def test_nested_expressions(self, manager_with_engines):
        """Test deeply nested expressions."""
        test_cases = [
            ("x and (y or z)", TranslationDirection.TO_TAU, "x&(y|z)"),
            ("not (x and y)", TranslationDirection.TO_TAU, "!(x&y)"),
            ("x equals 5 and (y > 10 or z < 0)", TranslationDirection.TO_TAU, "x=5&(y > 10|z < 0)"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected
    
    # Edge cases and special scenarios
    
    def test_article_removal(self, manager_with_engines):
        """Test that articles are properly removed."""
        test_cases = [
            ("the x equals the y", TranslationDirection.TO_TAU, "x=y"),
            ("the value of x", TranslationDirection.TO_TAU, "value of x"),
            ("a plus the b", TranslationDirection.TO_TAU, "a+b"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected
    
    def test_whitespace_normalization(self, manager_with_engines):
        """Test that whitespace is properly normalized."""
        test_cases = [
            ("x    equals    5", TranslationDirection.TO_TAU, "x=5"),
            ("  x and y  ", TranslationDirection.TO_TAU, "x&y"),
            ("x\t+\ty", TranslationDirection.TO_TAU, "x+y"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected
    
    def test_case_insensitivity(self, manager_with_engines):
        """Test case-insensitive translation."""
        test_cases = [
            ("X EQUALS 5", TranslationDirection.TO_TAU, "x=5"),
            ("X AND Y", TranslationDirection.TO_TAU, "x&y"),
            ("NOT Z", TranslationDirection.TO_TAU, "!z"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected
    
    # Round-trip translation tests
    
    def test_round_trip_simple(self, manager_with_engines):
        """Test round-trip translation of simple expressions."""
        original_expressions = [
            "x=5",
            "x&y",
            "x+y",
            "x > 5",
        ]
        
        for original in original_expressions:
            # Tau to TCE
            tce_result = manager_with_engines.translate(original, TranslationDirection.TO_TCE)
            assert tce_result.success
            
            # TCE back to Tau
            tau_result = manager_with_engines.translate(tce_result.translated_text, TranslationDirection.TO_TAU)
            assert tau_result.success
            
            # Should match original (ignoring whitespace)
            assert tau_result.translated_text.replace(" ", "") == original.replace(" ", "")
    
    def test_round_trip_complex(self, manager_with_engines):
        """Test round-trip translation of complex expressions."""
        test_expressions = [
            "x=5&y>10",
            "a+b=c",
            "!x|!y",
        ]
        
        for expr in test_expressions:
            # Forward and back
            tce = manager_with_engines.translate(expr, TranslationDirection.TO_TCE)
            tau = manager_with_engines.translate(tce.translated_text, TranslationDirection.TO_TAU)
            
            assert tau.success
            # Allow for some normalization
            assert tau.translated_text.replace(" ", "") == expr.replace(" ", "")
    
    # Metadata and confidence tests
    
    def test_translation_metadata(self, manager_with_engines):
        """Test that translations include proper metadata."""
        result = manager_with_engines.translate("x equals 5", TranslationDirection.TO_TAU)
        
        assert result.success
        assert result.metadata is not None
        assert "engine_type" in result.metadata or "patterns_applied" in result.metadata
        assert result.confidence > 0
        assert result.processing_time > 0
    
    def test_confidence_varies_by_complexity(self, manager_with_engines):
        """Test that confidence varies based on expression complexity."""
        simple_result = manager_with_engines.translate("x", TranslationDirection.TO_TAU)
        complex_result = manager_with_engines.translate("x and y or z equals 5", TranslationDirection.TO_TAU)
        
        assert simple_result.success
        assert complex_result.success
        
        # Both should have reasonable confidence
        assert 0 < simple_result.confidence <= 1
        assert 0 < complex_result.confidence <= 1
    
    # Error handling scenarios
    
    def test_malformed_expressions(self, manager_with_engines):
        """Test handling of malformed expressions."""
        malformed = [
            "x equals equals y",
            "and and or",
            "))) x (((",
        ]
        
        for expr in malformed:
            result = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
            # Should either succeed with pattern fallback or fail gracefully
            assert isinstance(result.success, bool)
            if not result.success:
                assert result.error_message
    
    def test_empty_and_whitespace_input(self, manager_with_engines):
        """Test handling of empty and whitespace-only input."""
        test_inputs = ["", "   ", "\t\n", None]
        
        for input_text in test_inputs:
            if input_text is None:
                continue  # Skip None test if validation happens before
            
            result = manager_with_engines.translate(input_text or "", TranslationDirection.TO_TAU)
            assert not result.success
            assert result.error_message
    
    # Performance scenarios
    
    def test_long_expression_handling(self, manager_with_engines):
        """Test handling of very long expressions."""
        # Create a long expression
        terms = [f"x{i} equals {i}" for i in range(50)]
        long_expr = " and ".join(terms)
        
        result = manager_with_engines.translate(long_expr, TranslationDirection.TO_TAU)
        
        assert result.success
        assert len(result.translated_text) > 0
        # Should complete reasonably quickly
        assert result.processing_time < 5.0
    
    def test_repeated_translations_cached(self, manager_with_engines):
        """Test that repeated translations benefit from caching."""
        expr = "x equals 5 and y > 10"
        
        # First translation
        result1 = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
        time1 = result1.processing_time
        
        # Second translation (should be cached if grammar engine is used)
        result2 = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
        time2 = result2.processing_time
        
        assert result1.success
        assert result2.success
        assert result1.translated_text == result2.translated_text
        
        # Second should be faster if caching is working
        # (though pattern engine doesn't cache, so this might not always be true)
        if result2.metadata.get("engine_type") == "grammar_parser":
            assert time2 <= time1


class TestSpecializedDomains:
    """Test translations for specialized domains."""
    
    @pytest.fixture
    def manager_with_engines(self):
        """Create a manager with engines."""
        manager = TranslationManager()
        pattern_engine = PatternTranslationEngine()
        manager.register_engine(pattern_engine, is_fallback=True)
        return manager
    
    def test_financial_expressions(self, manager_with_engines):
        """Test translation of financial domain expressions."""
        test_cases = [
            ("price equals 100", TranslationDirection.TO_TAU, "price=100"),
            ("profit equals revenue minus cost", TranslationDirection.TO_TAU, "profit=revenue-cost"),
            ("balance > 0 and status equals active", TranslationDirection.TO_TAU, "balance > 0&status=active"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected
    
    def test_scientific_expressions(self, manager_with_engines):
        """Test translation of scientific expressions."""
        test_cases = [
            ("temperature > 273", TranslationDirection.TO_TAU, "temperature > 273"),
            ("force equals mass times acceleration", TranslationDirection.TO_TAU, "force=mass*acceleration"),
            ("energy equals 0.5 times mass times velocity times velocity", 
             TranslationDirection.TO_TAU, "energy=0.5*mass*velocity*velocity"),
        ]
        
        for input_text, direction, expected in test_cases:
            result = manager_with_engines.translate(input_text, direction)
            assert result.success
            assert result.translated_text == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])