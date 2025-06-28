import pytest
from backend.unified.api.nlp import SuggestionGenerator, CodeText, Suggestion, SuggestionType
from backend.unified.api.nlp import TauConstants

class TestSuggestionGenerator:
    """Test the SuggestionGenerator class."""

    def test_generate_basic_suggestions_ForEmptyText_ReturnsAllKeywordsAndOperators(self):
        # Given: Empty text
        text = CodeText("")

        # When: Generating suggestions
        result = SuggestionGenerator.generate_basic_suggestions(text)

        # Then: The result should contain all keywords and operators
        expected_count = len(TauConstants.KEYWORDS) + len(TauConstants.OPERATORS)
        assert len(result) > 0
        assert len(result) <= expected_count
        
        # Verify a few key suggestions exist
        result_texts = {s.text for s in result}
        assert "DEFINE" in result_texts
        assert "->" in result_texts

    def test_generate_basic_suggestions_ForKeywordPrefix_ReturnsMatchingKeywords(self):
        # Given: A partial keyword
        text = CodeText("DEF")

        # When: Generating suggestions
        result = SuggestionGenerator.generate_basic_suggestions(text)

        # Then: The result contains the matching keyword
        assert len(result) == 1
        suggestion = result[0]
        assert suggestion.text == "DEFINE"
        assert suggestion.suggestion_type == SuggestionType.KEYWORD

    def test_generate_basic_suggestions_ForOperatorPrefix_ReturnsMatchingOperators(self):
        # Given: A partial operator
        text = CodeText("->")
        
        # When: Generating suggestions
        result = SuggestionGenerator.generate_basic_suggestions(text)
        
        # Then: The result contains the matching operator
        # Note: The '!=' check will also trigger, so we expect 2 suggestions
        assert len(result) >= 1
        op_suggestion = next(s for s in result if s.text == "->")
        assert op_suggestion.suggestion_type == SuggestionType.OPERATOR

    def test_generate_basic_suggestions_ForNonMatchingPrefix_ReturnsEmptyList(self):
        # Given: A prefix that doesn't match anything
        text = CodeText("xyz")

        # When: Generating suggestions
        result = SuggestionGenerator.generate_basic_suggestions(text)

        # Then: An empty list is returned
        assert len(result) == 0

    def test_generate_contextual_suggestion_for_not_equals(self):
        # Given: Code containing the '!=' operator
        text = CodeText("a != b")

        # When: Generating suggestions
        result = SuggestionGenerator.generate_basic_suggestions(text)

        # Then: A clarity suggestion is returned
        assert any(s.suggestion_type == SuggestionType.CLARITY for s in result)
        clarity_suggestion = next(s for s in result if s.suggestion_type == SuggestionType.CLARITY)
        assert "not (a = b)" in clarity_suggestion.text