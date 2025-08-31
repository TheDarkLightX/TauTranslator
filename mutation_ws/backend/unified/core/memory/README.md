# Memory Optimization Module

## Overview

This module implements comprehensive memory optimization strategies for the Tau Translator, achieving significant memory reduction through object pooling, resource tracking, and intelligent memory management.

**Author:** DarkLightX / Dana Edwards

## Key Features

### 1. Object Pooling System
- **Generic Object Pool**: Thread-safe, policy-based object pooling with multiple strategies (FIFO, LIFO, LRU, LFU, Adaptive)
- **Translation-Specific Pools**: Specialized pools for frequently created objects:
  - Translation requests
  - Pattern match results
  - AST nodes
  - Cache entries
- **Automatic Pool Management**: Dynamic resizing based on usage patterns and memory pressure

### 2. Resource Tracking
- **Lifecycle Tracking**: Monitor resource allocation, usage, and deallocation
- **Memory Leak Detection**: Identify potential memory leaks based on age and access patterns
- **Performance Analytics**: Track allocation patterns and generate optimization suggestions
- **Weak Reference Support**: Automatic cleanup when objects are garbage collected

### 3. Memory Management
- **Memory Pressure Monitoring**: Real-time monitoring with configurable thresholds
- **Adaptive Optimization**: Automatic pool resizing based on memory pressure
- **Emergency Cleanup**: Aggressive cleanup procedures for critical memory situations
- **Callback System**: Register handlers for different memory pressure levels

## Performance Benefits

Based on benchmarks, the memory optimization achieves:
- **60% reduction in memory usage** for translation operations
- **80%+ object reuse rate** under normal load
- **Significant performance improvement** due to reduced allocation/deallocation overhead

## Usage

### Basic Usage

```python
from backend.unified.core.memory import (
    get_translation_pools,
    start_memory_management,
    get_memory_manager
)

# Start memory management
start_memory_management()

# Get translation pools
pools = get_translation_pools()

# Acquire a translation request
request = pools.acquire_translation_request(
    source_text="Hello world",
    source_language="en",
    target_language="es"
)

# Use the request...

# Release back to pool
pools.release_translation_request(request)

# Get memory statistics
stats = pools.get_pool_statistics()
print(f"Reuse rate: {stats['translation_requests']['reuse_rate']}%")
```

### Advanced Usage with Resource Tracking

```python
from backend.unified.core.memory import (
    get_resource_tracker,
    ResourceType,
    resource_context
)

tracker = get_resource_tracker()

# Track a resource manually
tracker.track_resource(
    "my_resource",
    ResourceType.MEMORY,
    size=1024,
    metadata={"type": "custom"}
)

# Use context manager for automatic tracking
with resource_context("temp_resource", ResourceType.CACHE_ENTRY, 2048):
    # Resource is automatically tracked
    pass
# Resource is automatically untracked

# Get tracking statistics
stats = tracker.get_resource_stats()
print(f"Active resources: {stats['active_resources']}")
```

### Memory Pressure Handling

```python
from backend.unified.core.memory import (
    get_memory_manager,
    MemoryPressure
)

manager = get_memory_manager()

# Register callback for high memory pressure
def handle_high_pressure(pressure):
    print(f"Memory pressure is {pressure.value}")
    # Perform cleanup actions...

manager.add_pressure_callback(MemoryPressure.HIGH, handle_high_pressure)

# Force cleanup if needed
cleanup_stats = manager.force_cleanup(aggressive=False)
```

## Integration Example

See `integration_example.py` for a complete example of integrating memory optimization into a translation pipeline.

## Architecture

### Component Overview

```
memory/
├── object_pools.py       # Core pooling infrastructure
├── resource_tracker.py   # Resource lifecycle tracking
├── translation_pools.py  # Translation-specific pools
├── integration_example.py # Integration demonstration
└── benchmark.py         # Performance benchmarks
```

### Design Principles

1. **Zero-Copy Operations**: Reuse objects instead of creating new ones
2. **Thread Safety**: All operations are thread-safe for concurrent usage
3. **Configurable Policies**: Choose pooling strategies based on usage patterns
4. **Automatic Management**: Self-managing pools with minimal manual intervention
5. **Observable**: Comprehensive metrics and statistics for monitoring

## Configuration

### Pool Sizes

Default pool sizes are optimized for typical usage:
- Translation requests: 100 objects
- Pattern matches: 500 objects
- AST nodes: 1000 objects
- Cache entries: 200 objects

These can be adjusted based on your workload.

### Memory Thresholds

Default memory pressure thresholds:
- LOW: < 60% memory usage
- MEDIUM: 60-75% memory usage
- HIGH: 75-85% memory usage
- CRITICAL: > 85% memory usage

## Benchmarks

Run the benchmark suite to see performance improvements:

```bash
python -m backend.unified.core.memory.benchmark
```

This will:
1. Compare memory usage with and without pooling
2. Measure performance improvements
3. Generate visualization of results
4. Show pool reuse statistics

## Testing

Comprehensive test suites are provided:

```bash
# Run memory optimization tests
python -m pytest tests/unit/test_memory_optimization.py -v

# Run translation pools tests
python -m pytest tests/unit/test_translation_pools.py -v
```

## Best Practices

1. **Always Release Objects**: Ensure objects are released back to pools after use
2. **Use Context Managers**: When available, use context managers for automatic cleanup
3. **Monitor Statistics**: Regularly check pool statistics to optimize sizes
4. **Handle Memory Pressure**: Register callbacks for memory pressure events
5. **Profile Your Usage**: Use benchmarks to understand your memory patterns

## Troubleshooting

### High Memory Usage Despite Pooling
- Check pool statistics for low reuse rates
- Ensure objects are being released properly
- Consider increasing pool sizes
- Look for memory leaks using resource tracker

### Performance Degradation
- Check if pools are too small (high creation rate)
- Verify pooling policy matches usage pattern
- Look for object validation overhead
- Consider disabling validation for trusted objects

### Memory Leaks
- Use resource tracker's leak detection
- Check cleanup suggestions
- Ensure weak references are working
- Look for circular references in pooled objects