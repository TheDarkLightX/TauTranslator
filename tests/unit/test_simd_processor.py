"""
Comprehensive tests for SIMD-optimized parallel pattern processing.

Tests all aspects of the SIMD processor including:
- Vectorized pattern matching
- Parallel batch processing
- Transform operations
- Performance benchmarks
- Thread safety
- Resource management

Author: DarkLightX / Dana Edwards
"""

import pytest
import numpy as np
import threading
import time
import tempfile
import multiprocessing as mp
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import TimeoutError

from backend.unified.core.parallel.simd_processor import (
    SimdPatternMatcher,
    SimdTransformProcessor,
    ParallelBatchProcessor,
    SimdPatternEngine,
    BatchResult,
    ProcessingMetrics,
    simd_count_chars,
    simd_find_all,
    simd_to_upper,
    simd_to_lower,
    get_simd_engine,
    shutdown_simd_engine
)


class TestSimdPatternMatcher:
    """Test cases for SIMD-optimized pattern matching."""
    
    def test_pattern_compilation(self):
        """Test pattern compilation for SIMD operations."""
        matcher = SimdPatternMatcher()
        
        # Compile simple pattern
        matcher.compile_pattern("test_pattern", "hello")
        
        assert "test_pattern" in matcher.compiled_patterns
        assert "test_pattern" in matcher._pattern_cache
        
        # Check pattern metadata
        metadata = matcher._pattern_cache["test_pattern"]
        assert metadata['length'] == 5
        assert metadata['pattern'] == "hello"
        assert metadata['hash'] is not None
    
    def test_vectorized_search_single_match(self):
        """Test vectorized search with single match."""
        matcher = SimdPatternMatcher()
        matcher.compile_pattern("pattern1", "world")
        
        # Test single text
        texts = ["Hello world from Python"]
        results = matcher.search_batch(texts, "pattern1")
        
        assert len(results) == 1
        assert len(results[0]) == 1  # One match
        assert results[0][0] == 6  # Position of "world"
    
    def test_vectorized_search_multiple_matches(self):
        """Test vectorized search with multiple matches."""
        matcher = SimdPatternMatcher()
        matcher.compile_pattern("pattern2", "test")
        
        # Text with multiple occurrences
        texts = ["This is a test. Another test here. Final test."]
        results = matcher.search_batch(texts, "pattern2")
        
        assert len(results) == 1
        assert len(results[0]) == 3  # Three matches
    
    def test_vectorized_search_no_matches(self):
        """Test vectorized search with no matches."""
        matcher = SimdPatternMatcher()
        matcher.compile_pattern("pattern3", "xyz")
        
        texts = ["Hello world", "Python programming", "SIMD processing"]
        results = matcher.search_batch(texts, "pattern3")
        
        assert len(results) == 3
        assert all(len(r) == 0 for r in results)  # No matches
    
    def test_multi_pattern_search(self):
        """Test searching for multiple patterns in single text."""
        matcher = SimdPatternMatcher()
        
        # Compile multiple patterns
        matcher.compile_pattern("email", "@")
        matcher.compile_pattern("url", "http")
        matcher.compile_pattern("phone", "-")
        
        text = "Contact: john@example.com, visit http://site.com or call 555-1234"
        results = matcher.multi_pattern_search(text, ["email", "url", "phone"])
        
        assert "email" in results
        assert len(results["email"]) > 0  # Found @ symbol
        assert "url" in results
        assert len(results["url"]) > 0  # Found http
        assert "phone" in results
        assert len(results["phone"]) > 0  # Found - symbol
    
    def test_unicode_handling(self):
        """Test handling of Unicode text."""
        matcher = SimdPatternMatcher()
        matcher.compile_pattern("unicode_pattern", "café")
        
        texts = ["Welcome to the café!", "No match here", "Another café visit"]
        results = matcher.search_batch(texts, "unicode_pattern")
        
        assert len(results[0]) == 1  # First text has match
        assert len(results[1]) == 0  # Second text no match
        assert len(results[2]) == 1  # Third text has match
    
    def test_empty_pattern_handling(self):
        """Test handling of empty patterns."""
        matcher = SimdPatternMatcher()
        matcher.compile_pattern("empty", "")
        
        texts = ["Some text"]
        results = matcher.search_batch(texts, "empty")
        
        # Empty pattern should match at every position
        assert len(results) == 1
    
    def test_pattern_not_found(self):
        """Test searching for non-compiled pattern."""
        matcher = SimdPatternMatcher()
        
        results = matcher.search_batch(["test text"], "non_existent_pattern")
        assert len(results) == 1
        assert len(results[0]) == 0  # Empty result for non-existent pattern


