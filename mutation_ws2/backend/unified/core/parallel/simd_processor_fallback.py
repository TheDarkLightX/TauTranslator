"""
SIMD Processor Fallback Implementation

Provides the same interface as simd_processor.py but without numba dependency.
Used for testing and environments where numba is not available.

Author: DarkLightX / Dana Edwards
"""

import numpy as np
import multiprocessing as mp
from multiprocessing import Pool, Queue, Manager, Process
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import threading
import logging
import time
import os
import queue
from typing import List, Dict, Optional, Tuple, Any, Callable, Union, Iterator
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import psutil
from collections import defaultdict, deque
import functools
import pickle
import hashlib


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    batch_id: int
    start_time: float
    end_time: float
    input_size: int
    output_size: int
    patterns_matched: int
    transformations_applied: int
    processing_time: float
    success: bool
    error: Optional[str] = None
    results: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def throughput(self) -> float:
        """Calculate throughput in MB/s."""
        if self.processing_time > 0:
            return (self.input_size / (1024 * 1024)) / self.processing_time
        return 0.0
    
    @property
    def patterns_per_second(self) -> float:
        """Calculate patterns matched per second."""
        if self.processing_time > 0:
            return self.patterns_matched / self.processing_time
        return 0.0


@dataclass
class ProcessingMetrics:
    """Metrics for parallel processing performance."""
    total_batches: int = 0
    successful_batches: int = 0
    failed_batches: int = 0
    total_input_size: int = 0
    total_output_size: int = 0
    total_patterns_matched: int = 0
    total_transformations: int = 0
    total_processing_time: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    thread_count: int = 0
    process_count: int = 0
    
    @property
    def average_throughput(self) -> float:
        """Average throughput in MB/s."""
        if self.total_processing_time > 0:
            return (self.total_input_size / (1024 * 1024)) / self.total_processing_time
        return 0.0
    
    @property
    def success_rate(self) -> float:
        """Batch processing success rate."""
        if self.total_batches > 0:
            return (self.successful_batches / self.total_batches) * 100
        return 0.0


