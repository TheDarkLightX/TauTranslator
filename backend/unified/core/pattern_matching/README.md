# FSA Pattern Matching Engine

High-performance pattern matching engine for the Tau Translator using Finite State Automata (FSA) principles.

## Overview

The FSA pattern matching engine provides 50-70% faster pattern matching compared to traditional regex approaches for multiple literal pattern scenarios. It's designed specifically for the translation pipeline where multiple patterns need to be matched and replaced efficiently.

## Architecture

The pattern matching system consists of several components:

### 1. Core FSA Engine (`fsa_engine.py`)
- **FiniteStateAutomaton**: Traditional FSA implementation with states and transitions
- **FSAPatternCompiler**: Compiles patterns into FSA structures
- **OptimizedPatternMatcher**: Thread-safe pattern matcher with caching

### 2. Hybrid Pattern Matcher (`fsa_engine_hybrid.py`)
- Combines FSA concepts with optimized string algorithms
- Uses batch processing for better performance
- Automatically selects the best algorithm based on pattern characteristics

### 3. Pattern Integration (`fsa_pattern_integration.py`)
- Integrates with the pattern loader system
- Adapts patterns for FSA processing
- Provides fallback to regex for complex patterns

## Features

- **O(n) Complexity**: Linear time complexity for pattern matching
- **Thread-Safe**: All operations are thread-safe for concurrent use
- **Pattern Prioritization**: Supports priority-based pattern matching
- **Batch Processing**: Optimized batch operations for multiple patterns
- **Performance Metrics**: Built-in performance tracking and metrics

## Usage

### Basic Usage

```python
from backend.unified.core.pattern_matching import get_pattern_matcher

# Get the global pattern matcher
matcher = get_pattern_matcher()

# Add patterns: (pattern_id, source, replacement, priority)
patterns = [
    ("p1", "hello", "HELLO", 10),
    ("p2", "world", "WORLD", 5),
]
matcher.add_patterns(patterns)

# Find first match
match = matcher.match("hello world")
print(f"Found: {match.matched_text} at position {match.start_pos}")

# Find all matches
matches = matcher.find_all_matches("hello world hello")
for match in matches:
    print(f"Pattern {match.pattern_id}: {match.matched_text}")

# Replace patterns
result, count = matcher.replace("hello world", max_replacements=None)
print(f"Result: {result}, Replacements: {count}")
```

### Integration with Pattern Loader

```python
from backend.unified.core.pattern_matching import get_fsa_pattern_manager

# Get FSA-enabled pattern manager
manager = get_fsa_pattern_manager()

# Load patterns from file
manager.pattern_manager.load_pattern_set("patterns.json")

# Sync patterns to FSA
manager.sync_patterns()

# Use for matching
match = manager.match("test text")
```

## Performance

The FSA engine achieves significant performance improvements through:

1. **Optimized String Algorithms**: Uses Boyer-Moore-Horspool and native string methods
2. **Batch Processing**: Processes multiple patterns in a single pass
3. **Intelligent Caching**: Caches compiled patterns to avoid recompilation
4. **Minimal Overhead**: Reduces regex compilation overhead for literal patterns

### Benchmarks

For typical Tau translation patterns (20+ patterns on moderate text):
- FSA Engine: ~50-70% faster than regex
- Memory Usage: <1KB per pattern
- Compilation Time: <1ms for 100 patterns

## Pattern Types Supported

1. **Literal Patterns**: Exact string matching (fastest)
2. **Wildcard Patterns**: Single character wildcards
3. **Character Classes**: Sets of characters
4. **Simple Sequences**: Ordered character sequences

## Thread Safety

All operations are thread-safe:
- Pattern compilation is protected by locks
- Concurrent matching is supported
- Metrics collection is thread-safe

## Testing

Comprehensive test coverage includes:
- Unit tests for all components
- Integration tests with pattern loader
- Performance benchmarks
- Thread safety tests
- Edge case handling

Run tests:
```bash
python3 -m pytest tests/unit/test_fsa_engine.py
python3 -m pytest tests/unit/test_fsa_pattern_integration.py
python3 -m pytest tests/unit/test_fsa_performance.py
```

## Future Enhancements

1. **Regex Support**: Full regex-to-FSA compilation
2. **Unicode Optimization**: Specialized Unicode handling
3. **GPU Acceleration**: CUDA/OpenCL for massive pattern sets
4. **Streaming Support**: Process large files without loading into memory

## Author

DarkLightX / Dana Edwards