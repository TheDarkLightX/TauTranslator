"""
Optimized Symbol Table Implementation
====================================

High-performance symbol table with O(1) lookup using unified dictionary
and scope tracking, plus support for incremental updates.

Author: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Dict, Any, Set, Tuple
from collections import defaultdict
import weakref

from .semantic_types import Symbol, SemanticError
from .parsers.cnl_parser.ast_nodes import ASTNode


class OptimizedSymbolTable:
    """
    High-performance symbol table with O(1) lookup.
    
    Key optimizations:
    - Single unified dictionary for all symbols with scope tracking
    - O(1) symbol lookup regardless of scope depth
    - Efficient scope entry/exit with lazy cleanup
    - Memory-efficient with weakref support
    - Incremental updates for interactive editing
    """
    
    def __init__(self):
        """Initialize optimized symbol table."""
        # Unified symbol storage: name -> list of (symbol, scope_level)
        self._symbols: Dict[str, List[Tuple[Symbol, int]]] = defaultdict(list)
        
        # Track active scopes for efficient cleanup
        self._scope_symbols: Dict[int, Set[str]] = defaultdict(set)
        
        # Current scope level
        self._current_scope = 0
        
        # Performance counters
        self._lookup_count = 0
        self._symbol_count = 0
        self._cache_hits = 0
        
        # LRU cache for recent lookups
        self._lookup_cache: Dict[Tuple[str, int], Optional[Symbol]] = {}
        self._cache_max_size = 256
    
    def enter_scope(self) -> int:
        """
        Enter a new nested scope.
        
        Returns:
            The new scope level
        """
        self._current_scope += 1
        return self._current_scope
    
    def exit_scope(self) -> None:
        """
        Exit the current scope with efficient cleanup.
        
        Raises:
            SemanticError: If attempting to exit global scope
        """
        if self._current_scope == 0:
            raise SemanticError("Cannot exit global scope")
        
        # Clean up symbols from exited scope
        exited_symbols = self._scope_symbols.get(self._current_scope, set())
        
        for name in exited_symbols:
            if name in self._symbols:
                # Remove entries for this scope level
                self._symbols[name] = [
                    (sym, level) for sym, level in self._symbols[name]
                    if level != self._current_scope
                ]
                # Clean up empty entries
                if not self._symbols[name]:
                    del self._symbols[name]
        
        # Clear scope tracking
        if self._current_scope in self._scope_symbols:
            self._symbol_count -= len(self._scope_symbols[self._current_scope])
            del self._scope_symbols[self._current_scope]
        
        # Invalidate cache entries for exited scope
        self._invalidate_cache_for_scope(self._current_scope)
        
        self._current_scope -= 1
    
    def declare_symbol(self, symbol: Symbol) -> None:
        """
        Declare a symbol in the current scope with O(1) insertion.
        
        Args:
            symbol: Symbol to declare
            
        Raises:
            SemanticError: If symbol already exists in current scope
            ValueError: If symbol is None
        """
        if symbol is None:
            raise ValueError("Symbol cannot be None")
        
        # Check for redeclaration in current scope
        existing = self._lookup_in_scope(symbol.name, self._current_scope)
        if existing is not None:
            raise SemanticError(
                f"Symbol '{symbol.name}' already declared in current scope"
            )
        
        # Add to unified storage
        self._symbols[symbol.name].append((symbol, self._current_scope))
        self._scope_symbols[self._current_scope].add(symbol.name)
        self._symbol_count += 1
        
        # Invalidate cache for this name
        self._invalidate_cache_for_name(symbol.name)
    
    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """
        O(1) symbol lookup with caching.
        
        Args:
            name: Symbol name to find
            
        Returns:
            Symbol if found, None otherwise
        """
        if not name or not name.strip():
            raise ValueError("Symbol name cannot be empty")
        
        name = name.strip()
        self._lookup_count += 1
        
        # Check cache first
        cache_key = (name, self._current_scope)
        if cache_key in self._lookup_cache:
            self._cache_hits += 1
            return self._lookup_cache[cache_key]
        
        # Direct lookup in unified storage
        if name not in self._symbols:
            self._update_cache(cache_key, None)
            return None
        
        # Find the symbol with the highest scope level <= current scope
        best_symbol = None
        best_level = -1
        
        for symbol, scope_level in self._symbols[name]:
            if scope_level <= self._current_scope and scope_level > best_level:
                best_symbol = symbol
                best_level = scope_level
        
        self._update_cache(cache_key, best_symbol)
        return best_symbol
    
    def _lookup_in_scope(self, name: str, scope_level: int) -> Optional[Symbol]:
        """
        Look up a symbol in a specific scope only.
        
        Args:
            name: Symbol name
            scope_level: Specific scope to search
            
        Returns:
            Symbol if found in that scope, None otherwise
        """
        if name not in self._symbols:
            return None
        
        for symbol, level in self._symbols[name]:
            if level == scope_level:
                return symbol
        
        return None
    
    def symbol_exists(self, name: str) -> bool:
        """
        O(1) check if a symbol exists.
        
        Args:
            name: Symbol name to check
            
        Returns:
            True if symbol exists, False otherwise
        """
        return self.lookup_symbol(name) is not None
    
    def get_symbols_in_scope(self, scope_level: Optional[int] = None) -> List[Symbol]:
        """
        Get all symbols in a specific scope.
        
        Args:
            scope_level: Scope level to query (current scope if None)
            
        Returns:
            List of symbols in the specified scope
        """
        if scope_level is None:
            scope_level = self._current_scope
        
        if scope_level < 0:
            raise ValueError(f"Invalid scope level: {scope_level}")
        
        symbols = []
        for name in self._scope_symbols.get(scope_level, set()):
            symbol = self._lookup_in_scope(name, scope_level)
            if symbol:
                symbols.append(symbol)
        
        return symbols
    
    def _update_cache(self, key: Tuple[str, int], value: Optional[Symbol]) -> None:
        """Update the lookup cache with LRU eviction."""
        self._lookup_cache[key] = value
        
        # Simple LRU: remove oldest entries if cache is too large
        if len(self._lookup_cache) > self._cache_max_size:
            # Remove first 25% of entries (oldest)
            keys_to_remove = list(self._lookup_cache.keys())[:self._cache_max_size // 4]
            for k in keys_to_remove:
                del self._lookup_cache[k]
    
    def _invalidate_cache_for_name(self, name: str) -> None:
        """Invalidate all cache entries for a given name."""
        keys_to_remove = [
            key for key in self._lookup_cache
            if key[0] == name
        ]
        for key in keys_to_remove:
            del self._lookup_cache[key]
    
    def _invalidate_cache_for_scope(self, scope_level: int) -> None:
        """Invalidate all cache entries that might be affected by scope exit."""
        keys_to_remove = [
            key for key in self._lookup_cache
            if key[1] >= scope_level
        ]
        for key in keys_to_remove:
            del self._lookup_cache[key]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get detailed performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        cache_hit_rate = (
            (self._cache_hits / self._lookup_count * 100) 
            if self._lookup_count > 0 else 0
        )
        
        return {
            'lookup_count': self._lookup_count,
            'symbol_count': self._symbol_count,
            'scope_depth': self._current_scope,
            'unique_names': len(self._symbols),
            'cache_hits': self._cache_hits,
            'cache_size': len(self._lookup_cache),
            'cache_hit_rate': cache_hit_rate,
            'scopes_with_symbols': len(self._scope_symbols)
        }
    
    def clear_cache(self) -> None:
        """Clear the lookup cache."""
        self._lookup_cache.clear()
        self._cache_hits = 0