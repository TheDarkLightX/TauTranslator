"""
Unit tests for edge cases and boundary conditions in the NLP module.

Copyright: DarkLightX / Dana Edwards
"""

import pytest

from backend.unified.api.nlp import (
    ValidationService,
    SyntaxValidator,
    CodeLineProcessor,
    CodeText,
    TauConstants,
    SuggestionGenerator,
    ValidationError,
    ErrorMessage,
    SeverityLevel,
    LineNumber # Though not directly instantiated, it's part of ValidationError's signature
)

from returns.result import Success

class TestEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions."""

    def test_validation_WithDeeplyNestedParentheses_IsValid(self):
        # Given: Deeply nested but balanced parentheses
        service = ValidationService(SyntaxValidator(), CodeLineProcessor())
        code = CodeText("((((((((((x))))))))))")

        # When: Validating
        result = service.validate_code(code)

        # Then: Should pass (is_valid is True)
        assert isinstance(result, Success) is True

    def test_validation_WithMixedBracketAndParentheses_IsValid(self):
        # Given: Mixed brackets and parentheses, correctly nested
        service = ValidationService(SyntaxValidator(), CodeLineProcessor())
        code = CodeText("array[func(x[0])]")

        # When: Validating
        result = service.validate_code(code)

        # Then: Should pass (is_valid is True)
        assert isinstance(result, Success) is True

    def test_suggestion_generation_WhenConstantsAreEmpty_ReturnsEmptyListGracefully(self):
        # Given: TauConstants.KEYWORDS is temporarily empty (edge case)
        original_keywords = TauConstants.KEYWORDS
        TauConstants.KEYWORDS = frozenset()

        try:
            # When: Generating suggestions with a non-empty input text
            result = SuggestionGenerator.generate_basic_suggestions(CodeText("test"))

            # Then: Should return empty list gracefully
            assert result == []
        finally:
            # Restore original constants to prevent test side effects
            TauConstants.KEYWORDS = original_keywords

    @pytest.mark.parametrize("invalid_line_number_value", [-1, 0])
    def test_lineNumberNewType_WithInvalidIntegerValues_AcceptsValues(self, invalid_line_number_value):
        # Given: Invalid integer values for a line number
        # When: Creating a LineNumber instance with these unusual values
        # This tests that the NewType doesn't prevent runtime assignment of such ints if directly cast.
        line_num = LineNumber(invalid_line_number_value)

        # Then: The LineNumber object should hold these values
        assert line_num == invalid_line_number_value