class SimdPatternMatcher:
    """
    Pattern matching using numpy for vectorization (fallback version).
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compiled_patterns: Dict[str, np.ndarray] = {}
        self._pattern_cache: Dict[str, Any] = {}
        
    def compile_pattern(self, pattern_id: str, pattern: str) -> None:
        """Compile pattern for vectorized matching."""
        pattern_bytes = np.frombuffer(pattern.encode('utf-8'), dtype=np.uint8)
        self.compiled_patterns[pattern_id] = pattern_bytes
        
        self._pattern_cache[pattern_id] = {
            'length': len(pattern),
            'hash': hashlib.md5(pattern.encode()).hexdigest(),
            'pattern': pattern
        }
    
    def _vectorized_search(self, text_array: np.ndarray, pattern_array: np.ndarray) -> np.ndarray:
        """
        Vectorized pattern search (fallback without numba).
        """
        text_len = len(text_array)
        pattern_len = len(pattern_array)
        
        if pattern_len > text_len:
            return np.array([], dtype=np.int32)
        
        matches = []
        
        # Simple sliding window search
        for i in range(text_len - pattern_len + 1):
            if np.array_equal(text_array[i:i + pattern_len], pattern_array):
                matches.append(i)
        
        return np.array(matches, dtype=np.int32)
    
    def search_batch(self, texts: List[str], pattern_id: str) -> List[List[int]]:
        """Search for pattern in batch of texts."""
        if pattern_id not in self.compiled_patterns:
            return [[] for _ in texts]
        
        pattern_array = self.compiled_patterns[pattern_id]
        results = []
        
        for text in texts:
            text_bytes = np.frombuffer(text.encode('utf-8'), dtype=np.uint8)
            matches = self._vectorized_search(text_bytes, pattern_array)
            results.append(matches.tolist())
        
        return results
    
    def multi_pattern_search(self, text: str, pattern_ids: List[str]) -> Dict[str, List[int]]:
        """Search for multiple patterns in single text."""
        text_bytes = np.frombuffer(text.encode('utf-8'), dtype=np.uint8)
        results = {}
        
        for pattern_id in pattern_ids:
            if pattern_id in self.compiled_patterns:
                pattern_array = self.compiled_patterns[pattern_id]
                matches = self._vectorized_search(text_bytes, pattern_array)
                results[pattern_id] = matches.tolist()
            else:
                results[pattern_id] = []
        
        return results


class SimdTransformProcessor:
    """
    Text transformation processor (fallback version).
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.transform_tables: Dict[str, np.ndarray] = {}
        
    def create_transform_table(self, table_id: str, mappings: Dict[str, str]) -> None:
        """Create vectorized transformation table."""
        table = np.arange(256, dtype=np.uint8)
        
        for src, dst in mappings.items():
            if len(src) == 1 and len(dst) == 1:
                src_byte = ord(src)
                dst_byte = ord(dst)
                table[src_byte] = dst_byte
        
        self.transform_tables[table_id] = table
    
    def _apply_transform(self, text_array: np.ndarray, table: np.ndarray) -> np.ndarray:
        """Apply transformation using lookup table."""
        return table[text_array]
    
    def transform_batch(self, texts: List[str], table_id: str) -> List[str]:
        """Apply transformation to batch of texts."""
        if table_id not in self.transform_tables:
            return texts
        
        table = self.transform_tables[table_id]
        results = []
        
        for text in texts:
            text_bytes = np.frombuffer(text.encode('utf-8'), dtype=np.uint8)
            transformed = self._apply_transform(text_bytes, table)
            results.append(transformed.tobytes().decode('utf-8', errors='ignore'))
        
        return results
    
    def _parallel_replace(self, text_array: np.ndarray, old_pattern: np.ndarray, 
                         new_pattern: np.ndarray) -> np.ndarray:
        """Pattern replacement (fallback version)."""
        text_str = text_array.tobytes().decode('utf-8', errors='ignore')
        old_str = old_pattern.tobytes().decode('utf-8', errors='ignore')
        new_str = new_pattern.tobytes().decode('utf-8', errors='ignore')
        
        result_str = text_str.replace(old_str, new_str)
        return np.frombuffer(result_str.encode('utf-8'), dtype=np.uint8)
    
    def replace_batch(self, texts: List[str], old: str, new: str) -> List[str]:
        """Batch replace operation."""
        old_bytes = np.frombuffer(old.encode('utf-8'), dtype=np.uint8)
        new_bytes = np.frombuffer(new.encode('utf-8'), dtype=np.uint8)
        results = []
        
        for text in texts:
            text_bytes = np.frombuffer(text.encode('utf-8'), dtype=np.uint8)
            replaced = self._parallel_replace(text_bytes, old_bytes, new_bytes)
            results.append(replaced.tobytes().decode('utf-8', errors='ignore'))
        
        return results


