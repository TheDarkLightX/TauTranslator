import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    TemporalQuantifierNode,
    PredicateCallNode,
    VariableNode
)

@pytest.fixture(scope="module")
def parser():
    """Provides a parser instance for the test module."""
    return CNLParser()

def test_always_operator(parser):
    """Tests parsing a simple 'always' statement."""
    sentence = "always x is a p"
    ast = parser.parse(sentence)

    assert isinstance(ast, TemporalQuantifierNode)
    assert ast.quantifier == "always"

    # Check the expression
    expression = ast.expression
    assert isinstance(expression, PredicateCallNode)
    assert expression.name == "p"
    assert len(expression.args) == 1
    assert isinstance(expression.args[0], VariableNode)
    assert expression.args[0].name == "x"

def test_sometimes_operator(parser):
    """Tests parsing a simple 'sometimes' statement."""
    sentence = "sometimes x is a p"
    ast = parser.parse(sentence)

    assert isinstance(ast, TemporalQuantifierNode)
    assert ast.quantifier == "sometimes"

    # Check the expression
    expression = ast.expression
    assert isinstance(expression, PredicateCallNode)
    assert expression.name == "p"
    assert len(expression.args) == 1
    assert isinstance(expression.args[0], VariableNode)
    assert expression.args[0].name == "x"

def test_eventually_operator(parser):
    """Tests parsing a simple 'eventually' statement."""
    sentence = "eventually x is a p"
    ast = parser.parse(sentence)

    assert isinstance(ast, TemporalQuantifierNode)
    assert ast.quantifier == "eventually"

    # Check the expression
    expression = ast.expression
    assert isinstance(expression, PredicateCallNode)
    assert expression.name == "p"
    assert len(expression.args) == 1
    assert isinstance(expression.args[0], VariableNode)
    assert expression.args[0].name == "x"

def test_never_operator(parser):
    """Tests parsing a simple 'never' statement."""
    sentence = "never x is a p"
    ast = parser.parse(sentence)

    assert isinstance(ast, TemporalQuantifierNode)
    assert ast.quantifier == "never"

    # Check the expression
    expression = ast.expression
    assert isinstance(expression, PredicateCallNode)
    assert expression.name == "p"
    assert len(expression.args) == 1
    assert isinstance(expression.args[0], VariableNode)
    assert expression.args[0].name == "x"
