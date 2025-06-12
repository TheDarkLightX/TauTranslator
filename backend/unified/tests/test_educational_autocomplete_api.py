"""
Tests for educational autocomplete API integration.

Tests cover backward compatibility, educational mode features,
and full integration with the autocomplete service.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from fastapi.testclient import TestClient
from ..core.result_enhanced import Success, Failure

from backend.unified.api.nlp import router, AutocompleteRequest
from backend.unified.core.autocomplete.models import (
    EducationalSuggestion,
    SuggestionText,
    DisplayText,
    HintText,
    ExampleCode,
    SuggestionCategory,
    DifficultyLevel,
    LanguageMode,
    ContextType,
    SpecificationContext,
    SuggestionRequest,
    SuggestionResponse,
    CursorPosition,
    ConfidenceScore
)
from backend.unified.core.autocomplete.educational_autocomplete_service import (
    EducationalAutocompleteService,
    AutocompleteConfiguration
)


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router, prefix="/api/nlp")
    return TestClient(app)


@pytest.fixture
def mock_nlp_service():
    """Mock NLP service for testing."""
    service = Mock()
    service.autocomplete_engine = Mock()
    service.autocomplete_engine.get_completions = Mock(
        return_value=[("always", 0.9), ("all", 0.7)]
    )
    return service


@pytest.fixture
def mock_educational_service():
    """Mock educational autocomplete service."""
    service = Mock(spec=EducationalAutocompleteService)
    return service


@pytest.fixture
def sample_educational_suggestions():
    """Sample educational suggestions for testing."""
    return [
        EducationalSuggestion(
            text=SuggestionText("always"),
            display=DisplayText("always - temporal operator"),
            category=SuggestionCategory.TEMPORAL,
            description=HintText("States that something is always true"),
            example=ExampleCode("always (x > 0)"),
            difficulty=DifficultyLevel.BEGINNER,
            confidence=ConfidenceScore(0.95)
        ),
        EducationalSuggestion(
            text=SuggestionText("forall"),
            display=DisplayText("forall - universal quantifier"),
            category=SuggestionCategory.QUANTIFIER,
            description=HintText("Universal quantification - true for all values"),
            example=ExampleCode("forall x : x > 0 -> f(x) > 0"),
            difficulty=DifficultyLevel.INTERMEDIATE,
            confidence=ConfidenceScore(0.85)
        )
    ]


class TestBackwardCompatibility:
    """Test backward compatibility with legacy API."""
    
    def test_legacy_autocomplete_request_works(self, test_client):
        """Test that legacy requests without educational features still work."""
        # Arrange
        legacy_request = {
            "text": "al",
            "position": 2
        }
        
        # Act
        response = test_client.post("/api/nlp/autocomplete", json=legacy_request)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "suggestions" in data["data"]
        assert isinstance(data["data"]["suggestions"], list)
    
    def test_legacy_response_format_when_educational_disabled(self, test_client):
        """Test response matches old format when educational features disabled."""
        # Arrange
        request = {
            "text": "for",
            "position": 3,
            "context": {
                "educational_mode": False
            }
        }
        
        # Act
        response = test_client.post("/api/nlp/autocomplete", json=request)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        suggestions = data["data"]["suggestions"]
        
        # Check format matches legacy (simple suggestion objects)
        for suggestion in suggestions:
            assert "text" in suggestion
            assert "type" in suggestion
            # Educational fields should not be present
            assert "description" not in suggestion or suggestion["description"] is None
            assert "example" not in suggestion or suggestion["example"] is None
    
    def test_legacy_nlp_service_integration(self, test_client, mock_nlp_service):
        """Test integration with legacy NLP service."""
        with patch("backend.unified.api.nlp.NLPServiceLoader.load_nlp_service_async",
                  return_value=Success(mock_nlp_service)):
            # Arrange
            request = {"text": "al", "position": 2}
            
            # Act
            response = test_client.post("/api/nlp/autocomplete", json=request)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["source"] == "nlp"
            suggestions = data["data"]["suggestions"]
            assert len(suggestions) == 2
            assert suggestions[0]["text"] == "always"


class TestEducationalModeFeatures:
    """Test educational mode specific features."""
    
    def test_tau_language_mode_suggestions(self, test_client, mock_educational_service):
        """Test suggestions with TAU language mode."""
        # Arrange
        request = {
            "text": "for",
            "position": 3,
            "context": {
                "language_mode": "TAU",
                "educational_mode": True
            }
        }
        
        mock_educational_service.get_suggestions_async.return_value = Success(
            SuggestionResponse(
                suggestions=[
                    EducationalSuggestion(
                        text=SuggestionText("forall"),
                        display=DisplayText("forall"),
                        category=SuggestionCategory.QUANTIFIER,
                        description=HintText("Universal quantifier"),
                        example=ExampleCode("forall x : P(x)"),
                        difficulty=DifficultyLevel.INTERMEDIATE
                    )
                ]
            )
        )
        
        with patch("backend.unified.api.nlp._get_educational_service",
                  return_value=mock_educational_service):
            # Act
            response = test_client.post("/api/nlp/autocomplete", json=request)
            
            # Assert
            assert response.status_code == 200
            suggestions = response.json()["data"]["suggestions"]
            assert suggestions[0]["text"] == "forall"
            assert suggestions[0]["category"] == "quantifier"
    
    def test_tce_language_mode_suggestions(self, test_client, mock_educational_service):
        """Test suggestions with TCE language mode."""
        # Arrange
        request = {
            "text": "for all",
            "position": 7,
            "context": {
                "language_mode": "TCE",
                "educational_mode": True
            }
        }
        
        mock_educational_service.get_suggestions_async.return_value = Success(
            SuggestionResponse(
                suggestions=[
                    EducationalSuggestion(
                        text=SuggestionText("for all x such that"),
                        display=DisplayText("for all x such that"),
                        category=SuggestionCategory.PATTERN,
                        description=HintText("Universal quantification in English"),
                        example=ExampleCode("for all x such that x > 0"),
                        difficulty=DifficultyLevel.BEGINNER,
                        tau_equivalent="forall x : x > 0"
                    )
                ]
            )
        )
        
        with patch("backend.unified.api.nlp._get_educational_service",
                  return_value=mock_educational_service):
            # Act
            response = test_client.post("/api/nlp/autocomplete", json=request)
            
            # Assert
            assert response.status_code == 200
            suggestions = response.json()["data"]["suggestions"]
            assert suggestions[0]["text"] == "for all x such that"
            assert suggestions[0]["tau_equivalent"] == "forall x : x > 0"
    
    def test_learning_level_beginner(self, test_client, mock_educational_service):
        """Test suggestions filtered by beginner learning level."""
        # Arrange
        request = {
            "text": "al",
            "position": 2,
            "context": {
                "learning_level": "beginner",
                "educational_mode": True
            }
        }
        
        beginner_suggestions = [
            EducationalSuggestion(
                text=SuggestionText("always"),
                display=DisplayText("always"),
                category=SuggestionCategory.TEMPORAL,
                description=HintText("Something is always true"),
                example=ExampleCode("always (door_closed)"),
                difficulty=DifficultyLevel.BEGINNER
            )
        ]
        
        mock_educational_service.get_suggestions_async.return_value = Success(
            SuggestionResponse(suggestions=beginner_suggestions)
        )
        
        with patch("backend.unified.api.nlp._get_educational_service",
                  return_value=mock_educational_service):
            # Act
            response = test_client.post("/api/nlp/autocomplete", json=request)
            
            # Assert
            assert response.status_code == 200
            suggestions = response.json()["data"]["suggestions"]
            assert all(s["difficulty"] == "beginner" for s in suggestions)
    
    def test_include_examples_flag(self, test_client, sample_educational_suggestions):
        """Test include_examples flag controls example presence."""
        # Test with examples enabled
        request_with_examples = {
            "text": "al",
            "position": 2,
            "context": {
                "include_examples": True,
                "educational_mode": True
            }
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request_with_examples)
        assert response.status_code == 200
        suggestions = response.json()["data"]["suggestions"]
        if suggestions:  # If we have suggestions
            assert all("example" in s for s in suggestions)
        
        # Test with examples disabled
        request_without_examples = {
            "text": "al",
            "position": 2,
            "context": {
                "include_examples": False,
                "educational_mode": True
            }
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request_without_examples)
        assert response.status_code == 200
        suggestions = response.json()["data"]["suggestions"]
        if suggestions:
            assert all("example" not in s or s["example"] is None for s in suggestions)
    
    def test_include_explanations_flag(self, test_client):
        """Test include_explanations flag controls description presence."""
        # Test with explanations enabled
        request_with_explanations = {
            "text": "for",
            "position": 3,
            "context": {
                "include_explanations": True,
                "educational_mode": True
            }
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request_with_explanations)
        assert response.status_code == 200
        suggestions = response.json()["data"]["suggestions"]
        if suggestions:
            assert all("description" in s for s in suggestions)
        
        # Test with explanations disabled
        request_without_explanations = {
            "text": "for",
            "position": 3,
            "context": {
                "include_explanations": False,
                "educational_mode": True
            }
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request_without_explanations)
        assert response.status_code == 200
        suggestions = response.json()["data"]["suggestions"]
        if suggestions:
            assert all("description" not in s or s["description"] is None for s in suggestions)
    
    def test_max_suggestions_limit(self, test_client):
        """Test max_suggestions parameter limits results."""
        # Arrange
        request = {
            "text": "",
            "position": 0,
            "context": {
                "max_suggestions": 3,
                "educational_mode": True
            }
        }
        
        # Act
        response = test_client.post("/api/nlp/autocomplete", json=request)
        
        # Assert
        assert response.status_code == 200
        suggestions = response.json()["data"]["suggestions"]
        assert len(suggestions) <= 3


class TestIntegration:
    """Test full integration scenarios."""
    
    def test_full_request_response_cycle(self, test_client):
        """Test complete request/response cycle with all features."""
        # Arrange
        request = {
            "text": "forall x",
            "position": 8,
            "context": {
                "language_mode": "TAU",
                "learning_level": "intermediate",
                "include_examples": True,
                "include_explanations": True,
                "max_suggestions": 5,
                "educational_mode": True,
                "context_type": "quantifier_expression"
            }
        }
        
        # Act
        response = test_client.post("/api/nlp/autocomplete", json=request)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "suggestions" in data["data"]
        
        # Check response includes educational metadata
        if "context_hint" in data["data"]:
            assert isinstance(data["data"]["context_hint"], str)
        if "learning_tip" in data["data"]:
            assert isinstance(data["data"]["learning_tip"], str)
    
    def test_error_handling_invalid_request(self, test_client):
        """Test error handling for invalid requests."""
        # Missing required field
        invalid_request = {
            "position": 5
            # Missing 'text' field
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    def test_error_handling_service_failure(self, test_client, mock_educational_service):
        """Test handling when educational service fails."""
        # Arrange
        request = {
            "text": "test",
            "position": 4,
            "context": {"educational_mode": True}
        }
        
        mock_educational_service.get_suggestions_async.return_value = Failure(
            "SERVICE_ERROR", "Educational service unavailable"
        )
        
        with patch("backend.unified.api.nlp._get_educational_service",
                  return_value=mock_educational_service):
            # Act
            response = test_client.post("/api/nlp/autocomplete", json=request)
            
            # Assert - Should fallback gracefully
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            # Should fallback to basic suggestions
            assert data["data"]["source"] == "basic"
    
    def test_with_nlp_service_available(self, test_client, mock_nlp_service):
        """Test integration when NLP service is available."""
        with patch("backend.unified.api.nlp.NLPServiceLoader.load_nlp_service_async",
                  return_value=Success(mock_nlp_service)):
            # Arrange
            request = {
                "text": "al",
                "position": 2,
                "context": {"use_nlp": True}
            }
            
            # Act
            response = test_client.post("/api/nlp/autocomplete", json=request)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["source"] == "nlp"
            mock_nlp_service.autocomplete_engine.get_completions.assert_called_once()
    
    def test_without_nlp_service(self, test_client):
        """Test integration when NLP service is not available."""
        with patch("backend.unified.api.nlp.NLPServiceLoader.load_nlp_service_async",
                  return_value=Success(None)):
            # Arrange
            request = {
                "text": "al",
                "position": 2
            }
            
            # Act
            response = test_client.post("/api/nlp/autocomplete", json=request)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["source"] == "basic"
            assert len(data["data"]["suggestions"]) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_text_suggestions(self, test_client):
        """Test suggestions for empty text."""
        request = {
            "text": "",
            "position": 0,
            "context": {"educational_mode": True}
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request)
        assert response.status_code == 200
        # Should return some default suggestions
    
    def test_position_beyond_text_length(self, test_client):
        """Test when position exceeds text length."""
        request = {
            "text": "test",
            "position": 10,  # Beyond text length
            "context": {"educational_mode": True}
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request)
        assert response.status_code == 200
        # Should handle gracefully
    
    def test_special_characters_in_text(self, test_client):
        """Test handling of special characters."""
        request = {
            "text": "x -> y && z",
            "position": 11,
            "context": {"educational_mode": True}
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request)
        assert response.status_code == 200
    
    def test_unicode_text_handling(self, test_client):
        """Test handling of unicode characters."""
        request = {
            "text": "∀x : x > 0",
            "position": 10,
            "context": {"educational_mode": True}
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request)
        assert response.status_code == 200
    
    def test_concurrent_requests(self, test_client):
        """Test handling of concurrent requests."""
        import asyncio
        
        async def make_request():
            return test_client.post("/api/nlp/autocomplete", json={
                "text": "test",
                "position": 4
            })
        
        # Simulate concurrent requests
        loop = asyncio.new_event_loop()
        tasks = [make_request() for _ in range(5)]
        # All requests should succeed
    
    def test_malformed_context(self, test_client):
        """Test handling of malformed context data."""
        request = {
            "text": "test",
            "position": 4,
            "context": {
                "language_mode": "INVALID",
                "learning_level": 123,  # Should be string
                "max_suggestions": "five"  # Should be number
            }
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request)
        # Should handle gracefully with defaults
        assert response.status_code in [200, 422]


class TestContextualSuggestions:
    """Test context-aware suggestion features."""
    
    def test_solver_command_context(self, test_client):
        """Test suggestions in solver command context."""
        request = {
            "text": "solve",
            "position": 5,
            "context": {
                "context_type": "solver_command",
                "educational_mode": True
            }
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request)
        assert response.status_code == 200
        # Should get solver-specific suggestions
    
    def test_temporal_constraint_context(self, test_client):
        """Test suggestions in temporal constraint context."""
        request = {
            "text": "alw",
            "position": 3,
            "context": {
                "context_type": "temporal_constraint",
                "educational_mode": True
            }
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request)
        assert response.status_code == 200
        suggestions = response.json()["data"]["suggestions"]
        # Should prioritize temporal keywords
        if suggestions:
            assert any("always" in s["text"] for s in suggestions)
    
    def test_variables_in_scope(self, test_client):
        """Test suggestions include variables in scope."""
        request = {
            "text": "x",
            "position": 1,
            "context": {
                "variables_in_scope": ["x", "y", "counter"],
                "educational_mode": True
            }
        }
        
        response = test_client.post("/api/nlp/autocomplete", json=request)
        assert response.status_code == 200
        # Should include variables as suggestions