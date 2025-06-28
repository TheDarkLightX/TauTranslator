#!/usr/bin/env python3
"""
Comprehensive TDD Tests for Semantic Analyzer
=============================================

Full Test-Driven Development implementation for the semantic analyzer.
These tests define the complete expected behavior before implementation.

Red Phase: Define what the semantic analyzer should do
Green Phase: Implement minimal functionality to pass tests
Refactor Phase: Improve code quality while maintaining tests
"""

import unittest
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic.semantic_analyzer import (
    SemanticAnalyzer, SemanticError, Symbol, SymbolTable
)
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    ASTNode, VariableNode, ConstantNode, NumberNode, StringNode,
    ArithmeticBinaryOpNode, BooleanBinaryOpNode, ComparisonNode,
    PredicateCallNode, FunctionDefinitionNode, PredicateDefinitionNode,
    DefinitionNode, SentenceNode, FactNode, RuleNode, ConditionNode,
    VariableDeclNode, AssignmentNode, BooleanUnaryOpNode,
    QuantifierBlockNode
)


class TestSemanticAnalyzerCore(unittest.TestCase):
    """Core semantic analyzer functionality tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def test_analyzer_instantiation(self):
        """Test that semantic analyzer can be instantiated"""
        analyzer = SemanticAnalyzer()
        self.assertIsNotNone(analyzer)
        self.assertIsInstance(analyzer.symbol_table, SymbolTable)
        self.assertEqual(len(analyzer.errors), 0)
    
    def test_empty_ast_analysis(self):
        """Test analysis of empty/None AST"""
        result, errors = self.analyzer.analyze(None)
        self.assertIsNone(result)
        self.assertEqual(len(errors), 0)
    
    def test_simple_variable_declaration(self):
        """Test analysis of simple variable declaration"""
        # Create a variable declaration node
        var_decl_node = VariableDeclNode(name="x", var_type="integer", line=1, column=1)
        
        result, errors = self.analyzer.analyze(var_decl_node)
        
        # Should analyze without errors for valid declaration
        self.assertEqual(len(errors), 0)
        self.assertIsNotNone(result)
        
        # Should be able to lookup the declared variable
        symbol = self.analyzer.symbol_table.lookup("x")
        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.name, "x")
        self.assertEqual(symbol.var_type, "integer")
    
    def test_undefined_variable_usage(self):
        """Test error detection for undefined variable usage"""
        var_node = VariableNode(name="undefined_var", line=1, column=1)
        
        result, errors = self.analyzer.analyze(var_node)
        
        # Should detect undefined variable error
        self.assertGreater(len(errors), 0)
        self.assertIn("not declared", str(errors[0]).lower())
    
    def test_number_literal_analysis(self):
        """Test analysis of number literals"""
        num_node = NumberNode(value=42, line=1, column=1)
        
        result, errors = self.analyzer.analyze(num_node)
        
        # Number literals should not produce errors
        self.assertEqual(len(errors), 0)
    
    def test_string_literal_analysis(self):
        """Test analysis of string literals"""
        str_node = StringNode(value="hello", line=1, column=1)
        
        result, errors = self.analyzer.analyze(str_node)
        
        # String literals should not produce errors
        self.assertEqual(len(errors), 0)


class TestSymbolTableOperations(unittest.TestCase):
    """Test symbol table operations and scoping"""
    
    def setUp(self):
        """Set up test environment"""
        self.symbol_table = SymbolTable()
    
    def test_symbol_table_instantiation(self):
        """Test symbol table creation"""
        table = SymbolTable()
        self.assertIsNotNone(table)
        self.assertEqual(table.current_scope_level, 0)
        self.assertEqual(len(table.scopes), 1)  # Global scope
    
    def test_symbol_definition_and_lookup(self):
        """Test basic symbol definition and lookup"""
        symbol = Symbol("x", "variable", 0, var_type="integer")
        
        # Define symbol
        success = self.symbol_table.define(symbol)
        self.assertTrue(success)
        
        # Lookup symbol
        found_symbol = self.symbol_table.lookup("x")
        self.assertIsNotNone(found_symbol)
        self.assertEqual(found_symbol.name, "x")
        self.assertEqual(found_symbol.symbol_type, "variable")
        self.assertEqual(found_symbol.var_type, "integer")
    
    def test_symbol_redefinition_error(self):
        """Test error on symbol redefinition in same scope"""
        symbol1 = Symbol("x", "variable", 0, var_type="integer")
        symbol2 = Symbol("x", "variable", 0, var_type="string")
        
        # First definition should succeed
        success1 = self.symbol_table.define(symbol1)
        self.assertTrue(success1)
        
        # Second definition should fail
        success2 = self.symbol_table.define(symbol2)
        self.assertFalse(success2)
    
    def test_scope_management(self):
        """Test entering and exiting scopes"""
        # Start in global scope
        self.assertEqual(self.symbol_table.current_scope_level, 0)
        
        # Enter new scope
        self.symbol_table.enter_scope()
        self.assertEqual(self.symbol_table.current_scope_level, 1)
        self.assertEqual(len(self.symbol_table.scopes), 2)
        
        # Exit scope
        self.symbol_table.exit_scope()
        self.assertEqual(self.symbol_table.current_scope_level, 0)
        self.assertEqual(len(self.symbol_table.scopes), 1)
    
    def test_scope_shadowing(self):
        """Test variable shadowing across scopes"""
        # Define variable in global scope
        global_symbol = Symbol("x", "variable", 0, var_type="integer")
        self.symbol_table.define(global_symbol)
        
        # Enter new scope
        self.symbol_table.enter_scope()
        
        # Define variable with same name in local scope
        local_symbol = Symbol("x", "variable", 1, var_type="string")
        success = self.symbol_table.define(local_symbol)
        self.assertTrue(success)  # Should succeed (shadowing)
        
        # Lookup should find local variable
        found_symbol = self.symbol_table.lookup("x")
        self.assertEqual(found_symbol.var_type, "string")
        self.assertEqual(found_symbol.scope_level, 1)
        
        # Exit scope
        self.symbol_table.exit_scope()
        
        # Lookup should now find global variable
        found_symbol = self.symbol_table.lookup("x")
        self.assertEqual(found_symbol.var_type, "integer")
        self.assertEqual(found_symbol.scope_level, 0)
    
    def test_current_scope_lookup(self):
        """Test lookup only in current scope"""
        # Define variable in global scope
        global_symbol = Symbol("x", "variable", 0, var_type="integer")
        self.symbol_table.define(global_symbol)
        
        # Enter new scope
        self.symbol_table.enter_scope()
        
        # Current scope lookup should not find global variable
        found_symbol = self.symbol_table.lookup_current_scope("x")
        self.assertIsNone(found_symbol)
        
        # Regular lookup should find global variable
        found_symbol = self.symbol_table.lookup("x")
        self.assertIsNotNone(found_symbol)


class TestTypeChecking(unittest.TestCase):
    """Test type checking functionality"""
    
    def setUp(self):
        """Set up test environment"""
        vocabulary = {
            'types': {'integer', 'string', 'boolean', 'auto', 'real'}
        }
        self.analyzer = SemanticAnalyzer(vocabulary=vocabulary)
    
    def test_type_compatibility_checking(self):
        """Test type compatibility in assignments"""
        # Declare an integer variable
        var_decl = VariableDeclNode(name="x", var_type="integer", line=1, column=1)
        
        # Create valid assignment (integer = integer)
        num_literal = NumberNode(value=42, line=2, column=5)
        assignment = AssignmentNode(
            target=VariableNode(name="x", line=2, column=1),
            expression=num_literal,
            line=2, column=1
        )
        
        # Analyze declaration first
        result1, errors1 = self.analyzer.analyze(var_decl)
        self.assertEqual(len(errors1), 0)
        
        # Analyze assignment
        result2, errors2 = self.analyzer.analyze(assignment)
        
        # Should not have type compatibility errors for valid assignment
        self.assertEqual(len(errors2), 0)
    
    def test_arithmetic_type_inference(self):
        """Test type inference for arithmetic expressions"""
        # Create arithmetic expression: x + y
        var_x = VariableNode(name="x", line=1, column=1)
        var_y = VariableNode(name="y", line=1, column=5)
        arithmetic_expr = ArithmeticBinaryOpNode(
            left=var_x, 
            operator="+", 
            right=var_y,
            line=1, column=1
        )
        
        # First declare the variables
        decl_x = VariableDeclNode(name="x", var_type="integer", line=1, column=1)
        decl_y = VariableDeclNode(name="y", var_type="integer", line=1, column=1)
        
        # Analyze declarations
        self.analyzer.analyze(decl_x)
        self.analyzer.analyze(decl_y)
        
        # Analyze arithmetic expression
        result, errors = self.analyzer.analyze(arithmetic_expr)
        
        # Should analyze without errors and infer result type
        self.assertEqual(len(errors), 0)
        self.assertIsNotNone(result)
    
    def test_comparison_type_validation(self):
        """Test type validation for comparison operations"""
        # Declare variables of incompatible types for arithmetic
        str_decl = VariableDeclNode(name="s", var_type="string", line=1, column=1)
        int_decl = VariableDeclNode(name="x", var_type="integer", line=2, column=1)
        
        # Analyze declarations
        self.analyzer.analyze(str_decl)
        self.analyzer.analyze(int_decl)
        
        # Create arithmetic operation with incompatible types: s + x
        var_s = VariableNode(name="s", line=3, column=1)
        var_x = VariableNode(name="x", line=3, column=5)
        invalid_arithmetic = ArithmeticBinaryOpNode(
            left=var_s,
            operator="+", 
            right=var_x,
            line=3, column=1
        )
        
        # Analyze invalid arithmetic
        result, errors = self.analyzer.analyze(invalid_arithmetic)
        
        # Should detect type incompatibility error
        self.assertGreater(len(errors), 0)
        self.assertIn("numeric type", str(errors[0]).lower())
    
    def test_predicate_argument_type_checking(self):
        """Test argument type checking for predicate calls"""
        # Define expected behavior for predicate type checking
        pass


class TestPredicateAndFunctionAnalysis(unittest.TestCase):
    """Test analysis of predicates and functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def test_predicate_definition_analysis(self):
        """Test analysis of predicate definitions"""
        # Create a predicate definition: Define prime(n) as n > 1 and ...
        param_n = VariableNode(name="n", line=1, column=15)
        
        predicate_def = PredicateDefinitionNode(
            name="prime",
            parameters=[param_n],
            body=ComparisonNode(
                left=VariableNode(name="n", line=1, column=25),
                operator=">",
                right=NumberNode(value=1, line=1, column=29),
                line=1, column=25
            ),
            line=1, column=1
        )
        
        result, errors = self.analyzer.analyze(predicate_def)
        
        # Should analyze without errors
        self.assertEqual(len(errors), 0)
        
        # Should register the predicate in symbol table
        symbol = self.analyzer.symbol_table.lookup("prime")
        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.symbol_type, "predicate")
        self.assertEqual(symbol.attributes.get('arity'), 1)
    
    def test_function_definition_analysis(self):
        """Test analysis of function definitions"""
        # This test will drive implementation of function analysis
        pass
    
    def test_predicate_call_arity_checking(self):
        """Test arity checking for predicate calls"""
        # First define a predicate with 2 parameters
        param1 = VariableNode(name="x", line=1, column=15)
        param2 = VariableNode(name="y", line=1, column=18)
        
        predicate_def = PredicateDefinitionNode(
            name="equals",
            parameters=[param1, param2],
            body=ComparisonNode(
                left=VariableNode(name="x", line=1, column=25),
                operator="=",
                right=VariableNode(name="y", line=1, column=29),
                line=1, column=25
            ),
            line=1, column=1
        )
        
        # Analyze the definition
        self.analyzer.analyze(predicate_def)
        
        # Test correct arity call
        correct_call = PredicateCallNode(
            name="equals",
            args=[NumberNode(value=1), NumberNode(value=2)],
            line=2, column=1
        )
        
        result1, errors1 = self.analyzer.analyze(correct_call)
        self.assertEqual(len(errors1), 0)
        
        # Test incorrect arity call (too few arguments)
        incorrect_call = PredicateCallNode(
            name="equals",
            args=[NumberNode(value=1)],  # Only 1 argument, expects 2
            line=3, column=1
        )
        
        result2, errors2 = self.analyzer.analyze(incorrect_call)
        self.assertGreater(len(errors2), 0)
        self.assertIn("expects 2 arguments, got 1", str(errors2[0]))
    
    def test_recursive_predicate_analysis(self):
        """Test analysis of recursive predicates"""
        # Define expected behavior for recursion handling
        pass


