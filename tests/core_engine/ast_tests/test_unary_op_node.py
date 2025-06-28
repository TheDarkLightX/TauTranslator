import pytest
from pydantic import ValidationError

from tau_translator_omega.core_engine.ast import (
    ASTNode, UnaryExpressionNode, IdentifierNode, LiteralNode
)

def test_import_unary_expression_node_succeeds():
    """Ensures UnaryExpressionNode is importable."""
    assert UnaryExpressionNode is not None, "UnaryExpressionNode class should be imported."

def test_create_unary_expression_node_valid():
    """Test creating UnaryExpressionNode with valid parameters."""
    operand1 = IdentifierNode(name="p")
    operand2 = LiteralNode(value=True)

    node_logical_not = UnaryExpressionNode(operator="NOT", operand=operand1)
    assert node_logical_not.operator == "NOT"
    assert node_logical_not.operand == operand1
    assert isinstance(node_logical_not, ASTNode)
    assert isinstance(node_logical_not, UnaryExpressionNode)

    node_boolean_neg = UnaryExpressionNode(operator="NEG", operand=operand2)
    assert node_boolean_neg.operator == "NEG"
    assert node_boolean_neg.operand == operand2
    assert isinstance(node_boolean_neg, ASTNode)
    assert isinstance(node_boolean_neg, UnaryExpressionNode)

    node_always = UnaryExpressionNode(operator="ALWAYS", operand=operand1)
    assert node_always.operator == "ALWAYS"
    assert isinstance(node_always, UnaryExpressionNode)

    node_sometimes = UnaryExpressionNode(operator="SOMETIMES", operand=operand2)
    assert node_sometimes.operator == "SOMETIMES"
    assert isinstance(node_sometimes, UnaryExpressionNode)

def test_unary_expression_node_immutable():
    """Test that UnaryExpressionNode is immutable."""
    node = UnaryExpressionNode(operator="NOT", operand=IdentifierNode(name="q"))
    with pytest.raises(ValidationError, match="Instance is frozen"):
        node.operator = "NEG"
    with pytest.raises(ValidationError, match="Instance is frozen"):
        node.operand = IdentifierNode(name="r")

def test_unary_expression_node_invalid_operator_type():
    """Test creating UnaryExpressionNode with invalid operator type."""
    with pytest.raises(ValidationError, match=r"Input should be a valid string"):
        UnaryExpressionNode(operator=123, operand=IdentifierNode(name="p"))

def test_unary_expression_node_invalid_operand_type():
    """Test creating UnaryExpressionNode with invalid operand type."""
    with pytest.raises(ValidationError, match=r"Input should be a valid dictionary or instance of ASTNode"):
        UnaryExpressionNode(operator="NOT", operand="p")

def test_unary_expression_node_equality_and_hash():
    """Test equality and hashability of UnaryExpressionNode instances."""
    p = IdentifierNode(name="p")
    q = IdentifierNode(name="q")
    true_lit = LiteralNode(value=True)

    op1 = UnaryExpressionNode(operator="NOT", operand=p)
    op2 = UnaryExpressionNode(operator="NOT", operand=p)  # Same as op1
    op3 = UnaryExpressionNode(operator="NEG", operand=p)  # Diff operator
    op4 = UnaryExpressionNode(operator="NOT", operand=q)  # Diff operand (content)
    op5 = UnaryExpressionNode(operator="NOT", operand=true_lit)  # Diff operand (type)

    assert op1 == op2
    assert op1 != op3
    assert op1 != op4
    assert op1 != op5

    # Pydantic models with model_config(frozen=True) are hashable by default if all fields are hashable.
    node_set = {op1, op2, op3, op4, op5}
    assert len(node_set) == 4  # op1 and op2 are duplicates
    assert op1 in node_set
    assert op3 in node_set
    assert op4 in node_set
    assert op5 in node_set
