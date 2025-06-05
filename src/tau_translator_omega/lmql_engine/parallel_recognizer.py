"""
Parallel Pattern Recognition System
==================================

Implements parallel pattern matching for improved performance
on multi-core systems.

Author: DarkLightX / Dana Edwards
"""

import concurrent.futures
import multiprocessing
from typing import List, Tuple, Dict, Optional, Any, Callable
from dataclasses import dataclass
import logging
from functools import partial

from .recognizers import (
    PatternRecognizer, RecognitionResult, RecognizerFactory,
    BinaryArithmeticRecognizer, StreamRecognizer, LogicGateRecognizer,
    ConsensusRecognizer, TemporalRecognizer
)

logger = logging.getLogger(__name__)


@dataclass
class ParallelRecognitionResult:
    """Result from parallel pattern recognition."""
    recognizer_type: str
    result: RecognitionResult
    execution_time: float


class ParallelPatternMatcher:
    """
    Parallel pattern matching system for high-performance recognition.
    
    Features:
    - Concurrent pattern matching across multiple recognizers
    - Thread pool management for CPU-bound tasks
    - Result aggregation and ranking
    - Performance monitoring
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize parallel pattern matcher.
        
        Args:
            max_workers: Maximum number of worker threads (defaults to CPU count)
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.recognizers = self._initialize_recognizers()
        self._recognition_count = 0
        self._total_time = 0.0
        
        # Thread pool executor for parallel matching
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="PatternMatcher"
        )
    
    def _initialize_recognizers(self) -> Dict[str, PatternRecognizer]:
        """Initialize all available recognizers."""
        return {
            'arithmetic': BinaryArithmeticRecognizer(),
            'stream': StreamRecognizer(),
            'logic_gate': LogicGateRecognizer(),
            'consensus': ConsensusRecognizer(),
            'temporal': TemporalRecognizer(),
        }
    
    def recognize_parallel(self, text: str) -> List[ParallelRecognitionResult]:
        """
        Recognize patterns in parallel across all recognizers.
        
        Args:
            text: Text to recognize patterns in
            
        Returns:
            List of recognition results sorted by confidence
        """
        import time
        start_time = time.time()
        self._recognition_count += 1
        
        # Create recognition tasks
        futures = {}
        for recognizer_type, recognizer in self.recognizers.items():
            future = self.executor.submit(
                self._recognize_with_timing,
                recognizer,
                text,
                recognizer_type
            )
            futures[future] = recognizer_type
        
        # Collect results as they complete
        results = []
        for future in concurrent.futures.as_completed(futures):
            recognizer_type = futures[future]
            try:
                result, exec_time = future.result(timeout=1.0)
                if result.recognized:
                    results.append(ParallelRecognitionResult(
                        recognizer_type=recognizer_type,
                        result=result,
                        execution_time=exec_time
                    ))
            except Exception as e:
                logger.error(f"Recognition failed for {recognizer_type}: {e}")
        
        # Sort by confidence (highest first)
        results.sort(key=lambda r: r.result.confidence, reverse=True)
        
        self._total_time += time.time() - start_time
        return results
    
    def _recognize_with_timing(self, recognizer: PatternRecognizer, 
                              text: str, recognizer_type: str) -> Tuple[RecognitionResult, float]:
        """
        Recognize pattern with execution timing.
        
        Args:
            recognizer: Pattern recognizer instance
            text: Text to recognize
            recognizer_type: Type name for logging
            
        Returns:
            Tuple of (result, execution_time)
        """
        import time
        start = time.time()
        result = recognizer.recognize(text)
        exec_time = time.time() - start
        
        if result.recognized:
            logger.debug(f"{recognizer_type} recognized pattern in {exec_time:.4f}s")
        
        return result, exec_time
    
    def recognize_best(self, text: str) -> Optional[ParallelRecognitionResult]:
        """
        Get the best recognition result (highest confidence).
        
        Args:
            text: Text to recognize
            
        Returns:
            Best recognition result or None if no patterns matched
        """
        results = self.recognize_parallel(text)
        return results[0] if results else None
    
    def batch_recognize(self, texts: List[str], 
                       callback: Optional[Callable[[str, List[ParallelRecognitionResult]], None]] = None
                       ) -> Dict[str, List[ParallelRecognitionResult]]:
        """
        Recognize patterns in multiple texts concurrently.
        
        Args:
            texts: List of texts to process
            callback: Optional callback for progress updates
            
        Returns:
            Dictionary mapping text to recognition results
        """
        import time
        start_time = time.time()
        
        # Create futures for batch processing
        future_to_text = {
            self.executor.submit(self.recognize_parallel, text): text
            for text in texts
        }
        
        results = {}
        completed = 0
        
        for future in concurrent.futures.as_completed(future_to_text):
            text = future_to_text[future]
            try:
                recognition_results = future.result()
                results[text] = recognition_results
                completed += 1
                
                if callback:
                    callback(text, recognition_results)
                
                logger.debug(f"Batch progress: {completed}/{len(texts)}")
                
            except Exception as e:
                logger.error(f"Batch recognition failed for '{text}': {e}")
                results[text] = []
        
        batch_time = time.time() - start_time
        logger.info(f"Batch recognition completed: {len(texts)} texts in {batch_time:.2f}s")
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        avg_time = (self._total_time / self._recognition_count) if self._recognition_count > 0 else 0
        
        return {
            'recognition_count': self._recognition_count,
            'total_time': self._total_time,
            'average_time': avg_time,
            'max_workers': self.max_workers,
            'active_threads': self.executor._threads.__len__() if hasattr(self.executor, '_threads') else 0
        }
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the thread pool executor.
        
        Args:
            wait: Whether to wait for pending tasks to complete
        """
        self.executor.shutdown(wait=wait)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.shutdown()


