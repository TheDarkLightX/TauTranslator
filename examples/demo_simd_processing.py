#!/usr/bin/env python3
"""
SIMD Processing Demo

Demonstrates SIMD-optimized pattern matching and text processing
capabilities for the TauTranslator system.

Author: DarkLightX / Dana Edwards
"""

import sys
import os
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import with graceful fallback
try:
    from backend.unified.core.parallel.simd_processor import (
        SimdPatternEngine,
        get_simd_engine,
        shutdown_simd_engine
    )
    SIMD_AVAILABLE = True
except ImportError as e:
    print(f"Note: SIMD optimizations not available - {e}")
    print("Pattern matching will use standard processing.")
    SIMD_AVAILABLE = False


def demo_pattern_matching():
    """Demonstrate pattern matching capabilities."""
    print("\n=== Pattern Matching Demo ===")
    
    if not SIMD_AVAILABLE:
        print("SIMD not available - skipping demo")
        return
    
    # Create engine
    engine = get_simd_engine()
    
    # Define patterns
    patterns = {
        'email': '@',
        'url': 'http',
        'phone': '-',
        'mention': '@user'
    }
    
    # Compile patterns
    engine.compile_patterns(patterns)
    
    # Test texts
    texts = [
        "Contact us at support@example.com",
        "Visit our website at https://example.com",
        "Call us at 555-123-4567",
        "Follow @user123 for updates",
        "Email: info@test.org, Web: http://test.org"
    ]
    
    # Search for patterns
    print("\nSearching for patterns in texts:")
    results = engine.match_patterns(texts, list(patterns.keys()), parallel=False)
    
    for i, text in enumerate(texts):
        print(f"\nText {i+1}: '{text}'")
        for pattern_id, matches in results.items():
            if i < len(matches) and matches[i]:
                print(f"  - Found '{pattern_id}' at positions: {matches[i]}")


def demo_text_transformation():
    """Demonstrate text transformation capabilities."""
    print("\n=== Text Transformation Demo ===")
    
    if not SIMD_AVAILABLE:
        print("SIMD not available - skipping demo")
        return
    
    engine = get_simd_engine()
    
    # Define transforms
    transforms = {
        'uppercase': {chr(i): chr(i).upper() for i in range(97, 123)},
        'lowercase': {chr(i): chr(i).lower() for i in range(65, 91)},
        'leetspeak': {
            'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5'
        }
    }
    
    # Compile transforms
    engine.compile_transforms(transforms)
    
    # Test texts
    texts = [
        "Hello World",
        "Python Programming",
        "SIMD Processing"
    ]
    
    print("\nOriginal texts:")
    for text in texts:
        print(f"  - '{text}'")
    
    # Apply uppercase
    print("\nAfter uppercase transformation:")
    upper_texts = engine.transform_texts(texts, ['uppercase'], parallel=False)
    for text in upper_texts:
        print(f"  - '{text}'")
    
    # Apply leetspeak
    print("\nAfter leetspeak transformation:")
    leet_texts = engine.transform_texts(texts, ['leetspeak'], parallel=False)
    for text in leet_texts:
        print(f"  - '{text}'")


def demo_batch_replacement():
    """Demonstrate batch replacement capabilities."""
    print("\n=== Batch Replacement Demo ===")
    
    if not SIMD_AVAILABLE:
        print("SIMD not available - skipping demo")
        return
    
    engine = get_simd_engine()
    
    # Test texts
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "Python is a great programming language",
        "SIMD enables fast text processing"
    ]
    
    # Define replacements
    replacements = [
        ("quick", "fast"),
        ("brown", "red"),
        ("Python", "Tau"),
        ("great", "powerful"),
        ("SIMD", "Parallel processing")
    ]
    
    print("\nOriginal texts:")
    for text in texts:
        print(f"  - '{text}'")
    
    print("\nReplacements to apply:")
    for old, new in replacements:
        print(f"  - '{old}' → '{new}'")
    
    # Apply replacements
    print("\nAfter replacements:")
    result_texts = engine.replace_batch(texts, replacements, parallel=False)
    for text in result_texts:
        print(f"  - '{text}'")


