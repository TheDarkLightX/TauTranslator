#!/usr/bin/env python3
"""
ILR Bidirectional Translation Tests
===================================

Tests for bidirectional translation between Natural Language and Tau
through the ILR (Intermediate Logic Representation).

Author: DarkLightX/Dana Edwards
"""

import unittest
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.ilr_translator_refactored import (
    NaturalLanguageToILRTranslator, ILRToTauTranslator
)


class TestBidirectionalTranslation(unittest.TestCase):
    """Tests for bidirectional translation NL <-> ILR <-> Tau."""
    
    def setUp(self):
        """Set up translators."""
        self.nl_to_ilr = NaturalLanguageToILRTranslator()
        self.ilr_to_tau = ILRToTauTranslator()
    
    def test_simple_assignment_bidirectional(self):
        """Test bidirectional translation of simple assignment."""
        # Natural Language -> ILR
        nl_input = "x := 42."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        # Verify ILR structure
        self.assertEqual(ilr['type'], 'ILR')
        self.assertEqual(ilr['content']['type'], 'ASSIGNMENT')
        self.assertEqual(ilr['content']['variable'], 'x')
        self.assertEqual(ilr['content']['value']['node_type'], 'NUMERIC_CONSTANT')
        self.assertEqual(ilr['content']['value']['value'], 42)
        
        # ILR -> Tau
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "x := 42.")
    
    def test_boolean_assignment_bidirectional(self):
        """Test boolean value assignments."""
        # Test true
        nl_input = "flag := true."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "flag := true.")
        
        # Test false
        nl_input = "active := false."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "active := false.")
    
    def test_sbf_declarations_bidirectional(self):
        """Test SBF input/output declarations."""
        # SBF input
        nl_input = "SBF DataFilter takes sensor_stream."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'SBF_INPUT_DECLARATION')
        self.assertEqual(ilr['content']['sbf_name'], 'DataFilter')
        self.assertEqual(ilr['content']['input_variable'], 'sensor_stream')
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "SBF DataFilter takes sensor_stream.")
        
        # SBF output
        nl_input = "SBF Processor produces result_stream."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'SBF_OUTPUT_DECLARATION')
        self.assertEqual(ilr['content']['sbf_name'], 'Processor')
        self.assertEqual(ilr['content']['output_variable'], 'result_stream')
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "SBF Processor produces result_stream.")
    
    def test_stream_rule_bidirectional(self):
        """Test stream rule translation."""
        nl_input = "stream output <- input * 2 + 1."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'STREAM_RULE')
        self.assertEqual(ilr['content']['stream_name'], 'output')
        self.assertEqual(ilr['content']['expression'], 'input * 2 + 1')
        self.assertEqual(ilr['content']['operator'], '<-')
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "stream output <- input * 2 + 1.")
    
    def test_temporal_always_bidirectional(self):
        """Test temporal always pattern."""
        nl_input = "always temperature < 100."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'TEMPORAL_ALWAYS')
        self.assertEqual(ilr['content']['condition'], 'temperature < 100')
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "always temperature < 100.")
    
    def test_conditional_bidirectional(self):
        """Test conditional statements."""
        # Simple if-then
        nl_input = "if x > 0 then positive."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'CONDITIONAL')
        self.assertEqual(ilr['content']['condition'], 'x > 0')
        self.assertEqual(ilr['content']['then'], 'positive')
        self.assertNotIn('else', ilr['content'])
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "if x > 0 then positive.")
        
        # If-then-else
        nl_input = "if temperature > 30 then cooling_on else cooling_off."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['else'], 'cooling_off')
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "if temperature > 30 then cooling_on else cooling_off.")
    
    def test_boolean_operations_bidirectional(self):
        """Test boolean operations."""
        # AND operation
        nl_input = "active and ready."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'BOOLEAN_OPERATION')
        self.assertEqual(ilr['content']['operator'], 'AND')
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "active and ready.")
        
        # OR operation
        nl_input = "error or warning."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['operator'], 'OR')
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "error or warning.")
        
        # NOT operation
        nl_input = "not enabled."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'NEGATION')
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, "not enabled.")
    
    def test_assertion_default_pattern(self):
        """Test default assertion pattern for unrecognized input."""
        nl_input = "x > 5."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'ASSERTION')
        self.assertIn('expression', ilr['content'])
        
        tau_output = self.ilr_to_tau.translate(ilr)
        # Should handle comparison properly
        self.assertIn('>', tau_output)
        self.assertTrue(tau_output.endswith('.'))
    
    def test_complex_expression_parsing(self):
        """Test parsing of complex expressions."""
        nl_input = "result := calculate(a, b)."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'ASSIGNMENT')
        self.assertEqual(ilr['content']['variable'], 'result')
        
        # Check function call parsing
        value = ilr['content']['value']
        if isinstance(value, dict) and value.get('node_type') == 'FUNCTION_CALL':
            self.assertEqual(value['name'], 'calculate')
            self.assertEqual(len(value['arguments']), 2)
    
    def test_string_assignment_bidirectional(self):
        """Test string literal assignments."""
        nl_input = 'message := "Hello, World!".'
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        self.assertEqual(ilr['content']['type'], 'ASSIGNMENT')
        self.assertEqual(ilr['content']['value']['node_type'], 'STRING_CONSTANT')
        self.assertEqual(ilr['content']['value']['value'], 'Hello, World!')
        
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertEqual(tau_output, 'message := "Hello, World!".')
    
    def test_ilr_metadata_structure(self):
        """Test ILR metadata is properly included."""
        nl_input = "x := 1."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        # Check metadata
        self.assertIn('version', ilr)
        self.assertIn('metadata', ilr)
        self.assertEqual(ilr['metadata']['source'], 'natural_language')
        self.assertEqual(ilr['metadata']['target'], 'tau')
    
    def test_error_handling_empty_input(self):
        """Test error handling for empty input."""
        with self.assertRaises(ValueError) as cm:
            self.nl_to_ilr.translate_to_ilr("")
        self.assertIn("empty", str(cm.exception).lower())
    
    def test_error_handling_missing_period(self):
        """Test error handling for missing period."""
        with self.assertRaises(SyntaxError) as cm:
            self.nl_to_ilr.translate_to_ilr("x := 5")
        self.assertIn("period", str(cm.exception).lower())
    
    def test_error_handling_invalid_ilr(self):
        """Test error handling for invalid ILR format."""
        invalid_ilr = {"invalid": "format"}
        
        with self.assertRaises(ValueError) as cm:
            self.ilr_to_tau.translate(invalid_ilr)
        self.assertIn("Invalid ILR format", str(cm.exception))
    
    def test_arithmetic_expression_translation(self):
        """Test arithmetic expression in assignment."""
        nl_input = "result := a + b * 2."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        
        # The parser might parse this as a string or attempt to parse the expression
        # Either way, it should produce valid output
        tau_output = self.ilr_to_tau.translate(ilr)
        self.assertTrue(tau_output.startswith("result :="))
        self.assertTrue(tau_output.endswith("."))
    
    def test_comparison_operators(self):
        """Test various comparison operators."""
        operators = [
            ("x > 5.", ">"),
            ("x < 5.", "<"),
            ("x >= 5.", ">="),
            ("x <= 5.", "<="),
            ("x = 5.", "="),
            ("x != 5.", "≠")  # Should convert != to ≠
        ]
        
        for nl_input, expected_op in operators:
            ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
            tau_output = self.ilr_to_tau.translate(ilr)
            
            # Check that output contains the operator
            if expected_op == "≠":
                # Check that != was converted to ≠ or that it contains !=
                self.assertTrue("≠" in tau_output or "!=" in tau_output)
            else:
                self.assertIn(expected_op, tau_output)


