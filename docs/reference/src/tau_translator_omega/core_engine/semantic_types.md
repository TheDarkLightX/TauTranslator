Module src.tau_translator_omega.core_engine.semantic_types
==========================================================
Semantic Types and Error Management
==================================

Extracted from semantic_analyzer.py to maintain <600 line limit.
Contains core types, errors, and symbols for semantic analysis.

Author: DarkLightX / Dana Edwards

Functions
---------

`check_type_compatibility(type1: src.tau_translator_omega.core_engine.semantic_types.TypeInfo, type2: src.tau_translator_omega.core_engine.semantic_types.TypeInfo) ‑> bool`
:   Check if two types are compatible.

`create_type_info(type_name: str, is_inferred: bool = False) ‑> src.tau_translator_omega.core_engine.semantic_types.TypeInfo`
:   Factory function for creating TypeInfo instances.

Classes
-------

`ErrorCollector()`
:   Collects and manages semantic errors during analysis.
    
    Follows VibeArchitect principles:
    - Comprehensive error collection
    - Clear error categorization
    - Performance tracking
    
    Initialize error collector.

    ### Methods

    `add_error(self, error: src.tau_translator_omega.core_engine.semantic_types.SemanticError) ‑> None`
    :   Add a semantic error.
        
        Args:
            error: SemanticError to add

    `add_warning(self, message: str, line_number: int | None = None) ‑> None`
    :   Add a warning message.
        
        Args:
            message: Warning message
            line_number: Line number (optional)

    `clear(self) ‑> None`
    :   Clear all collected errors and warnings.

    `get_error_summary(self) ‑> Dict[str, Any]`
    :   Get summary of collected errors.
        
        Returns:
            Dictionary with error statistics

    `has_errors(self) ‑> bool`
    :   Check if any errors were collected.

    `has_warnings(self) ‑> bool`
    :   Check if any warnings were collected.

`SemanticError(message: str, line_number: int | None = None, column_number: int | None = None)`
:   Custom exception for semantic errors.
    
    Provides detailed error information including location context
    for precise error reporting and debugging.
    
    Follows VibeArchitect principles:
    - Clear error messages
    - Structured error information
    - Location context for debugging
    
    Initialize semantic error.
    
    Args:
        message: Descriptive error message
        line_number: Line number in source code (optional)
        column_number: Column number in source code (optional)

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`Symbol(name: str, symbol_type: str, scope_level: int, ast_node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | None = None, var_type: str | None = None)`
:   Represents an entry in the symbol table.
    
    Stores information about declared symbols including variables,
    predicates, functions, and types with associated metadata.
    
    Follows VibeArchitect principles:
    - Immutable after creation
    - Clear attribute responsibilities
    - Type safety with validation
    
    Initialize symbol table entry.
    
    Args:
        name: Symbol identifier name
        symbol_type: Type of symbol ('variable', 'predicate', 'function', etc.)
        scope_level: Lexical scope level where symbol is defined
        ast_node: AST node that declared this symbol (optional)
        var_type: Variable type for type checking (optional)
        
    Raises:
        ValueError: If name or symbol_type is empty

`SymbolTable()`
:   Manages hierarchical symbol tables with lexical scoping.
    
    Implements a stack-based approach to scope management, supporting
    nested scopes for functions, predicates, and quantified expressions.
    
    Follows VibeArchitect principles:
    - Clear scope management
    - O(1) symbol lookup
    - Comprehensive error handling
    - Performance monitoring
    
    Initialize symbol table with global scope.

    ### Methods

    `declare_symbol(self, symbol: src.tau_translator_omega.core_engine.semantic_types.Symbol) ‑> None`
    :   Declare a symbol in the current scope.
        
        Args:
            symbol: Symbol to declare
            
        Raises:
            SemanticError: If symbol already exists in current scope
            ValueError: If symbol is None

    `enter_scope(self) ‑> None`
    :   Enter a new nested scope.
        
        Creates a new scope level for local variables, function parameters,
        quantified variables, etc.

    `exit_scope(self) ‑> None`
    :   Exit the current scope.
        
        Returns to the previous scope level. Cannot exit global scope.
        
        Raises:
            SemanticError: If attempting to exit global scope

    `get_performance_stats(self) ‑> Dict[str, Any]`
    :   Get symbol table performance statistics.
        
        Returns:
            Dictionary with performance metrics

    `get_symbols_in_scope(self, scope_level: int | None = None) ‑> List[src.tau_translator_omega.core_engine.semantic_types.Symbol]`
    :   Get all symbols in a specific scope.
        
        Args:
            scope_level: Scope level to query (current scope if None)
            
        Returns:
            List of symbols in the specified scope
            
        Raises:
            ValueError: If scope_level is invalid

    `lookup_symbol(self, name: str) ‑> src.tau_translator_omega.core_engine.semantic_types.Symbol | None`
    :   Look up a symbol by name in current and parent scopes.
        
        Searches from current scope upward to global scope.
        
        Args:
            name: Symbol name to find
            
        Returns:
            Symbol if found, None otherwise
            
        Raises:
            ValueError: If name is empty

    `symbol_exists(self, name: str) ‑> bool`
    :   Check if a symbol exists in any accessible scope.
        
        Args:
            name: Symbol name to check
            
        Returns:
            True if symbol exists, False otherwise

`TypeInfo(type_name: str, is_inferred: bool = False)`
:   Represents type information for semantic analysis.
    
    Follows VibeArchitect principles:
    - Immutable type information
    - Clear type relationships
    - Validation on creation
    
    Initialize type information.
    
    Args:
        type_name: Name of the type
        is_inferred: Whether type was inferred vs explicitly declared
        
    Raises:
        ValueError: If type_name is invalid

    ### Class variables

    `TYPE_HIERARCHY`
    :

    `VALID_TYPES`
    :

    ### Methods

    `is_compatible_with(self, other_type: TypeInfo) ‑> bool`
    :   Check if this type is compatible with another type.
        
        Args:
            other_type: Type to check compatibility with
            
        Returns:
            True if types are compatible, False otherwise