# tests/core_engine/test_function_ast_nodes.py
"""
Tests for function-related AST nodes.
"""

import unittest
from typing import List, Optional

from tau_translator_omega.core_engine.ast.ast_nodes import (
    ASTNode, SourceLocation, IdentifierNode, LiteralNode, BlockNode, 
    ParameterNode, FunctionDeclarationNode, FunctionCallNode, ReturnStatementNode
)


class TestParameterNode(unittest.TestCase):
    """Tests for the ParameterNode class."""

    def test_parameter_node_creation(self):
        """Test creating a ParameterNode with and without type hint."""
        loc = SourceLocation(1, 0, 1, 10)
        name_ident = IdentifierNode("arg1")
        type_ident = IdentifierNode("int")

        # With type hint and location
        node_with_type = ParameterNode(name=name_ident, type_hint=type_ident, location=loc)
        self.assertEqual(repr(node_with_type.name), repr(name_ident))
        self.assertEqual(repr(node_with_type.type_hint), repr(type_ident))
        self.assertIs(node_with_type.location, loc)
        expected_repr_type = f"<ParameterNode name={repr(name_ident)} type_hint={repr(type_ident)}>"
        self.assertEqual(repr(node_with_type), expected_repr_type)

        # Without type hint, no location
        node_without_type = ParameterNode(name=name_ident)
        self.assertEqual(repr(node_without_type.name), repr(name_ident))
        self.assertIsNone(node_without_type.type_hint)
        self.assertIsNone(node_without_type.location)
        expected_repr_no_type = f"<ParameterNode name={repr(name_ident)}>"
        self.assertEqual(repr(node_without_type), expected_repr_no_type)


class TestFunctionDeclarationNode(unittest.TestCase):
    """Tests for the FunctionDeclarationNode class."""

    def setUp(self):
        self.name_ident = IdentifierNode(name="my_func")
        self.param1 = ParameterNode(IdentifierNode("a"), IdentifierNode("int"))
        self.param2 = ParameterNode(IdentifierNode("b"))
        self.return_type_node = IdentifierNode(name="string")
        self.body_stmt = ReturnStatementNode(LiteralNode("hello"))
        self.body_block = BlockNode(statements=[self.body_stmt])
        self.loc = SourceLocation(1,0,5,1)

    def test_function_declaration_full(self):
        """Test full function declaration."""
        node = FunctionDeclarationNode(
            name=self.name_ident,
            parameters=[self.param1, self.param2],
            return_type=self.return_type_node,
            body=self.body_block,
            location=self.loc
        )
        self.assertIs(node.name, self.name_ident)
        self.assertEqual(node.parameters, [self.param1, self.param2])
        self.assertIs(node.return_type, self.return_type_node)
        self.assertIs(node.body, self.body_block)
        self.assertIs(node.location, self.loc)
        expected_repr = (
            f"<FunctionDeclarationNode name={repr(self.name_ident)} "
            f"params={len([self.param1, self.param2])} return_type={self.return_type_node is not None} "
            f"body_stmts={len(self.body_block.statements)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_function_declaration_minimal(self):
        """Test minimal function declaration (name and body)."""
        node = FunctionDeclarationNode(name=self.name_ident, body=self.body_block)
        self.assertEqual(len(node.parameters), 0)
        self.assertIsNone(node.return_type)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<FunctionDeclarationNode name={repr(self.name_ident)} "
            f"params=0 return_type=False body_stmts={len(self.body_block.statements)}>"
        )
        self.assertEqual(repr(node), expected_repr)


class TestFunctionCallNode(unittest.TestCase):
    """Tests for the FunctionCallNode class."""

    def setUp(self):
        self.callee_ident = IdentifierNode(name="calculate")
        self.arg1 = LiteralNode(value=10)
        self.arg2 = IdentifierNode(name="x")
        self.loc = SourceLocation(10,0,10,15)

    def test_function_call_with_args(self):
        """Test function call with arguments."""
        node = FunctionCallNode(
            callee=self.callee_ident, 
            arguments=[self.arg1, self.arg2],
            location=self.loc
        )
        self.assertIs(node.callee, self.callee_ident)
        self.assertEqual(node.arguments, [self.arg1, self.arg2])
        self.assertIs(node.location, self.loc)
        expected_repr = (
            f"<FunctionCallNode callee={repr(self.callee_ident)} args={len([self.arg1, self.arg2])}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_function_call_no_args(self):
        """Test function call with no arguments."""
        node = FunctionCallNode(callee=self.callee_ident)
        self.assertEqual(len(node.arguments), 0)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<FunctionCallNode callee={repr(self.callee_ident)} args=0>"
        )
        self.assertEqual(repr(node), expected_repr)


class TestReturnStatementNode(unittest.TestCase):
    """Tests for the ReturnStatementNode class."""

    def test_return_statement_with_expression(self):
        """Test return statement with an expression."""
        loc = SourceLocation(5,4,5,15)
        expr = LiteralNode(value=100, location=SourceLocation(5,11,5,14))
        node = ReturnStatementNode(expression=expr, location=loc)
        self.assertIs(node.expression, expr)
        self.assertIs(node.location, loc)
        expected_repr = (
            f"<ReturnStatementNode expression={expr is not None}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_return_statement_no_expression(self):
        """Test return statement without an expression (bare return)."""
        node = ReturnStatementNode(expression=None)
        self.assertIsNone(node.expression)
        self.assertIsNone(node.location)
        expected_repr = f"<ReturnStatementNode expression=False>"
        self.assertEqual(repr(node), expected_repr)


if __name__ == '__main__':
    unittest.main()