def demo_processing_pipeline():
    """Demonstrate complex processing pipeline."""
    print("\n=== Processing Pipeline Demo ===")
    
    if not SIMD_AVAILABLE:
        print("SIMD not available - skipping demo")
        return
    
    engine = get_simd_engine()
    
    # Setup patterns and transforms
    engine.compile_patterns({
        'sensitive': 'password',
        'email': '@'
    })
    
    engine.compile_transforms({
        'uppercase': {chr(i): chr(i).upper() for i in range(97, 123)}
    })
    
    # Define pipeline
    pipeline = [
        {'type': 'pattern_match', 'pattern_id': 'sensitive'},
        {'type': 'transform', 'transform_id': 'uppercase'},
        {'type': 'replace', 'old': 'PASSWORD', 'new': '[REDACTED]'},
        {'type': 'replace', 'old': '@', 'new': '[at]'}
    ]
    
    # Test texts
    texts = [
        "User login with password: secret123",
        "Contact admin@example.com for help",
        "Change your password regularly"
    ]
    
    print("\nOriginal texts:")
    for text in texts:
        print(f"  - '{text}'")
    
    print("\nPipeline operations:")
    print("  1. Search for sensitive patterns")
    print("  2. Convert to uppercase")
    print("  3. Replace PASSWORD with [REDACTED]")
    print("  4. Replace @ with [at]")
    
    # Process pipeline
    start_time = time.perf_counter()
    final_texts, metrics = engine.process_pipeline(texts, pipeline)
    processing_time = time.perf_counter() - start_time
    
    print("\nAfter pipeline processing:")
    for text in final_texts:
        print(f"  - '{text}'")
    
    print(f"\nProcessing stats:")
    print(f"  - Time: {processing_time:.3f}s")
    print(f"  - Throughput: {metrics.average_throughput:.2f} MB/s")
    print(f"  - Success rate: {metrics.success_rate:.1f}%")


def demo_performance_comparison():
    """Demonstrate performance comparison."""
    print("\n=== Performance Comparison Demo ===")
    
    if not SIMD_AVAILABLE:
        print("SIMD not available - skipping demo")
        return
    
    engine = get_simd_engine()
    
    # Create test data
    print("\nGenerating test data...")
    test_texts = []
    for i in range(1000):
        test_texts.append(f"This is test text {i} with pattern matching example data")
    
    print(f"Created {len(test_texts)} test texts")
    
    # Setup
    engine.compile_patterns({
        'test': 'test',
        'pattern': 'pattern',
        'example': 'example'
    })
    
    operations = [
        {'type': 'pattern_match', 'pattern_id': 'test'},
        {'type': 'pattern_match', 'pattern_id': 'pattern'}
    ]
    
    # Run benchmark
    print("\nRunning performance benchmark...")
    benchmark = engine.benchmark(test_texts, operations)
    
    print(f"\nResults:")
    print(f"  - Sequential processing: {benchmark['sequential_time']:.3f}s")
    print(f"  - Parallel processing: {benchmark['parallel_time']:.3f}s")
    print(f"  - Speedup: {benchmark['speedup']:.2f}x")
    print(f"  - Efficiency: {benchmark['efficiency']:.1%}")


def main():
    """Run all demos."""
    print("SIMD Pattern Processing Demo")
    print("=" * 50)
    
    try:
        # Run demos
        demo_pattern_matching()
        demo_text_transformation()
        demo_batch_replacement()
        demo_processing_pipeline()
        demo_performance_comparison()
        
    finally:
        # Cleanup
        if SIMD_AVAILABLE:
            shutdown_simd_engine()
    
    print("\n" + "=" * 50)
    print("Demo complete!")


if __name__ == "__main__":
    main()