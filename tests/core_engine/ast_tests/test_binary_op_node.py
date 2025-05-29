import unittest
from dataclasses import FrozenInstanceError
import pytest # For pytest.raises
from enum import Enum # Required for BinaryOperatorEnum

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import (
    ASTNode, BinaryOpNode, BinaryOperatorEnum, IdentifierNode, NumberLiteralNode
)

class TestBinaryOpNode(unittest.TestCase):
    def test_import_binary_op_node_eventually_succeeds(self):
        """Ensures BinaryOpNode and BinaryOperatorEnum are importable."""
        self.assertIsNotNone(BinaryOpNode, "BinaryOpNode class should be imported.")
        self.assertIsNotNone(BinaryOperatorEnum, "BinaryOperatorEnum enum should be imported.")

    def test_create_binary_op_node_valid(self):
        """Test creating BinaryOpNode with valid parameters."""
        left = IdentifierNode("p")
        right_id = IdentifierNode("q")
        right_num = NumberLiteralNode(10)

        node_and = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, left, right_id)
        self.assertEqual(node_and.operator, BinaryOperatorEnum.LOGICAL_AND)
        self.assertEqual(node_and.left_operand, left)
        self.assertEqual(node_and.right_operand, right_id)
        self.assertIsInstance(node_and, ASTNode)

        node_eq = BinaryOpNode(BinaryOperatorEnum.EQUAL, left, right_num)
        self.assertEqual(node_eq.operator, BinaryOperatorEnum.EQUAL)
        self.assertEqual(node_eq.left_operand, left)
        self.assertEqual(node_eq.right_operand, right_num)

    def test_binary_op_node_immutable(self):
        """Test that BinaryOpNode is immutable."""
        node = BinaryOpNode(BinaryOperatorEnum.LOGICAL_OR, IdentifierNode("a"), IdentifierNode("b"))
        with pytest.raises(FrozenInstanceError):
            node.operator = BinaryOperatorEnum.LOGICAL_AND # type: ignore
        with pytest.raises(FrozenInstanceError):
            node.left_operand = IdentifierNode("c") # type: ignore
        with pytest.raises(FrozenInstanceError):
            node.right_operand = IdentifierNode("d") # type: ignore

    def test_binary_op_node_invalid_operator(self):
        """Test creating BinaryOpNode with invalid operator."""
        with pytest.raises((ValueError, TypeError), match="operator must be an instance of BinaryOperatorEnum"):
            BinaryOpNode(operator="AND", left_operand=IdentifierNode("p"), right_operand=IdentifierNode("q")) # type: ignore

    def test_binary_op_node_invalid_operands(self):
        """Test creating BinaryOpNode with invalid operands."""
        with pytest.raises((ValueError, TypeError), match="left_operand must be an ASTNode instance"):
            BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, "p", IdentifierNode("q")) # type: ignore
        with pytest.raises((ValueError, TypeError), match="right_operand must be an ASTNode instance"):
            BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, IdentifierNode("p"), "q") # type: ignore

    def test_binary_op_node_equality_and_hash(self):
        """Test equality and hashability of BinaryOpNode instances."""
        p = IdentifierNode("p")
        q = IdentifierNode("q")
        r = IdentifierNode("r")
        num10 = NumberLiteralNode(10)

        b1 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, p, q)
        b2 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, p, q) # Same as b1
        b3 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_OR, p, q) # Diff operator
        b4 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, r, q) # Diff left operand
        b5 = BinaryOpNode(BinaryOperatorEnum.LOGICAL_AND, p, r) # Diff right operand
        b6 = BinaryOpNode(BinaryOperatorEnum.EQUAL, p, num10) # Diff operator and right type

        self.assertEqual(b1, b2)
        self.assertNotEqual(b1, b3)
        self.assertNotEqual(b1, b4)
        self.assertNotEqual(b1, b5)
        self.assertNotEqual(b1, b6)

        try:
            node_set = {b1, b2, b3, b4, b5, b6}
            self.assertEqual(len(node_set), 5)
            self.assertIn(b1, node_set)
            self.assertIn(b3, node_set)
            self.assertIn(b4, node_set)
            self.assertIn(b5, node_set)
            self.assertIn(b6, node_set)
        except TypeError:
            self.fail("BinaryOpNode instances are not hashable.")

if __name__ == '__main__':
    unittest.main()
