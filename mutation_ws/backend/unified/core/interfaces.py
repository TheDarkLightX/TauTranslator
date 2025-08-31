"""
Core interfaces for infrastructure abstraction following Rule 4.
These interfaces define contracts that infrastructure must implement.

Copyright: DarkLightX/Dana Edwards
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from datetime import datetime

from .domain_types import (
    UserId, SessionId, ApiKey, PatternId, GrammarId,
    FilePath, DirectoryPath, AppError
)
from .result_enhanced import Result, Success, Failure


class IPatternRepository(ABC):
    """Interface for pattern storage and retrieval."""

    @abstractmethod
    async def load_patterns_from_source_async(self, source_path: FilePath) -> Result[Dict[str, Any], AppError]:
        """Load patterns from a source (file, database, etc)."""
        pass

    @abstractmethod
    async def save_patterns_to_destination_async(self, patterns: Dict[str, Any], destination: FilePath) -> Result[None, AppError]:
        """Save patterns to a destination."""
        pass

    @abstractmethod
    async def watch_for_pattern_changes_async(self, source_path: FilePath) -> Result[None, AppError]:
        """Watch for changes in pattern source."""
        pass

    @abstractmethod
    async def export_patterns_as_json_async(self, patterns: Dict[str, Any]) -> Result[str, AppError]:
        """Export patterns as JSON string."""
        pass


class IAuthenticationRepository(ABC):
    """Interface for authentication data persistence."""

    @abstractmethod
    async def load_sessions_async(self) -> Result[Dict[SessionId, Dict[str, Any]], AppError]:
        """Load all active sessions."""
        pass

    @abstractmethod
    async def save_session_async(self, session_id: SessionId, session_data: Dict[str, Any]) -> Result[None, AppError]:
        """Save a single session."""
        pass

    @abstractmethod
    async def delete_session_async(self, session_id: SessionId) -> Result[None, AppError]:
        """Delete a session."""
        pass

    @abstractmethod
    async def load_api_keys_async(self) -> Result[Dict[str, ApiKey], AppError]:
        """Load stored API keys."""
        pass

    @abstractmethod
    async def save_api_key_async(self, provider: str, key: ApiKey) -> Result[None, AppError]:
        """Save an API key for a provider."""
        pass

    @abstractmethod
    async def delete_api_key_async(self, provider: str) -> Result[None, AppError]:
        """Delete an API key."""
        pass

    @abstractmethod
    async def load_encryption_key_async(self) -> Result[bytes, AppError]:
        """Load the encryption key for API keys."""
        pass

    @abstractmethod
    async def save_encryption_key_async(self, key: bytes) -> Result[None, AppError]:
        """Save the encryption key."""
        pass


class IGrammarRepository(ABC):
    """Interface for grammar file access."""

    @abstractmethod
    async def list_available_grammars_async(self) -> Result[List[GrammarId], AppError]:
        """List all available grammar IDs."""
        pass

    @abstractmethod
    async def load_grammar_content_async(self, grammar_id: GrammarId) -> Result[str, AppError]:
        """Load the content of a grammar file."""
        pass

    @abstractmethod
    async def save_grammar_content_async(self, grammar_id: GrammarId, content: str) -> Result[None, AppError]:
        """Save grammar content."""
        pass

    @abstractmethod
    async def get_grammar_metadata_async(self, grammar_id: GrammarId) -> Result[Dict[str, Any], AppError]:
        """Get metadata about a grammar (size, modified date, etc)."""
        pass


class IResourceMonitor(ABC):
    """Interface for system resource monitoring."""

    @abstractmethod
    async def get_memory_usage_async(self) -> Result[Dict[str, float], AppError]:
        """Get current memory usage statistics."""
        pass

    @abstractmethod
    async def get_cpu_usage_async(self) -> Result[float, AppError]:
        """Get current CPU usage percentage."""
        pass

    @abstractmethod
    async def start_memory_profiling_async(self) -> Result[None, AppError]:
        """Start memory profiling."""
        pass

    @abstractmethod
    async def stop_memory_profiling_async(self) -> Result[Dict[str, Any], AppError]:
        """Stop profiling and return results."""
        pass


class ICacheRepository(ABC):
    """Interface for caching operations."""

    @abstractmethod
    async def get_cached_value_async(self, key: str) -> Result[Optional[Any], AppError]:
        """Retrieve a cached value."""
        pass

    @abstractmethod
    async def set_cached_value_async(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> Result[None, AppError]:
        """Store a value in cache."""
        pass

    @abstractmethod
    async def delete_cached_value_async(self, key: str) -> Result[None, AppError]:
        """Delete a cached value."""
        pass

    @abstractmethod
    async def clear_cache_async(self) -> Result[None, AppError]:
        """Clear all cached values."""
        pass


class IEventBus(ABC):
    """Interface for event-driven communication between layers."""

    @abstractmethod
    async def publish_event_async(self, event_type: str, data: Dict[str, Any]) -> Result[None, AppError]:
        """Publish an event."""
        pass

    @abstractmethod
    async def subscribe_to_events_async(self, event_type: str, handler: Any) -> Result[None, AppError]:
        """Subscribe to events of a specific type."""
        pass

    @abstractmethod
    async def unsubscribe_from_events_async(self, event_type: str, handler: Any) -> Result[None, AppError]:
        """Unsubscribe from events."""
        pass