#!/usr/bin/env python3
"""
Symbol Table Tests
==================

Tests for the SymbolTable class which manages symbol storage,
scope handling, and symbol lookup with lexical scoping.

Author: DarkLightX/Dana Edwards
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic_types import Symbol, SymbolTable, SemanticError


class TestSymbolTable(unittest.TestCase):
    """Tests for SymbolTable class"""
    
    def test_symbol_table_initialization(self):
        """Test symbol table initial state"""
        table = SymbolTable()
        self.assertEqual(table.current_scope_level, 0)
        self.assertEqual(len(table.scopes), 1)
        self.assertEqual(table.scopes[0], {})
        self.assertEqual(table._lookup_count, 0)
        self.assertEqual(table._symbol_count, 0)
    
    def test_declare_symbol_success(self):
        """Test successful symbol declaration"""
        table = SymbolTable()
        symbol = Symbol("x", "variable", 0)
        
        table.declare_symbol(symbol)
        
        self.assertIn("x", table.scopes[0])
        self.assertEqual(table.scopes[0]["x"], symbol)
        self.assertEqual(table._symbol_count, 1)
    
    def test_declare_symbol_duplicate(self):
        """Test declaring duplicate symbol in same scope"""
        table = SymbolTable()
        symbol1 = Symbol("x", "variable", 0)
        symbol2 = Symbol("x", "variable", 0)
        
        table.declare_symbol(symbol1)
        
        with self.assertRaises(SemanticError) as cm:
            table.declare_symbol(symbol2)
        self.assertIn("already declared", str(cm.exception))
    
    def test_declare_symbol_none(self):
        """Test declaring None as symbol"""
        table = SymbolTable()
        
        with self.assertRaises(ValueError) as cm:
            table.declare_symbol(None)
        self.assertIn("Symbol cannot be None", str(cm.exception))
    
    def test_lookup_symbol_exists(self):
        """Test looking up existing symbol"""
        table = SymbolTable()
        symbol = Symbol("test", "variable", 0)
        table.declare_symbol(symbol)
        
        found = table.lookup_symbol("test")
        
        self.assertEqual(found, symbol)
        self.assertEqual(table._lookup_count, 1)
    
    def test_lookup_symbol_not_exists(self):
        """Test looking up non-existent symbol"""
        table = SymbolTable()
        
        found = table.lookup_symbol("nonexistent")
        
        self.assertIsNone(found)
        self.assertEqual(table._lookup_count, 1)
    
    def test_lookup_symbol_empty_name(self):
        """Test lookup with empty name"""
        table = SymbolTable()
        
        with self.assertRaises(ValueError) as cm:
            table.lookup_symbol("")
        self.assertIn("Symbol name cannot be empty", str(cm.exception))
        
        with self.assertRaises(ValueError):
            table.lookup_symbol("   ")
    
    def test_symbol_exists_method(self):
        """Test symbol_exists convenience method"""
        table = SymbolTable()
        symbol = Symbol("x", "variable", 0)
        table.declare_symbol(symbol)
        
        self.assertTrue(table.symbol_exists("x"))
        self.assertFalse(table.symbol_exists("y"))
    
    def test_scope_management(self):
        """Test entering and exiting scopes"""
        table = SymbolTable()
        
        # Enter new scope
        table.enter_scope()
        self.assertEqual(table.current_scope_level, 1)
        self.assertEqual(len(table.scopes), 2)
        
        # Enter another scope
        table.enter_scope()
        self.assertEqual(table.current_scope_level, 2)
        self.assertEqual(len(table.scopes), 3)
        
        # Exit scope
        table.exit_scope()
        self.assertEqual(table.current_scope_level, 1)
        self.assertEqual(len(table.scopes), 2)
        
        # Exit to global
        table.exit_scope()
        self.assertEqual(table.current_scope_level, 0)
        self.assertEqual(len(table.scopes), 1)
    
    def test_exit_global_scope_error(self):
        """Test error when trying to exit global scope"""
        table = SymbolTable()
        
        with self.assertRaises(SemanticError) as cm:
            table.exit_scope()
        self.assertIn("Cannot exit global scope", str(cm.exception))
    
    def test_scope_shadowing(self):
        """Test variable shadowing in nested scopes"""
        table = SymbolTable()
        
        # Global variable
        global_x = Symbol("x", "variable", 0)
        table.declare_symbol(global_x)
        
        # Enter new scope and shadow
        table.enter_scope()
        local_x = Symbol("x", "variable", 1)
        table.declare_symbol(local_x)
        
        # Should find local x
        found = table.lookup_symbol("x")
        self.assertEqual(found, local_x)
        
        # Exit scope
        table.exit_scope()
        
        # Should find global x
        found = table.lookup_symbol("x")
        self.assertEqual(found, global_x)
    
    def test_symbol_count_tracking(self):
        """Test accurate symbol counting"""
        table = SymbolTable()
        
        # Add symbols
        table.declare_symbol(Symbol("a", "variable", 0))
        table.declare_symbol(Symbol("b", "variable", 0))
        self.assertEqual(table._symbol_count, 2)
        
        # Add in new scope
        table.enter_scope()
        table.declare_symbol(Symbol("c", "variable", 1))
        self.assertEqual(table._symbol_count, 3)
        
        # Exit scope should decrease count
        table.exit_scope()
        self.assertEqual(table._symbol_count, 2)
    
    def test_get_symbols_in_scope(self):
        """Test retrieving symbols from specific scope"""
        table = SymbolTable()
        
        # Add to global
        sym_a = Symbol("a", "variable", 0)
        sym_b = Symbol("b", "variable", 0)
        table.declare_symbol(sym_a)
        table.declare_symbol(sym_b)
        
        # Add to local
        table.enter_scope()
        sym_c = Symbol("c", "variable", 1)
        table.declare_symbol(sym_c)
        
        # Get global symbols
        global_symbols = table.get_symbols_in_scope(0)
        self.assertEqual(len(global_symbols), 2)
        self.assertIn(sym_a, global_symbols)
        self.assertIn(sym_b, global_symbols)
        
        # Get current scope symbols
        current_symbols = table.get_symbols_in_scope()
        self.assertEqual(len(current_symbols), 1)
        self.assertIn(sym_c, current_symbols)
        
        # Invalid scope
        with self.assertRaises(ValueError):
            table.get_symbols_in_scope(5)
    
    def test_performance_stats(self):
        """Test performance statistics tracking"""
        table = SymbolTable()
        
        # Initial stats
        stats = table.get_performance_stats()
        self.assertEqual(stats['lookup_count'], 0)
        self.assertEqual(stats['symbol_count'], 0)
        self.assertEqual(stats['scope_depth'], 0)
        self.assertEqual(stats['total_scopes'], 1)
        
        # After operations
        table.declare_symbol(Symbol("x", "variable", 0))
        table.lookup_symbol("x")
        table.enter_scope()
        
        stats = table.get_performance_stats()
        self.assertEqual(stats['lookup_count'], 1)
        self.assertEqual(stats['symbol_count'], 1)
        self.assertEqual(stats['scope_depth'], 1)
        self.assertEqual(stats['total_scopes'], 2)


if __name__ == '__main__':
    unittest.main()