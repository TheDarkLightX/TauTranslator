"""
Trie Data Structure for Efficient Pattern and Keyword Matching
=============================================================

Implements a high-performance Trie (prefix tree) for O(k) string
operations where k is the length of the string.

Author: DarkLightX / Dana Edwards
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Iterator
from dataclasses import dataclass, field
import re


@dataclass
class TrieNode:
    """
    Node in the Trie data structure.
    
    Attributes:
        children: Dictionary mapping characters to child nodes
        is_end: Whether this node represents the end of a word
        value: Optional value associated with this word
        frequency: Usage frequency for adaptive ordering
    """
    children: Dict[str, 'TrieNode'] = field(default_factory=dict)
    is_end: bool = False
    value: Optional[Any] = None
    frequency: int = 0


class Trie:
    """
    High-performance Trie implementation for string operations.
    
    Features:
    - O(k) insertion, deletion, and lookup
    - Prefix matching and autocomplete
    - Frequency tracking for optimization
    - Memory-efficient with node sharing
    """
    
    def __init__(self, case_sensitive: bool = True):
        """
        Initialize the Trie.
        
        Args:
            case_sensitive: Whether matches should be case-sensitive
        """
        self.root = TrieNode()
        self.case_sensitive = case_sensitive
        self._word_count = 0
        self._node_count = 1  # Root node
    
    def _normalize(self, word: str) -> str:
        """Normalize word based on case sensitivity setting."""
        return word if self.case_sensitive else word.lower()
    
    def insert(self, word: str, value: Optional[Any] = None) -> None:
        """
        Insert a word into the Trie with optional associated value.
        
        Args:
            word: Word to insert
            value: Optional value to associate with the word
            
        Time Complexity: O(k) where k is the length of the word
        """
        word = self._normalize(word)
        node = self.root
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
                self._node_count += 1
            node = node.children[char]
        
        if not node.is_end:
            self._word_count += 1
        
        node.is_end = True
        node.value = value
        node.frequency += 1
    
    def search(self, word: str) -> bool:
        """
        Check if a word exists in the Trie.
        
        Args:
            word: Word to search for
            
        Returns:
            True if word exists, False otherwise
            
        Time Complexity: O(k)
        """
        word = self._normalize(word)
        node = self._find_node(word)
        return node is not None and node.is_end
    
    def get(self, word: str) -> Optional[Any]:
        """
        Get the value associated with a word.
        
        Args:
            word: Word to look up
            
        Returns:
            Associated value if word exists, None otherwise
            
        Time Complexity: O(k)
        """
        word = self._normalize(word)
        node = self._find_node(word)
        return node.value if node and node.is_end else None
    
    def delete(self, word: str) -> bool:
        """
        Delete a word from the Trie.
        
        Args:
            word: Word to delete
            
        Returns:
            True if word was deleted, False if not found
            
        Time Complexity: O(k)
        """
        word = self._normalize(word)
        
        def _delete_recursive(node: TrieNode, word: str, index: int) -> bool:
            if index == len(word):
                if not node.is_end:
                    return False
                node.is_end = False
                node.value = None
                self._word_count -= 1
                return len(node.children) == 0
            
            char = word[index]
            if char not in node.children:
                return False
            
            should_delete_child = _delete_recursive(node.children[char], word, index + 1)
            
            if should_delete_child:
                del node.children[char]
                self._node_count -= 1
                return not node.is_end and len(node.children) == 0
            
            return False
        
        return _delete_recursive(self.root, word, 0)
    
    def starts_with(self, prefix: str) -> List[str]:
        """
        Find all words that start with the given prefix.
        
        Args:
            prefix: Prefix to search for
            
        Returns:
            List of words with the given prefix
            
        Time Complexity: O(p + n) where p is prefix length, n is number of results
        """
        prefix = self._normalize(prefix)
        node = self._find_node(prefix)
        
        if not node:
            return []
        
        results = []
        self._collect_words(node, prefix, results)
        
        # Sort by frequency for better suggestions
        results.sort(key=lambda x: x[1], reverse=True)
        return [word for word, _ in results]
    
    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        """Find the node corresponding to a prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
    
    def _collect_words(self, node: TrieNode, prefix: str, 
                      results: List[Tuple[str, int]]) -> None:
        """Recursively collect all words from a node."""
        if node.is_end:
            results.append((prefix, node.frequency))
        
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, results)
    
    def autocomplete(self, prefix: str, max_results: int = 10) -> List[str]:
        """
        Get autocomplete suggestions for a prefix.
        
        Args:
            prefix: Prefix to complete
            max_results: Maximum number of suggestions
            
        Returns:
            List of autocomplete suggestions ordered by frequency
            
        Time Complexity: O(p + m) where m is max_results
        """
        suggestions = self.starts_with(prefix)
        return suggestions[:max_results]
    
    def longest_prefix(self, word: str) -> str:
        """
        Find the longest prefix of the word that exists in the Trie.
        
        Args:
            word: Word to check
            
        Returns:
            Longest prefix that exists in the Trie
            
        Time Complexity: O(k)
        """
        word = self._normalize(word)
        node = self.root
        longest = ""
        current = ""
        
        for char in word:
            if char not in node.children:
                break
            node = node.children[char]
            current += char
            if node.is_end:
                longest = current
        
        return longest
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get Trie statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'word_count': self._word_count,
            'node_count': self._node_count,
            'memory_efficiency': self._word_count / self._node_count if self._node_count > 0 else 0
        }


