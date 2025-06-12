"""
Comprehensive unit tests for refactored NLP module.

Following FIRST principles and BDD style with Given-When-Then structure.
Tests are focused, isolated, and behavior-driven.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Tuple

# Import all the classes and types from the refactored module
from backend.unified.api.nlp import (
    # Domain types
    CodeText, LineNumber, ErrorMessage, ExplanationText, SuggestionText, ConfidenceScore,
    SeverityLevel, SuggestionType, LanguageType,
    ValidationError, ValidationResult, Suggestion, LineExplanation, CodeExplanation,
    
    # Infrastructure
    NLPServiceLoader,
    
    # Core business logic
    TauConstants, SyntaxValidator, CodeLineProcessor, SuggestionGenerator, CodeExplainer,
    
    # Services
    ValidationService, AutocompleteService, ExplanationService,
    
    # Request models
    AutocompleteRequest, ValidationRequest, ExplainRequest
)
from backend.unified.core.result_enhanced import success, failure


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
        assert result.line == LineNumber(5)
        assert result.message == ErrorMessage("Unmatched parentheses")
        assert result.severity == SeverityLevel.ERROR
    
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
        assert result.line == LineNumber(3)
        assert result.message == ErrorMessage("Unmatched brackets")
        assert result.severity == SeverityLevel.ERROR
    
    @pytest.mark.parametrize("line,keyword,should_warn", [
        ("DEFINE x := true", "DEFINE", False),  # Has operator
        ("always x -> y", "always", False),      # Has operator
        ("forall x", "forall", True),           # No operator
        ("exists y", "exists", True),           # No operator
    ])
    def test_check_keyword_usage_WithVariousInputs(self, line, keyword, should_warn):
        # Given: A line with a TAU keyword
        code_line = CodeText(line)
        line_number = LineNumber(1)
        
        # When: Checking keyword usage
        result = SyntaxValidator.check_keyword_usage(code_line, line_number)
        
        # Then: Warning is returned based on operator presence
        if should_warn:
            assert result is not None
            assert f"Keyword '{keyword}' found without operator" in result.message
            assert result.severity == SeverityLevel.WARNING
        else:
            assert result is None


class TestCodeLineProcessor:
    """Test the CodeLineProcessor class."""
    
    def test_extract_code_lines_WithMixedContent_ReturnsOnlyCodeLines(self):
        # Given: Code with mixed content (code, comments, empty lines)
        code = CodeText("""// This is a comment
DEFINE x := true

