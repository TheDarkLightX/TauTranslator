Module src.tau_translator_omega.core_engine.performance_utils
=============================================================
Performance Utilities for TauTranslator
======================================

Provides caching, monitoring, and optimization utilities.

Author: DarkLightX / Dana Edwards

Functions
---------

`compile_pattern(pattern: str, flags: int = 0) ‑> re.Pattern`
:   Compile regex pattern with caching.

`get_monitor() ‑> src.tau_translator_omega.core_engine.performance_utils.PerformanceMonitor`
:   Get the global performance monitor.

`measure(operation: str)`
:   Decorator to measure function performance.

`memoize(maxsize: int = 128)`
:   Decorator for memoizing function results.

Classes
-------

`CachedPatternCompiler(maxsize: int = 500)`
:   Cache compiled regex patterns.

    ### Methods

    `compile(self, pattern: str, flags: int = 0) ‑> re.Pattern`
    :   Compile regex pattern with caching.

    `get_stats(self) ‑> Dict[str, Any]`
    :   Get cache statistics.

`LRUCache(capacity: int = 1000)`
:   Least Recently Used cache implementation.

    ### Instance variables

    `hit_rate: float`
    :   Calculate cache hit rate.

    ### Methods

    `clear(self) ‑> None`
    :   Clear the cache.

    `get(self, key: Any) ‑> Any | None`
    :   Get value from cache.

    `get_stats(self) ‑> Dict[str, Any]`
    :   Get cache statistics.

    `put(self, key: Any, value: Any) ‑> None`
    :   Put value in cache.

`PerformanceMetric(operation: str, duration: float, timestamp: datetime.datetime = <factory>, metadata: Dict[str, Any] = <factory>)`
:   Single performance measurement.

    ### Instance variables

    `duration: float`
    :

    `metadata: Dict[str, Any]`
    :

    `operation: str`
    :

    `timestamp: datetime.datetime`
    :

`PerformanceMonitor(name: str = 'TauTranslator')`
:   Monitor and analyze performance of operations.

    ### Methods

    `clear(self) ‑> None`
    :   Clear all metrics.

    `get_report(self) ‑> str`
    :   Generate a performance report.

    `get_stats(self, operation: str | None = None) ‑> Dict[str, Dict[str, float]]`
    :   Get performance statistics.

    `measure(self, operation: str, **metadata)`
    :   Context manager to measure operation duration.

    `record(self, operation: str, duration: float, **metadata) ‑> None`
    :   Record a performance measurement.

    `save_report(self, filepath: str) ‑> None`
    :   Save performance report to file.

    `start_timer(self, operation: str) ‑> None`
    :   Start a named timer.

    `stop_timer(self, operation: str) ‑> float`
    :   Stop a named timer and record the duration.