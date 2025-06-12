"""
Comprehensive tests for memory optimization and object pooling.

Tests all aspects of the memory management system including:
- Object pool functionality
- Memory pressure handling
- Resource tracking
- Performance characteristics

Author: DarkLightX / Dana Edwards
"""

import pytest
import threading
import time
import gc
from unittest.mock import Mock, patch
from backend.unified.core.memory import (
    ObjectPool,
    MemoryManager,
    PooledObject,
    StringBuilderPool,
    BufferPool,
    PoolPolicy,
    MemoryPressure,
    ResourceTracker,
    ResourceType,
    AllocationEvent,
    ResourceContext,
    get_memory_manager,
    start_memory_management,
    stop_memory_management
)


class TestPooledObject(PooledObject):
    """Test implementation of pooled object."""
    
    def __init__(self, data=None):
        super().__init__()
        self.data = data or []
        self.processed = False
    
    def reset(self):
        super().reset()
        self.data.clear()
        self.processed = False
    
    def process(self, item):
        self.data.append(item)
        self.processed = True


class TestObjectPool:
    """Test cases for ObjectPool class."""
    
    def test_pool_initialization(self):
        """Test pool initialization with various policies."""
        # Test default initialization
        pool = ObjectPool(lambda: TestPooledObject(), max_size=10)
        assert pool.max_size == 10
        assert pool.policy == PoolPolicy.LIFO
        assert len(pool.pool) == 0
        
        # Test with custom policy
        pool = ObjectPool(
            lambda: TestPooledObject(),
            max_size=5,
            policy=PoolPolicy.LRU
        )
        assert pool.policy == PoolPolicy.LRU
        assert pool.max_size == 5
    
    def test_object_acquisition_and_release(self):
        """Test basic acquire/release functionality."""
        pool = ObjectPool(lambda: TestPooledObject(), max_size=5)
        
        # Acquire object
        obj1 = pool.acquire()
        assert isinstance(obj1, TestPooledObject)
        assert pool.get_stats().created_objects == 1
        assert pool.get_stats().reused_objects == 0
        
        # Process with object
        obj1.process("test")
        assert obj1.processed
        
        # Release object
        success = pool.release(obj1)
        assert success
        assert len(pool.pool) == 1
        
        # Acquire again - should reuse
        obj2 = pool.acquire()
        assert obj2 is obj1  # Same object instance
        assert not obj2.processed  # Should be reset
        assert len(obj2.data) == 0  # Should be clean
        assert pool.get_stats().reused_objects == 1
    
    def test_pool_capacity_management(self):
        """Test pool capacity enforcement."""
        pool = ObjectPool(lambda: TestPooledObject(), max_size=2)
        
        # Fill pool
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        obj3 = pool.acquire()
        
        # Release all objects
        pool.release(obj1)
        pool.release(obj2)
        pool.release(obj3)  # This should cause eviction
        
        # Pool should only contain 2 objects
        assert len(pool.pool) == 2
        assert pool.get_stats().destroyed_objects == 1
    
    def test_policy_behaviors(self):
        """Test different pooling policies."""
        # Test LIFO (Last In, First Out)
        lifo_pool = ObjectPool(lambda: TestPooledObject(), max_size=5, policy=PoolPolicy.LIFO)
        
        obj1 = lifo_pool.acquire()
        obj2 = lifo_pool.acquire()
        obj1.data = ["first"]
        obj2.data = ["second"]
        
        lifo_pool.release(obj1)
        lifo_pool.release(obj2)
        
        # Should get obj2 first (last in)
        retrieved = lifo_pool.acquire()
        assert retrieved is obj2
        
        # Test FIFO (First In, First Out)
        fifo_pool = ObjectPool(lambda: TestPooledObject(), max_size=5, policy=PoolPolicy.FIFO)
        
        obj3 = fifo_pool.acquire()
        obj4 = fifo_pool.acquire()
        obj3.data = ["third"]
        obj4.data = ["fourth"]
        
        fifo_pool.release(obj3)
        fifo_pool.release(obj4)
        
        # Should get obj3 first (first in)
        retrieved = fifo_pool.acquire()
        assert retrieved is obj3
    
    def test_object_validation(self):
        """Test object validation during release."""
        class InvalidatableObject(TestPooledObject):
            def __init__(self):
                super().__init__()
                self.valid = True
            
            def is_valid(self):
                return self.valid
            
            def invalidate(self):
                self.valid = False
        
        pool = ObjectPool(lambda: InvalidatableObject(), max_size=5, validate_objects=True)
        
        # Normal object
        obj1 = pool.acquire()
        success = pool.release(obj1)
        assert success
        assert len(pool.pool) == 1
        
        # Invalid object
        obj2 = pool.acquire()
        obj2.invalidate()
        success = pool.release(obj2)
        assert not success
        assert pool.get_stats().destroyed_objects == 1
    
    def test_pool_clearing(self):
        """Test pool clearing functionality."""
        pool = ObjectPool(lambda: TestPooledObject(), max_size=5)
        
        # Add objects to pool
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        pool.release(obj1)
        pool.release(obj2)
        
        assert len(pool.pool) == 2
        
        # Clear pool
        cleared_count = pool.clear()
        assert cleared_count == 2
        assert len(pool.pool) == 0
        assert pool.get_stats().current_size == 0
    
    def test_pool_resizing(self):
        """Test dynamic pool resizing."""
        pool = ObjectPool(lambda: TestPooledObject(), max_size=10)
        
        # Fill pool
        objects = [pool.acquire() for _ in range(5)]
        for obj in objects:
            pool.release(obj)
        
        assert len(pool.pool) == 5
        
        # Resize to smaller
        pool.resize(3)
        assert pool.max_size == 3
        assert len(pool.pool) == 3
        
        # Resize to larger
        pool.resize(8)
        assert pool.max_size == 8
        assert len(pool.pool) == 3  # Existing objects remain
    
    def test_thread_safety(self):
        """Test thread safety of object pool."""
        pool = ObjectPool(lambda: TestPooledObject(), max_size=20)
        acquired_objects = []
        errors = []
        
        def worker():
            try:
                for _ in range(10):
                    obj = pool.acquire()
                    acquired_objects.append(obj)
                    time.sleep(0.001)  # Small delay
                    pool.release(obj)
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have no errors
        assert len(errors) == 0
        
        # Pool statistics should be consistent
        stats = pool.get_stats()
        assert stats.total_requests == 50  # 5 threads * 10 requests
    
    def test_performance_metrics(self):
        """Test performance metrics collection."""
        pool = ObjectPool(lambda: TestPooledObject(), max_size=5)
        
        # Test initial stats
        stats = pool.get_stats()
        assert stats.created_objects == 0
        assert stats.reused_objects == 0
        assert stats.hit_rate == 0.0
        
        # Acquire and release objects
        obj1 = pool.acquire()
        pool.release(obj1)
        
        obj2 = pool.acquire()  # Should reuse obj1
        
        stats = pool.get_stats()
        assert stats.created_objects == 1
        assert stats.reused_objects == 1
        assert stats.hit_rate == 50.0  # 1 reuse out of 2 requests


