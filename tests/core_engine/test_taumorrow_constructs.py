#!/usr/bin/env python3
"""
TDD Tests for Taumorrow Demo Constructs
=======================================

Test-driven development for implementing Tau constructs found in
taumorrow community demos.

Author: DarkLightX / Dana Edwards
"""

import pytest
from typing import Dict, List, Optional


class TestBinaryArithmeticConstructs:
    """Test binary arithmetic operations from taumorrow demos."""
    
    def test_recognize_binary_adder_functions(self):
        """Test recognition of half/full adder function definitions."""
        test_cases = [
            {
                "tau": "halfAdderSum(a,b) := a + b",
                "expected": {
                    "type": "function_definition",
                    "name": "halfAdderSum",
                    "params": ["a", "b"],
                    "body": "a + b",
                    "operation": "XOR"  # In binary, + is XOR
                }
            },
            {
                "tau": "fullAdderSum(a,b,c) := a + b + c",
                "expected": {
                    "type": "function_definition", 
                    "name": "fullAdderSum",
                    "params": ["a", "b", "c"],
                    "body": "a + b + c",
                    "operation": "triple_XOR"
                }
            },
            {
                "tau": "fullAdderCarry(a,b,c) := (a & b) | (a & c) | (b & c)",
                "expected": {
                    "type": "function_definition",
                    "name": "fullAdderCarry",
                    "params": ["a", "b", "c"],
                    "body": "(a & b) | (a & c) | (b & c)",
                    "operation": "majority"
                }
            }
        ]
        
        from src.tau_translator_omega.core_engine.binary_arithmetic_recognizer import BinaryArithmeticRecognizer
        recognizer = BinaryArithmeticRecognizer()
        
        for test in test_cases:
            result = recognizer.recognize(test["tau"])
            assert result["type"] == test["expected"]["type"]
            assert result["name"] == test["expected"]["name"]
            assert result["params"] == test["expected"]["params"]
            assert result["operation"] == test["expected"]["operation"]
    
    def test_translate_binary_operations(self):
        """Test translation of binary arithmetic to English."""
        test_cases = [
            ("a + b", "a XOR b", "binary context"),
            ("a & b", "a AND b", "any context"),
            ("(a & b) | (a & c) | (b & c)", "majority of a, b, and c", "carry logic")
        ]
        
        from src.tau_translator_omega.core_engine.binary_translator import BinaryTranslator
        translator = BinaryTranslator()
        
        for tau_expr, expected_english, context in test_cases:
            result = translator.to_english(tau_expr, context=context)
            assert expected_english in result


class TestStreamFileOperations:
    """Test stream and file I/O operations."""
    
    def test_recognize_input_file_stream(self):
        """Test recognition of input file stream declarations."""
        tau_code = 'sbf i1 = ifile("input1.in")'
        
        expected = {
            "type": "stream_declaration",
            "stream_type": "sbf",
            "name": "i1",
            "direction": "input",
            "file": "input1.in"
        }
        
        from src.tau_translator_omega.core_engine.stream_recognizer import StreamRecognizer
        recognizer = StreamRecognizer()
        result = recognizer.recognize(tau_code)
        
        assert result == expected
    
    def test_recognize_output_file_stream(self):
        """Test recognition of output file stream declarations."""
        tau_code = 'sbf o1 = ofile("/simple_test/outputs/consensus.out")'
        
        expected = {
            "type": "stream_declaration",
            "stream_type": "sbf",
            "name": "o1", 
            "direction": "output",
            "file": "/simple_test/outputs/consensus.out"
        }
        
        from src.tau_translator_omega.core_engine.stream_recognizer import StreamRecognizer
        recognizer = StreamRecognizer()
        result = recognizer.recognize(tau_code)
        
        assert result == expected
    
    def test_translate_stream_declarations(self):
        """Test translation of stream declarations."""
        test_cases = [
            ('sbf i1 = ifile("data.in")', 'Define input stream i1 that reads from file "data.in"'),
            ('sbf o2 = ofile("result.out")', 'Define output stream o2 that writes to file "result.out"'),
        ]
        
        from src.tau_translator_omega.core_engine.stream_translator import StreamTranslator
        translator = StreamTranslator()
        
        for tau, expected in test_cases:
            result = translator.tau_to_english(tau)
            assert result == expected


