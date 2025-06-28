import pytest
from pydantic import ValidationError

from tau_translator_omega.core_engine.ast import (
    ASTNode,
    IdentifierNode,
    LiteralNode,
    BinaryExpressionNode,
)

def test_import_binary_expression_node_succeeds():
    """Ensures BinaryExpressionNode is importable."""
    assert BinaryExpressionNode is not None, "BinaryExpressionNode class should be imported."

def test_create_binary_op_node_valid():
    """Test creating BinaryExpressionNode with valid parameters."""
    left = IdentifierNode(name="p")
    right_id = IdentifierNode(name="q")
    right_num = LiteralNode(value=10)

    node_and = BinaryExpressionNode(left=left, operator="AND", right=right_id)
    assert node_and.operator == "AND"
    assert node_and.left == left
    assert node_and.right == right_id
    assert isinstance(node_and, ASTNode)
    assert isinstance(node_and, BinaryExpressionNode)

    node_eq = BinaryExpressionNode(left=left, operator="==", right=right_num)
    assert node_eq.operator == "=="
    assert node_eq.left == left
    assert node_eq.right == right_num
    assert isinstance(node_eq, ASTNode)
    assert isinstance(node_eq, BinaryExpressionNode)

def test_binary_expression_node_immutable():
    """Test that BinaryExpressionNode is immutable."""
    node = BinaryExpressionNode(left=IdentifierNode(name="a"), operator="OR", right=IdentifierNode(name="b"))
    with pytest.raises(ValidationError, match="Instance is frozen"):
        node.operator = "AND"
    with pytest.raises(ValidationError, match="Instance is frozen"):
        node.left = IdentifierNode(name="c")
    with pytest.raises(ValidationError, match="Instance is frozen"):
        node.right = IdentifierNode(name="d")

def test_binary_expression_node_invalid_operator_type():
    """Test creating BinaryExpressionNode with invalid operator type."""
    with pytest.raises(ValidationError, match=r"Input should be a valid string"):
        # operator should be a string, not an Enum or other type
        BinaryExpressionNode(left=IdentifierNode(name="p"), operator=123, right=IdentifierNode(name="q"))

def test_binary_op_node_invalid_operands():
    """Test creating BinaryExpressionNode with invalid operands."""
    # Pydantic raises ValidationError for type mismatches on fields.
    # For 'left' operand (expecting ASTNode, got str):
    with pytest.raises(ValidationError, match=r"Input should be a valid dictionary or instance of ASTNode"):
        BinaryExpressionNode(left="p", operator="AND", right=IdentifierNode(name="q"))

    # For 'right' operand (expecting ASTNode, got str):
    with pytest.raises(ValidationError, match=r"Input should be a valid dictionary or instance of ASTNode"):
        BinaryExpressionNode(left=IdentifierNode(name="p"), operator="AND", right="q")
    # It's assumed the string content itself (e.g. valid operator token) is validated by a later stage (parser/compiler), not the AST node constructor.

def test_binary_expression_node_equality_and_hash():
    """Test equality and hashability of BinaryExpressionNode instances."""
    p = IdentifierNode(name="p")
    q = IdentifierNode(name="q")
    r = IdentifierNode(name="r")
    num10 = LiteralNode(value=10)

    b1 = BinaryExpressionNode(left=p, operator="AND", right=q)
    b2 = BinaryExpressionNode(left=p, operator="AND", right=q) # Same as b1
    b3 = BinaryExpressionNode(left=p, operator="OR", right=q) # Diff operator
    b4 = BinaryExpressionNode(left=r, operator="AND", right=q) # Diff left operand
    b5 = BinaryExpressionNode(left=p, operator="AND", right=r) # Diff right operand
    b6 = BinaryExpressionNode(left=p, operator="==", right=num10) # Diff operator and right type

    assert b1 == b2
    assert b1 != b3
    assert b1 != b4
    assert b1 != b5
    assert b1 != b6

    # Pydantic models with model_config(frozen=True) are hashable if all fields are hashable.
    node_set = {b1, b2, b3, b4, b5, b6}
    assert len(node_set) == 5 # b1 and b2 are duplicates
    assert b1 in node_set
    assert b3 in node_set
    assert b4 in node_set
    assert b5 in node_set
    assert b6 in node_set
