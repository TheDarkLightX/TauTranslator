# tests/core_engine/test_expression_ast_nodes.py
"""
Tests for expression-related AST nodes.
"""

import unittest
from tau_translator_omega.core_engine.ast_nodes import (
    ASTNode, SourceLocation, IdentifierNode, LiteralNode, 
    BinaryExpressionNode, UnaryExpressionNode
)


class TestIdentifierNode(unittest.TestCase):
    """Tests for the IdentifierNode class."""

    def test_identifier_node_creation(self):
        """Test creating an IdentifierNode with and without location."""
        loc = SourceLocation(1, 0, 1, 5)
        node_with_loc = IdentifierNode(name="my_var", location=loc)
        self.assertEqual(node_with_loc.name, "my_var")
        self.assertIs(node_with_loc.location, loc)
        self.assertEqual(repr(node_with_loc), "<IdentifierNode name='my_var'>")

        node_without_loc = IdentifierNode(name="counter")
        self.assertEqual(node_without_loc.name, "counter")
        self.assertIsNone(node_without_loc.location)
        self.assertEqual(repr(node_without_loc), "<IdentifierNode name='counter'>")


class TestLiteralNode(unittest.TestCase):
    """Tests for the LiteralNode class."""

    def test_literal_node_creation_string(self):
        """Test LiteralNode with a string value."""
        loc = SourceLocation(2, 0, 2, 7)
        node = LiteralNode(value="hello", location=loc)
        self.assertEqual(node.value, "hello")
        self.assertIs(node.location, loc)
        self.assertEqual(repr(node), "<LiteralNode value='hello'>")

    def test_literal_node_creation_integer(self):
        """Test LiteralNode with an integer value."""
        loc = SourceLocation(3, 0, 3, 4)
        node_int = LiteralNode(value=123, location=loc)
        self.assertEqual(node_int.value, 123)
        self.assertIs(node_int.location, loc)
        self.assertEqual(repr(node_int), "<LiteralNode value=123>")

    def test_literal_node_creation_boolean(self):
        """Test LiteralNode with a boolean value."""
        node_bool = LiteralNode(value=True)
        self.assertEqual(node_bool.value, True)
        self.assertIsNone(node_bool.location)
        self.assertEqual(repr(node_bool), "<LiteralNode value=True>")


class TestBinaryExpressionNode(unittest.TestCase):
    """Tests for the BinaryExpressionNode class."""

    def setUp(self):
        """Set up common test fixtures."""
        self.left_operand = IdentifierNode(name="a")
        self.right_operand = LiteralNode(value=10)
        self.op_loc = SourceLocation(1,0,1,10)

    def test_binary_expression_node_creation(self):
        """Test creating a BinaryExpressionNode."""
        node = BinaryExpressionNode(
            left=self.left_operand, 
            operator="+", 
            right=self.right_operand, 
            location=self.op_loc
        )
        self.assertIs(node.left, self.left_operand)
        self.assertEqual(node.operator, "+")
        self.assertIs(node.right, self.right_operand)
        self.assertIs(node.location, self.op_loc)
        expected_repr = (
            f"<BinaryExpressionNode "
            f"left={repr(self.left_operand)} "
            f"operator='+' "
            f"right={repr(self.right_operand)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_binary_expression_node_no_location(self):
        """Test BinaryExpressionNode without explicit location."""
        node = BinaryExpressionNode(left=self.left_operand, operator="-", right=self.right_operand)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<BinaryExpressionNode "
            f"left={repr(self.left_operand)} "
            f"operator='-' "
            f"right={repr(self.right_operand)}>"
        )
        self.assertEqual(repr(node), expected_repr)


class TestUnaryExpressionNode(unittest.TestCase):
    """Tests for the UnaryExpressionNode class."""

    def setUp(self):
        """Set up common test fixtures."""
        self.operand = IdentifierNode(name="x")
        self.op_loc = SourceLocation(2,0,2,5)

    def test_unary_expression_node_creation(self):
        """Test creating a UnaryExpressionNode."""
        node = UnaryExpressionNode(operator="-", operand=self.operand, location=self.op_loc)
        self.assertEqual(node.operator, "-")
        self.assertIs(node.operand, self.operand)
        self.assertIs(node.location, self.op_loc)
        expected_repr = (
            f"<UnaryExpressionNode "
            f"operator='-' "
            f"operand={repr(self.operand)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_unary_expression_node_no_location(self):
        """Test UnaryExpressionNode without explicit location."""
        node = UnaryExpressionNode(operator="not", operand=self.operand)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<UnaryExpressionNode "
            f"operator='not' "
            f"operand={repr(self.operand)}>"
        )
        self.assertEqual(repr(node), expected_repr)


if __name__ == '__main__':
    unittest.main()
