"""
Test suite for TemporalRecognizer
=================================

Tests temporal pattern recognition and translation capabilities.

Author: DarkLightX / Dana Edwards
"""

import pytest
from src.tau_translator_omega.lmql_engine.recognizers import (
    TemporalRecognizer, RecognitionResult, RecognizerFactory
)


class TestTemporalRecognizer:
    """Test temporal pattern recognition."""
    
    @pytest.fixture
    def recognizer(self):
        """Create recognizer instance."""
        return TemporalRecognizer()
    
    def test_recognizer_factory_creation(self):
        """Test creating recognizer via factory."""
        recognizer = RecognizerFactory.create_recognizer('temporal')
        assert isinstance(recognizer, TemporalRecognizer)
    
    def test_delay_pattern_recognition(self, recognizer):
        """Test recognizing delay pattern."""
        tau_text = "delayed[t] := input[t-1]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'delay'
        assert result.components['output'] == 'delayed'
        assert result.components['output_time'] == 't'
        assert result.components['input'] == 'input'
        assert result.components['input_time'] == 't'
        assert result.components['delay_amount'] == '1'
        assert result.confidence > 0.9
    
    def test_advance_pattern_recognition(self, recognizer):
        """Test recognizing advance pattern."""
        tau_text = "future[n] := signal[n+2]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'advance'
        assert result.components['output'] == 'future'
        assert result.components['input'] == 'signal'
        assert result.components['advance_amount'] == '2'
    
    def test_temporal_implication_recognition(self, recognizer):
        """Test recognizing temporal implication pattern."""
        tau_text = "always (trigger[t] -> response[t+3])"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'temporal_implication'
        assert result.components['antecedent'] == 'trigger'
        assert result.components['antecedent_time'] == 't'
        assert result.components['consequent'] == 'response'
        assert result.components['consequent_time'] == 't'
        assert result.components['time_offset'] == '3'
    
    def test_delay_to_tce_translation(self, recognizer):
        """Test translating delay pattern to TCE."""
        tau_text = "output[t] := data[t-2]"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The output at time t equals data from 2 time steps ago."
        assert tce_output == expected
    
    def test_advance_to_tce_translation(self, recognizer):
        """Test translating advance pattern to TCE."""
        tau_text = "preview[t] := stream[t+5]"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The preview at time t equals stream from 5 time steps in the future."
        assert tce_output == expected
    
    def test_temporal_implication_to_tce_translation(self, recognizer):
        """Test translating temporal implication to TCE."""
        tau_text = "always (event[t] -> action[t+1])"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "Always: if event at time t then action at time t plus 1."
        assert tce_output == expected
    
    def test_tce_to_tau_translation(self, recognizer):
        """Test translating back from TCE to Tau."""
        # First recognize a pattern
        tau_text = "delayed[t] := signal[t-3]"
        result = recognizer.recognize(tau_text)
        
        # Translate to Tau (should match original)
        tau_output = recognizer.translate_to_tau(result)
        assert tau_output == tau_text
    
    def test_non_matching_pattern(self, recognizer):
        """Test behavior with non-matching pattern."""
        tau_text = "not a temporal pattern"
        result = recognizer.recognize(tau_text)
        
        assert not result.recognized
        assert result.pattern_type == 'unknown'
        assert result.confidence == 0.0
    
    def test_large_delay_amounts(self, recognizer):
        """Test recognition with large delay amounts."""
        tau_text = "history[t] := data[t-100]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'delay'
        assert result.components['delay_amount'] == '100'
    
    def test_complex_time_expressions_in_delay(self, recognizer):
        """Test delay pattern with complex expressions."""
        tau_text = "result[t+1] := input[t-2]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'delay'
        assert result.components['output_time'] == 't+1'
        assert result.components['delay_amount'] == '2'
    
    def test_whitespace_variations(self, recognizer):
        """Test recognition with various whitespace."""
        # Test cases that should be recognized
        tau_texts_valid = [
            "out[t]:=in[t-1]",  # No spaces
            "out[t]\t:=\tin[t-1]",  # Tabs
            "out[t] := in[t-1]",  # Spaces around :=
        ]
        
        for tau_text in tau_texts_valid:
            result = recognizer.recognize(tau_text)
            assert result.recognized
            assert result.pattern_type == 'delay'
        
        # Test case that won't be recognized due to space in time expression
        tau_text_invalid = "out[t] := in[t - 1]"  # Space around minus
        result = recognizer.recognize(tau_text_invalid)
        assert not result.recognized  # Current pattern doesn't handle spaces in time expr
    
    def test_multiple_digit_offsets(self, recognizer):
        """Test recognition with multi-digit time offsets."""
        test_cases = [
            ("delayed[t] := input[t-10]", 'delay', '10'),
            ("future[t] := input[t+25]", 'advance', '25'),
            ("always (a[t] -> b[t+100])", 'temporal_implication', '100'),
        ]
        
        for tau_text, expected_type, expected_amount in test_cases:
            result = recognizer.recognize(tau_text)
            assert result.recognized
            assert result.pattern_type == expected_type
            if expected_type == 'delay':
                assert result.components['delay_amount'] == expected_amount
            elif expected_type == 'advance':
                assert result.components['advance_amount'] == expected_amount
            elif expected_type == 'temporal_implication':
                assert result.components['time_offset'] == expected_amount