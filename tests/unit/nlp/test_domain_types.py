"""
Unit tests for the domain types in the NLP module.

Copyright: DarkLightX / Dana Edwards
"""

import pytest

from backend.unified.api.nlp import (
    ValidationError,
    LineNumber,
    ErrorMessage,
    SeverityLevel,
    Suggestion,
    SuggestionText,
    SuggestionType,
    ConfidenceScore
)

import dataclasses

class TestDomainTypes:
    """Test the behavior of domain types."""
    
    def test_frozenDataclassValidationError_WhenAttributeModified_RaisesAttributeError(self):
        # Given: A ValidationError instance (which should be a frozen dataclass)
        error = ValidationError(
            message=ErrorMessage("test"),
            error_type='TEST_ERROR',
            suggestion='Test suggestion',
            confidence=1.0
        )
        
        # When/Then: Attempting to modify an attribute should raise an exception
        # Note: dataclasses.FrozenInstanceError is a subclass of AttributeError
        with pytest.raises(dataclasses.FrozenInstanceError):
            error.message = ErrorMessage("new message")
    
    def test_suggestionEquality_WhenSuggestionsAreIdentical_ReturnsTrue(self):
        # Given: Two identical Suggestion instances
        s1 = Suggestion(
            text=SuggestionText("always"),
            suggestion_type=SuggestionType.TEMPORAL,
            confidence=ConfidenceScore(0.9)
        )
        s2 = Suggestion(
            text=SuggestionText("always"),
            suggestion_type=SuggestionType.TEMPORAL,
            confidence=ConfidenceScore(0.9)
        )
        
        # Then: They should be equal
        assert s1 == s2
    
    def test_severityLevelEnum_Values_MatchExpectedStrings(self):
        # Given/When: Accessing SeverityLevel enum values
        # Then: The .value attribute should match the expected string representation
        assert SeverityLevel.ERROR.value == "error"
        assert SeverityLevel.WARNING.value == "warning"
        assert SeverityLevel.INFO.value == "info"
