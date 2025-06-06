#!/usr/bin/env python3
"""
Comprehensive Performance Benchmarking Suite for Phase 2 Optimizations

Tests and benchmarks all performance optimizations including:
- FSA engine pattern matching
- Advanced caching strategies
- String matching algorithms
- Object pooling and memory management
- SIMD parallel processing

Provides baseline metrics, comparison reports, and regression detection.

Author: DarkLightX / Dana Edwards
"""

import sys
import os
import time
import json
import logging
import random
import string
import gc
import psutil
import threading
import multiprocessing as mp
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import optimization modules
from backend.unified.core.pattern_matching.fsa_engine import (
    FiniteStateAutomaton, FSAPatternCompiler, OptimizedPatternMatcher,
    get_pattern_matcher
)
from backend.unified.core.caching.advanced_cache import (
    LRUCache, LFUCache, TTLCache, AdaptiveReplacementCache,
    SmartCacheManager, get_cache_manager
)
from backend.unified.core.algorithms.string_matching import (
    BoyerMooreSearch, AhoCorasickAutomaton, KMPSearch, RabinKarpSearch,
    OptimizedStringMatcher, get_string_matcher
)
from backend.unified.core.memory.object_pools import (
    ObjectPool, PoolPolicy, MemoryManager, StringBuilderPool,
    get_memory_manager, get_string_builder_pool
)
from backend.unified.core.parallel.simd_processor import (
    SimdPatternEngine, ParallelBatchProcessor, get_simd_engine
)
from backend.unified.core.statistics import TranslationStatisticsService


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test."""
    test_name: str
    optimization: str
    baseline_time: float
    optimized_time: float
    speedup: float
    memory_before: float
    memory_after: float
    memory_saved: float
    iterations: int
    data_size: int
    additional_metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def speedup_percentage(self) -> float:
        """Calculate speedup as percentage."""
        if self.baseline_time > 0:
            return ((self.baseline_time - self.optimized_time) / self.baseline_time) * 100
        return 0.0
    
    @property
    def memory_saved_percentage(self) -> float:
        """Calculate memory saved as percentage."""
        if self.memory_before > 0:
            return ((self.memory_before - self.memory_after) / self.memory_before) * 100
        return 0.0


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results."""
    suite_name: str
    timestamp: datetime
    system_info: Dict[str, Any]
    results: List[BenchmarkResult] = field(default_factory=list)
    
    def add_result(self, result: BenchmarkResult) -> None:
        """Add benchmark result to suite."""
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.results:
            return {}
        
        speedups = [r.speedup for r in self.results]
        memory_savings = [r.memory_saved_percentage for r in self.results]
        
        return {
            'total_tests': len(self.results),
            'average_speedup': sum(speedups) / len(speedups),
            'max_speedup': max(speedups),
            'min_speedup': min(speedups),
            'average_memory_saved': sum(memory_savings) / len(memory_savings),
            'total_baseline_time': sum(r.baseline_time for r in self.results),
            'total_optimized_time': sum(r.optimized_time for r in self.results)
        }