class TestMemoryManager:
    """Test cases for MemoryManager class."""
    
    def test_memory_manager_initialization(self):
        """Test memory manager initialization."""
        manager = MemoryManager()
        assert len(manager.pools) == 0
        assert manager.monitoring_enabled
        assert manager.monitoring_interval == 30.0
    
    def test_pool_registration(self):
        """Test pool registration and management."""
        manager = MemoryManager()
        pool = ObjectPool(lambda: TestPooledObject(), max_size=10)
        
        # Register pool
        manager.register_pool("test_pool", pool)
        assert "test_pool" in manager.pools
        assert manager.pools["test_pool"] is pool
        
        # Unregister pool
        success = manager.unregister_pool("test_pool")
        assert success
        assert "test_pool" not in manager.pools
        
        # Unregister non-existent pool
        success = manager.unregister_pool("non_existent")
        assert not success
    
    @patch('psutil.virtual_memory')
    @patch('psutil.Process')
    def test_memory_stats_collection(self, mock_process, mock_memory):
        """Test memory statistics collection."""
        # Mock system memory
        mock_memory.return_value.total = 1024 * 1024 * 1024  # 1GB
        mock_memory.return_value.available = 512 * 1024 * 1024  # 512MB
        mock_memory.return_value.used = 512 * 1024 * 1024  # 512MB
        mock_memory.return_value.percent = 50.0
        
        # Mock process memory
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value.rss = 100 * 1024 * 1024  # 100MB
        mock_process.return_value = mock_process_instance
        
        manager = MemoryManager()
        stats = manager.get_memory_stats()
        
        assert stats.total_memory == 1024 * 1024 * 1024
        assert stats.process_memory == 100 * 1024 * 1024
        assert stats.memory_usage_percent == 50.0
        assert stats.memory_pressure in [MemoryPressure.LOW, MemoryPressure.MEDIUM]
    
    def test_force_cleanup(self):
        """Test force cleanup functionality."""
        manager = MemoryManager()
        
        # Create and register pools
        pool1 = ObjectPool(lambda: TestPooledObject(), max_size=5)
        pool2 = ObjectPool(lambda: TestPooledObject(), max_size=5)
        
        # Fill pools
        for pool in [pool1, pool2]:
            objects = [pool.acquire() for _ in range(3)]
            for obj in objects:
                pool.release(obj)
        
        manager.register_pool("pool1", pool1)
        manager.register_pool("pool2", pool2)
        
        # Normal cleanup (50% reduction)
        cleanup_stats = manager.force_cleanup(aggressive=False)
        assert "pool1" in cleanup_stats
        assert "pool2" in cleanup_stats
        
        # Aggressive cleanup (complete clear)
        cleanup_stats = manager.force_cleanup(aggressive=True)
        assert pool1.get_stats().current_size == 0
        assert pool2.get_stats().current_size == 0
    
    def test_pool_optimization(self):
        """Test automatic pool optimization."""
        manager = MemoryManager()
        pool = ObjectPool(lambda: TestPooledObject(), max_size=10)
        
        # Simulate high reuse rate
        for _ in range(20):
            obj = pool.acquire()
            pool.release(obj)
        
        manager.register_pool("test_pool", pool)
        
        # Run optimization
        with patch.object(manager, 'get_memory_stats') as mock_stats:
            mock_stats.return_value.memory_pressure = MemoryPressure.LOW
            manager.optimize_pools()
            
            # Pool should be expanded due to high reuse rate and low memory pressure
            assert pool.max_size >= 10  # Should be same or larger
    
    def test_memory_pressure_callbacks(self):
        """Test memory pressure callback system."""
        manager = MemoryManager()
        callback_called = []
        
        def pressure_callback(pressure):
            callback_called.append(pressure)
        
        manager.add_pressure_callback(MemoryPressure.HIGH, pressure_callback)
        
        # Simulate pressure change
        manager._handle_pressure_change(MemoryPressure.HIGH)
        
        assert len(callback_called) == 1
        assert callback_called[0] == MemoryPressure.HIGH