class PatternTrie(Trie):
    """
    Specialized Trie for pattern matching with regex support.
    
    Extends basic Trie with pattern-specific optimizations.
    """
    
    def __init__(self, case_sensitive: bool = True):
        super().__init__(case_sensitive)
        self._pattern_cache: Dict[str, re.Pattern] = {}
    
    def insert_pattern(self, pattern: str, pattern_type: str, 
                      confidence: float = 0.9) -> None:
        """
        Insert a pattern with metadata.
        
        Args:
            pattern: Pattern string
            pattern_type: Type of pattern (e.g., 'arithmetic', 'logical')
            confidence: Default confidence score
        """
        value = {
            'type': pattern_type,
            'confidence': confidence,
            'regex': None
        }
        
        # Cache compiled regex if pattern contains regex metacharacters
        if any(c in pattern for c in r'.*+?[]{}()^$|\\'):
            try:
                value['regex'] = re.compile(pattern)
                self._pattern_cache[pattern] = value['regex']
            except re.error:
                pass  # Not a valid regex, treat as literal
        
        self.insert(pattern, value)
    
    def match_pattern(self, text: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Find all patterns that match the given text.
        
        Args:
            text: Text to match against
            
        Returns:
            List of (pattern, metadata) tuples for matching patterns
        """
        matches = []
        
        # First, try exact matches
        if self.search(text):
            node = self._find_node(text)
            if node and node.value:
                matches.append((text, node.value))
        
        # Then, try regex patterns
        for pattern, regex in self._pattern_cache.items():
            if regex.match(text):
                node = self._find_node(pattern)
                if node and node.value:
                    matches.append((pattern, node.value))
        
        # Sort by confidence
        matches.sort(key=lambda x: x[1].get('confidence', 0), reverse=True)
        return matches


class KeywordTrie(Trie):
    """
    Optimized Trie for programming language keywords.
    
    Features:
    - Token type associations
    - Fast keyword classification
    - Reserved word checking
    """
    
    def __init__(self):
        super().__init__(case_sensitive=True)
        self._token_types: Dict[str, str] = {}
    
    def add_keyword(self, keyword: str, token_type: str) -> None:
        """
        Add a keyword with its token type.
        
        Args:
            keyword: Keyword string
            token_type: Associated token type
        """
        self.insert(keyword, token_type)
        self._token_types[keyword] = token_type
    
    def classify_token(self, word: str) -> Optional[str]:
        """
        Classify a word as a keyword or identifier.
        
        Args:
            word: Word to classify
            
        Returns:
            Token type if keyword, None if identifier
        """
        return self.get(word)
    
    def is_reserved(self, word: str) -> bool:
        """Check if a word is a reserved keyword."""
        return self.search(word)
    
    def bulk_add_keywords(self, keywords: Dict[str, str]) -> None:
        """
        Add multiple keywords at once.
        
        Args:
            keywords: Dictionary mapping keywords to token types
        """
        for keyword, token_type in keywords.items():
            self.add_keyword(keyword, token_type)