class TestLogicGatePatterns:
    """Test logic gate implementations."""
    
    @pytest.mark.parametrize("tau,gate_type,description", [
        ("r o1[t] = i1[t] & i2[t]", "AND", "AND gate"),
        ("r o2[t] = i1[t] | i2[t]", "OR", "OR gate"),
        ("r o3[t] = i1[t]'", "NOT", "NOT gate"),
        ("r o4[t] = (i1[t] & i2[t]') | (i1[t]' & i2[t])", "XOR", "XOR gate"),
    ])
    def test_recognize_logic_gates(self, tau, gate_type, description):
        """Test recognition of standard logic gate patterns."""
        from src.tau_translator_omega.core_engine.logic_gate_recognizer import LogicGateRecognizer
        recognizer = LogicGateRecognizer()
        
        result = recognizer.recognize(tau)
        assert result["gate_type"] == gate_type
        assert result["type"] == "logic_gate_rule"
    
    def test_translate_xor_gate(self):
        """Test XOR gate translation maintains semantic meaning."""
        tau = "r o4[t] = (i1[t] & i2[t]') | (i1[t]' & i2[t])"
        expected_phrases = [
            "o4 at time t",
            "i1 at time t AND complement of i2 at time t",
            "complement of i1 at time t AND i2 at time t",
            "OR"
        ]
        
        from src.tau_translator_omega.core_engine.logic_gate_translator import LogicGateTranslator
        translator = LogicGateTranslator()
        
        result = translator.tau_to_english(tau)
        for phrase in expected_phrases:
            assert phrase in result


class TestDemocracyConsensus:
    """Test democracy and consensus patterns."""
    
    def test_recognize_majority_vote(self):
        """Test recognition of majority vote pattern (2 out of 3)."""
        tau = "r o1[t] = (i1[t] & i2[t]) | (i2[t] & i3[t]) | (i1[t] & i3[t])"
        
        from src.tau_translator_omega.core_engine.consensus_recognizer import ConsensusRecognizer
        recognizer = ConsensusRecognizer()
        
        result = recognizer.recognize(tau)
        assert result["type"] == "majority_vote"
        assert result["inputs"] == ["i1", "i2", "i3"]
        assert result["threshold"] == 2
        assert result["total"] == 3
    
    def test_translate_majority_vote(self):
        """Test translation describes majority voting correctly."""
        tau = "r o1[t] = (i1[t] & i2[t]) | (i2[t] & i3[t]) | (i1[t] & i3[t])"
        
        from src.tau_translator_omega.core_engine.consensus_translator import ConsensusTranslator
        translator = ConsensusTranslator()
        
        result = translator.tau_to_english(tau)
        assert "majority vote" in result.lower()
        assert "at least two of three" in result.lower() or "2 out of 3" in result.lower()
    
    def test_recognize_unanimous_vote(self):
        """Test recognition of unanimous vote pattern."""
        tau = "r o2[t] = (i1[t] & i2[t] & i3[t])"
        
        from src.tau_translator_omega.core_engine.consensus_recognizer import ConsensusRecognizer
        recognizer = ConsensusRecognizer()
        
        result = recognizer.recognize(tau)
        assert result["type"] == "unanimous_vote"
        assert result["inputs"] == ["i1", "i2", "i3"]


class TestTemporalDependencies:
    """Test temporal dependencies and time-shifted operations."""
    
    def test_recognize_previous_time_reference(self):
        """Test recognition of t-1 time references."""
        tau = "i4[t-1]"
        
        expected = {
            "stream": "i4",
            "time": "t-1",
            "offset": -1,
            "description": "i4 at previous time step"
        }
        
        from src.tau_translator_omega.core_engine.temporal_recognizer import TemporalRecognizer
        recognizer = TemporalRecognizer()
        
        result = recognizer.recognize_time_reference(tau)
        assert result == expected
    
    def test_translate_complex_temporal_rule(self):
        """Test translation of rule with current and previous time."""
        tau = "r o3[t] = majority[t] & (consensus[t-1] | harmony[t])"
        
        from src.tau_translator_omega.core_engine.temporal_translator import TemporalTranslator
        translator = TemporalTranslator()
        
        result = translator.tau_to_english(tau)
        assert "at time t" in result
        assert "at time t-1" in result or "at previous time" in result
        assert "consensus" in result
        assert "harmony" in result


class TestRoundTripTranslation:
    """Test round-trip translation for taumorrow demos."""
    
    @pytest.mark.parametrize("original_tau", [
        "halfAdderSum(a,b) := a + b",
        "sbf i1 = ifile(\"input.in\")",
        "r o1[t] = i1[t] & i2[t]",
        "r o3[t] = i1[t]'",
        "r vote[t] = (a[t] & b[t]) | (b[t] & c[t]) | (a[t] & c[t])",
    ])
    def test_tau_english_tau_preserves_semantics(self, original_tau):
        """Test that round-trip translation preserves semantic meaning."""
        from src.tau_translator_omega.core_engine.roundtrip_translator import RoundtripTranslator
        translator = RoundtripTranslator()
        
        # First translation
        english = translator.tau_to_english(original_tau)
        assert english is not None
        
        # Translation back  
        tau_result = translator.english_to_tau(english)
        assert tau_result is not None
        
        # Verify semantic equivalence
        assert translator.are_semantically_equivalent(original_tau, tau_result)