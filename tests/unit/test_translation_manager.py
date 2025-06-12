"""
Unit tests for the refactored TranslationManager.
Follows BDD style with Given-When-Then structure.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.manager import TranslationManager
from backend.unified.translators.base import TranslationDirection, TranslationResult, TranslationEngine
from backend.unified.core.domain_types import SourceText, Success, Failure


class MockEngine(TranslationEngine):
    """Mock translation engine for testing."""
    
    def __init__(self, name="mock_engine", available=True, can_translate_result=True):
        super().__init__(name=name, description=f"Mock {name}")
        self.is_available = available
        self._can_translate_result = can_translate_result
        self.translate_calls = []
        
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        return self._can_translate_result and bool(text.strip())
    
    def get_supported_directions(self) -> list:
        return [TranslationDirection.TO_TAU, TranslationDirection.TO_TCE]
    
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        self.translate_calls.append((text, direction, kwargs))
        if text == "error":
            return TranslationResult(
                success=False,
                translated_text="",
                original_text=text,
                translation_method=self.name,
                direction=direction,
                confidence=0.0,
                error_message="Test error"
            )
        return TranslationResult(
            success=True,
            translated_text=f"translated_{text}",
            original_text=text,
            translation_method=self.name,
            direction=direction,
            confidence=0.8,
            metadata={"mock": True}
        )
    
    async def translate_async(self, text: SourceText, direction: TranslationDirection, **kwargs):
        """Async translate method."""
        result = self.translate(str(text), direction, **kwargs)
        if result.success:
            return Success(result)
        return Failure("TRANSLATION_ERROR", result.error_message)


class TestTranslationManagerRefactored:
    """Test suite for refactored TranslationManager."""
    
    @pytest.fixture
    def mock_event_bus(self):
        """Create mock event bus."""
        mock = Mock()
        mock.publish = Mock()
        return mock
    
    @pytest.fixture
    def mock_cache_repository(self):
        """Create mock cache repository."""
        mock = Mock()
        mock.get_async = AsyncMock(return_value=None)
        mock.set_async = AsyncMock()
        return mock
    
    @pytest.fixture
    def manager(self, mock_event_bus, mock_cache_repository):
        """Create translation manager with mocked dependencies."""
        return TranslationManager(
            event_bus=mock_event_bus,
            cache_repository=mock_cache_repository
        )
    
    @pytest.fixture
    def mock_engine(self):
        """Create mock translation engine."""
        return MockEngine()
    
    # Basic functionality tests
    
    def test_manager_initialization(self, manager):
        """Test manager initializes correctly."""
        # Given: A newly created manager
        # When: We check its initialization
        # Then: All components should be properly set up
        assert hasattr(manager, '_registry')
        assert hasattr(manager, '_cache')
        assert hasattr(manager, '_event_publisher')
        assert manager._confidence_threshold == 0.7
    
    def test_register_engine_success(self, manager, mock_engine):
        """Test successful engine registration."""
        # Given: A valid engine
        # When: We register it
        result = manager.register_engine(mock_engine)
        
        # Then: Registration should succeed
        assert result.is_success()
    
    def test_register_default_engine(self, manager, mock_engine):
        """Test registering an engine as default."""
        # Given: An engine to register as default
        # When: We register it with is_default=True
        result = manager.register_engine(mock_engine, is_default=True)
        
        # Then: Registration should succeed
        assert result.is_success()
    
    def test_register_fallback_engine(self, manager, mock_engine):
        """Test registering an engine as fallback."""
        # Given: An engine to register as fallback
        # When: We register it with is_fallback=True
        result = manager.register_engine(mock_engine, is_fallback=True)
        
        # Then: Registration should succeed
        assert result.is_success()
    
    def test_multiple_engine_registration(self, manager):
        """Test registering multiple engines."""
        # Given: Multiple engines
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2") 
        
        # When: We register them
        result1 = manager.register_engine(engine1)
        result2 = manager.register_engine(engine2, is_fallback=True)
        
        # Then: Both registrations should succeed
        assert result1.is_success()
        assert result2.is_success()
    
    # Translation tests
    
    @pytest.mark.asyncio
    async def test_translate_async_success(self, manager, mock_engine):
        """Test successful async translation."""
        # Given: A registered engine
        manager.register_engine(mock_engine, is_default=True)
        
        # When: We translate text
        result = await manager.translate_async(
            SourceText("hello"),
            TranslationDirection.TO_TAU
        )
        
        # Then: Translation should succeed
        assert result.is_success()
        translated = result.value
        assert translated.translated_text == "translated_hello"
        assert translated.success is True
    
    @pytest.mark.asyncio
    async def test_translate_async_with_cache(self, manager, mock_engine, mock_cache_repository):
        """Test translation with caching."""
        # Given: A registered engine and cache enabled
        manager.register_engine(mock_engine, is_default=True)
        
        # When: We translate with cache
        result = await manager.translate_async(
            SourceText("hello"),
            TranslationDirection.TO_TAU,
            use_cache=True
        )
        
        # Then: Cache should be checked and result cached
        assert mock_cache_repository.get_async.called
        assert result.is_success()
    
    @pytest.mark.asyncio
    async def test_translate_async_empty_text(self, manager, mock_engine):
        """Test translation with empty text."""
        # Given: A registered engine
        manager.register_engine(mock_engine, is_default=True)
        
        # When: We translate empty text
        result = await manager.translate_async(
            SourceText(""),
            TranslationDirection.TO_TAU
        )
        
        # Then: Translation should fail
        assert result.is_failure()
    
    @pytest.mark.asyncio
    async def test_translate_with_preferred_engine(self, manager):
        """Test translation with preferred engine."""
        # Given: Multiple registered engines
        engine1 = MockEngine("engine1")
        engine2 = MockEngine("engine2")
        manager.register_engine(engine1)
        manager.register_engine(engine2)
        
        # When: We translate with preferred engine
        result = await manager.translate_async(
            SourceText("hello"),
            TranslationDirection.TO_TAU,
            preferred_engine="engine2"
        )
        
        # Then: The preferred engine should be used
        assert result.is_success()
        assert len(engine2.translate_calls) == 1
        assert len(engine1.translate_calls) == 0
    
    @pytest.mark.asyncio
    async def test_translate_fallback_on_error(self, manager):
        """Test fallback mechanism when primary fails."""
        # Given: Primary engine that can't translate this text and fallback engine
        primary = MockEngine("primary", can_translate_result=False)
        fallback = MockEngine("fallback")
        manager.register_engine(primary, is_default=True)
        manager.register_engine(fallback, is_fallback=True)
        
        # When: We translate text
        result = await manager.translate_async(
            SourceText("hello"),
            TranslationDirection.TO_TAU,
            use_fallback=True
        )
        
        # Then: Fallback should be used since primary can't translate
        assert result.is_success()
        # Primary won't even be called since can_translate returns False
        assert len(fallback.translate_calls) == 1
    
    # Event publishing tests
    
    @pytest.mark.asyncio
    async def test_translation_events_published(self, manager, mock_engine, mock_event_bus):
        """Test that translation events are published."""
        # Given: A registered engine
        manager.register_engine(mock_engine, is_default=True)
        
        # When: We translate
        await manager.translate_async(
            SourceText("hello"),
            TranslationDirection.TO_TAU
        )
        
        # Then: Events should be published
        assert mock_event_bus.publish.call_count >= 2  # At least started and completed
    
    # Edge cases
    
    @pytest.mark.asyncio
    async def test_no_engines_registered(self, manager):
        """Test translation with no engines registered."""
        # Given: No engines registered
        # When: We try to translate
        result = await manager.translate_async(
            SourceText("hello"),
            TranslationDirection.TO_TAU
        )
        
        # Then: Translation should fail
        assert result.is_failure()
        assert "ALL_ENGINES_FAILED" in str(result)
    
    def test_confidence_threshold_setting(self, manager):
        """Test confidence threshold is properly set."""
        # Given: Default manager
        # When: We check confidence threshold
        # Then: It should match the default
        assert manager._confidence_threshold == 0.7
        
        # And: We can create manager with custom threshold
        custom_manager = TranslationManager(
            event_bus=Mock(),
            cache_repository=Mock(),
            confidence_threshold=0.9
        )
        assert custom_manager._confidence_threshold == 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])