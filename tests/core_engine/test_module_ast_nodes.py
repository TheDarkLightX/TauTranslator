# tests/core_engine/test_module_ast_nodes.py
"""
Tests for module and import related AST nodes.
"""

import unittest
from typing import List, Optional

from tau_translator_omega.core_engine.ast.ast_nodes import (
    ASTNode, SourceLocation, IdentifierNode, LiteralNode, BlockNode, # For ModuleNode body
    ImportSpecifierNode, ImportStatementNode, ModuleNode
)


class TestImportSpecifierNode(unittest.TestCase):
    """Tests for ImportSpecifierNode."""
    def test_import_specifier_simple(self):
        """Test import specifier without alias."""
        loc = SourceLocation(1, 7, 1, 10)
        name_id = IdentifierNode("math", location=SourceLocation(1,7,1,10))
        spec = ImportSpecifierNode(name=name_id, location=loc)
        self.assertIs(spec.name, name_id)
        self.assertIsNone(spec.alias)
        self.assertIs(spec.location, loc)
        expected_repr = f"<ImportSpecifierNode name={repr(name_id)}>"
        self.assertEqual(repr(spec), expected_repr)

    def test_import_specifier_with_alias(self):
        """Test import specifier with an alias."""
        loc = SourceLocation(1, 7, 1, 18)
        name_id = IdentifierNode("numpy", location=SourceLocation(1,7,1,11))
        alias_id = IdentifierNode("np", location=SourceLocation(1,16,1,18))
        spec = ImportSpecifierNode(name=name_id, alias=alias_id, location=loc)
        self.assertIs(spec.name, name_id)
        self.assertIs(spec.alias, alias_id)
        self.assertIs(spec.location, loc)
        expected_repr = f"<ImportSpecifierNode name={repr(name_id)} alias={repr(alias_id)}>"
        self.assertEqual(repr(spec), expected_repr)


class TestImportStatementNode(unittest.TestCase):
    """Tests for ImportStatementNode."""
    def setUp(self):
        self.loc = SourceLocation(1,0,1,20)
        self.module_part1 = IdentifierNode("my_lib")
        self.module_part2 = IdentifierNode("sub_module")
        self.spec1_name = IdentifierNode("func_a")
        self.spec1 = ImportSpecifierNode(self.spec1_name)
        self.spec2_name = IdentifierNode("ClassB")
        self.spec2_alias = IdentifierNode("CB")
        self.spec2 = ImportSpecifierNode(self.spec2_name, self.spec2_alias)

    def test_import_module_direct(self):
        """Test 'import module' style."""
        node = ImportStatementNode(module_path=[self.module_part1], location=self.loc)
        self.assertEqual(node.module_path, [self.module_part1])
        self.assertIsNone(node.specifiers)
        self.assertIs(node.location, self.loc)
        expected_repr = f"<ImportStatementNode path='my_lib' specifiers=0>"
        self.assertEqual(repr(node), expected_repr)

    def test_import_module_path_direct(self):
        """Test 'import module.submodule' style."""
        node = ImportStatementNode(module_path=[self.module_part1, self.module_part2])
        self.assertEqual(node.module_path, [self.module_part1, self.module_part2])
        self.assertIsNone(node.specifiers)
        expected_repr = f"<ImportStatementNode path='my_lib.sub_module' specifiers=0>"
        self.assertEqual(repr(node), expected_repr)

    def test_from_module_import_specifiers(self):
        """Test 'from module import name1, name2 as alias' style."""
        node = ImportStatementNode(
            module_path=[self.module_part1],
            specifiers=[self.spec1, self.spec2],
            location=self.loc
        )
        self.assertEqual(node.module_path, [self.module_part1])
        self.assertEqual(node.specifiers, [self.spec1, self.spec2])
        self.assertIs(node.location, self.loc)
        expected_repr = f"<ImportStatementNode path='my_lib' specifiers=2>"
        self.assertEqual(repr(node), expected_repr)


class TestModuleNode(unittest.TestCase):
    """Tests for ModuleNode."""
    def test_module_node_creation(self):
        """Test creating a ModuleNode with a body."""
        loc = SourceLocation(1,0,5,0) # Spanning the whole pseudo-file
        import_stmt = ImportStatementNode([IdentifierNode("os")])
        func_def = IdentifierNode("some_function_definition_placeholder") # Simplified for test
        class_def = IdentifierNode("some_class_definition_placeholder")   # Simplified for test
        
        body_nodes = [import_stmt, func_def, class_def]
        node = ModuleNode(body=body_nodes, location=loc)
        
        self.assertEqual(node.body, body_nodes)
        self.assertIs(node.location, loc)
        expected_repr = f"<ModuleNode body_items=3>"
        self.assertEqual(repr(node), expected_repr)

    def test_empty_module_node(self):
        """Test creating an empty ModuleNode."""
        node = ModuleNode(body=[])
        self.assertEqual(len(node.body), 0)
        self.assertIsNone(node.location)
        expected_repr = f"<ModuleNode body_items=0>"
        self.assertEqual(repr(node), expected_repr)


if __name__ == '__main__':
    unittest.main()
