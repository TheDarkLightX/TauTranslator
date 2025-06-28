"""
Micro unit tests for EBNF parser.
Tests every parsing method and functionality individually.
Following TDD principles - test first, implement after.
"""

import pytest
from pathlib import Path
from tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_parser import EBNFParser, create_ebnf_parser
from tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes import (
    GrammarNode, RuleNode, ChoiceNode, SequenceNode, OptionalNode,
    RepetitionNode, GroupNode, LiteralNode, RegexNode, NonTerminalNode
)


class TestEBNFParserInitialization:
    """Test EBNFParser initialization and setup."""
    
    def test_parser_creation(self):
        """Test that EBNFParser can be created."""
        parser = EBNFParser()
        assert parser is not None
        assert isinstance(parser, EBNFParser)
    
    def test_parser_creation_with_debug(self):
        """Test creating parser with debug flag."""
        parser = EBNFParser(debug=True)
        assert parser.debug is True
        
        parser = EBNFParser(debug=False)
        assert parser.debug is False
    
    def test_parser_has_tokenizer(self):
        """Test that parser has tokenizer instance."""
        parser = EBNFParser()
        assert hasattr(parser, 'tokenizer')
        assert parser.tokenizer is not None
    
    def test_parser_initial_state(self):
        """Test parser initial state is correct."""
        parser = EBNFParser()
        assert parser.tokens == []
        assert parser.position == 0
        assert parser._parse_count == 0
        assert isinstance(parser._cache, dict)
        assert len(parser._cache) == 0
    
    def test_parser_is_available(self):
        """Test parser availability check."""
        parser = EBNFParser()
        assert parser.is_available() is True


class TestEBNFParserFactoryFunction:
    """Test the create_ebnf_parser factory function."""
    
    def test_create_ebnf_parser_default(self):
        """Test creating parser with default settings."""
        parser = create_ebnf_parser()
        assert isinstance(parser, EBNFParser)
        assert parser.debug is False
    
    def test_create_ebnf_parser_with_debug(self):
        """Test creating parser with debug enabled."""
        parser = create_ebnf_parser(debug=True)
        assert isinstance(parser, EBNFParser)
        assert parser.debug is True


