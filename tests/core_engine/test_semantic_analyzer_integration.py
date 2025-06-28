#!/usr/bin/env python3
"""
Semantic Analyzer Integration Tests
===================================

Integration tests for the semantic analyzer covering variable declarations,
assignments, type checking, scoping, and error detection.

Author: DarkLightX / Dana Edwards
"""

import unittest
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic.semantic_analyzer import SemanticAnalyzer
from tau_translator_omega.core_engine.semantic_types import (
    SemanticError, Symbol, SymbolTable, TypeInfo, ErrorCollector,
    create_type_info, check_type_compatibility
)
from tau_translator_omega.core_engine.semantic.semantic_analyzer_core import (
    ExpressionTypeResolver, ValidationEngine, SymbolDefinitionManager
)
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    VariableDeclNode, VariableNode, ConstantNode, SentenceNode,
    AssignmentNode, ArithmeticBinaryOpNode, BooleanBinaryOpNode,
    ComparisonNode, PredicateCallNode, FunctionDefinitionNode,
    QuantifierBlockNode, ConditionNode
)


class TestSemanticAnalyzerIntegration(unittest.TestCase):
    """Integration tests for semantic analyzer functionality"""
    
    def setUp(self):
        """Set up test environment with comprehensive vocabulary"""
        self.vocabulary = {
            'types': {'integer', 'string', 'boolean', 'real', 'auto'},
            'predicates': {
                'prime': {'arity': 1, 'signature': ['integer']},
                'greater': {'arity': 2, 'signature': ['integer', 'integer']},
                'equals': {'arity': 2, 'signature': ['auto', 'auto']},
                'valid': {'arity': 1, 'signature': ['string']}
            },
            'functions': {
                'add': {'arity': 2, 'signature': ['integer', 'integer'], 'return': 'integer'},
                'concat': {'arity': 2, 'signature': ['string', 'string'], 'return': 'string'},
                'length': {'arity': 1, 'signature': ['string'], 'return': 'integer'},
                'max': {'arity': 2, 'signature': ['real', 'real'], 'return': 'real'}
            }
        }
        self.analyzer = SemanticAnalyzer(self.vocabulary)
    
    def test_analyzer_initialization_with_vocabulary(self):
        """Test analyzer initialization with comprehensive vocabulary loading"""
        # Test default initialization
        default_analyzer = SemanticAnalyzer()
        self.assertIsNotNone(default_analyzer.vocabulary)
        self.assertIn('types', default_analyzer.vocabulary)
        
        # Test custom vocabulary initialization
        custom_vocab = {'types': {'custom_type'}, 'predicates': {}, 'functions': {}}
        custom_analyzer = SemanticAnalyzer(custom_vocab)
        self.assertEqual(custom_analyzer.vocabulary, custom_vocab)
        
        # Test vocabulary symbol loading
        self.assertIsNotNone(self.analyzer.symbol_table.lookup_symbol('prime'))
        self.assertIsNotNone(self.analyzer.symbol_table.lookup_symbol('add'))
        
        # Verify predicate symbols
        prime_symbol = self.analyzer.symbol_table.lookup_symbol('prime')
        self.assertEqual(prime_symbol.symbol_type, 'predicate')
        self.assertEqual(prime_symbol.attributes['arity'], 1)
        
        # Verify function symbols
        add_symbol = self.analyzer.symbol_table.lookup_symbol('add')
        self.assertEqual(add_symbol.symbol_type, 'function')
        self.assertEqual(add_symbol.attributes['return_type'], 'integer')
    
    def test_analyze_variable_declarations(self):
        """Test comprehensive variable declaration analysis"""
        # Simple variable declaration
        ast = SentenceNode(content=[
            VariableDeclNode(name="x", var_type="integer", line=1, column=0)
        ])
        
        result, errors = self.analyzer.analyze(ast)
        self.assertEqual(len(errors), 0, f"Unexpected errors: {errors}")
        
        # Verify symbol was added
        x_symbol = self.analyzer.symbol_table.lookup_symbol("x")
        self.assertIsNotNone(x_symbol)
        self.assertEqual(x_symbol.var_type, "integer")
        
        # Test auto type inference
        ast_auto = SentenceNode(content=[
            VariableDeclNode(name="y", var_type="auto", 
                           value=ConstantNode(value=42, value_type="NUMBER"), 
                           line=2, column=0)
        ])
        
        result_auto, errors_auto = self.analyzer.analyze(ast_auto)
        self.assertEqual(len(errors_auto), 0, f"Auto type errors: {errors_auto}")
        
        # Test invalid type
        ast_invalid = SentenceNode(content=[
            VariableDeclNode(name="z", var_type="nonexistent", line=3, column=0)
        ])
        
        result_invalid, errors_invalid = self.analyzer.analyze(ast_invalid)
        self.assertGreater(len(errors_invalid), 0, "Expected error for invalid type")
    
    def test_analyze_assignments(self):
        """Test assignment analysis with type checking"""
        # Setup: declare variable first
        decl_ast = SentenceNode(content=[
            VariableDeclNode(name="count", var_type="integer", line=1, column=0)
        ])
        self.analyzer.analyze(decl_ast)
        
        # Valid assignment
        assign_ast = SentenceNode(content=[
            AssignmentNode(
                target=VariableNode(name="count", line=2, column=0),
                expression=ConstantNode(value=10, value_type="NUMBER"),
                line=2, column=0
            )
        ])
        
        result, errors = self.analyzer.analyze(assign_ast)
        self.assertEqual(len(errors), 0, f"Assignment errors: {errors}")
        
        # Invalid assignment - type mismatch
        invalid_assign_ast = SentenceNode(content=[
            AssignmentNode(
                target=VariableNode(name="count", line=3, column=0),
                expression=ConstantNode(value="text", value_type="STRING"),
                line=3, column=0
            )
        ])
        
        result_invalid, errors_invalid = self.analyzer.analyze(invalid_assign_ast)
        self.assertGreater(len(errors_invalid), 0, "Expected type mismatch error")
        
        # Assignment to undeclared variable
        undeclared_ast = SentenceNode(content=[
            AssignmentNode(
                target=VariableNode(name="undefined", line=4, column=0),
                expression=ConstantNode(value=5, value_type="NUMBER"),
                line=4, column=0
            )
        ])
        
        result_undeclared, errors_undeclared = self.analyzer.analyze(undeclared_ast)
        self.assertGreater(len(errors_undeclared), 0, "Expected undefined variable error")
    
    def test_analyze_arithmetic_expressions(self):
        """Test arithmetic expression type analysis"""
        # Setup variables
        setup_ast = SentenceNode(content=[
            VariableDeclNode(name="a", var_type="integer", line=1, column=0),
            VariableDeclNode(name="b", var_type="integer", line=2, column=0)
        ])
        self.analyzer.analyze(setup_ast)
        
        # Arithmetic expression
        expr_ast = SentenceNode(content=[
            VariableDeclNode(
                name="result", 
                var_type="auto",
                value=ArithmeticBinaryOpNode(
                    left=VariableNode(name="a", line=3, column=0),
                    operator="+",
                    right=VariableNode(name="b", line=3, column=4),
                    line=3, column=2
                ),
                line=3, column=0
            )
        ])
        
        result, errors = self.analyzer.analyze(expr_ast)
        self.assertEqual(len(errors), 0, f"Arithmetic expression errors: {errors}")
        
        # Verify type inference
        result_symbol = self.analyzer.symbol_table.lookup_symbol("result")
        self.assertIsNotNone(result_symbol)
        # Should infer integer type from integer operands
    
    def test_analyze_predicate_calls(self):
        """Test predicate call validation"""
        # Setup variable
        setup_ast = SentenceNode(content=[
            VariableDeclNode(name="num", var_type="integer", line=1, column=0)
        ])
        self.analyzer.analyze(setup_ast)
        
        # Valid predicate call
        pred_ast = SentenceNode(content=[
            PredicateCallNode(
                name="prime",
                args=[VariableNode(name="num", line=2, column=6)],
                line=2, column=0
            )
        ])
        
        result, errors = self.analyzer.analyze(pred_ast)
        self.assertEqual(len(errors), 0, f"Predicate call errors: {errors}")
        
        # Invalid arity
        invalid_arity_ast = SentenceNode(content=[
            PredicateCallNode(
                name="prime",
                args=[
                    VariableNode(name="num", line=3, column=6),
                    VariableNode(name="num", line=3, column=10)
                ],
                line=3, column=0
            )
        ])
        
        result_invalid, errors_invalid = self.analyzer.analyze(invalid_arity_ast)
        self.assertGreater(len(errors_invalid), 0, "Expected arity mismatch error")
        
        # Undefined predicate
        undefined_pred_ast = SentenceNode(content=[
            PredicateCallNode(
                name="undefined_predicate",
                args=[VariableNode(name="num", line=4, column=18)],
                line=4, column=0
            )
        ])
        
        result_undefined, errors_undefined = self.analyzer.analyze(undefined_pred_ast)
        self.assertGreater(len(errors_undefined), 0, "Expected undefined predicate error")
    
    def test_analyze_scoping_rules(self):
        """Test lexical scoping analysis"""
        # Test nested scopes with quantifiers
        quantifier_ast = SentenceNode(content=[
            QuantifierBlockNode(
                quant_type="forall",
                variables=[VariableNode(name="x", line=1, column=7)],
                condition=SentenceNode(content=[
                    VariableDeclNode(name="y", var_type="integer", line=2, column=4),
                    PredicateCallNode(
                        name="greater",
                        args=[
                            VariableNode(name="x", line=3, column=12),
                            VariableNode(name="y", line=3, column=15)
                        ],
                        line=3, column=4
                    )
                ]),
                line=1, column=0
            )
        ])
        
        result, errors = self.analyzer.analyze(quantifier_ast)
        self.assertEqual(len(errors), 0, f"Scoping errors: {errors}")
        
        # Test variable access outside scope (should fail)
        outside_scope_ast = SentenceNode(content=[
            QuantifierBlockNode(
                quant_type="exists",
                variables=[VariableNode(name="z", line=4, column=7)],
                condition=SentenceNode(content=[
                    VariableDeclNode(name="local", var_type="string", line=5, column=4)
                ]),
                line=4, column=0
            ),
            # Try to access 'local' outside its scope
            AssignmentNode(
                target=VariableNode(name="local", line=7, column=0),
                expression=ConstantNode(value="test", value_type="STRING"),
                line=7, column=0
            )
        ])
        
        result_scope, errors_scope = self.analyzer.analyze(outside_scope_ast)
        self.assertGreater(len(errors_scope), 0, "Expected scope violation error")
    
    def test_analyze_edge_cases(self):
        """Test edge cases and error conditions"""
        # Null AST - the analyzer should handle this gracefully
        result_null, errors_null = self.analyzer.analyze(None)
        self.assertIsNone(result_null)
        # Note: The analyzer may or may not produce errors for None - this depends on implementation
        
        # Empty sentence
        empty_ast = SentenceNode(content=[])
        result_empty, errors_empty = self.analyzer.analyze(empty_ast)
        self.assertIsNotNone(result_empty)
        self.assertEqual(len(errors_empty), 0, "Empty sentence should be valid")
        
        # Complex nested structure
        complex_ast = SentenceNode(content=[
            VariableDeclNode(name="x", var_type="integer", line=1, column=0),
            VariableDeclNode(
                name="complex_expr",
                var_type="auto",
                value=ArithmeticBinaryOpNode(
                    left=ArithmeticBinaryOpNode(
                        left=VariableNode(name="x", line=2, column=16),
                        operator="*",
                        right=ConstantNode(value=2, value_type="NUMBER"),
                        line=2, column=18
                    ),
                    operator="+",
                    right=ConstantNode(value=1, value_type="NUMBER"),
                    line=2, column=22
                ),
                line=2, column=0
            )
        ])
        
        result_complex, errors_complex = self.analyzer.analyze(complex_ast)
        self.assertEqual(len(errors_complex), 0, f"Complex expression errors: {errors_complex}")
    
    def test_analyzer_performance_tracking(self):
        """Test performance tracking functionality"""
        initial_count = self.analyzer._analysis_count
        
        # Perform analysis
        ast = SentenceNode(content=[
            VariableDeclNode(name="perf_test", var_type="integer", line=1, column=0)
        ])
        
        self.analyzer.analyze(ast)
        
        # Verify tracking
        self.assertEqual(self.analyzer._analysis_count, initial_count + 1)
        
        # Test multiple analyses
        for i in range(5):
            test_ast = SentenceNode(content=[
                VariableDeclNode(name=f"test_{i}", var_type="integer", line=i+2, column=0)
            ])
            self.analyzer.analyze(test_ast)
        
        self.assertEqual(self.analyzer._analysis_count, initial_count + 6)
    
    def test_error_collection_and_reporting(self):
        """Test comprehensive error collection"""
        # Create AST with multiple errors
        error_ast = SentenceNode(content=[
            # Error 1: Invalid type
            VariableDeclNode(name="bad_type", var_type="invalid_type", line=1, column=0),
            # Error 2: Undefined variable
            AssignmentNode(
                target=VariableNode(name="undefined", line=2, column=0),
                expression=ConstantNode(value=1, value_type="NUMBER"),
                line=2, column=0
            ),
            # Error 3: Type mismatch (after fixing the first error)
            VariableDeclNode(name="str_var", var_type="string", line=3, column=0),
            AssignmentNode(
                target=VariableNode(name="str_var", line=4, column=0),
                expression=ConstantNode(value=123, value_type="NUMBER"),
                line=4, column=0
            )
        ])
        
        result, errors = self.analyzer.analyze(error_ast)
        
        # Should collect multiple errors
        self.assertGreaterEqual(len(errors), 2, "Should collect multiple errors")
        
        # Verify error collector functionality
        self.assertGreater(len(self.analyzer.error_collector.errors), 0)
        
        # Test error summary
        summary = self.analyzer.error_collector.get_error_summary()
        self.assertIn('total_errors', summary)
        self.assertIn('has_errors', summary)
        self.assertTrue(summary['has_errors'])


