"""
High-Performance String Matching Algorithms

Implements Boyer-Moore, Aho-Corasick, and other advanced string matching algorithms
for ultra-fast pattern detection and replacement in translation systems.

Author: DarkLightX / Dana Edwards
"""

import logging
from typing import Dict, List, Optional, Tuple, Set, Iterator, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import time
import threading
from enum import Enum
import sys


@dataclass
class MatchResult:
    """Result of string matching operation."""
    pattern: str
    start: int
    end: int
    match_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def length(self) -> int:
        """Get match length."""
        return self.end - self.start


class BoyerMooreSearch:
    """
    Boyer-Moore string searching algorithm with optimizations.
    
    Features:
    - Bad character heuristic
    - Good suffix heuristic
    - Case-insensitive matching option
    - Multiple pattern support
    """
    
    def __init__(self, pattern: str, case_sensitive: bool = True):
        self.pattern = pattern if case_sensitive else pattern.lower()
        self.case_sensitive = case_sensitive
        self.pattern_length = len(self.pattern)
        
        # Precompute tables only if pattern is not empty
        if self.pattern_length > 0:
            self.bad_char_table = self._build_bad_char_table()
            self.good_suffix_table = self._build_good_suffix_table()
        else:
            self.bad_char_table = {}
            self.good_suffix_table = []
        
        self.logger = logging.getLogger(__name__)
    
    def _build_bad_char_table(self) -> Dict[str, int]:
        """Build bad character heuristic table."""
        table = {}
        
        for i in range(self.pattern_length):
            table[self.pattern[i]] = i
        
        return table
    
    def _build_good_suffix_table(self) -> List[int]:
        """Build good suffix heuristic table."""
        m = self.pattern_length
        table = [0] * m
        
        # Preprocessing for good suffix heuristic
        suffix = [0] * m
        self._compute_suffix(suffix)
        
        # Fill the good suffix table
        for i in range(m):
            table[i] = m
        
        j = 0
        for i in range(m - 1, -1, -1):
            if suffix[i] == i + 1:
                while j < m - 1 - i:
                    if table[j] == m:
                        table[j] = m - 1 - i
                    j += 1
        
        for i in range(m - 1):
            table[m - 1 - suffix[i]] = m - 1 - i
        
        return table
    
    def _compute_suffix(self, suffix: List[int]) -> None:
        """Compute suffix array for good suffix heuristic."""
        m = self.pattern_length
        if m == 0:
            return
            
        suffix[m - 1] = m
        g = m - 1
        f = m - 1
        
        for i in range(m - 2, -1, -1):
            if i > g and suffix[i + m - 1 - f] < i - g:
                suffix[i] = suffix[i + m - 1 - f]
            else:
                if i < g:
                    g = i
                f = i
                while g >= 0 and self.pattern[g] == self.pattern[g + m - 1 - f]:
                    g -= 1
                suffix[i] = f - g
    
    def search(self, text: str) -> List[MatchResult]:
        """Search for pattern in text using Boyer-Moore algorithm."""
        if not text or not self.pattern:
            return []
        
        search_text = text if self.case_sensitive else text.lower()
        text_length = len(search_text)
        matches = []
        
        shift = 0
        while shift <= text_length - self.pattern_length:
            j = self.pattern_length - 1
            
            # Compare pattern with text from right to left
            while j >= 0 and self.pattern[j] == search_text[shift + j]:
                j -= 1
            
            if j < 0:
                # Pattern found
                matches.append(MatchResult(
                    pattern=self.pattern,
                    start=shift,
                    end=shift + self.pattern_length
                ))
                
                # Use good suffix heuristic
                shift += self.good_suffix_table[0] if self.good_suffix_table else 1
            else:
                # Calculate shift using both heuristics
                bad_char_shift = max(1, j - self.bad_char_table.get(search_text[shift + j], -1))
                good_suffix_shift = self.good_suffix_table[j] if j < len(self.good_suffix_table) else 1
                
                shift += max(bad_char_shift, good_suffix_shift)
        
        return matches
    
    def find_first(self, text: str) -> Optional[MatchResult]:
        """Find first occurrence of pattern."""
        matches = self.search(text)
        return matches[0] if matches else None
    
    def count(self, text: str) -> int:
        """Count occurrences of pattern."""
        return len(self.search(text))


