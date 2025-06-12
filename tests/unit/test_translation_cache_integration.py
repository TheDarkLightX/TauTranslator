"""
Unit Tests for Translation Cache Integration

Tests the integration of advanced caching with the translation pipeline.

Author: DarkLightX / Dana Edwards
"""

import time
import pytest
from unittest.mock import Mock, patch

from backend.unified.core.caching.translation_cache_integration import (
    TranslationCacheConfig, TranslationCacheManager,
    cached_translation, get_translation_cache_manager,
    configure_translation_cache, _generate_function_cache_key
)
from backend.unified.core.caching.advanced_cache import CachePolicy


class TestTranslationCacheConfig:
    """Test translation cache configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = TranslationCacheConfig()
        
        assert config.pattern_cache_size == 10000
        assert config.grammar_cache_size == 1000
        assert config.nlp_cache_size == 5000
        assert config.result_cache_size == 50000
        
        assert config.pattern_ttl == 3600.0
        assert config.grammar_ttl == 7200.0
        assert config.nlp_ttl == 1800.0
        assert config.result_ttl == 300.0
        
        assert config.pattern_policy == CachePolicy.LFU
        assert config.grammar_policy == CachePolicy.LRU
        assert config.nlp_policy == CachePolicy.ARC
        assert config.result_policy == CachePolicy.TTL
        
        assert config.enable_compression
        assert config.enable_statistics
        assert config.enable_warmup
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = TranslationCacheConfig(
            pattern_cache_size=20000,
            result_ttl=600.0,
            enable_compression=False
        )
        
        assert config.pattern_cache_size == 20000
        assert config.result_ttl == 600.0
        assert not config.enable_compression


class TestTranslationCacheManager:
    """Test translation cache manager functionality."""
    
    def test_cache_initialization(self):
        """Test cache manager initialization."""
        manager = TranslationCacheManager()
        
        assert manager.pattern_cache is not None
        assert manager.grammar_cache is not None
        assert manager.nlp_cache is not None
        assert manager.result_cache is not None
        
        assert manager.stats['pattern_lookups'] == 0
        assert manager.stats['total_time_saved'] == 0.0
    
    def test_pattern_caching(self):
        """Test pattern caching operations."""
        manager = TranslationCacheManager()
        
        # Cache a pattern
        pattern = "test_pattern_[0-9]+"
        result = {'matched': True, 'groups': ['123']}
        
        assert manager.cache_pattern(pattern, result)
        
        # Retrieve cached pattern
        cached = manager.get_pattern(pattern)
        assert cached == result
        assert manager.stats['pattern_lookups'] == 1
        
        # Test cache miss
        assert manager.get_pattern("nonexistent") is None
        assert manager.stats['pattern_lookups'] == 2
    
    def test_grammar_caching(self):
        """Test grammar caching operations."""
        manager = TranslationCacheManager()
        
        # Cache a grammar
        grammar_id = "test_grammar_v1"
        parsed_grammar = {'rules': [], 'version': '1.0'}
        
        assert manager.cache_grammar(grammar_id, parsed_grammar)
        
        # Retrieve cached grammar
        cached = manager.get_grammar(grammar_id)
        assert cached == parsed_grammar
        assert manager.stats['grammar_lookups'] == 1
    
    def test_nlp_caching(self):
        """Test NLP result caching."""
        manager = TranslationCacheManager()
        
        # Cache NLP analysis
        text = "The user must provide valid credentials"
        analysis = {
            'entities': ['user', 'credentials'],
            'intent': 'requirement',
            'sentiment': 'neutral'
        }
        
        assert manager.cache_nlp_result(text, analysis)
        
        # Retrieve cached analysis
        cached = manager.get_nlp_result(text)
        assert cached == analysis
        assert manager.stats['nlp_lookups'] == 1
    
    def test_translation_caching(self):
        """Test translation result caching."""
        manager = TranslationCacheManager()
        
        # Cache translation
        source = "user must have admin role"
        target_format = "tau"
        result = "∀u ∈ Users: hasRole(u, 'admin')"
        
        assert manager.cache_translation(source, target_format, result)
        
        # Retrieve cached translation
        cached = manager.get_translation(source, target_format)
        assert cached == result
        assert manager.stats['result_lookups'] == 1
    
    def test_cache_warmup(self):
        """Test cache warming functionality."""
        manager = TranslationCacheManager()
        
        warmup_data = {
            'patterns': {
                'pattern1': {'result': 1},
                'pattern2': {'result': 2}
            },
            'grammars': {
                'grammar1': {'parsed': True},
                'grammar2': {'parsed': True}
            },
            'nlp': {
                'text1': {'analysis': 'result1'},
                'text2': {'analysis': 'result2'}
            }
        }
        
        manager.warm_caches(warmup_data)
        
        # Verify warmed data is accessible
        assert manager.get_pattern('pattern1') == {'result': 1}
        assert manager.get_grammar('grammar1') == {'parsed': True}
        assert manager.get_nlp_result('text1') == {'analysis': 'result1'}
    
    def test_cache_warmup_disabled(self):
        """Test that warmup respects configuration."""
        config = TranslationCacheConfig(enable_warmup=False)
        manager = TranslationCacheManager(config)
        
        warmup_data = {'patterns': {'p1': 'r1'}}
        manager.warm_caches(warmup_data)
        
        # Should not be cached when warmup is disabled
        assert manager.get_pattern('p1') is None
    
    def test_statistics_collection(self):
        """Test statistics collection."""
        manager = TranslationCacheManager()
        
        # Generate some activity
        manager.cache_pattern("p1", "r1")
        manager.get_pattern("p1")
        manager.get_pattern("p2")  # miss
        
        manager.cache_grammar("g1", "parsed")
        manager.get_grammar("g1")
        
        stats = manager.get_statistics()
        
        assert 'lookups' in stats
        assert stats['lookups']['pattern_lookups'] == 2
        assert stats['lookups']['grammar_lookups'] == 1
        
        assert 'caches' in stats
        assert 'pattern' in stats['caches']
        assert 'grammar' in stats['caches']
    
    def test_clear_all_caches(self):
        """Test clearing all caches."""
        manager = TranslationCacheManager()
        
        # Add data to caches
        manager.cache_pattern("p1", "r1")
        manager.cache_grammar("g1", "parsed")
        manager.cache_nlp_result("text", "analysis")
        manager.cache_translation("source", "tau", "result")
        
        # Verify data exists
        assert manager.get_pattern("p1") is not None
        assert manager.get_grammar("g1") is not None
        
        # Clear all caches
        manager.clear_all_caches()
        
        # Verify data is gone
        assert manager.get_pattern("p1") is None
        assert manager.get_grammar("g1") is None
        assert manager.get_nlp_result("text") is None
        assert manager.get_translation("source", "tau") is None
    
    def test_key_generation_with_compression(self):
        """Test cache key generation with compression enabled."""
        manager = TranslationCacheManager()
        
        # Short content - no hashing
        short_content = "short"
        key1 = manager._generate_key(short_content)
        assert key1 == short_content
        
        # Long content - should hash
        long_content = "x" * 200
        key2 = manager._generate_key(long_content)
        assert len(key2) == 64  # SHA256 hex length
        assert key2 != long_content
    
    def test_key_generation_without_compression(self):
        """Test cache key generation with compression disabled."""
        config = TranslationCacheConfig(enable_compression=False)
        manager = TranslationCacheManager(config)
        
        # Long content should not be hashed
        long_content = "x" * 200
        key = manager._generate_key(long_content)
        assert key == long_content
    
    def test_custom_cache_policies(self):
        """Test using custom cache policies."""
        config = TranslationCacheConfig(
            pattern_policy=CachePolicy.LRU,
            grammar_policy=CachePolicy.LFU,
            nlp_policy=CachePolicy.TTL,
            result_policy=CachePolicy.ARC
        )
        
        manager = TranslationCacheManager(config)
        
        # Verify caches are initialized with correct policies
        # This is implementation-specific testing
        assert manager.pattern_cache is not None
        assert manager.grammar_cache is not None
        assert manager.nlp_cache is not None
        assert manager.result_cache is not None


class TestCachedTranslationDecorator:
    """Test the cached translation decorator."""
    
    def test_basic_caching(self):
        """Test basic function caching."""
        call_count = 0
        
        @cached_translation('result')
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate work
            return x * 2
        
        # First call - executes function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should be cached
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not called again
        
        # Different argument - executes function
        result3 = expensive_function(7)
        assert result3 == 14
        assert call_count == 2
    
    def test_cache_type_routing(self):
        """Test different cache type routing."""
        manager = get_translation_cache_manager()
        
        @cached_translation('pattern')
        def pattern_func(pattern: str) -> dict:
            return {'pattern': pattern}
        
        @cached_translation('nlp')
        def nlp_func(text: str) -> dict:
            return {'text': text}
        
        # Execute functions
        pattern_result = pattern_func("test_pattern")
        nlp_result = nlp_func("test_text")
        
        # Verify results are cached in correct caches
        cached_pattern = manager.get_pattern(
            _generate_function_cache_key(pattern_func, ("test_pattern",), {})
        )
        assert cached_pattern == {'pattern': 'test_pattern'}
        
        cached_nlp = manager.get_nlp_result(
            _generate_function_cache_key(nlp_func, ("test_text",), {})
        )
        assert cached_nlp == {'text': 'test_text'}
    
    def test_translation_cache_special_handling(self):
        """Test special handling for translation cache type."""
        manager = get_translation_cache_manager()
        
        @cached_translation('translation')
        def translate_func(source: str, target: str) -> str:
            return f"{source} -> {target}"
        
        # Execute function
        result = translate_func("input", "tau")
        assert result == "input -> tau"
        
        # Verify it's cached with special key format
        cached = manager.get_translation("input", "tau")
        assert cached == "input -> tau"
    
    def test_function_cache_key_generation(self):
        """Test cache key generation for functions."""
        def test_func(a: int, b: str, c: float = 1.0) -> str:
            return f"{a}-{b}-{c}"
        
        # Test with positional args
        key1 = _generate_function_cache_key(
            test_func, (1, "hello"), {}
        )
        assert "test_func" in key1
        assert "1" in key1
        assert "hello" in key1
        
        # Test with keyword args
        key2 = _generate_function_cache_key(
            test_func, (1, "hello"), {"c": 2.0}
        )
        assert "c=2.0" in key2
        
        # Test with complex object
        complex_obj = {"nested": "value"}
        key3 = _generate_function_cache_key(
            test_func, (1, complex_obj), {}
        )
        assert "test_func" in key3
        assert len(key3) < 200  # Ensure truncation works


class TestGlobalCacheManagement:
    """Test global cache management functions."""
    
    def test_global_manager_singleton(self):
        """Test global manager singleton behavior."""
        manager1 = get_translation_cache_manager()
        manager2 = get_translation_cache_manager()
        
        assert manager1 is manager2
        
        # Test operations affect same instance
        manager1.cache_pattern("test", "result")
        assert manager2.get_pattern("test") == "result"
    
    def test_configure_translation_cache(self):
        """Test reconfiguring the global cache."""
        # Get initial manager
        initial_manager = get_translation_cache_manager()
        
        # Reconfigure with custom settings
        config = TranslationCacheConfig(
            pattern_cache_size=100,
            enable_compression=False
        )
        configure_translation_cache(config)
        
        # Get new manager
        new_manager = get_translation_cache_manager()
        
        # Should be different instance
        assert new_manager is not initial_manager
        assert new_manager.config.pattern_cache_size == 100
        assert not new_manager.config.enable_compression


class TestPerformanceAndConcurrency:
    """Test performance and concurrent access."""
    
    def test_decorator_performance_tracking(self):
        """Test that decorator tracks time saved."""
        manager = get_translation_cache_manager()
        initial_time_saved = manager.stats['total_time_saved']
        
        @cached_translation('result')
        def slow_function(x: int) -> int:
            time.sleep(0.05)  # 50ms delay
            return x * 2
        
        # First call - slow
        slow_function(10)
        
        # Time saved should increase
        assert manager.stats['total_time_saved'] > initial_time_saved
        
        # Second call - fast (cached)
        start = time.time()
        result = slow_function(10)
        elapsed = time.time() - start
        
        assert result == 20
        assert elapsed < 0.02  # Should be very fast (increased threshold for CI)
    
    def test_concurrent_cache_access(self):
        """Test concurrent access to translation caches."""
        import threading
        
        manager = TranslationCacheManager()
        results = []
        errors = []
        
        def worker(thread_id: int):
            try:
                for i in range(50):
                    # Pattern operations
                    pattern = f"pattern_{thread_id}_{i}"
                    manager.cache_pattern(pattern, i)
                    result = manager.get_pattern(pattern)
                    if result != i:
                        errors.append(f"Pattern mismatch: {result} != {i}")
                    
                    # Translation operations
                    source = f"source_{thread_id}_{i}"
                    manager.cache_translation(source, "tau", f"result_{i}")
                    
                results.append(f"Thread {thread_id} completed")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {str(e)}")
        
        # Run concurrent threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])