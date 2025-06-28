#!/usr/bin/env python3
"""
ILR Node Tests
==============

Tests for the Intermediate Logic Representation (ILR) node types.

Author: DarkLightX/Dana Edwards
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.ilr.ilr_nodes import (
    ILRNode, VariableReference, BooleanConstant, NumericConstant,
    StringConstant, ComparisonExpression, LogicalExpression,
    ArithmeticExpression, FunctionCall, ConditionalExpression,
    FunctionDeclaration, VariableDeclaration, AssignmentStatement
)


class TestILRNode(unittest.TestCase):
    """Tests for base ILRNode class."""
    
    def test_ilr_node_creation(self):
        """Test creating base ILR node."""
        node = ILRNode(node_type="TEST_NODE")
        self.assertEqual(node.node_type, "TEST_NODE")
    
    def test_ilr_node_to_dict(self):
        """Test converting ILR node to dictionary."""
        node = ILRNode(node_type="TEST_NODE")
        result = node.to_dict()
        self.assertEqual(result, {"node_type": "TEST_NODE"})


class TestVariableReference(unittest.TestCase):
    """Tests for VariableReference node."""
    
    def test_variable_reference_simple(self):
        """Test creating simple variable reference."""
        var = VariableReference("x")
        self.assertEqual(var.name, "x")
        self.assertEqual(var.node_type, "VARIABLE_REFERENCE")
        self.assertIsNone(var.temporal_qualifier)
    
    def test_variable_reference_with_temporal_offset(self):
        """Test variable reference with temporal offset."""
        var = VariableReference("stream_var", temporal_offset=-1)
        self.assertEqual(var.name, "stream_var")
        self.assertEqual(var.temporal_qualifier["type"], "TIME_OFFSET")
        self.assertEqual(var.temporal_qualifier["offset"], -1)
    
    def test_variable_reference_to_dict(self):
        """Test converting variable reference to dictionary."""
        var = VariableReference("y", temporal_offset=2)
        result = var.to_dict()
        self.assertEqual(result["node_type"], "VARIABLE_REFERENCE")
        self.assertEqual(result["name"], "y")
        self.assertEqual(result["temporal_qualifier"]["offset"], 2)


class TestConstantNodes(unittest.TestCase):
    """Tests for constant value nodes."""
    
    def test_boolean_constant_true(self):
        """Test boolean constant with true value."""
        bool_const = BooleanConstant(True)
        self.assertEqual(bool_const.value, True)
        self.assertEqual(bool_const.node_type, "BOOLEAN_CONSTANT")
    
    def test_boolean_constant_false(self):
        """Test boolean constant with false value."""
        bool_const = BooleanConstant(False)
        self.assertEqual(bool_const.value, False)
        self.assertEqual(bool_const.node_type, "BOOLEAN_CONSTANT")
    
    def test_numeric_constant_integer(self):
        """Test numeric constant with integer value."""
        num_const = NumericConstant(42)
        self.assertEqual(num_const.value, 42)
        self.assertEqual(num_const.node_type, "NUMERIC_CONSTANT")
    
    def test_numeric_constant_float(self):
        """Test numeric constant with float value."""
        num_const = NumericConstant(3.14)
        self.assertEqual(num_const.value, 3.14)
        self.assertEqual(num_const.node_type, "NUMERIC_CONSTANT")
    
    def test_string_constant(self):
        """Test string constant."""
        str_const = StringConstant("hello world")
        self.assertEqual(str_const.value, "hello world")
        self.assertEqual(str_const.node_type, "STRING_CONSTANT")
    
    def test_string_constant_empty(self):
        """Test string constant with empty string."""
        str_const = StringConstant("")
        self.assertEqual(str_const.value, "")
        self.assertEqual(str_const.node_type, "STRING_CONSTANT")


class TestComparisonExpression(unittest.TestCase):
    """Tests for ComparisonExpression node."""
    
    def test_comparison_expression_creation(self):
        """Test creating comparison expression."""
        left = NumericConstant(5)
        right = NumericConstant(10)
        comp = ComparisonExpression(left, ">", right)
        
        self.assertEqual(comp.node_type, "COMPARISON")
        self.assertEqual(comp.operator, ">")
        self.assertEqual(comp.left.value, 5)
        self.assertEqual(comp.right.value, 10)
    
    def test_comparison_with_variables(self):
        """Test comparison with variable references."""
        left = VariableReference("x")
        right = VariableReference("y")
        comp = ComparisonExpression(left, "==", right)
        
        self.assertEqual(comp.left.name, "x")
        self.assertEqual(comp.right.name, "y")
        self.assertEqual(comp.operator, "==")


class TestLogicalExpression(unittest.TestCase):
    """Tests for LogicalExpression node."""
    
    def test_logical_and_expression(self):
        """Test logical AND expression."""
        operands = [BooleanConstant(True), BooleanConstant(False)]
        logic = LogicalExpression("AND", operands)
        
        self.assertEqual(logic.node_type, "LOGICAL_EXPRESSION")
        self.assertEqual(logic.operator, "AND")
        self.assertEqual(len(logic.operands), 2)
    
    def test_logical_or_expression(self):
        """Test logical OR expression."""
        operands = [
            VariableReference("flag1"),
            VariableReference("flag2"),
            BooleanConstant(True)
        ]
        logic = LogicalExpression("OR", operands)
        
        self.assertEqual(logic.operator, "OR")
        self.assertEqual(len(logic.operands), 3)
    
    def test_logical_not_expression(self):
        """Test logical NOT expression."""
        operands = [VariableReference("condition")]
        logic = LogicalExpression("NOT", operands)
        
        self.assertEqual(logic.operator, "NOT")
        self.assertEqual(len(logic.operands), 1)


class TestArithmeticExpression(unittest.TestCase):
    """Tests for ArithmeticExpression node."""
    
    def test_arithmetic_addition(self):
        """Test arithmetic addition expression."""
        operands = [NumericConstant(5), NumericConstant(3)]
        arith = ArithmeticExpression("+", operands)
        
        self.assertEqual(arith.node_type, "ARITHMETIC_EXPRESSION")
        self.assertEqual(arith.operator, "+")
        self.assertEqual(len(arith.operands), 2)
    
    def test_arithmetic_to_dict(self):
        """Test converting arithmetic expression to dictionary."""
        operands = [
            VariableReference("x"),
            NumericConstant(10)
        ]
        arith = ArithmeticExpression("*", operands)
        result = arith.to_dict()
        
        self.assertEqual(result["node_type"], "ARITHMETIC_EXPRESSION")
        self.assertEqual(result["operator"], "*")
        self.assertEqual(len(result["operands"]), 2)
        self.assertEqual(result["operands"][0]["name"], "x")
        self.assertEqual(result["operands"][1]["value"], 10)


class TestFunctionCall(unittest.TestCase):
    """Tests for FunctionCall node."""
    
    def test_function_call_no_args(self):
        """Test function call with no arguments."""
        func = FunctionCall("get_value", [])
        
        self.assertEqual(func.node_type, "FUNCTION_CALL")
        self.assertEqual(func.name, "get_value")
        self.assertEqual(len(func.arguments), 0)
    
    def test_function_call_with_args(self):
        """Test function call with arguments."""
        args = [
            NumericConstant(42),
            StringConstant("test"),
            VariableReference("x")
        ]
        func = FunctionCall("process", args)
        
        self.assertEqual(func.name, "process")
        self.assertEqual(len(func.arguments), 3)
        self.assertEqual(func.arguments[0].value, 42)


class TestDeclarations(unittest.TestCase):
    """Tests for declaration nodes."""
    
    def test_function_declaration_simple(self):
        """Test simple function declaration."""
        func_decl = FunctionDeclaration("calculate", ["x", "y"])
        
        self.assertEqual(func_decl.name, "calculate")
        self.assertEqual(func_decl.parameters, ["x", "y"])
        self.assertIsNone(func_decl.body)
        self.assertIsNone(func_decl.return_type)
    
    def test_function_declaration_with_body(self):
        """Test function declaration with body."""
        body = ArithmeticExpression("+", [
            VariableReference("x"),
            VariableReference("y")
        ])
        func_decl = FunctionDeclaration("add", ["x", "y"], body=body, return_type="integer")
        
        self.assertEqual(func_decl.return_type, "integer")
        self.assertIsNotNone(func_decl.body)
    
    def test_variable_declaration_simple(self):
        """Test simple variable declaration."""
        var_decl = VariableDeclaration("count")
        
        self.assertEqual(var_decl.name, "count")
        self.assertIsNone(var_decl.var_type)
        self.assertIsNone(var_decl.initial_value)
        self.assertFalse(var_decl.is_stream)
    
    def test_variable_declaration_typed(self):
        """Test typed variable declaration with initial value."""
        initial = NumericConstant(0)
        var_decl = VariableDeclaration("counter", var_type="integer", initial_value=initial)
        
        self.assertEqual(var_decl.var_type, "integer")
        self.assertEqual(var_decl.initial_value.value, 0)
    
    def test_stream_declaration(self):
        """Test stream variable declaration."""
        var_decl = VariableDeclaration("temperature", var_type="real", is_stream=True)
        
        self.assertTrue(var_decl.is_stream)
        self.assertEqual(var_decl.var_type, "real")


class TestAssignmentStatement(unittest.TestCase):
    """Tests for AssignmentStatement."""
    
    def test_assignment_to_constant(self):
        """Test assignment of constant value."""
        value = NumericConstant(42)
        assign = AssignmentStatement("x", value)
        
        self.assertEqual(assign.variable, "x")
        self.assertEqual(assign.value.value, 42)
    
    def test_assignment_to_expression(self):
        """Test assignment of expression."""
        value = ArithmeticExpression("+", [
            VariableReference("y"),
            NumericConstant(1)
        ])
        assign = AssignmentStatement("x", value)
        
        self.assertEqual(assign.variable, "x")
        self.assertEqual(assign.value.operator, "+")
    
    def test_assignment_to_dict(self):
        """Test converting assignment to dictionary."""
        value = BooleanConstant(True)
        assign = AssignmentStatement("flag", value)
        result = assign.to_dict()
        
        self.assertEqual(result["variable"], "flag")
        self.assertEqual(result["value"]["node_type"], "BOOLEAN_CONSTANT")
        self.assertEqual(result["value"]["value"], True)


class TestConditionalExpression(unittest.TestCase):
    """Tests for ConditionalExpression node."""
    
    def test_conditional_if_then(self):
        """Test simple if-then conditional."""
        condition = ComparisonExpression(
            VariableReference("x"),
            ">",
            NumericConstant(0)
        )
        then_branch = StringConstant("positive")
        
        cond = ConditionalExpression(condition, then_branch)
        
        self.assertEqual(cond.node_type, "CONDITIONAL")
        self.assertIsNotNone(cond.condition)
        self.assertIsNotNone(cond.then_branch)
        self.assertIsNone(cond.else_branch)
    
    def test_conditional_if_then_else(self):
        """Test if-then-else conditional."""
        condition = BooleanConstant(True)
        then_branch = NumericConstant(1)
        else_branch = NumericConstant(0)
        
        cond = ConditionalExpression(condition, then_branch, else_branch)
        
        self.assertIsNotNone(cond.else_branch)
        self.assertEqual(cond.else_branch.value, 0)


if __name__ == '__main__':
    unittest.main()