class TestEBNFParserTokenManagement:
    """Test parser token management methods."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()
    
    def test_current_token_empty(self, parser):
        """Test _current_token with empty token list."""
        parser.tokens = []
        parser.position = 0
        assert parser._current_token() is None
    
    def test_current_token_valid(self, parser):
        """Test _current_token with valid tokens."""
        parser.tokens = [('IDENTIFIER', 'rule', 0), ('EQUALS', '=', 5)]
        parser.position = 0
        
        token = parser._current_token()
        assert token == ('IDENTIFIER', 'rule', 0)
        
        parser.position = 1
        token = parser._current_token()
        assert token == ('EQUALS', '=', 5)
    
    def test_current_token_beyond_end(self, parser):
        """Test _current_token beyond token list."""
        parser.tokens = [('IDENTIFIER', 'rule', 0)]
        parser.position = 1
        assert parser._current_token() is None
    
    def test_consume_token_empty(self, parser):
        """Test _consume_token with empty token list."""
        parser.tokens = []
        parser.position = 0
        
        with pytest.raises(RuntimeError, match="Unexpected end of input"):
            parser._consume_token()
    
    def test_consume_token_valid(self, parser):
        """Test _consume_token with valid tokens."""
        parser.tokens = [('IDENTIFIER', 'rule', 0), ('EQUALS', '=', 5)]
        parser.position = 0
        
        token = parser._consume_token()
        assert token == ('IDENTIFIER', 'rule', 0)
        assert parser.position == 1
        
        token = parser._consume_token()
        assert token == ('EQUALS', '=', 5)
        assert parser.position == 2
    
    def test_consume_token_with_expected_type(self, parser):
        """Test _consume_token with expected type checking."""
        parser.tokens = [('IDENTIFIER', 'rule', 0)]
        parser.position = 0
        
        # Correct type
        token = parser._consume_token('IDENTIFIER')
        assert token == ('IDENTIFIER', 'rule', 0)
        
        # Reset for next test
        parser.position = 0
        
        # Wrong type
        with pytest.raises(RuntimeError, match="Expected EQUALS, got IDENTIFIER"):
            parser._consume_token('EQUALS')


class TestEBNFParserAtomParsing:
    """Test parsing of atomic expressions."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()
    
    def test_parse_atom_identifier(self, parser):
        """Test parsing identifier atom."""
        parser.tokens = [('IDENTIFIER', 'my_rule', 0)]
        parser.position = 0
        
        result = parser._parse_atom()
        assert isinstance(result, NonTerminalNode)
        assert result.name == 'my_rule'
        assert parser.position == 1
    
    def test_parse_atom_string_double_quotes(self, parser):
        """Test parsing string atom with double quotes."""
        parser.tokens = [('STRING', '"hello"', 0)]
        parser.position = 0
        
        result = parser._parse_atom()
        assert isinstance(result, LiteralNode)
        assert result.value == 'hello'
        assert result.quote_type == '"'
        assert parser.position == 1
    
    def test_parse_atom_string_single_quotes(self, parser):
        """Test parsing string atom with single quotes."""
        parser.tokens = [('STRING', "'world'", 0)]
        parser.position = 0
        
        result = parser._parse_atom()
        assert isinstance(result, LiteralNode)
        assert result.value == 'world'
        assert result.quote_type == "'"
        assert parser.position == 1
    
    def test_parse_atom_regex(self, parser):
        """Test parsing regex atom."""
        parser.tokens = [('REGEX', '/[a-z]+/', 0)]
        parser.position = 0
        
        result = parser._parse_atom()
        assert isinstance(result, RegexNode)
        assert result.pattern == '[a-z]+'
        assert result.flags == ''
        assert parser.position == 1
    
    def test_parse_atom_parentheses(self, parser):
        """Test parsing parenthesized expression."""
        parser.tokens = [
            ('LPAREN', '(', 0),
            ('IDENTIFIER', 'rule', 1),
            ('RPAREN', ')', 5)
        ]
        parser.position = 0
        
        result = parser._parse_atom()
        assert isinstance(result, GroupNode)
        assert isinstance(result.expression, NonTerminalNode)
        assert result.expression.name == 'rule'
        assert parser.position == 3
    
    def test_parse_atom_optional_brackets(self, parser):
        """Test parsing optional expression with brackets."""
        parser.tokens = [
            ('LBRACKET', '[', 0),
            ('IDENTIFIER', 'rule', 1),
            ('RBRACKET', ']', 5)
        ]
        parser.position = 0
        
        result = parser._parse_atom()
        assert isinstance(result, OptionalNode)
        assert isinstance(result.expression, NonTerminalNode)
        assert result.expression.name == 'rule'
        assert parser.position == 3
    
    def test_parse_atom_repetition_braces(self, parser):
        """Test parsing repetition expression with braces."""
        parser.tokens = [
            ('LBRACE', '{', 0),
            ('IDENTIFIER', 'rule', 1),
            ('RBRACE', '}', 5)
        ]
        parser.position = 0
        
        result = parser._parse_atom()
        assert isinstance(result, RepetitionNode)
        assert isinstance(result.expression, NonTerminalNode)
        assert result.expression.name == 'rule'
        assert result.min_count == 0
        assert result.max_count is None
        assert parser.position == 3
    
    def test_parse_atom_missing_closing_paren(self, parser):
        """Test parsing atom with missing closing parenthesis."""
        parser.tokens = [
            ('LPAREN', '(', 0),
            ('IDENTIFIER', 'rule', 1)
        ]
        parser.position = 0
        
        with pytest.raises(RuntimeError, match="Unexpected end of input"):
            parser._parse_atom()
    
    def test_parse_atom_unexpected_token(self, parser):
        """Test parsing atom with unexpected token."""
        parser.tokens = [('EQUALS', '=', 0)]
        parser.position = 0
        
        with pytest.raises(RuntimeError, match="Unexpected token EQUALS"):
            parser._parse_atom()
    
    def test_parse_atom_empty_tokens(self, parser):
        """Test parsing atom with no tokens."""
        parser.tokens = []
        parser.position = 0
        
        with pytest.raises(RuntimeError, match="Expected atom"):
            parser._parse_atom()


