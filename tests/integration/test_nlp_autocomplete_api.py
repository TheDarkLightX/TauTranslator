"""
Unit Tests for NLP Autocomplete API
===================================
Following FIRST principles and BDD approach

Copyright: DarkLightX/Dana Edwards
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Test Data Builders
class AutoCompleteRequestBuilder:
    """Builder for autocomplete request data"""
    
    def __init__(self):
        self.text = "for"
        self.position = None
        self.context = None
    
    def with_text(self, text):
        self.text = text
        return self
    
    def with_position(self, position):
        self.position = position
        return self
    
    def with_context(self, context):
        self.context = context
        return self
    
    def build(self):
        return {
            "text": self.text,
            "position": self.position,
            "context": self.context
        }


class SuggestionBuilder:
    """Builder for suggestion objects"""
    
    def __init__(self):
        self.text = "forall"
        self.type = "quantifier"
        self.confidence = 0.9
    
    def with_text(self, text):
        self.text = text
        return self
    
    def with_type(self, suggestion_type):
        self.type = suggestion_type
        return self
    
    def with_confidence(self, confidence):
        self.confidence = confidence
        return self
    
    def build(self):
        return {
            "text": self.text,
            "type": self.type,
            "confidence": self.confidence
        }


class TestAutoCompleteBasicFunctionality:
    """Test basic autocomplete functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from ...api.nlp import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.fixture
    def mock_nlp_service(self):
        """Mock NLP service"""
        mock_service = Mock()
        mock_service.autocomplete_engine = Mock()
        mock_service.autocomplete_engine.get_completions = Mock(
            return_value=[("forall", 0.9), ("for every", 0.8)]
        )
        return mock_service
    
    # Test: AutoComplete_ValidRequest_ReturnsSuggestions
    def test_given_valid_request_when_calling_autocomplete_then_returns_suggestions(
        self, client, mock_nlp_service
    ):
        # Given: Valid autocomplete request with NLP service available
        request_data = AutoCompleteRequestBuilder().build()
        
        with patch("backend.unified.api.nlp.NLPServiceLoader.load_nlp_service_async") as mock_loader:
            mock_loader.return_value.value = mock_nlp_service
            mock_loader.return_value.is_success.return_value = True
            
            # When: Calling autocomplete endpoint
            response = client.post("/autocomplete", json=request_data)
            
            # Then: Returns success with suggestions
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["suggestions"]) == 2
            assert data["data"]["suggestions"][0]["text"] == "forall"
            assert data["data"]["suggestions"][0]["type"] == "quantifier"
            assert data["data"]["suggestions"][0]["confidence"] == 0.9
            assert data["data"]["source"] == "nlp"
    
    # Test: AutoComplete_EmptyText_ReturnsBasicSuggestions
    def test_given_empty_text_when_calling_autocomplete_then_returns_basic_suggestions(
        self, client
    ):
        # Given: Empty text request
        request_data = AutoCompleteRequestBuilder().with_text("").build()
        
        with patch("backend.unified.api.nlp.NLPServiceLoader.load_nlp_service_async") as mock_loader:
            mock_loader.return_value.value = None
            mock_loader.return_value.is_success.return_value = True
            
            # When: Calling autocomplete endpoint
            response = client.post("/autocomplete", json=request_data)
            
            # Then: Returns basic suggestions
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["suggestions"]) > 0
            assert data["data"]["source"] == "basic"
    
    # Test: AutoComplete_NLPServiceUnavailable_FallsBackToBasic
    def test_given_nlp_service_unavailable_when_calling_autocomplete_then_uses_basic_suggestions(
        self, client
    ):
        # Given: NLP service is not available
        request_data = AutoCompleteRequestBuilder().with_text("def").build()
        
        with patch("backend.unified.api.nlp.NLPServiceLoader.load_nlp_service_async") as mock_loader:
            mock_loader.return_value.value = None
            mock_loader.return_value.is_success.return_value = True
            
            # When: Calling autocomplete endpoint
            response = client.post("/autocomplete", json=request_data)
            
            # Then: Returns basic suggestions
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["source"] == "basic"
            # Should include DEFINE keyword
            suggestions = [s["text"] for s in data["data"]["suggestions"]]
            assert "DEFINE" in suggestions


