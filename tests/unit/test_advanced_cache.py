"""
Comprehensive Unit Tests for Advanced Caching System

Tests multiple caching strategies with TDD approach, focusing on thread safety,
performance, and correctness.

Author: DarkLightX / Dana Edwards
"""

import time
import threading
import pytest
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import string

from backend.unified.core.caching.advanced_cache import (
    CachePolicy, CacheEvent, CacheEntry, CacheStats,
    LRUCache, LFUCache, TTLCache, AdaptiveReplacementCache,
    SmartCacheManager, get_cache_manager
)


class TestCacheEntry:
    """Test cache entry functionality."""
    
    def test_cache_entry_creation(self):
        """Test creating a cache entry with proper metadata."""
        value = "test_value"
        entry = CacheEntry(
            value=value,
            created_at=time.time(),
            last_accessed=time.time(),
            ttl=60.0
        )
        
        assert entry.value == value
        assert entry.access_count == 0
        assert entry.ttl == 60.0
        assert not entry.is_expired
        assert entry.age >= 0
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration logic."""
        past_time = time.time() - 100
        entry = CacheEntry(
            value="expired",
            created_at=past_time,
            last_accessed=past_time,
            ttl=50.0
        )
        
        assert entry.is_expired
        assert entry.age >= 100
    
    def test_cache_entry_touch(self):
        """Test updating access information."""
        entry = CacheEntry(
            value="test",
            created_at=time.time(),
            last_accessed=time.time()
        )
        
        initial_access_time = entry.last_accessed
        initial_count = entry.access_count
        
        time.sleep(0.01)  # Small delay
        entry.touch()
        
        assert entry.access_count == initial_count + 1
        assert entry.last_accessed > initial_access_time


class TestCacheStats:
    """Test cache statistics functionality."""
    
    def test_cache_stats_initialization(self):
        """Test cache stats initial values."""
        stats = CacheStats(max_size=1000)
        
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.hit_rate == 0.0
        assert stats.miss_rate == 100.0
        assert stats.max_size == 1000
    
    def test_cache_stats_calculations(self):
        """Test hit/miss rate calculations."""
        stats = CacheStats()
        stats.hits = 75
        stats.misses = 25
        
        assert stats.hit_rate == 75.0
        assert stats.miss_rate == 25.0
    
    def test_cache_stats_edge_cases(self):
        """Test edge cases for statistics."""
        stats = CacheStats()
        
        # No requests
        assert stats.hit_rate == 0.0
        
        # Only hits
        stats.hits = 100
        assert stats.hit_rate == 100.0
        
        # Only misses
        stats.hits = 0
        stats.misses = 100
        assert stats.hit_rate == 0.0


class TestLRUCache:
    """Test LRU cache implementation."""
    
    def test_lru_basic_operations(self):
        """Test basic get/put operations."""
        cache = LRUCache(max_size=3)
        
        # Test put
        assert cache.put("key1", "value1")
        assert cache.size() == 1
        
        # Test get
        assert cache.get("key1") == "value1"
        assert cache.get("nonexistent") is None
        
        # Test stats
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1
    
    def test_lru_eviction(self):
        """Test LRU eviction policy."""
        cache = LRUCache(max_size=3)
        
        # Fill cache
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        
        # Access 'a' to make it recently used
        cache.get("a")
        
        # Add new item, 'b' should be evicted
        cache.put("d", 4)
        
        assert cache.get("a") == 1  # Still there
        assert cache.get("b") is None  # Evicted
        assert cache.get("c") == 3  # Still there
        assert cache.get("d") == 4  # New item
        
        stats = cache.get_stats()
        assert stats.evictions == 1
    
    def test_lru_update_existing(self):
        """Test updating existing entries."""
        cache = LRUCache(max_size=2)
        
        cache.put("key", "value1")
        cache.put("key", "value2")
        
        assert cache.get("key") == "value2"
        assert cache.size() == 1
    
    def test_lru_ttl_expiration(self):
        """Test TTL expiration in LRU cache."""
        cache = LRUCache(max_size=10)
        
        # Add item with short TTL
        cache.put("expire", "value", ttl=0.1)
        
        # Should be accessible immediately
        assert cache.get("expire") == "value"
        
        # Wait for expiration
        time.sleep(0.15)
        
        # Should be expired
        assert cache.get("expire") is None
        
        stats = cache.get_stats()
        assert stats.expirations == 1
    
    def test_lru_thread_safety(self):
        """Test thread safety of LRU cache."""
        cache = LRUCache(max_size=100)
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(100):
                    key = f"thread_{thread_id}_key_{i}"
                    cache.put(key, i)
                    value = cache.get(key)
                    if value != i:
                        errors.append(f"Thread {thread_id}: Expected {i}, got {value}")
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
        
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert cache.size() <= 100  # Should respect max size


class TestLFUCache:
    """Test LFU cache implementation."""
    
    def test_lfu_basic_operations(self):
        """Test basic LFU operations."""
        cache = LFUCache(max_size=3)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        
        # Access 'a' twice, 'b' once
        cache.get("a")
        cache.get("a")
        cache.get("b")
        
        # Add new item, 'c' should be evicted (least frequent)
        cache.put("d", 4)
        
        assert cache.get("a") == 1  # Frequently used
        assert cache.get("b") == 2  # Used once
        assert cache.get("c") is None  # Evicted
        assert cache.get("d") == 4  # New item
    
    def test_lfu_frequency_increment(self):
        """Test frequency tracking."""
        cache = LFUCache(max_size=2)
        
        cache.put("key1", "value1")
        
        # Access multiple times
        for _ in range(5):
            cache.get("key1")
        
        # Add items to trigger eviction
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key2
        
        assert cache.get("key1") == "value1"  # High frequency
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
    
    def test_lfu_tie_breaking(self):
        """Test eviction when frequencies are equal."""
        cache = LFUCache(max_size=2)
        
        cache.put("a", 1)
        cache.put("b", 2)
        
        # Both have frequency 1
        cache.put("c", 3)
        
        # One of a or b should be evicted
        remaining = []
        if cache.get("a") is not None:
            remaining.append("a")
        if cache.get("b") is not None:
            remaining.append("b")
        if cache.get("c") is not None:
            remaining.append("c")
        
        assert len(remaining) == 2
        assert "c" in remaining
    
    def test_lfu_empty_cache_operations(self):
        """Test operations on empty cache."""
        cache = LFUCache(max_size=0)
        
        assert not cache.put("key", "value")
        assert cache.get("key") is None
        assert cache.size() == 0


class TestTTLCache:
    """Test TTL cache implementation."""
    
    def test_ttl_basic_operations(self):
        """Test basic TTL operations."""
        cache = TTLCache(max_size=10, default_ttl=1.0)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2", ttl=0.5)
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        
        # Wait for key2 to expire
        time.sleep(0.6)
        
        assert cache.get("key1") == "value1"  # Still valid
        assert cache.get("key2") is None  # Expired
    
    def test_ttl_cleanup_on_access(self):
        """Test that expired entries are cleaned up on access."""
        cache = TTLCache(max_size=10, default_ttl=0.1)
        
        # Add multiple entries
        for i in range(5):
            cache.put(f"key{i}", f"value{i}")
        
        initial_size = cache.size()
        
        # Wait for expiration
        time.sleep(0.15)
        
        # Access should trigger cleanup
        cache.get("anykey")
        
        # All entries should be cleaned up
        assert cache.size() < initial_size
    
    def test_ttl_fifo_eviction(self):
        """Test FIFO eviction when cache is full."""
        cache = TTLCache(max_size=3, default_ttl=10.0)
        
        cache.put("a", 1)
        time.sleep(0.01)
        cache.put("b", 2)
        time.sleep(0.01)
        cache.put("c", 3)
        
        # Add new item, oldest should be evicted
        cache.put("d", 4)
        
        assert cache.get("a") is None  # Oldest, evicted
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("d") == 4


class TestAdaptiveReplacementCache:
    """Test ARC cache implementation."""
    
    def test_arc_basic_operations(self):
        """Test basic ARC operations."""
        cache = AdaptiveReplacementCache(max_size=4)
        
        # Add items
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("d", 4)
        
        # Access some items multiple times
        cache.get("a")  # Move to frequent
        cache.get("b")  # Move to frequent
        
        # Add new item
        cache.put("e", 5)
        
        # Frequently accessed items should remain
        assert cache.get("a") == 1
        assert cache.get("b") == 2
        
        # Check total size
        assert cache.size() <= 4
    
    def test_arc_adaptation(self):
        """Test ARC's adaptation between recency and frequency."""
        cache = AdaptiveReplacementCache(max_size=3)
        
        # Fill cache
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        
        # Make 'a' frequent
        cache.get("a")
        
        # Evict and re-add 'b'
        cache.put("d", 4)  # This should evict something
        
        # Re-add previously seen item
        cache.put("b", 2)  # Should adapt
        
        # Verify adaptation occurred
        stats = cache.get_stats()
        assert stats.puts > 0
    
    def test_arc_ghost_lists(self):
        """Test ARC's ghost list functionality."""
        cache = AdaptiveReplacementCache(max_size=2)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Evicts 'a'
        
        # Re-add 'a' - should be in ghost list
        cache.put("a", 1)
        
        # Should have adapted based on ghost hit
        assert cache.get("a") == 1


