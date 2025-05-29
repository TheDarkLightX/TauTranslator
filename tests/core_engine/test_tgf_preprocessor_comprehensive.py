"""Comprehensive tests for the TGF preprocessor module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from tau_translator_omega.core_engine.tgf_preprocessor import TGFPreprocessor
from tau_translator_omega.core_engine.tgf_directive_handler import TGFDirectiveHandler
from tau_translator_omega.core_engine.preprocessor_errors import CircularIncludeError, MacroExpansionError, ConditionalDirectiveError, IncludeFileNotFoundError


class TestTGFPreprocessorComprehensive:
    """Comprehensive tests for TGF preprocessor functionality."""

    @pytest.fixture
    def preprocessor(self):
        """Create a preprocessor instance for testing."""
        return TGFPreprocessor("") # Provide default empty string for initial_input

    @pytest.fixture
    def sample_grammar(self):
        """Sample grammar content for testing."""
        return """
        // Basic grammar rules
        start: expression
        
        expression: term ((PLUS | MINUS) term)*
        term: factor ((MUL | DIV) factor)*
        factor: NUMBER | LPAREN expression RPAREN
        
        // Terminals
        NUMBER: /[0-9]+/
        PLUS: "+"
        MINUS: "-"
        MUL: "*"
        DIV: "/"
        LPAREN: "("
        RPAREN: ")"
        
        %import common.WS
        %ignore WS
        """

    def test_preprocessor_initialization(self):
        """Test preprocessor initialization."""
        preprocessor = TGFPreprocessor("")
        assert preprocessor.directive_handler is not None
        assert isinstance(preprocessor.directive_handler, TGFDirectiveHandler)
        assert preprocessor.visited_files == set()

    def test_preprocess_simple_grammar(self, preprocessor, sample_grammar):
        """Test preprocessing a simple grammar without directives."""
        result = preprocessor.preprocess(sample_grammar)
        
        # Should return the grammar unchanged if no directives
        assert "start:" in result
        assert "expression:" in result
        assert "NUMBER:" in result

    def test_preprocess_with_conditional_directives(self, preprocessor):
        """Test preprocessing with conditional compilation directives."""
        grammar = """
        #define ENABLE_ADVANCED_FEATURES
        
        start: basic_expr
        
        #ifdef ENABLE_ADVANCED_FEATURES
        basic_expr: advanced_expr
        advanced_expr: function_call | array_access | basic_expr
        function_call: identifier LPAREN args? RPAREN
        array_access: identifier LSQB expression RSQB
        #else
        basic_expr: identifier | NUMBER
        #endif
        
        identifier: /[a-zA-Z_][a-zA-Z0-9_]*/
        NUMBER: /[0-9]+/
        """
        
        result = preprocessor.preprocess(grammar)
        
        assert "advanced_expr:" in result
        assert "function_call:" in result
        assert "array_access:" in result
        assert "#ifdef" not in result
        assert "#else" not in result
        assert "#endif" not in result

    def test_preprocess_with_macro_definitions(self, preprocessor):
        """Test preprocessing with macro definitions and expansions."""
        grammar = """
        #define DIGIT /[0-9]/
        #define LETTER /[a-zA-Z]/
        #define ALPHANUM (LETTER | DIGIT)
        
        start: identifier
        identifier: LETTER ALPHANUM*
        
        // Terminals use macros
        number: DIGIT+
        """
        
        result = preprocessor.preprocess(grammar)
        
        # Macros should be expanded
        assert "/[a-zA-Z]/" in result
        assert "/[0-9]/" in result
        assert "DIGIT" not in result or "#define" in result  # Raw macro name shouldn't appear
        assert "LETTER" not in result or "#define" in result

    def test_preprocess_conditional_nesting(self, preprocessor):
        """Test nested conditional directives."""
        grammar = """
        #define FEATURE_A
        #define FEATURE_B
        
        start: expr
        
        #ifdef FEATURE_A
            expr: advanced_expr
            #ifdef FEATURE_B
                advanced_expr: super_advanced_expr
                super_advanced_expr: quantum_expr | advanced_expr
            #else
                advanced_expr: basic_expr "+" basic_expr
            #endif
        #else
            expr: basic_expr
        #endif
        
        basic_expr: NUMBER
        NUMBER: /[0-9]+/
        """
        
        result = preprocessor.preprocess(grammar)
        
        assert "super_advanced_expr:" in result
        assert "quantum_expr" in result

    def test_preprocess_ifndef_directive(self, preprocessor):
        """Test #ifndef directive."""
        grammar = """
        #ifndef SIMPLE_MODE
        #define COMPLEX_MODE
        
        // Complex grammar rules
        start: complex_expr
        complex_expr: nested_expr | function_expr
        #endif
        
        #ifdef SIMPLE_MODE
        start: simple_expr
        simple_expr: NUMBER
        #endif
        
        NUMBER: /[0-9]+/
        """
        
        result = preprocessor.preprocess(grammar)
        
        assert "complex_expr:" in result
        assert "simple_expr" not in result

    def test_preprocess_undef_directive(self, preprocessor):
        """Test #undef directive."""
        grammar = """
        #define TEMP_FEATURE
        
        #ifdef TEMP_FEATURE
        temp_rule: "temporary"
        #endif
        
        #undef TEMP_FEATURE
        
        #ifdef TEMP_FEATURE
        should_not_appear: "this should not be in output"
        #endif
        
        start: temp_rule?
        """
        
        result = preprocessor.preprocess(grammar)
        
        assert "temp_rule:" in result
        assert "should_not_appear" not in result

    def test_preprocess_with_comments(self, preprocessor):
        """Test preprocessing preserves comments correctly."""
        grammar = """
        // Single line comment
        start: expression  // End of line comment
        
        /* Multi-line
           comment */
        expression: term ((PLUS | MINUS) term)*
        
        /* Another comment */ term: NUMBER
        """
        
        result = preprocessor.preprocess(grammar)
        
        # Comments should be preserved
        assert "Single line comment" in result
        assert "End of line comment" in result
        assert "Multi-line" in result

    def test_preprocess_error_handling(self, preprocessor):
        """Test error handling in preprocessing."""
        # Test unmatched endif
        with pytest.raises(Exception):
            preprocessor.preprocess("#endif")
        
        # Test unmatched else
        with pytest.raises(Exception):
            preprocessor.preprocess("#else")
        
        # Test missing endif
        with pytest.raises(Exception):
            preprocessor.preprocess("#ifdef SOMETHING\nrule: test")

    def test_preprocess_line_continuation(self, preprocessor):
        """Test handling of line continuation."""
        grammar = """
        #define LONG_PATTERN /[a-zA-Z0-9_\\
                               \\-\\.\\@\\#\\$\\%\\^\\&\\*\\(\\)\\[\\]\\{\\}]+/
        
        start: LONG_PATTERN
        """
        
        result = preprocessor.preprocess(grammar)
        
        # Line continuation should be handled
        assert result.count("\\") < grammar.count("\\")  # Some backslashes processed

    def test_preprocess_with_pragma_directives(self, preprocessor):
        """Test handling of pragma directives."""
        grammar = """
        #pragma once
        #pragma option strict_mode
        
        start: expression
        expression: NUMBER
        NUMBER: /[0-9]+/
        """
        
        result = preprocessor.preprocess(grammar)
        
        # Pragma directives might be handled specially or ignored
        assert "start:" in result
        assert "expression:" in result

    def test_preprocess_macro_with_parameters(self, preprocessor):
        """Test macros with parameters."""
        grammar = """
        #define REPEAT(rule, sep) rule (sep rule)*
        #define LIST(item) REPEAT(item, COMMA)
        
        start: LIST(expression)
        expression: NUMBER | STRING
        
        NUMBER: /[0-9]+/
        STRING: /"[^"]*"/
        COMMA: ","
        """
        
        result = preprocessor.preprocess(grammar)
        
        # Parameterized macros should be expanded
        assert "expression (COMMA expression)*" in result or "expression (\",\" expression)*" in result

    def test_preprocess_with_complex_conditions(self, preprocessor):
        """Test complex conditional expressions."""
        grammar = """
        #define FEATURE_A
        #define FEATURE_B
        
        #if defined(FEATURE_A) && defined(FEATURE_B)
        rule_ab: "both features"
        #elif defined(FEATURE_A)
        rule_a: "only feature A"
        #elif defined(FEATURE_B)
        rule_b: "only feature B"
        #else
        rule_none: "no features"
        #endif
        
        start: rule_ab
        """
        
        result = preprocessor.preprocess(grammar)
        
        assert "rule_ab:" in result
        assert "rule_a:" not in result
        assert "rule_b:" not in result
        assert "rule_none:" not in result

    def test_preprocess_with_empty_file(self, preprocessor):
        """Test preprocessing empty content."""
        result = preprocessor.preprocess("")
        assert result == ""

    def test_preprocess_with_only_directives(self, preprocessor):
        """Test preprocessing file with only directives."""
        grammar = """
        #define VERSION "1.0.0"
        #define AUTHOR "Test"
        #ifdef DEBUG
        #define LOG_LEVEL "verbose"
        #endif
        """
        
        result = preprocessor.preprocess(grammar)
        
        # Should handle gracefully even with no actual grammar rules
        assert isinstance(result, str)