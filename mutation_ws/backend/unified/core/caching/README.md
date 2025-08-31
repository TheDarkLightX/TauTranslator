# Advanced Caching System for Tau Translator

A production-ready, high-performance caching system with multiple eviction strategies, thread-safe operations, and intelligent adaptive selection.

## Features

### 1. Multiple Cache Eviction Strategies

- **LRU (Least Recently Used)**: Ideal for data with temporal locality
- **LFU (Least Frequently Used)**: Perfect for frequently accessed patterns
- **TTL (Time To Live)**: Time-based expiration for dynamic content
- **ARC (Adaptive Replacement Cache)**: Self-tuning between recency and frequency

### 2. Smart Cache Manager

The `SmartCacheManager` automatically selects the optimal caching strategy based on:
- Access patterns
- Hit/miss ratios
- Workload characteristics

### 3. Translation-Specific Integration

The `TranslationCacheManager` provides specialized caches for:
- **Pattern Cache** (LFU): For regex patterns that are reused frequently
- **Grammar Cache** (LRU): For recently parsed grammars
- **NLP Cache** (ARC): Adaptive for varying NLP workloads
- **Result Cache** (TTL): Time-based expiration for translation results

### 4. Thread-Safe Operations

- All cache implementations use thread-safe data structures
- Minimal lock contention for high-performance concurrent access
- Comprehensive concurrent testing with multiple threads

### 5. Performance Monitoring

- Real-time hit/miss statistics
- Cache size tracking
- Eviction and expiration counters
- Time saved by caching

## Usage

### Basic Cache Usage

```python
from backend.unified.core.caching import LRUCache, LFUCache, TTLCache

# Create an LRU cache
lru_cache = LRUCache(max_size=1000)
lru_cache.put("key", "value")
value = lru_cache.get("key")

# Create a TTL cache with 5-minute expiration
ttl_cache = TTLCache(max_size=1000, default_ttl=300.0)
ttl_cache.put("key", "value", ttl=60.0)  # Override TTL to 1 minute
```

### Translation Pipeline Integration

```python
from backend.unified.core.caching import (
    TranslationCacheConfig,
    configure_translation_cache,
    cached_translation
)

# Configure caching
config = TranslationCacheConfig(
    pattern_cache_size=20000,
    result_cache_size=100000,
    result_ttl=600.0,  # 10 minutes
    enable_compression=True
)
configure_translation_cache(config)

# Use the decorator for automatic caching
@cached_translation('pattern')
def expensive_pattern_match(pattern: str) -> dict:
    # Your expensive operation here
    return result

# First call is slow, subsequent calls are cached
result = expensive_pattern_match("complex_pattern")
```

### Cache Warming

```python
from backend.unified.core.caching import get_translation_cache_manager

manager = get_translation_cache_manager()

# Warm caches with pre-computed data
warmup_data = {
    'patterns': {
        'pattern1': {'result': 'cached_result1'},
        'pattern2': {'result': 'cached_result2'}
    },
    'grammars': {
        'grammar1': {'parsed': True, 'rules': []}
    }
}
manager.warm_caches(warmup_data)
```

### Performance Monitoring

```python
# Get comprehensive statistics
stats = manager.get_statistics()
print(f"Pattern cache hit rate: {stats['caches']['pattern']['hit_rate']:.1f}%")
print(f"Total time saved: {stats['lookups']['total_time_saved']:.2f}s")
```

## Configuration Options

### TranslationCacheConfig

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pattern_cache_size` | 10000 | Maximum patterns to cache |
| `grammar_cache_size` | 1000 | Maximum grammars to cache |
| `nlp_cache_size` | 5000 | Maximum NLP results to cache |
| `result_cache_size` | 50000 | Maximum translation results |
| `pattern_ttl` | 3600.0 | Pattern cache TTL (1 hour) |
| `grammar_ttl` | 7200.0 | Grammar cache TTL (2 hours) |
| `nlp_ttl` | 1800.0 | NLP cache TTL (30 minutes) |
| `result_ttl` | 300.0 | Result cache TTL (5 minutes) |
| `enable_compression` | True | Use hashing for long keys |
| `enable_statistics` | True | Track performance metrics |
| `enable_warmup` | True | Allow cache warming |

## Performance Characteristics

Based on our testing:

- **LRU Cache**: O(1) get/put operations with OrderedDict
- **LFU Cache**: O(1) amortized operations with frequency tracking
- **TTL Cache**: O(log n) cleanup with heap-based expiration
- **ARC Cache**: O(1) operations with adaptive balancing

### Benchmark Results

On a typical workload:
- Cache hit rates: 75-95% after warmup
- Performance improvement: 80-99% faster for cached operations
- Memory efficient: ~100 bytes per entry overhead
- Thread-safe: Supports 20+ concurrent threads

## Testing

The caching system includes comprehensive test coverage:

- 33 tests for core cache functionality
- 22 tests for translation integration
- Thread safety tests with concurrent access
- Performance benchmarks
- Edge case handling

Run tests with:
```bash
python3 -m pytest tests/unit/test_advanced_cache.py -v
python3 -m pytest tests/unit/test_translation_cache_integration.py -v
```

## Future Enhancements

Potential improvements for future versions:

1. **Distributed Caching**: Redis/Memcached backend support
2. **Cache Persistence**: Save/load cache state to disk
3. **Advanced Metrics**: Prometheus integration
4. **Memory Pressure Handling**: Automatic size adjustment
5. **Cache Invalidation**: Dependency-based invalidation

## Author

DarkLightX / Dana Edwards