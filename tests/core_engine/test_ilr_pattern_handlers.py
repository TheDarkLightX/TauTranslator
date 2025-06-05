#!/usr/bin/env python3
"""
ILR Pattern Handler Tests
=========================

Tests for the ILR pattern handlers that parse specific natural language patterns.

Author: DarkLightX/Dana Edwards
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.ilr_pattern_handlers import (
    PatternHandler, SBFInputHandler, SBFOutputHandler, StreamRuleHandler,
    TemporalAlwaysHandler, ConditionalHandler, AssignmentHandler,
    BooleanOperationHandler, PatternHandlerRegistry
)


class TestSBFInputHandler(unittest.TestCase):
    """Tests for SBF input pattern handler."""
    
    def setUp(self):
        """Set up test handler."""
        self.handler = SBFInputHandler()
    
    def test_can_handle_valid_pattern(self):
        """Test recognition of valid SBF input patterns."""
        self.assertTrue(self.handler.can_handle("SBF Filter takes input_stream"))
        self.assertTrue(self.handler.can_handle("sbf MyFilter takes data"))
        self.assertTrue(self.handler.can_handle("SBF Process takes x"))
    
    def test_can_handle_invalid_pattern(self):
        """Test rejection of invalid patterns."""
        self.assertFalse(self.handler.can_handle("SBF Filter produces output"))
        self.assertFalse(self.handler.can_handle("Filter takes input"))
        self.assertFalse(self.handler.can_handle("x := 5"))
    
    def test_analyze_pattern(self):
        """Test pattern analysis extracts correct data."""
        data = self.handler.analyze("SBF DataFilter takes sensor_input")
        self.assertEqual(data['sbf_name'], "DataFilter")
        self.assertEqual(data['input_var'], "sensor_input")
    
    def test_generate_ilr(self):
        """Test ILR generation from analyzed data."""
        data = {'sbf_name': 'Filter', 'input_var': 'stream_in'}
        ilr = self.handler.generate_ilr(data)
        
        self.assertEqual(ilr['type'], "SBF_INPUT_DECLARATION")
        self.assertEqual(ilr['sbf_name'], "Filter")
        self.assertEqual(ilr['input_variable'], "stream_in")


class TestSBFOutputHandler(unittest.TestCase):
    """Tests for SBF output pattern handler."""
    
    def setUp(self):
        """Set up test handler."""
        self.handler = SBFOutputHandler()
    
    def test_can_handle_valid_pattern(self):
        """Test recognition of valid SBF output patterns."""
        self.assertTrue(self.handler.can_handle("SBF Filter produces output_stream"))
        self.assertTrue(self.handler.can_handle("sbf Process produces result"))
    
    def test_analyze_and_generate(self):
        """Test full analysis and generation flow."""
        text = "SBF Transformer produces transformed_data"
        self.assertTrue(self.handler.can_handle(text))
        
        data = self.handler.analyze(text)
        self.assertEqual(data['sbf_name'], "Transformer")
        self.assertEqual(data['output_var'], "transformed_data")
        
        ilr = self.handler.generate_ilr(data)
        self.assertEqual(ilr['type'], "SBF_OUTPUT_DECLARATION")


class TestStreamRuleHandler(unittest.TestCase):
    """Tests for stream rule pattern handler."""
    
    def setUp(self):
        """Set up test handler."""
        self.handler = StreamRuleHandler()
    
    def test_can_handle_arrow_operators(self):
        """Test recognition of both arrow operators."""
        self.assertTrue(self.handler.can_handle("stream output <- input + 1"))
        self.assertTrue(self.handler.can_handle("stream data → process(x)"))
    
    def test_analyze_left_arrow(self):
        """Test analysis of left arrow stream rule."""
        data = self.handler.analyze("stream temperature <- sensor_reading * 1.8 + 32")
        
        self.assertEqual(data['stream_name'], "temperature")
        self.assertEqual(data['expression'], "sensor_reading * 1.8 + 32")
        self.assertEqual(data['operator'], "<-")
    
    def test_analyze_right_arrow(self):
        """Test analysis of right arrow stream rule."""
        data = self.handler.analyze("stream events → filter(raw_events)")
        
        self.assertEqual(data['stream_name'], "events")
        self.assertEqual(data['expression'], "filter(raw_events)")
        self.assertEqual(data['operator'], "→")


class TestTemporalAlwaysHandler(unittest.TestCase):
    """Tests for temporal always pattern handler."""
    
    def setUp(self):
        """Set up test handler."""
        self.handler = TemporalAlwaysHandler()
    
    def test_can_handle_always_pattern(self):
        """Test recognition of always patterns."""
        self.assertTrue(self.handler.can_handle("always x > 0"))
        self.assertTrue(self.handler.can_handle("Always temperature < 100"))
        self.assertFalse(self.handler.can_handle("x > 0"))
    
    def test_analyze_always_condition(self):
        """Test extraction of always condition."""
        data = self.handler.analyze("always speed <= max_speed")
        self.assertEqual(data['condition'], "speed <= max_speed")
    
    def test_generate_temporal_ilr(self):
        """Test ILR generation for temporal always."""
        data = {'condition': 'system_active = true'}
        ilr = self.handler.generate_ilr(data)
        
        self.assertEqual(ilr['type'], "TEMPORAL_ALWAYS")
        self.assertEqual(ilr['condition'], "system_active = true")


class TestConditionalHandler(unittest.TestCase):
    """Tests for conditional pattern handler."""
    
    def setUp(self):
        """Set up test handler."""
        self.handler = ConditionalHandler()
    
    def test_can_handle_if_then(self):
        """Test recognition of if-then patterns."""
        self.assertTrue(self.handler.can_handle("if x > 0 then positive"))
        self.assertTrue(self.handler.can_handle("If condition Then action"))
    
    def test_can_handle_if_then_else(self):
        """Test recognition of if-then-else patterns."""
        self.assertTrue(self.handler.can_handle("if x > 0 then pos else neg"))
    
    def test_analyze_simple_conditional(self):
        """Test analysis of simple if-then."""
        data = self.handler.analyze("if temperature > 30 then cooling_on")
        
        self.assertEqual(data['condition'], "temperature > 30")
        self.assertEqual(data['then_branch'], "cooling_on")
        self.assertIsNone(data['else_branch'])
    
    def test_analyze_if_then_else(self):
        """Test analysis of if-then-else."""
        data = self.handler.analyze("if x >= 0 then positive else negative")
        
        self.assertEqual(data['condition'], "x >= 0")
        self.assertEqual(data['then_branch'], "positive")
        self.assertEqual(data['else_branch'], "negative")


class TestAssignmentHandler(unittest.TestCase):
    """Tests for assignment pattern handler."""
    
    def setUp(self):
        """Set up test handler."""
        self.handler = AssignmentHandler()
    
    def test_can_handle_assignment(self):
        """Test recognition of assignment patterns."""
        self.assertTrue(self.handler.can_handle("x := 5"))
        self.assertTrue(self.handler.can_handle("result := calculate(a, b)"))
        self.assertFalse(self.handler.can_handle("f(x) := x + 1"))  # Function def
    
    def test_analyze_simple_assignment(self):
        """Test analysis of simple assignment."""
        data = self.handler.analyze("counter := 0")
        
        self.assertEqual(data['variable'], "counter")
        self.assertEqual(data['value'], "0")
    
    def test_parse_expression_literals(self):
        """Test parsing of literal values."""
        # Boolean
        result = self.handler._parse_expression("true")
        self.assertEqual(result['node_type'], "BOOLEAN_CONSTANT")
        self.assertTrue(result['value'])
        
        # Numeric
        result = self.handler._parse_expression("42")
        self.assertEqual(result['node_type'], "NUMERIC_CONSTANT")
        self.assertEqual(result['value'], 42)
        
        # Float
        result = self.handler._parse_expression("3.14")
        self.assertEqual(result['node_type'], "NUMERIC_CONSTANT")
        self.assertEqual(result['value'], 3.14)
        
        # String
        result = self.handler._parse_expression('"hello"')
        self.assertEqual(result['node_type'], "STRING_CONSTANT")
        self.assertEqual(result['value'], "hello")
    
    def test_parse_expression_variable(self):
        """Test parsing of variable reference."""
        result = self.handler._parse_expression("my_var")
        self.assertEqual(result['node_type'], "VARIABLE_REFERENCE")
        self.assertEqual(result['name'], "my_var")


class TestBooleanOperationHandler(unittest.TestCase):
    """Tests for boolean operation pattern handler."""
    
    def setUp(self):
        """Set up test handler."""
        self.handler = BooleanOperationHandler()
    
    def test_can_handle_boolean_ops(self):
        """Test recognition of boolean operation patterns."""
        self.assertTrue(self.handler.can_handle("x and y"))
        self.assertTrue(self.handler.can_handle("a or b"))
        self.assertTrue(self.handler.can_handle("not condition"))
        self.assertFalse(self.handler.can_handle("x + y"))
    
    def test_analyze_and_operation(self):
        """Test analysis of AND operation."""
        data = self.handler.analyze("active and ready")
        
        self.assertEqual(data['operator'], "AND")
        self.assertEqual(data['left'], "active")
        self.assertEqual(data['right'], "ready")
    
    def test_analyze_or_operation(self):
        """Test analysis of OR operation."""
        data = self.handler.analyze("error or warning")
        
        self.assertEqual(data['operator'], "OR")
        self.assertEqual(data['left'], "error")
        self.assertEqual(data['right'], "warning")
    
    def test_analyze_not_operation(self):
        """Test analysis of NOT operation."""
        data = self.handler.analyze("not enabled")
        
        self.assertEqual(data['operator'], "NOT")
        self.assertEqual(data['operand'], "enabled")
    
    def test_generate_boolean_ilr(self):
        """Test ILR generation for boolean operations."""
        # Binary operation
        data = {'operator': 'AND', 'left': 'a', 'right': 'b'}
        ilr = self.handler.generate_ilr(data)
        self.assertEqual(ilr['type'], "BOOLEAN_OPERATION")
        
        # Unary operation
        data = {'operator': 'NOT', 'operand': 'flag'}
        ilr = self.handler.generate_ilr(data)
        self.assertEqual(ilr['type'], "NEGATION")


class TestPatternHandlerRegistry(unittest.TestCase):
    """Tests for pattern handler registry."""
    
    def setUp(self):
        """Set up test registry."""
        self.registry = PatternHandlerRegistry()
    
    def test_registry_has_default_handlers(self):
        """Test registry initializes with default handlers."""
        self.assertTrue(len(self.registry.handlers) > 0)
    
    def test_find_handler_for_patterns(self):
        """Test finding appropriate handlers for patterns."""
        # SBF input
        handler = self.registry.find_handler("SBF Filter takes input")
        self.assertIsInstance(handler, SBFInputHandler)
        
        # Assignment
        handler = self.registry.find_handler("x := 42")
        self.assertIsInstance(handler, AssignmentHandler)
        
        # Unknown pattern
        handler = self.registry.find_handler("unknown pattern syntax")
        self.assertIsNone(handler)
    
    def test_register_custom_handler(self):
        """Test registering custom handler."""
        class CustomHandler(PatternHandler):
            def can_handle(self, text: str) -> bool:
                return text.startswith("CUSTOM")
            
            def analyze(self, text: str):
                return {"custom": True}
            
            def generate_ilr(self, data):
                return {"type": "CUSTOM"}
        
        custom = CustomHandler()
        self.registry.register_handler(custom)
        
        # Should find custom handler first (priority)
        handler = self.registry.find_handler("CUSTOM command")
        self.assertIsInstance(handler, CustomHandler)


if __name__ == '__main__':
    unittest.main()