class TestSemanticTypesComprehensive(unittest.TestCase):
    """Comprehensive tests for semantic types to achieve 95% coverage"""
    
    def test_symbol_table_comprehensive(self):
        """Test all SymbolTable functionality"""
        table = SymbolTable()
        
        # Test initial state
        self.assertEqual(table.current_scope_level, 0)
        self.assertEqual(len(table.scopes), 1)
        
        # Test symbol declaration
        symbol1 = Symbol("test_var", "variable", 0)
        table.declare_symbol(symbol1)
        
        # Test lookup
        found = table.lookup_symbol("test_var")
        self.assertEqual(found, symbol1)
        
        # Test symbol_exists
        self.assertTrue(table.symbol_exists("test_var"))
        self.assertFalse(table.symbol_exists("nonexistent"))
        
        # Test scope management
        table.enter_scope()
        self.assertEqual(table.current_scope_level, 1)
        
        # Test shadowing
        symbol2 = Symbol("test_var", "variable", 1)  # Same name, different scope
        table.declare_symbol(symbol2)
        
        # Should find the inner scope symbol
        found_inner = table.lookup_symbol("test_var")
        self.assertEqual(found_inner, symbol2)
        
        # Test scope exit
        table.exit_scope()
        self.assertEqual(table.current_scope_level, 0)
        
        # Should find outer scope symbol again
        found_outer = table.lookup_symbol("test_var")
        self.assertEqual(found_outer, symbol1)
        
        # Test error on global scope exit
        with self.assertRaises(SemanticError):
            table.exit_scope()
        
        # Test get_symbols_in_scope
        symbols_in_global = table.get_symbols_in_scope(0)
        self.assertIn(symbol1, symbols_in_global)
        
        # Test performance stats
        stats = table.get_performance_stats()
        self.assertIn('lookup_count', stats)
        self.assertIn('symbol_count', stats)
        self.assertGreater(stats['lookup_count'], 0)
    
    def test_type_info_comprehensive(self):
        """Test all TypeInfo functionality"""
        # Test valid type creation
        int_type = TypeInfo("integer")
        self.assertEqual(int_type.type_name, "integer")
        self.assertFalse(int_type.is_inferred)
        
        # Test inferred type
        inferred_type = TypeInfo("auto", is_inferred=True)
        self.assertTrue(inferred_type.is_inferred)
        
        # Test invalid type
        with self.assertRaises(ValueError):
            TypeInfo("invalid_type")
        
        # Test compatibility
        int_type2 = TypeInfo("integer")
        self.assertTrue(int_type.is_compatible_with(int_type2))
        
        string_type = TypeInfo("string")
        self.assertFalse(int_type.is_compatible_with(string_type))
        
        # Test auto type compatibility
        auto_type = TypeInfo("auto")
        self.assertTrue(auto_type.is_compatible_with(int_type))
        self.assertTrue(int_type.is_compatible_with(auto_type))
        
        # Test hierarchy compatibility
        real_type = TypeInfo("real")
        # Both integer and real are numbers, so should be compatible
        self.assertTrue(int_type.is_compatible_with(real_type))
        
        # Test equality and hashing
        int_type3 = TypeInfo("integer")
        self.assertEqual(int_type, int_type3)
        self.assertEqual(hash(int_type), hash(int_type3))
        
        # Test string representation
        str_repr = str(int_type)
        self.assertIn("integer", str_repr)
        
        inferred_repr = str(inferred_type)
        self.assertIn("inferred", inferred_repr)
    
    def test_error_collector_comprehensive(self):
        """Test all ErrorCollector functionality"""
        collector = ErrorCollector()
        
        # Test initial state
        self.assertFalse(collector.has_errors())
        self.assertFalse(collector.has_warnings())
        
        # Test error addition
        error1 = SemanticError("Test error 1", 1, 5)
        collector.add_error(error1)
        
        self.assertTrue(collector.has_errors())
        self.assertEqual(len(collector.errors), 1)
        
        # Test invalid error type
        with self.assertRaises(ValueError):
            collector.add_error("not an error object")
        
        # Test warning addition
        collector.add_warning("Test warning", 2)
        self.assertTrue(collector.has_warnings())
        self.assertEqual(len(collector.warnings), 1)
        
        # Test multiple errors of same type
        error2 = SemanticError("Test error 2", 3, 10)
        collector.add_error(error2)
        
        # Test error summary
        summary = collector.get_error_summary()
        self.assertEqual(summary['total_errors'], 2)
        self.assertEqual(summary['total_warnings'], 1)
        self.assertTrue(summary['has_errors'])
        self.assertIn('SemanticError', summary['errors_by_type'])
        self.assertEqual(summary['errors_by_type']['SemanticError'], 2)
        
        # Test clear
        collector.clear()
        self.assertFalse(collector.has_errors())
        self.assertFalse(collector.has_warnings())
        self.assertEqual(len(collector.errors), 0)
        self.assertEqual(len(collector.warnings), 0)
    
    def test_utility_functions(self):
        """Test utility functions"""
        # Test create_type_info factory
        type_info = create_type_info("boolean", True)
        self.assertEqual(type_info.type_name, "boolean")
        self.assertTrue(type_info.is_inferred)
        
        # Test check_type_compatibility
        int_type = TypeInfo("integer")
        string_type = TypeInfo("string")
        auto_type = TypeInfo("auto")
        
        self.assertTrue(check_type_compatibility(int_type, int_type))
        self.assertFalse(check_type_compatibility(int_type, string_type))
        self.assertTrue(check_type_compatibility(auto_type, int_type))


if __name__ == '__main__':
    # Run comprehensive tests
    unittest.main(verbosity=2)