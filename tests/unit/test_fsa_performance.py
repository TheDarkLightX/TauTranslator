"""
Performance benchmarks for FSA pattern matching engine.

Verifies that the FSA engine achieves 50-70% faster pattern matching
compared to traditional regex approaches.

Author: DarkLightX / Dana Edwards
"""

import pytest
import re
import time
import random
import string
from typing import List, Tuple

from backend.unified.core.pattern_matching.fsa_engine import (
    FSAPatternCompiler,
    OptimizedPatternMatcher
)


def generate_random_text(length: int) -> str:
    """Generate random text for testing."""
    return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))


def generate_patterns(count: int) -> List[Tuple[str, str, str, int]]:
    """Generate test patterns."""
    patterns = []
    words = ['hello', 'world', 'test', 'pattern', 'match', 'find', 'replace', 
             'tau', 'translator', 'engine', 'fast', 'performance', 'optimize']
    
    for i in range(count):
        word = random.choice(words)
        patterns.append((
            f"pattern_{i}",
            word,
            word.upper(),
            random.randint(1, 10)
        ))
    
    return patterns


class TestFSAPerformance:
    """Test FSA engine performance characteristics."""
    
    @pytest.fixture
    def test_patterns(self):
        """Generate test patterns."""
        return generate_patterns(50)
    
    @pytest.fixture
    def test_text(self):
        """Generate test text."""
        # Create text with known patterns
        base_text = generate_random_text(5000)
        # Insert some known patterns
        patterns_to_insert = ['hello', 'world', 'test', 'pattern', 'match']
        for pattern in patterns_to_insert:
            pos = random.randint(0, len(base_text) - len(pattern))
            base_text = base_text[:pos] + pattern + base_text[pos + len(pattern):]
        return base_text
    
    def test_fsa_vs_regex_single_pattern(self):
        """Compare FSA vs regex for single pattern matching."""
        text = "The quick brown fox jumps over the lazy dog " * 100
        pattern = "quick"
        replacement = "QUICK"
        
        # FSA setup
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns([("p1", pattern, replacement, 1)])
        
        # Regex setup
        regex = re.compile(pattern)
        
        # Benchmark FSA
        fsa_start = time.perf_counter()
        for _ in range(1000):
            fsa_match = fsa.match(text)
        fsa_time = time.perf_counter() - fsa_start
        
        # Benchmark regex
        regex_start = time.perf_counter()
        for _ in range(1000):
            regex_match = regex.search(text)
        regex_time = time.perf_counter() - regex_start
        
        # Calculate improvement
        improvement = ((regex_time - fsa_time) / regex_time) * 100
        
        print(f"\nSingle Pattern Performance:")
        print(f"FSA time: {fsa_time:.4f}s")
        print(f"Regex time: {regex_time:.4f}s")
        print(f"FSA improvement: {improvement:.1f}%")
        
        # FSA should be at least 20% faster for simple patterns
        assert improvement > 20
    
    def test_fsa_vs_regex_multiple_patterns(self, test_patterns):
        """Compare FSA vs regex for multiple pattern matching."""
        text = generate_random_text(10000)
        
        # Add known patterns to text
        for _, pattern, _, _ in test_patterns[:10]:
            pos = random.randint(0, len(text) - len(pattern))
            text = text[:pos] + pattern + text[pos + len(pattern):]
        
        # FSA setup
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns(test_patterns)
        
        # Regex setup - compile all patterns
        regex_patterns = [(re.compile(p[1]), p[2]) for p in test_patterns]
        
        # Benchmark FSA
        fsa_start = time.perf_counter()
        fsa_matches = fsa.find_all_matches(text)
        fsa_time = time.perf_counter() - fsa_start
        
        # Benchmark regex
        regex_start = time.perf_counter()
        regex_matches = []
        for pattern, replacement in regex_patterns:
            for match in pattern.finditer(text):
                regex_matches.append((match.group(), replacement))
        regex_time = time.perf_counter() - regex_start
        
        # Calculate improvement
        improvement = ((regex_time - fsa_time) / regex_time) * 100
        
        print(f"\nMultiple Pattern Performance ({len(test_patterns)} patterns):")
        print(f"FSA time: {fsa_time:.4f}s")
        print(f"Regex time: {regex_time:.4f}s")
        print(f"FSA improvement: {improvement:.1f}%")
        print(f"FSA matches: {len(fsa_matches)}")
        print(f"Regex matches: {len(regex_matches)}")
        
        # FSA should be 50-70% faster for multiple patterns
        assert improvement > 50
    
    def test_fsa_compilation_time(self):
        """Test FSA compilation performance."""
        # Generate many patterns
        patterns = generate_patterns(1000)
        
        compiler = FSAPatternCompiler()
        
        # Measure compilation time
        start_time = time.perf_counter()
        fsa = compiler.compile_patterns(patterns)
        compile_time = time.perf_counter() - start_time
        
        print(f"\nFSA Compilation Performance:")
        print(f"Patterns: {len(patterns)}")
        print(f"Compilation time: {compile_time:.4f}s")
        print(f"Time per pattern: {compile_time / len(patterns) * 1000:.2f}ms")
        print(f"States created: {len(fsa.states)}")
        
        # Compilation should be fast (< 1s for 1000 patterns)
        assert compile_time < 1.0
    
    def test_fsa_memory_efficiency(self, test_patterns):
        """Test FSA memory efficiency."""
        import sys
        
        # Create FSA with many patterns
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns(test_patterns)
        
        # Estimate memory usage
        states_memory = sys.getsizeof(fsa.states)
        transitions_memory = sys.getsizeof(fsa.transition_table)
        total_memory = states_memory + transitions_memory
        
        print(f"\nFSA Memory Usage:")
        print(f"Patterns: {len(test_patterns)}")
        print(f"States: {len(fsa.states)}")
        print(f"Transitions: {len(fsa.transition_table)}")
        print(f"States memory: {states_memory / 1024:.2f} KB")
        print(f"Transitions memory: {transitions_memory / 1024:.2f} KB")
        print(f"Total memory: {total_memory / 1024:.2f} KB")
        print(f"Memory per pattern: {total_memory / len(test_patterns):.0f} bytes")
        
        # Memory usage should be reasonable (< 1KB per simple pattern)
        assert total_memory / len(test_patterns) < 1024
    
    def test_fsa_scalability(self):
        """Test FSA scalability with increasing pattern counts."""
        pattern_counts = [10, 50, 100, 500, 1000]
        times = []
        
        for count in pattern_counts:
            patterns = generate_patterns(count)
            text = generate_random_text(10000)
            
            compiler = FSAPatternCompiler()
            fsa = compiler.compile_patterns(patterns)
            
            # Measure matching time
            start_time = time.perf_counter()
            matches = fsa.find_all_matches(text)
            match_time = time.perf_counter() - start_time
            
            times.append(match_time)
            
            print(f"\nPatterns: {count}, Time: {match_time:.4f}s, Matches: {len(matches)}")
        
        # Check that performance scales reasonably
        # Time should not increase dramatically with pattern count
        for i in range(1, len(times)):
            ratio = times[i] / times[i-1]
            pattern_ratio = pattern_counts[i] / pattern_counts[i-1]
            
            print(f"Time ratio: {ratio:.2f}, Pattern ratio: {pattern_ratio:.2f}")
            
            # Time should scale sub-linearly with pattern count
            assert ratio < pattern_ratio
    
    def test_optimized_matcher_caching(self):
        """Test that pattern compilation caching improves performance."""
        matcher = OptimizedPatternMatcher()
        patterns = generate_patterns(100)
        
        # Add patterns
        matcher.add_patterns(patterns)
        
        # First compilation
        start_time = time.perf_counter()
        assert matcher.compile() is True
        first_compile_time = time.perf_counter() - start_time
        
        # Second compilation (should use cache)
        start_time = time.perf_counter()
        assert matcher.compile() is True
        cached_compile_time = time.perf_counter() - start_time
        
        print(f"\nCompilation Caching:")
        print(f"First compilation: {first_compile_time:.4f}s")
        print(f"Cached compilation: {cached_compile_time:.6f}s")
        print(f"Speedup: {first_compile_time / cached_compile_time:.0f}x")
        
        # Cached compilation should be at least 100x faster
        assert cached_compile_time < first_compile_time / 100
    
    def test_concurrent_matching_performance(self):
        """Test performance under concurrent load."""
        import threading
        from concurrent.futures import ThreadPoolExecutor
        
        matcher = OptimizedPatternMatcher()
        patterns = generate_patterns(50)
        matcher.add_patterns(patterns)
        
        test_texts = [generate_random_text(1000) for _ in range(100)]
        results = []
        
        def worker(text):
            match = matcher.match(text)
            return match is not None
        
        # Sequential execution
        seq_start = time.perf_counter()
        seq_results = [worker(text) for text in test_texts]
        seq_time = time.perf_counter() - seq_start
        
        # Concurrent execution
        conc_start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=4) as executor:
            conc_results = list(executor.map(worker, test_texts))
        conc_time = time.perf_counter() - conc_start
        
        print(f"\nConcurrent Performance:")
        print(f"Sequential time: {seq_time:.4f}s")
        print(f"Concurrent time: {conc_time:.4f}s")
        print(f"Speedup: {seq_time / conc_time:.2f}x")
        
        # Concurrent execution should be faster
        assert conc_time < seq_time
        # Results should be the same
        assert seq_results == conc_results


