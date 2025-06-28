import pytest
from returns.result import Success

from backend.unified.api.nlp import ExplanationService, CodeText, CodeExplainer


class TestExplanationService:
    """Test the ExplanationService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ExplanationService(CodeExplainer())

    def test_explain_code_WithTAUConstructs_ReturnsDetailedExplanation(self):
        # Given: A code snippet with multiple Tau constructs
        code = CodeText("""DEFINE x := true
always (x -> y)""")
        
        # When: Explaining the code
        result = self.service.explain_code(code)
        
        # Then: The result is a success and contains specific explanations
        assert isinstance(result, Success)
        explanation = result.unwrap()
        assert "defines a new constant" in explanation
        assert "asserts a temporal property that must always hold" in explanation

    def test_explain_code_WithEmptyCode_ReturnsEmptyExplanation(self):
        # Given: Empty code
        code = CodeText("")
        
        # When: Explaining the code
        result = self.service.explain_code(code)
        
        # Then: The result indicates the code is empty
        assert isinstance(result, Success)
        assert "The code is empty" in result.unwrap()

    def test_explain_code_WithCommentsOnly_ReturnsEmptyExplanation(self):
        # Given: Code with only comments
        code = CodeText("# This is a comment")
        
        # When: Explaining the code
        result = self.service.explain_code(code)
        
        # Then: The result indicates the code is empty or commented
        assert isinstance(result, Success)
        assert "Could not generate any specific explanations" in result.unwrap()

    def test_explain_code_WithUnrecognizedCode_ReturnsGenericMessage(self):
        # Given: Code with no recognizable keywords
        code = CodeText("a + b = c")
        
        # When: Explaining the code
        result = self.service.explain_code(code)
        
        # Then: A generic message is returned
        assert isinstance(result, Success)
        assert "Could not generate any specific explanations" in result.unwrap()