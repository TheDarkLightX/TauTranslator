"""
Tests for translation-specific object pools.

Tests all translation pool functionality including:
- Translation request pooling
- Pattern match result pooling
- AST node pooling
- Cache entry pooling
- Integration with memory management

Author: DarkLightX / Dana Edwards
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from backend.unified.core.memory import (
    TranslationRequest,
    PatternMatchResult,
    ASTNode,
    CacheEntry,
    TranslationPools,
    get_translation_pools,
    initialize_translation_pools,
    get_memory_manager,
    get_resource_tracker,
    ResourceType
)


class TestTranslationRequest:
    """Test cases for TranslationRequest pooled object."""
    
    def test_translation_request_initialization(self):
        """Test translation request initialization."""
        request = TranslationRequest()
        assert request.source_text == ""
        assert request.source_language == ""
        assert request.target_language == ""
        assert len(request.options) == 0
        assert request.timestamp == 0.0
        assert request.request_id is None
    
    def test_translation_request_configuration(self):
        """Test configuring translation request."""
        request = TranslationRequest()
        
        request.configure(
            source_text="Hello world",
            source_language="en",
            target_language="es",
            options={"formal": True},
            request_id="req_123"
        )
        
        assert request.source_text == "Hello world"
        assert request.source_language == "en"
        assert request.target_language == "es"
        assert request.options["formal"] is True
        assert request.request_id == "req_123"
        assert request.timestamp > 0
    
    def test_translation_request_reset(self):
        """Test resetting translation request."""
        request = TranslationRequest()
        
        # Configure with data
        request.configure(
            source_text="Test text",
            source_language="en",
            target_language="fr",
            options={"mode": "technical"}
        )
        
        # Reset
        request.reset()
        
        # Should be back to initial state
        assert request.source_text == ""
        assert request.source_language == ""
        assert request.target_language == ""
        assert len(request.options) == 0
        assert request.timestamp == 0.0
    
    def test_translation_request_memory_size(self):
        """Test memory size calculation."""
        request = TranslationRequest()
        
        # Empty request
        base_size = request.get_memory_size()
        assert base_size >= 200
        
        # Configure with data
        request.configure(
            source_text="A" * 100,  # 100 chars
            source_language="english",
            target_language="spanish",
            options={"key": "value"}
        )
        
        # Size should increase
        new_size = request.get_memory_size()
        assert new_size > base_size
    
    def test_translation_request_validity(self):
        """Test validity checking."""
        request = TranslationRequest()
        assert request.is_valid()
        
        # Test age-based validity
        request._created_at = time.time() - 7200  # 2 hours ago
        assert not request.is_valid()  # Too old
        
        # Test reset count validity
        request._created_at = time.time()
        request._reset_count = 101
        assert not request.is_valid()  # Too many resets


class TestPatternMatchResult:
    """Test cases for PatternMatchResult pooled object."""
    
    def test_pattern_match_initialization(self):
        """Test pattern match initialization."""
        match = PatternMatchResult()
        assert match.pattern_name == ""
        assert match.matched_text == ""
        assert match.start_position == 0
        assert match.end_position == 0
        assert match.confidence == 0.0
        assert len(match.metadata) == 0
        assert len(match.sub_matches) == 0
    
    def test_pattern_match_configuration(self):
        """Test configuring pattern match."""
        match = PatternMatchResult()
        
        match.configure(
            pattern_name="email_pattern",
            matched_text="user@example.com",
            start_position=10,
            end_position=26,
            confidence=0.95,
            metadata={"type": "email"}
        )
        
        assert match.pattern_name == "email_pattern"
        assert match.matched_text == "user@example.com"
        assert match.start_position == 10
        assert match.end_position == 26
        assert match.confidence == 0.95
        assert match.metadata["type"] == "email"
    
    def test_pattern_match_reset(self):
        """Test resetting pattern match."""
        match = PatternMatchResult()
        
        # Configure with data
        match.configure(
            pattern_name="test_pattern",
            matched_text="test match",
            start_position=5,
            end_position=15,
            metadata={"key": "value"}
        )
        
        # Add sub-match
        sub_match = PatternMatchResult()
        match.sub_matches.append(sub_match)
        
        # Reset
        match.reset()
        
        # Should be back to initial state
        assert match.pattern_name == ""
        assert match.matched_text == ""
        assert match.start_position == 0
        assert match.end_position == 0
        assert len(match.metadata) == 0
        assert len(match.sub_matches) == 0
    
    def test_pattern_match_with_sub_matches(self):
        """Test pattern match with sub-matches."""
        parent_match = PatternMatchResult()
        parent_match.configure(
            pattern_name="parent_pattern",
            matched_text="full text",
            start_position=0,
            end_position=9
        )
        
        # Add sub-matches
        sub1 = PatternMatchResult()
        sub1.configure(
            pattern_name="sub_pattern_1",
            matched_text="full",
            start_position=0,
            end_position=4
        )
        
        sub2 = PatternMatchResult()
        sub2.configure(
            pattern_name="sub_pattern_2",
            matched_text="text",
            start_position=5,
            end_position=9
        )
        
        parent_match.sub_matches.extend([sub1, sub2])
        
        # Check memory size includes sub-matches
        total_size = parent_match.get_memory_size()
        assert total_size > sub1.get_memory_size() + sub2.get_memory_size()


class TestASTNode:
    """Test cases for ASTNode pooled object."""
    
    def test_ast_node_initialization(self):
        """Test AST node initialization."""
        node = ASTNode()
        assert node.node_type == ""
        assert node.value is None
        assert len(node.children) == 0
        assert len(node.attributes) == 0
        assert node.line_number == 0
        assert node.column_number == 0
    
    def test_ast_node_configuration(self):
        """Test configuring AST node."""
        node = ASTNode()
        
        node.configure(
            node_type="BinaryOp",
            value="+",
            line_number=10,
            column_number=5,
            attributes={"operator": "addition"}
        )
        
        assert node.node_type == "BinaryOp"
        assert node.value == "+"
        assert node.line_number == 10
        assert node.column_number == 5
        assert node.attributes["operator"] == "addition"
    
    def test_ast_node_children_management(self):
        """Test managing child nodes."""
        parent = ASTNode()
        parent.configure(node_type="Program")
        
        # Add single child
        child1 = ASTNode()
        child1.configure(node_type="Statement", value="print")
        parent.add_child(child1)
        
        assert len(parent.children) == 1
        assert parent.children[0].node_type == "Statement"
        
        # Add multiple children
        child2 = ASTNode()
        child2.configure(node_type="Statement", value="return")
        
        child3 = ASTNode()
        child3.configure(node_type="Statement", value="if")
        
        parent.add_children([child2, child3])
        
        assert len(parent.children) == 3
    
    def test_ast_node_reset(self):
        """Test resetting AST node."""
        node = ASTNode()
        
        # Configure with data
        node.configure(
            node_type="Expression",
            value=42,
            line_number=5,
            attributes={"type": "literal"}
        )
        
        # Add children
        child = ASTNode()
        node.add_child(child)
        
        # Reset
        node.reset()
        
        # Should be back to initial state
        assert node.node_type == ""
        assert node.value is None
        assert len(node.children) == 0
        assert len(node.attributes) == 0
    
    def test_ast_node_memory_size_with_tree(self):
        """Test memory size calculation for AST tree."""
        root = ASTNode()
        root.configure(node_type="Root")
        
        # Build a small tree
        for i in range(3):
            child = ASTNode()
            child.configure(node_type=f"Child{i}", value=i)
            
            for j in range(2):
                grandchild = ASTNode()
                grandchild.configure(node_type=f"Grandchild{i}_{j}")
                child.add_child(grandchild)
            
            root.add_child(child)
        
        # Memory size should include all nodes
        total_size = root.get_memory_size()
        assert total_size > 300 * 10  # At least 10 nodes worth


class TestCacheEntry:
    """Test cases for CacheEntry pooled object."""
    
    def test_cache_entry_initialization(self):
        """Test cache entry initialization."""
        entry = CacheEntry()
        assert entry.key == ""
        assert entry.value is None
        assert entry.created_at == 0.0
        assert entry.last_accessed == 0.0
        assert entry.access_count == 0
        assert entry.ttl == 3600.0
        assert len(entry.metadata) == 0
    
    def test_cache_entry_configuration(self):
        """Test configuring cache entry."""
        entry = CacheEntry()
        
        test_value = {"result": "translated text"}
        entry.configure(
            key="translation_en_es_hello",
            value=test_value,
            ttl=1800.0,  # 30 minutes
            metadata={"source": "api"}
        )
        
        assert entry.key == "translation_en_es_hello"
        assert entry.value == test_value
        assert entry.ttl == 1800.0
        assert entry.metadata["source"] == "api"
        assert entry.created_at > 0
        assert entry.last_accessed == entry.created_at
        assert entry.access_count == 0
    
    def test_cache_entry_access(self):
        """Test accessing cached value."""
        entry = CacheEntry()
        entry.configure(key="test_key", value="test_value")
        
        initial_access_time = entry.last_accessed
        time.sleep(0.01)  # Small delay
        
        # Access the value
        value = entry.access()
        assert value == "test_value"
        assert entry.access_count == 1
        assert entry.last_accessed > initial_access_time
        
        # Multiple accesses
        for _ in range(5):
            entry.access()
        
        assert entry.access_count == 6
    
    def test_cache_entry_ttl_validity(self):
        """Test TTL-based validity."""
        entry = CacheEntry()
        
        # Configure with short TTL
        entry.configure(key="test", value="value", ttl=0.1)  # 100ms
        
        # Should be valid initially
        assert entry.is_valid()
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be invalid now
        assert not entry.is_valid()
        
        # Test with zero TTL (never expires)
        entry2 = CacheEntry()
        entry2.configure(key="test2", value="value2", ttl=0)
        time.sleep(0.1)
        assert entry2.is_valid()  # Still valid
    
    def test_cache_entry_reset(self):
        """Test resetting cache entry."""
        entry = CacheEntry()
        
        # Configure with data
        entry.configure(
            key="cache_key",
            value={"data": "cached"},
            ttl=300.0,
            metadata={"type": "result"}
        )
        
        # Access it
        entry.access()
        
        # Reset
        entry.reset()
        
        # Should be back to initial state
        assert entry.key == ""
        assert entry.value is None
        assert entry.created_at == 0.0
        assert entry.access_count == 0
        assert len(entry.metadata) == 0


class TestTranslationPools:
    """Test cases for TranslationPools manager."""
    
    def test_translation_pools_initialization(self):
        """Test translation pools initialization."""
        pools = TranslationPools()
        
        # Check all pools are created
        assert pools.translation_request_pool is not None
        assert pools.pattern_match_pool is not None
        assert pools.ast_node_pool is not None
        assert pools.cache_entry_pool is not None
        
        # Check pool configurations
        assert pools.translation_request_pool.max_size == 100
        assert pools.pattern_match_pool.max_size == 500
        assert pools.ast_node_pool.max_size == 1000
        assert pools.cache_entry_pool.max_size == 200
    
    def test_acquire_release_translation_request(self):
        """Test acquiring and releasing translation requests."""
        pools = get_translation_pools()
        
        # Acquire request
        request = pools.acquire_translation_request(
            source_text="Hello",
            source_language="en",
            target_language="es",
            options={"style": "formal"},
            request_id="test_123"
        )
        
        assert isinstance(request, TranslationRequest)
        assert request.source_text == "Hello"
        assert request.request_id == "test_123"
        
        # Release request
        success = pools.release_translation_request(request)
        assert success
        
        # Acquire again - should reuse
        request2 = pools.acquire_translation_request(
            source_text="World",
            source_language="en",
            target_language="fr"
        )
        
        assert request2 is request  # Same object
        assert request2.source_text == "World"  # New data
    
    def test_acquire_release_pattern_match(self):
        """Test acquiring and releasing pattern matches."""
        pools = get_translation_pools()
        
        # Acquire match
        match = pools.acquire_pattern_match(
            pattern_name="test_pattern",
            matched_text="matched",
            start_position=0,
            end_position=7,
            confidence=0.9,
            metadata={"type": "test"}
        )
        
        assert isinstance(match, PatternMatchResult)
        assert match.pattern_name == "test_pattern"
        assert match.confidence == 0.9
        
        # Release match
        success = pools.release_pattern_match(match)
        assert success
    
    def test_acquire_release_ast_node(self):
        """Test acquiring and releasing AST nodes."""
        pools = get_translation_pools()
        
        # Acquire nodes
        root = pools.acquire_ast_node(
            node_type="Program",
            attributes={"version": "1.0"}
        )
        
        child1 = pools.acquire_ast_node(
            node_type="Statement",
            value="print",
            line_number=1
        )
        
        child2 = pools.acquire_ast_node(
            node_type="Expression",
            value=42,
            line_number=2
        )
        
        # Build tree
        root.add_children([child1, child2])
        
        assert len(root.children) == 2
        
        # Release tree (should release all nodes)
        success = pools.release_ast_node(root)
        assert success
    
    def test_acquire_release_cache_entry(self):
        """Test acquiring and releasing cache entries."""
        pools = get_translation_pools()
        
        # Acquire entry
        entry = pools.acquire_cache_entry(
            key="test_cache_key",
            value={"result": "cached data"},
            ttl=600.0,
            metadata={"source": "test"}
        )
        
        assert isinstance(entry, CacheEntry)
        assert entry.key == "test_cache_key"
        assert entry.ttl == 600.0
        
        # Access value
        value = entry.access()
        assert value["result"] == "cached data"
        assert entry.access_count == 1
        
        # Release entry
        success = pools.release_cache_entry(entry)
        assert success
    
    def test_pool_statistics(self):
        """Test getting pool statistics."""
        pools = initialize_translation_pools()  # Fresh instance
        
        # Use pools
        requests = []
        for i in range(5):
            req = pools.acquire_translation_request(
                source_text=f"Text {i}",
                source_language="en",
                target_language="es"
            )
            requests.append(req)
        
        # Release some
        for req in requests[:3]:
            pools.release_translation_request(req)
        
        # Get statistics
        stats = pools.get_pool_statistics()
        
        assert "translation_requests" in stats
        req_stats = stats["translation_requests"]
        assert req_stats["created_objects"] >= 5
        assert req_stats["reused_objects"] >= 0
    
    def test_pool_cleanup(self):
        """Test pool cleanup functionality."""
        pools = initialize_translation_pools()  # Fresh instance
        
        # Fill pools
        items = []
        for i in range(10):
            req = pools.acquire_translation_request(f"Text {i}", "en", "es")
            pools.release_translation_request(req)
            
            match = pools.acquire_pattern_match(f"pattern_{i}", f"match_{i}", i, i+5)
            pools.release_pattern_match(match)
        
        # Gentle cleanup
        cleanup_stats = pools.cleanup(aggressive=False)
        assert "translation_requests" in cleanup_stats
        assert "pattern_matches" in cleanup_stats
        
        # Aggressive cleanup
        cleanup_stats = pools.cleanup(aggressive=True)
        
        # All pools should be empty
        stats = pools.get_pool_statistics()
        assert stats["translation_requests"]["current_size"] == 0
        assert stats["pattern_matches"]["current_size"] == 0
    
    def test_resource_tracking_integration(self):
        """Test integration with resource tracking."""
        pools = get_translation_pools()
        tracker = get_resource_tracker()
        
        # Clear any existing resources
        tracker.active_resources.clear()
        
        # Acquire resources
        request = pools.acquire_translation_request("Test", "en", "es")
        match = pools.acquire_pattern_match("pattern", "text", 0, 4)
        
        # Should be tracked
        assert len(tracker.active_resources) >= 2
        
        # Release resources
        pools.release_translation_request(request)
        pools.release_pattern_match(match)
        
        # Should be untracked (but marked as reused)
        resource_stats = tracker.get_resource_stats()
        assert resource_stats['reuse_count'] >= 2
    
    def test_thread_safety(self):
        """Test thread safety of translation pools."""
        pools = get_translation_pools()
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(20):
                    # Acquire and use various objects
                    req = pools.acquire_translation_request(
                        f"Worker {worker_id} text {i}",
                        "en", "es"
                    )
                    
                    match = pools.acquire_pattern_match(
                        f"pattern_{worker_id}_{i}",
                        "matched text",
                        0, 10
                    )
                    
                    node = pools.acquire_ast_node(
                        f"Node_{worker_id}_{i}",
                        value=i
                    )
                    
                    # Simulate some work
                    time.sleep(0.001)
                    
                    # Release objects
                    pools.release_translation_request(req)
                    pools.release_pattern_match(match)
                    pools.release_ast_node(node)
                    
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have no errors
        assert len(errors) == 0
        
        # Check pool statistics are consistent
        stats = pools.get_pool_statistics()
        # Check using the correct field names from PoolStats
        req_stats = stats["translation_requests"]
        total_requests = req_stats["created_objects"] + req_stats["reused_objects"]
        assert total_requests >= 100  # 5 threads * 20 requests


def test_global_translation_pools():
    """Test global translation pools access."""
    pools1 = get_translation_pools()
    pools2 = get_translation_pools()
    
    # Should be same instance
    assert pools1 is pools2
    
    # Test initialization function
    new_pools = initialize_translation_pools()
    assert isinstance(new_pools, TranslationPools)
    
    # Should replace global instance
    pools3 = get_translation_pools()
    assert pools3 is new_pools


if __name__ == "__main__":
    pytest.main([__file__])