// Another comment
always y -> z
""")
        
        # When: Extracting code lines
        result = CodeLineProcessor.extract_code_lines(code)
        
        # Then: Only non-comment, non-empty lines are returned with correct line numbers
        assert len(result) == 2
        assert result[0] == (LineNumber(2), CodeText("DEFINE x := true"))
        assert result[1] == (LineNumber(5), CodeText("always y -> z"))
    
    def test_extract_code_lines_WithEmptyCode_ReturnsEmptyList(self):
        # Given: Empty code
        code = CodeText("")
        
        # When: Extracting code lines
        result = CodeLineProcessor.extract_code_lines(code)
        
        # Then: Empty list is returned
        assert result == []
    
    @pytest.mark.parametrize("line,expected", [
        ("DEFINE x := true", True),
        ("// comment", False),
        ("", False),
        ("   ", False),
        ("   // indented comment", False),
    ])
    def test_is_meaningful_line_WithVariousInputs(self, line, expected):
        # Given: Various line types
        code_line = CodeText(line)
        
        # When: Checking if line is meaningful
        result = CodeLineProcessor.is_meaningful_line(code_line)
        
        # Then: Correct boolean is returned
        assert result == expected


class TestSuggestionGenerator:
    """Test the SuggestionGenerator class."""
    
    def test_generate_basic_suggestions_ForKeywordPrefix_ReturnsMatchingKeywords(self):
        # Given: A partial keyword
        text = CodeText("al")
        
        # When: Generating suggestions
        result = SuggestionGenerator.generate_basic_suggestions(text)
        
        # Then: Matching keywords are returned
        keyword_texts = [s.text for s in result]
        assert "always" in keyword_texts
        assert all(s.type in [SuggestionType.KEYWORD, SuggestionType.TEMPORAL] for s in result)
    
    def test_generate_basic_suggestions_ForOperatorPrefix_ReturnsMatchingOperators(self):
        # Given: A partial operator
        text = CodeText("->")
        
        # When: Generating suggestions
        result = SuggestionGenerator.generate_basic_suggestions(text)
        
        # Then: Matching operators are returned
        assert any(s.text == "->" and s.type == SuggestionType.OPERATOR for s in result)
    
    def test_generate_basic_suggestions_LimitsToTenResults(self):
        # Given: A very common prefix
        text = CodeText("")
        
        # When: Generating suggestions
        result = SuggestionGenerator.generate_basic_suggestions(text)
        
        # Then: At most 10 suggestions are returned
        assert len(result) <= 10
    
    @pytest.mark.parametrize("keyword,expected_type", [
        ("always", SuggestionType.TEMPORAL),
        ("sometimes", SuggestionType.TEMPORAL),
        ("forall", SuggestionType.QUANTIFIER),
        ("exists", SuggestionType.QUANTIFIER),
        ("DEFINE", SuggestionType.KEYWORD),
        ("true", SuggestionType.KEYWORD),
    ])
    def test_determine_keyword_type_ForVariousKeywords(self, keyword, expected_type):
        # Given: Various TAU keywords
        # When: Determining type
        result = SuggestionGenerator._determine_keyword_type(keyword)
        
        # Then: Correct type is returned
        assert result == expected_type


class TestCodeExplainer:
    """Test the CodeExplainer class."""
    
    @pytest.mark.parametrize("line,expected_explanation", [
        ("DEFINE x := true", "Defines a new concept or function"),
        ("always x > 0", "States that something is always true"),
        ("forall x: x > 0", "Universal quantification - true for all values"),
        ("x -> y", "Logical implication"),
        ("a <-> b", "Logical equivalence (if and only if)"),
    ])
    def test_explain_line_ForVariousConstructs(self, line, expected_explanation):
        # Given: A line with TAU construct
        code_line = CodeText(line)
        
        # When: Explaining the line
        result = CodeExplainer.explain_line(code_line)
        
        # Then: Correct explanation is returned
        assert result == ExplanationText(expected_explanation)
    
    def test_explain_line_ForUnknownConstruct_ReturnsNone(self):
        # Given: A line without recognized constructs
        code_line = CodeText("x = 5")
        
        # When: Explaining the line
        result = CodeExplainer.explain_line(code_line)
        
        # Then: None is returned
        assert result is None
    
    def test_generate_overall_explanation_WithDefinitionsAndTemporal_DescribesBoth(self):
        # Given: Line explanations with different types
        explanations = [
            LineExplanation(CodeText("DEFINE x"), ExplanationText("Defines...")),
            LineExplanation(CodeText("always y"), ExplanationText("States...")),
            LineExplanation(CodeText("forall z"), ExplanationText("Universal..."))
        ]
        
        # When: Generating overall explanation
        result = CodeExplainer.generate_overall_explanation(explanations)
        
        # Then: All aspects are mentioned
        assert "defines concepts or functions" in result
        assert "uses temporal logic" in result
        assert "includes quantifiers" in result
    
    def test_generate_overall_explanation_WithNoExplanations_ReturnsEmptyMessage(self):
        # Given: No explanations
        explanations = []
        
        # When: Generating overall explanation
        result = CodeExplainer.generate_overall_explanation(explanations)
        
        # Then: Empty message is returned
        assert result == ExplanationText("This TAU code is empty.")


class TestValidationService:
    """Test the ValidationService orchestration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SyntaxValidator()
        self.processor = CodeLineProcessor()
        self.service = ValidationService(self.validator, self.processor)
    
    def test_validate_code_WithValidCode_ReturnsSuccessfulValidation(self):
        # Given: Valid TAU code
        code = CodeText("DEFINE x := true")
        
        # When: Validating code
        result = self.service.validate_code(code)
        
        # Then: Validation passes
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validate_code_WithUnmatchedParentheses_ReturnsError(self):
        # Given: Code with unmatched parentheses
        code = CodeText("print(hello")
        
        # When: Validating code
        result = self.service.validate_code(code)
        
        # Then: Validation fails with appropriate error
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "parentheses" in result.errors[0].message
        assert "Check parentheses matching" in result.suggestions
    
    def test_validate_code_WithKeywordMisuse_ReturnsWarning(self):
        # Given: Code with keyword but no operator
        code = CodeText("forall x")
        
        # When: Validating code
        result = self.service.validate_code(code)
        
        # Then: Validation passes but with warning
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert "forall" in result.warnings[0].message
    
    def test_validate_code_WithMultipleErrors_ReturnsAllErrors(self):
        # Given: Code with multiple syntax errors
        code = CodeText("""print(hello
array[index""")
        
        # When: Validating code
        result = self.service.validate_code(code)
        
        # Then: All errors are reported
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert any("parentheses" in e.message for e in result.errors)
        assert any("brackets" in e.message for e in result.errors)