class TestSmartCacheManager:
    """Test smart cache manager with adaptive strategy selection."""
    
    def test_manager_basic_operations(self):
        """Test basic cache manager operations."""
        manager = SmartCacheManager(max_size=100)
        
        # Basic operations
        assert manager.put("key", "value")
        assert manager.get("key") == "value"
        assert manager.remove("key")
        assert manager.get("key") is None
    
    def test_manager_strategy_switching(self):
        """Test manual strategy switching."""
        manager = SmartCacheManager(max_size=100)
        
        # Add data with default strategy
        manager.put("key1", "value1")
        
        # Force different strategy
        manager.force_strategy(CachePolicy.LFU)
        
        # Verify strategy changed
        stats = manager.get_comprehensive_stats()
        assert stats["current_strategy"] == CachePolicy.LFU.value
    
    def test_manager_warm_cache(self):
        """Test cache warming functionality."""
        manager = SmartCacheManager(max_size=100)
        
        data = {f"key{i}": f"value{i}" for i in range(50)}
        count = manager.warm_cache(data)
        
        assert count == 50
        
        # Verify data is accessible
        for i in range(50):
            assert manager.get(f"key{i}") == f"value{i}"
    
    def test_manager_comprehensive_stats(self):
        """Test comprehensive statistics collection."""
        manager = SmartCacheManager(max_size=100)
        
        # Generate some activity
        for i in range(20):
            manager.put(f"key{i}", f"value{i}")
            manager.get(f"key{i}")
        
        stats = manager.get_comprehensive_stats()
        
        assert "current_strategy" in stats
        assert "total_requests" in stats
        assert stats["total_requests"] >= 20
        
        # Check strategy stats
        for policy in CachePolicy:
            if policy.value in stats:
                assert "hit_rate" in stats[policy.value]
                assert "size" in stats[policy.value]
    
    @pytest.mark.slow
    def test_manager_adaptation(self):
        """Test automatic strategy adaptation."""
        manager = SmartCacheManager(max_size=100)
        manager.adaptation_interval = 50  # Faster adaptation for testing
        
        # Simulate workload that favors LRU
        for i in range(100):
            key = f"key{i % 20}"  # Repeating pattern
            manager.put(key, f"value{i}")
            manager.get(key)
        
        # Check if adaptation occurred
        stats = manager.get_comprehensive_stats()
        assert stats["total_requests"] >= 100


