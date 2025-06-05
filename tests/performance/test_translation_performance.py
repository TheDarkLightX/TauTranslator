"""
Performance tests for translation engines.

Measures timing, throughput, and resource usage.

Author: DarkLightX / Dana Edwards
"""

import pytest
import sys
import time
import statistics
from pathlib import Path
from typing import List, Tuple
import gc

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.translators.manager import TranslationManager
from backend.unified.translators.pattern_translator import PatternTranslationEngine
from backend.unified.translators.grammar_translator import GrammarTranslationEngine
from backend.unified.translators.base import TranslationDirection


class PerformanceMetrics:
    """Helper class to collect performance metrics."""
    
    def __init__(self):
        self.times: List[float] = []
        self.start_time = None
    
    def start(self):
        """Start timing."""
        self.start_time = time.perf_counter()
    
    def stop(self):
        """Stop timing and record."""
        if self.start_time:
            elapsed = time.perf_counter() - self.start_time
            self.times.append(elapsed)
            self.start_time = None
            return elapsed
        return 0
    
    def get_stats(self):
        """Get performance statistics."""
        if not self.times:
            return {}
        
        return {
            "count": len(self.times),
            "total": sum(self.times),
            "mean": statistics.mean(self.times),
            "median": statistics.median(self.times),
            "min": min(self.times),
            "max": max(self.times),
            "stdev": statistics.stdev(self.times) if len(self.times) > 1 else 0
        }


