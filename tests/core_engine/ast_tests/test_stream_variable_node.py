import unittest
from dataclasses import FrozenInstanceError
import pytest # For pytest.raises
from enum import Enum # Required for StreamTypeEnum if it's defined here or imported directly

# Import specific AST nodes needed for these tests
from tau_translator_omega.core_engine.ast import (
    ASTNode, StreamVariableNode, StreamTypeEnum, IdentifierNode, NumberLiteralNode
)

class TestStreamVariableNode(unittest.TestCase):
    def test_import_stream_variable_node_eventually_succeeds(self):
        """Ensures StreamVariableNode and StreamTypeEnum are importable."""
        self.assertIsNotNone(StreamVariableNode, "StreamVariableNode class should be imported.")
        self.assertIsNotNone(StreamTypeEnum, "StreamTypeEnum enum should be imported.")

    def test_create_stream_variable_node_valid(self):
        """Test creating StreamVariableNode with valid parameters."""
        idx_num = NumberLiteralNode(value=5)
        idx_var = IdentifierNode(name="t")

        node_input_num = StreamVariableNode(
            stream_type=StreamTypeEnum.INPUT,
            stream_id=1,
            index_node=idx_num
        )
        self.assertEqual(node_input_num.stream_type, StreamTypeEnum.INPUT)
        self.assertEqual(node_input_num.stream_id, 1)
        self.assertEqual(node_input_num.index_node, idx_num)
        self.assertIsInstance(node_input_num, ASTNode)

        node_output_var = StreamVariableNode(
            stream_type=StreamTypeEnum.OUTPUT,
            stream_id=2,
            index_node=idx_var
        )
        self.assertEqual(node_output_var.stream_type, StreamTypeEnum.OUTPUT)
        self.assertEqual(node_output_var.stream_id, 2)
        self.assertEqual(node_output_var.index_node, idx_var)

    def test_stream_variable_node_immutable(self):
        """Test that StreamVariableNode is immutable."""
        node = StreamVariableNode(StreamTypeEnum.INPUT, 1, NumberLiteralNode(0))
        with pytest.raises(FrozenInstanceError):
            node.stream_id = 2 # type: ignore
        with pytest.raises(FrozenInstanceError):
            node.stream_type = StreamTypeEnum.OUTPUT # type: ignore
        with pytest.raises(FrozenInstanceError):
            node.index_node = NumberLiteralNode(1) # type: ignore

    def test_stream_variable_node_invalid_stream_type(self):
        """Test creating StreamVariableNode with invalid stream_type."""
        with pytest.raises((ValueError, TypeError), match="stream_type must be an instance of StreamTypeEnum"):
            StreamVariableNode(stream_type="input", stream_id=1, index_node=NumberLiteralNode(0)) # type: ignore

    def test_stream_variable_node_invalid_stream_id(self):
        """Test creating StreamVariableNode with invalid stream_id."""
        with pytest.raises((ValueError, TypeError), match="stream_id must be an integer"):
            StreamVariableNode(StreamTypeEnum.INPUT, "1", NumberLiteralNode(0)) # type: ignore
        # Potentially add test for negative stream_id if disallowed
        # with pytest.raises(ValueError, match="stream_id must be non-negative"):
        #     StreamVariableNode(StreamTypeEnum.INPUT, -1, NumberLiteralNode(0))

    def test_stream_variable_node_invalid_index_node_type(self):
        """Test creating StreamVariableNode with invalid index_node type."""
        with pytest.raises((ValueError, TypeError), match="index_node must be an ASTNode instance"):
            StreamVariableNode(StreamTypeEnum.INPUT, 1, "not_an_ast_node") # type: ignore

    def test_stream_variable_node_equality_and_hash(self):
        """Test equality and hashability of StreamVariableNode instances."""
        idx1 = NumberLiteralNode(1)
        idx2 = NumberLiteralNode(2)
        idx_t = IdentifierNode("t")

        s1 = StreamVariableNode(StreamTypeEnum.INPUT, 1, idx1)
        s2 = StreamVariableNode(StreamTypeEnum.INPUT, 1, idx1) # Same as s1
        s3 = StreamVariableNode(StreamTypeEnum.OUTPUT, 1, idx1) # Diff type
        s4 = StreamVariableNode(StreamTypeEnum.INPUT, 2, idx1) # Diff id
        s5 = StreamVariableNode(StreamTypeEnum.INPUT, 1, idx2) # Diff index content
        s6 = StreamVariableNode(StreamTypeEnum.INPUT, 1, idx_t) # Diff index type

        self.assertEqual(s1, s2)
        self.assertNotEqual(s1, s3)
        self.assertNotEqual(s1, s4)
        self.assertNotEqual(s1, s5)
        self.assertNotEqual(s1, s6)

        try:
            node_set = {s1, s2, s3, s4, s5, s6}
            self.assertEqual(len(node_set), 5)
            self.assertIn(s1, node_set)
            self.assertIn(s3, node_set)
            self.assertIn(s4, node_set)
            self.assertIn(s5, node_set)
            self.assertIn(s6, node_set)
        except TypeError:
            self.fail("StreamVariableNode instances are not hashable.")

if __name__ == '__main__':
    unittest.main()