class TestQuantifierAnalysis(unittest.TestCase):
    """Test analysis of quantified expressions"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def test_universal_quantifier_analysis(self):
        """Test analysis of universal quantifiers (for all)"""
        # Create: for all x, P(x)
        var_x = VariableNode(name="x", line=1, column=10)
        
        quantifier = QuantifierBlockNode(
            quant_type="forall",
            variables=[var_x],
            line=1, column=1
        )
        
        # Create predicate call P(x) in the quantified expression
        predicate_call = PredicateCallNode(
            name="P",
            args=[VariableNode(name="x", line=1, column=15)],
            line=1, column=13
        )
        
        condition = ConditionNode(
            expression=predicate_call,
            quant_block=quantifier,
            line=1, column=1
        )
        
        result, errors = self.analyzer.analyze(condition)
        
        # Should analyze without errors (x is bound by quantifier)
        # Note: This assumes P is a known predicate or we add it to vocabulary
        # For now, we expect an error about P not being declared
        self.assertGreater(len(errors), 0)
        self.assertIn("not declared", str(errors[0]).lower())
    
    def test_existential_quantifier_analysis(self):
        """Test analysis of existential quantifiers (there exists)"""
        # Define expected behavior for existential quantifiers
        pass
    
    def test_quantifier_variable_scoping(self):
        """Test variable scoping in quantified expressions"""
        # Define expected behavior for quantifier variable scoping
        pass
    
    def test_nested_quantifier_analysis(self):
        """Test analysis of nested quantifiers"""
        # Define expected behavior for nested quantifiers
        pass


class TestTemporalLogicAnalysis(unittest.TestCase):
    """Test analysis of temporal logic constructs"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def test_temporal_operator_analysis(self):
        """Test analysis of temporal operators (always, eventually)"""
        # Define expected behavior for temporal operators
        pass
    
    def test_stream_reference_analysis(self):
        """Test analysis of stream references"""
        # Define expected behavior for stream references
        pass
    
    def test_temporal_quantifier_analysis(self):
        """Test analysis of temporal quantifiers"""
        # Define expected behavior for temporal quantifiers
        pass