class TestAutoCompleteEdgeCases:
    """Test edge cases and error scenarios"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from ...api.nlp import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.fixture
    def mock_nlp_service_error(self):
        """Mock NLP service that throws error"""
        mock_service = Mock()
        mock_service.autocomplete_engine = Mock()
        mock_service.autocomplete_engine.get_completions = Mock(
            side_effect=Exception("NLP service error")
        )
        return mock_service
    
    # Test: AutoComplete_NLPServiceError_ReturnsError
    def test_given_nlp_service_error_when_calling_autocomplete_then_returns_error_response(
        self, client, mock_nlp_service_error
    ):
        # Given: NLP service that throws error
        request_data = AutoCompleteRequestBuilder().build()
        
        with patch("backend.unified.api.nlp.NLPServiceLoader.load_nlp_service_async") as mock_loader:
            mock_loader.return_value.value = mock_nlp_service_error
            mock_loader.return_value.is_success.return_value = True
            
            # When: Calling autocomplete endpoint
            response = client.post("/autocomplete", json=request_data)
            
            # Then: Returns error response
            assert response.status_code == 200  # Still 200 but with error in data
            data = response.json()
            assert data["success"] is False
            assert "NLP suggestion failed" in data["message"]
    
    # Test: AutoComplete_LongText_HandlesGracefully
    def test_given_very_long_text_when_calling_autocomplete_then_handles_gracefully(
        self, client
    ):
        # Given: Very long input text
        long_text = "a" * 1000
        request_data = AutoCompleteRequestBuilder().with_text(long_text).build()
        
        with patch("backend.unified.api.nlp.NLPServiceLoader.load_nlp_service_async") as mock_loader:
            mock_loader.return_value.value = None
            mock_loader.return_value.is_success.return_value = True
            
            # When: Calling autocomplete endpoint
            response = client.post("/autocomplete", json=request_data)
            
            # Then: Handles gracefully
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # Should return empty or limited suggestions for nonsense input
            assert len(data["data"]["suggestions"]) <= 10
    
    # Test: AutoComplete_SpecialCharacters_HandlesCorrectly
    def test_given_special_characters_when_calling_autocomplete_then_handles_correctly(
        self, client
    ):
        # Given: Input with special characters
        special_text = "for<>all"
        request_data = AutoCompleteRequestBuilder().with_text(special_text).build()
        
        with patch("backend.unified.api.nlp.NLPServiceLoader.load_nlp_service_async") as mock_loader:
            mock_loader.return_value.value = None
            mock_loader.return_value.is_success.return_value = True
            
            # When: Calling autocomplete endpoint
            response = client.post("/autocomplete", json=request_data)
            
            # Then: Handles without crashing
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestSuggestionGeneration:
    """Test suggestion generation logic"""
    
    # Test: SuggestionGeneration_KeywordMatching_CaseInsensitive
    def test_given_mixed_case_input_when_generating_suggestions_then_matches_case_insensitive(self):
        # Given: Mixed case input
        from ...api.nlp import SuggestionGenerator
        
        text = "FOR"
        
        # When: Generating suggestions
        suggestions = SuggestionGenerator.generate_basic_suggestions(text)
        
        # Then: Matches keywords case-insensitively
        suggestion_texts = [s.text for s in suggestions]
        assert "forall" in suggestion_texts
    
    # Test: SuggestionGeneration_OperatorMatching_ExactPrefix
    def test_given_operator_prefix_when_generating_suggestions_then_matches_operators(self):
        # Given: Operator prefix
        from ...api.nlp import SuggestionGenerator
        
        text = ":"
        
        # When: Generating suggestions
        suggestions = SuggestionGenerator.generate_basic_suggestions(text)
        
        # Then: Matches operators starting with :
        suggestion_texts = [s.text for s in suggestions]
        assert ":=" in suggestion_texts
    
    # Test: SuggestionGeneration_TypeClassification_Correct
    def test_given_various_keywords_when_classifying_then_assigns_correct_types(self):
        # Given: Various keywords
        from ...api.nlp import SuggestionGenerator
        
        test_cases = [
            ("always", "temporal"),
            ("forall", "quantifier"),
            ("DEFINE", "keyword"),
            (":=", "operator")
        ]
        
        for keyword, expected_type in test_cases:
            # When: Determining keyword type
            actual_type = SuggestionGenerator._determine_keyword_type(keyword)
            
            # Then: Type is correct
            assert actual_type.value == expected_type


class TestValidationFunctionality:
    """Test code validation functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from ...api.nlp import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    # Test: Validation_ValidCode_ReturnsNoErrors
    def test_given_valid_tau_code_when_validating_then_returns_no_errors(self, client):
        # Given: Valid TAU code
        valid_code = "DEFINE concept1 := always (P(x) -> Q(x))"
        request_data = {"code": valid_code, "language": "TAU"}
        
        # When: Validating code
        response = client.post("/validate", json=request_data)
        
        # Then: Returns valid with no errors
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_valid"] is True
        assert len(data["data"]["errors"]) == 0
    
    # Test: Validation_UnbalancedParentheses_ReturnsError
    def test_given_unbalanced_parentheses_when_validating_then_returns_error(self, client):
        # Given: Code with unbalanced parentheses
        invalid_code = "DEFINE concept1 := always (P(x) -> Q(x)"
        request_data = {"code": invalid_code, "language": "TAU"}
        
        # When: Validating code
        response = client.post("/validate", json=request_data)
        
        # Then: Returns error about parentheses
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_valid"] is False
        assert len(data["data"]["errors"]) > 0
        assert any("parentheses" in error["message"] for error in data["data"]["errors"])
    
    # Test: Validation_KeywordWithoutOperator_ReturnsWarning
    def test_given_keyword_without_operator_when_validating_then_returns_warning(self, client):
        # Given: Keyword without operator
        code_with_warning = "forall x"
        request_data = {"code": code_with_warning, "language": "TAU"}
        
        # When: Validating code
        response = client.post("/validate", json=request_data)
        
        # Then: Returns warning
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["warnings"]) > 0


