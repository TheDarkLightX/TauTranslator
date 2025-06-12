"""
Integration tests for educational autocomplete with mock API implementation.

This demonstrates how the educational autocomplete should integrate
with the existing NLP API while maintaining backward compatibility.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch

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
from backend.unified.core.responses import create_success_response, create_error_response
from backend.unified.core.result_enhanced import Success, Failure


class EducationalAutocompleteRequest:
    """Enhanced autocomplete request with educational features."""
    
    def __init__(self, data: Dict[str, Any]):
        self.text: str = data.get("text", "")
        self.position: int = data.get("position", len(self.text))
        self.context: Optional[Dict[str, Any]] = data.get("context")
    
    def is_educational_mode(self) -> bool:
        """Check if educational mode is enabled."""
        return self.context and self.context.get("educational_mode", False)
    
    def get_language_mode(self) -> LanguageMode:
        """Extract language mode from context."""
        if not self.context:
            return LanguageMode.TAU
        
        mode = self.context.get("language_mode", "TAU").upper()
        try:
            return LanguageMode[mode]
        except KeyError:
            return LanguageMode.TAU
    
    def get_learning_level(self) -> DifficultyLevel:
        """Extract learning level from context."""
        if not self.context:
            return DifficultyLevel.INTERMEDIATE
        
        level = self.context.get("learning_level", "intermediate").lower()
        level_map = {
            "beginner": DifficultyLevel.BEGINNER,
            "intermediate": DifficultyLevel.INTERMEDIATE,
            "advanced": DifficultyLevel.ADVANCED
        }
        return level_map.get(level, DifficultyLevel.INTERMEDIATE)
    
    def get_max_suggestions(self) -> int:
        """Get maximum number of suggestions."""
        if not self.context:
            return 10
        return self.context.get("max_suggestions", 10)
    
    def should_include_examples(self) -> bool:
        """Check if examples should be included."""
        if not self.context:
            return True
        return self.context.get("include_examples", True)
    
    def should_include_explanations(self) -> bool:
        """Check if explanations should be included."""
        if not self.context:
            return True
        return self.context.get("include_explanations", True)


class MockEducationalAutocompleteService:
    """Mock implementation for testing."""
    
    def __init__(self):
        self.config = AutocompleteConfiguration()
        self._suggestions_db = self._build_suggestions_database()
    
    def _build_suggestions_database(self) -> Dict[str, List[EducationalSuggestion]]:
        """Build a database of educational suggestions."""
        return {
            "al": [
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
                    text=SuggestionText("all"),
                    display=DisplayText("all - common in patterns"),
                    category=SuggestionCategory.KEYWORD,
                    description=HintText("Used in 'for all' patterns"),
                    example=ExampleCode("for all x in set"),
                    difficulty=DifficultyLevel.BEGINNER,
                    confidence=ConfidenceScore(0.85)
                )
            ],
            "for": [
                EducationalSuggestion(
                    text=SuggestionText("forall"),
                    display=DisplayText("forall - universal quantifier"),
                    category=SuggestionCategory.QUANTIFIER,
                    description=HintText("Universal quantification - true for all values"),
                    example=ExampleCode("forall x : x > 0 -> f(x) > 0"),
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    confidence=ConfidenceScore(0.90)
                ),
                EducationalSuggestion(
                    text=SuggestionText("for all x such that"),
                    display=DisplayText("for all x such that - TCE pattern"),
                    category=SuggestionCategory.PATTERN,
                    description=HintText("English-like universal quantification"),
                    example=ExampleCode("for all x such that x > 0"),
                    difficulty=DifficultyLevel.BEGINNER,
                    tau_equivalent=TauCode("forall x : x > 0"),
                    confidence=ConfidenceScore(0.88)
                )
            ]
        }
    
    async def get_suggestions_async(
        self,
        request: SuggestionRequest
    ) -> Success[SuggestionResponse]:
        """Get educational suggestions based on context."""
        text = request.context.get_text_before_cursor()
        
        # Find matching suggestions
        suggestions = []
        for prefix, suggs in self._suggestions_db.items():
            if text.startswith(prefix):
                suggestions.extend(suggs)
        
        # Filter by learning level
        level = request.context.learning_level
        if level == DifficultyLevel.BEGINNER:
            suggestions = [s for s in suggestions if s.difficulty == DifficultyLevel.BEGINNER]
        
        # Apply max suggestions limit
        max_suggs = request.max_suggestions
        suggestions = suggestions[:max_suggs]
        
        # Create response with hints
        context_hint = self._generate_context_hint(request.context)
        learning_tip = self._generate_learning_tip(suggestions, request.context)
        
        return Success(SuggestionResponse(
            suggestions=suggestions,
            context_hint=context_hint,
            learning_tip=learning_tip
        ))
    
    def _generate_context_hint(self, context: SpecificationContext) -> Optional[HintText]:
        """Generate contextual hint."""
        if context.context_type == ContextType.QUANTIFIER_EXPRESSION:
            return HintText("You're writing a quantifier. Use 'forall' or 'exists'.")
        return None
    
    def _generate_learning_tip(
        self,
        suggestions: List[EducationalSuggestion],
        context: SpecificationContext
    ) -> Optional[HintText]:
        """Generate learning tip."""
        if context.learning_level == DifficultyLevel.BEGINNER:
            return HintText("Start with simple patterns. Each suggestion includes an example.")
        return None


async def enhanced_autocomplete_endpoint(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced autocomplete endpoint supporting educational features.
    
    This demonstrates how the API should handle both legacy and educational requests.
    """
    request = EducationalAutocompleteRequest(request_data)
    
    if request.is_educational_mode():
        # Use educational autocomplete service
        service = MockEducationalAutocompleteService()
        
        # Build domain context
        context = SpecificationContext(
            full_text=request.text,
            cursor_position=CursorPosition(request.position),
            language_mode=request.get_language_mode(),
            context_type=ContextType.BOOLEAN_EXPRESSION,  # Would be detected from text
            learning_level=request.get_learning_level()
        )
        
        # Create suggestion request
        suggestion_request = SuggestionRequest(
            context=context,
            max_suggestions=request.get_max_suggestions(),
            include_examples=request.should_include_examples(),
            include_templates=True
        )
        
        # Get suggestions
        result = await service.get_suggestions_async(suggestion_request)
        
        if result.is_success():
            response = result.value
            
            # Format suggestions based on flags
            formatted_suggestions = []
            for sugg in response.suggestions:
                formatted = {
                    "text": sugg.text,
                    "type": sugg.category.value,
                    "confidence": float(sugg.confidence),
                    "difficulty": sugg.difficulty.value
                }
                
                if request.should_include_explanations():
                    formatted["description"] = sugg.description
                
                if request.should_include_examples():
                    formatted["example"] = sugg.example
                
                if sugg.tau_equivalent:
                    formatted["tau_equivalent"] = sugg.tau_equivalent
                
                formatted_suggestions.append(formatted)
            
            response_data = {
                "suggestions": formatted_suggestions,
                "source": "educational"
            }
            
            if response.context_hint:
                response_data["context_hint"] = response.context_hint
            
            if response.learning_tip:
                response_data["learning_tip"] = response.learning_tip
            
            return create_success_response(response_data)
        else:
            return create_error_response("Failed to get educational suggestions")
    
    else:
        # Legacy mode - simple suggestions
        text = request.text.lower()
        basic_suggestions = []
        
        if text.startswith("al"):
            basic_suggestions = [
                {"text": "always", "type": "temporal"},
                {"text": "all", "type": "keyword"}
            ]
        elif text.startswith("for"):
            basic_suggestions = [
                {"text": "forall", "type": "quantifier"},
                {"text": "for", "type": "keyword"}
            ]
        
        return create_success_response({
            "suggestions": basic_suggestions,
            "source": "basic"
        })


