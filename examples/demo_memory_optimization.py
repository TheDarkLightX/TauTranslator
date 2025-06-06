#!/usr/bin/env python3
"""
Demonstration of memory optimization features in Tau Translator.

This script shows:
1. Object pooling reducing memory usage
2. Resource tracking identifying patterns
3. Memory pressure handling
4. Performance improvements

Author: DarkLightX / Dana Edwards
"""

import sys
import os
import time
import psutil
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.unified.core.memory import (
    get_translation_pools,
    start_memory_management,
    stop_memory_management,
    get_memory_manager,
    get_resource_tracker,
    MemoryPressure
)


def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f}TB"


def demonstrate_without_pooling():
    """Show memory usage without pooling."""
    print("\n1. DEMONSTRATION WITHOUT POOLING")
    print("=" * 50)
    
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss
    
    print(f"Starting memory: {format_bytes(start_memory)}")
    
    # Create many objects without pooling
    translations = []
    for i in range(1000):
        translation = {
            "source_text": f"This is test sentence number {i} that needs translation.",
            "source_language": "en",
            "target_language": "es",
            "timestamp": time.time(),
            "metadata": {"index": i, "category": "test", "priority": i % 3}
        }
        translations.append(translation)
        
        # Create pattern matches
        patterns = []
        for j in range(5):
            pattern = {
                "pattern_name": f"pattern_{j}",
                "matched_text": f"word_{i}_{j}",
                "confidence": 0.95,
                "position": j * 10
            }
            patterns.append(pattern)
        
        # Create AST nodes
        ast_nodes = []
        for k in range(10):
            node = {
                "type": "node",
                "value": f"value_{k}",
                "children": [{"type": "child", "value": n} for n in range(3)]
            }
            ast_nodes.append(node)
    
    mid_memory = process.memory_info().rss
    memory_used = mid_memory - start_memory
    
    print(f"Memory after creating objects: {format_bytes(mid_memory)}")
    print(f"Memory used: {format_bytes(memory_used)}")
    
    # Clear objects
    translations.clear()
    
    # Force garbage collection
    import gc
    gc.collect()
    time.sleep(0.5)
    
    end_memory = process.memory_info().rss
    print(f"Memory after cleanup: {format_bytes(end_memory)}")
    print(f"Memory retained: {format_bytes(end_memory - start_memory)}")
    
    return memory_used


def demonstrate_with_pooling():
    """Show memory usage with pooling."""
    print("\n2. DEMONSTRATION WITH POOLING")
    print("=" * 50)
    
    # Start memory management
    start_memory_management()
    pools = get_translation_pools()
    
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss
    
    print(f"Starting memory: {format_bytes(start_memory)}")
    
    # Create same number of objects with pooling
    for i in range(1000):
        # Acquire translation request
        request = pools.acquire_translation_request(
            source_text=f"This is test sentence number {i} that needs translation.",
            source_language="en",
            target_language="es"
        )
        
        # Create pattern matches
        patterns = []
        for j in range(5):
            pattern = pools.acquire_pattern_match(
                pattern_name=f"pattern_{j}",
                matched_text=f"word_{i}_{j}",
                start_position=j * 10,
                end_position=j * 10 + 5,
                confidence=0.95
            )
            patterns.append(pattern)
        
        # Create AST nodes
        root = pools.acquire_ast_node("root", value=f"tree_{i}")
        for k in range(10):
            node = pools.acquire_ast_node(f"node_{k}", value=f"value_{k}")
            for n in range(3):
                child = pools.acquire_ast_node("child", value=n)
                node.add_child(child)
            root.add_child(node)
        
        # Release everything back to pools
        pools.release_translation_request(request)
        for pattern in patterns:
            pools.release_pattern_match(pattern)
        pools.release_ast_node(root)  # Recursively releases children
    
    mid_memory = process.memory_info().rss
    memory_used = mid_memory - start_memory
    
    print(f"Memory after creating objects: {format_bytes(mid_memory)}")
    print(f"Memory used: {format_bytes(memory_used)}")
    
    # Show pool statistics
    print("\nPool Statistics:")
    stats = pools.get_pool_statistics()
    for pool_name, pool_stats in stats.items():
        print(f"\n{pool_name}:")
        print(f"  Created: {pool_stats['created_objects']}")
        print(f"  Reused: {pool_stats['reused_objects']}")
        print(f"  Reuse rate: {pool_stats['reuse_rate']:.1f}%")
        print(f"  Pool size: {pool_stats['current_size']}")
    
    stop_memory_management()
    
    return memory_used