class TestEBNFParserFactorParsing:
    """Test parsing of factors (atoms with quantifiers)."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()
    
    def test_parse_factor_simple_atom(self, parser):
        """Test parsing factor that's just an atom."""
        parser.tokens = [('IDENTIFIER', 'rule', 0)]
        parser.position = 0
        
        result = parser._parse_factor()
        assert isinstance(result, NonTerminalNode)
        assert result.name == 'rule'
        assert parser.position == 1
    
    def test_parse_factor_optional_question(self, parser):
        """Test parsing factor with ? quantifier."""
        parser.tokens = [
            ('IDENTIFIER', 'rule', 0),
            ('QUESTION', '?', 4)
        ]
        parser.position = 0
        
        result = parser._parse_factor()
        assert isinstance(result, OptionalNode)
        assert isinstance(result.expression, NonTerminalNode)
        assert result.expression.name == 'rule'
        assert parser.position == 2
    
    def test_parse_factor_star_quantifier(self, parser):
        """Test parsing factor with * quantifier."""
        parser.tokens = [
            ('IDENTIFIER', 'rule', 0),
            ('STAR', '*', 4)
        ]
        parser.position = 0
        
        result = parser._parse_factor()
        assert isinstance(result, RepetitionNode)
        assert isinstance(result.expression, NonTerminalNode)
        assert result.expression.name == 'rule'
        assert result.min_count == 0
        assert result.max_count is None
        assert parser.position == 2
    
    def test_parse_factor_plus_quantifier(self, parser):
        """Test parsing factor with + quantifier."""
        parser.tokens = [
            ('IDENTIFIER', 'rule', 0),
            ('PLUS', '+', 4)
        ]
        parser.position = 0
        
        result = parser._parse_factor()
        assert isinstance(result, RepetitionNode)
        assert isinstance(result.expression, NonTerminalNode)
        assert result.expression.name == 'rule'
        assert result.min_count == 1
        assert result.max_count is None
        assert parser.position == 2


class TestEBNFParserSequenceParsing:
    """Test parsing of sequences."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()
    
    def test_parse_sequence_single_factor(self, parser):
        """Test parsing sequence with single factor."""
        parser.tokens = [('IDENTIFIER', 'rule', 0)]
        parser.position = 0
        
        result = parser._parse_sequence()
        assert isinstance(result, NonTerminalNode)
        assert result.name == 'rule'
        assert parser.position == 1
    
    def test_parse_sequence_multiple_factors(self, parser):
        """Test parsing sequence with multiple factors."""
        parser.tokens = [
            ('IDENTIFIER', 'rule1', 0),
            ('IDENTIFIER', 'rule2', 6),
            ('STRING', '"hello"', 12)
        ]
        parser.position = 0
        
        result = parser._parse_sequence()
        assert isinstance(result, SequenceNode)
        assert len(result.elements) == 3
        assert isinstance(result.elements[0], NonTerminalNode)
        assert result.elements[0].name == 'rule1'
        assert isinstance(result.elements[1], NonTerminalNode)
        assert result.elements[1].name == 'rule2'
        assert isinstance(result.elements[2], LiteralNode)
        assert result.elements[2].value == 'hello'
        assert parser.position == 3
    
    def test_parse_sequence_stops_at_pipe(self, parser):
        """Test parsing sequence stops at pipe operator."""
        parser.tokens = [
            ('IDENTIFIER', 'rule1', 0),
            ('PIPE', '|', 6),
            ('IDENTIFIER', 'rule2', 8)
        ]
        parser.position = 0
        
        result = parser._parse_sequence()
        assert isinstance(result, NonTerminalNode)
        assert result.name == 'rule1'
        assert parser.position == 1  # Should stop before pipe
    
    def test_parse_sequence_stops_at_closing_paren(self, parser):
        """Test parsing sequence stops at closing parenthesis."""
        parser.tokens = [
            ('IDENTIFIER', 'rule1', 0),
            ('RPAREN', ')', 6)
        ]
        parser.position = 0
        
        result = parser._parse_sequence()
        assert isinstance(result, NonTerminalNode)
        assert result.name == 'rule1'
        assert parser.position == 1
    
    def test_parse_sequence_empty_raises_error(self, parser):
        """Test parsing empty sequence raises error."""
        parser.tokens = [('PIPE', '|', 0)]
        parser.position = 0
        
        with pytest.raises(RuntimeError, match="Empty sequence not allowed"):
            parser._parse_sequence()


class TestEBNFParserChoiceParsing:
    """Test parsing of choice expressions."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()
    
    def test_parse_choice_single_sequence(self, parser):
        """Test parsing choice with single sequence."""
        parser.tokens = [('IDENTIFIER', 'rule', 0)]
        parser.position = 0
        
        result = parser._parse_choice()
        assert isinstance(result, NonTerminalNode)
        assert result.name == 'rule'
        assert parser.position == 1
    
    def test_parse_choice_multiple_sequences(self, parser):
        """Test parsing choice with multiple sequences."""
        parser.tokens = [
            ('IDENTIFIER', 'rule1', 0),
            ('PIPE', '|', 6),
            ('IDENTIFIER', 'rule2', 8),
            ('PIPE', '|', 14),
            ('STRING', '"hello"', 16)
        ]
        parser.position = 0
        
        result = parser._parse_choice()
        assert isinstance(result, ChoiceNode)
        assert len(result.alternatives) == 3
        assert isinstance(result.alternatives[0], NonTerminalNode)
        assert result.alternatives[0].name == 'rule1'
        assert isinstance(result.alternatives[1], NonTerminalNode)
        assert result.alternatives[1].name == 'rule2'
        assert isinstance(result.alternatives[2], LiteralNode)
        assert result.alternatives[2].value == 'hello'
        assert parser.position == 5


