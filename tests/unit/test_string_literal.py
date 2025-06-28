import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (PredicateCallNode, StringNode, VariableNode)

@pytest.fixture
def parser():
    return CNLParser()

def test_string_literal_parsing(parser):
    """Tests parsing a relational fact with a string literal as the object."""
    sentence = 'x named "my_variable"'
    ast = parser.parse(sentence)

    assert isinstance(ast, PredicateCallNode)
    assert ast.name == 'named'
    assert len(ast.args) == 2

    subject = ast.args[0]
    assert isinstance(subject, VariableNode)
    assert subject.name == 'x'

    obj = ast.args[1]
    assert isinstance(obj, StringNode)
    assert obj.value == '"my_variable"'