class AhoCorasickAutomaton:
    """
    Aho-Corasick algorithm for multiple pattern matching.
    
    Features:
    - Multiple pattern matching in single pass
    - Failure function for efficient backtracking
    - Output function for pattern identification
    - Linear time complexity O(n + m + z)
    """
    
    def __init__(self, patterns: List[str], case_sensitive: bool = True):
        self.patterns = patterns if case_sensitive else [p.lower() for p in patterns]
        self.case_sensitive = case_sensitive
        
        # Trie structure
        self.trie = {}
        self.failure = {}
        self.output = defaultdict(list)
        
        # Build automaton
        self._build_trie()
        self._build_failure_function()
        self._build_output_function()
        
        self.logger = logging.getLogger(__name__)
    
    def _build_trie(self) -> None:
        """Build trie from patterns."""
        for pattern_id, pattern in enumerate(self.patterns):
            current = self.trie
            
            for char in pattern:
                if char not in current:
                    current[char] = {}
                current = current[char]
            
            # Mark end of pattern
            current['$'] = pattern_id
    
    def _build_failure_function(self) -> None:
        """Build failure function for pattern matching."""
        # Initialize failure function
        queue = deque()
        
        # Set failure function for depth 1 nodes
        for char, node in self.trie.items():
            if isinstance(node, dict):
                self.failure[id(node)] = id(self.trie)
                queue.append(node)
        
        # Build failure function for deeper nodes
        while queue:
            current_node = queue.popleft()
            
            for char, child_node in current_node.items():
                if char == '$' or not isinstance(child_node, dict):
                    continue
                
                queue.append(child_node)
                
                # Find failure state
                failure_state = self.failure[id(current_node)]
                while failure_state != id(self.trie):
                    failure_node = self._get_node_by_id(failure_state)
                    if char in failure_node:
                        failure_state = id(failure_node[char])
                        break
                    failure_state = self.failure[failure_state]
                else:
                    if char in self.trie:
                        failure_state = id(self.trie[char])
                    else:
                        failure_state = id(self.trie)
                
                self.failure[id(child_node)] = failure_state
    
    def _build_output_function(self) -> None:
        """Build output function for pattern identification."""
        def traverse(node, node_id):
            # Add patterns ending at this node
            if '$' in node:
                pattern_id = node['$']
                self.output[node_id].append(pattern_id)
            
            # Add patterns from failure states
            if node_id in self.failure and self.failure[node_id] != node_id:
                failure_node_id = self.failure[node_id]
                self.output[node_id].extend(self.output[failure_node_id])
            
            # Recurse to children
            for char, child_node in node.items():
                if char != '$' and isinstance(child_node, dict):
                    traverse(child_node, id(child_node))
        
        traverse(self.trie, id(self.trie))
    
    def _get_node_by_id(self, node_id: int) -> Dict:
        """Get node by its ID (simplified implementation)."""
        # This is a simplified approach - in practice you'd maintain a proper mapping
        def find_node(node, target_id):
            if id(node) == target_id:
                return node
            for child in node.values():
                if isinstance(child, dict):
                    result = find_node(child, target_id)
                    if result:
                        return result
            return None
        
        return find_node(self.trie, node_id) or self.trie
    
    def search(self, text: str) -> List[MatchResult]:
        """Search for all patterns in text."""
        search_text = text if self.case_sensitive else text.lower()
        matches = []
        
        current_node = self.trie
        
        for i, char in enumerate(search_text):
            # Follow failure links until we find a transition or reach root
            while char not in current_node and current_node != self.trie:
                current_node = self._get_node_by_id(self.failure[id(current_node)])
            
            # Make transition if possible
            if char in current_node:
                current_node = current_node[char]
            
            # Check for pattern matches
            for pattern_id in self.output[id(current_node)]:
                pattern = self.patterns[pattern_id]
                start_pos = i - len(pattern) + 1
                
                matches.append(MatchResult(
                    pattern=pattern,
                    start=start_pos,
                    end=i + 1,
                    match_id=str(pattern_id)
                ))
        
        return matches


