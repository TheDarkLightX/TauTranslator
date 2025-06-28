# tests/core_engine/test_statement_ast_nodes.py
"""
Tests for statement-related AST nodes.
"""

import unittest
from typing import List, Tuple, Optional # Required for IfStatementNode test setup

from tau_translator_omega.core_engine.ast.ast_nodes import (
    SourceLocation, IdentifierNode, LiteralNode, BlockNode, 
    VariableDeclarationNode, IfStatementNode, BinaryExpressionNode, ASTNode
)


class TestBlockNode(unittest.TestCase):
    """Tests for the BlockNode class."""

    def test_block_node_creation_empty(self):
        """Test creating an empty BlockNode."""
        loc = SourceLocation(1, 0, 1, 2)
        node = BlockNode(statements=[], location=loc)
        self.assertEqual(len(node.statements), 0)
        self.assertIs(node.location, loc)
        self.assertEqual(repr(node), "<BlockNode statements=0>")

        node_no_loc = BlockNode(statements=[])
        self.assertIsNone(node_no_loc.location)
        self.assertEqual(repr(node_no_loc), "<BlockNode statements=0>")

    def test_block_node_creation_with_statements(self):
        """Test BlockNode with a list of statements."""
        stmt1 = IdentifierNode(name="a")
        stmt2 = LiteralNode(value=1)
        node = BlockNode(statements=[stmt1, stmt2])
        self.assertEqual(len(node.statements), 2)
        self.assertIs(node.statements[0], stmt1)
        self.assertIs(node.statements[1], stmt2)
        self.assertEqual(repr(node), "<BlockNode statements=2>")


