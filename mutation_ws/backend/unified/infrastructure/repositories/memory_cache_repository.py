"""
In-memory implementation of ICacheRepository.
Provides fast, thread-safe caching without external dependencies.

Copyright: DarkLightX/Dana Edwards
"""

import asyncio
import time
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict
import threading

from ...core.domain_types import Result, Success, Failure
from ...core.interfaces import ICacheRepository


class CacheEntry:
    """Represents a single cache entry with TTL."""
    
    def __init__(self, value: Any, ttl_seconds: Optional[int] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        if self.ttl_seconds is None:
            return False
        return time.time() - self.created_at > self.ttl_seconds


class MemoryCacheRepository(ICacheRepository):
    """
    Thread-safe in-memory cache implementation.
    Uses LRU eviction when max size is reached.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[int] = None):
        """Initialize with max size and default TTL."""
        self.max_size = max_size
        self.default_ttl = ttl_seconds
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    async def get_cached_value_async(self, key: str) -> Result[Optional[Any]]:
        """Retrieve a cached value if it exists and hasn't expired."""
        with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                return Success(None)
            
            entry = self._cache[key]
            
            if entry.is_expired():
                # Remove expired entry
                del self._cache[key]
                self._stats["misses"] += 1
                return Success(None)
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._stats["hits"] += 1
            
            return Success(entry.value)
    
    async def set_cached_value_async(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None
    ) -> Result[None]:
        """Store a value in cache with optional TTL."""
        with self._lock:
            # Use provided TTL or default
            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            
            # Check if we need to evict
            if key not in self._cache and len(self._cache) >= self.max_size:
                # Evict least recently used
                self._evict_lru()
            
            # Store the entry
            self._cache[key] = CacheEntry(value, ttl)
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            
            return Success(None)
    
    async def delete_cached_value_async(self, key: str) -> Result[None]:
        """Delete a cached value."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            return Success(None)
    
    async def clear_cache_async(self) -> Result[None]:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()
            return Success(None)
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._lock:
            return {
                **self._stats,
                "size": len(self._cache),
                "max_size": self.max_size
            }
    
    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if self._cache:
            # Remove first item (least recently used)
            self._cache.popitem(last=False)
            self._stats["evictions"] += 1
    
    async def cleanup_expired_async(self) -> int:
        """Remove all expired entries and return count removed."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)