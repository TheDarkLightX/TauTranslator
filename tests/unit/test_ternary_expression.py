import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    TernaryOpNode,
    PredicateCallNode,
    VariableNode
)

@pytest.fixture(scope="module")
def parser():
    """Provides a parser instance for the test module."""
    return CNLParser()

def test_simple_ternary_expression(parser):
    """Tests parsing a simple 'if...then...else' statement."""
    sentence = "if x is a p then y is a q else z is a r"
    ast = parser.parse(sentence)

    assert isinstance(ast, TernaryOpNode), f"Expected TernaryOpNode, but got {type(ast).__name__}"

    # Check condition
    condition = ast.condition
    assert isinstance(condition, PredicateCallNode)
    assert condition.name == "p"
    assert len(condition.args) == 1
    assert condition.args[0].name == "x"

    # Check value_if_true
    value_if_true = ast.value_if_true
    assert isinstance(value_if_true, PredicateCallNode)
    assert value_if_true.name == "q"
    assert len(value_if_true.args) == 1
    assert value_if_true.args[0].name == "y"

    # Check value_if_false
    value_if_false = ast.value_if_false
    assert isinstance(value_if_false, PredicateCallNode)
    assert value_if_false.name == "r"
    assert len(value_if_false.args) == 1
    assert value_if_false.args[0].name == "z"