class TestSimdTransformProcessor:
    """Test cases for SIMD-optimized text transformations."""
    
    def test_transform_table_creation(self):
        """Test creation of vectorized transformation tables."""
        processor = SimdTransformProcessor()
        
        # Create simple uppercase transform
        mappings = {chr(i): chr(i).upper() for i in range(97, 123)}  # a-z to A-Z
        processor.create_transform_table("uppercase", mappings)
        
        assert "uppercase" in processor.transform_tables
        table = processor.transform_tables["uppercase"]
        assert len(table) == 256  # Full byte lookup table
    
    def test_batch_transformation(self):
        """Test batch text transformation."""
        processor = SimdTransformProcessor()
        
        # Create lowercase transform
        mappings = {chr(i): chr(i).lower() for i in range(65, 91)}  # A-Z to a-z
        processor.create_transform_table("lowercase", mappings)
        
        texts = ["HELLO WORLD", "PYTHON SIMD", "TEST STRING"]
        results = processor.transform_batch(texts, "lowercase")
        
        assert len(results) == 3
        assert results[0] == "hello world"
        assert results[1] == "python simd"
        assert results[2] == "test string"
    
    def test_invalid_transform_table(self):
        """Test transformation with non-existent table."""
        processor = SimdTransformProcessor()
        
        texts = ["test text"]
        results = processor.transform_batch(texts, "non_existent_table")
        
        assert results == texts  # Should return original texts
    
    def test_parallel_replace_simple(self):
        """Test simple parallel replacement."""
        processor = SimdTransformProcessor()
        
        texts = ["Hello world", "Hello Python", "Hello SIMD"]
        results = processor.replace_batch(texts, "Hello", "Hi")
        
        assert len(results) == 3
        assert results[0] == "Hi world"
        assert results[1] == "Hi Python"
        assert results[2] == "Hi SIMD"
    
    def test_parallel_replace_multiple_occurrences(self):
        """Test replacement with multiple occurrences."""
        processor = SimdTransformProcessor()
        
        texts = ["test test test", "one test two test"]
        results = processor.replace_batch(texts, "test", "example")
        
        assert results[0] == "example example example"
        assert results[1] == "one example two example"
    
    def test_parallel_replace_no_match(self):
        """Test replacement with no matches."""
        processor = SimdTransformProcessor()
        
        texts = ["Hello world", "Python programming"]
        results = processor.replace_batch(texts, "xyz", "abc")
        
        assert results == texts  # No changes
    
    def test_replace_different_lengths(self):
        """Test replacement with different length strings."""
        processor = SimdTransformProcessor()
        
        # Shorter replacement
        texts = ["Hello world"]
        results = processor.replace_batch(texts, "Hello", "Hi")
        assert results[0] == "Hi world"
        
        # Longer replacement
        texts = ["Hi world"]
        results = processor.replace_batch(texts, "Hi", "Hello")
        assert results[0] == "Hello world"