class TestAutocompleteService:
    """Test the AutocompleteService with mocked NLP service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SuggestionGenerator()
        self.service = AutocompleteService(self.generator)
    
    @pytest.mark.asyncio
    async def test_get_suggestions_async_WithoutNLP_ReturnsBasicSuggestions(self):
        # Given: No NLP service available
        text = CodeText("al")
        nlp_service = None
        
        # When: Getting suggestions
        result = await self.service.get_suggestions_async(text, nlp_service)
        
        # Then: Basic suggestions are returned
        assert result.is_success()
        suggestions = result.value
        assert any(s.text == "always" for s in suggestions)
        assert all(s.confidence is None for s in suggestions)  # No confidence without NLP
    
    @pytest.mark.asyncio
    async def test_get_suggestions_async_WithNLP_ReturnsEnhancedSuggestions(self):
        # Given: Mocked NLP service
        text = CodeText("def")
        nlp_service = Mock()
        nlp_service.autocomplete_engine.get_completions.return_value = [
            ("DEFINE", 0.95),
            ("default", 0.80),
        ]
        
        # When: Getting suggestions
        result = await self.service.get_suggestions_async(text, nlp_service)
        
        # Then: NLP suggestions are returned with confidence
        assert result.is_success()
        suggestions = result.value
        assert len(suggestions) == 2
        assert suggestions[0].text == "DEFINE"
        assert suggestions[0].confidence == 0.95
        assert suggestions[1].text == "default"
        assert suggestions[1].confidence == 0.80
    
    @pytest.mark.asyncio
    async def test_get_suggestions_async_WhenNLPFails_ReturnsError(self):
        # Given: NLP service that throws exception
        text = CodeText("test")
        nlp_service = Mock()
        nlp_service.autocomplete_engine.get_completions.side_effect = Exception("NLP error")
        
        # When: Getting suggestions
        result = await self.service.get_suggestions_async(text, nlp_service)
        
        # Then: Error result is returned
        assert result.is_failure()
        assert result.error_code == "NLP_ERROR"
        assert "NLP suggestion failed" in result.message


class TestExplanationService:
    """Test the ExplanationService orchestration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.explainer = CodeExplainer()
        self.processor = CodeLineProcessor()
        self.service = ExplanationService(self.explainer, self.processor)
    
    def test_explain_code_WithTAUConstructs_ReturnsDetailedExplanation(self):
        # Given: TAU code with various constructs
        code = CodeText("""DEFINE isPrime(n) := ...
always isPrime(2)
forall x: x > 0 -> exists y: y > x""")
        
        # When: Explaining code
        result = self.service.explain_code(code)
        
        # Then: Comprehensive explanation is returned
        assert "defines concepts or functions" in result.overall
        assert "uses temporal logic" in result.overall
        assert "includes quantifiers" in result.overall
        assert len(result.line_explanations) == 3
    
    def test_explain_code_WithEmptyCode_ReturnsEmptyExplanation(self):
        # Given: Empty code
        code = CodeText("")
        
        # When: Explaining code
        result = self.service.explain_code(code)
        
        # Then: Empty explanation is returned
        assert result.overall == "This TAU code is empty."
        assert len(result.line_explanations) == 0
    
    def test_explain_code_WithCommentsOnly_ReturnsEmptyExplanation(self):
        # Given: Code with only comments
        code = CodeText("""// This is a comment
// Another comment""")
        
        # When: Explaining code
        result = self.service.explain_code(code)
        
        # Then: Empty explanation is returned
        assert result.overall == "This TAU code is empty."
        assert len(result.line_explanations) == 0


