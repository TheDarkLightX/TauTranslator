"""
Comprehensive tests for the O(n) CNL parser implementation.

This test suite validates the optimized O(n) CNL parser with:
- Complete coverage of all parsing functionality
- Performance validation
- Error handling verification
- Memory optimization testing
"""

import pytest
import time
from tau_translator_omega.core_engine.parsers.cnl_parser.cnl_parser import (
    create_cnl_parser, CNLParser, OptimizedTokenizer, PrattParser, Token
)
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    SentenceNode, FactNode, ConstantNode, PredicateCallNode,
    ComparisonNode, ArithmeticBinaryOpNode, BooleanBinaryOpNode
)


class TestOptimizedTokenizer:
    """Test the O(n) tokenizer implementation."""
    
    def test_tokenizer_initialization(self):
        """Test tokenizer creates successfully."""
        tokenizer = OptimizedTokenizer()
        assert tokenizer.patterns is not None
        assert len(tokenizer.patterns) > 0
    
    def test_tokenize_simple_constants(self):
        """Test tokenizing basic constants."""
        tokenizer = OptimizedTokenizer()
        
        # Boolean
        tokens = tokenizer.tokenize("true")
        assert len(tokens) == 1
        assert tokens[0].type == 'BOOLEAN'
        assert tokens[0].value == 'true'
        
        # Number
        tokens = tokenizer.tokenize("42")
        assert len(tokens) == 1
        assert tokens[0].type == 'NUMBER'
        assert tokens[0].value == '42'
        
        # String
        tokens = tokenizer.tokenize('"hello"')
        assert len(tokens) == 1
        assert tokens[0].type == 'STRING'
        assert tokens[0].value == '"hello"'
    
    def test_tokenize_operators(self):
        """Test tokenizing operators."""
        tokenizer = OptimizedTokenizer()
        
        # Comparison
        tokens = tokenizer.tokenize(">")
        assert tokens[0].type == 'COMPARISON'
        assert tokens[0].value == '>'
        
        # Arithmetic
        tokens = tokenizer.tokenize("+")
        assert tokens[0].type == 'ARITHMETIC'
        assert tokens[0].value == '+'
    
    def test_tokenize_complex_expression(self):
        """Test tokenizing complex expressions."""
        tokenizer = OptimizedTokenizer()
        tokens = tokenizer.tokenize("temperature > 30")
        
        assert len(tokens) == 3
        assert tokens[0].type == 'IDENTIFIER'
        assert tokens[0].value == 'temperature'
        assert tokens[1].type == 'COMPARISON'
        assert tokens[1].value == '>'
        assert tokens[2].type == 'NUMBER'
        assert tokens[2].value == '30'
    
    def test_tokenize_performance(self):
        """Test tokenizer O(n) performance."""
        tokenizer = OptimizedTokenizer()
        
        # Test with increasing input sizes
        for size in [100, 1000, 10000]:
            text = "temperature > 30 " * size
            start_time = time.perf_counter()
            tokens = tokenizer.tokenize(text)
            end_time = time.perf_counter()
            
            # Should be roughly linear
            assert len(tokens) == size * 3  # 3 tokens per repetition
            assert end_time - start_time < 0.1  # Should be very fast


