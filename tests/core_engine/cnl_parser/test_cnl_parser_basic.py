"""
Basic CNL parser tests following TDD principles.

This file contains the most fundamental tests for CNL parsing,
starting with the simplest possible cases and building up complexity.
"""

import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser import CNLParser
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    SentenceNode, FactNode, ConstantNode, PredicateCallNode, ASTNode
)


class TestCNLParserBasicConstants:
    """Test parsing of basic constants (simplest case)."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return CNLParser()

    def test_parse_boolean_true(self, parser):
        """Test parsing boolean true constant."""
        result = parser.parse("true.")
        
        # Should return a SentenceNode containing a FactNode with a boolean constant
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ConstantNode)
        assert result.content.statement.value is True
        assert result.content.statement.value_type == 'BOOLEAN'

    def test_parse_boolean_false(self, parser):
        """Test parsing boolean false constant."""
        result = parser.parse("false.")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ConstantNode)
        assert result.content.statement.value is False
        assert result.content.statement.value_type == 'BOOLEAN'

    def test_parse_integer_constant(self, parser):
        """Test parsing integer constants."""
        result = parser.parse("42.")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ConstantNode)
        assert result.content.statement.value == 42
        assert result.content.statement.value_type == 'INTEGER'

    def test_parse_negative_integer(self, parser):
        """Test parsing negative integer constants."""
        result = parser.parse("-10.")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ConstantNode)
        assert result.content.statement.value == -10
        assert result.content.statement.value_type == 'INTEGER'

    def test_parse_float_constant(self, parser):
        """Test parsing float constants."""
        result = parser.parse("3.14.")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ConstantNode)
        assert abs(result.content.statement.value - 3.14) < 0.001
        assert result.content.statement.value_type == 'FLOAT'

    def test_parse_string_constant(self, parser):
        """Test parsing string constants."""
        result = parser.parse('"hello".')
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ConstantNode)
        assert result.content.statement.value == "hello"
        assert result.content.statement.value_type == 'STRING'


class TestCNLParserBasicPredicates:
    """Test parsing of basic predicate calls."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return CNLParser()

    def test_parse_simple_predicate_no_args(self, parser):
        """Test parsing predicate with no arguments."""
        result = parser.parse("is_sunny().")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, PredicateCallNode)
        assert result.content.statement.name == "is_sunny"
        assert len(result.content.statement.args) == 0

    def test_parse_simple_predicate_one_arg(self, parser):
        """Test parsing predicate with one argument."""
        result = parser.parse("is_hot(sun).")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, PredicateCallNode)
        assert result.content.statement.name == "is_hot"
        assert len(result.content.statement.args) == 1
        
        # The argument should be a constant (CNAME treated as constant)
        arg = result.content.statement.args[0]
        assert isinstance(arg, ConstantNode)
        assert arg.value == "sun"

    def test_parse_predicate_multiple_args(self, parser):
        """Test parsing predicate with multiple arguments."""
        result = parser.parse("distance(earth, moon, 384400).")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, PredicateCallNode)
        assert result.content.statement.name == "distance"
        assert len(result.content.statement.args) == 3
        
        # Check argument types
        assert isinstance(result.content.statement.args[0], ConstantNode)
        assert result.content.statement.args[0].value == "earth"
        
        assert isinstance(result.content.statement.args[1], ConstantNode)
        assert result.content.statement.args[1].value == "moon"
        
        assert isinstance(result.content.statement.args[2], ConstantNode)
        assert result.content.statement.args[2].value == 384400


class TestCNLParserErrorCases:
    """Test error handling for malformed input."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return CNLParser()

    def test_parse_missing_period(self, parser):
        """Test that missing period raises an error."""
        with pytest.raises(Exception):
            parser.parse("true")

    def test_parse_unclosed_parenthesis(self, parser):
        """Test that unclosed parenthesis raises an error."""
        with pytest.raises(Exception):
            parser.parse("is_hot(sun")

    def test_parse_invalid_syntax(self, parser):
        """Test that invalid syntax raises an error."""
        with pytest.raises(Exception):
            parser.parse("@#$%.")


class TestCNLParserTransformerMethods:
    """Test individual transformer methods in isolation."""

    def test_transformer_boolean_literals(self):
        """Test that transformer handles boolean literals correctly."""
        from tau_translator_omega.core_engine.parsers.cnl_parser.parser import TceTransformer
        from lark import Token
        
        transformer = TceTransformer()
        
        # Test TRUE_KW
        true_token = Token('TRUE_KW', 'true')
        result = transformer.boolean_literal([true_token])
        assert isinstance(result, ConstantNode)
        assert result.value is True
        assert result.value_type == 'BOOLEAN'
        
        # Test FALSE_KW
        false_token = Token('FALSE_KW', 'false')
        result = transformer.boolean_literal([false_token])
        assert isinstance(result, ConstantNode)
        assert result.value is False
        assert result.value_type == 'BOOLEAN'

    def test_transformer_number_handling(self):
        """Test that transformer handles numbers correctly."""
        from tau_translator_omega.core_engine.parsers.cnl_parser.parser import TceTransformer
        from lark import Token
        
        transformer = TceTransformer()
        
        # Test integer
        int_token = Token('NUMBER', '42')
        result = transformer.NUMBER(int_token)
        assert isinstance(result, ConstantNode)
        assert result.value == 42
        assert result.value_type == 'INTEGER'
        
        # Test float
        float_token = Token('NUMBER', '3.14')
        result = transformer.NUMBER(float_token)
        assert isinstance(result, ConstantNode)
        assert abs(result.value - 3.14) < 0.001
        assert result.value_type == 'FLOAT'

    def test_transformer_string_handling(self):
        """Test that transformer handles strings correctly."""
        from tau_translator_omega.core_engine.parsers.cnl_parser.parser import TceTransformer
        from lark import Token
        
        transformer = TceTransformer()
        
        # Test string (note: ESCAPED_STRING includes quotes)
        string_token = Token('ESCAPED_STRING', '"hello"')
        result = transformer.ESCAPED_STRING(string_token)
        assert isinstance(result, ConstantNode)
        assert result.value == "hello"
        assert result.value_type == 'STRING'
