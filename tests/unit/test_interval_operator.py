import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    BooleanBinaryOpNode,
    ComparisonNode,
    VariableNode,
    ConstantNode,
)

@pytest.fixture
def parser():
    return CNLParser()

def test_interval_operator(parser):
    """Tests parsing an interval expression like 'x is > 5 and < 10'."""
    sentence = "x is greater than 5 and less than 10"
    ast = parser.parse(sentence)

    assert isinstance(ast, BooleanBinaryOpNode), f"Expected BooleanBinaryOpNode, but got {type(ast).__name__}"
    assert ast.operator == "&&"

    # Check left side of the AND
    left = ast.left
    assert isinstance(left, ComparisonNode)
    assert isinstance(left.left, VariableNode)
    assert left.left.name == "x"
    assert left.operator == ">"
    assert isinstance(left.right, ConstantNode)
    assert left.right.value == 5

    # Check right side of the AND
    right = ast.right
    assert isinstance(right, ComparisonNode)
    assert isinstance(right.left, VariableNode)
    assert right.left.name == "x"
    assert right.operator == "<"
    assert isinstance(right.right, ConstantNode)
    assert right.right.value == 10
