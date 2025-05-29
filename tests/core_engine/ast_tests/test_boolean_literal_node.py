import unittest
from dataclasses import FrozenInstanceError
import pytest # For pytest.raises

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import ASTNode, BooleanLiteralNode

class TestBooleanLiteralNode(unittest.TestCase):
    def test_import_boolean_literal_node_eventually_succeeds(self):
        """Ensures BooleanLiteralNode is importable."""
        self.assertIsNotNone(BooleanLiteralNode, "BooleanLiteralNode class should be imported.")

    def test_create_boolean_literal_node_valid(self):
        """Test creating BooleanLiteralNode with valid boolean values."""
        node_true = BooleanLiteralNode(value=True)
        self.assertEqual(node_true.value, True)
        self.assertIsInstance(node_true, ASTNode)
        self.assertIsInstance(node_true, BooleanLiteralNode)

        node_false = BooleanLiteralNode(value=False)
        self.assertEqual(node_false.value, False)
        self.assertIsInstance(node_false, ASTNode)
        self.assertIsInstance(node_false, BooleanLiteralNode)

    def test_boolean_literal_node_immutable(self):
        """Test that BooleanLiteralNode is immutable."""
        node = BooleanLiteralNode(value=True)
        with pytest.raises(FrozenInstanceError):
            node.value = False # type: ignore

    def test_boolean_literal_node_invalid_value_type(self):
        """Test creating BooleanLiteralNode with non-boolean values."""
        invalid_values = ["True", "False", 0, 1, None, "string", 123.45]
        for val in invalid_values:
            with self.subTest(value=val):
                with pytest.raises((ValueError, TypeError), match="BooleanLiteralNode value must be a boolean."):
                    BooleanLiteralNode(value=val) # type: ignore

    def test_boolean_literal_node_equality_and_hash(self):
        """Test equality and hashability of BooleanLiteralNode instances."""
        node_true1 = BooleanLiteralNode(value=True)
        node_true2 = BooleanLiteralNode(value=True)
        node_false1 = BooleanLiteralNode(value=False)
        node_false2 = BooleanLiteralNode(value=False)

        self.assertEqual(node_true1, node_true2)
        self.assertEqual(node_false1, node_false2)
        self.assertNotEqual(node_true1, node_false1)
        self.assertNotEqual(node_true1, True) # Equality with other types

        try:
            node_set = {node_true1, node_true2, node_false1, node_false2}
            self.assertEqual(len(node_set), 2) # Should contain unique nodes for True and False
            self.assertIn(BooleanLiteralNode(value=True), node_set)
            self.assertIn(BooleanLiteralNode(value=False), node_set)
        except TypeError:
            self.fail("BooleanLiteralNode instances are not hashable.")

if __name__ == '__main__':
    unittest.main()