class PerformanceBenchmarkRunner:
    """
    Main benchmark runner for all Phase 2 optimizations.
    
    Provides comprehensive testing, comparison, and reporting capabilities.
    """
    
    def __init__(self, output_dir: str = "benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add file handler
        log_file = self.output_dir / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        
        # System info
        self.system_info = self._get_system_info()
        
        # Test data generators
        self.test_data_cache = {}
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Collect system information."""
        cpu_info = {
            'count': mp.cpu_count(),
            'physical_cores': psutil.cpu_count(logical=False),
            'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0
        }
        
        memory_info = {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        }
        
        return {
            'platform': sys.platform,
            'python_version': sys.version,
            'cpu': cpu_info,
            'memory': memory_info,
            'timestamp': datetime.now().isoformat()
        }
    
    def _measure_memory(self) -> float:
        """Measure current process memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    
    def _generate_test_data(self, data_type: str, size: int) -> Any:
        """Generate test data for benchmarks."""
        cache_key = f"{data_type}_{size}"
        if cache_key in self.test_data_cache:
            return self.test_data_cache[cache_key]
        
        self.logger.info(f"Generating {data_type} test data of size {size}")
        
        if data_type == "text_corpus":
            # Generate realistic text corpus
            words = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog',
                    'hello', 'world', 'python', 'programming', 'benchmark', 'test',
                    'performance', 'optimization', 'algorithm', 'data', 'structure']
            
            texts = []
            for _ in range(size):
                length = random.randint(50, 200)
                text = ' '.join(random.choices(words, k=length))
                texts.append(text)
            
            data = texts
            
        elif data_type == "patterns":
            # Generate search patterns
            patterns = []
            for i in range(size):
                length = random.randint(3, 10)
                pattern = ''.join(random.choices(string.ascii_lowercase, k=length))
                patterns.append((f"pattern_{i}", pattern, f"replacement_{i}", i))
            
            data = patterns
            
        elif data_type == "cache_data":
            # Generate key-value pairs for caching
            data = {}
            for i in range(size):
                key = f"key_{i}_{random.randint(1000, 9999)}"
                value = {
                    'data': ''.join(random.choices(string.ascii_letters, k=100)),
                    'timestamp': time.time(),
                    'metadata': {'index': i}
                }
                data[key] = value
            
        else:
            data = None
        
        self.test_data_cache[cache_key] = data
        return data
    
    def benchmark_fsa_pattern_matching(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark FSA pattern matching vs regex."""
        self.logger.info("Starting FSA pattern matching benchmark")
        
        # Generate test data
        texts = self._generate_test_data("text_corpus", 1000)
        patterns = self._generate_test_data("patterns", 50)
        
        # Baseline: Regex matching
        import re
        regex_patterns = [(p[0], re.compile(p[1])) for p in patterns[:10]]  # Use subset for regex
        
        gc.collect()
        memory_before = self._measure_memory()
        
        baseline_start = time.perf_counter()
        for _ in range(iterations):
            for text in texts[:100]:  # Use subset for fair comparison
                for _, regex in regex_patterns:
                    list(regex.finditer(text))
        baseline_time = time.perf_counter() - baseline_start
        
        # Optimized: FSA matching
        fsa_compiler = FSAPatternCompiler()
        fsa = fsa_compiler.compile_patterns(patterns)
        
        gc.collect()
        
        optimized_start = time.perf_counter()
        for _ in range(iterations):
            for text in texts[:100]:
                fsa.find_all_matches(text)
        optimized_time = time.perf_counter() - optimized_start
        
        memory_after = self._measure_memory()
        
        speedup = baseline_time / optimized_time if optimized_time > 0 else 0
        
        result = BenchmarkResult(
            test_name="FSA Pattern Matching",
            optimization="Finite State Automaton",
            baseline_time=baseline_time,
            optimized_time=optimized_time,
            speedup=speedup,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_saved=memory_before - memory_after,
            iterations=iterations,
            data_size=len(texts),
            additional_metrics={
                'patterns_count': len(patterns),
                'fsa_states': len(fsa.states),
                'matches_per_second': (len(texts) * len(patterns) * iterations) / optimized_time
            }
        )
        
        self.logger.info(f"FSA benchmark complete: {speedup:.2f}x speedup")
        return result
    
    def benchmark_advanced_caching(self, iterations: int = 1000) -> BenchmarkResult:
        """Benchmark advanced caching strategies."""
        self.logger.info("Starting advanced caching benchmark")
        
        # Generate test data
        cache_data = self._generate_test_data("cache_data", 5000)
        keys = list(cache_data.keys())
        
        # Simulate access pattern (80/20 rule)
        hot_keys = keys[:1000]  # 20% of keys
        access_pattern = hot_keys * 4 + keys[1000:2000]  # 80% of accesses on 20% of keys
        random.shuffle(access_pattern)
        
        # Baseline: Simple dict cache
        simple_cache = {}
        
        gc.collect()
        memory_before = self._measure_memory()
        
        baseline_start = time.perf_counter()
        hits = 0
        for _ in range(iterations):
            for key in access_pattern[:100]:
                if key in simple_cache:
                    value = simple_cache[key]
                    hits += 1
                else:
                    simple_cache[key] = cache_data[key]
                    # Simple eviction when too large
                    if len(simple_cache) > 1000:
                        # Remove random key
                        del_key = random.choice(list(simple_cache.keys()))
                        del simple_cache[del_key]
        baseline_time = time.perf_counter() - baseline_start
        baseline_hit_rate = hits / (iterations * 100)
        
        # Optimized: Smart cache manager
        cache_manager = SmartCacheManager(max_size=1000)
        
        gc.collect()
        
        optimized_start = time.perf_counter()
        for _ in range(iterations):
            for key in access_pattern[:100]:
                value = cache_manager.get(key)
                if value is None:
                    cache_manager.put(key, cache_data[key])
        optimized_time = time.perf_counter() - optimized_start
        
        memory_after = self._measure_memory()
        
        # Get cache stats
        cache_stats = cache_manager.get_comprehensive_stats()
        optimized_hit_rate = cache_stats.get(cache_manager.current_strategy.value, {}).get('hit_rate', 0) / 100
        
        speedup = baseline_time / optimized_time if optimized_time > 0 else 0
        
        result = BenchmarkResult(
            test_name="Advanced Caching",
            optimization="Smart Cache Manager",
            baseline_time=baseline_time,
            optimized_time=optimized_time,
            speedup=speedup,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_saved=memory_before - memory_after,
            iterations=iterations,
            data_size=len(cache_data),
            additional_metrics={
                'baseline_hit_rate': baseline_hit_rate,
                'optimized_hit_rate': optimized_hit_rate,
                'hit_rate_improvement': (optimized_hit_rate - baseline_hit_rate) * 100,
                'current_strategy': cache_manager.current_strategy.value
            }
        )
        
        self.logger.info(f"Caching benchmark complete: {speedup:.2f}x speedup, "
                        f"{result.additional_metrics['hit_rate_improvement']:.1f}% hit rate improvement")
        return result
    
    def benchmark_string_matching(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark optimized string matching algorithms."""
        self.logger.info("Starting string matching benchmark")
        
        # Generate test data
        texts = self._generate_test_data("text_corpus", 500)
        search_patterns = ['the', 'quick', 'brown', 'fox', 'programming', 'test']
        
        # Baseline: Native string search
        gc.collect()
        memory_before = self._measure_memory()
        
        baseline_start = time.perf_counter()
        for _ in range(iterations):
            for text in texts:
                for pattern in search_patterns:
                    # Native find all occurrences
                    positions = []
                    start = 0
                    while True:
                        pos = text.find(pattern, start)
                        if pos == -1:
                            break
                        positions.append(pos)
                        start = pos + 1
        baseline_time = time.perf_counter() - baseline_start
        
        # Optimized: Aho-Corasick for multiple patterns
        matcher = AhoCorasickAutomaton(search_patterns)
        
        gc.collect()
        
        optimized_start = time.perf_counter()
        for _ in range(iterations):
            for text in texts:
                matches = matcher.search(text)
        optimized_time = time.perf_counter() - optimized_start
        
        memory_after = self._measure_memory()
        
        speedup = baseline_time / optimized_time if optimized_time > 0 else 0
        
        result = BenchmarkResult(
            test_name="String Matching",
            optimization="Aho-Corasick Algorithm",
            baseline_time=baseline_time,
            optimized_time=optimized_time,
            speedup=speedup,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_saved=memory_before - memory_after,
            iterations=iterations,
            data_size=len(texts),
            additional_metrics={
                'patterns_count': len(search_patterns),
                'average_text_length': sum(len(t) for t in texts) / len(texts),
                'throughput_mb_per_sec': sum(len(t) for t in texts) * iterations / (optimized_time * 1024 * 1024)
            }
        )
        
        self.logger.info(f"String matching benchmark complete: {speedup:.2f}x speedup")
        return result
    
    def benchmark_object_pooling(self, iterations: int = 10000) -> BenchmarkResult:
        """Benchmark object pooling vs direct allocation."""
        self.logger.info("Starting object pooling benchmark")
        
        # Test object class
        class TestObject:
            def __init__(self):
                self.data = [0] * 1000  # Reasonable size object
                self.timestamp = time.time()
            
            def reset(self):
                self.data = [0] * 1000
                self.timestamp = time.time()
            
            def is_valid(self):
                return True
        
        # Baseline: Direct allocation
        gc.collect()
        memory_before = self._measure_memory()
        
        baseline_start = time.perf_counter()
        for _ in range(iterations):
            obj = TestObject()
            # Simulate some work
            obj.data[500] = 42
            # Object goes out of scope and waits for GC
        baseline_time = time.perf_counter() - baseline_start
        
        # Force GC to see memory impact
        gc.collect()
        memory_after_baseline = self._measure_memory()
        
        # Optimized: Object pooling
        pool = ObjectPool(
            factory=TestObject,
            max_size=100,
            policy=PoolPolicy.LIFO
        )
        
        gc.collect()
        
        optimized_start = time.perf_counter()
        for _ in range(iterations):
            obj = pool.acquire()
            # Simulate same work
            obj.data[500] = 42
            pool.release(obj)
        optimized_time = time.perf_counter() - optimized_start
        
        memory_after = self._measure_memory()
        
        speedup = baseline_time / optimized_time if optimized_time > 0 else 0
        
        # Get pool stats
        pool_stats = pool.get_stats()
        
        result = BenchmarkResult(
            test_name="Object Pooling",
            optimization="Memory Pool with LIFO",
            baseline_time=baseline_time,
            optimized_time=optimized_time,
            speedup=speedup,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_saved=memory_after_baseline - memory_after,
            iterations=iterations,
            data_size=1,
            additional_metrics={
                'pool_size': pool_stats.current_size,
                'objects_created': pool_stats.created_objects,
                'objects_reused': pool_stats.reused_objects,
                'reuse_rate': pool_stats.reuse_rate,
                'gc_impact_reduction': (memory_after_baseline - memory_after) / 1024  # KB saved
            }
        )
        
        self.logger.info(f"Object pooling benchmark complete: {speedup:.2f}x speedup, "
                        f"{pool_stats.reuse_rate:.1f}% reuse rate")
        return result
    
    def benchmark_simd_processing(self, iterations: int = 10) -> BenchmarkResult:
        """Benchmark SIMD parallel processing."""
        self.logger.info("Starting SIMD processing benchmark")
        
        # Generate test data
        texts = self._generate_test_data("text_corpus", 5000)
        
        # Operations to perform
        operations = [
            {'type': 'pattern_match', 'pattern_id': 'email'},
            {'type': 'transform', 'transform_id': 'uppercase'},
            {'type': 'replace', 'old': 'the', 'new': 'THE'}
        ]
        
        # Setup SIMD engine
        engine = SimdPatternEngine()
        engine.compile_patterns({
            'email': r'[\w\.-]+@[\w\.-]+',
            'url': r'https?://[\w\.-]+'
        })
        engine.compile_transforms({
            'uppercase': {chr(i): chr(i).upper() for i in range(97, 123)}
        })
        
        # Baseline: Sequential processing
        gc.collect()
        memory_before = self._measure_memory()
        
        baseline_start = time.perf_counter()
        for _ in range(iterations):
            results = []
            for text in texts:
                # Sequential pattern matching
                if 'the' in text:
                    text = text.replace('the', 'THE')
                # Simple uppercase
                text = text.upper()
                results.append(text)
        baseline_time = time.perf_counter() - baseline_start
        
        # Optimized: SIMD parallel processing
        gc.collect()
        
        optimized_start = time.perf_counter()
        for _ in range(iterations):
            final_texts, metrics = engine.process_pipeline(texts, operations)
        optimized_time = time.perf_counter() - optimized_start
        
        memory_after = self._measure_memory()
        
        speedup = baseline_time / optimized_time if optimized_time > 0 else 0
        
        result = BenchmarkResult(
            test_name="SIMD Processing",
            optimization="Vectorized Parallel Processing",
            baseline_time=baseline_time,
            optimized_time=optimized_time,
            speedup=speedup,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_saved=memory_before - memory_after,
            iterations=iterations,
            data_size=len(texts),
            additional_metrics={
                'cpu_cores_used': mp.cpu_count(),
                'throughput': metrics.average_throughput if metrics else 0,
                'success_rate': metrics.success_rate if metrics else 0,
                'parallel_efficiency': speedup / mp.cpu_count()
            }
        )
        
        self.logger.info(f"SIMD benchmark complete: {speedup:.2f}x speedup")
        
        # Cleanup
        engine.shutdown()
        
        return result
    
    def run_all_benchmarks(self) -> BenchmarkSuite:
        """Run all benchmarks and collect results."""
        suite = BenchmarkSuite(
            suite_name="Phase 2 Performance Optimizations",
            timestamp=datetime.now(),
            system_info=self.system_info
        )
        
        self.logger.info("Starting comprehensive benchmark suite")
        
        # Run each benchmark
        benchmarks = [
            ("FSA Pattern Matching", self.benchmark_fsa_pattern_matching),
            ("Advanced Caching", self.benchmark_advanced_caching),
            ("String Matching", self.benchmark_string_matching),
            ("Object Pooling", self.benchmark_object_pooling),
            ("SIMD Processing", self.benchmark_simd_processing)
        ]
        
        for name, benchmark_func in benchmarks:
            try:
                self.logger.info(f"Running {name} benchmark...")
                result = benchmark_func()
                suite.add_result(result)
                self.logger.info(f"{name} complete: {result.speedup:.2f}x speedup")
            except Exception as e:
                self.logger.error(f"Error in {name} benchmark: {e}")
        
        return suite
    
    def generate_report(self, suite: BenchmarkSuite) -> str:
        """Generate comprehensive benchmark report."""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("PHASE 2 PERFORMANCE OPTIMIZATION BENCHMARK REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {suite.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # System Information
        report_lines.append("System Information:")
        report_lines.append(f"  Platform: {suite.system_info['platform']}")
        report_lines.append(f"  CPU Cores: {suite.system_info['cpu']['count']} "
                          f"({suite.system_info['cpu']['physical_cores']} physical)")
        report_lines.append(f"  Memory: {suite.system_info['memory']['total'] / (1024**3):.1f} GB")
        report_lines.append("")
        
        # Summary Statistics
        summary = suite.get_summary()
        report_lines.append("Summary Statistics:")
        report_lines.append(f"  Total Tests: {summary.get('total_tests', 0)}")
        report_lines.append(f"  Average Speedup: {summary.get('average_speedup', 0):.2f}x")
        report_lines.append(f"  Maximum Speedup: {summary.get('max_speedup', 0):.2f}x")
        report_lines.append(f"  Average Memory Saved: {summary.get('average_memory_saved', 0):.1f}%")
        report_lines.append(f"  Total Time Saved: {summary.get('total_baseline_time', 0) - summary.get('total_optimized_time', 0):.2f}s")
        report_lines.append("")
        
        # Detailed Results Table
        report_lines.append("Detailed Benchmark Results:")
        report_lines.append("")
        
        table_data = []
        for result in suite.results:
            table_data.append([
                result.test_name,
                f"{result.baseline_time:.3f}s",
                f"{result.optimized_time:.3f}s",
                f"{result.speedup:.2f}x",
                f"{result.speedup_percentage:.1f}%",
                f"{result.memory_saved:.1f}MB",
                f"{result.memory_saved_percentage:.1f}%"
            ])
        
        headers = ["Test", "Baseline", "Optimized", "Speedup", "Improvement", "Memory Saved", "Memory %"]
        report_lines.append(tabulate(table_data, headers=headers, tablefmt="grid"))
        report_lines.append("")
        
        # Individual Test Details
        report_lines.append("Individual Test Details:")
        report_lines.append("-" * 80)
        
        for result in suite.results:
            report_lines.append(f"\n{result.test_name}:")
            report_lines.append(f"  Optimization: {result.optimization}")
            report_lines.append(f"  Data Size: {result.data_size}")
            report_lines.append(f"  Iterations: {result.iterations}")
            report_lines.append(f"  Performance Gain: {result.speedup_percentage:.1f}%")
            
            if result.additional_metrics:
                report_lines.append("  Additional Metrics:")
                for key, value in result.additional_metrics.items():
                    if isinstance(value, float):
                        report_lines.append(f"    - {key}: {value:.2f}")
                    else:
                        report_lines.append(f"    - {key}: {value}")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        
        return "\n".join(report_lines)
    
    def save_results(self, suite: BenchmarkSuite, report: str) -> Dict[str, str]:
        """Save benchmark results in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save text report
        report_file = self.output_dir / f"benchmark_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save JSON data
        json_file = self.output_dir / f"benchmark_data_{timestamp}.json"
        suite_dict = {
            'suite_name': suite.suite_name,
            'timestamp': suite.timestamp.isoformat(),
            'system_info': suite.system_info,
            'results': [asdict(r) for r in suite.results],
            'summary': suite.get_summary()
        }
        with open(json_file, 'w') as f:
            json.dump(suite_dict, f, indent=2)
        
        # Save baseline metrics for regression detection
        baseline_file = self.output_dir / "baseline_metrics.json"
        baseline_data = {
            'timestamp': suite.timestamp.isoformat(),
            'metrics': {
                r.test_name: {
                    'speedup': r.speedup,
                    'memory_saved_percentage': r.memory_saved_percentage,
                    'optimized_time': r.optimized_time
                }
                for r in suite.results
            }
        }
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        return {
            'report': str(report_file),
            'data': str(json_file),
            'baseline': str(baseline_file)
        }
    
    def generate_visualizations(self, suite: BenchmarkSuite) -> str:
        """Generate performance visualization charts."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Speedup comparison chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Speedup bar chart
        test_names = [r.test_name for r in suite.results]
        speedups = [r.speedup for r in suite.results]
        colors = ['green' if s > 2 else 'orange' if s > 1.5 else 'red' for s in speedups]
        
        bars = ax1.bar(test_names, speedups, color=colors)
        ax1.set_ylabel('Speedup Factor')
        ax1.set_title('Performance Speedup by Optimization')
        ax1.axhline(y=1, color='black', linestyle='--', alpha=0.5)
        
        # Add value labels on bars
        for bar, speedup in zip(bars, speedups):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{speedup:.2f}x', ha='center', va='bottom')
        
        # Memory savings chart
        memory_savings = [r.memory_saved_percentage for r in suite.results]
        bars2 = ax2.bar(test_names, memory_savings, color='blue', alpha=0.7)
        ax2.set_ylabel('Memory Saved (%)')
        ax2.set_xlabel('Optimization')
        ax2.set_title('Memory Usage Improvement')
        
        # Add value labels
        for bar, saving in zip(bars2, memory_savings):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{saving:.1f}%', ha='center', va='bottom')
        
        # Rotate x labels for better readability
        for ax in [ax1, ax2]:
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.output_dir / f"benchmark_chart_{timestamp}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate time comparison chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(test_names))
        width = 0.35
        
        baseline_times = [r.baseline_time for r in suite.results]
        optimized_times = [r.optimized_time for r in suite.results]
        
        bars1 = ax.bar(x - width/2, baseline_times, width, label='Baseline', color='red', alpha=0.7)
        bars2 = ax.bar(x + width/2, optimized_times, width, label='Optimized', color='green', alpha=0.7)
        
        ax.set_ylabel('Time (seconds)')
        ax.set_title('Execution Time Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(test_names, rotation=45, ha='right')
        ax.legend()
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        time_chart_file = self.output_dir / f"time_comparison_{timestamp}.png"
        plt.savefig(time_chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
    
    def check_regression(self, current_suite: BenchmarkSuite) -> Dict[str, Any]:
        """Check for performance regressions against baseline."""
        baseline_file = self.output_dir / "baseline_metrics.json"
        
        if not baseline_file.exists():
            return {'status': 'no_baseline', 'regressions': []}
        
        with open(baseline_file) as f:
            baseline_data = json.load(f)
        
        baseline_metrics = baseline_data['metrics']
        regressions = []
        
        for result in current_suite.results:
            if result.test_name in baseline_metrics:
                baseline = baseline_metrics[result.test_name]
                
                # Check for speedup regression (10% threshold)
                speedup_diff = (result.speedup - baseline['speedup']) / baseline['speedup'] * 100
                if speedup_diff < -10:
                    regressions.append({
                        'test': result.test_name,
                        'metric': 'speedup',
                        'baseline': baseline['speedup'],
                        'current': result.speedup,
                        'regression': speedup_diff
                    })
                
                # Check for time regression (10% threshold)
                time_diff = (result.optimized_time - baseline['optimized_time']) / baseline['optimized_time'] * 100
                if time_diff > 10:
                    regressions.append({
                        'test': result.test_name,
                        'metric': 'execution_time',
                        'baseline': baseline['optimized_time'],
                        'current': result.optimized_time,
                        'regression': time_diff
                    })
        
        return {
            'status': 'checked',
            'baseline_date': baseline_data['timestamp'],
            'regressions': regressions,
            'regression_count': len(regressions)
        }


def main():
    """Main entry point for benchmark suite."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create benchmark runner
    runner = PerformanceBenchmarkRunner()
    
    print("TauTranslator Performance Benchmark Suite")
    print("=" * 50)
    print("Running comprehensive performance benchmarks...")
    print("This may take several minutes to complete.\n")
    
    # Run benchmarks
    start_time = time.time()
    suite = runner.run_all_benchmarks()
    elapsed_time = time.time() - start_time
    
    print(f"\nAll benchmarks completed in {elapsed_time:.1f} seconds")
    
    # Generate report
    print("Generating performance report...")
    report = runner.generate_report(suite)
    
    # Save results
    print("Saving benchmark results...")
    files = runner.save_results(suite, report)
    
    # Generate visualizations
    print("Creating performance charts...")
    chart_file = runner.generate_visualizations(suite)
    
    # Check for regressions
    print("Checking for performance regressions...")
    regression_check = runner.check_regression(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("BENCHMARK SUMMARY")
    print("=" * 50)
    
    summary = suite.get_summary()
    print(f"Total Tests Run: {summary['total_tests']}")
    print(f"Average Speedup: {summary['average_speedup']:.2f}x")
    print(f"Maximum Speedup: {summary['max_speedup']:.2f}x")
    print(f"Average Memory Saved: {summary['average_memory_saved']:.1f}%")
    
    if regression_check['regression_count'] > 0:
        print(f"\n⚠️  WARNING: {regression_check['regression_count']} performance regressions detected!")
        for reg in regression_check['regressions']:
            print(f"  - {reg['test']}: {reg['metric']} regressed by {abs(reg['regression']):.1f}%")
    else:
        print("\n✅ No performance regressions detected")
    
    print(f"\nResults saved to:")
    print(f"  Report: {files['report']}")
    print(f"  Data: {files['data']}")
    print(f"  Charts: {chart_file}")
    print(f"  Baseline: {files['baseline']}")
    
    # Print a sample of the report
    print("\n" + "=" * 50)
    print("REPORT PREVIEW")
    print("=" * 50)
    print("\n".join(report.split("\n")[:50]))
    print("\n... (see full report in output file)")


if __name__ == "__main__":
    main()