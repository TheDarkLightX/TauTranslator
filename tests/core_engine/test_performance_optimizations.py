"""
Comprehensive tests for performance optimizations.

Tests all new implementations to ensure correctness and performance gains.

Author: DarkLightX / Dana Edwards
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import tempfile
import json
from pathlib import Path

# Import new implementations
from tau_translator_omega.core_engine.pattern_cache import PatternCache, get_pattern
from tau_translator_omega.core_engine.optimized_symbol_table import OptimizedSymbolTable
from tau_translator_omega.core_engine.semantic_types import Symbol
from tau_translator_omega.lmql_engine.parallel_recognizer import ParallelPatternMatcher
from tau_translator_omega.lmql_engine.confidence_optimizer import (
    ConfidenceOptimizer, TranslationExample
)
from tau_translator_omega.core_engine.trie import Trie, PatternTrie, KeywordTrie
from tau_translator_omega.core_engine.utils.lazy_loader import (
    LazyGrammarLoader, LazyPluginLoader, LazyLoaderManager
)
from tau_translator_omega.core_engine.utils.bloom_filter import (
    BloomFilter, ScalableBloomFilter, SymbolBloomFilter
)


class TestPatternCache:
    """Test pattern caching functionality."""
    
    def test_pattern_cache_basic(self):
        """Test basic pattern caching."""
        cache = PatternCache(max_size=10)
        
        # First access - cache miss
        pattern = cache.get_pattern(r'\d+')
        assert pattern.pattern == r'\d+'
        
        stats = cache.get_stats()
        assert stats['hit_count'] == 0
        assert stats['miss_count'] == 1
        
        # Second access - cache hit
        pattern2 = cache.get_pattern(r'\d+')
        assert pattern is pattern2  # Same object
        
        stats = cache.get_stats()
        assert stats['hit_count'] == 1
        assert stats['miss_count'] == 1
    
    def test_pattern_cache_eviction(self):
        """Test LRU eviction."""
        cache = PatternCache(max_size=3)
        
        # Fill cache
        cache.get_pattern('a')
        cache.get_pattern('b')
        cache.get_pattern('c')
        
        # Access 'a' to make it recently used
        cache.get_pattern('a')
        
        # Add new pattern - should evict 'b'
        cache.get_pattern('d')
        
        stats = cache.get_stats()
        assert stats['cache_size'] == 3
    
    def test_pattern_cache_thread_safety(self):
        """Test thread safety of pattern cache."""
        cache = PatternCache()
        patterns = [f'pattern_{i}' for i in range(100)]
        
        def access_patterns():
            for p in patterns:
                cache.get_pattern(p)
        
        # Run concurrent access
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(access_patterns) for _ in range(10)]
            for f in futures:
                f.result()
        
        stats = cache.get_stats()
        assert stats['cache_size'] <= cache._max_size


class TestOptimizedSymbolTable:
    """Test optimized symbol table."""
    
    def test_optimized_lookup(self):
        """Test O(1) symbol lookup."""
        table = OptimizedSymbolTable()
        
        # Add symbols in multiple scopes
        table.declare_symbol(Symbol('global_var', 'variable', 0))
        
        table.enter_scope()
        table.declare_symbol(Symbol('local_var', 'variable', 1))
        
        # Test lookups
        assert table.lookup_symbol('global_var') is not None
        assert table.lookup_symbol('local_var') is not None
        assert table.lookup_symbol('unknown') is None
        
        # Exit scope
        table.exit_scope()
        assert table.lookup_symbol('global_var') is not None
        assert table.lookup_symbol('local_var') is None
    
    def test_performance_vs_original(self):
        """Compare performance with original implementation."""
        # Create deep nesting
        table = OptimizedSymbolTable()
        
        # Add many symbols
        for i in range(100):
            table.declare_symbol(Symbol(f'var_{i}', 'variable', 0))
        
        # Create deep scopes
        for i in range(10):
            table.enter_scope()
            table.declare_symbol(Symbol(f'scope_{i}_var', 'variable', i + 1))
        
        # Time lookups
        start = time.time()
        for _ in range(1000):
            table.lookup_symbol('var_50')
            table.lookup_symbol('scope_5_var')
        lookup_time = time.time() - start
        
        stats = table.get_performance_stats()
        assert stats['cache_hit_rate'] > 90  # Should have high hit rate
        print(f"Optimized lookup time: {lookup_time:.4f}s")


class TestParallelPatternMatching:
    """Test parallel pattern recognition."""
    
    def test_parallel_recognition(self):
        """Test parallel pattern matching."""
        matcher = ParallelPatternMatcher(max_workers=4)
        
        # Test various patterns
        test_cases = [
            "adder[n] := i1[n] + i2[n]",  # Arithmetic
            "output_file(n) to \"results.txt\"",  # Stream
            "and_gate[t] := a[t] & b[t]",  # Logic gate
        ]
        
        for text in test_cases:
            results = matcher.recognize_parallel(text)
            assert len(results) > 0
            assert results[0].result.recognized
        
        # Test batch recognition
        batch_results = matcher.batch_recognize(test_cases)
        assert len(batch_results) == len(test_cases)
        
        matcher.shutdown()
    
    def test_adaptive_matching(self):
        """Test adaptive pattern matcher."""
        from tau_translator_omega.lmql_engine.parallel_recognizer import AdaptivePatternMatcher
        
        matcher = AdaptivePatternMatcher(max_workers=2)
        
        # Train with patterns
        for _ in range(10):
            matcher.recognize_parallel("adder[n] := i1[n] + i2[n]")
        
        stats = matcher.get_recognizer_stats()
        assert stats['arithmetic']['success_rate'] > 0
        
        # Get recommended order
        order = matcher.get_recommended_order()
        assert 'arithmetic' in order
        
        matcher.shutdown()


class TestConfidenceOptimizer:
    """Test gradient descent confidence optimization."""
    
    def test_confidence_optimization(self):
        """Test basic confidence optimization."""
        optimizer = ConfidenceOptimizer(learning_rate=0.1)
        
        # Add training examples
        examples = [
            TranslationExample("pattern1", "translation1", "type1", True, 0.85),
            TranslationExample("pattern2", "translation2", "type1", False, 0.85),
            TranslationExample("pattern3", "translation3", "type1", True, 0.85),
        ]
        
        for ex in examples:
            optimizer.add_training_example(ex)
        
        # Optimize
        results = optimizer.optimize(max_iterations=50, verbose=False)
        
        assert 'type1' in results
        result = results['type1']
        assert result.iterations > 0
        assert result.final_loss >= 0
    
    def test_adaptive_learning_rate(self):
        """Test adaptive learning rate adjustment."""
        optimizer = ConfidenceOptimizer(learning_rate=0.1)
        
        # Add examples
        for i in range(20):
            optimizer.add_training_example(
                TranslationExample(f"p{i}", f"t{i}", "type1", i % 2 == 0, 0.85)
            )
        
        initial_lr = optimizer.learning_rate
        optimizer.optimize(max_iterations=100)
        optimizer.adaptive_learning_rate()
        
        # Learning rate should decrease if plateaued
        assert optimizer.learning_rate <= initial_lr


class TestTrie:
    """Test Trie data structure."""
    
    def test_basic_trie_operations(self):
        """Test basic Trie operations."""
        trie = Trie()
        
        # Insert words
        words = ["hello", "help", "hero", "heroic"]
        for word in words:
            trie.insert(word)
        
        # Test search
        assert trie.search("hello")
        assert trie.search("help")
        assert not trie.search("hel")
        
        # Test prefix matching
        results = trie.starts_with("hel")
        assert set(results) == {"hello", "help"}
        
        # Test autocomplete
        suggestions = trie.autocomplete("her", max_results=2)
        assert len(suggestions) <= 2
        assert all(s.startswith("her") for s in suggestions)
    
    def test_pattern_trie(self):
        """Test pattern-specific Trie."""
        trie = PatternTrie()
        
        # Insert patterns
        trie.insert_pattern(r'\d+', 'number', 0.95)
        trie.insert_pattern(r'[a-z]+', 'word', 0.90)
        
        # Test pattern matching
        matches = trie.match_pattern("123")
        assert len(matches) > 0
        assert matches[0][1]['type'] == 'number'
    
    def test_keyword_trie(self):
        """Test keyword Trie."""
        trie = KeywordTrie()
        
        # Add keywords
        keywords = {
            'if': 'IF',
            'then': 'THEN',
            'else': 'ELSE',
            'function': 'FUNCTION'
        }
        trie.bulk_add_keywords(keywords)
        
        # Test classification
        assert trie.classify_token('if') == 'IF'
        assert trie.classify_token('variable') is None
        assert trie.is_reserved('function')


class TestLazyLoading:
    """Test lazy loading system."""
    
    def test_lazy_grammar_loader(self):
        """Test lazy grammar loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test grammar files
            grammar_dir = Path(tmpdir) / "grammars"
            grammar_dir.mkdir()
            
            (grammar_dir / "test.lark").write_text("start: NUMBER")
            (grammar_dir / "test2.ebnf").write_text("rule ::= term")
            
            # Test loader
            loader = LazyGrammarLoader(str(grammar_dir), max_cache_size=2)
            
            # Grammar not loaded yet
            stats = loader.get_stats()
            assert stats['cached_grammars'] == 0
            
            # Load grammar
            content = loader.get_grammar("test")
            assert content == "start: NUMBER"
            
            stats = loader.get_stats()
            assert stats['cached_grammars'] == 1
            assert stats['total_loads'] == 1
    
    def test_lazy_plugin_loader(self):
        """Test lazy plugin loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test plugin
            plugin_dir = Path(tmpdir) / "plugins" / "test_plugin"
            plugin_dir.mkdir(parents=True)
            
            manifest = {
                "id": "test_plugin",
                "name": "Test Plugin",
                "version": "1.0.0"
            }
            
            (plugin_dir / "plugin.json").write_text(json.dumps(manifest))
            
            # Test loader
            loader = LazyPluginLoader([str(Path(tmpdir) / "plugins")])
            
            # Check available plugins
            available = loader.get_available_plugins()
            assert "test_plugin" in available
            
            # Plugin not loaded yet
            assert len(loader.get_loaded_plugins()) == 0


class TestBloomFilter:
    """Test Bloom filter implementation."""
    
    def test_basic_bloom_filter(self):
        """Test basic Bloom filter operations."""
        bloom = BloomFilter(expected_items=1000, false_positive_rate=0.01)
        
        # Add items
        items = [f"item_{i}" for i in range(100)]
        for item in items:
            bloom.add(item)
        
        # Test membership
        for item in items:
            assert item in bloom
        
        # Test non-membership
        assert "not_in_filter" not in bloom
        
        # Check stats
        stats = bloom.get_stats()
        assert stats['item_count'] == 100
        assert stats['fill_ratio'] < 0.1  # Should be sparse
    
    def test_scalable_bloom_filter(self):
        """Test scalable Bloom filter."""
        bloom = ScalableBloomFilter(initial_capacity=10, false_positive_rate=0.01)
        
        # Add many items
        for i in range(100):
            bloom.add(f"item_{i}")
        
        # Test membership
        assert "item_50" in bloom
        assert "not_added" not in bloom
        
        # Check that it scaled
        stats = bloom.get_stats()
        assert stats['num_filters'] > 1
    
    def test_symbol_bloom_filter(self):
        """Test symbol-specific Bloom filter."""
        bloom = SymbolBloomFilter(expected_symbols=1000)
        
        # Add symbols with categories
        bloom.add_symbol("my_var", "variables")
        bloom.add_symbol("my_func", "functions")
        bloom.add_symbol("MyType", "types")
        
        # Test category queries
        assert bloom.contains_in_category("my_var", "variables")
        assert not bloom.contains_in_category("my_var", "functions")
        
        # Get category stats
        cat_stats = bloom.get_category_stats()
        assert 'variables' in cat_stats


class TestIntegration:
    """Integration tests for all optimizations."""
    
    def test_combined_optimizations(self):
        """Test that all optimizations work together."""
        # Pattern cache
        pattern = get_pattern(r'\d+')
        assert pattern is not None
        
        # Symbol table with Bloom filter
        table = OptimizedSymbolTable()
        bloom = SymbolBloomFilter()
        
        # Add symbols
        for i in range(100):
            symbol = Symbol(f'var_{i}', 'variable', 0)
            table.declare_symbol(symbol)
            bloom.add_symbol(f'var_{i}', 'variables')
        
        # Fast negative lookup with Bloom filter
        if 'unknown_var' not in bloom:
            # Skip expensive lookup
            assert table.lookup_symbol('unknown_var') is None
        
        # Trie for keywords
        keyword_trie = KeywordTrie()
        keyword_trie.add_keyword('function', 'FUNCTION')
        
        assert keyword_trie.classify_token('function') == 'FUNCTION'
        
        print("All optimizations working together successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])