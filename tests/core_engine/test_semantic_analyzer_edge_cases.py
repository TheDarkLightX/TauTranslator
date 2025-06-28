#!/usr/bin/env python3
"""
Mutation-Hardened Semantic Analyzer Tests
=========================================

RED-GREEN-MUTATE-REFACTOR TDD tests designed to kill mutants and achieve
100% mutation test resistance for critical semantic analyzer functionality.

Author: DarkLightX / Dana Edwards
"""

import unittest
import sys
from pathlib import Path
from typing import List, Optional
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic.semantic_analyzer import SemanticAnalyzer
from tau_translator_omega.core_engine.semantic_types import (
    SemanticError, Symbol, SymbolTable, TypeInfo, ErrorCollector
)
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    VariableDeclNode, VariableNode, ConstantNode, SentenceNode,
    AssignmentNode, ArithmeticBinaryOpNode, PredicateCallNode
)


class TestSemanticAnalyzerMutationHardened(unittest.TestCase):
    """Mutation-hardened tests to kill surviving mutants in semantic analyzer"""
    
    def setUp(self):
        """Set up test environment with minimal vocabulary for focused testing"""
        self.analyzer = SemanticAnalyzer({
            'types': {'integer', 'string', 'boolean', 'auto'},
            'predicates': {'prime': {'arity': 1, 'signature': ['integer']}},
            'functions': {'add': {'arity': 2, 'signature': ['integer', 'integer'], 'return': 'integer'}}
        })
    
    def test_analyzer_initialization_kills_null_vocabulary_mutant(self):
        """KILL MUTANT: Analyzer with None vocabulary should use default"""
        # This kills mutants that might skip default vocabulary initialization
        analyzer_null = SemanticAnalyzer(None)
        self.assertIsNotNone(analyzer_null.vocabulary)
        self.assertIn('types', analyzer_null.vocabulary)
        
        # Mutant killer: Verify specific default types exist
        self.assertIn('integer', analyzer_null.vocabulary['types'])
        self.assertIn('auto', analyzer_null.vocabulary['types'])
    
    def test_analysis_count_increment_kills_tracking_mutants(self):
        """KILL MUTANT: Analysis count must increment on every analyze() call"""
        initial_count = self.analyzer._analysis_count
        
        # Kill mutant that might not increment counter
        self.analyzer.analyze(None)
        self.assertEqual(self.analyzer._analysis_count, initial_count + 1)
        
        # Kill mutant that might increment by wrong amount
        ast = SentenceNode(content=[VariableDeclNode(name="test", var_type="integer")])
        self.analyzer.analyze(ast)
        self.assertEqual(self.analyzer._analysis_count, initial_count + 2)
        
        # Kill mutant that might reset counter incorrectly
        for _ in range(3):
            self.analyzer.analyze(None)
        self.assertEqual(self.analyzer._analysis_count, initial_count + 5)
    
    def test_error_collector_clear_kills_accumulation_mutants(self):
        """KILL MUTANT: Error collector must clear between analyses"""
        # Setup: create an AST that will generate an error
        error_ast = SentenceNode(content=[
            VariableDeclNode(name="bad", var_type="nonexistent_type")
        ])
        
        # First analysis - should have errors
        _, errors1 = self.analyzer.analyze(error_ast)
        
        # Second analysis with valid AST - errors should be cleared
        valid_ast = SentenceNode(content=[
            VariableDeclNode(name="good", var_type="integer")
        ])
        _, errors2 = self.analyzer.analyze(valid_ast)
        
        # Kill mutant that might accumulate errors across analyses
        self.assertEqual(len(errors2), 0, "Errors should be cleared between analyses")
        
        # Kill mutant that might not clear error collector internal state
        self.assertFalse(self.analyzer.error_collector.has_errors())
    
    def test_vocabulary_symbol_loading_kills_skip_mutants(self):
        """KILL MUTANT: All vocabulary symbols must be loaded into symbol table"""
        # Kill mutant that might skip predicate loading
        prime_symbol = self.analyzer.symbol_table.lookup_symbol('prime')
        self.assertIsNotNone(prime_symbol, "Predicate 'prime' must be loaded")
        self.assertEqual(prime_symbol.symbol_type, 'predicate')
        
        # Kill mutant that might skip function loading
        add_symbol = self.analyzer.symbol_table.lookup_symbol('add')
        self.assertIsNotNone(add_symbol, "Function 'add' must be loaded")
        self.assertEqual(add_symbol.symbol_type, 'function')
        
        # Kill mutant that might not set attributes correctly
        self.assertEqual(prime_symbol.attributes['arity'], 1)
        self.assertEqual(add_symbol.attributes['return_type'], 'integer')
        
        # Kill mutant that might use wrong scope level for vocabulary symbols
        self.assertEqual(prime_symbol.scope_level, 0, "Vocabulary symbols must be global")
        self.assertEqual(add_symbol.scope_level, 0, "Vocabulary symbols must be global")
    
    def test_visit_method_dispatch_kills_bypass_mutants(self):
        """KILL MUTANT: _visit method must dispatch to correct visitor methods"""
        # Create a mock node to track visitor calls
        test_node = SentenceNode(content=[])
        
        # Kill mutant that might not call visitor at all
        with patch.object(self.analyzer, '_visit_SentenceNode') as mock_visitor:
            self.analyzer._visit(test_node)
            mock_visitor.assert_called_once_with(test_node)
        
        # Kill mutant that might call wrong visitor method
        var_node = VariableDeclNode(name="test", var_type="integer")
        with patch.object(self.analyzer, '_visit_VariableDeclNode') as mock_var_visitor:
            self.analyzer._visit(var_node)
            mock_var_visitor.assert_called_once_with(var_node)
    
    def test_null_node_handling_kills_crash_mutants(self):
        """KILL MUTANT: Null nodes must be handled gracefully without crashing"""
        # Kill mutant that might crash on None input
        try:
            result, errors = self.analyzer.analyze(None)
            # Should not crash - this kills crash mutants
        except Exception as e:
            self.fail(f"Analyzer should handle None gracefully, but got: {e}")
        
        # Kill mutant that might return wrong values for None
        self.assertIsNone(result)
        
        # Kill mutant in _visit that might crash on None
        try:
            self.analyzer._visit(None)
            # Should not crash
        except Exception as e:
            self.fail(f"_visit should handle None gracefully, but got: {e}")
    
    def test_sentence_node_content_iteration_kills_skip_mutants(self):
        """KILL MUTANT: SentenceNode visitor must process all content items"""
        # Create sentence with multiple statements
        multi_stmt = SentenceNode(content=[
            VariableDeclNode(name="a", var_type="integer"),
            VariableDeclNode(name="b", var_type="integer"),
            VariableDeclNode(name="c", var_type="integer")
        ])
        
        # Track how many variable declarations are processed
        original_visit_var = self.analyzer._visit_VariableDeclNode
        visit_count = 0
        
        def counting_visitor(node):
            nonlocal visit_count
            visit_count += 1
            return original_visit_var(node)
        
        # Kill mutant that might skip some content items
        with patch.object(self.analyzer, '_visit_VariableDeclNode', counting_visitor):
            self.analyzer.analyze(multi_stmt)
            
        self.assertEqual(visit_count, 3, "Must visit all 3 variable declarations")
        
        # Verify all variables were actually declared
        self.assertIsNotNone(self.analyzer.symbol_table.lookup_symbol('a'))
        self.assertIsNotNone(self.analyzer.symbol_table.lookup_symbol('b'))
        self.assertIsNotNone(self.analyzer.symbol_table.lookup_symbol('c'))
    
    def test_variable_type_validation_kills_bypass_mutants(self):
        """KILL MUTANT: Variable type validation must be called for every declaration"""
        # Kill mutant that might skip type validation
        valid_types = ['integer', 'string', 'boolean', 'auto']
        invalid_types = ['nonexistent', 'invalid', 'badtype']
        
        # Test all valid types - should not produce errors (except auto without initializer)
        for valid_type in valid_types:
            if valid_type == 'auto':
                # Auto type requires initializer
                ast = SentenceNode(content=[
                    VariableDeclNode(name=f"var_{valid_type}", var_type=valid_type,
                                   value=ConstantNode(value=1, value_type="NUMBER"))
                ])
            else:
                ast = SentenceNode(content=[
                    VariableDeclNode(name=f"var_{valid_type}", var_type=valid_type)
                ])
            _, errors = self.analyzer.analyze(ast)
            # Kill mutant that might generate errors for valid types
            self.assertEqual(len([e for e in errors if 'type' in str(e).lower()]), 0,
                           f"Valid type '{valid_type}' should not generate type errors")
        
        # Test invalid types - should produce errors
        for invalid_type in invalid_types:
            ast = SentenceNode(content=[
                VariableDeclNode(name=f"var_{invalid_type}", var_type=invalid_type)
            ])
            _, errors = self.analyzer.analyze(ast)
            # Kill mutant that might not generate errors for invalid types
            type_errors = [e for e in errors if 'type' in str(e).lower() or 'unknown' in str(e).lower()]
            self.assertGreater(len(type_errors), 0,
                             f"Invalid type '{invalid_type}' should generate type errors")
    
    def test_performance_stats_kills_tracking_mutants(self):
        """KILL MUTANT: Performance stats must accurately reflect analyzer state"""
        # Get initial stats
        initial_stats = self.analyzer.get_analysis_stats()
        
        # Kill mutant that might return None or wrong structure
        self.assertIsInstance(initial_stats, dict)
        self.assertIn('analysis_count', initial_stats)
        self.assertIn('symbol_table_stats', initial_stats)
        self.assertIn('error_summary', initial_stats)
        
        # Perform analysis and verify stats update
        ast = SentenceNode(content=[VariableDeclNode(name="stat_test", var_type="integer")])
        self.analyzer.analyze(ast)
        
        updated_stats = self.analyzer.get_analysis_stats()
        
        # Kill mutant that might not update analysis count
        self.assertEqual(updated_stats['analysis_count'], 
                        initial_stats['analysis_count'] + 1)
        
        # Kill mutant that might not delegate to symbol table stats
        self.assertIsInstance(updated_stats['symbol_table_stats'], dict)
        
        # Kill mutant that might not delegate to error collector stats
        self.assertIsInstance(updated_stats['error_summary'], dict)
    
    def test_auto_type_inference_boundary_conditions(self):
        """KILL MUTANT: Auto type handling must work for all boundary conditions"""
        # Kill mutant that might skip auto type without initializer error
        auto_no_init = SentenceNode(content=[
            VariableDeclNode(name="auto_var", var_type="auto", value=None)
        ])
        _, errors = self.analyzer.analyze(auto_no_init)
        
        # Must generate error for auto without initializer
        auto_errors = [e for e in errors if 'auto' in str(e).lower() and 'initializer' in str(e).lower()]
        self.assertGreater(len(auto_errors), 0, "Auto type without initializer must generate error")
        
        # Kill mutant that might not process auto with initializer correctly
        auto_with_init = SentenceNode(content=[
            VariableDeclNode(name="auto_with_val", var_type="auto", 
                           value=ConstantNode(value=42, value_type="NUMBER"))
        ])
        _, errors_init = self.analyzer.analyze(auto_with_init)
        
        # Should not generate auto-related errors when initializer is present
        auto_init_errors = [e for e in errors_init if 'auto' in str(e).lower() and 'initializer' in str(e).lower()]
        self.assertEqual(len(auto_init_errors), 0, "Auto type with initializer should not generate auto errors")


