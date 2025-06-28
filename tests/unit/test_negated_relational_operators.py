import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    ComparisonNode,
    VariableNode
)

@pytest.fixture(scope="module")
def parser():
    """Provides a parser instance for the test module."""
    return CNLParser()

@pytest.mark.parametrize(
    "sentence, expected_operator",
    [
        ("x is not less than y", "!<"),
        ("x is not less than or equal to y", "!<="),
        ("x is not greater than y", "!>"),
        ("x is not greater than or equal to y", "!>="),
    ]
)
def test_negated_relational_operators(parser, sentence, expected_operator):
    """Tests parsing various negated relational operators."""
    ast = parser.parse(sentence)

    assert isinstance(ast, ComparisonNode), f"Expected ComparisonNode, but got {type(ast).__name__}"
    assert ast.operator == expected_operator, f"Expected operator '{expected_operator}', but got '{ast.operator}'"

    assert isinstance(ast.left, VariableNode)
    assert ast.left.name == "x"

    assert isinstance(ast.right, VariableNode)
    assert ast.right.name == "y"
