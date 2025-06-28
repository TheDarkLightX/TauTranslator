# backend/unified/tests/unit/test_cnl_parser_logic.py

import pytest
from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    BooleanBinaryOpNode,
    BooleanUnaryOpNode,
    ComparisonNode,
    VariableNode,
    ConstantNode,
    QuantifierBlockNode
)

@pytest.fixture
def parser() -> CNLParser:
    return CNLParser()

def test_simple_comparison(parser: CNLParser):
    """Test parsing a simple comparison: x == 1"""
    ast = parser.parse("always (x is equal to 1)")
    # The top node is the temporal quantifier
    assert ast.quantifier == "always"
    # The actual comparison is the expression within it
    comp_node = ast.expression
    assert isinstance(comp_node, ComparisonNode)
    assert comp_node.operator == "=="
    assert isinstance(comp_node.left, VariableNode)
    assert comp_node.left.name == "x"
    assert isinstance(comp_node.right, ConstantNode)
    assert comp_node.right.value == 1

def test_logical_and(parser: CNLParser):
    """Test parsing a logical AND expression."""
    ast = parser.parse("always ((x > 0) and also (y < 10))")
    expr = ast.expression
    assert isinstance(expr, BooleanBinaryOpNode)
    assert expr.operator == "and also"
    assert isinstance(expr.left, ComparisonNode)
    assert expr.left.operator == ">"
    assert isinstance(expr.right, ComparisonNode)
    assert expr.right.operator == "<"

def test_logical_or(parser: CNLParser):
    """Test parsing a logical OR expression."""
    ast = parser.parse("always ((a != b) or else (c == d))")
    expr = ast.expression
    assert isinstance(expr, BooleanBinaryOpNode)
    assert expr.operator == "or else"

def test_logical_not(parser: CNLParser):
    """Test parsing a logical NOT expression."""
    ast = parser.parse("always (it is not the case that (x > 5))")
    expr = ast.expression
    assert isinstance(expr, BooleanUnaryOpNode)
    assert expr.operator == "not"
    assert isinstance(expr.operand, ComparisonNode)

def test_quantifier_forall(parser: CNLParser):
    """Test parsing a forall quantifier."""
    ast = parser.parse("always (for all x such that (x > 0))")
    expr = ast.expression
    assert isinstance(expr, QuantifierBlockNode)
    assert expr.quant_type == "forall"
    assert len(expr.variables) == 1
    assert expr.variables[0].name == "x"
    assert isinstance(expr.condition, ComparisonNode)

def test_quantifier_exists(parser: CNLParser):
    """Test parsing a there exists quantifier."""
    ast = parser.parse("always (there exists y, (y < 100))")
    expr = ast.expression
    assert isinstance(expr, QuantifierBlockNode)
    assert expr.quant_type == "exists"
    assert expr.variables[0].name == "y"