class TestCodeExplanation:
    """Test code explanation functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from ...api.nlp import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    # Test: Explanation_SimpleCode_ProvidesAccurateExplanation
    def test_given_simple_code_when_explaining_then_provides_accurate_explanation(self, client):
        # Given: Simple TAU code
        simple_code = "DEFINE P := always true"
        request_data = {"code": simple_code, "language": "TAU"}
        
        # When: Explaining code
        response = client.post("/explain", json=request_data)
        
        # Then: Provides meaningful explanation
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["explanation"]) > 0
        assert len(data["data"]["line_explanations"]) > 0
        
        # Should explain DEFINE and always
        line_explanations = data["data"]["line_explanations"]
        assert any("Define" in exp["explanation"] for exp in line_explanations)
    
    # Test: Explanation_ComplexCode_ExplainsAllConstructs
    def test_given_complex_code_when_explaining_then_explains_all_constructs(self, client):
        # Given: Complex TAU code with multiple constructs
        complex_code = """
DEFINE concept1 := forall x (P(x) -> Q(x))
DEFINE concept2 := exists y (R(y) && S(y))
always (concept1 <-> concept2)
        """.strip()
        request_data = {"code": complex_code, "language": "TAU"}
        
        # When: Explaining code
        response = client.post("/explain", json=request_data)
        
        # Then: Explains all constructs
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Overall explanation should mention key features
        overall = data["data"]["explanation"]
        assert "defines concepts" in overall or "functions" in overall
        assert "temporal logic" in overall
        assert "quantifiers" in overall