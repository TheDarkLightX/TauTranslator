import pytest
from unittest.mock import Mock
from backend.unified.api.nlp import (
    CodeText,
    AutocompleteService,
    Suggestion,
    SuggestionType,
    Success,
    Failure,
)


class TestAutocompleteService:
    """Test the AutocompleteService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AutocompleteService()

    def test_get_suggestions_for_partial_keyword_returns_correct_suggestion(self):
        # Given: Text that partially matches a basic keyword
        text = CodeText("al")

        # When: Getting suggestions
        result = self.service.get_suggestions(text)

        # Then: The result is a success and contains the 'always' keyword
        assert isinstance(result, Success)
        suggestions = result.unwrap()
        assert len(suggestions) == 1
        assert suggestions[0].text == "always"
        assert suggestions[0].suggestion_type == SuggestionType.TEMPORAL

    def test_get_suggestions_for_define_keyword_returns_correct_suggestion(self):
        # Given: Text that partially matches a keyword
        text = CodeText("def")

        # When: Getting suggestions
        result = self.service.get_suggestions(text)

        # Then: The result is a success and contains the 'DEFINE' keyword
        assert isinstance(result, Success)
        suggestions = result.unwrap()
        assert len(suggestions) == 1
        assert suggestions[0].text == "DEFINE"
        assert suggestions[0].suggestion_type == SuggestionType.KEYWORD

    def test_get_suggestions_for_unrecognized_input_returns_empty_list(self):
        # Given: Text that does not match any keywords
        text = CodeText("test")

        # When: Getting suggestions
        result = self.service.get_suggestions(text)

        # Then: The result is a success with an empty list of suggestions
        assert isinstance(result, Success)
        suggestions = result.unwrap()
        assert suggestions == []
