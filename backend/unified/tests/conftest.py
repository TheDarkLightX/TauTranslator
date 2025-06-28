"""
Pytest configuration for unified backend tests.

Provides common fixtures and test configuration.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path


@pytest.fixture
def mock_nlp_service():
    """Mock NLP service for testing."""
    from unittest.mock import Mock
    
    service = Mock()
    service.autocomplete_engine = Mock()
    service.autocomplete_engine.get_completions = Mock(
        return_value=[("always", 0.9), ("all", 0.7)]
    )
    return service


@pytest.fixture
def sample_tau_suggestions():
    """Sample TAU language suggestions."""
    from backend.unified.core.autocomplete.models import (
        EducationalSuggestion,
        SuggestionText,
        DisplayText,
        HintText,
        ExampleCode,
        SuggestionCategory,
        DifficultyLevel,
        ConfidenceScore
    )
    
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


@pytest.fixture
def sample_tce_suggestions():
    """Sample TCE language suggestions."""
    from backend.unified.core.autocomplete.models import (
        EducationalSuggestion,
        SuggestionText,
        DisplayText,
        HintText,
        ExampleCode,
        SuggestionCategory,
        DifficultyLevel,
        ConfidenceScore,
        TauCode
    )
    
    return [
        EducationalSuggestion(
            text=SuggestionText("for all x such that"),
            display=DisplayText("for all x such that - universal quantifier"),
            category=SuggestionCategory.PATTERN,
            description=HintText("English-like universal quantification"),
            example=ExampleCode("for all x such that x > 0"),
            difficulty=DifficultyLevel.BEGINNER,
            tau_equivalent=TauCode("forall x : x > 0"),
            confidence=ConfidenceScore(0.90)
        ),
        EducationalSuggestion(
            text=SuggestionText("it is always the case that"),
            display=DisplayText("it is always the case that - temporal"),
            category=SuggestionCategory.PATTERN,
            description=HintText("English-like temporal constraint"),
            example=ExampleCode("it is always the case that door_closed"),
            difficulty=DifficultyLevel.BEGINNER,
            tau_equivalent=TauCode("always (door_closed)"),
            confidence=ConfidenceScore(0.88)
        )
    ]