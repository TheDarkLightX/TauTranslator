# tests/core_engine/test_class_ast_nodes.py
"""
Tests for class-related AST nodes.
"""

import unittest
from typing import List, Optional

from tau_translator_omega.core_engine.ast_nodes import (
    ASTNode, SourceLocation, IdentifierNode, LiteralNode, BlockNode,
    ParameterNode, FunctionDeclarationNode, # For method body/params
    ClassDeclarationNode, MethodDeclarationNode, AttributeDeclarationNode,
    InstanceCreationNode, MemberAccessNode
)


class TestClassDeclarationNode(unittest.TestCase):
    """Tests for ClassDeclarationNode."""
    def setUp(self):
        self.loc = SourceLocation(1, 0, 10, 1)
        self.name_ident = IdentifierNode("MyClass", location=SourceLocation(1, 6, 1, 12))
        self.base1_ident = IdentifierNode("Base1", location=SourceLocation(1, 20, 1, 25))
        self.base2_ident = IdentifierNode("Base2", location=SourceLocation(1, 27, 1, 32))
        self.method_name = IdentifierNode("my_method")
        self.method_body = BlockNode([LiteralNode(1)]) # Dummy body
        self.method_decl = MethodDeclarationNode(self.method_name, [], None, self.method_body)
        self.attr_name = IdentifierNode("my_attr")
        self.attr_decl = AttributeDeclarationNode(self.attr_name)
        self.body_block = BlockNode(statements=[self.method_decl, self.attr_decl])

    def test_class_declaration_full(self):
        """Test full class declaration with name, base classes, and body."""
        node = ClassDeclarationNode(
            name=self.name_ident,
            base_classes=[self.base1_ident, self.base2_ident],
            body=self.body_block,
            location=self.loc
        )
        self.assertIs(node.name, self.name_ident)
        self.assertEqual(node.base_classes, [self.base1_ident, self.base2_ident])
        self.assertIs(node.body, self.body_block)
        self.assertIs(node.location, self.loc)
        expected_repr = (
            f"<ClassDeclarationNode name={repr(self.name_ident)} "
            f"bases=2 body_items={len(self.body_block.statements)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_class_declaration_no_bases(self):
        """Test class declaration with no base classes."""
        node = ClassDeclarationNode(name=self.name_ident, body=self.body_block)
        self.assertEqual(len(node.base_classes), 0)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<ClassDeclarationNode name={repr(self.name_ident)} "
            f"bases=0 body_items={len(self.body_block.statements)}>"
        )
        self.assertEqual(repr(node), expected_repr)


class TestMethodDeclarationNode(unittest.TestCase):
    """Tests for MethodDeclarationNode."""
    def setUp(self):
        self.loc = SourceLocation(2, 4, 5, 5)
        self.name_ident = IdentifierNode("do_stuff")
        self.param1 = ParameterNode(IdentifierNode("p1"), IdentifierNode("int"))
        self.return_type = IdentifierNode("bool")
        self.body_stmt = LiteralNode(True)
        self.body_block = BlockNode([self.body_stmt])

    def test_method_declaration_full(self):
        """Test full method declaration."""
        node = MethodDeclarationNode(
            name=self.name_ident,
            parameters=[self.param1],
            return_type=self.return_type,
            body=self.body_block,
            location=self.loc
        )
        self.assertIs(node.name, self.name_ident)
        self.assertEqual(node.parameters, [self.param1])
        self.assertIs(node.return_type, self.return_type)
        self.assertIs(node.body, self.body_block)
        self.assertIs(node.location, self.loc)
        expected_repr = (
            f"<MethodDeclarationNode name={repr(self.name_ident)} "
            f"params={len([self.param1])} return_type={self.return_type is not None} "
            f"body_stmts={len(self.body_block.statements)}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_method_declaration_minimal(self):
        """Test minimal method declaration (name and body)."""
        name_ident = IdentifierNode("my_method")
        body_block = BlockNode([LiteralNode(True)])
        node = MethodDeclarationNode(name=name_ident, body=body_block)
        self.assertEqual(len(node.parameters), 0)
        self.assertIsNone(node.return_type)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<MethodDeclarationNode name={repr(name_ident)} "
            f"params=0 return_type=False body_stmts={len(body_block.statements)}>"
        )
        self.assertEqual(repr(node), expected_repr)


class TestAttributeDeclarationNode(unittest.TestCase):
    """Tests for AttributeDeclarationNode."""
    def test_attribute_declaration(self):
        """Test attribute declaration with type and initializer."""
        loc = SourceLocation(3,4,3,20)
        attr_name = IdentifierNode("count")
        type_node = IdentifierNode("int")
        init_val = LiteralNode(0)
        node = AttributeDeclarationNode(
            name=attr_name, type_hint=type_node, initializer=init_val, location=loc
        )
        self.assertIs(node.name, attr_name)
        self.assertIs(node.type_hint, type_node)
        self.assertIs(node.initializer, init_val)
        self.assertIs(node.location, loc)
        expected_repr = (
            f"<AttributeDeclarationNode name={repr(attr_name)} "
            f"type_hint=True initializer=True>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_attribute_declaration_minimal(self):
        """Test minimal attribute declaration (name only)."""
        attr_name = IdentifierNode("data")
        node = AttributeDeclarationNode(name=attr_name)
        self.assertIsNone(node.type_hint)
        self.assertIsNone(node.initializer)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<AttributeDeclarationNode name={repr(attr_name)} "
            f"type_hint=False initializer=False>"
        )
        self.assertEqual(repr(node), expected_repr)


class TestInstanceCreationNode(unittest.TestCase):
    """Tests for InstanceCreationNode."""
    def test_instance_creation(self):
        """Test instance creation with arguments."""
        loc = SourceLocation(10,2,10,20)
        class_id = IdentifierNode("MyService")
        arg1 = LiteralNode(10)
        arg2 = IdentifierNode("config")
        node = InstanceCreationNode(
            class_identifier=class_id, arguments=[arg1, arg2], location=loc
        )
        self.assertIs(node.class_identifier, class_id)
        self.assertEqual(node.arguments, [arg1, arg2])
        self.assertIs(node.location, loc)
        expected_repr = (
            f"<InstanceCreationNode class={repr(class_id)} "
            f"args={len([arg1, arg2])}>"
        )
        self.assertEqual(repr(node), expected_repr)

    def test_instance_creation_no_args(self):
        """Test instance creation with no arguments."""
        class_id = IdentifierNode("Logger")
        node = InstanceCreationNode(class_identifier=class_id)
        self.assertEqual(len(node.arguments), 0)
        self.assertIsNone(node.location)
        expected_repr = (
            f"<InstanceCreationNode class={repr(class_id)} "
            f"args=0>"
        )
        self.assertEqual(repr(node), expected_repr)


class TestMemberAccessNode(unittest.TestCase):
    """Tests for MemberAccessNode."""
    def test_member_access(self):
        """Test member access."""
        loc = SourceLocation(12,0,12,15)
        obj_expr = IdentifierNode("my_obj")
        member_name = IdentifierNode("value")
        node = MemberAccessNode(object_expr=obj_expr, member_name=member_name, location=loc)
        self.assertIs(node.object_expr, obj_expr)
        self.assertIs(node.member_name, member_name)
        self.assertIs(node.location, loc)
        expected_repr = (
            f"<MemberAccessNode object={repr(obj_expr)} "
            f"member={repr(member_name)}>"
        )
        self.assertEqual(repr(node), expected_repr)


if __name__ == '__main__':
    unittest.main()