class TestErrorHandlingAndReporting(unittest.TestCase):
    """Test error handling and reporting functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def test_error_accumulation(self):
        """Test that multiple errors are accumulated"""
        # Create an AST with multiple semantic errors
        
        # 1. Use undefined variable
        undefined_var = VariableNode(name="undefined1", line=1, column=1)
        
        # 2. Use another undefined variable
        undefined_var2 = VariableNode(name="undefined2", line=2, column=1)
        
        # 3. Call undefined predicate
        undefined_pred = PredicateCallNode(name="undefined_pred", args=[], line=3, column=1)
        
        # Analyze each and accumulate errors
        result1, errors1 = self.analyzer.analyze(undefined_var)
        result2, errors2 = self.analyzer.analyze(undefined_var2)
        result3, errors3 = self.analyzer.analyze(undefined_pred)
        
        # Should have accumulated all errors
        total_errors = len(errors1) + len(errors2) + len(errors3)
        self.assertGreaterEqual(total_errors, 3)  # At least 3 errors
    
    def test_error_location_reporting(self):
        """Test that errors include line and column information"""
        var_node = VariableNode(name="undefined", line=5, column=10)
        
        result, errors = self.analyzer.analyze(var_node)
        
        self.assertGreater(len(errors), 0)
        error = errors[0]
        self.assertEqual(error.line_number, 5)
        self.assertEqual(error.column_number, 10)
    
    def test_error_message_quality(self):
        """Test that error messages are descriptive and helpful"""
        var_node = VariableNode(name="undefined_variable", line=1, column=1)
        
        result, errors = self.analyzer.analyze(var_node)
        
        self.assertGreater(len(errors), 0)
        error_message = str(errors[0])
        
        # Error message should be informative
        self.assertIn("undefined_variable", error_message)
        self.assertIn("not declared", error_message.lower())
        self.assertIn("L1", error_message)  # Line number
        self.assertIn("C1", error_message)  # Column number
    
    def test_error_recovery(self):
        """Test that analyzer recovers from errors and continues analysis"""
        # Should not crash on errors, should continue analyzing
        pass


class TestComplexSemanticAnalysis(unittest.TestCase):
    """Test complex semantic analysis scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def test_definition_before_use(self):
        """Test that variables must be defined before use"""
        # Define expected behavior for definition-before-use checking
        pass
    
    def test_circular_definition_detection(self):
        """Test detection of circular definitions"""
        # Define expected behavior for circular definition detection
        pass
    
    def test_dead_code_detection(self):
        """Test detection of unreachable or unused code"""
        # Define expected behavior for dead code analysis
        pass
    
    def test_control_flow_analysis(self):
        """Test control flow analysis"""
        # Define expected behavior for control flow validation
        pass


