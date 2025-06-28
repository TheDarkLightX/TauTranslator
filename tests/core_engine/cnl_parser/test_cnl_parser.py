import pytest
from tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser import (
    CNLParser, ASTNode, FactNode, SentenceNode, PredicateCallNode, 
    ConstantNode, VariableNode, ComparisonNode, ArithmeticBinaryOpNode, 
    BooleanBinaryOpNode
)

@pytest.fixture
def parser() -> CNLParser:
    """Provides a CNLParser instance for testing."""
    return CNLParser()

class TestCNLParserHappyPath:
    """Tests for successful parsing of valid CNL sentences."""

    def test_parse_simple_fact(self, parser):
        """Test parsing a simple fact like 'is_hot(sun).'"""
        ast = parser.parse("is_hot(sun).")
        assert isinstance(ast, SentenceNode)
        assert isinstance(ast.content, FactNode)
        predicate = ast.content.statement
        assert isinstance(predicate, PredicateCallNode)
        assert predicate.name == 'is_hot'
        assert len(predicate.args) == 1
        arg = predicate.args[0]
        assert isinstance(arg, ConstantNode)
        assert arg.value == 'sun'

    def test_parse_fact_with_number(self, parser):
        """Test parsing a fact with a numeric argument."""
        ast = parser.parse("temperature(25).")
        predicate = ast.content.statement
        assert isinstance(predicate, PredicateCallNode)
        arg = predicate.args[0]
        assert isinstance(arg, ConstantNode)
        assert arg.value == 25
        assert arg.value_type == 'INTEGER'

    def test_parse_comparison_expression(self, parser):
        """Test parsing a comparison expression like 'temperature > 30.'"""
        ast = parser.parse("temperature > 30.")
        comparison = ast.content.statement
        assert isinstance(comparison, ComparisonNode)
        assert comparison.operator == '>'
        assert isinstance(comparison.left, ConstantNode)
        assert comparison.left.value == 'temperature'
        assert isinstance(comparison.right, ConstantNode)
        assert comparison.right.value == 30

    def test_parse_arithmetic_expression(self, parser):
        """Test parsing an arithmetic expression like '(5 + 3) * 2.'"""
        ast = parser.parse("(5 + 3) * 2.")
        op_mul = ast.content.statement
        assert isinstance(op_mul, ArithmeticBinaryOpNode)
        assert op_mul.operator == '*'
        assert isinstance(op_mul.right, ConstantNode)
        assert op_mul.right.value == 2
        op_add = op_mul.left
        assert isinstance(op_add, ArithmeticBinaryOpNode)
        assert op_add.operator == '+'
        assert op_add.left.value == 5
        assert op_add.right.value == 3

    def test_parse_boolean_logic(self, parser):
        """Test parsing a boolean expression with AND."""
        ast = parser.parse("is_hot(X) AND is_sunny(X).")
        op_and = ast.content.statement
        assert isinstance(op_and, BooleanBinaryOpNode)
        assert op_and.operator == 'AND'
        left = op_and.left
        right = op_and.right
        assert isinstance(left, PredicateCallNode)
        assert left.name == 'is_hot'
        assert isinstance(right, PredicateCallNode)
        assert right.name == 'is_sunny'

class TestCNLParserErrorHandling:
    """Tests for parser's error handling capabilities."""

    def test_parse_empty_input(self, parser):
        """Test that parsing an empty string raises ValueError."""
        with pytest.raises(ValueError, match="Input text cannot be empty or whitespace only"):
            parser.parse("")

    def test_parse_whitespace_input(self, parser):
        """Test that parsing a whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Input text cannot be empty or whitespace only"):
            parser.parse("   \t\n  ")

    def test_sentence_must_end_with_period(self, parser):
        """Test that a sentence without a period raises ValueError."""
        with pytest.raises(RuntimeError, match="Sentence must end with period"):
            parser.parse("is_hot(sun)")

    def test_unexpected_token(self, parser):
        """Test that an unexpected token raises a RuntimeError."""
        with pytest.raises(RuntimeError, match="Failed to parse CNL text"):
            parser.parse("is_hot(sun) extra_token.")

    def test_incomplete_expression(self, parser):
        """Test that an incomplete expression raises an error."""
        with pytest.raises(RuntimeError, match="Unexpected end of expression"):
            parser.parse("temperature > .")

class TestCNLParserStateAndCache:
    """Tests for parser's state management and caching."""

    def test_parser_is_available(self, parser):
        """Test that the parser reports itself as available."""
        assert parser.is_available()

    def test_performance_stats(self, parser):
        """Test that performance stats are tracked."""
        parser.parse("a(b).")
        stats = parser.get_performance_stats()
        assert stats['total_parses'] == 1
        assert stats['cache_entries'] == 1

    def test_cache_usage(self, parser):
        """Test that the cache is used for repeated parses."""
        text = "is_cached(true)."
        
        # First parse, should not be a cache hit
        ast1 = parser.parse(text)
        stats1 = parser.get_performance_stats()
        assert stats1['total_parses'] == 1
        assert stats1['cache_entries'] == 1

        # Second parse, should be a cache hit
        ast2 = parser.parse(text)
        stats2 = parser.get_performance_stats()
        assert stats2['total_parses'] == 2
        assert stats2['cache_entries'] == 1 # Cache size doesn't grow
        assert ast1 is ast2 # Should be the same object from cache

    def test_clear_cache(self, parser):
        """Test that the cache can be cleared."""
        parser.parse("some_fact(x).")
        assert parser.get_performance_stats()['cache_entries'] == 1
        parser.clear_cache()
        assert parser.get_performance_stats()['cache_entries'] == 0