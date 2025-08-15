"""
Test suite for BinaryArithmeticRecognizer
=========================================

Tests arithmetic pattern recognition and translation capabilities.

Author: DarkLightX / Dana Edwards
"""

import pytest
from tau_translator_omega.lmql_engine.recognizers import (
    BinaryArithmeticRecognizer, RecognitionResult, RecognizerFactory
)


class TestBinaryArithmeticRecognizer:
    """Test arithmetic pattern recognition."""
    
    @pytest.fixture
    def recognizer(self):
        """Create recognizer instance."""
        return BinaryArithmeticRecognizer()
    
    def test_recognizer_factory_creation(self):
        """Test creating recognizer via factory."""
        recognizer = RecognizerFactory.create_recognizer('arithmetic')
        assert isinstance(recognizer, BinaryArithmeticRecognizer)
    
    def test_simple_adder_recognition(self, recognizer):
        """Test recognizing simple adder pattern."""
        tau_text = "sum[t] := i1[t] + i2[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'adder'
        assert result.components['output'] == 'sum'
        assert result.components['output_time'] == 't'
        assert result.components['input1'] == 'i1'
        assert result.components['input1_time'] == 't'
        assert result.components['input2'] == 'i2'
        assert result.components['input2_time'] == 't'
        assert result.confidence > 0.9
    
    def test_simple_multiplier_recognition(self, recognizer):
        """Test recognizing simple multiplier pattern."""
        tau_text = "product[n] := a[n] * b[n]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'multiplier'
        assert result.components['output'] == 'product'
        assert result.components['input1'] == 'a'
        assert result.components['input2'] == 'b'
    
    def test_accumulator_recognition(self, recognizer):
        """Test recognizing accumulator pattern."""
        tau_text = "acc[t] := acc[t-1] + input[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'accumulator'
        assert result.components['accumulator'] == 'acc'
        assert result.components['current_time'] == 't'
        assert result.components['prev_time'] == 't-1'
        assert result.components['input'] == 'input'
    
    def test_bitwise_and_recognition(self, recognizer):
        """Test recognizing bitwise AND pattern."""
        tau_text = "result[t] := a[t] & b[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'bitwise_and'
        assert result.components['output'] == 'result'
    
    def test_full_adder_sum_recognition(self, recognizer):
        """Test recognizing full adder sum pattern."""
        tau_text = "sum[t] := a[t] + b[t] + carry_in[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'full_adder_sum'
        assert result.components['input1'] == 'a'
        assert result.components['input2'] == 'b'
    
    def test_adder_to_tce_translation(self, recognizer):
        """Test translating adder pattern to TCE."""
        tau_text = "sum[t] := i1[t] + i2[t]"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The sum at time t equals the sum of i1 at time t and i2 at time t."
        assert tce_output == expected
    
    def test_multiplier_to_tce_translation(self, recognizer):
        """Test translating multiplier pattern to TCE."""
        tau_text = "product[n] := x[n] * y[n]"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The product at time n equals the product of x at time n and y at time n."
        assert tce_output == expected
    
    def test_accumulator_to_tce_translation(self, recognizer):
        """Test translating accumulator pattern to TCE."""
        tau_text = "total[t] := total[t-1] + value[t]"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The total at time t equals the total at time t-1 plus value at time t."
        assert tce_output == expected
    
    def test_tce_to_tau_translation(self, recognizer):
        """Test translating back from TCE to Tau."""
        # First recognize a pattern
        tau_text = "sum[t] := a[t] + b[t]"
        result = recognizer.recognize(tau_text)
        
        # Translate to Tau (should match original)
        tau_output = recognizer.translate_to_tau(result)
        assert tau_output == tau_text
    
    def test_non_matching_pattern(self, recognizer):
        """Test behavior with non-matching pattern."""
        tau_text = "something completely different"
        result = recognizer.recognize(tau_text)
        
        assert not result.recognized
        assert result.pattern_type == 'unknown'
        assert result.confidence == 0.0
    
    def test_complex_time_expressions(self, recognizer):
        """Test recognition with complex time expressions."""
        tau_text = "delayed_sum[t+2] := input1[t-1] + input2[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'adder'
        assert result.components['output_time'] == 't+2'
        assert result.components['input1_time'] == 't-1'
        assert result.components['input2_time'] == 't'
    
    def test_nested_arithmetic(self, recognizer):
        """Test patterns that don't match due to nesting."""
        tau_text = "result[t] := (a[t] + b[t]) * c[t]"
        result = recognizer.recognize(tau_text)
        
        # This shouldn't match simple patterns due to nesting
        assert not result.recognized
    
    def test_all_recognizer_types(self):
        """Test that all recognizer types are available."""
        types = RecognizerFactory.list_recognizer_types()
        assert 'arithmetic' in types
        assert 'stream' in types
        assert 'logic_gate' in types
        assert 'consensus' in types
        assert 'temporal' in types
    
    def test_get_all_recognizers(self):
        """Test getting all recognizers at once."""
        recognizers = RecognizerFactory.get_all_recognizers()
        assert 'arithmetic' in recognizers
        assert isinstance(recognizers['arithmetic'], BinaryArithmeticRecognizer)
    
    def test_invalid_recognizer_type(self):
        """Test factory with invalid recognizer type."""
        with pytest.raises(ValueError, match="Unsupported recognizer type"):
            RecognizerFactory.create_recognizer('invalid_type')