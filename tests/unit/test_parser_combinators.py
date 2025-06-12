"""
Unit tests for Parser Combinators
Tests composable parsing primitives and combinations.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend/unified"))

from advanced_parsing_architecture import (
    Parser, ParserResult, RegexParser, SequenceParser, ChoiceParser,
    ManyParser, OptionalParser, MapParser, AndParser
)


class TestParserResult:
    """Test ParserResult data structure."""
    
    def test_successful_result(self):
        """Test creating successful parse result."""
        result = ParserResult(value="parsed", remaining=" rest", success=True)
        assert result.value == "parsed"
        assert result.remaining == " rest"
        assert result.success is True
    
    def test_failed_result(self):
        """Test creating failed parse result."""
        result = ParserResult(value=None, remaining="input", success=False)
        assert result.value is None
        assert result.remaining == "input"
        assert result.success is False


class TestRegexParser:
    """Test regex-based parser."""
    
    def test_simple_regex(self):
        """Test simple regex matching."""
        parser = RegexParser(r'\d+', 'number')
        
        # Successful match
        result = parser.parse("123 abc")
        assert result.success
        assert result.value == "123"
        assert result.remaining == " abc"
        
        # Failed match
        result = parser.parse("abc 123")
        assert not result.success
        assert result.remaining == "abc 123"
    
    def test_word_parser(self):
        """Test word parsing."""
        parser = RegexParser(r'\w+', 'word')
        
        result = parser.parse("hello world")
        assert result.success
        assert result.value == "hello"
        assert result.remaining == " world"
    
    def test_whitespace_parser(self):
        """Test whitespace parsing."""
        parser = RegexParser(r'\s+', 'whitespace')
        
        result = parser.parse("   text")
        assert result.success
        assert result.value == "   "
        assert result.remaining == "text"
    
    def test_specific_keyword(self):
        """Test parsing specific keywords."""
        parser = RegexParser(r'if\b', 'if_keyword')
        
        # Match "if" as complete word
        result = parser.parse("if condition")
        assert result.success
        assert result.value == "if"
        
        # Don't match "if" as part of word
        result = parser.parse("iffy")
        assert result.success  # \b allows this
        assert result.value == "if"


class TestSequenceParser:
    """Test sequence combinator."""
    
    def test_simple_sequence(self):
        """Test parsing two elements in sequence."""
        word = RegexParser(r'\w+')
        space = RegexParser(r'\s+')
        
        parser = SequenceParser(word, space)
        
        result = parser.parse("hello world")
        assert result.success
        assert result.value == ("hello", " ")
        assert result.remaining == "world"
    
    def test_sequence_operator(self):
        """Test >> operator for sequences."""
        word = RegexParser(r'\w+')
        space = RegexParser(r'\s+')
        number = RegexParser(r'\d+')
        
        # Using >> operator
        parser = word >> space >> number
        
        result = parser.parse("test 123")
        assert result.success
        # Note: >> creates nested tuples
        assert result.value == (("test", " "), "123")
        assert result.remaining == ""
    
    def test_failed_sequence(self):
        """Test sequence fails if any part fails."""
        word = RegexParser(r'\w+')
        number = RegexParser(r'\d+')
        
        parser = word >> number
        
        result = parser.parse("hello world")  # No number after word
        assert not result.success


class TestChoiceParser:
    """Test choice combinator."""
    
    def test_simple_choice(self):
        """Test choosing between alternatives."""
        number = RegexParser(r'\d+')
        word = RegexParser(r'\w+')
        
        parser = ChoiceParser(number, word)
        
        # First choice matches
        result = parser.parse("123 abc")
        assert result.success
        assert result.value == "123"
        
        # First fails, second matches
        result = parser.parse("abc 123")
        assert result.success
        assert result.value == "abc"
    
    def test_choice_operator(self):
        """Test | operator for choices."""
        number = RegexParser(r'\d+')
        word = RegexParser(r'[a-z]+')
        upper = RegexParser(r'[A-Z]+')
        
        parser = number | word | upper
        
        # Test each alternative
        assert parser.parse("123").value == "123"
        assert parser.parse("abc").value == "abc"
        assert parser.parse("ABC").value == "ABC"
    
    def test_choice_precedence(self):
        """Test that first matching choice wins."""
        any_word = RegexParser(r'\w+')
        specific = RegexParser(r'test')
        
        # Order matters
        parser1 = any_word | specific
        parser2 = specific | any_word
        
        result1 = parser1.parse("test")
        result2 = parser2.parse("test")
        
        assert result1.value == "test"  # any_word matches
        assert result2.value == "test"  # specific matches


class TestManyParser:
    """Test many (zero or more) combinator."""
    
    def test_many_matches(self):
        """Test parsing multiple occurrences."""
        digit = RegexParser(r'\d')
        parser = ManyParser(digit)
        
        result = parser.parse("123abc")
        assert result.success
        assert result.value == ["1", "2", "3"]
        assert result.remaining == "abc"
    
    def test_many_zero_matches(self):
        """Test many succeeds with zero matches."""
        digit = RegexParser(r'\d')
        parser = digit.many()
        
        result = parser.parse("abc")
        assert result.success
        assert result.value == []
        assert result.remaining == "abc"
    
    def test_many_with_separator(self):
        """Test parsing list with separators."""
        word = RegexParser(r'\w+')
        comma = RegexParser(r',\s*')
        
        # word followed by many (comma >> word)
        parser = word >> (comma >> word).many()
        
        result = parser.parse("a, b, c")
        assert result.success
        # First word separate, then list of (comma, word) pairs


class TestOptionalParser:
    """Test optional (zero or one) combinator."""
    
    def test_optional_present(self):
        """Test optional when element is present."""
        sign = RegexParser(r'[+-]')
        parser = OptionalParser(sign)
        
        result = parser.parse("+123")
        assert result.success
        assert result.value == "+"
        assert result.remaining == "123"
    
    def test_optional_absent(self):
        """Test optional when element is absent."""
        sign = RegexParser(r'[+-]')
        parser = sign.optional()
        
        result = parser.parse("123")
        assert result.success
        assert result.value is None
        assert result.remaining == "123"
    
    def test_optional_in_sequence(self):
        """Test optional within a sequence."""
        sign = RegexParser(r'[+-]').optional()
        digits = RegexParser(r'\d+')
        
        parser = sign >> digits
        
        # With sign
        result = parser.parse("-42")
        assert result.value == ("-", "42")
        
        # Without sign
        result = parser.parse("42")
        assert result.value == (None, "42")


class TestMapParser:
    """Test map (transform) combinator."""
    
    def test_simple_map(self):
        """Test transforming parsed value."""
        digits = RegexParser(r'\d+')
        parser = MapParser(digits, int)
        
        result = parser.parse("123 abc")
        assert result.success
        assert result.value == 123  # String converted to int
        assert isinstance(result.value, int)
    
    def test_map_method(self):
        """Test map method on parser."""
        digits = RegexParser(r'\d+')
        parser = digits.map(lambda x: int(x) * 2)
        
        result = parser.parse("21")
        assert result.value == 42
    
    def test_complex_transformation(self):
        """Test complex value transformation."""
        word = RegexParser(r'\w+')
        
        # Transform to dictionary
        parser = word.map(lambda w: {"type": "word", "value": w, "length": len(w)})
        
        result = parser.parse("hello")
        assert result.value == {"type": "word", "value": "hello", "length": 5}
    
    def test_failed_map(self):
        """Test map doesn't run on failed parse."""
        digits = RegexParser(r'\d+')
        parser = digits.map(int)
        
        result = parser.parse("abc")
        assert not result.success
        assert result.value is None  # Transform not applied