class TestRealWorldPerformance:
    """Test performance with real-world translation patterns."""
    
    def test_tau_translation_patterns(self):
        """Test with actual Tau translation patterns."""
        # Simulate real Tau translation patterns
        tau_patterns = [
            ("forall", "for all", "∀", 10),
            ("exists", "there exists", "∃", 10),
            ("implies", "implies", "→", 9),
            ("and", "and", "∧", 8),
            ("or", "or", "∨", 8),
            ("not", "not", "¬", 8),
            ("equals", "equals", "=", 7),
            ("notequals", "not equals", "≠", 7),
            ("leq", "less than or equal", "≤", 6),
            ("geq", "greater than or equal", "≥", 6),
            ("lt", "less than", "<", 5),
            ("gt", "greater than", ">", 5),
            ("in", "in", "∈", 5),
            ("notin", "not in", "∉", 5),
            ("subset", "subset", "⊆", 4),
            ("superset", "superset", "⊇", 4),
            ("union", "union", "∪", 3),
            ("intersection", "intersection", "∩", 3),
            ("emptyset", "empty set", "∅", 2),
            ("infinity", "infinity", "∞", 1)
        ]
        
        # Create realistic test text
        test_text = """
        For all x in the set, there exists a y such that x equals y.
        If x is less than y and y is less than z, then x is less than z.
        The union of A and B equals the intersection of C and D.
        For all elements in the empty set, the statement is true.
        There exists an x greater than or equal to infinity.
        """ * 10
        
        # FSA setup
        compiler = FSAPatternCompiler()
        fsa = compiler.compile_patterns(tau_patterns)
        
        # Regex setup
        regex_patterns = [(re.compile(p[1]), p[2]) for p in tau_patterns]
        
        # Benchmark FSA
        fsa_start = time.perf_counter()
        for _ in range(100):
            fsa_result, fsa_count = fsa.replace(test_text)
        fsa_time = time.perf_counter() - fsa_start
        
        # Benchmark regex
        regex_start = time.perf_counter()
        for _ in range(100):
            regex_result = test_text
            regex_count = 0
            for pattern, replacement in regex_patterns:
                regex_result, n = pattern.subn(replacement, regex_result)
                regex_count += n
        regex_time = time.perf_counter() - regex_start
        
        # Calculate improvement
        improvement = ((regex_time - fsa_time) / regex_time) * 100
        
        print(f"\nTau Translation Performance:")
        print(f"FSA time: {fsa_time:.4f}s")
        print(f"Regex time: {regex_time:.4f}s")
        print(f"FSA improvement: {improvement:.1f}%")
        print(f"Replacements made: {fsa_count}")
        
        # FSA should achieve 50-70% improvement
        assert improvement > 50
        assert improvement < 80  # Sanity check
        
        # Results should be similar (order might differ)
        assert len(fsa_result) == len(regex_result)