class TestNLPServiceLoader:
    """Test the NLP service loader infrastructure."""
    
    def teardown_method(self):
        """Reset class state after each test."""
        NLPServiceLoader._service_instance = None
    
    def test_load_nlp_service_async_WhenSuccessful_ReturnsCachedInstance(self):
        # Given: NLP module is available
        mock_instance = Mock()
        
        # Mock the import inside the method
        import sys
        mock_module = Mock()
        mock_module.NLPTranslationService = Mock(return_value=mock_instance)
        
        with patch.dict('sys.modules', {'nlp.nlp_integration': mock_module}):
            # When: Loading service twice
            result1 = NLPServiceLoader.load_nlp_service_async()
            result2 = NLPServiceLoader.load_nlp_service_async()
            
            # Then: Same instance is returned (cached)
            assert result1.is_success()
            assert result1.value is mock_instance
            assert result2.value is mock_instance
            mock_module.NLPTranslationService.assert_called_once()  # Only instantiated once
    
    def test_load_nlp_service_async_WhenImportFails_ReturnsNone(self):
        # Given: NLP module is not available
        # Remove nlp.nlp_integration from sys.modules to simulate import failure
        import sys
        if 'nlp.nlp_integration' in sys.modules:
            del sys.modules['nlp.nlp_integration']
        
        # When: Loading service
        result = NLPServiceLoader.load_nlp_service_async()
        
        # Then: Success with None value (graceful degradation)
        assert result.is_success()
        assert result.value is None
    
    def test_load_nlp_service_async_WhenInitFails_ReturnsError(self):
        # Given: NLP module fails to initialize
        import sys
        mock_module = Mock()
        mock_module.NLPTranslationService = Mock(side_effect=Exception("Init failed"))
        
        with patch.dict('sys.modules', {'nlp.nlp_integration': mock_module}):
            # When: Loading service
            result = NLPServiceLoader.load_nlp_service_async()
            
            # Then: Failure result with error details
            assert result.is_failure()
            assert result.error_code == "SERVICE_LOAD_ERROR"
            assert "Failed to load NLP service" in result.message


class TestEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions."""
    
    def test_validation_with_deeply_nested_parentheses(self):
        # Given: Deeply nested but balanced parentheses
        service = ValidationService(SyntaxValidator(), CodeLineProcessor())
        code = CodeText("((((((((((x))))))))))")
        
        # When: Validating
        result = service.validate_code(code)
        
        # Then: Should pass
        assert result.is_valid is True
    
    def test_validation_with_mixed_bracket_types(self):
        # Given: Mixed brackets and parentheses
        service = ValidationService(SyntaxValidator(), CodeLineProcessor())
        code = CodeText("array[func(x[0])]")
        
        # When: Validating
        result = service.validate_code(code)
        
        # Then: Should pass
        assert result.is_valid is True
    
    def test_suggestion_generation_with_empty_constants(self):
        # Given: Temporarily empty constants (edge case)
        original_keywords = TauConstants.KEYWORDS
        TauConstants.KEYWORDS = frozenset()
        
        try:
            # When: Generating suggestions
            result = SuggestionGenerator.generate_basic_suggestions(CodeText("test"))
            
            # Then: Should return empty list gracefully
            assert result == []
        finally:
            # Restore original constants
            TauConstants.KEYWORDS = original_keywords
    
    @pytest.mark.parametrize("invalid_line_number", [-1, 0])
    def test_validation_error_with_invalid_line_numbers(self, invalid_line_number):
        # Given: Invalid line number
        # When: Creating validation error with unusual line numbers
        # Then: Should accept them (NewType doesn't prevent at runtime)
        error = ValidationError(
            line=invalid_line_number,
            message=ErrorMessage("test"),
            severity=SeverityLevel.ERROR
        )
        assert error.line == invalid_line_number


class TestDomainTypes:
    """Test the behavior of domain types."""
    
    def test_frozen_dataclasses_are_immutable(self):
        # Given: A validation error instance
        error = ValidationError(
            line=LineNumber(1),
            message=ErrorMessage("test"),
            severity=SeverityLevel.ERROR
        )
        
        # When/Then: Attempting to modify should raise error
        with pytest.raises(AttributeError):
            error.line = LineNumber(2)
    
    def test_suggestion_equality(self):
        # Given: Two identical suggestions
        s1 = Suggestion(
            text=SuggestionText("always"),
            type=SuggestionType.TEMPORAL,
            confidence=ConfidenceScore(0.9)
        )
        s2 = Suggestion(
            text=SuggestionText("always"),
            type=SuggestionType.TEMPORAL,
            confidence=ConfidenceScore(0.9)
        )
        
        # Then: They should be equal
        assert s1 == s2
    
    def test_severity_level_values(self):
        # Given/When: Severity levels
        # Then: Values should match expected strings
        assert SeverityLevel.ERROR.value == "error"
        assert SeverityLevel.WARNING.value == "warning"
        assert SeverityLevel.INFO.value == "info"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])