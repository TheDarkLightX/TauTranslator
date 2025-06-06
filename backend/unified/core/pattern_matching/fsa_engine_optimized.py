"""
Optimized Finite State Automaton Pattern Matching Engine

Implements high-performance pattern matching using Aho-Corasick algorithm
for multiple pattern matching with O(n + m) complexity.

Author: DarkLightX / Dana Edwards
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Set, Any, Union, Deque
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict, deque


class StateType(Enum):
    """Types of FSA states."""
    ROOT = "root"
    INTERMEDIATE = "intermediate"
    ACCEPTING = "accepting"


@dataclass(frozen=True)
class PatternInfo:
    """Information about a matched pattern."""
    pattern_id: str
    pattern: str
    replacement: str
    priority: int
    length: int


@dataclass
class MatchResult:
    """Result of pattern matching operation."""
    matched: bool
    pattern_id: Optional[str] = None
    start_pos: int = 0
    end_pos: int = 0
    matched_text: str = ""
    replacement: Optional[str] = None
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TrieNode:
    """Node in the trie structure for pattern storage."""
    
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.failure_link: Optional['TrieNode'] = None
        self.output_link: Optional['TrieNode'] = None
        self.patterns: List[PatternInfo] = []
        self.is_accepting = False
    
    def add_child(self, char: str) -> 'TrieNode':
        """Add or get child node for character."""
        if char not in self.children:
            self.children[char] = TrieNode()
        return self.children[char]
    
    def get_child(self, char: str) -> Optional['TrieNode']:
        """Get child node for character."""
        return self.children.get(char)
    
    def add_pattern(self, pattern_info: PatternInfo) -> None:
        """Add pattern to this node."""
        self.patterns.append(pattern_info)
        self.is_accepting = True
        # Sort by priority (descending) and length (descending)
        self.patterns.sort(key=lambda p: (p.priority, p.length), reverse=True)


class AhoCorasickFSA:
    """
    Optimized FSA using Aho-Corasick algorithm for efficient multi-pattern matching.
    
    Features:
    - O(n + m) complexity where n is text length and m is total pattern length
    - Efficient failure function for fast state transitions
    - Support for overlapping patterns
    - Priority-based pattern selection
    """
    
    def __init__(self):
        self.root = TrieNode()
        self.compiled = False
        self.pattern_count = 0
        self.logger = logging.getLogger(__name__)
    
    def add_pattern(self, pattern_id: str, pattern: str, replacement: str, priority: int) -> None:
        """Add a pattern to the FSA."""
        if not pattern:
            return
        
        node = self.root
        for char in pattern:
            node = node.add_child(char)
        
        pattern_info = PatternInfo(
            pattern_id=pattern_id,
            pattern=pattern,
            replacement=replacement,
            priority=priority,
            length=len(pattern)
        )
        node.add_pattern(pattern_info)
        self.pattern_count += 1
        self.compiled = False
    
    def compile(self) -> None:
        """Build failure function using BFS."""
        if self.compiled:
            return
        
        # Initialize failure links for depth 1
        queue: Deque[TrieNode] = deque()
        for child in self.root.children.values():
            child.failure_link = self.root
            queue.append(child)
        
        # Build failure links for remaining nodes
        while queue:
            current = queue.popleft()
            
            for char, child in current.children.items():
                queue.append(child)
                
                # Find failure link
                failure = current.failure_link
                while failure is not None and char not in failure.children:
                    failure = failure.failure_link
                
                if failure is None:
                    child.failure_link = self.root
                else:
                    child.failure_link = failure.children[char]
                
                # Build output link
                if child.failure_link.is_accepting:
                    child.output_link = child.failure_link
                else:
                    child.output_link = child.failure_link.output_link
        
        self.compiled = True
        self.logger.debug(f"Compiled FSA with {self.pattern_count} patterns")
    
    def _get_all_patterns_at_node(self, node: TrieNode) -> List[PatternInfo]:
        """Get all patterns at a node including those from output links."""
        patterns = list(node.patterns)
        
        # Follow output links
        output_node = node.output_link
        while output_node:
            patterns.extend(output_node.patterns)
            output_node = output_node.output_link
        
        # Sort by priority and length
        patterns.sort(key=lambda p: (p.priority, p.length), reverse=True)
        return patterns
    
    def search(self, text: str) -> List[MatchResult]:
        """Search for all pattern matches in text."""
        if not self.compiled:
            self.compile()
        
        matches = []
        node = self.root
        
        for i, char in enumerate(text):
            # Follow failure links until we find a match or reach root
            while node != self.root and char not in node.children:
                node = node.failure_link
            
            if char in node.children:
                node = node.children[char]
            else:
                node = self.root
            
            # Check for matches at current position
            if node.is_accepting or node.output_link:
                patterns = self._get_all_patterns_at_node(node)
                for pattern_info in patterns:
                    match = MatchResult(
                        matched=True,
                        pattern_id=pattern_info.pattern_id,
                        start_pos=i - pattern_info.length + 1,
                        end_pos=i + 1,
                        matched_text=text[i - pattern_info.length + 1:i + 1],
                        replacement=pattern_info.replacement,
                        priority=pattern_info.priority
                    )
                    matches.append(match)
        
        return matches
    
    def match(self, text: str, start_pos: int = 0) -> Optional[MatchResult]:
        """Find first match in text."""
        if not self.compiled:
            self.compile()
        
        node = self.root
        
        for i in range(start_pos, len(text)):
            char = text[i]
            
            # Follow failure links
            while node != self.root and char not in node.children:
                node = node.failure_link
            
            if char in node.children:
                node = node.children[char]
            else:
                node = self.root
            
            # Check for matches
            if node.is_accepting or node.output_link:
                patterns = self._get_all_patterns_at_node(node)
                if patterns:
                    # Return highest priority match
                    pattern_info = patterns[0]
                    return MatchResult(
                        matched=True,
                        pattern_id=pattern_info.pattern_id,
                        start_pos=i - pattern_info.length + 1,
                        end_pos=i + 1,
                        matched_text=text[i - pattern_info.length + 1:i + 1],
                        replacement=pattern_info.replacement,
                        priority=pattern_info.priority
                    )
        
        return None
    
    def find_all_matches(self, text: str) -> List[MatchResult]:
        """Find all non-overlapping matches in text."""
        all_matches = self.search(text)
        
        if not all_matches:
            return []
        
        # Sort by start position and priority
        all_matches.sort(key=lambda m: (m.start_pos, -m.priority, -len(m.matched_text)))
        
        # Filter out overlapping matches
        non_overlapping = []
        last_end = -1
        
        for match in all_matches:
            if match.start_pos >= last_end:
                non_overlapping.append(match)
                last_end = match.end_pos
        
        return non_overlapping
    
    def replace(self, text: str, max_replacements: Optional[int] = None) -> Tuple[str, int]:
        """Replace patterns in text."""
        matches = self.find_all_matches(text)
        
        if not matches:
            return text, 0
        
        if max_replacements:
            matches = matches[:max_replacements]
        
        # Build result string
        result = []
        last_pos = 0
        
        for match in matches:
            result.append(text[last_pos:match.start_pos])
            result.append(match.replacement)
            last_pos = match.end_pos
        
        result.append(text[last_pos:])
        
        return ''.join(result), len(matches)


class OptimizedFSAPatternCompiler:
    """Compiles patterns into optimized Aho-Corasick FSA."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compile_patterns(self, patterns: List[Tuple[str, str, str, int]]) -> AhoCorasickFSA:
        """Compile patterns into optimized FSA."""
        fsa = AhoCorasickFSA()
        
        for pattern_id, source, replacement, priority in patterns:
            fsa.add_pattern(pattern_id, source, replacement, priority)
        
        fsa.compile()
        self.logger.info(f"Compiled {len(patterns)} patterns into optimized FSA")
        
        return fsa


