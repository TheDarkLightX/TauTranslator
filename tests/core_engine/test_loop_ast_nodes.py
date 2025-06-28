# tests/core_engine/test_loop_ast_nodes.py
"""
Tests for loop-related AST nodes.
"""

import unittest
from tau_translator_omega.core_engine.ast.ast_nodes import (
    ASTNode, SourceLocation, IdentifierNode, LiteralNode, BlockNode, 
    WhileLoopNode, ForLoopNode, BinaryExpressionNode # BinaryExpression for While condition
)


class TestWhileLoopNode(unittest.TestCase):
    """Tests for the WhileLoopNode class."""

    def test_while_loop_creation(self):
        """Test creating a WhileLoopNode."""
        loc = SourceLocation(1,0,3,5)
        condition = BinaryExpressionNode(
            IdentifierNode(name="i"), "<", LiteralNode(value=10)
        )
        body_stmts = [IdentifierNode(name="do_something")]
        body_block = BlockNode(statements=body_stmts, location=SourceLocation(2,4,2,20))

        node = WhileLoopNode(condition=condition, body=body_block, location=loc)
        self.assertIs(node.condition, condition)
        self.assertIs(node.body, body_block)
        self.assertIs(node.location, loc)
        expected_repr = (
            f"<WhileLoopNode condition={repr(condition)} "
            f"body={repr(body_block)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_while_loop_no_location(self):
        """Test WhileLoopNode without explicit location."""
        condition = LiteralNode(value=True)
        body_block = BlockNode(statements=[])
        node = WhileLoopNode(condition=condition, body=body_block)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<WhileLoopNode condition={repr(condition)} "
            f"body={repr(body_block)}>"
        )
        self.assertEqual(repr(node), expected_repr)


class TestForLoopNode(unittest.TestCase):
    """Tests for the ForLoopNode class (for...in style)."""

    def test_for_loop_creation(self):
        """Test creating a ForLoopNode."""
        loc = SourceLocation(1,0,3,9)
        iterator_var = IdentifierNode(name="item", location=SourceLocation(1,4,1,8))
        iterable_expr = IdentifierNode(name="my_list", location=SourceLocation(1,12,1,19))
        body_stmts = [IdentifierNode(name="process_item")]
        body_block = BlockNode(statements=body_stmts, location=SourceLocation(2,4,2,20))

        node = ForLoopNode(
            iterator_variable=iterator_var, 
            iterable=iterable_expr, 
            body=body_block, 
            location=loc
        )
        self.assertIs(node.iterator_variable, iterator_var)
        self.assertIs(node.iterable, iterable_expr)
        self.assertIs(node.body, body_block)
        self.assertIs(node.location, loc)
        expected_repr = (
            f"<ForLoopNode iterator_variable={repr(iterator_var)} "
            f"iterable={repr(iterable_expr)} "
            f"body={repr(body_block)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_for_loop_no_location(self):
        """Test ForLoopNode without explicit location."""
        iterator_var = IdentifierNode(name="x")
        iterable_expr = IdentifierNode(name="items")
        body_block = BlockNode(statements=[])
        node = ForLoopNode(iterator_variable=iterator_var, iterable=iterable_expr, body=body_block)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<ForLoopNode iterator_variable={repr(iterator_var)} "
            f"iterable={repr(iterable_expr)} "
            f"body={repr(body_block)}>"
        )
        self.assertEqual(repr(node), expected_repr)


if __name__ == '__main__':
    unittest.main()
