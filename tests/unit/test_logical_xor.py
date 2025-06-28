import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    BooleanBinaryOpNode,
    PredicateCallNode,
    VariableNode
)

@pytest.fixture(scope="module")
def parser():
    """Provides a parser instance for the test module."""
    return CNLParser()

def test_simple_xor(parser):
    """Tests parsing a simple 'xor' statement."""
    sentence = "it is raining xor it is sunny"
    ast = parser.parse(sentence)

    assert isinstance(ast, BooleanBinaryOpNode), f"Expected BooleanBinaryOpNode, but got {type(ast).__name__}"
    assert ast.operator == "xor"

    # Check the left operand
    left = ast.left
    assert isinstance(left, PredicateCallNode)
    assert left.name == "raining"
    assert len(left.args) == 1
    assert isinstance(left.args[0], VariableNode)
    assert left.args[0].name == "it"

    # Check the right operand
    right = ast.right
    assert isinstance(right, PredicateCallNode)
    assert right.name == "sunny"
    assert len(right.args) == 1
    assert isinstance(right.args[0], VariableNode)
    assert right.args[0].name == "it"