class AdaptivePatternMatcher(ParallelPatternMatcher):
    """
    Adaptive pattern matcher that learns from usage patterns.
    
    Features:
    - Tracks recognizer success rates
    - Prioritizes high-performing recognizers
    - Adaptive worker allocation
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        super().__init__(max_workers)
        
        # Track success rates for each recognizer
        self._success_counts: Dict[str, int] = {r: 0 for r in self.recognizers}
        self._attempt_counts: Dict[str, int] = {r: 0 for r in self.recognizers}
    
    def recognize_parallel(self, text: str) -> List[ParallelRecognitionResult]:
        """
        Recognize patterns with adaptive prioritization.
        
        Recognizers with higher success rates get priority.
        """
        results = super().recognize_parallel(text)
        
        # Update success statistics
        recognized_types = set()
        for result in results:
            recognized_types.add(result.recognizer_type)
            self._success_counts[result.recognizer_type] += 1
        
        # Update attempt counts
        for recognizer_type in self.recognizers:
            self._attempt_counts[recognizer_type] += 1
        
        return results
    
    def get_recognizer_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed statistics for each recognizer.
        
        Returns:
            Dictionary with stats for each recognizer type
        """
        stats = {}
        
        for recognizer_type in self.recognizers:
            attempts = self._attempt_counts[recognizer_type]
            successes = self._success_counts[recognizer_type]
            success_rate = (successes / attempts * 100) if attempts > 0 else 0
            
            stats[recognizer_type] = {
                'attempts': attempts,
                'successes': successes,
                'success_rate': success_rate
            }
        
        return stats
    
    def get_recommended_order(self) -> List[str]:
        """
        Get recommended recognizer order based on success rates.
        
        Returns:
            List of recognizer types ordered by success rate
        """
        # Calculate success rates
        rates = []
        for recognizer_type in self.recognizers:
            attempts = self._attempt_counts[recognizer_type]
            if attempts > 0:
                rate = self._success_counts[recognizer_type] / attempts
                rates.append((recognizer_type, rate))
            else:
                rates.append((recognizer_type, 0.0))
        
        # Sort by success rate (descending)
        rates.sort(key=lambda x: x[1], reverse=True)
        
        return [r[0] for r in rates]