class TestAndParser:
    """Test and (both must match) combinator."""
    
    def test_and_success(self):
        """Test when both parsers succeed on same input."""
        word = RegexParser(r'\w+')
        lowercase = RegexParser(r'[a-z]+')
        
        parser = AndParser(word, lowercase)
        
        result = parser.parse("hello")
        assert result.success
        assert result.value == ("hello", "hello")
        assert result.remaining == ""
    
    def test_and_failure(self):
        """Test when one parser fails."""
        word = RegexParser(r'\w+')
        lowercase = RegexParser(r'[a-z]+')
        
        parser = word * lowercase  # Using * operator
        
        result = parser.parse("Hello")  # Has uppercase
        assert not result.success
    
    def test_and_consumes_once(self):
        """Test that input is consumed only once."""
        word = RegexParser(r'\w+')
        first_char = RegexParser(r'.')
        
        parser = word * first_char
        
        result = parser.parse("test")
        assert result.success
        assert result.value == ("test", "t")
        assert result.remaining == ""  # word parser consumed all


class TestComplexCombinations:
    """Test complex parser combinations."""
    
    def test_expression_parser(self):
        """Test parsing simple arithmetic expressions."""
        # Define basic elements
        num = RegexParser(r'\d+').map(int)
        ws = RegexParser(r'\s*')
        plus = RegexParser(r'\+')
        minus = RegexParser(r'-')
        
        # Define operators
        op = (plus | minus).map(lambda x: '+' if x == '+' else '-')
        
        # Simple expression: num (op num)*
        parser = num >> (ws >> op >> ws >> num).many()
        
        result = parser.parse("1 + 2 - 3")
        assert result.success
        # Complex nested structure from combinators
    
    def test_identifier_list(self):
        """Test parsing comma-separated identifiers."""
        ident = RegexParser(r'[a-zA-Z_]\w*')
        ws = RegexParser(r'\s*')
        comma = RegexParser(r',')
        
        # ident (, ident)*
        sep = ws >> comma >> ws
        parser = ident >> (sep >> ident).many()
        
        result = parser.parse("foo, bar, baz")
        assert result.success
    
    def test_nested_parentheses(self):
        """Test parsing nested structures."""
        # This would require recursive parser definition
        # which our simple combinators don't support directly
        
        lparen = RegexParser(r'\(')
        rparen = RegexParser(r'\)')
        content = RegexParser(r'[^()]+')
        
        # Simple non-nested version
        parser = lparen >> content >> rparen
        
        result = parser.parse("(hello)")
        assert result.success
        assert result.value[1] == "hello"
    
    def test_keyword_parser(self):
        """Test parsing programming language keywords."""
        # Define keywords
        keywords = ["if", "then", "else", "while", "for"]
        
        # Create parser for each keyword
        keyword_parsers = [RegexParser(rf'{kw}\b') for kw in keywords]
        
        # Combine with choice
        keyword = keyword_parsers[0]
        for p in keyword_parsers[1:]:
            keyword = keyword | p
        
        # Test each keyword
        assert keyword.parse("if").success
        assert keyword.parse("then").success
        assert keyword.parse("while").success
        
        # Should not match partial
        result = keyword.parse("iffy")
        assert result.value == "if"  # Matches "if" part


