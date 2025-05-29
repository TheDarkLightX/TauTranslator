import unittest
from dataclasses import FrozenInstanceError
import pytest # For pytest.raises

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import ASTNode, IdentifierNode

class TestIdentifierNode(unittest.TestCase):
    def test_import_ast_nodes_eventually_succeeds(self):
        """Ensures IdentifierNode and its base ASTNode are importable."""
        # This test's original purpose was broader. Now it confirms specific imports for this file.
        # The top-level 'from ... import ...' already handles the primary import check.
        self.assertIsNotNone(IdentifierNode, "IdentifierNode class should be imported.")
        self.assertIsNotNone(ASTNode, "ASTNode class should be imported.")

    def test_create_identifier_node_valid(self):
        """Test creating an IdentifierNode with a valid name."""
        node = IdentifierNode(name="my_var")
        self.assertEqual(node.name, "my_var")
        self.assertIsInstance(node, ASTNode)
        self.assertIsInstance(node, IdentifierNode)

    def test_identifier_node_immutable(self):
        """Test that IdentifierNode is immutable."""
        node = IdentifierNode(name="test_immutability")
        with pytest.raises(FrozenInstanceError):
            node.name = "new_name" # type: ignore

    def test_identifier_node_invalid_name_empty(self):
        """Test creating an IdentifierNode with an empty string name."""
        with pytest.raises(ValueError, match="Identifier name must be a non-empty string."):
            IdentifierNode(name="")

    def test_identifier_node_invalid_name_whitespace_only(self):
        """Test creating an IdentifierNode with a name consisting only of whitespace."""
        with pytest.raises(ValueError, match="Identifier name must be a non-empty string."):
            IdentifierNode(name="   ")

    def test_identifier_node_invalid_name_type_integer(self):
        """Test creating an IdentifierNode with a non-string name (integer)."""
        with pytest.raises((ValueError, TypeError), match="Identifier name must be a non-empty string."):
            IdentifierNode(name=123) # type: ignore
    
    def test_identifier_node_invalid_name_type_none(self):
        """Test creating an IdentifierNode with a non-string name (None)."""
        with pytest.raises((ValueError, TypeError), match="Identifier name must be a non-empty string."):
            IdentifierNode(name=None) # type: ignore

    def test_identifier_node_equality_and_hash(self):
        """Test equality and hashability of IdentifierNode instances."""
        node1_var1 = IdentifierNode(name="var1")
        node2_var1 = IdentifierNode(name="var1")
        node3_var2 = IdentifierNode(name="var2")

        self.assertEqual(node1_var1, node2_var1)
        self.assertNotEqual(node1_var1, node3_var2)
        self.assertNotEqual(node1_var1, "var1") # Equality with other types

        try:
            node_set = {node1_var1, node2_var1, node3_var2}
            self.assertEqual(len(node_set), 2)
            self.assertIn(IdentifierNode(name="var1"), node_set)
            self.assertIn(IdentifierNode(name="var2"), node_set)
        except TypeError:
            self.fail("IdentifierNode instances are not hashable.")

if __name__ == '__main__':
    unittest.main()