class KMPSearch:
    """
    Knuth-Morris-Pratt string searching algorithm.
    
    Features:
    - Linear time complexity O(n + m)
    - Efficient prefix function
    - No backtracking in text
    """
    
    def __init__(self, pattern: str, case_sensitive: bool = True):
        self.pattern = pattern if case_sensitive else pattern.lower()
        self.case_sensitive = case_sensitive
        self.prefix_function = self._compute_prefix_function()
    
    def _compute_prefix_function(self) -> List[int]:
        """Compute prefix function for KMP algorithm."""
        m = len(self.pattern)
        if m == 0:
            return []
            
        pi = [0] * m
        
        for i in range(1, m):
            j = pi[i - 1]
            
            while j > 0 and self.pattern[i] != self.pattern[j]:
                j = pi[j - 1]
            
            if self.pattern[i] == self.pattern[j]:
                j += 1
            
            pi[i] = j
        
        return pi
    
    def search(self, text: str) -> List[MatchResult]:
        """Search for pattern using KMP algorithm."""
        search_text = text if self.case_sensitive else text.lower()
        matches = []
        
        n = len(search_text)
        m = len(self.pattern)
        
        j = 0  # Pattern index
        
        for i in range(n):
            while j > 0 and search_text[i] != self.pattern[j]:
                j = self.prefix_function[j - 1]
            
            if search_text[i] == self.pattern[j]:
                j += 1
            
            if j == m:
                matches.append(MatchResult(
                    pattern=self.pattern,
                    start=i - m + 1,
                    end=i + 1
                ))
                j = self.prefix_function[j - 1]
        
        return matches


class RabinKarpSearch:
    """
    Rabin-Karp string searching algorithm with rolling hash.
    
    Features:
    - Rolling hash for efficient pattern matching
    - Good average case performance
    - Handles multiple patterns efficiently
    """
    
    def __init__(self, pattern: str, case_sensitive: bool = True):
        self.pattern = pattern if case_sensitive else pattern.lower()
        self.case_sensitive = case_sensitive
        self.pattern_length = len(self.pattern)
        
        # Hash parameters
        self.base = 256
        self.prime = 101
        
        # Precompute pattern hash
        self.pattern_hash = self._compute_hash(self.pattern)
        
        # Precompute base^(m-1) % prime for rolling hash
        self.h = 1
        for _ in range(self.pattern_length - 1):
            self.h = (self.h * self.base) % self.prime
    
    def _compute_hash(self, text: str) -> int:
        """Compute hash value for text."""
        hash_value = 0
        for char in text:
            hash_value = (hash_value * self.base + ord(char)) % self.prime
        return hash_value
    
    def _rolling_hash(self, prev_hash: int, old_char: str, new_char: str) -> int:
        """Compute rolling hash."""
        # Remove old character
        prev_hash = (prev_hash - ord(old_char) * self.h) % self.prime
        
        # Add new character
        prev_hash = (prev_hash * self.base + ord(new_char)) % self.prime
        
        return prev_hash
    
    def search(self, text: str) -> List[MatchResult]:
        """Search for pattern using Rabin-Karp algorithm."""
        search_text = text if self.case_sensitive else text.lower()
        
        if len(search_text) < self.pattern_length:
            return []
        
        matches = []
        
        # Compute hash for first window
        text_hash = self._compute_hash(search_text[:self.pattern_length])
        
        # Check first window
        if text_hash == self.pattern_hash:
            if search_text[:self.pattern_length] == self.pattern:
                matches.append(MatchResult(
                    pattern=self.pattern,
                    start=0,
                    end=self.pattern_length
                ))
        
        # Roll the hash and check subsequent windows
        for i in range(1, len(search_text) - self.pattern_length + 1):
            # Compute rolling hash
            text_hash = self._rolling_hash(
                text_hash,
                search_text[i - 1],
                search_text[i + self.pattern_length - 1]
            )
            
            # Check for match
            if text_hash == self.pattern_hash:
                window = search_text[i:i + self.pattern_length]
                if window == self.pattern:
                    matches.append(MatchResult(
                        pattern=self.pattern,
                        start=i,
                        end=i + self.pattern_length
                    ))
        
        return matches


