import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import ConstantNode

@pytest.fixture(scope="module")
def parser():
    """Provides a parser instance for the test module."""
    return CNLParser()

def test_true_literal(parser):
    """Tests parsing the 'it is true' literal."""
    sentence = "it is true"
    ast = parser.parse(sentence)

    assert isinstance(ast, ConstantNode), f"Expected ConstantNode, but got {type(ast).__name__}"
    assert ast.value is True
    assert ast.value_type == 'BOOLEAN'

def test_false_literal(parser):
    """Tests parsing the 'it is false' literal."""
    sentence = "it is false"
    ast = parser.parse(sentence)

    assert isinstance(ast, ConstantNode), f"Expected ConstantNode, but got {type(ast).__name__}"
    assert ast.value is False
    assert ast.value_type == 'BOOLEAN'
