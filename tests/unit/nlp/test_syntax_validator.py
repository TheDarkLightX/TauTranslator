"""
Unit tests for the SyntaxValidator class from the NLP module.

Copyright: DarkLightX / Dana Edwards
"""

import pytest

from backend.unified.api.nlp import (
    CodeText,
    LineNumber,
    ErrorMessage,
    SeverityLevel,
    SyntaxValidator
)

from backend.unified.core.semantic_validator import ValidationError
from backend.unified.core.error_handling import ErrorType

class TestSyntaxValidator:
    """Test the SyntaxValidator class following AAA pattern."""
    
    def test_validate_parentheses_WhenBalanced_ReturnsNone(self):
        # Given: A line with balanced parentheses
        line = CodeText("print(hello(world))")
        line_number = LineNumber(1)
        
        # When: Validating parentheses
        result = SyntaxValidator.validate_parentheses(line, line_number)
        
        # Then: No error is returned
        assert result is None
    
    def test_validate_parentheses_WhenUnbalanced_ReturnsError(self):
        # Given: A line with unbalanced parentheses
        line = CodeText("print(hello(world)")
        line_number = LineNumber(5)
        
        # When: Validating parentheses
        result = SyntaxValidator.validate_parentheses(line, line_number)
        
        # Then: An error is returned with correct details
        assert result is not None
        assert isinstance(result, ValidationError)
        assert result.message == ErrorMessage("Unmatched parentheses")
        assert result.error_type == ErrorType.SYNTAX_ERROR
        assert result.suggestion == 'Check parentheses balance.'
        assert result.confidence == 0.9
    
    def test_validate_brackets_WhenBalanced_ReturnsNone(self):
        # Given: A line with balanced brackets
        line = CodeText("array[index[0]]")
        line_number = LineNumber(1)
        
        # When: Validating brackets
        result = SyntaxValidator.validate_brackets(line, line_number)
        
        # Then: No error is returned
        assert result is None
    
    def test_validate_brackets_WhenUnbalanced_ReturnsError(self):
        # Given: A line with unbalanced brackets
        line = CodeText("array[index[0]")
        line_number = LineNumber(3)
        
        # When: Validating brackets
        result = SyntaxValidator.validate_brackets(line, line_number)
        
        # Then: An error is returned
        assert result is not None
        assert isinstance(result, ValidationError)
        assert result.message == ErrorMessage("Unmatched brackets")
        assert result.error_type == ErrorType.SYNTAX_ERROR
        assert result.suggestion == 'Check bracket balance.'
        assert result.confidence == 0.9
    
    @pytest.mark.parametrize("line,keyword,should_warn", [
        ("DEFINE x := true", "DEFINE", False),  # Has operator
        ("always x -> y", "always", False),      # Has operator
        ("forall x", "forall", True),           # No operator
        ("exists y", "exists", True),           # No operator
    ])
    def test_check_keyword_usage_WithVariousInputs_ReturnsWarningOrNone(self, line, keyword, should_warn):
        # Given: A line with a TAU keyword
        code_line = CodeText(line)
        line_number = LineNumber(1)
        
        # When: Checking keyword usage
        result = SyntaxValidator.check_keyword_usage(code_line, line_number)
        
        # Then: Warning is returned based on operator presence
        if should_warn:
            assert result is not None
            assert f"Keyword '{keyword}' found without a corresponding operator." in result.message
            assert result.error_type == ErrorType.SYNTAX_WARNING
        else:
            assert result is None