class TestParallelBatchProcessor:
    """Test cases for parallel batch processing."""
    
    def test_processor_initialization(self):
        """Test processor initialization with various configurations."""
        # Default initialization
        processor = ParallelBatchProcessor()
        assert processor.num_workers == mp.cpu_count()
        assert processor.batch_size == 1000
        assert processor.use_processes
        
        # Custom initialization
        processor = ParallelBatchProcessor(num_workers=4, batch_size=500, use_processes=False)
        assert processor.num_workers == 4
        assert processor.batch_size == 500
        assert not processor.use_processes
    
    def test_pattern_registration(self):
        """Test pattern registration in processor."""
        processor = ParallelBatchProcessor()
        
        processor.add_pattern("test_pattern", "hello")
        assert "test_pattern" in processor.pattern_matcher.compiled_patterns
        
        processor.add_transform("test_transform", {"a": "A", "b": "B"})
        assert "test_transform" in processor.transform_processor.transform_tables
    
    def test_single_batch_processing(self):
        """Test processing of single batch."""
        processor = ParallelBatchProcessor()
        processor.add_pattern("pattern1", "test")
        
        texts = ["This is a test", "Another test here", "No match here"]
        operations = [{'type': 'pattern_match', 'pattern_id': 'pattern1'}]
        
        result = processor.process_batch(texts, operations)
        
        assert isinstance(result, BatchResult)
        assert result.success
        assert result.patterns_matched > 0
        assert result.input_size > 0
        assert result.throughput > 0
    
    def test_batch_processing_with_transforms(self):
        """Test batch processing with transformations."""
        processor = ParallelBatchProcessor()
        processor.add_transform("upper", {chr(i): chr(i).upper() for i in range(97, 123)})
        
        texts = ["hello world", "python programming"]
        operations = [{'type': 'transform', 'transform_id': 'upper'}]
        
        result = processor.process_batch(texts, operations)
        
        assert result.success
        assert result.transformations_applied == 2
        assert "final_texts" in result.metadata
        assert result.metadata['final_texts'][0] == "HELLO WORLD"
    
    def test_batch_processing_with_replacements(self):
        """Test batch processing with replacements."""
        processor = ParallelBatchProcessor()
        
        texts = ["foo bar foo", "bar foo bar"]
        operations = [{'type': 'replace', 'old': 'foo', 'new': 'baz'}]
        
        result = processor.process_batch(texts, operations)
        
        assert result.success
        assert result.transformations_applied == 2
        assert result.metadata['final_texts'][0] == "baz bar baz"
        assert result.metadata['final_texts'][1] == "bar baz bar"
    
    def test_batch_processing_error_handling(self):
        """Test error handling in batch processing."""
        processor = ParallelBatchProcessor()
        
        # Create operation that will fail
        texts = ["test"]
        operations = [{'type': 'invalid_operation'}]
        
        result = processor.process_batch(texts, operations)
        
        assert not result.success
        assert result.error is not None
    
    def test_parallel_processing_multiprocessing(self):
        """Test parallel processing with multiprocessing."""
        processor = ParallelBatchProcessor(num_workers=2, use_processes=True)
        processor.add_pattern("pattern1", "test")
        
        # Create larger dataset
        texts = ["test " * 10] * 100
        operations = [{'type': 'pattern_match', 'pattern_id': 'pattern1'}]
        
        results = processor.process_parallel(texts, operations, batch_size=50)
        
        assert len(results) == 2  # 100 texts / 50 batch_size
        assert all(r.success for r in results)
        
        # Check metrics
        metrics = processor.get_metrics()
        assert metrics.total_batches == 2
        assert metrics.successful_batches == 2
        assert metrics.average_throughput > 0
    
    def test_parallel_processing_threading(self):
        """Test parallel processing with threading."""
        processor = ParallelBatchProcessor(num_workers=2, use_processes=False)
        processor.add_transform("upper", {chr(i): chr(i).upper() for i in range(97, 123)})
        
        texts = ["hello world"] * 50
        operations = [{'type': 'transform', 'transform_id': 'upper'}]
        
        results = processor.process_parallel(texts, operations, batch_size=25)
        
        assert len(results) == 2  # 50 texts / 25 batch_size
        assert all(r.success for r in results)
    
    def test_metrics_collection(self):
        """Test metrics collection and reporting."""
        processor = ParallelBatchProcessor()
        
        # Process some batches
        texts = ["test text"] * 10
        operations = [{'type': 'replace', 'old': 'test', 'new': 'example'}]
        
        processor.process_parallel(texts, operations, batch_size=5)
        
        metrics = processor.get_metrics()
        assert metrics.total_batches == 2
        assert metrics.successful_batches == 2
        assert metrics.failed_batches == 0
        assert metrics.success_rate == 100.0
        assert metrics.cpu_usage_percent >= 0
        assert metrics.memory_usage_mb > 0
    
    def test_metrics_reset(self):
        """Test metrics reset functionality."""
        processor = ParallelBatchProcessor()
        
        # Process batch to generate metrics
        texts = ["test"] * 10
        operations = []
        processor.process_parallel(texts, operations)
        
        # Reset metrics
        processor.reset_metrics()
        metrics = processor.get_metrics()
        
        assert metrics.total_batches == 0
        assert metrics.successful_batches == 0
        assert metrics.total_input_size == 0
    
    def test_processor_shutdown(self):
        """Test processor shutdown."""
        processor = ParallelBatchProcessor()
        
        # Process something
        texts = ["test"]
        operations = []
        processor.process_parallel(texts, operations)
        
        # Shutdown
        processor.shutdown()
        assert processor._shutdown


