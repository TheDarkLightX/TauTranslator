"""
Tests for bidirectional translation functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from returns.result import Success

from backend.unified.core.domain_types import SourceText, AppError
from backend.unified.translators.base import TranslationDirection, TranslationResult
from backend.unified.translators.manager_v2 import TranslationManager
from backend.unified.translators.tau_to_nl_strategy import TauToNaturalLanguageStrategy
from backend.unified.core.llm_client import LLMClient
from backend.unified.core.ifaces import ICacheRepository, IEventBus


@pytest.fixture
def llm_client() -> LLMClient:
    """Fixture for a mock LLMClient."""
    client = Mock(spec=LLMClient)
    client.query_async = AsyncMock(return_value="This is a test translation.")
    return client


@pytest.mark.asyncio
async def test_tau_to_nl_translation(llm_client):
    """Test that the manager can translate from Tau to Natural Language."""
    # Arrange
    mock_cache_repo = AsyncMock(spec=ICacheRepository)
    mock_cache_repo.get_cached_value_async.return_value = Success(None)  # Simulate cache miss
    mock_event_bus = Mock(spec=IEventBus)
    manager = TranslationManager(cache_repository=mock_cache_repo, event_bus=mock_event_bus)

    tau_to_nl_strategy = TauToNaturalLanguageStrategy(llm_client=llm_client)
    manager.register_engine(tau_to_nl_strategy)

    tau_code = SourceText("person(name: 'John Doe', age: 30).")
    direction = TranslationDirection.TAU_TO_NL

    # Act
    result = await manager.translate_async(tau_code, direction)

    # Assert
    assert result.is_ok()
    translation = result.unwrap()
    assert translation.success
    assert translation.direction == direction
    assert translation.translation_method == "tau_to_nl_strategy"
    assert "test translation" in translation.translated_text