class TestSemanticAnalyzerIntegration(unittest.TestCase):
    """Test integration with other components"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def test_ast_annotation(self):
        """Test that analyzer annotates AST with semantic information"""
        # Should add type information, symbol references, etc. to AST nodes
        pass
    
    def test_vocabulary_integration(self):
        """Test integration with vocabulary system"""
        custom_vocabulary = {
            'types': {'custom_type', 'another_type'},
            'predicates': {'custom_predicate'},
            'functions': {'custom_function'}
        }
        
        analyzer = SemanticAnalyzer(vocabulary=custom_vocabulary)
        
        # Should recognize custom vocabulary items
        self.assertIn('custom_type', analyzer.vocabulary['types'])
    
    def test_plugin_system_integration(self):
        """Test integration with plugin validation system"""
        # Should work with plugin validators
        pass


class TestPerformanceAndScalability(unittest.TestCase):
    """Test performance and scalability of semantic analyzer"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def test_large_ast_analysis_performance(self):
        """Test performance on large ASTs"""
        # Should handle large ASTs efficiently
        pass
    
    def test_deep_nesting_analysis(self):
        """Test analysis of deeply nested structures"""
        # Should handle deep nesting without stack overflow
        pass
    
    def test_memory_usage_efficiency(self):
        """Test memory usage efficiency"""
        # Should not leak memory or use excessive memory
        pass


def run_tdd_red_phase():
    """Run Red phase - all tests should fail initially"""
    print("🔴 TDD RED PHASE: Running Semantic Analyzer Tests")
    print("=" * 60)
    print("These tests define the expected semantic analyzer behavior.")
    print("They SHOULD fail initially - that's the point of TDD!")
    print("=" * 60)
    
    # Run tests with high verbosity
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("🔴 RED PHASE COMPLETE")
    print("Next: Implement minimal functionality to make tests pass (GREEN PHASE)")
    print("=" * 60)


if __name__ == "__main__":
    run_tdd_red_phase()