class ParallelBatchProcessor:
    """
    Parallel batch processor (fallback version).
    """
    
    def __init__(self, num_workers: Optional[int] = None, 
                 batch_size: int = 1000,
                 use_processes: bool = True):
        self.num_workers = num_workers or mp.cpu_count()
        self.batch_size = batch_size
        self.use_processes = use_processes
        
        self.pattern_matcher = SimdPatternMatcher()
        self.transform_processor = SimdTransformProcessor()
        
        self.process = psutil.Process(os.getpid())
        self.metrics = ProcessingMetrics()
        
        self.manager = Manager()
        self.work_queue = self.manager.Queue()
        self.result_queue = self.manager.Queue()
        self.active_workers = 0
        
        self._lock = threading.RLock()
        self._shutdown = False
        
        self.logger = logging.getLogger(__name__)
    
    def add_pattern(self, pattern_id: str, pattern: str) -> None:
        """Add pattern for matching."""
        self.pattern_matcher.compile_pattern(pattern_id, pattern)
    
    def add_transform(self, transform_id: str, mappings: Dict[str, str]) -> None:
        """Add transformation mapping."""
        self.transform_processor.create_transform_table(transform_id, mappings)
    
    def process_batch(self, texts: List[str], operations: List[Dict[str, Any]]) -> BatchResult:
        """Process single batch with specified operations."""
        batch_id = hash(time.time())
        start_time = time.time()
        
        try:
            results = []
            patterns_matched = 0
            transformations_applied = 0
            
            current_texts = texts.copy()
            
            for operation in operations:
                op_type = operation.get('type')
                
                if op_type == 'pattern_match':
                    pattern_id = operation.get('pattern_id')
                    matches = self.pattern_matcher.search_batch(current_texts, pattern_id)
                    results.append({
                        'operation': 'pattern_match',
                        'pattern_id': pattern_id,
                        'matches': matches
                    })
                    patterns_matched += sum(len(m) for m in matches)
                
                elif op_type == 'transform':
                    transform_id = operation.get('transform_id')
                    current_texts = self.transform_processor.transform_batch(
                        current_texts, transform_id
                    )
                    results.append({
                        'operation': 'transform',
                        'transform_id': transform_id
                    })
                    transformations_applied += len(current_texts)
                
                elif op_type == 'replace':
                    old = operation.get('old', '')
                    new = operation.get('new', '')
                    current_texts = self.transform_processor.replace_batch(
                        current_texts, old, new
                    )
                    results.append({
                        'operation': 'replace',
                        'old': old,
                        'new': new
                    })
                    transformations_applied += len(current_texts)
            
            input_size = sum(len(t.encode('utf-8')) for t in texts)
            output_size = sum(len(t.encode('utf-8')) for t in current_texts)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            return BatchResult(
                batch_id=batch_id,
                start_time=start_time,
                end_time=end_time,
                input_size=input_size,
                output_size=output_size,
                patterns_matched=patterns_matched,
                transformations_applied=transformations_applied,
                processing_time=processing_time,
                success=True,
                results=results,
                metadata={
                    'final_texts': current_texts,
                    'operation_count': len(operations)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Batch processing error: {e}")
            return BatchResult(
                batch_id=batch_id,
                start_time=start_time,
                end_time=time.time(),
                input_size=sum(len(t.encode('utf-8')) for t in texts),
                output_size=0,
                patterns_matched=0,
                transformations_applied=0,
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def process_parallel(self, texts: List[str], operations: List[Dict[str, Any]], 
                        batch_size: Optional[int] = None) -> List[BatchResult]:
        """Process texts in parallel with automatic batching."""
        if batch_size is None:
            batch_size = self.batch_size
        
        batches = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batches.append(batch)
        
        self.logger.info(f"Processing {len(texts)} texts in {len(batches)} batches")
        
        with self._lock:
            self.metrics.total_batches += len(batches)
            self.metrics.cpu_usage_percent = self.process.cpu_percent()
            self.metrics.memory_usage_mb = self.process.memory_info().rss / (1024 * 1024)
        
        if self.use_processes:
            return self._process_with_multiprocessing(batches, operations)
        else:
            return self._process_with_threading(batches, operations)
    
    def _process_with_multiprocessing(self, batches: List[List[str]], 
                                    operations: List[Dict[str, Any]]) -> List[BatchResult]:
        """Process using multiprocessing."""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            for batch in batches:
                future = executor.submit(self.process_batch, batch, operations)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    
                    with self._lock:
                        if result.success:
                            self.metrics.successful_batches += 1
                        else:
                            self.metrics.failed_batches += 1
                        
                        self.metrics.total_input_size += result.input_size
                        self.metrics.total_output_size += result.output_size
                        self.metrics.total_patterns_matched += result.patterns_matched
                        self.metrics.total_transformations += result.transformations_applied
                        self.metrics.total_processing_time += result.processing_time
                        
                except Exception as e:
                    self.logger.error(f"Failed to process batch: {e}")
                    with self._lock:
                        self.metrics.failed_batches += 1
        
        return results
    
    def _process_with_threading(self, batches: List[List[str]], 
                               operations: List[Dict[str, Any]]) -> List[BatchResult]:
        """Process using threading."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            for batch in batches:
                future = executor.submit(self.process_batch, batch, operations)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    
                    with self._lock:
                        if result.success:
                            self.metrics.successful_batches += 1
                        else:
                            self.metrics.failed_batches += 1
                        
                        self.metrics.total_input_size += result.input_size
                        self.metrics.total_output_size += result.output_size
                        self.metrics.total_patterns_matched += result.patterns_matched
                        self.metrics.total_transformations += result.transformations_applied
                        self.metrics.total_processing_time += result.processing_time
                        
                except Exception as e:
                    self.logger.error(f"Failed to process batch: {e}")
                    with self._lock:
                        self.metrics.failed_batches += 1
        
        return results
    
    def get_metrics(self) -> ProcessingMetrics:
        """Get current processing metrics."""
        with self._lock:
            self.metrics.cpu_usage_percent = self.process.cpu_percent()
            self.metrics.memory_usage_mb = self.process.memory_info().rss / (1024 * 1024)
            self.metrics.thread_count = threading.active_count()
            self.metrics.process_count = len(mp.active_children())
            
            return self.metrics
    
    def reset_metrics(self) -> None:
        """Reset processing metrics."""
        with self._lock:
            self.metrics = ProcessingMetrics()
    
    def shutdown(self) -> None:
        """Shutdown processor and clean up resources."""
        self._shutdown = True
        
        for _ in range(self.num_workers):
            self.work_queue.put(None)
        
        self.logger.info("Parallel processor shutdown complete")


class SimdPatternEngine:
    """
    High-level SIMD pattern processing engine (fallback version).
    """
    
    def __init__(self, auto_optimize: bool = True):
        self.processor = ParallelBatchProcessor()
        self.auto_optimize = auto_optimize
        
        self.operation_times: Dict[str, List[float]] = defaultdict(list)
        self.optimization_threshold = 100
        
        self.logger = logging.getLogger(__name__)
    
    def compile_patterns(self, patterns: Dict[str, str]) -> None:
        """Compile multiple patterns for SIMD processing."""
        for pattern_id, pattern in patterns.items():
            self.processor.add_pattern(pattern_id, pattern)
        
        self.logger.info(f"Compiled {len(patterns)} patterns for SIMD processing")
    
    def compile_transforms(self, transforms: Dict[str, Dict[str, str]]) -> None:
        """Compile transformation tables."""
        for transform_id, mappings in transforms.items():
            self.processor.add_transform(transform_id, mappings)
        
        self.logger.info(f"Compiled {len(transforms)} transform tables")
    
    def match_patterns(self, texts: List[str], pattern_ids: List[str], 
                      parallel: bool = True) -> Dict[str, List[List[int]]]:
        """Match multiple patterns across multiple texts."""
        operations = [
            {'type': 'pattern_match', 'pattern_id': pid}
            for pid in pattern_ids
        ]
        
        if parallel and len(texts) > 100:
            results = self.processor.process_parallel(texts, operations)
            
            pattern_matches = defaultdict(list)
            for result in results:
                if result.success:
                    for op_result in result.results:
                        if op_result['operation'] == 'pattern_match':
                            pattern_id = op_result['pattern_id']
                            pattern_matches[pattern_id].extend(op_result['matches'])
            
            return dict(pattern_matches)
        else:
            pattern_matches = {}
            for pattern_id in pattern_ids:
                matches = self.processor.pattern_matcher.search_batch(texts, pattern_id)
                pattern_matches[pattern_id] = matches
            
            return pattern_matches
    
    def transform_texts(self, texts: List[str], transform_ids: List[str],
                       parallel: bool = True) -> List[str]:
        """Apply multiple transformations to texts."""
        operations = [
            {'type': 'transform', 'transform_id': tid}
            for tid in transform_ids
        ]
        
        if parallel and len(texts) > 100:
            results = self.processor.process_parallel(texts, operations)
            
            final_texts = []
            for result in results:
                if result.success and 'final_texts' in result.metadata:
                    final_texts.extend(result.metadata['final_texts'])
            
            return final_texts
        else:
            current_texts = texts
            for transform_id in transform_ids:
                current_texts = self.processor.transform_processor.transform_batch(
                    current_texts, transform_id
                )
            return current_texts
    
    def replace_batch(self, texts: List[str], replacements: List[Tuple[str, str]],
                     parallel: bool = True) -> List[str]:
        """Apply multiple replacements to texts."""
        operations = [
            {'type': 'replace', 'old': old, 'new': new}
            for old, new in replacements
        ]
        
        if parallel and len(texts) > 100:
            results = self.processor.process_parallel(texts, operations)
            
            final_texts = []
            for result in results:
                if result.success and 'final_texts' in result.metadata:
                    final_texts.extend(result.metadata['final_texts'])
            
            return final_texts
        else:
            current_texts = texts
            for old, new in replacements:
                current_texts = self.processor.transform_processor.replace_batch(
                    current_texts, old, new
                )
            return current_texts
    
    def process_pipeline(self, texts: List[str], pipeline: List[Dict[str, Any]],
                        batch_size: int = 1000) -> Tuple[List[str], ProcessingMetrics]:
        """Process texts through a pipeline of operations."""
        start_time = time.time()
        
        self.processor.reset_metrics()
        
        results = self.processor.process_parallel(texts, pipeline, batch_size)
        
        final_texts = []
        for result in results:
            if result.success and 'final_texts' in result.metadata:
                final_texts.extend(result.metadata['final_texts'])
        
        metrics = self.processor.get_metrics()
        
        if self.auto_optimize:
            pipeline_time = time.time() - start_time
            pipeline_key = self._pipeline_key(pipeline)
            self.operation_times[pipeline_key].append(pipeline_time)
            
            if len(self.operation_times[pipeline_key]) >= self.optimization_threshold:
                self._optimize_pipeline(pipeline_key)
        
        return final_texts, metrics
    
    def benchmark(self, sample_texts: List[str], operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Benchmark SIMD performance vs sequential processing."""
        seq_start = time.time()
        seq_results = []
        
        for text in sample_texts:
            result = self.processor.process_batch([text], operations)
            seq_results.append(result)
        
        seq_time = time.time() - seq_start
        
        self.processor.reset_metrics()
        par_start = time.time()
        par_results = self.processor.process_parallel(sample_texts, operations)
        par_time = time.time() - par_start
        
        speedup = seq_time / par_time if par_time > 0 else 0
        
        return {
            'sequential_time': seq_time,
            'parallel_time': par_time,
            'speedup': speedup,
            'efficiency': speedup / self.processor.num_workers,
            'texts_processed': len(sample_texts),
            'operations_count': len(operations),
            'parallel_metrics': self.processor.get_metrics()
        }
    
    def _pipeline_key(self, pipeline: List[Dict[str, Any]]) -> str:
        """Generate unique key for pipeline."""
        return hashlib.md5(str(pipeline).encode()).hexdigest()
    
    def _optimize_pipeline(self, pipeline_key: str) -> None:
        """Optimize pipeline based on performance data."""
        times = self.operation_times[pipeline_key]
        avg_time = sum(times) / len(times)
        
        self.logger.info(f"Optimizing pipeline {pipeline_key}: avg time {avg_time:.3f}s")
        
        self.operation_times[pipeline_key] = times[-50:]
    
    def shutdown(self) -> None:
        """Shutdown the SIMD engine."""
        self.processor.shutdown()


# Utility functions (fallback versions)
def simd_count_chars(text_array: np.ndarray, char: np.uint8) -> int:
    """Count occurrences of character."""
    return np.sum(text_array == char)


def simd_find_all(text_array: np.ndarray, char: np.uint8) -> np.ndarray:
    """Find all positions of character."""
    return np.where(text_array == char)[0].astype(np.int32)


def simd_to_upper(text_array: np.ndarray) -> np.ndarray:
    """Convert to uppercase."""
    result = text_array.copy()
    mask = (text_array >= 97) & (text_array <= 122)
    result[mask] -= 32
    return result


def simd_to_lower(text_array: np.ndarray) -> np.ndarray:
    """Convert to lowercase."""
    result = text_array.copy()
    mask = (text_array >= 65) & (text_array <= 90)
    result[mask] += 32
    return result


# Global engine management
_global_simd_engine: Optional[SimdPatternEngine] = None


def get_simd_engine() -> SimdPatternEngine:
    """Get or create global SIMD engine."""
    global _global_simd_engine
    if _global_simd_engine is None:
        _global_simd_engine = SimdPatternEngine()
    return _global_simd_engine


def shutdown_simd_engine() -> None:
    """Shutdown global SIMD engine."""
    global _global_simd_engine
    if _global_simd_engine is not None:
        _global_simd_engine.shutdown()
        _global_simd_engine = None