#!/usr/bin/env python3
"""
SIMD Performance Benchmark Script

Demonstrates the performance improvements of SIMD-optimized pattern matching
and text processing compared to sequential processing.

Author: DarkLightX / Dana Edwards
"""

import sys
import os
import time
import statistics
from typing import List, Dict, Any
import random
import string

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Check for required dependencies
try:
    import numpy as np
    import numba
    from backend.unified.core.parallel.simd_processor import (
        SimdPatternEngine,
        SimdPatternMatcher,
        SimdTransformProcessor,
        get_simd_engine,
        shutdown_simd_engine
    )
except ImportError as e:
    print(f"Error: Missing required dependency - {e}")
    print("Please install required packages:")
    print("  pip install numpy numba psutil")
    sys.exit(1)


def generate_test_data(num_texts: int, text_length: int, pattern_density: float = 0.1) -> List[str]:
    """Generate test data for benchmarking."""
    texts = []
    patterns = ["pattern", "test", "example", "data", "process"]
    
    for _ in range(num_texts):
        # Generate random text with controlled pattern density
        words = []
        for _ in range(text_length // 7):  # Average word length ~7
            if random.random() < pattern_density:
                words.append(random.choice(patterns))
            else:
                word_len = random.randint(3, 10)
                words.append(''.join(random.choices(string.ascii_lowercase, k=word_len)))
        texts.append(' '.join(words))
    
    return texts


def benchmark_pattern_matching(engine: SimdPatternEngine, texts: List[str], 
                              patterns: Dict[str, str], iterations: int = 3) -> Dict[str, Any]:
    """Benchmark pattern matching performance."""
    print("\n=== Pattern Matching Benchmark ===")
    
    # Compile patterns
    engine.compile_patterns(patterns)
    pattern_ids = list(patterns.keys())
    
    # Sequential benchmark
    seq_times = []
    for i in range(iterations):
        start = time.perf_counter()
        _ = engine.match_patterns(texts, pattern_ids, parallel=False)
        seq_time = time.perf_counter() - start
        seq_times.append(seq_time)
        print(f"Sequential run {i+1}: {seq_time:.3f}s")
    
    # Parallel benchmark
    par_times = []
    for i in range(iterations):
        start = time.perf_counter()
        _ = engine.match_patterns(texts, pattern_ids, parallel=True)
        par_time = time.perf_counter() - start
        par_times.append(par_time)
        print(f"Parallel run {i+1}: {par_time:.3f}s")
    
    # Calculate statistics
    seq_avg = statistics.mean(seq_times)
    par_avg = statistics.mean(par_times)
    speedup = seq_avg / par_avg if par_avg > 0 else 0
    
    return {
        'sequential_avg': seq_avg,
        'parallel_avg': par_avg,
        'speedup': speedup,
        'texts_processed': len(texts),
        'patterns_searched': len(patterns)
    }


def benchmark_transformations(engine: SimdPatternEngine, texts: List[str], 
                            iterations: int = 3) -> Dict[str, Any]:
    """Benchmark text transformation performance."""
    print("\n=== Text Transformation Benchmark ===")
    
    # Compile transforms
    transforms = {
        'uppercase': {chr(i): chr(i).upper() for i in range(97, 123)},
        'lowercase': {chr(i): chr(i).lower() for i in range(65, 91)},
        'rot13': {chr(i): chr((ord(chr(i)) - 97 + 13) % 26 + 97) for i in range(97, 123)}
    }
    engine.compile_transforms(transforms)
    
    # Sequential benchmark
    seq_times = []
    for i in range(iterations):
        start = time.perf_counter()
        _ = engine.transform_texts(texts, ['uppercase', 'rot13'], parallel=False)
        seq_time = time.perf_counter() - start
        seq_times.append(seq_time)
        print(f"Sequential run {i+1}: {seq_time:.3f}s")
    
    # Parallel benchmark
    par_times = []
    for i in range(iterations):
        start = time.perf_counter()
        _ = engine.transform_texts(texts, ['uppercase', 'rot13'], parallel=True)
        par_time = time.perf_counter() - start
        par_times.append(par_time)
        print(f"Parallel run {i+1}: {par_time:.3f}s")
    
    # Calculate statistics
    seq_avg = statistics.mean(seq_times)
    par_avg = statistics.mean(par_times)
    speedup = seq_avg / par_avg if par_avg > 0 else 0
    
    return {
        'sequential_avg': seq_avg,
        'parallel_avg': par_avg,
        'speedup': speedup,
        'texts_processed': len(texts),
        'transforms_applied': 2
    }


def benchmark_replacements(engine: SimdPatternEngine, texts: List[str], 
                         iterations: int = 3) -> Dict[str, Any]:
    """Benchmark batch replacement performance."""
    print("\n=== Batch Replacement Benchmark ===")
    
    replacements = [
        ("pattern", "PATTERN"),
        ("test", "TEST"),
        ("example", "EXAMPLE"),
        ("data", "DATA"),
        ("process", "PROCESS")
    ]
    
    # Sequential benchmark
    seq_times = []
    for i in range(iterations):
        start = time.perf_counter()
        _ = engine.replace_batch(texts, replacements, parallel=False)
        seq_time = time.perf_counter() - start
        seq_times.append(seq_time)
        print(f"Sequential run {i+1}: {seq_time:.3f}s")
    
    # Parallel benchmark
    par_times = []
    for i in range(iterations):
        start = time.perf_counter()
        _ = engine.replace_batch(texts, replacements, parallel=True)
        par_time = time.perf_counter() - start
        par_times.append(par_time)
        print(f"Parallel run {i+1}: {par_time:.3f}s")
    
    # Calculate statistics
    seq_avg = statistics.mean(seq_times)
    par_avg = statistics.mean(par_times)
    speedup = seq_avg / par_avg if par_avg > 0 else 0
    
    return {
        'sequential_avg': seq_avg,
        'parallel_avg': par_avg,
        'speedup': speedup,
        'texts_processed': len(texts),
        'replacements': len(replacements)
    }


def benchmark_complex_pipeline(engine: SimdPatternEngine, texts: List[str]) -> Dict[str, Any]:
    """Benchmark complex processing pipeline."""
    print("\n=== Complex Pipeline Benchmark ===")
    
    # Setup complex pipeline
    engine.compile_patterns({
        'email': '@',
        'url': 'http',
        'number': '\\d+'
    })
    
    engine.compile_transforms({
        'uppercase': {chr(i): chr(i).upper() for i in range(97, 123)}
    })
    
    pipeline = [
        {'type': 'pattern_match', 'pattern_id': 'email'},
        {'type': 'pattern_match', 'pattern_id': 'url'},
        {'type': 'transform', 'transform_id': 'uppercase'},
        {'type': 'replace', 'old': 'PATTERN', 'new': '[REDACTED]'},
        {'type': 'replace', 'old': 'TEST', 'new': '[REMOVED]'}
    ]
    
    # Run benchmark using engine's built-in benchmark
    operations = pipeline[:2]  # Use first two operations for comparison
    benchmark_result = engine.benchmark(texts[:1000], operations)  # Use subset for built-in benchmark
    
    # Run full pipeline
    start = time.perf_counter()
    final_texts, metrics = engine.process_pipeline(texts, pipeline)
    pipeline_time = time.perf_counter() - start
    
    print(f"Pipeline processing time: {pipeline_time:.3f}s")
    print(f"Throughput: {metrics.average_throughput:.2f} MB/s")
    print(f"Success rate: {metrics.success_rate:.1f}%")
    
    return {
        'pipeline_time': pipeline_time,
        'throughput_mbps': metrics.average_throughput,
        'success_rate': metrics.success_rate,
        'builtin_speedup': benchmark_result['speedup'],
        'total_operations': len(pipeline)
    }


def print_summary(results: Dict[str, Dict[str, Any]]) -> None:
    """Print benchmark summary."""
    print("\n" + "="*60)
    print("SIMD PERFORMANCE BENCHMARK SUMMARY")
    print("="*60)
    
    for name, result in results.items():
        print(f"\n{name}:")
        if 'speedup' in result:
            print(f"  Average Speedup: {result['speedup']:.2f}x")
            print(f"  Sequential Time: {result.get('sequential_avg', 0):.3f}s")
            print(f"  Parallel Time: {result.get('parallel_avg', 0):.3f}s")
        
        for key, value in result.items():
            if key not in ['speedup', 'sequential_avg', 'parallel_avg']:
                if isinstance(value, float):
                    print(f"  {key.replace('_', ' ').title()}: {value:.2f}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "="*60)
    print("PERFORMANCE INSIGHTS:")
    print("="*60)
    
    avg_speedup = statistics.mean([r['speedup'] for r in results.values() if 'speedup' in r])
    print(f"- Average SIMD Speedup: {avg_speedup:.2f}x")
    print(f"- Best suited for: Large text datasets (>100 texts)")
    print(f"- Numba JIT compilation: Enabled")
    print(f"- CPU cores utilized: {numba.config.NUMBA_NUM_THREADS}")
    print(f"- Threading layer: {numba.config.THREADING_LAYER}")


def main():
    """Run SIMD performance benchmarks."""
    print("SIMD Pattern Processing Performance Benchmark")
    print("=" * 60)
    
    # Generate test data
    print("\nGenerating test data...")
    small_texts = generate_test_data(100, 100, 0.2)
    medium_texts = generate_test_data(1000, 500, 0.15)
    large_texts = generate_test_data(5000, 1000, 0.1)
    
    print(f"Small dataset: {len(small_texts)} texts (~{sum(len(t) for t in small_texts)/1024:.1f}KB)")
    print(f"Medium dataset: {len(medium_texts)} texts (~{sum(len(t) for t in medium_texts)/1024:.1f}KB)")
    print(f"Large dataset: {len(large_texts)} texts (~{sum(len(t) for t in large_texts)/1024/1024:.1f}MB)")
    
    # Create SIMD engine
    engine = SimdPatternEngine(auto_optimize=True)
    
    # Define patterns to search
    patterns = {
        'pattern1': 'pattern',
        'pattern2': 'test',
        'pattern3': 'example',
        'pattern4': 'data',
        'pattern5': 'process'
    }
    
    # Run benchmarks on different dataset sizes
    print("\n" + "="*60)
    print("BENCHMARKING LARGE DATASET")
    print("="*60)
    
    results = {}
    
    # Pattern matching
    results['Pattern Matching'] = benchmark_pattern_matching(engine, large_texts, patterns)
    
    # Text transformations
    results['Text Transformations'] = benchmark_transformations(engine, large_texts)
    
    # Batch replacements
    results['Batch Replacements'] = benchmark_replacements(engine, large_texts)
    
    # Complex pipeline
    results['Complex Pipeline'] = benchmark_complex_pipeline(engine, large_texts)
    
    # Print summary
    print_summary(results)
    
    # Cleanup
    shutdown_simd_engine()
    
    print("\nBenchmark complete!")


if __name__ == "__main__":
    main()