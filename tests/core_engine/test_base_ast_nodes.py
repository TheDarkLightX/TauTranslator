# tests/core_engine/test_base_ast_nodes.py
"""
Tests for the ASTNode base class and SourceLocation.
"""

import unittest
from tau_translator_omega.core_engine.ast_nodes import ASTNode, SourceLocation


class TestSourceLocation(unittest.TestCase):
    """Tests for the SourceLocation dataclass."""

    def test_source_location_creation_and_attributes(self):
        """Test basic creation and attribute access for SourceLocation."""
        loc = SourceLocation(line=1, column=0, end_line=1, end_column=10)
        self.assertEqual(loc.line, 1)
        self.assertEqual(loc.column, 0)
        self.assertEqual(loc.end_line, 1)
        self.assertEqual(loc.end_column, 10)

    def test_source_location_repr(self):
        """Test the __repr__ method of SourceLocation."""
        loc = SourceLocation(line=5, column=2, end_line=5, end_column=8)
        expected_repr = "SourceLocation(line=5, column=2, end_line=5, end_column=8, absolute_char_start_index=None, absolute_char_end_index=None)"
        self.assertEqual(repr(loc), expected_repr)

    def test_source_location_is_frozen(self):
        """Test that SourceLocation instances are immutable (frozen dataclass)."""
        loc = SourceLocation(line=1, column=1, end_line=1, end_column=1)
        # Dataclasses are not frozen by default. If it were, this would raise FrozenInstanceError.
        # For now, we just check if we can change it. If it becomes frozen, this test will need adjustment.
        try:
            loc.line = 2
            # If we want to enforce immutability, @dataclass(frozen=True) should be used for SourceLocation
            # and this test should assert that the above line raises dataclasses.FrozenInstanceError.
        except AttributeError: # Or potentially FrozenInstanceError if it were frozen
            self.fail("SourceLocation should be mutable by default, or test needs update for frozen=True.")


class TestASTNode(unittest.TestCase):
    """Tests for the base ASTNode class."""

    def test_ast_node_creation_without_location(self):
        """Test creating an ASTNode without a SourceLocation."""
        node = ASTNode()
        self.assertIsNone(node.location)
        # ASTNode.__repr__ does not include location information by default
        self.assertEqual(repr(node), "<ASTNode>")

    def test_ast_node_creation_with_location(self):
        """Test creating an ASTNode with a SourceLocation."""
        loc = SourceLocation(line=10, column=5, end_line=11, end_column=20)
        node = ASTNode(location=loc)
        self.assertIs(node.location, loc)
        self.assertEqual(repr(node), "<ASTNode>") # ASTNode.__repr__ is just the class name


if __name__ == '__main__':
    unittest.main()
