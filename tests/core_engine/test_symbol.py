#!/usr/bin/env python3
"""
Symbol Class Tests
==================

Tests for the Symbol class which represents identifiers in the symbol table
including variables, functions, types, and other named entities.

Author: DarkLightX/Dana Edwards
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic_types import Symbol
from tau_translator_omega.core_engine.cnl_parser.ast_nodes import VariableNode


class TestSymbol(unittest.TestCase):
    """Tests for Symbol class"""
    
    def test_symbol_creation_valid(self):
        """Test creating a valid symbol"""
        symbol = Symbol("test_var", "variable", 0)
        self.assertEqual(symbol.name, "test_var")
        self.assertEqual(symbol.symbol_type, "variable")
        self.assertEqual(symbol.scope_level, 0)
        self.assertEqual(symbol.attributes, {})
        self.assertIsNone(symbol.ast_node)
        self.assertIsNone(symbol.var_type)
    
    def test_symbol_creation_with_optional_params(self):
        """Test symbol creation with all parameters"""
        node = VariableNode(name="x", line=1, column=0)
        symbol = Symbol("x", "variable", 1, ast_node=node, var_type="integer")
        self.assertEqual(symbol.ast_node, node)
        self.assertEqual(symbol.var_type, "integer")
    
    def test_symbol_name_validation(self):
        """Test symbol name validation"""
        # Empty name
        with self.assertRaises(ValueError) as cm:
            Symbol("", "variable", 0)
        self.assertIn("Symbol name cannot be empty", str(cm.exception))
        
        # Whitespace only
        with self.assertRaises(ValueError) as cm:
            Symbol("   ", "variable", 0)
        self.assertIn("Symbol name cannot be empty", str(cm.exception))
        
        # None name - Python's truth test makes None fail the "not name" check
        with self.assertRaises(ValueError):
            Symbol(None, "variable", 0)
    
    def test_symbol_type_validation(self):
        """Test symbol type validation"""
        # Empty type
        with self.assertRaises(ValueError) as cm:
            Symbol("test", "", 0)
        self.assertIn("Symbol type cannot be empty", str(cm.exception))
        
        # Whitespace only
        with self.assertRaises(ValueError) as cm:
            Symbol("test", "   ", 0)
        self.assertIn("Symbol type cannot be empty", str(cm.exception))
    
    def test_symbol_scope_level_validation(self):
        """Test scope level validation"""
        with self.assertRaises(ValueError) as cm:
            Symbol("test", "variable", -1)
        self.assertIn("Scope level cannot be negative", str(cm.exception))
    
    def test_symbol_name_and_type_stripping(self):
        """Test that name and type are stripped of whitespace"""
        symbol = Symbol("  test  ", "  variable  ", 0)
        self.assertEqual(symbol.name, "test")
        self.assertEqual(symbol.symbol_type, "variable")
    
    def test_symbol_equality(self):
        """Test symbol equality comparison"""
        sym1 = Symbol("x", "variable", 0)
        sym2 = Symbol("x", "variable", 0)
        sym3 = Symbol("x", "variable", 1)  # Different scope
        sym4 = Symbol("y", "variable", 0)  # Different name
        sym5 = Symbol("x", "function", 0)  # Different type
        
        self.assertEqual(sym1, sym2)
        self.assertNotEqual(sym1, sym3)
        self.assertNotEqual(sym1, sym4)
        self.assertNotEqual(sym1, sym5)
        self.assertNotEqual(sym1, "not a symbol")
    
    def test_symbol_hash(self):
        """Test symbol hashing for use in sets/dicts"""
        sym1 = Symbol("x", "variable", 0)
        sym2 = Symbol("x", "variable", 0)
        sym3 = Symbol("y", "variable", 0)
        
        # Equal symbols should have same hash
        self.assertEqual(hash(sym1), hash(sym2))
        
        # Can be used in sets
        symbol_set = {sym1, sym2, sym3}
        self.assertEqual(len(symbol_set), 2)  # sym1 and sym2 are equal
    
    def test_symbol_repr(self):
        """Test symbol string representation"""
        symbol = Symbol("test_func", "function", 2)
        repr_str = repr(symbol)
        self.assertIn("test_func", repr_str)
        self.assertIn("function", repr_str)
        self.assertIn("scope=2", repr_str)


if __name__ == '__main__':
    unittest.main()