"""
Tests the end-to-end functionality of the NLPAutocompleteService.

This test suite validates the entire railway-oriented pipeline, ensuring that
the service correctly handles valid inputs, produces accurate suggestions, and
gracefully manages failures like parsing errors.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from returns.result import Success, Failure

from tau_translator_omega.core_engine.autocomplete.domain import (
    AutocompleteRequest,
    AutocompleteError,
    SuggestionType,
)
from tau_translator_omega.services.autocomplete_service import NLPAutocompleteService


@pytest.mark.asyncio
async def test_service_returns_success_for_valid_prefix():
    """Verify the service returns correct suggestions for a valid prefix."""
    # Arrange
    service = NLPAutocompleteService()
    request = AutocompleteRequest(text="alw", cursor_position=3)

    # Act
    result = await service.get_suggestions_for_request_async(request)

    # Assert
    assert isinstance(result, Success)
    suggestions = result.unwrap()
    assert len(suggestions) == 1
    assert suggestions[0].text == "always"
    assert suggestions[0].type == SuggestionType.KEYWORD


@pytest.mark.asyncio
async def test_service_returns_failure_for_unparseable_text():
    """Verify the service returns a parsing error for invalid syntax."""
    # Arrange
    service = NLPAutocompleteService()
    # Assuming '$$$' is not valid syntax in the grammar
    request = AutocompleteRequest(text="$$$", cursor_position=3)

    # Act
    result = await service.get_suggestions_for_request_async(request)

    # Assert
    assert isinstance(result, Failure)
    assert result.failure() == AutocompleteError.PARSING_ERROR


@pytest.mark.asyncio
async def test_service_returns_no_suggestions_for_unknown_prefix():
    """Verify the service returns an empty list for a prefix with no matches."""
    # Arrange
    service = NLPAutocompleteService()
    request = AutocompleteRequest(text="xyz", cursor_position=3)

    # Act
    result = await service.get_suggestions_for_request_async(request)

    # Assert
    assert isinstance(result, Success)
    suggestions = result.unwrap()
    assert len(suggestions) == 0
