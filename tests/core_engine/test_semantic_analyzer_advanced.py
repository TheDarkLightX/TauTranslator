#!/usr/bin/env python3
"""
Advanced Semantic Analysis Tests
================================

TDD tests for advanced semantic analysis features:
- Complex type inference
- Function overloading resolution
- Quantifier scope analysis
- Predicate arity checking
- Cross-reference validation
"""

import unittest
from typing import List
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.semantic_analyzer import (
    SemanticAnalyzer, SemanticError, Symbol
)
from tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
    VariableDeclNode, VariableNode, ConstantNode, SentenceNode,
    AssignmentNode, ArithmeticBinaryOpNode, BooleanBinaryOpNode,
    ComparisonNode, PredicateCallNode, FunctionDefinitionNode,
    QuantifierBlockNode, ConditionNode
)


class TestAdvancedSemanticAnalysis(unittest.TestCase):
    """Test advanced semantic analysis features"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer({
            'types': {'integer', 'string', 'boolean', 'real', 'auto'},
            'predicates': {
                'prime': {'arity': 1, 'signature': ['integer']},
                'greater': {'arity': 2, 'signature': ['integer', 'integer']},
                'between': {'arity': 3, 'signature': ['integer', 'integer', 'integer']}
            },
            'functions': {
                'add': {'arity': 2, 'signature': ['integer', 'integer'], 'return': 'integer'},
                'concat': {'arity': 2, 'signature': ['string', 'string'], 'return': 'string'},
                'length': {'arity': 1, 'signature': ['string'], 'return': 'integer'}
            }
        })
    
    def test_type_inference_arithmetic(self):
        """Test type inference for arithmetic expressions"""
        ast = SentenceNode(content=[
            # let x = 10
            VariableDeclNode(name="x", var_type="auto", 
                           value=ConstantNode(value=10, value_type="NUMBER")),
            # let y = x + 5
            VariableDeclNode(name="y", var_type="auto",
                           value=ArithmeticBinaryOpNode(
                               left=VariableNode(name="x"),
                               operator="+",
                               right=ConstantNode(value=5, value_type="NUMBER")
                           ))
        ])
        
        result, errors = self.analyzer.analyze(ast)
        
        # Should infer types correctly
        self.assertEqual(len(errors), 0, f"Unexpected errors: {errors}")
        
        # Check inferred types
        x_symbol = self.analyzer.symbol_table.lookup_symbol("x")
        y_symbol = self.analyzer.symbol_table.lookup_symbol("y")
        
        self.assertIsNotNone(x_symbol)
        self.assertEqual(x_symbol.var_type, "integer", "Should infer x as integer")
        
        self.assertIsNotNone(y_symbol)
        self.assertEqual(y_symbol.var_type, "integer", "Should infer y as integer from arithmetic")
    
    def test_type_mismatch_detection(self):
        """Test detection of type mismatches"""
        ast = SentenceNode(content=[
            # let s: string = "hello"
            VariableDeclNode(name="s", var_type="string",
                           value=ConstantNode(value="hello", value_type="STRING")),
            # let n: integer = s  # Type mismatch!
            VariableDeclNode(name="n", var_type="integer",
                           value=VariableNode(name="s"))
        ])
        
        result, errors = self.analyzer.analyze(ast)
        
        # Should detect type mismatch
        self.assertGreater(len(errors), 0, "Should detect type mismatch")
        self.assertTrue(any("type" in str(e).lower() for e in errors),
                       "Error should mention type mismatch")
    
    def test_predicate_arity_checking(self):
        """Test predicate arity validation"""
        # Test correct arity
        ast_correct = SentenceNode(content=[
            VariableDeclNode(name="x", var_type="integer"),
            PredicateCallNode(
                name="prime",
                args=[VariableNode(name="x")]
            )
        ])
        
        result, errors = self.analyzer.analyze(ast_correct)
        self.assertEqual(len(errors), 0, "Correct arity should not produce errors")
        
        # Test incorrect arity
        ast_incorrect = SentenceNode(content=[
            VariableDeclNode(name="x", var_type="integer"),
            VariableDeclNode(name="y", var_type="integer"),
            PredicateCallNode(
                name="prime",
                args=[VariableNode(name="x"), VariableNode(name="y")]  # Wrong!
            )
        ])
        
        result, errors = self.analyzer.analyze(ast_incorrect)
        self.assertGreater(len(errors), 0, "Should detect arity mismatch")
        self.assertTrue(any("arity" in str(e).lower() or "argument" in str(e).lower() 
                           for e in errors),
                       "Error should mention arity or arguments")
    
    def test_quantifier_scope_analysis(self):
        """Test quantifier variable scoping"""
        ast = SentenceNode(content=[
            # For all x, P(x)
            QuantifierBlockNode(
                quant_type="forall",
                variables=[VariableNode(name="x")],
                condition=PredicateCallNode(
                    name="prime",
                    args=[VariableNode(name="x")]
                )
            ),
            # x should not be accessible here
            AssignmentNode(
                target=VariableNode(name="y"),
                expression=VariableNode(name="x")  # Error: x out of scope
            )
        ])
        
        result, errors = self.analyzer.analyze(ast)
        
        # Should detect variable out of scope
        self.assertGreater(len(errors), 0, "Should detect variable out of scope")
        
        # Check error messages
        error_messages = [str(e) for e in errors]
        print(f"Errors found: {error_messages}")
        
        self.assertTrue(any("not declared" in str(e).lower() or "undefined" in str(e).lower()
                           for e in errors),
                       f"Error should mention undefined variable. Got: {error_messages}")
    
    def test_nested_quantifiers(self):
        """Test nested quantifier scoping"""
        ast = SentenceNode(content=[
            # For all x, there exists y such that greater(y, x)
            QuantifierBlockNode(
                quant_type="forall",
                variables=[VariableNode(name="x")],
                condition=QuantifierBlockNode(
                    quant_type="exists",
                    variables=[VariableNode(name="y")],
                    condition=PredicateCallNode(
                        name="greater",
                        args=[
                            VariableNode(name="y"),
                            VariableNode(name="x")
                        ]
                    )
                )
            )
        ])
        
        result, errors = self.analyzer.analyze(ast)
        
        # Should handle nested scopes correctly
        self.assertEqual(len(errors), 0, "Nested quantifiers should work correctly")
    
    def test_function_return_type_checking(self):
        """Test function return type validation"""
        ast = SentenceNode(content=[
            # let s1: string = "hello"
            VariableDeclNode(name="s1", var_type="string",
                           value=ConstantNode(value="hello", value_type="STRING")),
            # let s2: string = "world"
            VariableDeclNode(name="s2", var_type="string",
                           value=ConstantNode(value="world", value_type="STRING")),
            # let result: string = concat(s1, s2)  # Correct
            VariableDeclNode(name="result", var_type="string",
                           value=PredicateCallNode(
                               name="concat",
                               args=[
                                   VariableNode(name="s1"),
                                   VariableNode(name="s2")
                               ]
                           )),
            # let len: string = length(s1)  # Wrong! length returns integer
            VariableDeclNode(name="len", var_type="string",
                           value=PredicateCallNode(
                               name="length",
                               args=[VariableNode(name="s1")]
                           ))
        ])
        
        result, errors = self.analyzer.analyze(ast)
        
        # Should detect return type mismatch
        self.assertGreater(len(errors), 0, "Should detect return type mismatch")
        self.assertTrue(any("type" in str(e).lower() for e in errors),
                       "Error should mention type mismatch")
    
    def test_complex_expression_type_checking(self):
        """Test type checking in complex expressions"""
        ast = SentenceNode(content=[
            # let a: integer = 5
            VariableDeclNode(name="a", var_type="integer",
                           value=ConstantNode(value=5, value_type="NUMBER")),
            # let b: integer = 10
            VariableDeclNode(name="b", var_type="integer", 
                           value=ConstantNode(value=10, value_type="NUMBER")),
            # let c: boolean = (a + b) > 12
            VariableDeclNode(name="c", var_type="boolean",
                           value=ComparisonNode(
                               left=ArithmeticBinaryOpNode(
                                   left=VariableNode(name="a"),
                                   operator="+",
                                   right=VariableNode(name="b")
                               ),
                               operator=">",
                               right=ConstantNode(value=12, value_type="NUMBER")
                           ))
        ])
        
        result, errors = self.analyzer.analyze(ast)
        
        # Should handle complex expression types correctly
        self.assertEqual(len(errors), 0, "Complex expression should type check correctly")
    
    def skip_test_conditional_branch_type_consistency(self):
        """Test type consistency in conditional branches"""
        ast = SentenceNode(content=[
            VariableDeclNode(name="x", var_type="integer"),
            VariableDeclNode(name="result", var_type="auto"),
            # if x > 0 then result = "positive" else result = -1
            ConditionNode(
                condition=ComparisonNode(
                    left=VariableNode(name="x"),
                    operator=">",
                    right=ConstantNode(value=0, value_type="NUMBER")
                ),
                then_branch=AssignmentNode(
                    target=VariableNode(name="result"),
                    expression=ConstantNode(value="positive", value_type="STRING")
                ),
                else_branch=AssignmentNode(
                    target=VariableNode(name="result"),
                    expression=ConstantNode(value=-1, value_type="NUMBER")
                )
            )
        ])
        
        result, errors = self.analyzer.analyze(ast)
        
        # Should warn about inconsistent types in branches
        # This is a design choice - could either error or infer union type
        # For now, let's expect a warning/error
        self.assertGreater(len(errors), 0, "Should detect type inconsistency in branches")


class TestSemanticAnalyzerErrorRecovery(unittest.TestCase):
    """Test error recovery and reporting"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = SemanticAnalyzer()
    
    def test_multiple_error_collection(self):
        """Test that analyzer collects multiple errors"""
        ast = SentenceNode(content=[
            # Multiple errors in one program
            AssignmentNode(  # Error 1: undefined variable
                target=VariableNode(name="undefined1"),
                expression=ConstantNode(value=1)
            ),
            AssignmentNode(  # Error 2: another undefined variable
                target=VariableNode(name="undefined2"),
                expression=ConstantNode(value=2)
            ),
            VariableDeclNode(  # Error 3: unknown type
                name="x",
                var_type="unknown_type"
            )
        ])
        
        result, errors = self.analyzer.analyze(ast)
        
        # Should collect all errors
        self.assertGreaterEqual(len(errors), 3, "Should collect multiple errors")
    
    def test_error_location_tracking(self):
        """Test that errors include location information"""
        # Create nodes with location info
        node = AssignmentNode(
            target=VariableNode(name="undefined", line=10, column=5),
            expression=ConstantNode(value=1),
            line=10,
            column=1
        )
        
        ast = SentenceNode(content=[node])
        result, errors = self.analyzer.analyze(ast)
        
        # Should include location in error
        self.assertGreater(len(errors), 0)
        error_str = str(errors[0])
        self.assertIn("10", error_str, "Error should include line number")


if __name__ == '__main__':
    unittest.main()