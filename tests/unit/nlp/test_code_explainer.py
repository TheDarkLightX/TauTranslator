import pytest
from returns.result import Success

from backend.unified.api.nlp import (
    CodeExplainer,
    CodeText,
    LineExplanation,
    ExplanationText,
)


class TestCodeExplainer:
    """Test the refactored CodeExplainer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.explainer = CodeExplainer()

    def test_explain_line_ForDefine_ReturnsCorrectExplanation(self):
        # Given: A line with a DEFINE statement
        code_line = CodeText("DEFINE x := true")

        # When: Explaining the line
        result = self.explainer.explain(code_line)

        # Then: A successful result with the correct explanation is returned
        assert isinstance(result, Success)
        explanation = result.unwrap()
        assert "defines a new constant" in explanation

    def test_explain_line_ForUnknownConstruct_ReturnsNone(self):
        # Given: A line with no recognizable construct
        code_line = CodeText("a = b + c")

        # When: Explaining the line
        result = self.explainer.explain(code_line)

        # Then: No explanation is returned
        assert isinstance(result, Success)
        assert "Could not generate" in result.unwrap()



    def test_full_explain_workflow_WithMultipleConstructs(self):
        # Given: A multi-line code snippet with recognizable constructs
        code = CodeText("""DEFINE x := true
# some comment
always (x -> y)""")

        # When: Running the full explanation workflow
        result = self.explainer.explain(code)

        # Then: A successful result with a full explanation is returned
        assert isinstance(result, Success)
        explanation = result.unwrap()
        assert "defines a new constant" in explanation
        assert "asserts a temporal property" in explanation

    def test_full_explain_workflow_WithNoRecognizedLines(self):
        # Given: Code with no recognizable constructs
        code = CodeText("""a = 1
b = 2""")

        # When: Running the full explanation workflow
        result = self.explainer.explain(code)

        # Then: A message indicating no specific explanations could be generated
        assert isinstance(result, Success)
        assert "Could not generate any specific explanations" in result.unwrap()