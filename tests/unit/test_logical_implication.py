import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    ConditionalExpressionNode,
    PredicateCallNode,
    VariableNode,
)

@pytest.fixture
def parser():
    return CNLParser()

def test_simple_implication(parser):
    """Tests parsing a simple 'if...then' statement."""
    sentence = "if x is a man then x is mortal"
    ast = parser.parse(sentence)

    assert isinstance(ast, ConditionalExpressionNode), f"Expected ConditionalExpressionNode, but got {type(ast).__name__}"
    assert ast.conditional_type == "if_then"

    # Check the condition (antecedent)
    condition = ast.condition
    assert isinstance(condition, PredicateCallNode)
    assert condition.name == "man"
    assert len(condition.args) == 1
    assert isinstance(condition.args[0], VariableNode)
    assert condition.args[0].name == "x"

    # Check the consequent
    consequent = ast.consequent
    assert isinstance(consequent, PredicateCallNode)
    assert consequent.name == "mortal"
    assert len(consequent.args) == 1
    assert isinstance(consequent.args[0], VariableNode)
    assert consequent.args[0].name == "x"
