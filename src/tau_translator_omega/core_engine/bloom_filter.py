"""
Bloom Filter Implementation for Efficient Negative Lookups
========================================================

Implements a space-efficient probabilistic data structure for
fast negative membership tests in symbol tables.

Author: DarkLightX / Dana Edwards
"""

import math
from typing import List, Tuple, Optional
import numpy as np

# Try to import mmh3, fallback to hashlib if not available
try:
    import mmh3  # MurmurHash3 for fast hashing
except ImportError:
    mmh3 = None  # Will use fallback implementation


class BloomFilter:
    """
    Space-efficient Bloom filter for membership testing.
    
    Features:
    - Configurable false positive rate
    - Multiple hash functions for better distribution
    - Bit array backed by numpy for efficiency
    - No false negatives guarantee
    """
    
    def __init__(self, expected_items: int = 10000, 
                 false_positive_rate: float = 0.01):
        """
        Initialize Bloom filter.
        
        Args:
            expected_items: Expected number of items to be added
            false_positive_rate: Desired false positive probability
        """
        self.expected_items = expected_items
        self.false_positive_rate = false_positive_rate
        
        # Calculate optimal parameters
        self.bit_size, self.num_hashes = self._optimal_parameters(
            expected_items, false_positive_rate
        )
        
        # Initialize bit array
        self.bit_array = np.zeros(self.bit_size, dtype=bool)
        
        # Track statistics
        self.item_count = 0
        self.query_count = 0
        self.positive_queries = 0
    
    @staticmethod
    def _optimal_parameters(n: int, p: float) -> Tuple[int, int]:
        """
        Calculate optimal bit array size and number of hash functions.
        
        Args:
            n: Expected number of items
            p: Desired false positive rate
            
        Returns:
            Tuple of (bit_size, num_hashes)
        """
        # Optimal bit array size: m = -n * ln(p) / (ln(2)^2)
        m = int(-n * math.log(p) / (math.log(2) ** 2))
        
        # Optimal number of hash functions: k = m/n * ln(2)
        k = max(1, int(m / n * math.log(2)))
        
        return m, k
    
    def _hash_functions(self, item: str) -> List[int]:
        """
        Generate k hash values for an item.
        
        Uses double hashing with MurmurHash3 for speed.
        
        Args:
            item: Item to hash
            
        Returns:
            List of k hash values
        """
        # Use two independent hash functions
        hash1 = mmh3.hash(item, 0)
        hash2 = mmh3.hash(item, hash1)
        
        # Generate k hashes using double hashing
        hashes = []
        for i in range(self.num_hashes):
            # hash_i = hash1 + i * hash2
            combined_hash = (hash1 + i * hash2) % self.bit_size
            hashes.append(abs(combined_hash))
        
        return hashes
    
    def add(self, item: str) -> None:
        """
        Add an item to the Bloom filter.
        
        Args:
            item: Item to add
        """
        for hash_value in self._hash_functions(item):
            self.bit_array[hash_value] = True
        
        self.item_count += 1
    
    def contains(self, item: str) -> bool:
        """
        Check if an item might be in the set.
        
        Args:
            item: Item to check
            
        Returns:
            False if definitely not in set, True if possibly in set
        """
        self.query_count += 1
        
        for hash_value in self._hash_functions(item):
            if not self.bit_array[hash_value]:
                return False
        
        self.positive_queries += 1
        return True
    
    def __contains__(self, item: str) -> bool:
        """Support 'in' operator."""
        return self.contains(item)
    
    def add_all(self, items: List[str]) -> None:
        """
        Add multiple items efficiently.
        
        Args:
            items: List of items to add
        """
        for item in items:
            self.add(item)
    
    def estimated_fpp(self) -> float:
        """
        Estimate current false positive probability.
        
        Returns:
            Estimated false positive rate
        """
        if self.item_count == 0:
            return 0.0
        
        # FPP = (1 - e^(-k*n/m))^k
        exponent = -self.num_hashes * self.item_count / self.bit_size
        return (1 - math.exp(exponent)) ** self.num_hashes
    
    def fill_ratio(self) -> float:
        """
        Get the ratio of set bits.
        
        Returns:
            Proportion of bits that are set
        """
        return np.sum(self.bit_array) / self.bit_size
    
    def get_stats(self) -> dict:
        """
        Get Bloom filter statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'bit_size': self.bit_size,
            'num_hashes': self.num_hashes,
            'item_count': self.item_count,
            'fill_ratio': self.fill_ratio(),
            'estimated_fpp': self.estimated_fpp(),
            'query_count': self.query_count,
            'positive_queries': self.positive_queries,
            'negative_queries': self.query_count - self.positive_queries,
            'memory_bytes': self.bit_array.nbytes
        }
    
    def clear(self) -> None:
        """Clear the Bloom filter."""
        self.bit_array.fill(False)
        self.item_count = 0
        self.query_count = 0
        self.positive_queries = 0
    
    def merge(self, other: 'BloomFilter') -> None:
        """
        Merge another Bloom filter into this one.
        
        Args:
            other: Another Bloom filter with same parameters
            
        Raises:
            ValueError: If filters have incompatible parameters
        """
        if self.bit_size != other.bit_size or self.num_hashes != other.num_hashes:
            raise ValueError("Cannot merge Bloom filters with different parameters")
        
        # OR the bit arrays
        self.bit_array |= other.bit_array
        self.item_count += other.item_count


class ScalableBloomFilter:
    """
    Scalable Bloom filter that grows as needed.
    
    Maintains target false positive rate as more items are added
    by chaining multiple Bloom filters with geometrically decreasing
    false positive rates.
    """
    
    def __init__(self, initial_capacity: int = 1000,
                 false_positive_rate: float = 0.01,
                 growth_factor: int = 2):
        """
        Initialize scalable Bloom filter.
        
        Args:
            initial_capacity: Initial expected items
            false_positive_rate: Target false positive rate
            growth_factor: Capacity growth factor
        """
        self.false_positive_rate = false_positive_rate
        self.growth_factor = growth_factor
        
        # Create initial filter
        self.filters: List[BloomFilter] = [
            BloomFilter(initial_capacity, false_positive_rate * 0.5)
        ]
        
        self.capacity = initial_capacity
        self.item_count = 0
    
    def add(self, item: str) -> None:
        """Add an item to the filter."""
        # Check if we need a new filter
        if self.item_count >= self.capacity:
            self._add_filter()
        
        # Add to current filter
        self.filters[-1].add(item)
        self.item_count += 1
    
    def _add_filter(self) -> None:
        """Add a new filter when current one is full."""
        # Double capacity
        self.capacity *= self.growth_factor
        
        # Halve the false positive rate for new filter
        new_fpp = self.false_positive_rate * (0.5 ** len(self.filters))
        
        self.filters.append(
            BloomFilter(self.capacity, new_fpp)
        )
    
    def contains(self, item: str) -> bool:
        """Check if item might be in the filter."""
        # Check all filters (any positive is positive)
        for bloom_filter in self.filters:
            if item in bloom_filter:
                return True
        return False
    
    def __contains__(self, item: str) -> bool:
        """Support 'in' operator."""
        return self.contains(item)
    
    def get_stats(self) -> dict:
        """Get statistics for all filters."""
        stats = {
            'num_filters': len(self.filters),
            'total_items': self.item_count,
            'total_capacity': self.capacity,
            'filters': [f.get_stats() for f in self.filters]
        }
        
        # Calculate combined FPP
        combined_fpp = 1.0
        for f in self.filters:
            combined_fpp *= (1 - f.estimated_fpp())
        stats['combined_fpp'] = 1 - combined_fpp
        
        return stats


# Fallback implementation if mmh3 is not available
if mmh3 is None:
    import hashlib
    
    class mmh3:
        """Fallback hash implementation using hashlib."""
        
        @staticmethod
        def hash(data: str, seed: int = 0) -> int:
            """Simple hash function fallback."""
            h = hashlib.md5(f"{seed}{data}".encode()).hexdigest()
            return int(h[:8], 16)


class SymbolBloomFilter(BloomFilter):
    """
    Specialized Bloom filter for symbol table lookups.
    
    Optimized for programming language identifiers.
    """
    
    def __init__(self, expected_symbols: int = 5000):
        """
        Initialize symbol Bloom filter.
        
        Args:
            expected_symbols: Expected number of unique symbols
        """
        # Use lower FPP for symbol lookups (more memory, better accuracy)
        super().__init__(expected_symbols, false_positive_rate=0.001)
        
        # Track symbol categories
        self.categories = {
            'variables': BloomFilter(expected_symbols // 2, 0.001),
            'functions': BloomFilter(expected_symbols // 4, 0.001),
            'types': BloomFilter(expected_symbols // 4, 0.001),
        }
    
    def add_symbol(self, name: str, category: str) -> None:
        """
        Add a symbol with its category.
        
        Args:
            name: Symbol name
            category: Symbol category (variables, functions, types)
        """
        self.add(name)
        
        if category in self.categories:
            self.categories[category].add(name)
    
    def contains_in_category(self, name: str, category: str) -> bool:
        """
        Check if symbol might exist in a specific category.
        
        Args:
            name: Symbol name
            category: Category to check
            
        Returns:
            False if definitely not in category, True if possibly
        """
        if category in self.categories:
            return name in self.categories[category]
        return False
    
    def get_category_stats(self) -> dict:
        """Get statistics for each category."""
        return {
            cat: bloom.get_stats() 
            for cat, bloom in self.categories.items()
        }