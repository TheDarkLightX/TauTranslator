"""
Unit tests for the refactored TranslationManager.
Follows BDD style with Given-When-Then structure.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from unittest.mock import Mock, AsyncMock
import asyncio

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful

from backend.unified.core.domain_types import AppError, SourceText
from backend.unified.translators.base import (
    TranslationDirection,
    TranslationEngine,
    TranslationResult,
)
from backend.unified.translators.manager import TranslationManager


@pytest.fixture
def mock_event_bus():
    """Fixture for a mock event bus."""
    return Mock()


@pytest.fixture
def mock_cache_repository():
    """Fixture for a mock cache repository."""
    mock = Mock()
    # Simulate cache miss by default
    mock.get_async = AsyncMock(return_value=None)
    mock.set_async = AsyncMock()
    return mock


@pytest.fixture
def manager(mock_event_bus, mock_cache_repository):
    """Fixture for a TranslationManager instance."""
    return TranslationManager(
        event_bus=mock_event_bus, cache_repository=mock_cache_repository
    )


class MockEngine(TranslationEngine):
    """A flexible mock engine for testing that adheres to the new ABC."""

    def __init__(self, name="mock_engine", can_translate_result=True, fails=False):
        self._name = name
        self._can_translate_result = can_translate_result
        self._fails = fails

    @property
    def name(self) -> str:
        return self._name

    def can_translate(self, text: SourceText, direction: TranslationDirection) -> bool:
        return self._can_translate_result

    def get_supported_directions(self) -> list[TranslationDirection]:
        """Returns supported translation directions."""
        return [TranslationDirection.TO_TAU, TranslationDirection.TO_TCE]

    def translate(
        self, text: SourceText, direction: TranslationDirection, **kwargs
    ) -> Result[TranslationResult, AppError]:
        """Simulates synchronous translation, returning a Result monad."""
        if self._fails:
            return Failure(AppError(error_code="TRANSLATION_ERROR", message="Engine failed as configured"))

        return Success(
            TranslationResult(
                success=True,
                translated_text=f"{self.name} translation",
                original_text=str(text),
                translation_method=self.name,
                direction=direction,
                confidence=0.9,
            )
        )

    async def translate_async(
        self, text: SourceText, direction: TranslationDirection, **kwargs
    ) -> Result[TranslationResult, AppError]:
        """Simulates async translation, returning a Result monad."""
        if self._fails:
            return Failure(AppError(error_code="TRANSLATION_ERROR", message="Engine failed as configured"))

        return Success(
            TranslationResult(
                success=True,
                translated_text=f"{self.name} translation",
                original_text=str(text),
                translation_method=self.name,
                direction=direction,
                confidence=0.9,
            )
        )


@pytest.fixture
def mock_engine():
    """Fixture for a default mock translation engine."""
    return MockEngine()


class TestTranslationManagerRefactored:
    """Tests for the refactored TranslationManager."""

    def test_manager_initialization(self, manager):
        """Test that the manager and its components are initialized correctly."""
        assert manager is not None
        assert hasattr(manager, "_registry")
        assert hasattr(manager, "_cache")
        assert hasattr(manager, "_event_publisher")
        assert manager._confidence_threshold == 0.7

    def test_register_engine_success(self, manager, mock_engine):
        """Test successful engine registration."""
        result = manager.register_engine(mock_engine)
        assert is_successful(result)
        registrations = manager._registry.get_all()
        assert len(registrations) == 1
        assert registrations[0].engine == mock_engine

    def test_register_default_engine(self, manager, mock_engine):
        """Test registering an engine as default."""
        manager.register_engine(mock_engine, is_default=True)
        registrations = manager._registry.get_all()
        assert len(registrations) == 1
        assert registrations[0].is_default

    def test_register_fallback_engine(self, manager, mock_engine):
        """Test registering a fallback engine."""
        manager.register_engine(mock_engine, is_fallback=True)
        registrations = manager._registry.get_all()
        assert len(registrations) == 1
        assert registrations[0].is_fallback

    def test_multiple_engine_registration(self, manager, mock_engine):
        """Test registering multiple engines."""
        another_engine = MockEngine(name="another_mock_engine")
        manager.register_engine(mock_engine)
        manager.register_engine(another_engine)
        assert len(manager._registry.get_all()) == 2

    @pytest.mark.asyncio
    async def test_translate_async_success(self, manager, mock_engine):
        """Test a successful translation."""
        manager.register_engine(mock_engine, is_default=True)
        result = await manager.translate_async(
            SourceText("hello"), TranslationDirection.TO_TAU
        )
        assert is_successful(result)
        assert result.unwrap().translated_text == "mock_engine translation"

    @pytest.mark.asyncio
    async def test_translate_async_with_cache(
        self, manager, mock_engine, mock_cache_repository
    ):
        """Test that a cached result is returned."""
        cached_result = TranslationResult(
            success=True,
            translated_text="cached translation",
            original_text="hello",
            translation_method="cache",
            direction=TranslationDirection.TO_TAU,
            confidence=0.99,
        )
        mock_cache_repository.get_async.return_value = cached_result
        
        # Replace the real engine's method with a mock to track calls
        mock_engine.translate_async = AsyncMock()
        
        manager.register_engine(mock_engine, is_default=True)

        result = await manager.translate_async(
            SourceText("hello"), TranslationDirection.TO_TAU
        )

        assert is_successful(result)
        assert result.unwrap() == cached_result
        mock_engine.translate_async.assert_not_called()

    @pytest.mark.asyncio
    async def test_translate_async_empty_text(self, manager, mock_engine):
        """Test translation with empty text."""
        manager.register_engine(mock_engine, is_default=True)
        result = await manager.translate_async(
            SourceText(""), TranslationDirection.TO_TAU
        )
        assert not is_successful(result)
        assert result.failure().error_code == "EMPTY_TEXT"

    @pytest.mark.asyncio
    async def test_translate_with_preferred_engine(self, manager, mock_engine):
        """Test translation using a preferred engine."""
        another_engine = MockEngine(name="another_engine")
        manager.register_engine(mock_engine, is_default=True)
        manager.register_engine(another_engine)

        result = await manager.translate_async(
            SourceText("hello"),
            TranslationDirection.TO_TAU,
            preferred_engine="another_engine",
        )
        assert is_successful(result)
        assert result.unwrap().translation_method == "another_engine"

    @pytest.mark.asyncio
    async def test_translate_fallback_on_error(self, manager):
        """Test that fallback engine is used on primary engine failure."""
        failing_engine = MockEngine(name="failing_engine", fails=True)
        fallback_engine = MockEngine(name="fallback_engine")

        manager.register_engine(failing_engine, is_default=True)
        manager.register_engine(fallback_engine, is_fallback=True)

        result = await manager.translate_async(
            SourceText("hello"), TranslationDirection.TO_TAU
        )
        assert is_successful(result)
        assert result.unwrap().translation_method == "fallback_engine"

    @pytest.mark.asyncio
    async def test_translation_events_published(
        self, manager, mock_engine, mock_event_bus
    ):
        """Test that translation events are published."""
        manager.register_engine(mock_engine, is_default=True)
        await manager.translate_async(SourceText("hello"), TranslationDirection.TO_TAU)
        # Expect at least a 'started' and 'completed' event
        assert mock_event_bus.publish.call_count >= 2

    @pytest.mark.asyncio
    async def test_no_engines_registered(self, manager):
        """Test translation with no engines registered."""
        result = await manager.translate_async(
            SourceText("hello"), TranslationDirection.TO_TAU
        )
        assert not is_successful(result)
        assert result.failure().error_code == "NO_ENGINE_AVAILABLE"

    def test_confidence_threshold_setting(self):
        """Test confidence threshold is properly set."""
        manager = TranslationManager(
            event_bus=Mock(), cache_repository=Mock(), confidence_threshold=0.9
        )
        assert manager._confidence_threshold == 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])