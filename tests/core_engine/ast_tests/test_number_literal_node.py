import unittest
from dataclasses import FrozenInstanceError
import pytest # For pytest.raises

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import ASTNode, NumberLiteralNode

class TestNumberLiteralNode(unittest.TestCase):
    def test_import_number_literal_node_eventually_succeeds(self):
        """Ensures NumberLiteralNode is importable."""
        self.assertIsNotNone(NumberLiteralNode, "NumberLiteralNode class should be imported.")

    def test_create_number_literal_node_valid(self):
        """Test creating NumberLiteralNode with valid integer values."""
        values_to_test = [0, 1, -1, 100, -2345]
        for val in values_to_test:
            with self.subTest(value=val):
                node = NumberLiteralNode(value=val)
                self.assertEqual(node.value, val)
                self.assertIsInstance(node, ASTNode)
                self.assertIsInstance(node, NumberLiteralNode)

    def test_number_literal_node_immutable(self):
        """Test that NumberLiteralNode is immutable."""
        node = NumberLiteralNode(value=42)
        with pytest.raises(FrozenInstanceError):
            node.value = 99 # type: ignore

    def test_number_literal_node_invalid_value_type(self):
        """Test creating NumberLiteralNode with non-integer values."""
        invalid_values = [3.14, "123", "text", None, True, []]
        for val in invalid_values:
            with self.subTest(value=val):
                with pytest.raises((ValueError, TypeError), match="NumberLiteralNode value must be an integer."):
                    NumberLiteralNode(value=val) # type: ignore

    def test_number_literal_node_equality_and_hash(self):
        """Test equality and hashability of NumberLiteralNode instances."""
        node_1a = NumberLiteralNode(value=1)
        node_1b = NumberLiteralNode(value=1)
        node_2a = NumberLiteralNode(value=2)
        node_neg_5 = NumberLiteralNode(value=-5)

        self.assertEqual(node_1a, node_1b)
        self.assertNotEqual(node_1a, node_2a)
        self.assertNotEqual(node_1a, node_neg_5)
        self.assertNotEqual(node_1a, 1) # Equality with other types

        try:
            node_set = {node_1a, node_1b, node_2a, node_neg_5}
            self.assertEqual(len(node_set), 3) 
            self.assertIn(NumberLiteralNode(value=1), node_set)
            self.assertIn(NumberLiteralNode(value=2), node_set)
            self.assertIn(NumberLiteralNode(value=-5), node_set)
        except TypeError:
            self.fail("NumberLiteralNode instances are not hashable.")

if __name__ == '__main__':
    unittest.main()
