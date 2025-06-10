# Interfaces: The Castle's Contracts

## Overview: The Sacred Scrolls of Agreement

Interfaces are like contracts between different parts of the castle. When the kitchen promises to provide meals, they sign a contract specifying exactly what they'll deliver - not how they'll cook it. This allows the castle to switch from a French chef to an Italian chef without changing the contract. In code, interfaces define what operations are available without specifying implementation details.

**File**: `backend/unified/core/interfaces.py`  
**Purpose**: Define contracts that implementations must fulfill  
**Architecture**: Abstract base classes enabling dependency injection

---

## The Repository Contracts

### Pattern Repository: The Recipe Archive Contract

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Set
from .domain_types import (
    Pattern, PatternId, PatternSet, PatternSetName,
    PatternType, Result, PatternFilePath
)

class IPatternRepository(ABC):
    """
    Interface for pattern storage and retrieval.
    Implementations might use files, databases, or remote APIs.
    """
    
    @abstractmethod
    async def get_pattern_async(self, pattern_id: PatternId) -> Result[Pattern]:
        """Retrieve a single pattern by ID."""
        pass
    
    @abstractmethod
    async def get_pattern_set_async(self, set_name: PatternSetName) -> Result[PatternSet]:
        """Retrieve a named collection of patterns."""
        pass
    
    @abstractmethod
    async def save_pattern_async(self, pattern: Pattern) -> Result[None]:
        """Save or update a pattern."""
        pass
    
    @abstractmethod
    async def delete_pattern_async(self, pattern_id: PatternId) -> Result[None]:
        """Delete a pattern."""
        pass
    
    @abstractmethod
    async def search_patterns_async(
        self,
        query: str,
        pattern_type: Optional[PatternType] = None,
        tags: Optional[Set[str]] = None
    ) -> Result[List[Pattern]]:
        """Search patterns by text query and filters."""
        pass
    
    @abstractmethod
    async def list_pattern_sources_async(self) -> Result[List[PatternFilePath]]:
        """List all available pattern sources."""
        pass
```

This contract is like an agreement with the recipe archive:
- **get_pattern_async**: "I promise to fetch any recipe by its ID"
- **save_pattern_async**: "I promise to store new recipes safely"
- **search_patterns_async**: "I promise to help you find recipes"

The beauty is that the archive could be:
- A filing cabinet (file system)
- A computer database (SQL)
- A remote library (API)

As long as they fulfill the contract, the rest of the castle doesn't care!

### Authentication Repository: The Identity Vault Contract

```python
class IAuthenticationRepository(ABC):
    """
    Interface for authentication data storage.
    Handles API keys, sessions, and user data.
    """
    
    @abstractmethod
    async def save_api_key_async(self, api_key_record: ApiKeyRecord) -> Result[None]:
        """Save an API key record."""
        pass
    
    @abstractmethod
    async def get_api_key_async(self, key_id: KeyId) -> Result[ApiKeyRecord]:
        """Retrieve an API key record by ID."""
        pass
    
    @abstractmethod
    async def get_all_api_keys_async(self) -> Result[List[ApiKeyRecord]]:
        """Retrieve all API key records (for validation)."""
        pass
    
    @abstractmethod
    async def delete_api_key_async(self, key_id: KeyId) -> Result[None]:
        """Delete an API key record."""
        pass
    
    @abstractmethod
    async def save_session_async(self, session_info: SessionInfo) -> Result[None]:
        """Save a session."""
        pass
    
    @abstractmethod
    async def get_session_async(self, session_token: SessionToken) -> Result[SessionInfo]:
        """Retrieve a session by token."""
        pass
    
    @abstractmethod
    async def delete_session_async(self, session_token: SessionToken) -> Result[None]:
        """Delete a session."""
        pass
    
    @abstractmethod
    async def cleanup_expired_sessions_async(self) -> Result[int]:
        """Remove expired sessions, return count deleted."""
        pass
