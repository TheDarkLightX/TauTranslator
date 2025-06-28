# tests/core_engine/test_exception_ast_nodes.py
"""
Tests for exception handling related AST nodes.
"""

import unittest
from typing import List, Optional

from tau_translator_omega.core_engine.ast.ast_nodes import (
    ASTNode, SourceLocation, IdentifierNode, LiteralNode, BlockNode,
    TryCatchClauseNode, RaiseStatementNode, TryStatementNode
)


class TestTryCatchClauseNode(unittest.TestCase):
    """Tests for TryCatchClauseNode."""
    def test_try_catch_clause_full(self):
        """Test TryCatchClauseNode with exception type, alias, and body."""
        loc = SourceLocation(2, 4, 5, 8)
        exc_type1 = IdentifierNode("ValueError")
        exc_type2 = IdentifierNode("TypeError")
        as_name_id = IdentifierNode("e")
        stmt = LiteralNode(1)
        body_block = BlockNode([stmt])
        
        clause = TryCatchClauseNode(
            exception_types=[exc_type1, exc_type2],
            as_name=as_name_id,
            body=body_block,
            location=loc
        )
        self.assertEqual(clause.exception_types, [exc_type1, exc_type2])
        self.assertIs(clause.as_name, as_name_id)
        self.assertIs(clause.body, body_block)
        self.assertIs(clause.location, loc)
        expected_repr = (
            f"<TryCatchClauseNode types={len(clause.exception_types)} "
            f"as_name={clause.as_name is not None} body_stmts={len(clause.body.statements)}>"
        )
        self.assertEqual(repr(clause), expected_repr)

    def test_try_catch_clause_no_alias_no_type(self):
        """Test TryCatchClauseNode with no alias and no specific exception type (catch-all)."""
        body_block = BlockNode([LiteralNode(True)])
        clause = TryCatchClauseNode(exception_types=[], body=body_block)
        self.assertEqual(len(clause.exception_types), 0)
        self.assertIsNone(clause.as_name)
        self.assertIs(clause.body, body_block)
        self.assertIsNone(clause.location)
        expected_repr = (
            f"<TryCatchClauseNode types=0 as_name=False body_stmts={len(clause.body.statements)}>"
        )
        self.assertEqual(repr(clause), expected_repr)


class TestRaiseStatementNode(unittest.TestCase):
    """Tests for RaiseStatementNode."""
    def test_raise_statement(self):
        """Test RaiseStatementNode with an exception expression."""
        loc = SourceLocation(10, 4, 10, 20)
        exc_instance = IdentifierNode("MyExceptionInstance") # Could be InstanceCreationNode in practice
        node = RaiseStatementNode(exception_expr=exc_instance, location=loc)
        self.assertIs(node.exception_expr, exc_instance)
        self.assertIs(node.location, loc)
        expected_repr = (
            f"<RaiseStatementNode expr={repr(exc_instance)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_raise_statement_no_location(self):
        """Test RaiseStatementNode without explicit location (re-raise or bare raise)."""
        exc_expr = None
        node = RaiseStatementNode(exception_expr=exc_expr)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<RaiseStatementNode expr=None>"
        )
        self.assertEqual(repr(node), expected_repr)


class TestTryStatementNode(unittest.TestCase):
    """Tests for TryStatementNode."""
    def setUp(self):
        self.loc = SourceLocation(1, 0, 20, 0)
        self.try_body_stmt = LiteralNode("try_action")
        self.try_block = BlockNode([self.try_body_stmt])
        
        self.catch_exc_type = IdentifierNode("SpecificError")
        self.catch_as_name = IdentifierNode("err")
        self.catch_body_stmt = LiteralNode("handle_error")
        self.catch_block = BlockNode([self.catch_body_stmt])
        self.catch_clause1 = TryCatchClauseNode(
            exception_types=[self.catch_exc_type],
            as_name=self.catch_as_name,
            body=self.catch_block
        )
        self.catch_all_body = BlockNode([LiteralNode("catch_all_action")])
        self.catch_clause2 = TryCatchClauseNode(exception_types=[], body=self.catch_all_body)
        
        self.else_body_stmt = LiteralNode("else_action")
        self.else_block = BlockNode([self.else_body_stmt])
        
        self.finally_body_stmt = LiteralNode("finally_action")
        self.finally_block = BlockNode([self.finally_body_stmt])

    def test_try_catch_finally(self):
        """Test TryStatementNode with try, catch clauses, and finally."""
        node = TryStatementNode(
            try_block=self.try_block,
            catch_clauses=[self.catch_clause1, self.catch_clause2],
            finally_block=self.finally_block,
            location=self.loc
        )
        self.assertIs(node.try_block, self.try_block)
        self.assertEqual(node.catch_clauses, [self.catch_clause1, self.catch_clause2])
        self.assertIsNone(node.else_block)
        self.assertIs(node.finally_block, self.finally_block)
        self.assertIs(node.location, self.loc)
        expected_repr = (
            f"<TryStatementNode try_stmts={len(node.try_block.statements)} "
            f"catches={len(node.catch_clauses)} else=False "
            f"finally={node.finally_block is not None}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_try_catch_else_finally(self):
        """Test TryStatementNode with try, catch, else, and finally."""
        node = TryStatementNode(
            try_block=self.try_block,
            catch_clauses=[self.catch_clause1],
            else_block=self.else_block,
            finally_block=self.finally_block,
            location=self.loc
        )
        self.assertIs(node.try_block, self.try_block)
        self.assertEqual(node.catch_clauses, [self.catch_clause1])
        self.assertIs(node.else_block, self.else_block)
        self.assertIs(node.finally_block, self.finally_block)
        expected_repr = (
            f"<TryStatementNode try_stmts={len(node.try_block.statements)} "
            f"catches={len(node.catch_clauses)} else={node.else_block is not None} "
            f"finally={node.finally_block is not None}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_try_finally_only(self):
        """Test TryStatementNode with only try and finally blocks."""
        node = TryStatementNode(
            try_block=self.try_block,
            finally_block=self.finally_block
        )
        self.assertIs(node.try_block, self.try_block)
        self.assertEqual(len(node.catch_clauses), 0)
        self.assertIsNone(node.else_block)
        self.assertIs(node.finally_block, self.finally_block)
        expected_repr = (
            f"<TryStatementNode try_stmts={len(node.try_block.statements)} "
            f"catches={len(node.catch_clauses)} else=False "
            f"finally={node.finally_block is not None}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_try_catch_only(self):
        """Test TryStatementNode with only try and catch blocks."""
        node = TryStatementNode(
            try_block=self.try_block,
            catch_clauses=[self.catch_clause1]
        )
        self.assertIsNone(node.else_block)
        self.assertIsNone(node.finally_block)
        expected_repr = (
            f"<TryStatementNode try_stmts={len(node.try_block.statements)} "
            f"catches={len(node.catch_clauses)} else=False finally=False>"
        )
        self.assertEqual(repr(node), expected_repr)


if __name__ == '__main__':
    unittest.main()
