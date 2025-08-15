"""
Test suite for LogicGateRecognizer
==================================

Tests logic gate pattern recognition and translation capabilities.

Author: DarkLightX / Dana Edwards
"""

import pytest
from tau_translator_omega.lmql_engine.recognizers import (
    LogicGateRecognizer, RecognitionResult, RecognizerFactory
)


class TestLogicGateRecognizer:
    """Test logic gate pattern recognition."""
    
    @pytest.fixture
    def recognizer(self):
        """Create recognizer instance."""
        return LogicGateRecognizer()
    
    def test_recognizer_factory_creation(self):
        """Test creating recognizer via factory."""
        recognizer = RecognizerFactory.create_recognizer('logic_gate')
        assert isinstance(recognizer, LogicGateRecognizer)
    
    def test_and_gate_recognition(self, recognizer):
        """Test recognizing AND gate pattern."""
        tau_text = "and_output[t] := input1[t] & input2[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'and_gate'
        assert result.components['output'] == 'and_output'
        assert result.components['output_time'] == 't'
        assert result.components['input1'] == 'input1'
        assert result.components['input2'] == 'input2'
        assert result.confidence > 0.9
    
    def test_or_gate_recognition(self, recognizer):
        """Test recognizing OR gate pattern."""
        tau_text = "or_result[n] := a[n] | b[n]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'or_gate'
        assert result.components['output'] == 'or_result'
        assert result.components['input1'] == 'a'
        assert result.components['input2'] == 'b'
    
    def test_not_gate_recognition(self, recognizer):
        """Test recognizing NOT gate pattern."""
        tau_text = "inverted[t] := signal[t]'"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'not_gate'
        assert result.components['output'] == 'inverted'
        assert result.components['input'] == 'signal'
        assert result.components['input_time'] == 't'
    
    def test_xor_gate_recognition(self, recognizer):
        """Test recognizing XOR gate pattern."""
        tau_text = "xor_out[t] := in1[t] + in2[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'xor_gate'
        assert result.components['output'] == 'xor_out'
    
    def test_nand_gate_recognition(self, recognizer):
        """Test recognizing NAND gate pattern."""
        tau_text = "nand_out[t] := (a[t] & b[t])'"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'nand_gate'
        assert result.components['output'] == 'nand_out'
        assert result.components['input1'] == 'a'
        assert result.components['input2'] == 'b'
    
    def test_nor_gate_recognition(self, recognizer):
        """Test recognizing NOR gate pattern."""
        tau_text = "nor_out[t] := (x[t] | y[t])'"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'nor_gate'
        assert result.components['output'] == 'nor_out'
        assert result.components['input1'] == 'x'
        assert result.components['input2'] == 'y'
    
    def test_and_gate_to_tce_translation(self, recognizer):
        """Test translating AND gate to TCE."""
        tau_text = "result[t] := a[t] & b[t]"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The result at time t equals a at time t AND b at time t."
        assert tce_output == expected
    
    def test_or_gate_to_tce_translation(self, recognizer):
        """Test translating OR gate to TCE."""
        tau_text = "output[n] := x[n] | y[n]"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The output at time n equals x at time n OR y at time n."
        assert tce_output == expected
    
    def test_not_gate_to_tce_translation(self, recognizer):
        """Test translating NOT gate to TCE."""
        tau_text = "inv[t] := input[t]'"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The inv at time t equals NOT input at time t."
        assert tce_output == expected
    
    def test_xor_gate_to_tce_translation(self, recognizer):
        """Test translating XOR gate to TCE."""
        tau_text = "xor_res[t] := p[t] + q[t]"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The xor_res at time t equals p at time t XOR q at time t."
        assert tce_output == expected
    
    def test_nand_gate_to_tce_translation(self, recognizer):
        """Test translating NAND gate to TCE."""
        tau_text = "nand[t] := (in1[t] & in2[t])'"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The nand at time t equals NOT (in1 at time t AND in2 at time t)."
        assert tce_output == expected
    
    def test_nor_gate_to_tce_translation(self, recognizer):
        """Test translating NOR gate to TCE."""
        tau_text = "nor[t] := (a[t] | b[t])'"
        result = recognizer.recognize(tau_text)
        tce_output = recognizer.translate_to_tce(result)
        
        expected = "The nor at time t equals NOT (a at time t OR b at time t)."
        assert tce_output == expected
    
    def test_tce_to_tau_translation(self, recognizer):
        """Test translating back from TCE to Tau."""
        # First recognize a pattern
        tau_text = "gate[t] := a[t] & b[t]"
        result = recognizer.recognize(tau_text)
        
        # Translate to Tau (should match original)
        tau_output = recognizer.translate_to_tau(result)
        assert tau_output == tau_text
    
    def test_non_matching_pattern(self, recognizer):
        """Test behavior with non-matching pattern."""
        tau_text = "not a logic gate pattern"
        result = recognizer.recognize(tau_text)
        
        assert not result.recognized
        assert result.pattern_type == 'unknown'
        assert result.confidence == 0.0
    
    def test_complex_time_expressions(self, recognizer):
        """Test recognition with complex time expressions."""
        tau_text = "delayed_and[t+1] := input1[t-1] & input2[t]"
        result = recognizer.recognize(tau_text)
        
        assert result.recognized
        assert result.pattern_type == 'and_gate'
        assert result.components['output_time'] == 't+1'
        assert result.components['input1_time'] == 't-1'
        assert result.components['input2_time'] == 't'
    
    def test_whitespace_variations(self, recognizer):
        """Test recognition with various whitespace."""
        tau_texts = [
            "out[t]:=a[t]&b[t]",  # No spaces
            "out[t] := a[t]  &  b[t]",  # Extra spaces
            "out[t]\t:=\ta[t]\t&\tb[t]",  # Tabs
        ]
        
        for tau_text in tau_texts:
            result = recognizer.recognize(tau_text)
            assert result.recognized
            assert result.pattern_type == 'and_gate'
    
    def test_all_gate_types(self, recognizer):
        """Test that all gate types are recognized."""
        test_cases = [
            ("out[t] := a[t] & b[t]", 'and_gate'),
            ("out[t] := a[t] | b[t]", 'or_gate'),
            ("out[t] := a[t]'", 'not_gate'),
            ("out[t] := a[t] + b[t]", 'xor_gate'),
            ("out[t] := (a[t] & b[t])'", 'nand_gate'),
            ("out[t] := (a[t] | b[t])'", 'nor_gate'),
        ]
        
        for tau_text, expected_type in test_cases:
            result = recognizer.recognize(tau_text)
            assert result.recognized
            assert result.pattern_type == expected_type