class TestSymbolTableMutationHardened(unittest.TestCase):
    """Mutation-hardened tests for SymbolTable to kill all surviving mutants"""
    
    def setUp(self):
        self.table = SymbolTable()
    
    def test_scope_level_tracking_kills_increment_mutants(self):
        """KILL MUTANT: Scope level must increment/decrement correctly"""
        initial_level = self.table.current_scope_level
        
        # Kill mutant that might not increment scope level
        self.table.enter_scope()
        self.assertEqual(self.table.current_scope_level, initial_level + 1)
        
        # Kill mutant that might increment by wrong amount
        self.table.enter_scope()
        self.assertEqual(self.table.current_scope_level, initial_level + 2)
        
        # Kill mutant that might not decrement scope level
        self.table.exit_scope()
        self.assertEqual(self.table.current_scope_level, initial_level + 1)
        
        # Kill mutant that might decrement by wrong amount
        self.table.exit_scope()
        self.assertEqual(self.table.current_scope_level, initial_level)
    
    def test_symbol_lookup_scope_order_kills_wrong_order_mutants(self):
        """KILL MUTANT: Symbol lookup must search from inner to outer scopes"""
        # Declare symbol in global scope
        global_symbol = Symbol("test", "variable", 0)
        self.table.declare_symbol(global_symbol)
        
        # Enter new scope and declare symbol with same name
        self.table.enter_scope()
        inner_symbol = Symbol("test", "variable", 1)
        self.table.declare_symbol(inner_symbol)
        
        # Kill mutant that might return wrong symbol or search in wrong order
        found = self.table.lookup_symbol("test")
        self.assertEqual(found, inner_symbol, "Must find inner scope symbol first")
        self.assertNotEqual(found, global_symbol, "Must not return outer scope symbol when inner exists")
        
        # Exit scope and verify outer symbol is found
        self.table.exit_scope()
        found_outer = self.table.lookup_symbol("test")
        self.assertEqual(found_outer, global_symbol, "Must find outer scope symbol after exiting inner")
    
    def test_symbol_count_tracking_kills_counting_mutants(self):
        """KILL MUTANT: Symbol count must be accurate across scope operations"""
        initial_count = self.table.get_performance_stats()['symbol_count']
        
        # Kill mutant that might not increment symbol count
        symbol1 = Symbol("sym1", "variable", 0)
        self.table.declare_symbol(symbol1)
        self.assertEqual(self.table.get_performance_stats()['symbol_count'], initial_count + 1)
        
        # Kill mutant that might not handle scope exit counting correctly
        self.table.enter_scope()
        symbol2 = Symbol("sym2", "variable", 1)
        self.table.declare_symbol(symbol2)
        self.assertEqual(self.table.get_performance_stats()['symbol_count'], initial_count + 2)
        
        # Exit scope - should decrease count
        self.table.exit_scope()
        self.assertEqual(self.table.get_performance_stats()['symbol_count'], initial_count + 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)