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

def test_logical_and(parser):
    """Tests parsing a simple 'and also' statement."""
    sentence = "x is a p and also x is a q"
    ast = parser.parse(sentence)

    assert isinstance(ast, BooleanBinaryOpNode)
    assert ast.operator == "&&"

    # Check left operand
    left = ast.left
    assert isinstance(left, PredicateCallNode)
    assert left.name == "p"
    assert len(left.args) == 1
    assert isinstance(left.args[0], VariableNode)
    assert left.args[0].name == "x"

    # Check right operand
    right = ast.right
    assert isinstance(right, PredicateCallNode)
    assert right.name == "q"
    assert len(right.args) == 1
    assert isinstance(right.args[0], VariableNode)
    assert right.args[0].name == "x"

def test_logical_or(parser):
    """Tests parsing a simple 'or else' statement."""
    sentence = "x is a p or else x is a q"
    ast = parser.parse(sentence)

    assert isinstance(ast, BooleanBinaryOpNode)
    assert ast.operator == "||"

    # Check left operand
    left = ast.left
    assert isinstance(left, PredicateCallNode)
    assert left.name == "p"
    assert len(left.args) == 1
    assert isinstance(left.args[0], VariableNode)
    assert left.args[0].name == "x"

    # Check right operand
    right = ast.right
    assert isinstance(right, PredicateCallNode)
    assert right.name == "q"
    assert len(right.args) == 1
    assert isinstance(right.args[0], VariableNode)
    assert right.args[0].name == "x"