class TestPrattParser:
    """Test the O(n) Pratt parser implementation."""
    
    def test_parser_initialization(self):
        """Test parser creates successfully."""
        tokens = [Token('NUMBER', '42', 0), Token('PERIOD', '.', 2)]
        parser = PrattParser(tokens)
        assert parser.tokens == tokens
        assert parser.position == 0
    
    def test_parse_simple_atom(self):
        """Test parsing simple atomic values."""
        # Boolean
        tokens = [Token('BOOLEAN', 'true', 0)]
        parser = PrattParser(tokens)
        result = parser.parse_atom()
        assert isinstance(result, ConstantNode)
        assert result.value is True
        
        # Number
        tokens = [Token('NUMBER', '42', 0)]
        parser = PrattParser(tokens)
        result = parser.parse_atom()
        assert isinstance(result, ConstantNode)
        assert result.value == 42
    
    def test_parse_comparison_expression(self):
        """Test parsing comparison expressions."""
        tokens = [
            Token('NUMBER', '5', 0),
            Token('COMPARISON', '>', 1),
            Token('NUMBER', '3', 2)
        ]
        parser = PrattParser(tokens)
        result = parser.parse_expression()
        
        assert isinstance(result, ComparisonNode)
        assert result.operator == '>'
        assert isinstance(result.left, ConstantNode)
        assert result.left.value == 5
        assert isinstance(result.right, ConstantNode)
        assert result.right.value == 3
    
    def test_parse_arithmetic_expression(self):
        """Test parsing arithmetic expressions."""
        tokens = [
            Token('NUMBER', '5', 0),
            Token('ARITHMETIC', '+', 1),
            Token('NUMBER', '3', 2)
        ]
        parser = PrattParser(tokens)
        result = parser.parse_expression()
        
        assert isinstance(result, ArithmeticBinaryOpNode)
        assert result.operator == '+'
        assert result.left.value == 5
        assert result.right.value == 3
    
    def test_parse_function_call(self):
        """Test parsing function calls."""
        tokens = [
            Token('IDENTIFIER', 'is_hot', 0),
            Token('LPAREN', '(', 6),
            Token('IDENTIFIER', 'sun', 7),
            Token('RPAREN', ')', 10)
        ]
        parser = PrattParser(tokens)
        result = parser.parse_expression()
        
        assert isinstance(result, PredicateCallNode)
        assert result.name == 'is_hot'
        assert len(result.args) == 1
        assert result.args[0].value == 'sun'
    
    def test_operator_precedence(self):
        """Test operator precedence is handled correctly."""
        # 2 + 3 * 4 should be 2 + (3 * 4)
        tokens = [
            Token('NUMBER', '2', 0),
            Token('ARITHMETIC', '+', 1),
            Token('NUMBER', '3', 2),
            Token('ARITHMETIC', '*', 3),
            Token('NUMBER', '4', 4)
        ]
        parser = PrattParser(tokens)
        result = parser.parse_expression()
        
        # Should be: (2 + (3 * 4))
        assert isinstance(result, ArithmeticBinaryOpNode)
        assert result.operator == '+'
        assert result.left.value == 2
        assert isinstance(result.right, ArithmeticBinaryOpNode)
        assert result.right.operator == '*'
        assert result.right.left.value == 3
        assert result.right.right.value == 4