```

The identity vault promises to:
- Keep keys safe (but doesn't say if in a safe or encrypted file)
- Track who's currently in the castle (sessions)
- Clean up old visitor passes (expired sessions)

---

## The Cache Contract

### Cache Repository: The Quick Storage Agreement

```python
class ICacheRepository(ABC):
    """
    Interface for caching operations.
    Could be in-memory, Redis, Memcached, etc.
    """
    
    @abstractmethod
    async def get_async(self, key: CacheKey) -> Optional[Any]:
        """Retrieve value from cache."""
        pass
    
    @abstractmethod
    async def set_async(
        self,
        key: CacheKey,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> Result[None]:
        """Store value in cache with optional TTL."""
        pass
    
    @abstractmethod
    async def delete_async(self, key: CacheKey) -> Result[None]:
        """Remove value from cache."""
        pass
    
    @abstractmethod
    async def clear_async(self) -> Result[None]:
        """Clear all cached values."""
        pass
    
    @abstractmethod
    async def exists_async(self, key: CacheKey) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    async def get_stats_async(self) -> Result[Dict[str, Any]]:
        """Get cache statistics (hits, misses, size, etc)."""
        pass
```

The cache contract is like an agreement with a storage locker service:
- **get_async**: "I'll retrieve your items quickly"
- **set_async**: "I'll store items, optionally disposing after X time"
- **get_stats_async**: "I'll tell you how often items are accessed"

Could be implemented by:
- A closet (in-memory)
- A warehouse (Redis)
- A distributed storage network (Hazelcast)

---

## The Event System Contract

### Event Bus: The Announcement System Agreement

```python
from typing import Callable, Awaitable

EventHandler = Callable[[Event], Awaitable[None]]

class IEventBus(ABC):
    """
    Interface for event publishing and subscription.
    Enables loose coupling between components.
    """
    
    @abstractmethod
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        pass
    
    @abstractmethod
    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler
    ) -> None:
        """Subscribe to specific event type."""
        pass
    
    @abstractmethod
    def unsubscribe(
        self,
        event_type: EventType,
        handler: EventHandler
    ) -> None:
        """Unsubscribe from event type."""
        pass
    
    @abstractmethod
    def subscribe_pattern(
        self,
        pattern: str,
        handler: EventHandler
    ) -> None:
        """Subscribe to events matching pattern (e.g., 'auth.*')."""
        pass
```

The event bus is like the castle's herald service:
- **publish**: "I'll announce this to everyone who cares"
- **subscribe**: "I'll notify you when this specific thing happens"
- **subscribe_pattern**: "I'll notify you about all authentication events"

Implementation could be:
- A town crier (in-process)
- A messaging service (RabbitMQ)
- A distributed event stream (Kafka)

---

## The Monitoring Contract

### Resource Monitor: The Castle Inspector Agreement

```python
@dataclass
class ResourceUsage:
    """Current resource usage snapshot."""
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    active_threads: int
    timestamp: datetime

class IResourceMonitor(ABC):
    """
    Interface for system resource monitoring.
    Helps prevent resource exhaustion.
    """
    
    @abstractmethod
    async def get_current_usage_async(self) -> ResourceUsage:
        """Get current resource usage."""
        pass
    
    @abstractmethod
    async def is_healthy_async(self) -> bool:
        """Check if system resources are within healthy limits."""
        pass
    
    @abstractmethod
    def set_limits(
        self,
        max_cpu_percent: float,
        max_memory_percent: float
    ) -> None:
        """Set resource limit thresholds."""
        pass
    
    @abstractmethod
    async def wait_for_resources_async(
        self,
        timeout_seconds: float = 30.0
    ) -> Result[None]:
        """Wait until resources are available or timeout."""
        pass
```

The inspector promises to:
- Monitor castle resources (food, water, space)
- Alert when running low
- Wait for resources to become available

---

## The Statistics Contract

### Statistics Repository: The Record Keeper Agreement

```python
@dataclass
class TranslationStats:
    """Statistics for translation operations."""
    total_count: int
    success_count: int
    failure_count: int
    average_duration_ms: float
    cache_hit_rate: float
    by_engine: Dict[str, Dict[str, Any]]
    by_direction: Dict[str, Dict[str, Any]]