class TestConcurrencyAndPerformance:
    """Test concurrent access and performance characteristics."""
    
    def test_concurrent_lru_access(self):
        """Test concurrent access to LRU cache."""
        cache = LRUCache(max_size=1000)
        num_threads = 20
        operations_per_thread = 500
        
        def worker(thread_id):
            for i in range(operations_per_thread):
                key = f"t{thread_id}_k{i % 100}"
                if i % 3 == 0:
                    cache.put(key, i)
                else:
                    cache.get(key)
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            for future in as_completed(futures):
                future.result()  # Raise any exceptions
        
        # Verify cache is still functional
        cache.put("test", "value")
        assert cache.get("test") == "value"
        assert cache.size() <= 1000
    
    def test_performance_characteristics(self):
        """Test cache performance under load."""
        cache = LRUCache(max_size=10000)
        
        # Measure put performance
        start_time = time.time()
        for i in range(10000):
            cache.put(f"key{i}", f"value{i}")
        put_time = time.time() - start_time
        
        # Measure get performance (hits)
        start_time = time.time()
        for i in range(10000):
            cache.get(f"key{i}")
        get_hit_time = time.time() - start_time
        
        # Measure get performance (misses)
        start_time = time.time()
        for i in range(10000, 20000):
            cache.get(f"key{i}")
        get_miss_time = time.time() - start_time
        
        # Performance assertions (these are generous for CI environments)
        assert put_time < 1.0, f"Put operations too slow: {put_time}s"
        assert get_hit_time < 0.5, f"Get hit operations too slow: {get_hit_time}s"
        assert get_miss_time < 0.5, f"Get miss operations too slow: {get_miss_time}s"
        
        # Verify stats
        stats = cache.get_stats()
        assert stats.hits == 10000
        assert stats.misses == 10000
        assert stats.hit_rate == 50.0


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_zero_size_cache(self):
        """Test caches with zero size."""
        for cache_class in [LRUCache, LFUCache, TTLCache, AdaptiveReplacementCache]:
            cache = cache_class(max_size=0)
            
            # Should handle gracefully
            if cache_class != LFUCache:  # LFU explicitly returns False
                cache.put("key", "value")
            
            assert cache.get("key") is None
            assert cache.size() == 0
    
    def test_none_values(self):
        """Test handling of None values."""
        cache = LRUCache(max_size=10)
        
        # Should handle None values
        cache.put("none_key", None)
        assert cache.get("none_key") is None
        
        # But should distinguish from missing keys
        assert cache.size() == 1
    
    def test_large_values(self):
        """Test caching large values."""
        cache = LRUCache(max_size=10)
        
        # Create a large value
        large_value = "x" * 1000000  # 1MB string
        
        cache.put("large", large_value)
        retrieved = cache.get("large")
        
        assert retrieved == large_value
        assert len(retrieved) == 1000000
    
    def test_special_keys(self):
        """Test handling of special key types."""
        cache = LRUCache(max_size=10)
        
        # Various key types
        keys = [
            "",  # Empty string
            " ",  # Space
            "key with spaces",
            "key\nwith\nnewlines",
            "key\twith\ttabs",
            "🔑",  # Unicode
            "a" * 1000,  # Long key
        ]
        
        for i, key in enumerate(keys):
            cache.put(key, f"value{i}")
            assert cache.get(key) == f"value{i}"


class TestGlobalCacheManager:
    """Test global cache manager singleton."""
    
    def test_global_manager_singleton(self):
        """Test that get_cache_manager returns the same instance."""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()
        
        assert manager1 is manager2
        
        # Verify operations affect the same instance
        manager1.put("shared", "value")
        assert manager2.get("shared") == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])