class TestSimdPatternEngine:
    """Test cases for high-level SIMD pattern engine."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = SimdPatternEngine(auto_optimize=True)
        assert engine.auto_optimize
        assert isinstance(engine.processor, ParallelBatchProcessor)
        assert len(engine.operation_times) == 0
    
    def test_pattern_compilation(self):
        """Test bulk pattern compilation."""
        engine = SimdPatternEngine()
        
        patterns = {
            "email": r"@",
            "url": r"http",
            "phone": r"-"
        }
        engine.compile_patterns(patterns)
        
        # Check all patterns were compiled
        for pattern_id in patterns:
            assert pattern_id in engine.processor.pattern_matcher.compiled_patterns
    
    def test_transform_compilation(self):
        """Test bulk transform compilation."""
        engine = SimdPatternEngine()
        
        transforms = {
            "uppercase": {chr(i): chr(i).upper() for i in range(97, 123)},
            "lowercase": {chr(i): chr(i).lower() for i in range(65, 91)}
        }
        engine.compile_transforms(transforms)
        
        # Check all transforms were compiled
        for transform_id in transforms:
            assert transform_id in engine.processor.transform_processor.transform_tables
    
    def test_pattern_matching_sequential(self):
        """Test pattern matching in sequential mode."""
        engine = SimdPatternEngine()
        engine.compile_patterns({"test": "hello"})
        
        texts = ["hello world", "hi there", "hello again"]
        results = engine.match_patterns(texts, ["test"], parallel=False)
        
        assert "test" in results
        assert len(results["test"]) == 3  # Results for 3 texts
        assert len(results["test"][0]) == 1  # First text has 1 match
        assert len(results["test"][1]) == 0  # Second text has no match
        assert len(results["test"][2]) == 1  # Third text has 1 match
    
    def test_pattern_matching_parallel(self):
        """Test pattern matching in parallel mode."""
        engine = SimdPatternEngine()
        engine.compile_patterns({
            "pattern1": "test",
            "pattern2": "example"
        })
        
        # Create large dataset to trigger parallel processing
        texts = ["test example text"] * 200
        results = engine.match_patterns(texts, ["pattern1", "pattern2"], parallel=True)
        
        assert "pattern1" in results
        assert "pattern2" in results
        assert len(results["pattern1"]) > 0
        assert len(results["pattern2"]) > 0
    
    def test_text_transformation(self):
        """Test text transformation operations."""
        engine = SimdPatternEngine()
        engine.compile_transforms({
            "upper": {chr(i): chr(i).upper() for i in range(97, 123)}
        })
        
        texts = ["hello world", "python simd"]
        results = engine.transform_texts(texts, ["upper"], parallel=False)
        
        assert len(results) == 2
        assert results[0] == "HELLO WORLD"
        assert results[1] == "PYTHON SIMD"
    
    def test_batch_replacement(self):
        """Test batch replacement operations."""
        engine = SimdPatternEngine()
        
        texts = ["foo bar foo", "bar foo bar"]
        replacements = [("foo", "baz"), ("bar", "qux")]
        
        results = engine.replace_batch(texts, replacements, parallel=False)
        
        assert len(results) == 2
        assert results[0] == "baz qux baz"
        assert results[1] == "qux baz qux"
    
    def test_processing_pipeline(self):
        """Test processing pipeline with multiple operations."""
        engine = SimdPatternEngine()
        
        # Setup
        engine.compile_patterns({"email": "@"})
        engine.compile_transforms({
            "upper": {chr(i): chr(i).upper() for i in range(97, 123)}
        })
        
        # Define pipeline
        pipeline = [
            {'type': 'pattern_match', 'pattern_id': 'email'},
            {'type': 'transform', 'transform_id': 'upper'},
            {'type': 'replace', 'old': 'EXAMPLE', 'new': 'TEST'}
        ]
        
        texts = ["contact: user@example.com", "email: admin@example.org"]
        final_texts, metrics = engine.process_pipeline(texts, pipeline, batch_size=10)
        
        assert len(final_texts) == 2
        assert "TEST" in final_texts[0]
        assert metrics.total_batches > 0
        assert metrics.successful_batches > 0
    
    def test_benchmark_functionality(self):
        """Test benchmarking functionality."""
        engine = SimdPatternEngine()
        engine.compile_patterns({"test": "hello"})
        
        sample_texts = ["hello world"] * 50
        operations = [{'type': 'pattern_match', 'pattern_id': 'test'}]
        
        benchmark = engine.benchmark(sample_texts, operations)
        
        assert "sequential_time" in benchmark
        assert "parallel_time" in benchmark
        assert "speedup" in benchmark
        assert "efficiency" in benchmark
        assert benchmark["texts_processed"] == 50
        assert benchmark["speedup"] > 0
    
    def test_auto_optimization(self):
        """Test automatic pipeline optimization."""
        engine = SimdPatternEngine(auto_optimize=True)
        
        pipeline = [
            {'type': 'replace', 'old': 'test', 'new': 'example'}
        ]
        
        # Run pipeline multiple times to trigger optimization
        texts = ["test text"] * 10
        for _ in range(110):  # Above optimization threshold
            engine.process_pipeline(texts, pipeline)
        
        # Check that optimization data was collected
        pipeline_key = engine._pipeline_key(pipeline)
        assert pipeline_key in engine.operation_times
        assert len(engine.operation_times[pipeline_key]) <= 50  # Should be trimmed
    
    def test_engine_shutdown(self):
        """Test engine shutdown."""
        engine = SimdPatternEngine()
        
        # Use engine
        engine.compile_patterns({"test": "hello"})
        texts = ["hello world"]
        engine.match_patterns(texts, ["test"])
        
        # Shutdown
        engine.shutdown()
        assert engine.processor._shutdown


class TestSimdUtilityFunctions:
    """Test cases for SIMD utility functions."""
    
    def test_simd_count_chars(self):
        """Test SIMD character counting."""
        text = "hello world"
        text_array = np.frombuffer(text.encode('utf-8'), dtype=np.uint8)
        
        # Count 'l' characters
        count = simd_count_chars(text_array, ord('l'))
        assert count == 3
        
        # Count 'x' characters (not present)
        count = simd_count_chars(text_array, ord('x'))
        assert count == 0
    
    def test_simd_find_all(self):
        """Test SIMD find all positions."""
        text = "hello world"
        text_array = np.frombuffer(text.encode('utf-8'), dtype=np.uint8)
        
        # Find all 'o' positions
        positions = simd_find_all(text_array, ord('o'))
        assert len(positions) == 2
        assert positions[0] == 4  # First 'o' in "hello"
        assert positions[1] == 7  # Second 'o' in "world"
    
    def test_simd_case_conversion(self):
        """Test SIMD case conversion functions."""
        # Test uppercase conversion
        text = "hello world"
        text_array = np.frombuffer(text.encode('utf-8'), dtype=np.uint8)
        upper_array = simd_to_upper(text_array)
        upper_text = upper_array.tobytes().decode('utf-8')
        assert upper_text == "HELLO WORLD"
        
        # Test lowercase conversion
        text = "HELLO WORLD"
        text_array = np.frombuffer(text.encode('utf-8'), dtype=np.uint8)
        lower_array = simd_to_lower(text_array)
        lower_text = lower_array.tobytes().decode('utf-8')
        assert lower_text == "hello world"
    
    def test_mixed_case_conversion(self):
        """Test case conversion with mixed input."""
        text = "HeLLo WoRLd 123!"
        text_array = np.frombuffer(text.encode('utf-8'), dtype=np.uint8)
        
        # Convert to upper
        upper_array = simd_to_upper(text_array)
        upper_text = upper_array.tobytes().decode('utf-8')
        assert upper_text == "HELLO WORLD 123!"
        
        # Convert to lower
        lower_array = simd_to_lower(text_array)
        lower_text = lower_array.tobytes().decode('utf-8')
        assert lower_text == "heLLo world 123!"  # Only uppercase letters affected


class TestGlobalEngineManagement:
    """Test cases for global engine management."""
    
    def test_get_simd_engine(self):
        """Test getting global SIMD engine."""
        engine1 = get_simd_engine()
        engine2 = get_simd_engine()
        
        # Should return same instance
        assert engine1 is engine2
        assert isinstance(engine1, SimdPatternEngine)
    
    def test_shutdown_simd_engine(self):
        """Test shutting down global SIMD engine."""
        # Get engine
        engine = get_simd_engine()
        assert engine is not None
        
        # Shutdown
        shutdown_simd_engine()
        
        # Getting engine again should create new instance
        new_engine = get_simd_engine()
        assert new_engine is not engine


class TestThreadSafety:
    """Test cases for thread safety."""
    
    def test_concurrent_pattern_matching(self):
        """Test concurrent pattern matching operations."""
        engine = SimdPatternEngine()
        engine.compile_patterns({
            "pattern1": "test",
            "pattern2": "example"
        })
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                texts = [f"test example {worker_id}"] * 10
                result = engine.match_patterns(texts, ["pattern1", "pattern2"])
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Run concurrent workers
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(results) == 10
    
    def test_concurrent_transformations(self):
        """Test concurrent transformation operations."""
        engine = SimdPatternEngine()
        engine.compile_transforms({
            "upper": {chr(i): chr(i).upper() for i in range(97, 123)}
        })
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                texts = [f"hello world {worker_id}"] * 5
                result = engine.transform_texts(texts, ["upper"])
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Run concurrent workers
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(results) == 5
        assert all(all("HELLO WORLD" in text for text in result) for result in results)


class TestPerformanceCharacteristics:
    """Test performance characteristics and optimization."""
    
    def test_simd_speedup_verification(self):
        """Verify SIMD provides speedup for suitable workloads."""
        engine = SimdPatternEngine()
        engine.compile_patterns({"test": "pattern"})
        
        # Create large dataset
        texts = ["This is a test pattern for SIMD processing"] * 1000
        operations = [{'type': 'pattern_match', 'pattern_id': 'test'}]
        
        benchmark = engine.benchmark(texts, operations)
        
        # SIMD should provide speedup for large datasets
        assert benchmark["speedup"] > 1.0
        assert benchmark["parallel_time"] < benchmark["sequential_time"]
    
    def test_small_dataset_handling(self):
        """Test that small datasets don't trigger parallel processing."""
        engine = SimdPatternEngine()
        engine.compile_patterns({"test": "hello"})
        
        # Small dataset
        texts = ["hello world"] * 5
        results = engine.match_patterns(texts, ["test"], parallel=True)
        
        # Should still work correctly even if processed sequentially
        assert "test" in results
        assert len(results["test"]) == 5
    
    def test_memory_efficiency(self):
        """Test memory efficiency of SIMD operations."""
        processor = ParallelBatchProcessor()
        
        # Process large batch
        texts = ["Large text content " * 100] * 100
        operations = [{'type': 'replace', 'old': 'Large', 'new': 'Small'}]
        
        initial_metrics = processor.get_metrics()
        initial_memory = initial_metrics.memory_usage_mb
        
        # Process data
        processor.process_parallel(texts, operations, batch_size=50)
        
        # Check memory usage didn't explode
        final_metrics = processor.get_metrics()
        memory_increase = final_metrics.memory_usage_mb - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_input_handling(self):
        """Test handling of empty inputs."""
        engine = SimdPatternEngine()
        
        # Empty text list
        results = engine.match_patterns([], ["test"], parallel=False)
        assert results == {}
        
        # Empty pattern list
        results = engine.match_patterns(["test"], [], parallel=False)
        assert results == {}
    
    def test_very_long_patterns(self):
        """Test handling of very long patterns."""
        matcher = SimdPatternMatcher()
        
        # Create very long pattern
        long_pattern = "a" * 1000
        matcher.compile_pattern("long", long_pattern)
        
        # Test with text containing the pattern
        text = "prefix " + long_pattern + " suffix"
        results = matcher.search_batch([text], "long")
        
        assert len(results) == 1
        assert len(results[0]) == 1  # Should find the pattern
    
    def test_special_characters(self):
        """Test handling of special characters."""
        processor = SimdTransformProcessor()
        
        # Test with various special characters
        texts = ["Special: \n\t\r", "Unicode: 🎉🎊", "Null: \x00"]
        results = processor.replace_batch(texts, ":", " -")
        
        assert results[0] == "Special - \n\t\r"
        assert results[1] == "Unicode - 🎉🎊"
        assert results[2] == "Null - \x00"
    
    def test_pattern_at_boundaries(self):
        """Test pattern matching at text boundaries."""
        matcher = SimdPatternMatcher()
        matcher.compile_pattern("boundary", "test")
        
        texts = [
            "test at start",
            "at end test",
            "test",  # Exact match
            "in test middle"
        ]
        
        results = matcher.search_batch(texts, "boundary")
        
        assert len(results[0]) == 1  # Start
        assert results[0][0] == 0
        assert len(results[1]) == 1  # End
        assert results[1][0] == 7
        assert len(results[2]) == 1  # Exact
        assert results[2][0] == 0
        assert len(results[3]) == 1  # Middle
        assert results[3][0] == 3