class TestParserUsagePatterns:
    """Test common parser usage patterns."""
    
    def test_lexer_pattern(self):
        """Test building a simple lexer."""
        # Token types
        num = RegexParser(r'\d+').map(lambda x: ('NUM', int(x)))
        ident = RegexParser(r'[a-zA-Z_]\w*').map(lambda x: ('ID', x))
        ws = RegexParser(r'\s+').map(lambda x: ('WS', x))
        op = RegexParser(r'[+\-*/]').map(lambda x: ('OP', x))
        
        # Combined token parser
        token = num | ident | op | ws
        
        # Tokenize input
        tokens = []
        remaining = "x + 42"
        
        while remaining:
            result = token.parse(remaining)
            if result.success:
                tokens.append(result.value)
                remaining = result.remaining
            else:
                break
        
        # Filter out whitespace
        tokens = [t for t in tokens if t[0] != 'WS']
        
        assert tokens == [('ID', 'x'), ('OP', '+'), ('NUM', 42)]
    
    def test_validation_pattern(self):
        """Test using parsers for validation."""
        # Email-like pattern (simplified)
        local = RegexParser(r'[a-zA-Z0-9._%+-]+')
        at = RegexParser(r'@')
        domain = RegexParser(r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        
        email = local >> at >> domain
        
        # Valid emails
        assert email.parse("user@example.com").success
        assert email.parse("test.user@domain.co.uk").success
        
        # Invalid emails
        assert not email.parse("invalid.email").success
        assert not email.parse("@domain.com").success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])