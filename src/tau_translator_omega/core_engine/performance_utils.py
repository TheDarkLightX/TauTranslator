"""
Performance Utilities for TauTranslator
======================================

Provides caching, monitoring, and optimization utilities.

Author: DarkLightX / Dana Edwards
"""

import time
import functools
import statistics
from collections import OrderedDict, defaultdict
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class LRUCache:
    """Least Recently Used cache implementation."""
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: Any) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: Any, value: Any) -> None:
        """Put value in cache."""
        if key in self.cache:
            # Update existing
            self.cache.move_to_end(key)
        else:
            # Add new
            if len(self.cache) >= self.capacity:
                # Remove least recently used
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'capacity': self.capacity,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hit_rate
        }


def memoize(maxsize: int = 128):
    """Decorator for memoizing function results."""
    def decorator(func: Callable) -> Callable:
        cache = LRUCache(maxsize)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = (args, tuple(sorted(kwargs.items())))
            
            # Check cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache.put(key, result)
            return result
        
        # Add cache access methods
        wrapper.cache = cache
        wrapper.cache_info = lambda: cache.get_stats()
        wrapper.cache_clear = lambda: cache.clear()
        
        return wrapper
    return decorator


@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    operation: str
    duration: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Monitor and analyze performance of operations."""
    
    def __init__(self, name: str = "TauTranslator"):
        self.name = name
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.detailed_metrics: List[PerformanceMetric] = []
        self.active_timers: Dict[str, float] = {}
    
    @contextmanager
    def measure(self, operation: str, **metadata):
        """Context manager to measure operation duration."""
        start_time = time.perf_counter()
        
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.record(operation, duration, **metadata)
    
    def start_timer(self, operation: str) -> None:
        """Start a named timer."""
        self.active_timers[operation] = time.perf_counter()
    
    def stop_timer(self, operation: str) -> float:
        """Stop a named timer and record the duration."""
        if operation not in self.active_timers:
            logger.warning(f"Timer '{operation}' was not started")
            return 0.0
        
        start_time = self.active_timers.pop(operation)
        duration = time.perf_counter() - start_time
        self.record(operation, duration)
        return duration
    
    def record(self, operation: str, duration: float, **metadata) -> None:
        """Record a performance measurement."""
        self.metrics[operation].append(duration)
        
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            metadata=metadata
        )
        self.detailed_metrics.append(metric)
        
        # Log slow operations
        if duration > 1.0:  # More than 1 second
            logger.warning(f"Slow operation '{operation}': {duration:.3f}s")
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """Get performance statistics."""
        if operation:
            times = self.metrics.get(operation, [])
            return self._calculate_stats(operation, times)
        
        # Return stats for all operations
        return {
            op: self._calculate_stats(op, times)
            for op, times in self.metrics.items()
        }
    
    def _calculate_stats(self, operation: str, times: List[float]) -> Dict[str, float]:
        """Calculate statistics for a set of measurements."""
        if not times:
            return {
                'count': 0,
                'total': 0.0,
                'mean': 0.0,
                'min': 0.0,
                'max': 0.0,
                'p50': 0.0,
                'p95': 0.0,
                'p99': 0.0
            }
        
        sorted_times = sorted(times)
        n = len(times)
        
        return {
            'count': n,
            'total': sum(times),
            'mean': statistics.mean(times),
            'min': min(times),
            'max': max(times),
            'p50': sorted_times[n // 2],
            'p95': sorted_times[int(n * 0.95)] if n > 1 else sorted_times[0],
            'p99': sorted_times[int(n * 0.99)] if n > 1 else sorted_times[0]
        }
    
    def get_report(self) -> str:
        """Generate a performance report."""
        stats = self.get_stats()
        
        report_lines = [
            f"Performance Report: {self.name}",
            "=" * 60,
            ""
        ]
        
        # Sort by total time
        sorted_ops = sorted(
            stats.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )
        
        for operation, op_stats in sorted_ops:
            report_lines.extend([
                f"Operation: {operation}",
                f"  Count: {op_stats['count']}",
                f"  Total: {op_stats['total']:.3f}s",
                f"  Mean: {op_stats['mean']:.3f}s",
                f"  Min: {op_stats['min']:.3f}s",
                f"  Max: {op_stats['max']:.3f}s",
                f"  P95: {op_stats['p95']:.3f}s",
                ""
            ])
        
        return "\n".join(report_lines)
    
    def save_report(self, filepath: str) -> None:
        """Save performance report to file."""
        report_data = {
            'name': self.name,
            'generated_at': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'detailed_metrics': [
                {
                    'operation': m.operation,
                    'duration': m.duration,
                    'timestamp': m.timestamp.isoformat(),
                    'metadata': m.metadata
                }
                for m in self.detailed_metrics[-1000:]  # Keep last 1000
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)
    
    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
        self.detailed_metrics.clear()
        self.active_timers.clear()


# Global performance monitor instance
_global_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return _global_monitor


def measure(operation: str):
    """Decorator to measure function performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with _global_monitor.measure(f"{func.__module__}.{func.__name__}"):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class CachedPatternCompiler:
    """Cache compiled regex patterns."""
    
    def __init__(self, maxsize: int = 500):
        self.cache = LRUCache(maxsize)
    
    def compile(self, pattern: str, flags: int = 0) -> 're.Pattern':
        """Compile regex pattern with caching."""
        import re
        
        key = (pattern, flags)
        compiled = self.cache.get(key)
        
        if compiled is None:
            compiled = re.compile(pattern, flags)
            self.cache.put(key, compiled)
        
        return compiled
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()


# Global pattern compiler
_pattern_compiler = CachedPatternCompiler()


def compile_pattern(pattern: str, flags: int = 0) -> 're.Pattern':
    """Compile regex pattern with caching."""
    return _pattern_compiler.compile(pattern, flags)