class TestIntegration:
    """Integration tests with real-world scenarios."""
    
    def test_email_extraction_pipeline(self):
        """Test email extraction pipeline."""
        engine = SimdPatternEngine()
        
        # Compile email-related patterns
        engine.compile_patterns({
            "at_symbol": "@",
            "dot": "."
        })
        
        texts = [
            "Contact us at info@example.com for more information",
            "Send emails to support@test.org or admin@demo.net",
            "No email here",
            "Multiple: user1@site.com, user2@site.com"
        ]
        
        # Find @ symbols
        results = engine.match_patterns(texts, ["at_symbol", "dot"], parallel=False)
        
        # Verify @ symbols found in texts with emails
        assert len(results["at_symbol"][0]) == 1  # First text
        assert len(results["at_symbol"][1]) == 2  # Second text
        assert len(results["at_symbol"][2]) == 0  # Third text
        assert len(results["at_symbol"][3]) == 2  # Fourth text
    
    def test_log_processing_pipeline(self):
        """Test log processing pipeline."""
        engine = SimdPatternEngine()
        
        # Setup for log processing
        engine.compile_patterns({
            "error": "ERROR",
            "warning": "WARN",
            "info": "INFO"
        })
        
        engine.compile_transforms({
            "lowercase": {chr(i): chr(i).lower() for i in range(65, 91)}
        })
        
        logs = [
            "[2024-01-01] ERROR: Failed to connect",
            "[2024-01-01] INFO: Server started",
            "[2024-01-01] WARN: Memory usage high",
            "[2024-01-01] ERROR: Connection timeout"
        ]
        
        # Process pipeline
        pipeline = [
            {'type': 'pattern_match', 'pattern_id': 'error'},
            {'type': 'pattern_match', 'pattern_id': 'warning'},
            {'type': 'transform', 'transform_id': 'lowercase'}
        ]
        
        final_logs, metrics = engine.process_pipeline(logs, pipeline)
        
        assert len(final_logs) == 4
        assert all(log.islower() for log in final_logs)
        assert metrics.patterns_matched > 0
    
    def test_text_sanitization_pipeline(self):
        """Test text sanitization pipeline."""
        engine = SimdPatternEngine()
        
        # Setup sanitization rules
        texts = [
            "Remove <script>alert('xss')</script> tags",
            "Clean up <b>HTML</b> content",
            "Normal text without tags"
        ]
        
        # Multi-step sanitization
        replacements = [
            ("<script>", "[removed]"),
            ("</script>", "[/removed]"),
            ("<b>", ""),
            ("</b>", "")
        ]
        
        results = engine.replace_batch(texts, replacements, parallel=False)
        
        assert "[removed]" in results[0]
        assert "<b>" not in results[1]
        assert results[2] == texts[2]  # Unchanged


def test_cleanup():
    """Cleanup after all tests."""
    # Ensure global engine is shutdown
    shutdown_simd_engine()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])