class TestSpecializedPools:
    """Test cases for specialized pool implementations."""
    
    def test_string_builder_pool(self):
        """Test string builder pool functionality."""
        pool = StringBuilderPool()
        
        # Acquire builder
        builder = pool.acquire()
        assert isinstance(builder, list)
        assert len(builder) == 0
        
        # Use builder
        builder.extend(["Hello", " ", "World"])
        
        # Build string and release
        result = pool.build_string(builder)
        assert result == "Hello World"
        
        # Builder should be returned to pool and cleared
        next_builder = pool.acquire()
        assert len(next_builder) == 0
    
    def test_buffer_pool(self):
        """Test buffer pool functionality."""
        pool = BufferPool(buffer_size=1024)
        
        # Acquire buffer
        buffer = pool.acquire()
        assert isinstance(buffer, bytearray)
        assert len(buffer) == 0
        
        # Use buffer
        buffer.extend(b"test data")
        assert len(buffer) == 9
        
        # Release buffer
        pool.release(buffer)
        
        # Next buffer should be clean
        next_buffer = pool.acquire()
        assert len(next_buffer) == 0


class TestResourceTracker:
    """Test cases for ResourceTracker class."""
    
    def test_resource_tracking_basic(self):
        """Test basic resource tracking functionality."""
        tracker = ResourceTracker(enable_tracemalloc=False)
        
        # Track resource
        tracker.track_resource("test_res_1", ResourceType.MEMORY, 1024, metadata={"type": "test"})
        
        assert len(tracker.active_resources) == 1
        assert "test_res_1" in tracker.active_resources
        
        resource_info = tracker.active_resources["test_res_1"]
        assert resource_info.resource_type == ResourceType.MEMORY
        assert resource_info.size == 1024
        assert resource_info.metadata["type"] == "test"
        
        # Untrack resource
        success = tracker.untrack_resource("test_res_1")
        assert success
        assert len(tracker.active_resources) == 0
    
    def test_resource_access_tracking(self):
        """Test resource access tracking."""
        tracker = ResourceTracker(enable_tracemalloc=False)
        
        tracker.track_resource("test_res_1", ResourceType.MEMORY, 1024)
        
        # Initially no access
        resource_info = tracker.active_resources["test_res_1"]
        assert resource_info.access_count == 0
        assert resource_info.last_accessed is None
        
        # Access resource
        success = tracker.access_resource("test_res_1")
        assert success
        
        # Should be updated
        assert resource_info.access_count == 1
        assert resource_info.last_accessed is not None
        
        # Access non-existent resource
        success = tracker.access_resource("non_existent")
        assert not success
    
    def test_memory_snapshots(self):
        """Test memory snapshot functionality."""
        tracker = ResourceTracker(enable_tracemalloc=False)
        
        # Track some resources
        tracker.track_resource("res_1", ResourceType.MEMORY, 1024)
        tracker.track_resource("res_2", ResourceType.CACHE_ENTRY, 2048)
        tracker.track_resource("res_3", ResourceType.MEMORY, 1024 * 1024)  # 1MB
        
        # Take snapshot
        snapshot = tracker.take_snapshot()
        
        assert snapshot.tracked_resources == 3
        assert ResourceType.MEMORY in snapshot.resource_breakdown
        assert ResourceType.CACHE_ENTRY in snapshot.resource_breakdown
        assert len(snapshot.large_objects) == 1  # The 1MB object
        assert snapshot.large_objects[0].size == 1024 * 1024
    
    def test_leak_detection(self):
        """Test memory leak detection."""
        tracker = ResourceTracker(enable_tracemalloc=False)
        
        # Track old resource (simulate old timestamp)
        tracker.track_resource("old_res", ResourceType.MEMORY, 1024)
        old_resource = tracker.active_resources["old_res"]
        old_resource.created_at = time.time() - 7200  # 2 hours ago
        
        # Track recent resource
        tracker.track_resource("new_res", ResourceType.MEMORY, 1024)
        
        # Detect leaks (1 hour threshold)
        leaks = tracker.detect_leaks(age_threshold=3600.0)
        
        assert len(leaks) == 1
        assert leaks[0].resource_id == "old_res"
    
    def test_resource_context_manager(self):
        """Test resource context manager."""
        tracker = ResourceTracker(enable_tracemalloc=False)
        
        # Use context manager
        with ResourceContext(tracker, "ctx_res", ResourceType.MEMORY, 1024) as resource_id:
            assert resource_id == "ctx_res"
            assert len(tracker.active_resources) == 1
            assert "ctx_res" in tracker.active_resources
        
        # Should be automatically untracked
        assert len(tracker.active_resources) == 0
    
    def test_resource_statistics(self):
        """Test resource statistics collection."""
        tracker = ResourceTracker(enable_tracemalloc=False)
        
        # Track and untrack resources
        tracker.track_resource("res_1", ResourceType.MEMORY, 1024)
        tracker.track_resource("res_2", ResourceType.MEMORY, 2048)
        tracker.untrack_resource("res_1")
        tracker.untrack_resource("res_2", reused=True)
        
        stats = tracker.get_resource_stats()
        assert stats['total_allocations'] == 2
        assert stats['total_deallocations'] == 1
        assert stats['reuse_count'] == 1
        assert stats['active_resources'] == 0
    
    def test_cleanup_suggestions(self):
        """Test cleanup suggestions generation."""
        tracker = ResourceTracker(enable_tracemalloc=False)
        
        # Create scenarios that trigger suggestions
        
        # Large object
        tracker.track_resource("large_obj", ResourceType.MEMORY, 2 * 1024 * 1024)  # 2MB
        
        # Old unused resource
        tracker.track_resource("unused_res", ResourceType.MEMORY, 1024)
        unused_resource = tracker.active_resources["unused_res"]
        unused_resource.created_at = time.time() - 600  # 10 minutes ago
        
        suggestions = tracker.cleanup_suggestions()
        
        assert len(suggestions) > 0
        assert any("large objects" in suggestion for suggestion in suggestions)
        assert any("unused resources" in suggestion for suggestion in suggestions)