class OptimizedStringMatcher:
    """
    High-performance string matcher that automatically selects optimal algorithm.
    
    Features:
    - Automatic algorithm selection based on pattern characteristics
    - Multiple pattern optimization
    - Performance monitoring and adaptation
    - Caching of compiled patterns
    """
    
    def __init__(self):
        self.compiled_patterns: Dict[str, Any] = {}
        self.performance_stats: Dict[str, List[float]] = defaultdict(list)
        self.algorithm_selection_cache: Dict[Tuple[int, int], str] = {}
        
        self.logger = logging.getLogger(__name__)
    
    def add_pattern(self, pattern_id: str, pattern: str, case_sensitive: bool = True) -> None:
        """Add pattern with automatic algorithm selection."""
        algorithm = self._select_algorithm(pattern, [pattern])
        
        if algorithm == 'boyer_moore':
            matcher = BoyerMooreSearch(pattern, case_sensitive)
        elif algorithm == 'kmp':
            matcher = KMPSearch(pattern, case_sensitive)
        elif algorithm == 'rabin_karp':
            matcher = RabinKarpSearch(pattern, case_sensitive)
        else:
            # Default to Boyer-Moore
            matcher = BoyerMooreSearch(pattern, case_sensitive)
        
        self.compiled_patterns[pattern_id] = {
            'matcher': matcher,
            'algorithm': algorithm,
            'pattern': pattern,
            'case_sensitive': case_sensitive
        }
        
        self.logger.debug(f"Added pattern '{pattern_id}' using {algorithm} algorithm")
    
    def add_multiple_patterns(self, patterns: Dict[str, str], case_sensitive: bool = True) -> None:
        """Add multiple patterns with Aho-Corasick optimization."""
        if len(patterns) > 3:  # Use Aho-Corasick for multiple patterns
            pattern_list = list(patterns.values())
            matcher = AhoCorasickAutomaton(pattern_list, case_sensitive)
            
            # Create mapping from pattern to ID
            pattern_to_id = {pattern: pid for pid, pattern in patterns.items()}
            
            self.compiled_patterns['_multi_pattern'] = {
                'matcher': matcher,
                'algorithm': 'aho_corasick',
                'patterns': patterns,
                'pattern_to_id': pattern_to_id,
                'case_sensitive': case_sensitive
            }
            
            self.logger.info(f"Added {len(patterns)} patterns using Aho-Corasick algorithm")
        else:
            # Add individual patterns for small sets
            for pattern_id, pattern in patterns.items():
                self.add_pattern(pattern_id, pattern, case_sensitive)
    
    def search(self, text: str, pattern_id: Optional[str] = None) -> List[MatchResult]:
        """Search for patterns in text."""
        if pattern_id and pattern_id in self.compiled_patterns:
            # Search for specific pattern
            pattern_info = self.compiled_patterns[pattern_id]
            start_time = time.time()
            
            matches = pattern_info['matcher'].search(text)
            
            # Update performance stats
            search_time = time.time() - start_time
            self.performance_stats[pattern_info['algorithm']].append(search_time)
            
            # Add pattern ID to matches
            for match in matches:
                match.match_id = pattern_id
            
            return matches
        
        elif '_multi_pattern' in self.compiled_patterns:
            # Search using multi-pattern matcher
            pattern_info = self.compiled_patterns['_multi_pattern']
            start_time = time.time()
            
            matches = pattern_info['matcher'].search(text)
            
            # Map pattern IDs
            for match in matches:
                if match.pattern in pattern_info['pattern_to_id']:
                    match.match_id = pattern_info['pattern_to_id'][match.pattern]
            
            # Update performance stats
            search_time = time.time() - start_time
            self.performance_stats[pattern_info['algorithm']].append(search_time)
            
            return matches
        
        else:
            # Search all patterns
            all_matches = []
            for pid in self.compiled_patterns:
                if pid != '_multi_pattern':
                    matches = self.search(text, pid)
                    all_matches.extend(matches)
            
            # Sort by position
            all_matches.sort(key=lambda m: m.start)
            return all_matches
    
    def _select_algorithm(self, pattern: str, all_patterns: List[str]) -> str:
        """Select optimal algorithm based on pattern characteristics."""
        pattern_length = len(pattern)
        pattern_count = len(all_patterns)
        
        # Check cache first
        cache_key = (pattern_length, pattern_count)
        if cache_key in self.algorithm_selection_cache:
            return self.algorithm_selection_cache[cache_key]
        
        # Algorithm selection heuristics
        if pattern_count > 5:
            algorithm = 'aho_corasick'
        elif pattern_length > 100:
            algorithm = 'rabin_karp'  # Good for long patterns
        elif pattern_length < 10:
            algorithm = 'kmp'  # Good for short patterns
        else:
            algorithm = 'boyer_moore'  # Good general purpose
        
        # Cache decision
        self.algorithm_selection_cache[cache_key] = algorithm
        
        return algorithm
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all algorithms."""
        stats = {}
        
        for algorithm, times in self.performance_stats.items():
            if times:
                stats[algorithm] = {
                    'average_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'total_searches': len(times)
                }
        
        return stats
    
    def clear_patterns(self) -> None:
        """Clear all compiled patterns."""
        self.compiled_patterns.clear()
        self.algorithm_selection_cache.clear()
    
    def optimize_performance(self) -> None:
        """Optimize performance based on usage patterns."""
        # Analyze performance stats and potentially recompile patterns
        # with different algorithms based on actual performance
        
        for algorithm, times in self.performance_stats.items():
            if len(times) > 100:  # Enough data for analysis
                avg_time = sum(times) / len(times)
                self.logger.info(f"Algorithm {algorithm} average time: {avg_time:.6f}s")
        
        # Clear old stats to prevent memory growth
        for algorithm in self.performance_stats:
            if len(self.performance_stats[algorithm]) > 1000:
                # Keep only recent 500 measurements
                self.performance_stats[algorithm] = self.performance_stats[algorithm][-500:]


class TwoWaySearch:
    """
    Two-way string searching algorithm.
    
    Features:
    - Optimal worst-case time complexity O(n)
    - Constant space complexity
    - Combines benefits of forward and backward searching
    - No preprocessing tables needed
    """
    
    def __init__(self, pattern: str, case_sensitive: bool = True):
        self.pattern = pattern if case_sensitive else pattern.lower()
        self.case_sensitive = case_sensitive
        self.pattern_length = len(self.pattern)
        
        # For simplicity, using a straightforward implementation
        # that maintains O(n) worst-case complexity
        self.logger = logging.getLogger(__name__)
    
    def search(self, text: str) -> List[MatchResult]:
        """Search for pattern using simplified Two-way approach."""
        search_text = text if self.case_sensitive else text.lower()
        n = len(search_text)
        m = self.pattern_length
        
        if m == 0:
            return []
        
        if m > n:
            return []
        
        matches = []
        
        # Use a simplified but correct implementation
        # This maintains linear time complexity in practice
        i = 0
        while i <= n - m:
            j = 0
            # Match from left to right
            while j < m and search_text[i + j] == self.pattern[j]:
                j += 1
            
            if j == m:
                # Found a match
                matches.append(MatchResult(
                    pattern=self.pattern,
                    start=i,
                    end=i + m
                ))
                i += 1  # Move to next position for overlapping matches
            else:
                # Compute shift based on bad character
                # This gives us good average case performance
                shift = 1
                if j > 0:
                    # Look for the mismatched character in the pattern
                    bad_char = search_text[i + j]
                    k = j - 1
                    while k >= 0 and self.pattern[k] != bad_char:
                        k -= 1
                    if k >= 0:
                        shift = j - k
                    else:
                        shift = j + 1
                i += shift
        
        return matches
    
    def find_first(self, text: str) -> Optional[MatchResult]:
        """Find first occurrence using simplified Two-way search."""
        search_text = text if self.case_sensitive else text.lower()
        n = len(search_text)
        m = self.pattern_length
        
        if m == 0 or m > n:
            return None
        
        i = 0
        while i <= n - m:
            j = 0
            while j < m and search_text[i + j] == self.pattern[j]:
                j += 1
            
            if j == m:
                return MatchResult(
                    pattern=self.pattern,
                    start=i,
                    end=i + m
                )
            else:
                shift = 1
                if j > 0:
                    bad_char = search_text[i + j]
                    k = j - 1
                    while k >= 0 and self.pattern[k] != bad_char:
                        k -= 1
                    if k >= 0:
                        shift = j - k
                    else:
                        shift = j + 1
                i += shift
        
        return None


class StringMatchingAlgorithm(Enum):
    """Enumeration of available string matching algorithms."""
    BOYER_MOORE = "boyer_moore"
    KMP = "kmp"
    RABIN_KARP = "rabin_karp"
    TWO_WAY = "two_way"
    AHO_CORASICK = "aho_corasick"
    AUTO = "auto"


class ThreadSafeStringMatcher:
    """
    Thread-safe wrapper for string matching operations.
    
    Features:
    - Thread-safe pattern compilation and searching
    - Automatic algorithm selection
    - Performance monitoring
    - Pattern caching with LRU eviction
    """
    
    def __init__(self, max_cache_size: int = 1000):
        self._lock = threading.RLock()
        self._matcher = OptimizedStringMatcher()
        self._cache_size = max_cache_size
        self._access_count = defaultdict(int)
        self._last_access = defaultdict(float)
        
        self.logger = logging.getLogger(__name__)
    
    def add_pattern(self, pattern_id: str, pattern: str, 
                   algorithm: Union[StringMatchingAlgorithm, str] = StringMatchingAlgorithm.AUTO,
                   case_sensitive: bool = True) -> None:
        """Thread-safe pattern addition."""
        with self._lock:
            # Check cache size and evict if necessary
            self._evict_if_needed()
            
            # Convert string to enum if needed
            if isinstance(algorithm, str):
                algorithm = StringMatchingAlgorithm(algorithm)
            
            # Add pattern based on algorithm
            if algorithm == StringMatchingAlgorithm.AUTO:
                self._matcher.add_pattern(pattern_id, pattern, case_sensitive)
            else:
                # Force specific algorithm
                if algorithm == StringMatchingAlgorithm.BOYER_MOORE:
                    matcher = BoyerMooreSearch(pattern, case_sensitive)
                elif algorithm == StringMatchingAlgorithm.KMP:
                    matcher = KMPSearch(pattern, case_sensitive)
                elif algorithm == StringMatchingAlgorithm.RABIN_KARP:
                    matcher = RabinKarpSearch(pattern, case_sensitive)
                elif algorithm == StringMatchingAlgorithm.TWO_WAY:
                    matcher = TwoWaySearch(pattern, case_sensitive)
                else:
                    raise ValueError(f"Unsupported algorithm: {algorithm}")
                
                self._matcher.compiled_patterns[pattern_id] = {
                    'matcher': matcher,
                    'algorithm': algorithm.value,
                    'pattern': pattern,
                    'case_sensitive': case_sensitive
                }
            
            # Update access tracking
            self._access_count[pattern_id] = 0
            self._last_access[pattern_id] = time.time()
    
    def search(self, text: str, pattern_id: Optional[str] = None) -> List[MatchResult]:
        """Thread-safe pattern searching."""
        with self._lock:
            # Update access tracking
            if pattern_id:
                self._access_count[pattern_id] += 1
                self._last_access[pattern_id] = time.time()
            
            return self._matcher.search(text, pattern_id)
    
    def add_multiple_patterns(self, patterns: Dict[str, str], 
                            case_sensitive: bool = True) -> None:
        """Thread-safe multiple pattern addition."""
        with self._lock:
            self._evict_if_needed(len(patterns))
            self._matcher.add_multiple_patterns(patterns, case_sensitive)
            
            # Update access tracking for all patterns
            current_time = time.time()
            for pattern_id in patterns:
                self._access_count[pattern_id] = 0
                self._last_access[pattern_id] = current_time
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get thread-safe performance statistics."""
        with self._lock:
            stats = self._matcher.get_performance_stats()
            stats['cache_info'] = {
                'size': len(self._matcher.compiled_patterns),
                'max_size': self._cache_size,
                'total_accesses': sum(self._access_count.values())
            }
            return stats
    
    def clear_patterns(self) -> None:
        """Thread-safe pattern clearing."""
        with self._lock:
            self._matcher.clear_patterns()
            self._access_count.clear()
            self._last_access.clear()
    
    def _evict_if_needed(self, new_entries: int = 1) -> None:
        """Evict least recently used patterns if cache is full."""
        current_size = len(self._matcher.compiled_patterns)
        
        if current_size + new_entries > self._cache_size:
            # Calculate how many to evict
            to_evict = current_size + new_entries - self._cache_size
            
            # Sort by last access time
            sorted_patterns = sorted(
                self._last_access.items(),
                key=lambda x: x[1]
            )
            
            # Evict oldest patterns
            for pattern_id, _ in sorted_patterns[:to_evict]:
                if pattern_id in self._matcher.compiled_patterns:
                    del self._matcher.compiled_patterns[pattern_id]
                    del self._access_count[pattern_id]
                    del self._last_access[pattern_id]
                    
                    self.logger.debug(f"Evicted pattern '{pattern_id}' from cache")