class OptimizedPatternMatcher:
    """
    High-performance pattern matcher using optimized FSA.
    
    Features:
    - Aho-Corasick algorithm for O(n + m) complexity
    - Pattern caching and recompilation
    - Performance metrics
    - Thread-safe operations
    """
    
    def __init__(self):
        self.fsa: Optional[AhoCorasickFSA] = None
        self.compiler = OptimizedFSAPatternCompiler()
        self.patterns: List[Tuple[str, str, str, int]] = []
        self.compiled_hash: Optional[str] = None
        self._lock = threading.RLock()
        
        # Performance metrics
        self.match_count = 0
        self.total_match_time = 0.0
        self.cache_hits = 0
        self.cache_misses = 0
        
        self.logger = logging.getLogger(__name__)
    
    def add_patterns(self, patterns: List[Tuple[str, str, str, int]]) -> None:
        """Add patterns to matcher."""
        with self._lock:
            self.patterns.extend(patterns)
            self.fsa = None
            self.compiled_hash = None
    
    def clear_patterns(self) -> None:
        """Clear all patterns."""
        with self._lock:
            self.patterns.clear()
            self.fsa = None
            self.compiled_hash = None
    
    def compile(self, force: bool = False) -> bool:
        """Compile patterns into FSA if needed."""
        with self._lock:
            if not self.patterns:
                return False
            
            # Check if compilation is needed
            current_hash = self._calculate_patterns_hash()
            if not force and self.compiled_hash == current_hash and self.fsa:
                self.cache_hits += 1
                return True
            
            self.cache_misses += 1
            start_time = time.time()
            
            try:
                self.fsa = self.compiler.compile_patterns(self.patterns)
                self.compiled_hash = current_hash
                
                compile_time = time.time() - start_time
                self.logger.info(f"Compiled {len(self.patterns)} patterns in {compile_time:.3f}s")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Pattern compilation failed: {e}")
                return False
    
    def match(self, text: str) -> Optional[MatchResult]:
        """Find first match in text."""
        if not self._ensure_compiled():
            return None
        
        start_time = time.time()
        
        with self._lock:
            result = self.fsa.match(text)
            
            # Update metrics
            self.match_count += 1
            self.total_match_time += time.time() - start_time
            
            return result
    
    def find_all_matches(self, text: str) -> List[MatchResult]:
        """Find all matches in text."""
        if not self._ensure_compiled():
            return []
        
        start_time = time.time()
        
        with self._lock:
            results = self.fsa.find_all_matches(text)
            
            # Update metrics
            self.match_count += 1
            self.total_match_time += time.time() - start_time
            
            return results
    
    def replace(self, text: str, max_replacements: Optional[int] = None) -> Tuple[str, int]:
        """Replace patterns in text."""
        if not self._ensure_compiled():
            return text, 0
        
        start_time = time.time()
        
        with self._lock:
            result, count = self.fsa.replace(text, max_replacements)
            
            # Update metrics
            self.match_count += 1
            self.total_match_time += time.time() - start_time
            
            return result, count
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        with self._lock:
            avg_match_time = (self.total_match_time / self.match_count 
                            if self.match_count > 0 else 0.0)
            
            return {
                'total_matches': self.match_count,
                'total_match_time': self.total_match_time,
                'average_match_time': avg_match_time,
                'patterns_count': len(self.patterns),
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'cache_hit_rate': (self.cache_hits / (self.cache_hits + self.cache_misses) * 100
                                 if (self.cache_hits + self.cache_misses) > 0 else 0.0)
            }
    
    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        with self._lock:
            self.match_count = 0
            self.total_match_time = 0.0
            self.cache_hits = 0
            self.cache_misses = 0
    
    def _ensure_compiled(self) -> bool:
        """Ensure FSA is compiled."""
        if self.fsa is None:
            return self.compile()
        return True
    
    def _calculate_patterns_hash(self) -> str:
        """Calculate hash of current patterns for change detection."""
        import hashlib
        pattern_str = str(sorted(self.patterns))
        return hashlib.md5(pattern_str.encode()).hexdigest()