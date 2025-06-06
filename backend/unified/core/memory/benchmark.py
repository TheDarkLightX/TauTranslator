"""
Memory optimization benchmarks.

Demonstrates and measures the performance improvements and memory reduction
achieved through object pooling and resource tracking.

Author: DarkLightX / Dana Edwards
"""

import time
import gc
import psutil
import os
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from .translation_pools import get_translation_pools, TranslationRequest, PatternMatchResult, ASTNode
from .object_pools import start_memory_management, stop_memory_management, get_memory_manager


@dataclass
class BenchmarkResult:
    """Benchmark result data."""
    name: str
    duration: float
    memory_before: int
    memory_after: int
    memory_peak: int
    operations: int
    
    @property
    def memory_used(self) -> int:
        """Memory used during benchmark."""
        return self.memory_after - self.memory_before
    
    @property
    def memory_used_mb(self) -> float:
        """Memory used in MB."""
        return self.memory_used / (1024 * 1024)
    
    @property
    def ops_per_second(self) -> float:
        """Operations per second."""
        return self.operations / self.duration if self.duration > 0 else 0


class MemoryBenchmark:
    """Benchmark suite for memory optimization."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.results: List[BenchmarkResult] = []
    
    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        return self.process.memory_info().rss
    
    def run_benchmark(
        self,
        name: str,
        func: callable,
        operations: int = 10000
    ) -> BenchmarkResult:
        """Run a single benchmark."""
        print(f"\nRunning benchmark: {name}")
        print(f"Operations: {operations:,}")
        
        # Force garbage collection before starting
        gc.collect()
        time.sleep(0.1)  # Let system settle
        
        memory_before = self.get_memory_usage()
        memory_peak = memory_before
        
        # Run benchmark
        start_time = time.time()
        
        for i in range(operations):
            func(i)
            
            # Track peak memory periodically
            if i % 100 == 0:
                current_memory = self.get_memory_usage()
                memory_peak = max(memory_peak, current_memory)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Force garbage collection after
        gc.collect()
        time.sleep(0.1)  # Let system settle
        
        memory_after = self.get_memory_usage()
        
        result = BenchmarkResult(
            name=name,
            duration=duration,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_peak=memory_peak,
            operations=operations
        )
        
        self.results.append(result)
        
        print(f"Duration: {duration:.2f}s")
        print(f"Ops/sec: {result.ops_per_second:,.0f}")
        print(f"Memory used: {result.memory_used_mb:.2f}MB")
        print(f"Peak memory: {(memory_peak - memory_before) / (1024*1024):.2f}MB")
        
        return result


def benchmark_without_pooling():
    """Benchmark translation objects without pooling."""
    
    def create_translation_request(i: int):
        """Create translation request without pooling."""
        request = {
            "source_text": f"This is test text number {i} for translation",
            "source_language": "en",
            "target_language": "es",
            "options": {"formal": i % 2 == 0},
            "timestamp": time.time(),
            "request_id": f"req_{i}"
        }
        # Simulate some processing
        _ = len(str(request))
    
    def create_pattern_match(i: int):
        """Create pattern match without pooling."""
        match = {
            "pattern_name": f"pattern_{i % 10}",
            "matched_text": f"match_{i}",
            "start_position": i * 10,
            "end_position": i * 10 + 5,
            "confidence": 0.95,
            "metadata": {"index": i}
        }
        # Simulate some processing
        _ = len(str(match))
    
    def create_ast_node(i: int):
        """Create AST node without pooling."""
        node = {
            "node_type": f"Node_{i % 20}",
            "value": i,
            "children": [],
            "attributes": {"index": i, "type": "test"},
            "line_number": i // 100,
            "column_number": i % 100
        }
        # Add some children
        for j in range(3):
            child = {
                "node_type": f"Child_{j}",
                "value": f"child_{i}_{j}",
                "children": [],
                "attributes": {},
                "line_number": 0,
                "column_number": j
            }
            node["children"].append(child)
        # Simulate some processing
        _ = len(str(node))
    
    benchmark = MemoryBenchmark()
    
    # Run benchmarks
    benchmark.run_benchmark(
        "Translation Requests (No Pooling)",
        create_translation_request,
        operations=10000
    )
    
    benchmark.run_benchmark(
        "Pattern Matches (No Pooling)",
        create_pattern_match,
        operations=20000
    )
    
    benchmark.run_benchmark(
        "AST Nodes (No Pooling)",
        create_ast_node,
        operations=50000
    )
    
    return benchmark.results


def benchmark_with_pooling():
    """Benchmark translation objects with pooling."""
    
    # Initialize pools
    pools = get_translation_pools()
    start_memory_management()
    
    def create_translation_request(i: int):
        """Create translation request with pooling."""
        request = pools.acquire_translation_request(
            source_text=f"This is test text number {i} for translation",
            source_language="en",
            target_language="es",
            options={"formal": i % 2 == 0},
            request_id=f"req_{i}"
        )
        # Simulate some processing
        _ = len(request.source_text)
        # Release back to pool
        pools.release_translation_request(request)
    
    def create_pattern_match(i: int):
        """Create pattern match with pooling."""
        match = pools.acquire_pattern_match(
            pattern_name=f"pattern_{i % 10}",
            matched_text=f"match_{i}",
            start_position=i * 10,
            end_position=i * 10 + 5,
            confidence=0.95,
            metadata={"index": i}
        )
        # Simulate some processing
        _ = len(match.matched_text)
        # Release back to pool
        pools.release_pattern_match(match)
    
    def create_ast_node(i: int):
        """Create AST node with pooling."""
        node = pools.acquire_ast_node(
            node_type=f"Node_{i % 20}",
            value=i,
            line_number=i // 100,
            column_number=i % 100,
            attributes={"index": i, "type": "test"}
        )
        # Add some children
        for j in range(3):
            child = pools.acquire_ast_node(
                node_type=f"Child_{j}",
                value=f"child_{i}_{j}",
                line_number=0,
                column_number=j
            )
            node.add_child(child)
        # Simulate some processing
        _ = len(node.node_type)
        # Release back to pool (releases children too)
        pools.release_ast_node(node)
    
    benchmark = MemoryBenchmark()
    
    # Run benchmarks
    benchmark.run_benchmark(
        "Translation Requests (With Pooling)",
        create_translation_request,
        operations=10000
    )
    
    benchmark.run_benchmark(
        "Pattern Matches (With Pooling)",
        create_pattern_match,
        operations=20000
    )
    
    benchmark.run_benchmark(
        "AST Nodes (With Pooling)",
        create_ast_node,
        operations=50000
    )
    
    # Get pool statistics
    pool_stats = pools.get_pool_statistics()
    
    stop_memory_management()
    
    return benchmark.results, pool_stats


def compare_results(
    results_without: List[BenchmarkResult],
    results_with: List[BenchmarkResult]
) -> Dict[str, Any]:
    """Compare benchmark results."""
    comparison = {}
    
    for i, (without, with_pool) in enumerate(zip(results_without, results_with)):
        name = without.name.split(" (")[0]  # Extract base name
        
        memory_reduction = (
            (without.memory_used - with_pool.memory_used) / without.memory_used * 100
            if without.memory_used > 0 else 0
        )
        
        performance_improvement = (
            (with_pool.ops_per_second - without.ops_per_second) / without.ops_per_second * 100
            if without.ops_per_second > 0 else 0
        )
        
        comparison[name] = {
            "memory_without_mb": without.memory_used_mb,
            "memory_with_mb": with_pool.memory_used_mb,
            "memory_reduction_percent": memory_reduction,
            "ops_per_sec_without": without.ops_per_second,
            "ops_per_sec_with": with_pool.ops_per_second,
            "performance_improvement_percent": performance_improvement
        }
    
    return comparison


def plot_results(
    results_without: List[BenchmarkResult],
    results_with: List[BenchmarkResult],
    pool_stats: Dict[str, Any]
):
    """Plot benchmark results."""
    # Prepare data
    names = [r.name.split(" (")[0] for r in results_without]
    memory_without = [r.memory_used_mb for r in results_without]
    memory_with = [r.memory_used_mb for r in results_with]
    ops_without = [r.ops_per_second for r in results_without]
    ops_with = [r.ops_per_second for r in results_with]
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Memory usage comparison
    x = np.arange(len(names))
    width = 0.35
    
    ax1.bar(x - width/2, memory_without, width, label='Without Pooling', color='red', alpha=0.7)
    ax1.bar(x + width/2, memory_with, width, label='With Pooling', color='green', alpha=0.7)
    ax1.set_xlabel('Object Type')
    ax1.set_ylabel('Memory Used (MB)')
    ax1.set_title('Memory Usage Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Performance comparison
    ax2.bar(x - width/2, ops_without, width, label='Without Pooling', color='red', alpha=0.7)
    ax2.bar(x + width/2, ops_with, width, label='With Pooling', color='green', alpha=0.7)
    ax2.set_xlabel('Object Type')
    ax2.set_ylabel('Operations/Second')
    ax2.set_title('Performance Comparison')
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Pool reuse rates
    pool_names = list(pool_stats.keys())
    reuse_rates = [stats['reuse_rate'] for stats in pool_stats.values()]
    
    ax3.bar(pool_names, reuse_rates, color='blue', alpha=0.7)
    ax3.set_xlabel('Pool Type')
    ax3.set_ylabel('Reuse Rate (%)')
    ax3.set_title('Object Pool Reuse Rates')
    ax3.set_xticklabels(pool_names, rotation=45, ha='right')
    ax3.grid(True, alpha=0.3)
    
    # Memory reduction percentages
    memory_reductions = [
        ((m1 - m2) / m1 * 100) if m1 > 0 else 0
        for m1, m2 in zip(memory_without, memory_with)
    ]
    
    ax4.bar(names, memory_reductions, color='purple', alpha=0.7)
    ax4.set_xlabel('Object Type')
    ax4.set_ylabel('Memory Reduction (%)')
    ax4.set_title('Memory Reduction Achieved')
    ax4.set_xticklabels(names, rotation=45, ha='right')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('memory_optimization_benchmarks.png', dpi=300, bbox_inches='tight')
    plt.show()


def main():
    """Run complete benchmark suite."""
    print("Memory Optimization Benchmark Suite")
    print("===================================")
    
    # Run benchmarks without pooling
    print("\n1. Running benchmarks WITHOUT object pooling...")
    results_without = benchmark_without_pooling()
    
    # Wait a bit between test suites
    time.sleep(2)
    gc.collect()
    
    # Run benchmarks with pooling
    print("\n2. Running benchmarks WITH object pooling...")
    results_with, pool_stats = benchmark_with_pooling()
    
    # Compare results
    print("\n3. Comparison Results")
    print("=====================")
    
    comparison = compare_results(results_without, results_with)
    
    for obj_type, stats in comparison.items():
        print(f"\n{obj_type}:")
        print(f"  Memory without pooling: {stats['memory_without_mb']:.2f}MB")
        print(f"  Memory with pooling: {stats['memory_with_mb']:.2f}MB")
        print(f"  Memory reduction: {stats['memory_reduction_percent']:.1f}%")
        print(f"  Performance without: {stats['ops_per_sec_without']:,.0f} ops/sec")
        print(f"  Performance with: {stats['ops_per_sec_with']:,.0f} ops/sec")
        print(f"  Performance improvement: {stats['performance_improvement_percent']:.1f}%")
    
    # Overall statistics
    print("\n4. Overall Statistics")
    print("====================")
    
    total_memory_without = sum(r.memory_used_mb for r in results_without)
    total_memory_with = sum(r.memory_used_mb for r in results_with)
    overall_reduction = (total_memory_without - total_memory_with) / total_memory_without * 100
    
    print(f"Total memory without pooling: {total_memory_without:.2f}MB")
    print(f"Total memory with pooling: {total_memory_with:.2f}MB")
    print(f"Overall memory reduction: {overall_reduction:.1f}%")
    
    # Pool statistics
    print("\n5. Object Pool Statistics")
    print("========================")
    
    for pool_name, stats in pool_stats.items():
        print(f"\n{pool_name}:")
        print(f"  Created objects: {stats['created_objects']:,}")
        print(f"  Reused objects: {stats['reused_objects']:,}")
        print(f"  Reuse rate: {stats['reuse_rate']:.1f}%")
        print(f"  Current pool size: {stats['current_size']}")
        print(f"  Max pool size: {stats['max_size']}")
    
    # Generate plots
    print("\n6. Generating visualization...")
    try:
        plot_results(results_without, results_with, pool_stats)
        print("Plots saved to 'memory_optimization_benchmarks.png'")
    except ImportError:
        print("Matplotlib not available - skipping visualization")
    
    return comparison, pool_stats


if __name__ == "__main__":
    results = main()