class TestVariableDeclarationNode(unittest.TestCase):
    """Tests for the VariableDeclarationNode class."""

    def setUp(self):
        """Set up common test fixtures."""
        self.ident = IdentifierNode(name="my_var")
        self.type_node = IdentifierNode(name="int") # Representing a type as an identifier for simplicity
        self.init_expr = LiteralNode(value=42)
        self.decl_loc = SourceLocation(1,0,1,20)

    def test_variable_declaration_full(self):
        """Test VariableDeclarationNode with identifier, type, and initializer."""
        node = VariableDeclarationNode(
            identifier=self.ident, 
            type_hint=self.type_node, 
            initializer=self.init_expr, 
            location=self.decl_loc
        )
        self.assertIs(node.identifier, self.ident)
        self.assertIs(node.type_hint, self.type_node)
        self.assertIs(node.initializer, self.init_expr)
        self.assertIs(node.location, self.decl_loc)
        expected_repr = (
            f"<VariableDeclarationNode identifier={repr(self.ident)} "
            f"type_hint={repr(self.type_node)} "
            f"initializer={repr(self.init_expr)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_variable_declaration_no_type(self):
        """Test VariableDeclarationNode without a type hint."""
        node = VariableDeclarationNode(identifier=self.ident, initializer=self.init_expr)
        self.assertIsNone(node.type_hint)
        expected_repr = (
            f"<VariableDeclarationNode identifier={repr(self.ident)} "
            f"initializer={repr(self.init_expr)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_variable_declaration_no_initializer(self):
        """Test VariableDeclarationNode without an initializer."""
        node = VariableDeclarationNode(identifier=self.ident, type_hint=self.type_node)
        self.assertIsNone(node.initializer)
        expected_repr = (
            f"<VariableDeclarationNode identifier={repr(self.ident)} "
            f"type_hint={repr(self.type_node)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_variable_declaration_identifier_only(self):
        """Test VariableDeclarationNode with only an identifier (minimal)."""
        node = VariableDeclarationNode(identifier=self.ident)
        self.assertIsNone(node.type_hint)
        self.assertIsNone(node.initializer)
        self.assertIsNone(node.location)
        expected_repr = f"<VariableDeclarationNode identifier={repr(self.ident)}>"
        self.assertEqual(repr(node), expected_repr)


class TestIfStatementNode(unittest.TestCase):
    """Tests for the IfStatementNode class."""

    def setUp(self):
        """Set up common test fixtures for IfStatementNode tests."""
        self.true_cond = LiteralNode(value=True, location=SourceLocation(1,3,1,7))
        self.false_cond = LiteralNode(value=False, location=SourceLocation(3,7,3,12))
        self.then_stmts = [IdentifierNode(name="do_this")]
        self.then_block = BlockNode(statements=self.then_stmts, location=SourceLocation(2,4,2,15))
        self.else_stmts = [IdentifierNode(name="do_that")]
        self.else_block = BlockNode(statements=self.else_stmts, location=SourceLocation(4,4,4,15))
        
        self.elif_cond1 = BinaryExpressionNode(IdentifierNode("a"), ">", LiteralNode(10))
        self.elif_block1_stmts = [IdentifierNode("elif_action1")]
        self.elif_block1 = BlockNode(self.elif_block1_stmts)
        self.elif_cond2 = LiteralNode(value=True) # A simple true condition for another elif
        self.elif_block2_stmts = [IdentifierNode("elif_action2")]
        self.elif_block2 = BlockNode(self.elif_block2_stmts)

        self.if_loc = SourceLocation(1,0,5,0)

    def test_if_statement_basic(self):
        """Test a basic if statement (condition and then_block only)."""
        node = IfStatementNode(condition=self.true_cond, then_block=self.then_block, location=self.if_loc)
        self.assertIs(node.condition, self.true_cond)
        self.assertIs(node.then_block, self.then_block)
        self.assertEqual(len(node.elif_clauses), 0)
        self.assertIsNone(node.else_block)
        self.assertIs(node.location, self.if_loc)
        expected_repr = (
            f"<IfStatementNode condition={repr(self.true_cond)} "
            f"then_block={repr(self.then_block)} "
            f"elifs=0 else=False>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_if_else_statement(self):
        """Test an if-else statement."""
        node = IfStatementNode(
            condition=self.false_cond, 
            then_block=self.then_block, 
            else_block=self.else_block
        )
        self.assertIs(node.else_block, self.else_block)
        self.assertEqual(len(node.elif_clauses), 0)
        expected_repr = (
            f"<IfStatementNode condition={repr(self.false_cond)} "
            f"then_block={repr(self.then_block)} "
            f"elifs=0 else=True>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_if_elif_statement(self):
        """Test an if-elif statement."""
        elif_clauses: List[Tuple[ASTNode, BlockNode]] = [(self.elif_cond1, self.elif_block1)]
        node = IfStatementNode(
            condition=self.false_cond, 
            then_block=self.then_block, 
            elif_clauses=elif_clauses
        )
        self.assertEqual(len(node.elif_clauses), 1)
        self.assertIs(node.elif_clauses[0][0], self.elif_cond1)
        self.assertIs(node.elif_clauses[0][1], self.elif_block1)
        self.assertIsNone(node.else_block)
        expected_repr = (
            f"<IfStatementNode condition={repr(self.false_cond)} "
            f"then_block={repr(self.then_block)} "
            f"elifs=1 else=False>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_if_elif_else_statement(self):
        """Test an if-elif-else statement with multiple elifs."""
        elif_clauses: List[Tuple[ASTNode, BlockNode]] = [
            (self.elif_cond1, self.elif_block1),
            (self.elif_cond2, self.elif_block2)
        ]
        node = IfStatementNode(
            condition=self.true_cond, 
            then_block=self.then_block, 
            elif_clauses=elif_clauses,
            else_block=self.else_block
        )
        self.assertEqual(len(node.elif_clauses), 2)
        self.assertIs(node.else_block, self.else_block)
        expected_repr = (
            f"<IfStatementNode condition={repr(self.true_cond)} "
            f"then_block={repr(self.then_block)} "
            f"elifs=2 else=True>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_if_statement_default_empty_elif(self):
        """Test that elif_clauses defaults to an empty list."""
        node = IfStatementNode(condition=self.true_cond, then_block=self.then_block)
        self.assertIsInstance(node.elif_clauses, list)
        self.assertEqual(len(node.elif_clauses), 0)


if __name__ == '__main__':
    unittest.main()