class TestTranslationPerformance:
    """Performance tests for translation engines."""
    
    @pytest.fixture
    def pattern_engine(self):
        """Create a pattern translation engine."""
        return PatternTranslationEngine()
    
    @pytest.fixture
    def manager_with_engines(self):
        """Create a manager with engines."""
        manager = TranslationManager()
        
        pattern_engine = PatternTranslationEngine()
        manager.register_engine(pattern_engine, is_fallback=True)
        
        try:
            grammar_engine = GrammarTranslationEngine()
            manager.register_engine(grammar_engine, is_default=True)
        except:
            pass
        
        return manager
    
    # Single translation performance tests
    
    def test_pattern_engine_single_translation_speed(self, pattern_engine):
        """Test speed of single translations with pattern engine."""
        test_cases = [
            ("x equals 5", TranslationDirection.TO_TAU),
            ("x and y or z", TranslationDirection.TO_TAU),
            ("x > 5 & y < 10", TranslationDirection.TO_TCE),
        ]
        
        metrics = PerformanceMetrics()
        
        for text, direction in test_cases:
            metrics.start()
            result = pattern_engine.translate(text, direction)
            elapsed = metrics.stop()
            
            assert result.success
            assert elapsed < 0.01  # Should be under 10ms for simple patterns
        
        stats = metrics.get_stats()
        print(f"\nPattern engine single translation stats: {stats}")
        assert stats["mean"] < 0.01  # Average should be under 10ms
    
    def test_grammar_engine_single_translation_speed(self):
        """Test speed of single translations with grammar engine."""
        try:
            engine = GrammarTranslationEngine()
            if not engine.is_available:
                pytest.skip("Grammar engine not available")
        except:
            pytest.skip("Could not create grammar engine")
        
        test_cases = [
            ("x equals 5", TranslationDirection.TO_TAU),
            ("x and y", TranslationDirection.TO_TAU),
        ]
        
        metrics = PerformanceMetrics()
        
        for text, direction in test_cases:
            metrics.start()
            result = engine.translate(text, direction)
            elapsed = metrics.stop()
            
            # Grammar engine might fail, but should complete quickly
            assert elapsed < 0.1  # Should be under 100ms even with parsing
        
        stats = metrics.get_stats()
        print(f"\nGrammar engine single translation stats: {stats}")
    
    # Throughput tests
    
    def test_pattern_engine_throughput(self, pattern_engine):
        """Test pattern engine throughput for many translations."""
        expressions = [
            "x equals 5",
            "y > 10",
            "a and b or c",
            "not x",
            "p plus q minus r",
        ]
        
        num_iterations = 1000
        
        start_time = time.perf_counter()
        successful = 0
        
        for i in range(num_iterations):
            expr = expressions[i % len(expressions)]
            result = pattern_engine.translate(expr, TranslationDirection.TO_TAU)
            if result.success:
                successful += 1
        
        total_time = time.perf_counter() - start_time
        throughput = num_iterations / total_time
        
        print(f"\nPattern engine throughput:")
        print(f"  Translations: {num_iterations}")
        print(f"  Successful: {successful}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Throughput: {throughput:.1f} translations/second")
        
        assert successful == num_iterations  # All should succeed
        assert throughput > 1000  # Should handle >1000 translations/second
    
    def test_manager_throughput_with_fallback(self, manager_with_engines):
        """Test translation manager throughput with fallback."""
        expressions = [
            "x equals 5",
            "malformed expression",
            "y and z",
            "another bad one",
            "valid equals true",
        ]
        
        num_iterations = 500
        
        start_time = time.perf_counter()
        successful = 0
        
        for i in range(num_iterations):
            expr = expressions[i % len(expressions)]
            result = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
            if result.success:
                successful += 1
        
        total_time = time.perf_counter() - start_time
        throughput = num_iterations / total_time
        
        print(f"\nManager with fallback throughput:")
        print(f"  Translations: {num_iterations}")
        print(f"  Successful: {successful}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Throughput: {throughput:.1f} translations/second")
        
        assert successful > 0  # Some should succeed
        assert throughput > 100  # Should handle >100 translations/second with fallback
    
    # Scaling tests
    
    def test_performance_scaling_with_expression_length(self, pattern_engine):
        """Test how performance scales with expression length."""
        base_expr = "x{} equals {}"
        lengths = [1, 10, 50, 100, 500]
        
        metrics_by_length = {}
        
        for length in lengths:
            # Create expression with 'length' terms
            terms = [base_expr.format(i, i) for i in range(length)]
            long_expr = " and ".join(terms)
            
            metrics = PerformanceMetrics()
            
            # Do 10 translations of this length
            for _ in range(10):
                metrics.start()
                result = pattern_engine.translate(long_expr, TranslationDirection.TO_TAU)
                metrics.stop()
                assert result.success
            
            stats = metrics.get_stats()
            metrics_by_length[length] = stats["mean"]
            
            print(f"\nLength {length}: {stats['mean']*1000:.2f}ms average")
        
        # Check that performance scales reasonably (not exponentially)
        # Time for 500 terms should be less than 100x time for 1 term
        assert metrics_by_length[500] < metrics_by_length[1] * 100
    
    def test_performance_with_nested_expressions(self, pattern_engine):
        """Test performance with deeply nested expressions."""
        nesting_levels = [1, 5, 10, 20]
        
        metrics_by_level = {}
        
        for level in nesting_levels:
            # Create nested expression
            expr = "x equals 5"
            for i in range(level):
                expr = f"({expr} and y{i} > {i})"
            
            metrics = PerformanceMetrics()
            
            # Do 10 translations
            for _ in range(10):
                metrics.start()
                result = pattern_engine.translate(expr, TranslationDirection.TO_TAU)
                metrics.stop()
                assert result.success
            
            stats = metrics.get_stats()
            metrics_by_level[level] = stats["mean"]
            
            print(f"\nNesting level {level}: {stats['mean']*1000:.2f}ms average")
        
        # Performance should degrade gracefully
        assert metrics_by_level[20] < metrics_by_level[1] * 50
    
    # Caching performance tests
    
    def test_caching_performance_benefit(self):
        """Test performance benefit of caching (if implemented)."""
        try:
            engine = GrammarTranslationEngine()
            if not engine.is_available:
                pytest.skip("Grammar engine not available")
        except:
            pytest.skip("Could not create grammar engine")
        
        expr = "x equals 5 and y > 10"
        
        # First translation (cold cache)
        start = time.perf_counter()
        result1 = engine.translate(expr, TranslationDirection.TO_TAU)
        cold_time = time.perf_counter() - start
        
        # Subsequent translations (warm cache)
        warm_times = []
        for _ in range(10):
            start = time.perf_counter()
            result = engine.translate(expr, TranslationDirection.TO_TAU)
            warm_times.append(time.perf_counter() - start)
            assert result.translated_text == result1.translated_text
        
        avg_warm_time = statistics.mean(warm_times)
        
        print(f"\nCaching performance:")
        print(f"  Cold cache: {cold_time*1000:.2f}ms")
        print(f"  Warm cache average: {avg_warm_time*1000:.2f}ms")
        print(f"  Speedup: {cold_time/avg_warm_time:.1f}x")
        
        # Warm cache should be faster (if caching is implemented)
        # Pattern engine doesn't cache, so this might not show improvement
        if hasattr(engine, 'cache_size') and engine.cache_size > 0:
            assert avg_warm_time <= cold_time
    
    # Parallel translation performance
    
    def test_parallel_translation_performance(self, manager_with_engines):
        """Test performance of parallel translation mode."""
        expr = "x equals 5 and y > 10"
        
        # Sequential mode
        seq_start = time.perf_counter()
        seq_results = []
        for _ in range(10):
            result = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
            seq_results.append(result)
        seq_time = time.perf_counter() - seq_start
        
        # Parallel mode
        par_start = time.perf_counter()
        par_results = []
        for _ in range(10):
            results = manager_with_engines.translate_parallel(expr, TranslationDirection.TO_TAU)
            par_results.extend(results)
        par_time = time.perf_counter() - par_start
        
        print(f"\nParallel translation performance:")
        print(f"  Sequential (10 translations): {seq_time*1000:.2f}ms")
        print(f"  Parallel (10 batches): {par_time*1000:.2f}ms")
        
        # Parallel might not be faster for small workloads due to overhead
        assert par_time < seq_time * 3  # But shouldn't be much slower
    
    # Memory usage tests
    
    def test_memory_stability_many_translations(self, pattern_engine):
        """Test memory stability over many translations."""
        gc.collect()
        initial_count = len(gc.get_objects())
        
        # Do many translations
        for i in range(1000):
            expr = f"variable{i} equals {i}"
            result = pattern_engine.translate(expr, TranslationDirection.TO_TAU)
            assert result.success
        
        gc.collect()
        final_count = len(gc.get_objects())
        
        object_growth = final_count - initial_count
        
        print(f"\nMemory stability test:")
        print(f"  Initial objects: {initial_count}")
        print(f"  Final objects: {final_count}")
        print(f"  Growth: {object_growth}")
        
        # Should not leak too many objects
        assert object_growth < 1000  # Less than 1 object per translation
    
    # Stress tests
    
    def test_sustained_high_load(self, manager_with_engines):
        """Test sustained high load performance."""
        duration = 5.0  # Run for 5 seconds
        
        expressions = [
            "x equals 5",
            "y > 10 and z < 20",
            "not (a or b)",
            "p plus q minus r times s",
        ]
        
        start_time = time.perf_counter()
        count = 0
        successful = 0
        
        while time.perf_counter() - start_time < duration:
            expr = expressions[count % len(expressions)]
            result = manager_with_engines.translate(expr, TranslationDirection.TO_TAU)
            count += 1
            if result.success:
                successful += 1
        
        elapsed = time.perf_counter() - start_time
        rate = count / elapsed
        
        print(f"\nSustained load test:")
        print(f"  Duration: {elapsed:.1f}s")
        print(f"  Total translations: {count}")
        print(f"  Successful: {successful}")
        print(f"  Rate: {rate:.1f} translations/second")
        
        assert successful == count  # All should succeed
        assert rate > 100  # Should maintain >100 translations/second
    
    def test_performance_degradation_check(self, pattern_engine):
        """Test for performance degradation over time."""
        # Measure performance at start
        metrics_start = PerformanceMetrics()
        
        for _ in range(100):
            metrics_start.start()
            pattern_engine.translate("x equals 5", TranslationDirection.TO_TAU)
            metrics_start.stop()
        
        start_avg = metrics_start.get_stats()["mean"]
        
        # Do many translations
        for i in range(5000):
            pattern_engine.translate(f"var{i} equals {i}", TranslationDirection.TO_TAU)
        
        # Measure performance at end
        metrics_end = PerformanceMetrics()
        
        for _ in range(100):
            metrics_end.start()
            pattern_engine.translate("x equals 5", TranslationDirection.TO_TAU)
            metrics_end.stop()
        
        end_avg = metrics_end.get_stats()["mean"]
        
        degradation = (end_avg - start_avg) / start_avg * 100
        
        print(f"\nPerformance degradation test:")
        print(f"  Start average: {start_avg*1000:.2f}ms")
        print(f"  End average: {end_avg*1000:.2f}ms")
        print(f"  Degradation: {degradation:.1f}%")
        
        # Performance should not degrade significantly
        assert degradation < 20  # Less than 20% degradation


