import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    ConditionalExpressionNode,
    PredicateCallNode,
    VariableNode
)

@pytest.fixture(scope="module")
def parser():
    """Provides a parser instance for the test module."""
    return CNLParser()

def test_left_implication(parser):
    """Tests parsing a left-implication statement ('A if B')."""
    sentence = "y is a q if x is a p"
    ast = parser.parse(sentence)

    assert isinstance(ast, ConditionalExpressionNode), f"Expected ConditionalExpressionNode, but got {type(ast).__name__}"
    assert ast.conditional_type == "if_then"

    # Check condition (B part: 'x is a p')
    condition = ast.condition
    assert isinstance(condition, PredicateCallNode)
    assert condition.name == "p"
    assert len(condition.args) == 1
    assert condition.args[0].name == "x"

    # Check consequence (A part: 'y is a q')
    consequent = ast.consequent
    assert isinstance(consequent, PredicateCallNode)
    assert consequent.name == "q"
    assert len(consequent.args) == 1
    assert consequent.args[0].name == "y"
