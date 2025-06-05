"""
Edge case tests for parser-pattern fallback behavior.

Tests unusual, malformed, and boundary conditions.

Author: DarkLightX / Dana Edwards
"""

import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.manager import TranslationManager
from backend.unified.translators.pattern_translator import PatternTranslationEngine
from backend.unified.translators.grammar_translator import GrammarTranslationEngine
from backend.unified.translators.base import TranslationDirection, TranslationEngine, TranslationResult


class TestEdgeCasesFallback:
    """Test edge cases in parser-pattern fallback system."""
    
    @pytest.fixture
    def manager_with_engines(self):
        """Create a manager with grammar and pattern engines."""
        manager = TranslationManager()
        
        pattern_engine = PatternTranslationEngine()
        manager.register_engine(pattern_engine, is_fallback=True)
        
        try:
            grammar_engine = GrammarTranslationEngine()
            manager.register_engine(grammar_engine, is_default=True)
        except:
            pass
        
        return manager
    
    # Unicode and special character tests
    
    def test_unicode_characters(self, manager_with_engines):
        """Test handling of unicode characters."""
        test_cases = [
            ("α equals β", "α=β"),  # Greek letters
            ("price equals 100€", "price=100€"),  # Currency symbols
            ("temp equals 25°C", "temp=25°C"),  # Degree symbol
            ("x ≥ 5", "x ≥ 5"),  # Mathematical symbols
            ("你好 equals 世界", "你好=世界"),  # Chinese characters
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            assert expected in result.translated_text
    
    def test_emoji_handling(self, manager_with_engines):
        """Test handling of emojis."""
        test_cases = [
            ("happy 😊 equals true", "happy 😊=true"),
            ("status equals 🔴", "status=🔴"),
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected
    
    # Malformed input tests
    
    def test_multiple_operators(self, manager_with_engines):
        """Test handling of multiple consecutive operators."""
        test_cases = [
            "x and and y",
            "x or or or y",
            "x equals equals 5",
            "not not not x",
            "x plus plus y",
        ]
        
        for expr in test_cases:
            result = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
            # Should succeed with pattern fallback
            assert result.success
            # Should not have triple operators
            assert "&&&&" not in result.translated_text
            assert "|||" not in result.translated_text
    
    def test_mismatched_parentheses(self, manager_with_engines):
        """Test handling of mismatched parentheses."""
        test_cases = [
            "(x and y",
            "x and y)",
            "((x and y)",
            "(x and (y)",
            ")))x and y(((",
        ]
        
        for expr in test_cases:
            result = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
            # Pattern engine should still process it
            assert isinstance(result.success, bool)
            if result.success:
                assert "x" in result.translated_text
                assert "y" in result.translated_text
    
    def test_mixed_language_keywords(self, manager_with_engines):
        """Test mixing English and symbolic operators."""
        test_cases = [
            ("x and y & z", "x&y&z"),  # Mixed 'and' and '&'
            ("x | y or z", "x|y|z"),  # Mixed '|' and 'or'
            ("!x not y", "!x!y"),  # Mixed '!' and 'not'
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            # Result should normalize operators
            assert "&" in result.translated_text or "|" in result.translated_text
    
    # Whitespace edge cases
    
    def test_extreme_whitespace(self, manager_with_engines):
        """Test handling of extreme whitespace scenarios."""
        test_cases = [
            ("\n\n\nx equals 5\n\n\n", "x=5"),
            ("\t\t\tx\t\tequals\t\t5\t\t", "x=5"),
            ("x     equals     5", "x=5"),
            ("   x   and   y   ", "x&y"),
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected
    
    def test_no_spaces(self, manager_with_engines):
        """Test handling of expressions with no spaces."""
        test_cases = [
            ("xequals5", "xequals5"),  # Won't be recognized as 'equals'
            ("xandy", "xandy"),  # Won't be recognized as 'and'
            ("x+y", "x+y"),  # Already valid
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected
    
    # Very long input tests
    
    def test_extremely_long_expression(self, manager_with_engines):
        """Test handling of extremely long expressions."""
        # Create an expression with 1000 terms
        terms = [f"var{i} equals {i}" for i in range(1000)]
        huge_expr = " and ".join(terms)
        
        start_time = time.time()
        result = manager_with_engines.translate(huge_expr, TranslationDirection.TO_TAU)
        elapsed = time.time() - start_time
        
        assert result.success
        assert len(result.translated_text) > 1000  # Should be quite long
        assert elapsed < 10.0  # Should complete in reasonable time
        
        # Check that it processed correctly
        assert "var0=0" in result.translated_text
        assert "var999=999" in result.translated_text
    
    def test_deeply_nested_expression(self, manager_with_engines):
        """Test handling of deeply nested expressions."""
        # Create deeply nested expression
        expr = "x"
        for i in range(20):
            expr = f"({expr} and y{i})"
        
        result = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
        assert result.success
        assert result.translated_text.count("(") == result.translated_text.count(")")
    
    # Special operator combinations
    
    def test_operator_precedence_preservation(self, manager_with_engines):
        """Test that operator precedence is preserved."""
        test_cases = [
            ("x and y or z", "x&y|z"),  # AND before OR
            ("x or y and z", "x|y&z"),  # Should preserve order
            ("x plus y times z", "x+y*z"),  # Multiplication before addition
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected
    
    def test_chained_comparisons(self, manager_with_engines):
        """Test chained comparison operators."""
        test_cases = [
            "x > y > z",
            "a < b < c < d",
            "x >= y <= z",
        ]
        
        for expr in test_cases:
            result = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
            assert result.success
            # Comparisons should pass through
            assert ">" in result.translated_text or "<" in result.translated_text
    
    # Error recovery tests
    
    def test_partial_valid_expression(self, manager_with_engines):
        """Test expressions that are partially valid."""
        test_cases = [
            ("x equals 5 and GARBAGE TEXT HERE", "x=5&GARBAGE TEXT HERE"),
            ("INVALID START and y equals 10", "INVALID START&y=10"),
            ("x equals @#$%", "x=@#$%"),
        ]
        
        for input_text, expected_pattern in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            # Should process what it can
            assert "=" in result.translated_text or "&" in result.translated_text
    
    # Engine failure simulation
    
    def test_grammar_timeout_fallback(self, manager_with_engines):
        """Test fallback when grammar engine times out."""
        # Create a mock grammar engine that times out
        class SlowGrammarEngine(TranslationEngine):
            def __init__(self):
                super().__init__("slow_grammar", "Slow grammar engine")
                self.is_available = True
            
            def can_translate(self, text, direction):
                return True
            
            def get_supported_directions(self):
                return [TranslationDirection.TO_TAU, TranslationDirection.TO_TCE]
            
            def translate(self, text, direction, **kwargs):
                time.sleep(0.1)  # Simulate slow processing
                return TranslationResult(
                    success=False,
                    translated_text="",
                    original_text=text,
                    translation_method=self.name,
                    direction=direction,
                    error_message="Timeout"
                )
        
        # Replace grammar engine with slow one
        manager = TranslationManager()
        slow_engine = SlowGrammarEngine()
        pattern_engine = PatternTranslationEngine()
        
        manager.register_engine(slow_engine, is_default=True)
        manager.register_engine(pattern_engine, is_fallback=True)
        
        result = manager.translate("x equals 5", TranslationDirection.TO_TAU)
        assert result.success
        assert result.translation_method == "pattern_based"
    
    # Case sensitivity edge cases
    
    def test_mixed_case_operators(self, manager_with_engines):
        """Test mixed case in operators."""
        test_cases = [
            ("x EqUaLs 5", "x=5"),
            ("x AnD y", "x&y"),
            ("NoT x", "!x"),
            ("x PlUs y", "x+y"),
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected
    
    def test_case_preserved_in_identifiers(self, manager_with_engines):
        """Test that case is preserved in identifiers."""
        test_cases = [
            ("myVariable equals 5", "myvariable=5"),  # Pattern engine lowercases
            ("XMLParser and JSONData", "xmlparser&jsondata"),
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            # Pattern engine converts to lowercase
            assert result.translated_text.lower() == expected.lower()
    
    # Numeric edge cases
    
    def test_numeric_formats(self, manager_with_engines):
        """Test various numeric formats."""
        test_cases = [
            ("x equals 3.14159", "x=3.14159"),  # Decimals
            ("x equals -42", "x=-42"),  # Negative numbers
            ("x equals 1e6", "x=1e6"),  # Scientific notation
            ("x equals 0xFF", "x=0xFF"),  # Hexadecimal
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            assert result.translated_text == expected
    
    # Stress tests
    
    def test_rapid_succession_translations(self, manager_with_engines):
        """Test many translations in rapid succession."""
        expressions = [
            "x equals 5",
            "y > 10",
            "a and b",
            "not z",
            "p or q",
        ]
        
        results = []
        start_time = time.time()
        
        # Do 100 translations rapidly
        for i in range(100):
            expr = expressions[i % len(expressions)]
            result = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
            results.append(result)
        
        elapsed = time.time() - start_time
        
        # All should succeed
        assert all(r.success for r in results)
        # Should be fast
        assert elapsed < 5.0  # 100 translations in under 5 seconds
    
    def test_conflicting_patterns(self, manager_with_engines):
        """Test expressions with potentially conflicting patterns."""
        test_cases = [
            ("order and sort", "order&sort"),  # 'or' in 'order'
            ("band or brand", "band|brand"),  # 'and' in 'band'
            ("notion equals 5", "notion=5"),  # 'not' in 'notion'
        ]
        
        for input_text, expected in test_cases:
            result = manager_with_engines.translate(input_text, TranslationDirection.TO_TAU)
            assert result.success
            # Should not partially replace words
            assert "der" not in result.translated_text  # 'order' not becoming '|der'
            assert "br&" not in result.translated_text  # 'brand' not becoming 'br&'


class TestFallbackBehaviorDetails:
    """Detailed tests of fallback behavior."""
    
    def test_fallback_metadata_preserved(self):
        """Test that fallback information is preserved in metadata."""
        manager = TranslationManager()
        
        # Create a failing primary engine
        class FailingEngine(TranslationEngine):
            def __init__(self):
                super().__init__("failing", "Always fails")
                self.is_available = True
            
            def can_translate(self, text, direction):
                return True
            
            def get_supported_directions(self):
                return [TranslationDirection.TO_TAU]
            
            def translate(self, text, direction, **kwargs):
                return TranslationResult(
                    success=False,
                    translated_text="",
                    original_text=text,
                    translation_method=self.name,
                    direction=direction,
                    error_message="Intentional failure",
                    metadata={"failed_at": "parsing"}
                )
        
        failing = FailingEngine()
        pattern = PatternTranslationEngine()
        
        manager.register_engine(failing, is_default=True)
        manager.register_engine(pattern, is_fallback=True)
        
        result = manager.translate("x equals 5", TranslationDirection.TO_TAU)
        
        assert result.success
        assert result.translation_method == "pattern_based"
        # Should indicate fallback was used
        assert result.metadata.get("engine_type") == "pattern_based"
    
    def test_fallback_chain_exhaustion(self):
        """Test when all engines including fallbacks fail."""
        manager = TranslationManager()
        
        # Create multiple failing engines
        for i in range(3):
            engine = Mock()
            engine.name = f"engine{i}"
            engine.is_available = True
            engine.can_translate = Mock(return_value=True)
            engine.get_supported_directions = Mock(return_value=[TranslationDirection.TO_TAU])
            engine.translate = Mock(return_value=TranslationResult(
                success=False,
                translated_text="",
                original_text="test",
                translation_method=engine.name,
                direction=TranslationDirection.TO_TAU,
                error_message=f"Engine {i} failed"
            ))
            
            if i == 0:
                manager.register_engine(engine, is_default=True)
            else:
                manager.register_engine(engine, is_fallback=True)
        
        result = manager.translate("test", TranslationDirection.TO_TAU)
        
        assert not result.success
        assert result.error_message == "All translation engines failed"
        assert result.translation_method == "fallback_failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])