class IStatisticsRepository(ABC):
    """
    Interface for collecting and retrieving statistics.
    Used for monitoring and optimization.
    """
    
    @abstractmethod
    async def record_translation(
        self,
        engine: str,
        direction: TranslationDirection,
        duration: float,
        success: bool,
        confidence: float,
        timestamp: datetime
    ) -> Result[None]:
        """Record a translation event."""
        pass
    
    @abstractmethod
    async def get_stats_async(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Result[TranslationStats]:
        """Get aggregated statistics."""
        pass
    
    @abstractmethod
    async def get_engine_performance_async(
        self,
        engine_name: str
    ) -> Result[Dict[str, float]]:
        """Get performance metrics for specific engine."""
        pass
    
    @abstractmethod
    async def update_engine_score(
        self,
        engine_name: str,
        score_delta: float
    ) -> Result[None]:
        """Update engine performance score."""
        pass
```

The record keeper maintains the castle's logs:
- How many visitors (translations)?
- Which gates (engines) are most efficient?
- What's the success rate?

---

## Implementation Examples

### A Simple In-Memory Cache Implementation

```python
class InMemoryCacheRepository(ICacheRepository):
    """Simple in-memory implementation of cache repository."""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[CacheKey, CacheEntry] = {}
        self._max_size = max_size
        self._lock = asyncio.Lock()
    
    async def get_async(self, key: CacheKey) -> Optional[Any]:
        async with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired:
                entry.record_hit()
                return entry.value
            elif entry and entry.is_expired:
                del self._cache[key]
            return None
    
    async def set_async(
        self,
        key: CacheKey,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> Result[None]:
        async with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self._max_size:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k].created_at
                )
                del self._cache[oldest_key]
            
            # Store new entry
            expires_at = None
            if ttl_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            
            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            return Success(None)
```

This implementation fulfills the cache contract using a simple dictionary. Another implementation could use Redis - the rest of the code doesn't need to know!

---

## The Power of Interfaces

### Testability Through Mocking

```python
class MockPatternRepository(IPatternRepository):
    """Mock implementation for testing."""
    
    def __init__(self):
        self.patterns = {}
        self.save_called = False
    
    async def save_pattern_async(self, pattern: Pattern) -> Result[None]:
        self.save_called = True
        self.patterns[pattern.pattern_id] = pattern
        return Success(None)
    
    async def get_pattern_async(self, pattern_id: PatternId) -> Result[Pattern]:
        if pattern_id in self.patterns:
            return Success(self.patterns[pattern_id])
        return Failure("NOT_FOUND", f"Pattern {pattern_id} not found")
```

Tests can use this mock instead of real file/database operations - faster and more reliable!

### Swappable Implementations

```python
# Development: Use in-memory cache
if config.environment == "development":
    cache = InMemoryCacheRepository()
# Production: Use Redis
else:
    cache = RedisCacheRepository(config.redis_url)

# Usage is identical regardless of implementation
result = await cache.get_async(key)
```

---

## Design Principles in Interfaces

### 1. Interface Segregation
Each interface has a focused purpose:
- `IPatternRepository`: Only pattern operations
- `ICacheRepository`: Only caching operations
- No "god interfaces" with dozens of methods

### 2. Dependency Inversion
High-level code depends on interfaces, not concrete implementations:
```python
class PatternLoader:
    def __init__(self, repository: IPatternRepository):
        # Depends on interface, not FilePatternRepository
        self.repository = repository
```

### 3. Open/Closed Principle
Open for extension (new implementations), closed for modification:
- Add `S3PatternRepository` without changing existing code
- Add `MemcachedCacheRepository` without touching cache users

---

## Summary

Interfaces provide:

1. **Decoupling**: Components depend on contracts, not implementations
2. **Flexibility**: Swap implementations without changing code
3. **Testability**: Easy to mock for testing
4. **Documentation**: Clear contracts show what's expected
5. **Type Safety**: IDEs and type checkers enforce contracts

Key benefits:
- **Multiple Implementations**: File, database, API - all behind same interface
- **Evolution**: Add new implementations without breaking existing code
- **Testing**: Mock implementations for fast, reliable tests
- **Clear Boundaries**: Interfaces define system boundaries

The interface system creates a flexible, maintainable architecture where components can evolve independently while maintaining compatibility through well-defined contracts.