import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    PredicateCallNode,
    VariableNode
)

@pytest.fixture(scope="module")
def parser():
    """Provides a parser instance for the test module."""
    return CNLParser()

def test_three_argument_fact(parser):
    """Tests parsing a fact with three arguments, e.g., 'x gives y z'."""
    sentence = "x gives y z"
    ast = parser.parse(sentence)

    assert isinstance(ast, PredicateCallNode)
    assert ast.name == "gives"
    assert len(ast.args) == 3
    assert isinstance(ast.args[0], VariableNode)
    assert ast.args[0].name == "x"
    assert isinstance(ast.args[1], VariableNode)
    assert ast.args[1].name == "y"
    assert isinstance(ast.args[2], VariableNode)
    assert ast.args[2].name == "z"
