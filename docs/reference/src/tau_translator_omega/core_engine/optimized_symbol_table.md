Module src.tau_translator_omega.core_engine.optimized_symbol_table
==================================================================
Optimized Symbol Table Implementation
====================================

High-performance symbol table with O(1) lookup using unified dictionary
and scope tracking, plus support for incremental updates.

Author: DarkLightX / Dana Edwards

Classes
-------

`OptimizedSymbolTable()`
:   High-performance symbol table with O(1) lookup.
    
    Key optimizations:
    - Single unified dictionary for all symbols with scope tracking
    - O(1) symbol lookup regardless of scope depth
    - Efficient scope entry/exit with lazy cleanup
    - Memory-efficient with weakref support
    - Incremental updates for interactive editing
    
    Initialize optimized symbol table.

    ### Methods

    `clear_cache(self) ‑> None`
    :   Clear the lookup cache.

    `declare_symbol(self, symbol: src.tau_translator_omega.core_engine.semantic_types.Symbol) ‑> None`
    :   Declare a symbol in the current scope with O(1) insertion.
        
        Args:
            symbol: Symbol to declare
            
        Raises:
            SemanticError: If symbol already exists in current scope
            ValueError: If symbol is None

    `enter_scope(self) ‑> int`
    :   Enter a new nested scope.
        
        Returns:
            The new scope level

    `exit_scope(self) ‑> None`
    :   Exit the current scope with efficient cleanup.
        
        Raises:
            SemanticError: If attempting to exit global scope

    `get_performance_stats(self) ‑> Dict[str, Any]`
    :   Get detailed performance statistics.
        
        Returns:
            Dictionary with performance metrics

    `get_symbols_in_scope(self, scope_level: int | None = None) ‑> List[src.tau_translator_omega.core_engine.semantic_types.Symbol]`
    :   Get all symbols in a specific scope.
        
        Args:
            scope_level: Scope level to query (current scope if None)
            
        Returns:
            List of symbols in the specified scope

    `lookup_symbol(self, name: str) ‑> src.tau_translator_omega.core_engine.semantic_types.Symbol | None`
    :   O(1) symbol lookup with caching.
        
        Args:
            name: Symbol name to find
            
        Returns:
            Symbol if found, None otherwise

    `symbol_exists(self, name: str) ‑> bool`
    :   O(1) check if a symbol exists.
        
        Args:
            name: Symbol name to check
            
        Returns:
            True if symbol exists, False otherwise