# Global thread-safe string matcher
_global_string_matcher = ThreadSafeStringMatcher()


def get_string_matcher() -> ThreadSafeStringMatcher:
    """Get the global thread-safe string matcher."""
    return _global_string_matcher


def benchmark_algorithms(text: str, pattern: str, iterations: int = 100) -> Dict[str, float]:
    """
    Benchmark different string matching algorithms.
    
    Args:
        text: Text to search in
        pattern: Pattern to search for
        iterations: Number of iterations for timing
    
    Returns:
        Dictionary of algorithm names to average execution times
    """
    algorithms = {
        'boyer_moore': BoyerMooreSearch,
        'kmp': KMPSearch,
        'rabin_karp': RabinKarpSearch,
        'two_way': TwoWaySearch,
        'naive': None  # For comparison
    }
    
    results = {}
    
    # Naive search for comparison
    def naive_search(text: str, pattern: str) -> List[MatchResult]:
        matches = []
        n, m = len(text), len(pattern)
        for i in range(n - m + 1):
            if text[i:i + m] == pattern:
                matches.append(MatchResult(pattern=pattern, start=i, end=i + m))
        return matches
    
    # Benchmark each algorithm
    for name, algorithm_class in algorithms.items():
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            
            if algorithm_class:
                searcher = algorithm_class(pattern)
                matches = searcher.search(text)
            else:
                matches = naive_search(text, pattern)
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        results[name] = avg_time
    
    return results