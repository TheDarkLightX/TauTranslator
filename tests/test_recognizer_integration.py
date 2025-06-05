"""
Test integration of recognizers with translation system
=====================================================

Tests that recognizers are properly integrated into the translation strategies.

Author: DarkLightX / Dana Edwards
"""

import pytest
from src.tau_translator_omega.lmql_engine.translation_strategies import (
    PatternBasedTranslationStrategy, TranslationDirection, TranslationStrategyFactory
)


class TestRecognizerIntegration:
    """Test recognizer integration with translation strategies."""
    
    @pytest.fixture
    def tau_to_tce_strategy(self):
        """Create Tau to TCE translation strategy."""
        return PatternBasedTranslationStrategy(TranslationDirection.TAU_TO_TCE)
    
    @pytest.fixture
    def tce_to_tau_strategy(self):
        """Create TCE to Tau translation strategy."""
        return PatternBasedTranslationStrategy(TranslationDirection.TCE_TO_TAU)
    
    def test_adder_pattern_translation(self, tau_to_tce_strategy):
        """Test translating adder pattern from Tau to TCE."""
        tau_text = "sum[t] := i1[t] + i2[t]"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        assert result.output == "The sum at time t equals the sum of i1 at time t and i2 at time t."
        assert 'adder' in result.patterns_detected
        assert result.confidence > 0.9
    
    def test_multiplier_pattern_translation(self, tau_to_tce_strategy):
        """Test translating multiplier pattern from Tau to TCE."""
        tau_text = "product[n] := x[n] * y[n]"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        assert result.output == "The product at time n equals the product of x at time n and y at time n."
        assert 'multiplier' in result.patterns_detected
    
    def test_accumulator_pattern_translation(self, tau_to_tce_strategy):
        """Test translating accumulator pattern from Tau to TCE."""
        tau_text = "total[t] := total[t-1] + value[t]"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        assert result.output == "The total at time t equals the total at time t-1 plus value at time t."
        assert 'accumulator' in result.patterns_detected
    
    def test_full_adder_pattern_translation(self, tau_to_tce_strategy):
        """Test translating full adder pattern from Tau to TCE."""
        tau_text = "sum[t] := a[t] + b[t] + carry_in[t]"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        assert result.output == "The sum at time t equals a at time t plus b at time t plus carry_in at time t."
        assert 'full_adder_sum' in result.patterns_detected
    
    def test_bitwise_and_pattern_translation(self, tau_to_tce_strategy):
        """Test translating bitwise AND pattern from Tau to TCE."""
        tau_text = "result[t] := a[t] & b[t]"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        assert result.output == "The result at time t equals the bitwise AND of a at time t and b at time t."
        assert 'bitwise_and' in result.patterns_detected
    
    def test_stream_declaration_translation(self, tau_to_tce_strategy):
        """Test translating stream declaration from Tau to TCE."""
        tau_text = 'sbf input_data = ifile("data.txt")'
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        assert result.output == 'Define input stream input_data that reads from file "data.txt".'
        assert 'input_stream' in result.patterns_detected
    
    def test_logic_gate_translation(self, tau_to_tce_strategy):
        """Test translating logic gate pattern from Tau to TCE."""
        tau_text = "and_gate[t] := i1[t] & i2[t]"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        # Should be recognized as bitwise_and by BinaryArithmeticRecognizer
        assert "bitwise AND" in result.output
    
    def test_temporal_delay_translation(self, tau_to_tce_strategy):
        """Test translating temporal delay pattern from Tau to TCE."""
        tau_text = "delayed[t] := input[t-1]"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        assert "delayed at time t equals input from 1 time steps ago" in result.output
        assert 'delay' in result.patterns_detected
    
    def test_fallback_to_general_patterns(self, tau_to_tce_strategy):
        """Test fallback to general patterns when no recognizer matches."""
        tau_text = "solve x = 5"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        assert "Find a value for x such that x equals 5" in result.output
        assert 'solve_command' in result.patterns_detected
    
    def test_complex_expression_with_recognizers(self, tau_to_tce_strategy):
        """Test that complex expressions still work with recognizers."""
        tau_text = "always (sum[t] > 10)"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        assert "Always sum at time t is greater than ten" in result.output
        assert 'always_stmt' in result.patterns_detected
    
    def test_strategy_factory_with_recognizers(self):
        """Test that factory-created strategies have recognizers."""
        strategy = TranslationStrategyFactory.create_pattern_strategy(
            TranslationDirection.TAU_TO_TCE
        )
        
        # Check that recognizers are initialized
        assert hasattr(strategy, 'recognizers')
        assert len(strategy.recognizers) > 0
        assert 'arithmetic' in strategy.recognizers
        assert 'stream' in strategy.recognizers
    
    def test_recognizer_priority_over_general_patterns(self, tau_to_tce_strategy):
        """Test that recognizers have priority over general patterns."""
        # This could match both a general pattern and accumulator
        tau_text = "acc[n] := acc[n-1] + input[n]"
        result = tau_to_tce_strategy.translate(tau_text)
        
        assert result.success
        # Should be recognized by accumulator pattern, not general pattern
        assert 'accumulator' in result.patterns_detected
        assert "equals the acc at time n-1 plus" in result.output