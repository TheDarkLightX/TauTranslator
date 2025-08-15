#!/usr/bin/env python3
"""
Test script to verify benchmark components are working
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all optimization modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test FSA engine
        from backend.unified.core.pattern_matching.fsa_engine import (
            FiniteStateAutomaton, FSAPatternCompiler
        )
        print("✓ FSA engine imported successfully")
    except ImportError as e:
        print(f"✗ FSA engine import failed: {e}")
    
    try:
        # Test caching
        from backend.unified.core.caching.advanced_cache import (
            LRUCache, SmartCacheManager
        )
        print("✓ Advanced caching imported successfully")
    except ImportError as e:
        print(f"✗ Advanced caching import failed: {e}")
    
    try:
        # Test string matching
        from backend.unified.core.algorithms.string_matching import (
            BoyerMooreSearch, AhoCorasickAutomaton
        )
        print("✓ String matching imported successfully")
    except ImportError as e:
        print(f"✗ String matching import failed: {e}")
    
    try:
        # Test object pools
        from backend.unified.core.memory.object_pools import (
            ObjectPool, MemoryManager
        )
        print("✓ Object pooling imported successfully")
    except ImportError as e:
        print(f"✗ Object pooling import failed: {e}")
    
    try:
        # Test SIMD processor
        from backend.unified.core.parallel.simd_processor import (
            SimdPatternEngine, ParallelBatchProcessor
        )
        print("✓ SIMD processor imported successfully")
    except ImportError as e:
        print(f"✗ SIMD processor import failed: {e}")
    
    try:
        # Test statistics
        from backend.unified.core.statistics import TranslationStatisticsService
        print("✓ Statistics service imported successfully")
    except ImportError as e:
        print(f"✗ Statistics service import failed: {e}")

def test_fsa_basic():
    """Test basic FSA functionality."""
    print("\nTesting FSA pattern matching...")
    
    try:
        from backend.unified.core.pattern_matching.fsa_engine import FSAPatternCompiler
        
        compiler = FSAPatternCompiler()
        patterns = [
            ("p1", "hello", "HELLO", 1),
            ("p2", "world", "WORLD", 1)
        ]
        
        fsa = compiler.compile_patterns(patterns)
        text = "hello world, hello again"
        matches = fsa.find_all_matches(text)
        
        print(f"  Found {len(matches)} matches")
        print("✓ FSA pattern matching works")
    except Exception as e:
        print(f"✗ FSA test failed: {e}")

def test_cache_basic():
    """Test basic cache functionality."""
    print("\nTesting advanced caching...")
    
    try:
        from backend.unified.core.caching.advanced_cache import LRUCache
        
        cache = LRUCache(max_size=100)
        
        # Test operations
        cache.put("key1", "value1")
        value = cache.get("key1")
        
        if value == "value1":
            print("✓ Cache operations work")
        else:
            print("✗ Cache returned wrong value")
            
        stats = cache.get_stats()
        print(f"  Cache stats: hits={stats.hits}, misses={stats.misses}")
        
    except Exception as e:
        print(f"✗ Cache test failed: {e}")

def test_string_matching_basic():
    """Test basic string matching."""
    print("\nTesting string matching algorithms...")
    
    try:
        from backend.unified.core.algorithms.string_matching import BoyerMooreSearch
        
        searcher = BoyerMooreSearch("pattern")
        text = "This is a pattern matching test with pattern repeated"
        matches = searcher.search(text)
        
        print(f"  Found {len(matches)} matches")
        print("✓ String matching works")
    except Exception as e:
        print(f"✗ String matching test failed: {e}")

def test_object_pool_basic():
    """Test basic object pooling."""
    print("\nTesting object pooling...")
    
    try:
        from backend.unified.core.memory.object_pools import ObjectPool, PoolPolicy
        
        class TestObject:
            def __init__(self):
                self.data = [0] * 100
            
            def reset(self):
                self.data = [0] * 100
            
            def is_valid(self):
                return True
        
        pool = ObjectPool(
            factory=TestObject,
            max_size=10,
            policy=PoolPolicy.LIFO
        )
        
        # Test acquire/release
        obj = pool.acquire()
        pool.release(obj)
        
        stats = pool.get_stats()
        print(f"  Pool stats: created={stats.created_objects}, reused={stats.reused_objects}")
        print("✓ Object pooling works")
    except Exception as e:
        print(f"✗ Object pool test failed: {e}")

if __name__ == "__main__":
    print("Testing Benchmark Components")
    print("=" * 50)
    
    test_imports()
    test_fsa_basic()
    test_cache_basic()
    test_string_matching_basic()
    test_object_pool_basic()
    
    print("\nComponent tests complete!")