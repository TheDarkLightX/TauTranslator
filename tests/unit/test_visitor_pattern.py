"""
Test script to verify visitor pattern implementation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.tau_translator_omega.core_engine.semantic_types import SymbolTable, Symbol
from src.tau_translator_omega.core_engine.semantic_analyzer_core import ExpressionTypeResolver
from src.tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
    ConstantNode, NumberNode, StringNode, VariableNode,
    ArithmeticBinaryOpNode, ComparisonNode
)


def test_visitor_pattern():
    """Test that visitor pattern produces same results as isinstance checks."""
    
    # Create symbol table and add a variable
    symbol_table = SymbolTable()
    symbol_table.declare_symbol(Symbol('x', 'variable', 0, var_type='integer'))
    
    # Test with instanceof pattern (default)
    resolver_isinstance = ExpressionTypeResolver(symbol_table, use_visitor_pattern=False)
    
    # Test with visitor pattern
    resolver_visitor = ExpressionTypeResolver(symbol_table, use_visitor_pattern=True)
    
    # Test cases
    test_nodes = [
        # Basic literal nodes
        ConstantNode(value=42, value_type='NUMBER'),
        ConstantNode(value='hello', value_type='STRING'),
        ConstantNode(value=True, value_type='BOOLEAN'),
        NumberNode(value=123),
        StringNode(value='test'),
        
        # Variable reference
        VariableNode(name='x'),
        
        # Arithmetic expression
        ArithmeticBinaryOpNode(
            left=NumberNode(value=1),
            right=NumberNode(value=2),
            operator='+'
        ),
        
        # Comparison
        ComparisonNode(
            left=NumberNode(value=1),
            right=NumberNode(value=2),
            operator='<'
        ),
    ]
    
    print("Testing visitor pattern vs isinstance pattern:")
    print("-" * 50)
    
    all_passed = True
    for i, node in enumerate(test_nodes):
        type_isinstance = resolver_isinstance.get_expression_type(node)
        type_visitor = resolver_visitor.get_expression_type(node)
        
        passed = type_isinstance == type_visitor
        all_passed &= passed
        
        status = "✓" if passed else "✗"
        print(f"{status} Test {i+1}: {type(node).__name__}")
        print(f"   isinstance: {type_isinstance}")
        print(f"   visitor:    {type_visitor}")
        
        if not passed:
            print(f"   MISMATCH!")
    
    print("-" * 50)
    print(f"Overall: {'PASSED' if all_passed else 'FAILED'}")
    
    # Performance comparison
    print("\nPerformance Stats:")
    print(f"isinstance resolver: {resolver_isinstance.get_cache_stats()}")
    print(f"visitor resolver: {resolver_visitor.get_cache_stats()}")
    
    return all_passed


if __name__ == "__main__":
    success = test_visitor_pattern()
    sys.exit(0 if success else 1)