"""
Pattern cache for compiled regex patterns.
Provides efficient caching and reuse of compiled regex patterns.

Author: DarkLightX / Dana Edwards
"""

import re
from typing import Dict, Optional, Pattern
import threading
import logging

logger = logging.getLogger(__name__)


class PatternCache:
    """
    Thread-safe cache for compiled regex patterns.
    
    This cache prevents redundant compilation of regex patterns,
    which improves performance especially for frequently used patterns.
    """
    
    def __init__(self, max_size: int = 1024):
        """
        Initialize the pattern cache.
        
        Args:
            max_size: Maximum number of patterns to cache (default: 1024)
        """
        self._cache: Dict[str, Pattern] = {}
        self._lock = threading.RLock()
        self._max_size = max_size
        self._access_count: Dict[str, int] = {}
        self._hit_count = 0
        self._miss_count = 0
    
    def get_pattern(self, pattern_str: str, flags: int = 0) -> Pattern:
        """
        Get a compiled regex pattern from cache or compile and cache it.
        
        Args:
            pattern_str: The regex pattern string
            flags: Optional regex flags (e.g., re.IGNORECASE)
            
        Returns:
            Compiled regex pattern
        """
        # Create cache key that includes flags
        cache_key = f"{pattern_str}:{flags}"
        
        with self._lock:
            # Check if pattern is already cached
            if cache_key in self._cache:
                self._hit_count += 1
                self._access_count[cache_key] = self._access_count.get(cache_key, 0) + 1
                return self._cache[cache_key]
            
            # Pattern not in cache - compile it
            self._miss_count += 1
            try:
                compiled_pattern = re.compile(pattern_str, flags)
            except re.error as e:
                logger.error(f"Failed to compile regex pattern '{pattern_str}': {e}")
                raise
            
            # Add to cache if not at capacity
            if len(self._cache) < self._max_size:
                self._cache[cache_key] = compiled_pattern
                self._access_count[cache_key] = 1
            else:
                # Cache is full - evict least recently used pattern
                self._evict_lru()
                self._cache[cache_key] = compiled_pattern
                self._access_count[cache_key] = 1
            
            return compiled_pattern
    
    def _evict_lru(self):
        """Evict the least recently used pattern from cache."""
        if not self._cache:
            return
        
        # Find pattern with lowest access count
        lru_key = min(self._access_count, key=self._access_count.get)
        del self._cache[lru_key]
        del self._access_count[lru_key]
        logger.debug(f"Evicted pattern from cache: {lru_key}")
    
    def clear(self):
        """Clear all cached patterns."""
        with self._lock:
            self._cache.clear()
            self._access_count.clear()
            self._hit_count = 0
            self._miss_count = 0
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hit_count + self._miss_count
            hit_rate = (self._hit_count / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'cache_size': len(self._cache),
                'max_size': self._max_size,
                'hit_count': self._hit_count,
                'miss_count': self._miss_count,
                'total_requests': total_requests,
                'hit_rate': hit_rate
            }
    
    def precompile_patterns(self, patterns: Dict[str, str], flags: int = 0):
        """
        Precompile a dictionary of patterns for better startup performance.
        
        Args:
            patterns: Dictionary mapping pattern names to pattern strings
            flags: Optional regex flags to apply to all patterns
        """
        for name, pattern_str in patterns.items():
            try:
                self.get_pattern(pattern_str, flags)
                logger.debug(f"Precompiled pattern '{name}'")
            except re.error as e:
                logger.error(f"Failed to precompile pattern '{name}': {e}")


# Global pattern cache instance
_global_pattern_cache = PatternCache()


def get_pattern(pattern_str: str, flags: int = 0) -> Pattern:
    """
    Get a compiled regex pattern using the global cache.
    
    Args:
        pattern_str: The regex pattern string
        flags: Optional regex flags
        
    Returns:
        Compiled regex pattern
    """
    return _global_pattern_cache.get_pattern(pattern_str, flags)


def clear_cache():
    """Clear the global pattern cache."""
    _global_pattern_cache.clear()


def get_cache_stats() -> Dict[str, int]:
    """Get statistics from the global pattern cache."""
    return _global_pattern_cache.get_stats()


def precompile_patterns(patterns: Dict[str, str], flags: int = 0):
    """Precompile patterns using the global cache."""
    _global_pattern_cache.precompile_patterns(patterns, flags)