def demonstrate_resource_tracking():
    """Show resource tracking capabilities."""
    print("\n3. RESOURCE TRACKING DEMONSTRATION")
    print("=" * 50)
    
    tracker = get_resource_tracker()
    
    # Take initial snapshot
    initial_snapshot = tracker.take_snapshot()
    print(f"Initial tracked resources: {initial_snapshot.tracked_resources}")
    
    # Track some operations
    pools = get_translation_pools()
    
    # Simulate translation workflow
    requests = []
    for i in range(10):
        req = pools.acquire_translation_request(
            f"Text {i} to translate",
            "en", "es"
        )
        requests.append(req)
    
    # Take snapshot during operations
    mid_snapshot = tracker.take_snapshot()
    print(f"\nDuring operations:")
    print(f"  Tracked resources: {mid_snapshot.tracked_resources}")
    print(f"  Process memory: {format_bytes(mid_snapshot.process_memory)}")
    
    # Check for patterns
    patterns = tracker.get_allocation_patterns()
    print(f"\nAllocation patterns:")
    print(f"  Allocation rate: {patterns['allocation_rate']:.2f} objects/sec")
    print(f"  Resource distribution: {dict(patterns['resource_type_distribution'])}")
    
    # Release some resources
    for req in requests[:5]:
        pools.release_translation_request(req)
    
    # Get suggestions
    suggestions = tracker.cleanup_suggestions()
    if suggestions:
        print(f"\nCleanup suggestions:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
    
    # Final cleanup
    for req in requests[5:]:
        pools.release_translation_request(req)
    
    # Final statistics
    final_stats = tracker.get_resource_stats()
    print(f"\nFinal statistics:")
    print(f"  Total allocations: {final_stats['total_allocations']}")
    print(f"  Total deallocations: {final_stats['total_deallocations']}")
    print(f"  Reuse count: {final_stats['reuse_count']}")
    print(f"  Potential leaks detected: {final_stats['leak_count']}")


def demonstrate_memory_pressure():
    """Show memory pressure handling."""
    print("\n4. MEMORY PRESSURE HANDLING")
    print("=" * 50)
    
    manager = get_memory_manager()
    pools = get_translation_pools()
    
    # Register callback
    pressure_events = []
    
    def handle_pressure(pressure: MemoryPressure):
        pressure_events.append(pressure)
        print(f"  ! Memory pressure event: {pressure.value}")
    
    manager.add_pressure_callback(MemoryPressure.HIGH, handle_pressure)
    manager.add_pressure_callback(MemoryPressure.CRITICAL, handle_pressure)
    
    # Get current memory stats
    mem_stats = manager.get_memory_stats()
    print(f"Current memory status:")
    print(f"  Total system memory: {format_bytes(mem_stats.total_memory)}")
    print(f"  Available memory: {format_bytes(mem_stats.available_memory)}")
    print(f"  Process memory: {format_bytes(mem_stats.process_memory)}")
    print(f"  Memory pressure: {mem_stats.memory_pressure.value}")
    print(f"  Usage percent: {mem_stats.memory_usage_percent:.1f}%")
    
    # Simulate memory pressure by reducing pool sizes
    print(f"\nSimulating memory pressure response...")
    
    # Force optimization
    manager.optimize_pools()
    
    # Show pool adjustments
    stats_after = pools.get_pool_statistics()
    print(f"\nPool sizes after optimization:")
    for pool_name, stats in stats_after.items():
        print(f"  {pool_name}: {stats['max_size']} max size")


def main():
    """Run all demonstrations."""
    print("TAU TRANSLATOR MEMORY OPTIMIZATION DEMONSTRATION")
    print("=" * 50)
    print("Author: DarkLightX / Dana Edwards")
    
    # Show system info
    print(f"\nSystem Information:")
    print(f"  Python version: {sys.version.split()[0]}")
    print(f"  Total system memory: {format_bytes(psutil.virtual_memory().total)}")
    print(f"  Available memory: {format_bytes(psutil.virtual_memory().available)}")
    
    # Run demonstrations
    memory_without = demonstrate_without_pooling()
    memory_with = demonstrate_with_pooling()
    
    # Show comparison
    print("\n" + "=" * 50)
    print("MEMORY USAGE COMPARISON")
    print("=" * 50)
    print(f"Without pooling: {format_bytes(memory_without)}")
    print(f"With pooling: {format_bytes(memory_with)}")
    
    if memory_without > 0:
        reduction = (memory_without - memory_with) / memory_without * 100
        print(f"Memory reduction: {reduction:.1f}%")
    
    # Additional demonstrations
    demonstrate_resource_tracking()
    demonstrate_memory_pressure()
    
    print("\n" + "=" * 50)
    print("DEMONSTRATION COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()