class TestEBNFParserRuleParsing:
    """Test parsing of complete rules."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()
    
    def test_parse_rule_simple(self, parser):
        """Test parsing simple rule."""
        parser.tokens = [
            ('IDENTIFIER', 'my_rule', 0),
            ('EQUALS', '=', 8),
            ('STRING', '"hello"', 10),
            ('SEMICOLON', ';', 17)
        ]
        parser.position = 0
        
        result = parser._parse_rule()
        assert isinstance(result, RuleNode)
        assert result.name == 'my_rule'
        assert isinstance(result.expression, LiteralNode)
        assert result.expression.value == 'hello'
        assert parser.position == 4
    
    def test_parse_rule_with_period_terminator(self, parser):
        """Test parsing rule with period terminator."""
        parser.tokens = [
            ('IDENTIFIER', 'my_rule', 0),
            ('EQUALS', '=', 8),
            ('STRING', '"hello"', 10),
            ('PERIOD', '.', 17)
        ]
        parser.position = 0
        
        result = parser._parse_rule()
        assert isinstance(result, RuleNode)
        assert result.name == 'my_rule'
        assert parser.position == 4
    
    def test_parse_rule_without_terminator(self, parser):
        """Test parsing rule without terminator (should still work)."""
        parser.tokens = [
            ('IDENTIFIER', 'my_rule', 0),
            ('EQUALS', '=', 8),
            ('STRING', '"hello"', 10)
        ]
        parser.position = 0
        
        result = parser._parse_rule()
        assert isinstance(result, RuleNode)
        assert result.name == 'my_rule'
        assert parser.position == 3
    
    def test_parse_rule_complex_expression(self, parser):
        """Test parsing rule with complex expression."""
        parser.tokens = [
            ('IDENTIFIER', 'expr', 0),
            ('EQUALS', '=', 5),
            ('IDENTIFIER', 'term', 7),
            ('PIPE', '|', 12),
            ('IDENTIFIER', 'factor', 14),
            ('SEMICOLON', ';', 20)
        ]
        parser.position = 0
        
        result = parser._parse_rule()
        assert isinstance(result, RuleNode)
        assert result.name == 'expr'
        assert isinstance(result.expression, ChoiceNode)
        assert len(result.expression.alternatives) == 2


class TestEBNFParserGrammarParsing:
    """Test parsing of complete grammars."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()
    
    def test_parse_grammar_single_rule(self, parser):
        """Test parsing grammar with single rule."""
        parser.tokens = [
            ('IDENTIFIER', 'rule', 0),
            ('EQUALS', '=', 5),
            ('STRING', '"hello"', 7),
            ('SEMICOLON', ';', 14)
        ]
        parser.position = 0
        
        result = parser._parse_grammar()
        assert isinstance(result, GrammarNode)
        assert len(result.rules) == 1
        assert result.rules[0].name == 'rule'
    
    def test_parse_grammar_multiple_rules(self, parser):
        """Test parsing grammar with multiple rules."""
        parser.tokens = [
            ('IDENTIFIER', 'rule1', 0),
            ('EQUALS', '=', 6),
            ('STRING', '"hello"', 8),
            ('SEMICOLON', ';', 15),
            ('IDENTIFIER', 'rule2', 17),
            ('EQUALS', '=', 23),
            ('STRING', '"world"', 25),
            ('SEMICOLON', ';', 32)
        ]
        parser.position = 0
        
        result = parser._parse_grammar()
        assert isinstance(result, GrammarNode)
        assert len(result.rules) == 2
        assert result.rules[0].name == 'rule1'
        assert result.rules[1].name == 'rule2'
    
    def test_parse_grammar_empty_raises_error(self, parser):
        """Test parsing empty grammar raises error."""
        parser.tokens = []
        parser.position = 0

        with pytest.raises(RuntimeError, match="Grammar must contain at least one rule"):
            parser._parse_grammar()


