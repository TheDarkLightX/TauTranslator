#!/usr/bin/env python3
"""
Refactoring Verification Script
==============================

Verifies that the refactored semantic analyzer still works correctly.
Tests key functionality without requiring external dependencies.

Author: DarklightX (Dana Edwards)
"""

import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from tau_translator_omega.core_engine.semantic_analyzer import (
        SemanticAnalyzer, SemanticError, Symbol, SymbolTable
    )
    from tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
        VariableDeclNode, VariableNode, ConstantNode, 
        PredicateCallNode, ArithmeticBinaryOpNode
    )
    print("✅ Successfully imported refactored modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_symbol_table():
    """Test symbol table functionality"""
    print("\n🧪 Testing SymbolTable...")
    
    symbol_table = SymbolTable()
    
    # Test basic symbol definition
    symbol = Symbol("x", "variable", 0, var_type="integer")
    assert symbol_table.define(symbol), "Should define symbol successfully"
    
    # Test symbol lookup
    found = symbol_table.lookup("x")
    assert found is not None, "Should find defined symbol"
    assert found.name == "x", "Should return correct symbol"
    
    # Test redefinition in same scope
    duplicate = Symbol("x", "variable", 0, var_type="string")
    assert not symbol_table.define(duplicate), "Should reject redefinition"
    
    # Test nested scopes
    symbol_table.enter_scope()
    nested_symbol = Symbol("y", "variable", 1, var_type="boolean")
    assert symbol_table.define(nested_symbol), "Should define in nested scope"
    
    # Should find both symbols
    assert symbol_table.lookup("x") is not None, "Should find outer symbol"
    assert symbol_table.lookup("y") is not None, "Should find inner symbol"
    
    symbol_table.exit_scope()
    
    # Should not find inner symbol after exiting scope
    assert symbol_table.lookup("y") is None, "Should not find inner symbol"
    assert symbol_table.lookup("x") is not None, "Should still find outer symbol"
    
    print("  ✅ SymbolTable tests passed")


def test_semantic_analyzer_basic():
    """Test basic semantic analyzer functionality"""
    print("\n🧪 Testing SemanticAnalyzer...")
    
    analyzer = SemanticAnalyzer()
    
    # Test variable declaration (integer type should not require initializer)
    var_decl = VariableDeclNode()
    var_decl.name = "x"
    var_decl.var_type = "integer"
    var_decl.value = None
    var_decl.line = 1
    var_decl.column = 1
    
    analyzed_node, errors = analyzer.analyze(var_decl)
    print(f"  Debug: errors = {[e.message for e in errors]}")
    assert len(errors) == 0, f"Should have no errors, got: {errors}"
    
    # Test variable usage after declaration
    analyzer2 = SemanticAnalyzer()
    var_decl2 = VariableDeclNode()
    var_decl2.name = "x"
    var_decl2.var_type = "integer"
    var_decl2.value = None
    analyzer2._visit_VariableDeclNode(var_decl2)
    
    var_use = VariableNode()
    var_use.name = "x"
    analyzer2._visit_VariableNode(var_use)
    assert len(analyzer2.errors) == 0, "Should have no errors for valid variable use"
    
    # Test undeclared variable
    analyzer3 = SemanticAnalyzer()
    undeclared = VariableNode()
    undeclared.name = "undefined_var"
    analyzer3._visit_VariableNode(undeclared)
    assert len(analyzer3.errors) == 1, "Should have error for undeclared variable"
    assert "not declared" in analyzer3.errors[0].message, "Should have appropriate error message"
    
    print("  ✅ SemanticAnalyzer basic tests passed")


def test_refactored_methods():
    """Test that refactored methods work correctly"""
    print("\n🧪 Testing refactored methods...")
    
    analyzer = SemanticAnalyzer()
    
    # Test _validate_variable_type
    valid_node = VariableDeclNode()
    valid_node.name = "x"
    valid_node.var_type = "integer"
    analyzer._validate_variable_type(valid_node)
    assert len(analyzer.errors) == 0, "Should accept valid type"
    
    invalid_node = VariableDeclNode()
    invalid_node.name = "y"
    invalid_node.var_type = "invalid_type"
    analyzer._validate_variable_type(invalid_node)
    assert len(analyzer.errors) == 1, "Should reject invalid type"
    
    # Test _check_variable_redeclaration
    analyzer2 = SemanticAnalyzer()
    new_node = VariableDeclNode()
    new_node.name = "z"
    new_node.var_type = "integer"
    result = analyzer2._check_variable_redeclaration(new_node)
    assert not result, "Should not detect redeclaration for new variable"
    
    # Define the variable first
    analyzer2._define_variable_symbol(new_node)
    
    # Now check for redeclaration
    duplicate_node = VariableDeclNode()
    duplicate_node.name = "z"
    duplicate_node.var_type = "string"
    result = analyzer2._check_variable_redeclaration(duplicate_node)
    assert result, "Should detect redeclaration"
    
    print("  ✅ Refactored methods tests passed")


def test_type_inference():
    """Test type inference functionality"""
    print("\n🧪 Testing type inference...")
    
    analyzer = SemanticAnalyzer()
    
    # Test auto type with initializer  
    const_node = ConstantNode()
    const_node.value = 42
    const_node.value_type = "NUMBER"
    
    auto_node = VariableDeclNode()
    auto_node.name = "x"
    auto_node.var_type = "auto"
    auto_node.value = const_node
    
    analyzer._visit_VariableDeclNode(auto_node)
    
    # Should have defined the variable
    symbol = analyzer.symbol_table.lookup("x")
    assert symbol is not None, "Should have defined auto variable"
    
    print("  ✅ Type inference tests passed")


def test_arithmetic_validation():
    """Test arithmetic operation validation"""
    print("\n🧪 Testing arithmetic validation...")
    
    analyzer = SemanticAnalyzer()
    
    # Define two integer variables
    x_decl = VariableDeclNode()
    x_decl.name = "x"
    x_decl.var_type = "integer"
    
    y_decl = VariableDeclNode()
    y_decl.name = "y"
    y_decl.var_type = "integer"
    
    analyzer._visit_VariableDeclNode(x_decl)
    analyzer._visit_VariableDeclNode(y_decl)
    
    # Test arithmetic operation
    x_var = VariableNode()
    x_var.name = "x"
    
    y_var = VariableNode()
    y_var.name = "y"
    arith_op = ArithmeticBinaryOpNode(x_var, "+", y_var)
    
    analyzer._visit_ArithmeticBinaryOpNode(arith_op)
    
    # Should have no errors for valid arithmetic
    assert len(analyzer.errors) == 0, f"Should have no arithmetic errors, got: {[e.message for e in analyzer.errors]}"
    
    print("  ✅ Arithmetic validation tests passed")


def main():
    """Run all verification tests"""
    print("🔧 Verifying Refactored Semantic Analyzer")
    print("=" * 50)
    
    try:
        test_symbol_table()
        test_semantic_analyzer_basic()
        test_refactored_methods()
        test_type_inference()
        test_arithmetic_validation()
        
        print("\n" + "=" * 50)
        print("✅ All verification tests passed!")
        print("🎉 Refactoring successful - semantic analyzer working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        print("\n🔍 Stack trace:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)