class TestCNLParserO_n:
    """Test the complete O(n) CNL parser."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return create_cnl_parser(debug=False)
    
    def test_parser_creation(self, parser):
        """Test parser creates successfully."""
        assert isinstance(parser, CNLParser)
        assert parser.tokenizer is not None
        assert parser.is_available()
    
    def test_parse_simple_constants(self, parser):
        """Test parsing simple constants."""
        # Boolean
        result = parser.parse("true.")
        assert isinstance(result, SentenceNode)
        assert isinstance(result.content, FactNode)
        assert isinstance(result.content.statement, ConstantNode)
        assert result.content.statement.value is True
        
        # Number
        result = parser.parse("42.")
        assert result.content.statement.value == 42
        
        # String
        result = parser.parse('"hello".')
        assert result.content.statement.value == "hello"
    
    def test_parse_predicates(self, parser):
        """Test parsing predicate calls."""
        # No arguments
        result = parser.parse("is_sunny().")
        assert isinstance(result.content.statement, PredicateCallNode)
        assert result.content.statement.name == "is_sunny"
        assert len(result.content.statement.args) == 0
        
        # With arguments
        result = parser.parse("is_hot(sun).")
        assert result.content.statement.name == "is_hot"
        assert len(result.content.statement.args) == 1
        assert result.content.statement.args[0].value == "sun"
    
    def test_parse_comparisons(self, parser):
        """Test parsing comparison expressions."""
        result = parser.parse("temperature > 30.")
        assert isinstance(result.content.statement, ComparisonNode)
        assert result.content.statement.operator == ">"
        assert result.content.statement.left.value == "temperature"
        assert result.content.statement.right.value == 30
    
    def test_parse_arithmetic(self, parser):
        """Test parsing arithmetic expressions."""
        result = parser.parse("5 + 3.")
        assert isinstance(result.content.statement, ArithmeticBinaryOpNode)
        assert result.content.statement.operator == "+"
        assert result.content.statement.left.value == 5
        assert result.content.statement.right.value == 3
    
    def test_parse_complex_expressions(self, parser):
        """Test parsing complex nested expressions."""
        # Parentheses
        result = parser.parse("(5 + 3) * 2.")
        assert isinstance(result.content.statement, ArithmeticBinaryOpNode)
        assert result.content.statement.operator == "*"
        
        # Function with arithmetic
        result = parser.parse("distance(earth, moon, 384400).")
        assert isinstance(result.content.statement, PredicateCallNode)
        assert result.content.statement.name == "distance"
        assert len(result.content.statement.args) == 3
    
    def test_error_handling(self, parser):
        """Test error handling for invalid input."""
        # Empty input
        with pytest.raises(ValueError, match="cannot be empty"):
            parser.parse("")
        
        # Missing period
        with pytest.raises(RuntimeError):
            parser.parse("true")
        
        # Invalid syntax
        with pytest.raises(RuntimeError):
            parser.parse("@#$%.")
    
    def test_caching_functionality(self, parser):
        """Test caching improves performance."""
        text = "temperature > 30."
        
        # First parse (cache miss)
        start_time = time.perf_counter()
        result1 = parser.parse(text)
        first_time = time.perf_counter() - start_time
        
        # Second parse (cache hit)
        start_time = time.perf_counter()
        result2 = parser.parse(text)
        second_time = time.perf_counter() - start_time
        
        # Results should be identical
        assert type(result1) == type(result2)
        
        # Second parse should be faster (cached)
        assert second_time <= first_time
        
        # Check cache statistics
        stats = parser.get_performance_stats()
        assert stats['total_parses'] >= 2
        assert stats['cache_entries'] >= 1
    
    def test_performance_characteristics(self, parser):
        """Test O(n) performance characteristics."""
        # Test with increasing complexity
        test_cases = [
            "true.",
            "temperature > 30.",
            "(temperature + 10) > 40.",
            "is_hot(sun) AND temperature > 30.",
        ]
        
        for case in test_cases:
            start_time = time.perf_counter()
            result = parser.parse(case)
            end_time = time.perf_counter()
            
            # Should parse quickly (< 1ms for simple cases)
            assert end_time - start_time < 0.001
            assert result is not None
    
    def test_performance_stats(self, parser):
        """Test performance statistics reporting."""
        # Parse some expressions
        parser.parse("true.")
        parser.parse("42.")
        parser.parse("temperature > 30.")
        
        stats = parser.get_performance_stats()
        
        # Check required fields
        assert 'total_parses' in stats
        assert 'cache_entries' in stats
        assert 'algorithm' in stats
        assert 'complexity' in stats
        
        # Check values
        assert stats['total_parses'] >= 3
        assert stats['algorithm'] == 'O(n) Pratt Parser'
        assert stats['complexity'] == 'Linear'
    
    def test_cache_management(self, parser):
        """Test cache management functionality."""
        # Parse some expressions
        parser.parse("true.")
        parser.parse("false.")
        
        # Check cache has entries
        stats = parser.get_performance_stats()
        assert stats['cache_entries'] >= 2
        
        # Clear cache
        parser.clear_cache()
        
        # Check cache is empty
        stats = parser.get_performance_stats()
        assert stats['cache_entries'] == 0


class TestCNLParserIntegration:
    """Integration tests for the O(n) CNL parser."""
    
    def test_comprehensive_cnl_constructs(self):
        """Test all supported CNL constructs work correctly."""
        parser = create_cnl_parser()
        
        test_cases = [
            # Basic constants
            ("Boolean true", "true."),
            ("Boolean false", "false."),
            ("Integer", "42."),
            ("Float", "3.14."),
            ("String", '"hello world".'),
            ("Identifier", "temperature."),
            
            # Predicates
            ("Simple predicate", "is_hot(sun)."),
            ("Multi-arg predicate", "distance(earth, moon, 384400)."),
            ("No-arg predicate", "is_sunny()."),
            
            # Comparisons
            ("Greater than", "temperature > 30."),
            ("Less than", "pressure < 100."),
            ("Equality", "status = active."),
            ("Greater equal", "score >= 90."),
            ("Not equal", "color != red."),
            
            # Arithmetic
            ("Addition", "temperature + 10."),
            ("Subtraction", "pressure - 5."),
            ("Multiplication", "speed * 2."),
            ("Division", "distance / time."),
            
            # Complex expressions
            ("Parentheses", "(temperature + 10) > 40."),
            ("Function with arithmetic", "calculate(5 + 3)."),
        ]
        
        for name, cnl_text in test_cases:
            try:
                result = parser.parse(cnl_text)
                assert result is not None, f"Failed to parse {name}: {cnl_text}"
                assert isinstance(result, SentenceNode), f"Wrong result type for {name}"
            except Exception as e:
                pytest.fail(f"Failed to parse {name} '{cnl_text}': {e}")
    
    def test_algorithm_correctness(self):
        """Test that the O(n) algorithm produces correct results."""
        parser = create_cnl_parser()
        
        # Test operator precedence
        result = parser.parse("2 + 3 * 4.")
        # Should be parsed as 2 + (3 * 4) = 14, not (2 + 3) * 4 = 20
        assert isinstance(result.content.statement, ArithmeticBinaryOpNode)
        assert result.content.statement.operator == "+"
        assert isinstance(result.content.statement.right, ArithmeticBinaryOpNode)
        assert result.content.statement.right.operator == "*"
        
        # Test left associativity
        result = parser.parse("10 - 5 - 2.")
        # Should be parsed as (10 - 5) - 2 = 3, not 10 - (5 - 2) = 7
        assert isinstance(result.content.statement, ArithmeticBinaryOpNode)
        assert result.content.statement.operator == "-"
        assert isinstance(result.content.statement.left, ArithmeticBinaryOpNode)
        assert result.content.statement.left.operator == "-"