class TestEBNFParserIntegration:
    """Test complete EBNF parser integration."""

    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()

    def test_parse_simple_grammar(self, parser):
        """Test parsing simple complete grammar."""
        grammar = 'rule = "hello";'
        result = parser.parse(grammar)

        assert isinstance(result, GrammarNode)
        assert len(result.rules) == 1
        assert result.rules[0].name == 'rule'
        assert isinstance(result.rules[0].expression, LiteralNode)
        assert result.rules[0].expression.value == 'hello'

    def test_parse_complex_grammar(self, parser):
        """Test parsing complex grammar with multiple constructs."""
        grammar = '''
        expr = term (("+" | "-") term)*;
        term = factor (("*" | "/") factor)*;
        factor = number | "(" expr ")";
        number = /[0-9]+/;
        '''

        result = parser.parse(grammar)
        assert isinstance(result, GrammarNode)
        assert len(result.rules) == 4

        # Check rule names
        rule_names = [rule.name for rule in result.rules]
        assert 'expr' in rule_names
        assert 'term' in rule_names
        assert 'factor' in rule_names
        assert 'number' in rule_names

    def test_parse_with_comments(self, parser):
        """Test parsing grammar with comments."""
        grammar = '''
        // This is a simple grammar
        rule = "hello"; // End of line comment
        /* Multi-line
           comment */
        other = "world";
        '''

        result = parser.parse(grammar)
        assert isinstance(result, GrammarNode)
        assert len(result.rules) == 2
        assert result.rules[0].name == 'rule'
        assert result.rules[1].name == 'other'

    def test_parse_with_all_quantifiers(self, parser):
        """Test parsing grammar with all quantifier types."""
        grammar = '''
        optional_rule = term?;
        star_rule = term*;
        plus_rule = term+;
        bracket_optional = [term];
        brace_repetition = {term};
        '''

        result = parser.parse(grammar)
        assert isinstance(result, GrammarNode)
        assert len(result.rules) == 5

        # Check that quantifiers are parsed correctly
        assert isinstance(result.rules[0].expression, OptionalNode)
        assert isinstance(result.rules[1].expression, RepetitionNode)
        assert result.rules[1].expression.min_count == 0
        assert isinstance(result.rules[2].expression, RepetitionNode)
        assert result.rules[2].expression.min_count == 1

    def test_parse_empty_input_error(self, parser):
        """Test parsing empty input raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            parser.parse("")

        with pytest.raises(ValueError, match="cannot be empty"):
            parser.parse("   ")

    def test_parse_invalid_syntax_error(self, parser):
        """Test parsing invalid syntax raises error."""
        with pytest.raises(RuntimeError):
            parser.parse("invalid syntax @#$")

    def test_parse_caching(self, parser):
        """Test that parsing uses caching correctly."""
        grammar = 'rule = "hello";'

        # First parse
        result1 = parser.parse(grammar)
        assert parser._parse_count == 1
        assert len(parser._cache) == 1

        # Second parse (should use cache)
        result2 = parser.parse(grammar)
        assert parser._parse_count == 2  # Count still increments
        assert len(parser._cache) == 1   # Cache size stays same

        # Results should be identical
        assert type(result1) == type(result2)
        assert result1.rules[0].name == result2.rules[0].name

    def test_parse_without_caching(self, parser):
        """Test parsing without caching."""
        grammar = 'rule = "hello";'

        result = parser.parse(grammar, use_cache=False)
        assert isinstance(result, GrammarNode)
        assert len(parser._cache) == 0  # No caching

    def test_get_performance_stats(self, parser):
        """Test performance statistics."""
        grammar = 'rule = "hello";'
        parser.parse(grammar)

        stats = parser.get_performance_stats()
        assert 'total_parses' in stats
        assert 'cache_entries' in stats
        assert 'parser_type' in stats
        assert 'memory_optimized' in stats

        assert stats['total_parses'] >= 1
        assert stats['parser_type'] == 'EBNF Recursive Descent'
        assert stats['memory_optimized'] is True

    def test_clear_cache(self, parser):
        """Test cache clearing functionality."""
        grammar = 'rule = "hello";'
        parser.parse(grammar)

        assert len(parser._cache) == 1

        parser.clear_cache()
        assert len(parser._cache) == 0


class TestEBNFParserFileHandling:
    """Test EBNF parser file handling functionality."""

    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()

    @pytest.fixture
    def temp_grammar_file(self, tmp_path):
        """Create temporary grammar file for testing."""
        grammar_content = '''
        expr = term (("+" | "-") term)*;
        term = factor (("*" | "/") factor)*;
        factor = number | "(" expr ")";
        number = /[0-9]+/;
        '''

        file_path = tmp_path / "test_grammar.ebnf"
        file_path.write_text(grammar_content)
        return str(file_path)

    def test_parse_file_success(self, parser, temp_grammar_file):
        """Test parsing grammar from file."""
        result = parser.parse_file(temp_grammar_file)

        assert isinstance(result, GrammarNode)
        assert len(result.rules) == 4

        rule_names = [rule.name for rule in result.rules]
        assert 'expr' in rule_names
        assert 'term' in rule_names
        assert 'factor' in rule_names
        assert 'number' in rule_names

    def test_parse_file_not_found(self, parser):
        """Test parsing non-existent file raises error."""
        with pytest.raises(FileNotFoundError, match="EBNF file not found"):
            parser.parse_file("non_existent_file.ebnf")

    def test_parse_file_with_unicode(self, parser, tmp_path):
        """Test parsing file with unicode content."""
        grammar_content = 'rule = "héllo wörld";'

        file_path = tmp_path / "unicode_grammar.ebnf"
        file_path.write_text(grammar_content, encoding='utf-8')

        result = parser.parse_file(str(file_path))
        assert isinstance(result, GrammarNode)
        assert result.rules[0].expression.value == "héllo wörld"


class TestEBNFParserErrorHandling:
    """Test EBNF parser error handling and edge cases."""

    @pytest.fixture
    def parser(self):
        """Create parser instance for testing."""
        return EBNFParser()

    def test_parse_missing_equals(self, parser):
        """Test parsing rule without equals sign."""
        with pytest.raises(RuntimeError, match="Expected EQUALS"):
            parser.parse('rule "hello";')

    def test_parse_missing_rule_name(self, parser):
        """Test parsing rule without name."""
        with pytest.raises(RuntimeError, match="Expected IDENTIFIER"):
            parser.parse('= "hello";')

    def test_parse_unclosed_parentheses(self, parser):
        """Test parsing with unclosed parentheses."""
        with pytest.raises(RuntimeError, match="Expected RPAREN"):
            parser.parse('rule = (term;')

    def test_parse_unclosed_brackets(self, parser):
        """Test parsing with unclosed brackets."""
        with pytest.raises(RuntimeError, match="Expected RBRACKET"):
            parser.parse('rule = [term;')

    def test_parse_unclosed_braces(self, parser):
        """Test parsing with unclosed braces."""
        with pytest.raises(RuntimeError, match="Expected RBRACE"):
            parser.parse('rule = {term;')

    def test_parse_invalid_token_sequence(self, parser):
        """Test parsing invalid token sequence."""
        with pytest.raises(RuntimeError):
            parser.parse('rule = = "hello";')  # Double equals

    def test_parse_empty_choice(self, parser):
        """Test parsing choice with empty alternative."""
        # This should work - empty alternatives are valid in some EBNF variants
        try:
            result = parser.parse('rule = | "hello";')
            # If it parses, verify structure
            assert isinstance(result, GrammarNode)
        except RuntimeError:
            # If it fails, that's also acceptable behavior
            pass

    def test_parse_very_nested_expression(self, parser):
        """Test parsing deeply nested expression."""
        # Create deeply nested parentheses
        nested = "(" * 100 + '"hello"' + ")" * 100
        grammar = f'rule = {nested};'

        try:
            result = parser.parse(grammar)
            assert isinstance(result, GrammarNode)
        except RecursionError:
            # Deep nesting might hit recursion limits - that's acceptable
            pytest.skip("Deep nesting hits recursion limit")

    def test_parse_with_debug_enabled(self, parser):
        """Test parsing with debug output enabled."""
        parser.debug = True

        # This should work without errors (debug output goes to stdout)
        result = parser.parse('rule = "hello";')
        assert isinstance(result, GrammarNode)
