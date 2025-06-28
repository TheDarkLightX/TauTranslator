"""
Unit tests for the ValidationService class from the NLP module.

Copyright: DarkLightX / Dana Edwards
"""

from backend.unified.api.nlp import (
    CodeText,
    CodeLineProcessor,
    ErrorType,
    SyntaxValidator,
    ValidationService,
)

from returns.result import Success, Failure

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
        assert isinstance(result, Success)
    
    def test_validate_code_WithUnmatchedParentheses_ReturnsErrorAndSuggestion(self):
        # Given: Code with unmatched parentheses
        code = CodeText("print(hello")
        
        # When: Validating code
        result = self.service.validate_code(code)
        
        # Then: Validation fails with appropriate error and suggestion
        assert isinstance(result, Failure)
        assert len(result.failure()) == 1
        assert "parentheses" in result.failure()[0].message
        assert "Check parentheses balance." in result.failure()[0].suggestion
    
    def test_validate_code_WithKeywordMisuse_ReturnsWarning(self):
        # Given: Code with keyword but no operator
        code = CodeText("forall x")
        
        # When: Validating code
        result = self.service.validate_code(code)
        
        # Then: Validation passes but with warning
        assert isinstance(result, Failure)
        failure = result.failure()
        assert len(failure) == 1
        assert failure[0].error_type == ErrorType.SYNTAX_WARNING
        assert "forall" in failure[0].message
    
    def test_validate_code_WithMultipleErrors_ReturnsAllErrors(self):
        # Given: Code with multiple syntax errors
        code = CodeText("""print(hello
array[index""")
        
        # When: Validating code
        result = self.service.validate_code(code)
        
        # Then: All errors are reported
        assert isinstance(result, Failure)
        assert len(result.failure()) == 2
        assert any("parentheses" in e.message for e in result.failure())
        assert any("brackets" in e.message for e in result.failure())