class TestEducationalAutocompleteIntegration:
    """Test educational autocomplete integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_educational_mode_full_features(self):
        """Test educational mode with all features enabled."""
        # Arrange
        request = {
            "text": "forall",
            "position": 6,
            "context": {
                "educational_mode": True,
                "language_mode": "TAU",
                "learning_level": "intermediate",
                "include_examples": True,
                "include_explanations": True,
                "max_suggestions": 5
            }
        }
        
        # Act
        response = await enhanced_autocomplete_endpoint(request)
        
        # Assert
        assert response["status"] == "success"
        data = response["data"]
        assert data["source"] == "educational"
        assert len(data["suggestions"]) > 0
        
        # Check first suggestion has all fields
        first = data["suggestions"][0]
        assert "text" in first
        assert "type" in first
        assert "confidence" in first
        assert "difficulty" in first
        assert "description" in first
        assert "example" in first
    
    @pytest.mark.asyncio
    async def test_legacy_mode_backward_compatibility(self):
        """Test legacy mode maintains backward compatibility."""
        # Arrange
        request = {
            "text": "al",
            "position": 2
            # No context = legacy mode
        }
        
        # Act
        response = await enhanced_autocomplete_endpoint(request)
        
        # Assert
        assert response["status"] == "success"
        data = response["data"]
        assert data["source"] == "basic"
        suggestions = data["suggestions"]
        
        # Check legacy format
        for sugg in suggestions:
            assert "text" in sugg
            assert "type" in sugg
            assert "description" not in sugg
            assert "example" not in sugg
    
    @pytest.mark.asyncio
    async def test_tce_language_mode(self):
        """Test TCE language mode suggestions."""
        # Arrange
        request = {
            "text": "for",
            "position": 3,
            "context": {
                "educational_mode": True,
                "language_mode": "TCE",
                "learning_level": "beginner"
            }
        }
        
        # Act
        response = await enhanced_autocomplete_endpoint(request)
        
        # Assert
        assert response["status"] == "success"
        suggestions = response["data"]["suggestions"]
        
        # Should have TCE pattern
        tce_suggestion = next((s for s in suggestions if "for all x such that" in s["text"]), None)
        assert tce_suggestion is not None
        assert tce_suggestion["tau_equivalent"] == "forall x : x > 0"
    
    @pytest.mark.asyncio
    async def test_learning_tips_included(self):
        """Test learning tips are included for beginners."""
        # Arrange
        request = {
            "text": "al",
            "position": 2,
            "context": {
                "educational_mode": True,
                "learning_level": "beginner"
            }
        }
        
        # Act
        response = await enhanced_autocomplete_endpoint(request)
        
        # Assert
        assert response["status"] == "success"
        data = response["data"]
        assert "learning_tip" in data
        assert "Start with simple patterns" in data["learning_tip"]
    
    @pytest.mark.asyncio
    async def test_exclude_examples_flag(self):
        """Test examples can be excluded."""
        # Arrange
        request = {
            "text": "al",
            "position": 2,
            "context": {
                "educational_mode": True,
                "include_examples": False,
                "include_explanations": True
            }
        }
        
        # Act
        response = await enhanced_autocomplete_endpoint(request)
        
        # Assert
        suggestions = response["data"]["suggestions"]
        for sugg in suggestions:
            assert "example" not in sugg
            assert "description" in sugg  # Explanations still included
    
    @pytest.mark.asyncio
    async def test_max_suggestions_limit(self):
        """Test max suggestions limit is respected."""
        # Arrange
        request = {
            "text": "al",
            "position": 2,
            "context": {
                "educational_mode": True,
                "max_suggestions": 1
            }
        }
        
        # Act
        response = await enhanced_autocomplete_endpoint(request)
        
        # Assert
        suggestions = response["data"]["suggestions"]
        assert len(suggestions) == 1