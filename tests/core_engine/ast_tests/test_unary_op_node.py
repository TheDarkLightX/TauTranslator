import unittest
from dataclasses import FrozenInstanceError
import pytest # For pytest.raises
from enum import Enum # Required for UnaryOperatorEnum

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import (
    ASTNode, UnaryOpNode, UnaryOperatorEnum, IdentifierNode, BooleanLiteralNode
)

class TestUnaryOpNode(unittest.TestCase):
    def test_import_unary_op_node_eventually_succeeds(self):
        """Ensures UnaryOpNode and UnaryOperatorEnum are importable."""
        self.assertIsNotNone(UnaryOpNode, "UnaryOpNode class should be imported.")
        self.assertIsNotNone(UnaryOperatorEnum, "UnaryOperatorEnum enum should be imported.")

    def test_create_unary_op_node_valid(self):
        """Test creating UnaryOpNode with valid parameters."""
        operand1 = IdentifierNode("p")
        operand2 = BooleanLiteralNode(True)

        node_logical_not = UnaryOpNode(UnaryOperatorEnum.LOGICAL_NOT, operand1)
        self.assertEqual(node_logical_not.operator, UnaryOperatorEnum.LOGICAL_NOT)
        self.assertEqual(node_logical_not.operand, operand1)
        self.assertIsInstance(node_logical_not, ASTNode)

        node_boolean_neg = UnaryOpNode(UnaryOperatorEnum.BOOLEAN_NEGATION, operand2)
        self.assertEqual(node_boolean_neg.operator, UnaryOperatorEnum.BOOLEAN_NEGATION)
        self.assertEqual(node_boolean_neg.operand, operand2)

        node_always = UnaryOpNode(UnaryOperatorEnum.TEMPORAL_ALWAYS, operand1)
        self.assertEqual(node_always.operator, UnaryOperatorEnum.TEMPORAL_ALWAYS)

        node_sometimes = UnaryOpNode(UnaryOperatorEnum.TEMPORAL_SOMETIMES, operand2)
        self.assertEqual(node_sometimes.operator, UnaryOperatorEnum.TEMPORAL_SOMETIMES)

    def test_unary_op_node_immutable(self):
        """Test that UnaryOpNode is immutable."""
        node = UnaryOpNode(UnaryOperatorEnum.LOGICAL_NOT, IdentifierNode("q"))
        with pytest.raises(FrozenInstanceError):
            node.operator = UnaryOperatorEnum.BOOLEAN_NEGATION # type: ignore
        with pytest.raises(FrozenInstanceError):
            node.operand = IdentifierNode("r") # type: ignore

    def test_unary_op_node_invalid_operator(self):
        """Test creating UnaryOpNode with invalid operator."""
        with pytest.raises((ValueError, TypeError), match="operator must be an instance of UnaryOperatorEnum"):
            UnaryOpNode(operator="NOT", operand=IdentifierNode("p")) # type: ignore

    def test_unary_op_node_invalid_operand(self):
        """Test creating UnaryOpNode with invalid operand."""
        with pytest.raises((ValueError, TypeError), match="operand must be an ASTNode instance"):
            UnaryOpNode(operator=UnaryOperatorEnum.LOGICAL_NOT, operand="p") # type: ignore

    def test_unary_op_node_equality_and_hash(self):
        """Test equality and hashability of UnaryOpNode instances."""
        p = IdentifierNode("p")
        q = IdentifierNode("q")
        true_lit = BooleanLiteralNode(True)

        op1 = UnaryOpNode(UnaryOperatorEnum.LOGICAL_NOT, p)
        op2 = UnaryOpNode(UnaryOperatorEnum.LOGICAL_NOT, p) # Same as op1
        op3 = UnaryOpNode(UnaryOperatorEnum.BOOLEAN_NEGATION, p) # Diff operator
        op4 = UnaryOpNode(UnaryOperatorEnum.LOGICAL_NOT, q) # Diff operand (content)
        op5 = UnaryOpNode(UnaryOperatorEnum.LOGICAL_NOT, true_lit) # Diff operand (type)

        self.assertEqual(op1, op2)
        self.assertNotEqual(op1, op3)
        self.assertNotEqual(op1, op4)
        self.assertNotEqual(op1, op5)

        try:
            node_set = {op1, op2, op3, op4, op5}
            self.assertEqual(len(node_set), 4)
            self.assertIn(op1, node_set)
            self.assertIn(op3, node_set)
            self.assertIn(op4, node_set)
            self.assertIn(op5, node_set)
        except TypeError:
            self.fail("UnaryOpNode instances are not hashable.")

if __name__ == '__main__':
    unittest.main()
