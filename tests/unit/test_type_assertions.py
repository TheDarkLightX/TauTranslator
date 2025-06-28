import pytest
from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
from src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    TypeAssertionNode,
    VariableNode,
)

@pytest.fixture
def parser():
    """Returns a CNLParser instance."""
    return CNLParser()

class TestTypeAssertions:
    def test_simple_type_assertion(self, parser):
        """
        Tests parsing a simple type assertion like 'x is of type integer'.
        """
        text = "x is of type integer"
        result = parser.parse(text)
        
        assert isinstance(result, TypeAssertionNode), f"Expected TypeAssertionNode, but got {type(result).__name__}"
        assert isinstance(result.variable, VariableNode), f"Expected VariableNode, but got {type(result.variable).__name__}"
        assert result.variable.name == "x"
        assert result.type_name == "integer"

    def test_type_assertion_with_built_in_types(self, parser):
        """
        Tests parsing type assertions with various built-in Tau types.
        """
        test_cases = {
            "y is of type boolean": ("y", "boolean"),
            "t is of type time": ("t", "time"),
            "s is of type string": ("s", "string"),
            "r is of type real": ("r", "real"),
        }

        for text, (var, type_name) in test_cases.items():
            result = parser.parse(text)
            assert isinstance(result, TypeAssertionNode), f"Failed on: {text}"
            assert result.variable.name == var, f"Failed on: {text}"
            assert result.type_name == type_name, f"Failed on: {text}"

    def test_type_assertion_with_custom_type(self, parser):
        """
        Tests parsing a type assertion with a user-defined type name.
        """
        text = "my_car is of type Vehicle"
        result = parser.parse(text)
        assert isinstance(result, TypeAssertionNode)
        assert result.variable.name == "my_car"
        assert result.type_name == "Vehicle"
