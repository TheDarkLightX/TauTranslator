"""
Test suite for Grammar Integration
==================================

Tests the integration of TGFGrammarLoader with the translation pipeline.

Author: DarkLightX / Dana Edwards
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.tau_translator_omega.lmql_engine.grammar_integrated_translator import (
    GrammarIntegratedTranslator, TranslationMethod, get_integrated_translator
)
from src.tau_translator_omega.core_engine.tgf_grammar_loader import (
    TGFGrammarLoader, LoadedGrammar
)


class TestGrammarIntegration:
    """Test grammar loader integration with translation pipeline."""
    
    @pytest.fixture
    def translator(self):
        """Create translator instance."""
        return GrammarIntegratedTranslator()
    
    def test_translator_initialization(self, translator):
        """Test translator initializes with available strategies."""
        assert translator is not None
        assert translator.grammar_loader is not None
        assert translator.default_method == TranslationMethod.HYBRID
        
        # Pattern-based should always be available
        methods = translator.get_available_methods()
        assert 'pattern' in methods
        assert 'hybrid' in methods
    
    def test_pattern_based_translation(self, translator):
        """Test pattern-based translation works."""
        result = translator.translate(
            "solve x > 5",
            method=TranslationMethod.PATTERN_BASED
        )
        
        assert result['method'] == 'pattern'
        assert result['success'] is True
        assert 'Find a value for x' in result['output']
    
    def test_hybrid_translation(self, translator):
        """Test hybrid translation tries multiple methods."""
        result = translator.translate("sum[t] := i1[t] + i2[t]")
        
        assert result['method'] == 'hybrid'
        assert result['success'] is True
        # Should use pattern-based with recognizers
        assert 'sum' in result['output'].lower()
    
    def test_empty_input_handling(self, translator):
        """Test handling of empty input."""
        result = translator.translate("")
        
        assert result['success'] is False
        assert result['error'] == 'Empty input text'
        assert result['method'] == 'none'
    
    def test_unsupported_translation_direction(self, translator):
        """Test handling of unsupported translation direction."""
        result = translator.translate("test", "french", "german")
        
        assert result['success'] is False
        assert 'Unsupported translation' in result['error']
    
    def test_translation_directions(self, translator):
        """Test correct translation direction detection."""
        # Tau to English
        result = translator.translate("solve x = 5", "tau", "english")
        assert result['success'] is True
        
        # English to Tau (if supported by method)
        result = translator.translate(
            "Find a value for x such that x equals 5",
            "english", "tau"
        )
        # May or may not succeed depending on available methods
        assert 'method' in result
    
    def test_method_availability(self, translator):
        """Test checking method availability."""
        methods = translator.get_available_methods()
        
        assert isinstance(methods, list)
        assert len(methods) >= 2  # At least pattern and hybrid
        
        # All listed methods should be valid
        for method in methods:
            assert method in ['pattern', 'grammar', 'lmql', 'hybrid']
    
    def test_set_default_method(self, translator):
        """Test setting default translation method."""
        # Valid method
        assert translator.set_default_method('pattern') is True
        assert translator.default_method == TranslationMethod.PATTERN_BASED
        
        # Invalid method
        assert translator.set_default_method('invalid') is False
        
        # Hybrid is always valid
        assert translator.set_default_method('hybrid') is True
        assert translator.default_method == TranslationMethod.HYBRID
    
    def test_recognizer_integration(self, translator):
        """Test that recognizers work within the integrated translator."""
        test_cases = [
            # Arithmetic
            ("sum[t] := a[t] + b[t]", "sum at time t equals"),
            # Stream
            ('sbf input = ifile("data.txt")', "input stream"),
            # Logic gate
            ("and_gate[t] := i1[t] & i2[t]", "bitwise and"),
            # Temporal
            ("delayed[t] := input[t-1]", "time steps ago"),
        ]
        
        for tau_expr, expected_phrase in test_cases:
            result = translator.translate(tau_expr)
            assert result['success'] is True
            assert expected_phrase in result['output'].lower()
    
    @patch('src.tau_translator_omega.lmql_engine.grammar_integrated_translator.GrammarDrivenTranslationStrategy')
    def test_grammar_driven_integration(self, mock_grammar_strategy_class, translator):
        """Test integration with grammar-driven strategy."""
        # Mock the grammar strategy
        mock_strategy = Mock()
        mock_strategy.is_available.return_value = True
        mock_strategy.translate.return_value = {
            'success': True,
            'output': 'Grammar-translated output',
            'method': 'grammar',
            'grammar': {'filename': 'test.tgf'}
        }
        mock_grammar_strategy_class.return_value = mock_strategy
        
        # Reinitialize strategies to pick up mock
        translator.reload_strategies()
        
        # Grammar method should be available
        assert 'grammar' in translator.get_available_methods()
        
        # Test translation
        result = translator.translate(
            "solve x > 5",
            method=TranslationMethod.GRAMMAR_DRIVEN
        )
        
        assert result['success'] is True
        assert result['output'] == 'Grammar-translated output'
        assert result['method'] == 'grammar'
    
    def test_global_instance(self):
        """Test global translator instance."""
        translator1 = get_integrated_translator()
        translator2 = get_integrated_translator()
        
        # Should be the same instance
        assert translator1 is translator2
        
        # Should be properly initialized
        assert translator1 is not None
        assert 'pattern' in translator1.get_available_methods()
    
    def test_complex_expressions(self, translator):
        """Test translation of complex expressions."""
        complex_expr = "always (sensor1[t] & sensor2[t] -> alarm[t+1])"
        result = translator.translate(complex_expr)
        
        assert result['success'] is True
        assert 'always' in result['output'].lower()
    
    def test_method_priority_in_hybrid(self, translator):
        """Test that hybrid mode prioritizes methods correctly."""
        # Expression that could be handled by multiple methods
        expr = "solve x > 0"
        result = translator.translate(expr, method=TranslationMethod.HYBRID)
        
        assert result['success'] is True
        assert result['method'] == 'hybrid'
        
        # Should have tried multiple methods
        if 'methods_tried' in result:
            assert len(result['methods_tried']) >= 1
            # Pattern might be included as 'hybrid' or 'lmql' in the list


class TestRealGrammarIntegration:
    """Integration tests with real grammar files."""
    
    def test_with_real_tau_grammar(self):
        """Test with actual tau.tgf if available."""
        grammar_path = Path("grammars/tau.tgf")
        if not grammar_path.exists():
            pytest.skip("tau.tgf not found")
        
        # Create translator with real grammar
        translator = GrammarIntegratedTranslator()
        
        # If grammar loads successfully, grammar method should be available
        if 'grammar' in translator.get_available_methods():
            result = translator.translate(
                "solve x = 5",
                method=TranslationMethod.GRAMMAR_DRIVEN
            )
            # We don't assert success as it depends on grammar content
            assert 'method' in result
            assert result['method'] == 'grammar'