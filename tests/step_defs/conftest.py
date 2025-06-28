import pytest
import tempfile
import shutil
from pathlib import Path

from typing import Dict, Any, Optional

from backend.unified.core.domain_types import Result, Success, AppError
from backend.unified.core.interfaces import IEventBus, ICacheRepository


class DummyEventBus(IEventBus):
    """A dummy event bus that does nothing, for testing purposes."""
    async def publish_event_async(self, event_type: str, data: Dict[str, Any]) -> Result[None, AppError]:
        # In a real scenario, this would publish to a message queue.
        # For the dummy implementation, we just log it or do nothing.
        print(f"Event published: {event_type}, data: {data}")
        return Success(None)

    async def subscribe_to_events_async(self, event_type: str, handler: Any) -> Result[None, AppError]:
        print(f"Handler subscribed to event: {event_type}")
        return Success(None)

    async def unsubscribe_from_events_async(self, event_type: str, handler: Any) -> Result[None, AppError]:
        print(f"Handler unsubscribed from event: {event_type}")
        return Success(None)


class DummyCacheRepository(ICacheRepository):
    """A dummy in-memory cache repository for testing."""
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    async def get_cached_value_async(self, key: str) -> Result[Optional[Any], AppError]:
        """Retrieve a cached value."""
        value = self._cache.get(key)
        return Success(value)

    async def set_cached_value_async(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> Result[None, AppError]:
        """Store a value in cache."""
        self._cache[key] = value
        return Success(None)

    async def delete_cached_value_async(self, key: str) -> Result[None, AppError]:
        """Delete a cached value."""
        if key in self._cache:
            del self._cache[key]
        return Success(None)

    async def clear_cache_async(self) -> Result[None, AppError]:
        """Clear all cached values."""
        self._cache.clear()
        return Success(None)

@pytest.fixture
def grammar_context():
    """Context to share data between steps, including a temp directory."""
    temp_dir = tempfile.mkdtemp()
    context = {"temp_dir": Path(temp_dir)}
    yield context
    shutil.rmtree(temp_dir)


@pytest.fixture
def event_bus() -> IEventBus:
    """Provides a dummy event bus for testing."""
    return DummyEventBus()


@pytest.fixture
def cache_repository() -> ICacheRepository:
    """Provides a dummy cache repository for testing."""
    return DummyCacheRepository()
