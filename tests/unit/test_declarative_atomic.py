import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    PredicateCallNode,
    VariableNode,
    BooleanUnaryOpNode,
    QuantifierBlockNode,
    BooleanBinaryOpNode,
    ComparisonNode,
    ConstantNode,
    TemporalQuantifierNode
)

@pytest.fixture(scope="module")
def parser():
    """Provides a parser instance for the test module."""
    return CNLParser()

def test_is_a_fact(parser):
    """Tests parsing a simple 'is a' fact."""
    sentence = "Socrates is a man"
    ast = parser.parse(sentence)
    assert isinstance(ast, PredicateCallNode), f"Expected PredicateCallNode, but got {type(ast).__name__}"
    assert ast.name == "man"
    assert len(ast.args) == 1
    assert isinstance(ast.args[0], VariableNode)
    assert ast.args[0].name == "Socrates"

def test_negated_is_a_fact(parser):
    """Tests parsing a simple 'is not a' fact."""
    sentence = "table is not a person"
    ast = parser.parse(sentence)
    assert isinstance(ast, BooleanUnaryOpNode)
    assert ast.operator == "NOT"
    fact_node = ast.operand
    assert isinstance(fact_node, PredicateCallNode)
    assert fact_node.name == "person"
    assert len(fact_node.args) == 1
    assert isinstance(fact_node.args[0], VariableNode)
    assert fact_node.args[0].name == "table"

def test_logical_and(parser):
    sentence = "always (x > 5 and also y < 10)"
    ast = parser.parse(sentence)

    assert isinstance(ast, TemporalQuantifierNode)
    expression = ast.expression
    assert isinstance(expression, BooleanBinaryOpNode)
    assert expression.operator == "and also"

    assert isinstance(expression.left, ComparisonNode)
    assert expression.left.operator == ">"
    assert expression.left.left.name == "x"
    assert expression.left.right.value == 5

    assert isinstance(expression.right, ComparisonNode)
    assert expression.right.operator == "<"
    assert expression.right.left.name == "y"
    assert expression.right.right.value == 10

def test_for_all(parser):
    sentence = "always (for all x, x is a person)"
    ast = parser.parse(sentence)

    assert isinstance(ast, TemporalQuantifierNode)
    expression = ast.expression
    assert isinstance(expression, QuantifierBlockNode)
    assert expression.quant_type == 'forall'
    assert len(expression.variables) == 1
    assert expression.variables[0].name == 'x'

    condition = expression.condition
    assert isinstance(condition, PredicateCallNode)
    assert condition.name == "person"
    assert len(condition.args) == 1
    assert isinstance(condition.args[0], VariableNode)
    assert condition.args[0].name == "x"