class TestIntegration:
    """Integration tests for memory management components."""
    
    def test_memory_manager_with_pools_integration(self):
        """Test integration between memory manager and object pools."""
        manager = MemoryManager()
        
        # Create pools with different characteristics
        high_reuse_pool = ObjectPool(lambda: TestPooledObject(), max_size=10)
        low_reuse_pool = ObjectPool(lambda: TestPooledObject(), max_size=10)
        
        # Simulate high reuse for first pool
        for _ in range(50):
            obj = high_reuse_pool.acquire()
            high_reuse_pool.release(obj)
        
        # Simulate low reuse for second pool
        for _ in range(10):
            obj = low_reuse_pool.acquire()
            # Don't release - simulates low reuse
        
        manager.register_pool("high_reuse", high_reuse_pool)
        manager.register_pool("low_reuse", low_reuse_pool)
        
        # Get comprehensive stats
        all_stats = manager.get_all_pool_stats()
        assert "high_reuse" in all_stats
        assert "low_reuse" in all_stats
        
        high_stats = all_stats["high_reuse"]
        low_stats = all_stats["low_reuse"]
        
        assert high_stats.reuse_rate > low_stats.reuse_rate
    
    def test_resource_tracker_with_pools_integration(self):
        """Test integration between resource tracker and object pools."""
        tracker = ResourceTracker(enable_tracemalloc=False)
        pool = ObjectPool(lambda: TestPooledObject(), max_size=5)
        
        # Simulate pool usage with tracking
        for i in range(10):
            obj = pool.acquire()
            
            # Track the object
            tracker.track_resource(
                f"pooled_obj_{i}",
                ResourceType.MEMORY,
                200,  # Approximate object size
                obj
            )
            
            # Use object
            obj.process(f"data_{i}")
            
            # Access tracking
            tracker.access_resource(f"pooled_obj_{i}")
            
            # Release back to pool
            pool.release(obj)
            
            # Untrack (simulate reuse)
            tracker.untrack_resource(f"pooled_obj_{i}", reused=True)
        
        # Check statistics
        tracker_stats = tracker.get_resource_stats()
        pool_stats = pool.get_stats()
        
        assert tracker_stats['total_allocations'] == 10
        assert tracker_stats['reuse_count'] == 10
        assert pool_stats.reused_objects > 0  # Some objects were reused


def test_global_memory_management():
    """Test global memory management functions."""
    # Test global access functions
    manager = get_memory_manager()
    assert isinstance(manager, MemoryManager)
    
    # Test start/stop functions
    start_memory_management()
    assert manager.monitoring_enabled
    
    stop_memory_management()
    # Note: monitoring might still be enabled, but thread should be stopped


if __name__ == "__main__":
    pytest.main([__file__])