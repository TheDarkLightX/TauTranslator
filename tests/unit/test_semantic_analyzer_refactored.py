"""
Unit tests for refactored semantic analyzer.

Tests the refactored semantic analyzer functionality following IDP principles.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from dataclasses import dataclass
from typing import Optional, List

from backend.unified.domain.semantic_analyzer_refactored import SemanticAnalyzerRefactored
from backend.unified.domain.semantic_types import (
    SemanticError, Symbol, SymbolTable, TypeInfo, ErrorCollector
)


# Mock AST nodes for testing
@dataclass
class MockNode:
    """Base mock AST node."""
    line: Optional[int] = 1
    column: Optional[int] = 1


@dataclass
class SentenceNode(MockNode):
    """Mock sentence node."""
    content: List = None
    
    def __post_init__(self):
        if self.content is None:
            self.content = []


@dataclass
class VariableNode(MockNode):
    """Mock variable reference node."""
    name: str = "test_var"


@dataclass
class VariableDeclNode(MockNode):
    """Mock variable declaration node."""
    name: str = "test_var"
    var_type: str = "integer"
    value: Optional[MockNode] = None


@dataclass
class ConstantNode(MockNode):
    """Mock constant node."""
    value: int = 42


@dataclass
class AssignmentNode(MockNode):
    """Mock assignment node."""
    target: VariableNode = None
    expression: MockNode = None
    
    def __post_init__(self):
        if self.target is None:
            self.target = VariableNode()
        if self.expression is None:
            self.expression = ConstantNode()


@dataclass
class QuantifierBlockNode(MockNode):
    """Mock quantifier block node."""
    variables: List = None
    condition: Optional[MockNode] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = ["x", "y"]


@dataclass
class ConditionNode(MockNode):
    """Mock condition node."""
    quantifier_block: Optional[QuantifierBlockNode] = None
    expression: Optional[MockNode] = None


@dataclass
class PredicateCallNode(MockNode):
    """Mock predicate call node."""
    name: str = "is_valid"
    arguments: List = None
    
    def __post_init__(self):
        if self.arguments is None:
            self.arguments = []


@dataclass
class ArithmeticBinaryOpNode(MockNode):
    """Mock arithmetic binary operation node."""
    left: MockNode = None
    right: MockNode = None
    operator: str = "+"
    
    def __post_init__(self):
        if self.left is None:
            self.left = ConstantNode(5)
        if self.right is None:
            self.right = ConstantNode(3)


class TestSemanticAnalyzerRefactored:
    """Test suite for refactored semantic analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance with test vocabulary."""
        vocabulary = {
            'types': {'integer', 'string', 'boolean', 'auto'},
            'predicates': {
                'is_valid': {'arity': 1, 'signature': ['auto']},
                'equals': {'arity': 2, 'signature': ['auto', 'auto']}
            },
            'functions': {
                'max': {'arity': 2, 'signature': ['number', 'number'], 'return': 'number'}
            }
        }
        return SemanticAnalyzerRefactored(vocabulary)
    
    def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer._analysis_count == 0
        assert analyzer.symbol_table is not None
        assert analyzer.error_collector is not None
        assert analyzer.vocabulary is not None
    
    def test_analyze_empty_node(self, analyzer):
        """Test analyzing None node."""
        node, errors = analyzer.analyze(None)
        
        assert node is None
        assert errors == []
        assert analyzer._analysis_count == 1
    
    def test_analyze_sentence_node(self, analyzer):
        """Test analyzing sentence node."""
        sentence = SentenceNode(content=[
            VariableDeclNode(name="x", var_type="integer"),
            AssignmentNode(
                target=VariableNode(name="x"),
                expression=ConstantNode(42)
            )
        ])
        
        node, errors = analyzer.analyze(sentence)
        
        assert node is sentence
        assert errors == []
        assert analyzer.symbol_table.lookup_symbol("x") is not None
    
    def test_variable_declaration(self, analyzer):
        """Test variable declaration analysis."""
        decl = VariableDeclNode(name="count", var_type="integer", value=ConstantNode(0))
        
        node, errors = analyzer.analyze(decl)
        
        assert errors == []
        symbol = analyzer.symbol_table.lookup_symbol("count")
        assert symbol is not None
        assert symbol.var_type == "integer"
    
    def test_variable_redeclaration_error(self, analyzer):
        """Test variable redeclaration detection."""
        # First declaration
        decl1 = VariableDeclNode(name="x", var_type="integer")
        analyzer.analyze(decl1)
        
        # Second declaration (should cause error)
        decl2 = VariableDeclNode(name="x", var_type="string")
        node, errors = analyzer.analyze(decl2)
        
        assert len(errors) == 1
        assert "already declared" in errors[0].message
    
    def test_undeclared_variable_error(self, analyzer):
        """Test undeclared variable reference."""
        var_ref = VariableNode(name="undefined_var")
        
        node, errors = analyzer.analyze(var_ref)
        
        assert len(errors) == 1
        assert "not declared" in errors[0].message
    
    def test_auto_type_inference(self, analyzer):
        """Test auto type variable with initializer."""
        decl = VariableDeclNode(
            name="auto_var",
            var_type="auto",
            value=ConstantNode(42)
        )
        
        node, errors = analyzer.analyze(decl)
        
        assert errors == []
        symbol = analyzer.symbol_table.lookup_symbol("auto_var")
        assert symbol is not None
        # Auto type should be inferred from initializer
    
    def test_auto_without_initializer_error(self, analyzer):
        """Test auto type without initializer."""
        decl = VariableDeclNode(name="auto_var", var_type="auto", value=None)
        
        node, errors = analyzer.analyze(decl)
        
        assert len(errors) == 1
        assert "requires an initializer" in errors[0].message
    
    def test_assignment_type_checking(self, analyzer):
        """Test assignment with type checking."""
        # Declare integer variable
        decl = VariableDeclNode(name="int_var", var_type="integer")
        analyzer.analyze(decl)
        
        # Valid assignment
        assign = AssignmentNode(
            target=VariableNode(name="int_var"),
            expression=ConstantNode(100)
        )
        node, errors = analyzer.analyze(assign)
        
        assert errors == []
    
    def test_quantifier_block_scoping(self, analyzer):
        """Test quantifier block creates new scope."""
        quantifier = QuantifierBlockNode(
            variables=["x", "y"],
            condition=ConstantNode(value=True)
        )
        
        initial_scope = analyzer.symbol_table.current_scope
        node, errors = analyzer.analyze(quantifier)
        
        # Should be back to original scope after analysis
        assert analyzer.symbol_table.current_scope == initial_scope
    
    def test_predicate_call_validation(self, analyzer):
        """Test predicate call validation."""
        # Valid predicate call
        pred_call = PredicateCallNode(
            name="is_valid",
            arguments=[VariableNode(name="x")]
        )
        
        node, errors = analyzer.analyze(pred_call)
        
        # Should have error for undefined variable x, but not for predicate
        assert any("not declared" in err.message for err in errors)
        assert not any("not defined" in err.message and "is_valid" in err.message for err in errors)
    
    def test_undefined_predicate_error(self, analyzer):
        """Test undefined predicate call."""
        pred_call = PredicateCallNode(
            name="undefined_predicate",
            arguments=[]
        )
        
        node, errors = analyzer.analyze(pred_call)
        
        assert len(errors) == 1
        assert "not defined" in errors[0].message
    
    def test_predicate_arity_mismatch(self, analyzer):
        """Test predicate arity mismatch."""
        # is_valid expects 1 argument
        pred_call = PredicateCallNode(
            name="is_valid",
            arguments=[VariableNode("x"), VariableNode("y")]
        )
        
        node, errors = analyzer.analyze(pred_call)
        
        assert any("expects 1 arguments, got 2" in err.message for err in errors)
    
    def test_analysis_stats(self, analyzer):
        """Test analysis statistics tracking."""
        # Perform some analyses
        analyzer.analyze(VariableDeclNode(name="x"))
        analyzer.analyze(VariableDeclNode(name="y"))
        analyzer.analyze(VariableNode(name="z"))  # This will create an error
        
        stats = analyzer.get_analysis_stats()
        
        assert stats['analysis_count'] == 3
        assert stats['symbols_declared'] >= 2
        assert stats['errors_found'] >= 1
    
    def test_error_collector_reset(self, analyzer):
        """Test error collector resets between analyses."""
        # First analysis with error
        analyzer.analyze(VariableNode(name="undefined"))
        
        # Second analysis without error
        node, errors = analyzer.analyze(ConstantNode())
        
        # Should only have errors from second analysis
        assert errors == []
    
    def test_arithmetic_operation_visit(self, analyzer):
        """Test arithmetic operation node visit."""
        arith = ArithmeticBinaryOpNode()
        
        node, errors = analyzer.analyze(arith)
        
        # Should process without errors for valid arithmetic
        assert node is arith
    
    def test_condition_node_with_quantifier(self, analyzer):
        """Test condition node with quantifier block."""
        condition = ConditionNode(
            quantifier_block=QuantifierBlockNode(variables=["x"]),
            expression=ConstantNode(value=True)
        )
        
        node, errors = analyzer.analyze(condition)
        
        assert node is condition
        # Quantifier variables should be scoped properly
    
    def test_nested_scopes(self, analyzer):
        """Test nested scope handling."""
        # Create nested quantifier blocks
        inner_quantifier = QuantifierBlockNode(variables=["y"])
        outer_quantifier = QuantifierBlockNode(
            variables=["x"],
            condition=inner_quantifier
        )
        
        node, errors = analyzer.analyze(outer_quantifier)
        
        # Should handle nested scopes without errors
        assert errors == []


class TestSymbolTableIntegration:
    """Test symbol table integration with semantic analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return SemanticAnalyzerRefactored()
    
    def test_symbol_table_scope_management(self, analyzer):
        """Test symbol table scope management during analysis."""
        # Track scope changes
        initial_scope = analyzer.symbol_table.current_scope
        
        # Analyze quantifier (should create and exit scope)
        quantifier = QuantifierBlockNode(variables=["x"])
        analyzer.analyze(quantifier)
        
        # Should be back to initial scope
        assert analyzer.symbol_table.current_scope == initial_scope
    
    def test_symbol_visibility_across_scopes(self, analyzer):
        """Test symbol visibility across different scopes."""
        # Declare in outer scope
        analyzer.analyze(VariableDeclNode(name="outer_var", var_type="integer"))
        
        # Reference in quantifier scope should work
        quantifier = QuantifierBlockNode(
            variables=["x"],
            condition=VariableNode(name="outer_var")
        )
        
        node, errors = analyzer.analyze(quantifier)
        
        # outer_var should be visible in inner scope
        assert not any("outer_var" in err.message and "not declared" in err.message for err in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])