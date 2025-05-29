"""
Tests for the Mock CNL Parser.

This tests the core AST generation functionality without relying on Lark,
allowing us to verify that our AST nodes and parsing logic work correctly.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from tau_translator_omega.core_engine.cnl_parser.mock_parser import MockCNLParser
from tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
    SentenceNode, FactNode, ConstantNode, PredicateCallNode, ComparisonNode
)


class TestMockCNLParserBasics:
    """Test basic functionality of the mock parser."""

    @pytest.fixture
    def parser(self):
        """Create a mock parser instance for testing."""
        return MockCNLParser(debug=False)

    def test_parser_creation(self, parser):
        """Test that parser can be created."""
        assert parser is not None
        assert hasattr(parser, 'parse')

    def test_empty_input_error(self, parser):
        """Test that empty input raises appropriate error."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            parser.parse("")
        
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            parser.parse("   ")

    def test_missing_period_error(self, parser):
        """Test that missing period raises error."""
        with pytest.raises(ValueError, match="Sentence must end with period"):
            parser.parse("true")


class TestMockCNLParserConstants:
    """Test parsing of basic constants."""

    @pytest.fixture
    def parser(self):
        """Create a mock parser instance for testing."""
        return MockCNLParser(debug=False)

    def test_parse_boolean_true(self, parser):
        """Test parsing boolean true constant."""
        result = parser.parse("true.")
        
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

    def test_parse_identifier_constant(self, parser):
        """Test parsing identifier constants."""
        result = parser.parse("sun.")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ConstantNode)
        assert result.content.statement.value == "sun"
        assert result.content.statement.value_type == 'IDENTIFIER'


class TestMockCNLParserPredicates:
    """Test parsing of predicate calls."""

    @pytest.fixture
    def parser(self):
        """Create a mock parser instance for testing."""
        return MockCNLParser(debug=False)

    def test_parse_predicate_no_args(self, parser):
        """Test parsing predicate with no arguments."""
        result = parser.parse("is_sunny().")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, PredicateCallNode)
        assert result.content.statement.name == "is_sunny"
        assert len(result.content.statement.args) == 0

    def test_parse_predicate_one_arg(self, parser):
        """Test parsing predicate with one argument."""
        result = parser.parse("is_hot(sun).")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, PredicateCallNode)
        assert result.content.statement.name == "is_hot"
        assert len(result.content.statement.args) == 1
        
        arg = result.content.statement.args[0]
        assert isinstance(arg, ConstantNode)
        assert arg.value == "sun"
        assert arg.value_type == 'IDENTIFIER'

    def test_parse_predicate_multiple_args(self, parser):
        """Test parsing predicate with multiple arguments."""
        result = parser.parse("distance(earth, moon, 384400).")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, PredicateCallNode)
        assert result.content.statement.name == "distance"
        assert len(result.content.statement.args) == 3
        
        # Check argument types and values
        args = result.content.statement.args
        
        assert isinstance(args[0], ConstantNode)
        assert args[0].value == "earth"
        assert args[0].value_type == 'IDENTIFIER'
        
        assert isinstance(args[1], ConstantNode)
        assert args[1].value == "moon"
        assert args[1].value_type == 'IDENTIFIER'
        
        assert isinstance(args[2], ConstantNode)
        assert args[2].value == 384400
        assert args[2].value_type == 'INTEGER'


class TestMockCNLParserComparisons:
    """Test parsing of comparison expressions."""

    @pytest.fixture
    def parser(self):
        """Create a mock parser instance for testing."""
        return MockCNLParser(debug=False)

    def test_parse_simple_comparison(self, parser):
        """Test parsing simple comparison."""
        result = parser.parse("temperature > 30.")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ComparisonNode)
        
        comp = result.content.statement
        assert comp.operator == ">"
        
        assert isinstance(comp.left, ConstantNode)
        assert comp.left.value == "temperature"
        assert comp.left.value_type == 'IDENTIFIER'
        
        assert isinstance(comp.right, ConstantNode)
        assert comp.right.value == 30
        assert comp.right.value_type == 'INTEGER'

    def test_parse_equality_comparison(self, parser):
        """Test parsing equality comparison."""
        result = parser.parse("status = active.")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ComparisonNode)
        
        comp = result.content.statement
        assert comp.operator == "="
        assert comp.left.value == "status"
        assert comp.right.value == "active"

    def test_parse_numeric_comparison(self, parser):
        """Test parsing numeric comparison."""
        result = parser.parse("3.14 >= 3.")
        
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ComparisonNode)
        
        comp = result.content.statement
        assert comp.operator == ">="
        assert comp.left.value == 3.14
        assert comp.right.value == 3


class TestMockCNLParserTokenizer:
    """Test the tokenizer functionality."""

    @pytest.fixture
    def parser(self):
        """Create a mock parser instance for testing."""
        return MockCNLParser(debug=True)

    def test_tokenize_simple_boolean(self, parser):
        """Test tokenizing simple boolean."""
        tokens = parser.tokenize("true.")
        expected = [('BOOLEAN', 'true', 0), ('PERIOD', '.', 4)]
        assert tokens == expected

    def test_tokenize_predicate_call(self, parser):
        """Test tokenizing predicate call."""
        tokens = parser.tokenize("is_hot(sun).")
        expected = [
            ('IDENTIFIER', 'is_hot', 0),
            ('LPAREN', '(', 6),
            ('IDENTIFIER', 'sun', 7),
            ('RPAREN', ')', 10),
            ('PERIOD', '.', 11)
        ]
        assert tokens == expected

    def test_tokenize_comparison(self, parser):
        """Test tokenizing comparison."""
        tokens = parser.tokenize("temp > 30.")
        expected = [
            ('IDENTIFIER', 'temp', 0),
            ('COMPARISON', '>', 5),
            ('NUMBER', '30', 7),
            ('PERIOD', '.', 9)
        ]
        assert tokens == expected