class TestPerformanceComparison:
    """Compare performance between different engines."""
    
    def test_engine_performance_comparison(self):
        """Compare performance of different translation engines."""
        engines = []
        
        # Create engines
        pattern_engine = PatternTranslationEngine()
        engines.append(("Pattern", pattern_engine))
        
        try:
            grammar_engine = GrammarTranslationEngine()
            if grammar_engine.is_available:
                engines.append(("Grammar", grammar_engine))
        except:
            pass
        
        # Test expressions
        test_cases = [
            ("x equals 5", TranslationDirection.TO_TAU),
            ("x and y or z", TranslationDirection.TO_TAU),
            ("x > 5 & y < 10", TranslationDirection.TO_TCE),
        ]
        
        results = {}
        
        for engine_name, engine in engines:
            metrics = PerformanceMetrics()
            successful = 0
            
            for text, direction in test_cases * 10:  # 10 iterations each
                metrics.start()
                result = engine.translate(text, direction)
                metrics.stop()
                if result.success:
                    successful += 1
            
            stats = metrics.get_stats()
            results[engine_name] = {
                "stats": stats,
                "success_rate": successful / (len(test_cases) * 10) * 100
            }
        
        print("\nEngine Performance Comparison:")
        print("-" * 60)
        print(f"{'Engine':<15} {'Avg Time':<15} {'Min Time':<15} {'Success Rate'}")
        print("-" * 60)
        
        for engine_name, data in results.items():
            stats = data["stats"]
            print(f"{engine_name:<15} {stats['mean']*1000:<15.2f}ms "
                  f"{stats['min']*1000:<15.2f}ms {data['success_rate']:.1f}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])