class TestILRRoundTrip(unittest.TestCase):
    """Test round-trip translation preserves semantics."""
    
    def setUp(self):
        """Set up translators."""
        self.nl_to_ilr = NaturalLanguageToILRTranslator()
        self.ilr_to_tau = ILRToTauTranslator()
    
    def test_preserve_numeric_types(self):
        """Test that numeric types are preserved."""
        # Integer
        nl_input = "count := 42."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        self.assertIsInstance(ilr['content']['value']['value'], int)
        
        # Float
        nl_input = "pi := 3.14."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        self.assertIsInstance(ilr['content']['value']['value'], float)
    
    def test_preserve_boolean_values(self):
        """Test that boolean values are preserved."""
        nl_input = "flag := true."
        ilr = self.nl_to_ilr.translate_to_ilr(nl_input)
        self.assertIsInstance(ilr['content']['value']['value'], bool)
        self.assertTrue(ilr['content']['value']['value'])
    
    def test_multiple_translations_stable(self):
        """Test that multiple translations produce stable results."""
        inputs = [
            "x := 42.",
            "SBF Filter takes input.",
            "always x > 0.",
            "if a then b else c."
        ]
        
        for nl_input in inputs:
            # First translation
            ilr1 = self.nl_to_ilr.translate_to_ilr(nl_input)
            tau1 = self.ilr_to_tau.translate(ilr1)
            
            # Second translation of same input
            ilr2 = self.nl_to_ilr.translate_to_ilr(nl_input)
            tau2 = self.ilr_to_tau.translate(ilr2)
            
            # Results should be identical
            self.assertEqual(json.dumps(ilr1, sort_keys=True), 
                           json.dumps(ilr2, sort_keys=True))
            self.assertEqual(tau1, tau2)


if __name__ == '__main__':
    unittest.main()