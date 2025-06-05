"""
Semantic Types and Error Management
==================================

Extracted from semantic_analyzer.py to maintain <600 line limit.
Contains core types, errors, and symbols for semantic analysis.

Author: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from .cnl_parser.ast_nodes import ASTNode


class SemanticError(Exception):
    """
    Custom exception for semantic errors.
    
    Provides detailed error information including location context
    for precise error reporting and debugging.
    
    Follows VibeArchitect principles:
    - Clear error messages
    - Structured error information
    - Location context for debugging
    """
    
    def __init__(self, message: str, line_number: Optional[int] = None, 
                 column_number: Optional[int] = None):
        """
        Initialize semantic error.
        
        Args:
            message: Descriptive error message
            line_number: Line number in source code (optional)
            column_number: Column number in source code (optional)
        """
        super().__init__(message)
        self.message = message
        self.line_number = line_number
        self.column_number = column_number

    def __str__(self) -> str:
        """Format error with location information."""
        if self.line_number is not None and self.column_number is not None:
            return f"SemanticError (L{self.line_number}, C{self.column_number}): {self.message}"
        elif self.line_number is not None:
            return f"SemanticError (L{self.line_number}): {self.message}"
        return f"SemanticError: {self.message}"


class Symbol:
    """
    Represents an entry in the symbol table.
    
    Stores information about declared symbols including variables,
    predicates, functions, and types with associated metadata.
    
    Follows VibeArchitect principles:
    - Immutable after creation
    - Clear attribute responsibilities
    - Type safety with validation
    """
    
    def __init__(self, name: str, symbol_type: str, scope_level: int, 
                 ast_node: Optional[ASTNode] = None, var_type: Optional[str] = None):
        """
        Initialize symbol table entry.
        
        Args:
            name: Symbol identifier name
            symbol_type: Type of symbol ('variable', 'predicate', 'function', etc.)
            scope_level: Lexical scope level where symbol is defined
            ast_node: AST node that declared this symbol (optional)
            var_type: Variable type for type checking (optional)
            
        Raises:
            ValueError: If name or symbol_type is empty
        """
        if not name or not name.strip():
            raise ValueError("Symbol name cannot be empty")
        if not symbol_type or not symbol_type.strip():
            raise ValueError("Symbol type cannot be empty")
        if scope_level < 0:
            raise ValueError("Scope level cannot be negative")
        
        self.name = name.strip()
        self.symbol_type = symbol_type.strip()
        self.scope_level = scope_level
        self.attributes = {}  # For storing type info, arity, etc.
        self.ast_node = ast_node
        self.var_type = var_type
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Symbol({self.name}, {self.symbol_type}, scope={self.scope_level})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison for symbols."""
        if not isinstance(other, Symbol):
            return False
        return (self.name == other.name and 
                self.symbol_type == other.symbol_type and
                self.scope_level == other.scope_level)
    
    def __hash__(self) -> int:
        """Hash for using symbols in sets/dicts."""
        return hash((self.name, self.symbol_type, self.scope_level))


class SymbolTable:
    """
    Manages hierarchical symbol tables with lexical scoping.
    
    Implements a stack-based approach to scope management, supporting
    nested scopes for functions, predicates, and quantified expressions.
    
    Follows VibeArchitect principles:
    - Clear scope management
    - O(1) symbol lookup
    - Comprehensive error handling
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize symbol table with global scope."""
        self.scopes = [{}]  # Stack of scopes, global scope is at index 0
        self.current_scope_level = 0
        self._lookup_count = 0  # Performance monitoring
        self._symbol_count = 0

    def enter_scope(self) -> None:
        """
        Enter a new nested scope.
        
        Creates a new scope level for local variables, function parameters,
        quantified variables, etc.
        """
        self.current_scope_level += 1
        self.scopes.append({})

    def exit_scope(self) -> None:
        """
        Exit the current scope.
        
        Returns to the previous scope level. Cannot exit global scope.
        
        Raises:
            SemanticError: If attempting to exit global scope
        """
        if self.current_scope_level > 0:
            # Remove symbols from exited scope
            exited_scope = self.scopes.pop()
            self._symbol_count -= len(exited_scope)
            self.current_scope_level -= 1
        else:
            raise SemanticError("Cannot exit global scope.")

    def declare_symbol(self, symbol: Symbol) -> None:
        """
        Declare a symbol in the current scope.
        
        Args:
            symbol: Symbol to declare
            
        Raises:
            SemanticError: If symbol already exists in current scope
            ValueError: If symbol is None
        """
        if symbol is None:
            raise ValueError("Symbol cannot be None")
        
        current_scope = self.scopes[self.current_scope_level]
        
        if symbol.name in current_scope:
            existing = current_scope[symbol.name]
            raise SemanticError(
                f"Symbol '{symbol.name}' already declared in current scope "
                f"(line {existing.ast_node.line_number if existing.ast_node else 'unknown'})"
            )
        
        current_scope[symbol.name] = symbol
        self._symbol_count += 1

    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol by name in current and parent scopes.
        
        Searches from current scope upward to global scope.
        
        Args:
            name: Symbol name to find
            
        Returns:
            Symbol if found, None otherwise
            
        Raises:
            ValueError: If name is empty
        """
        if not name or not name.strip():
            raise ValueError("Symbol name cannot be empty")
        
        self._lookup_count += 1
        name = name.strip()
        
        # Search from current scope up to global scope
        for scope_level in range(self.current_scope_level, -1, -1):
            scope = self.scopes[scope_level]
            if name in scope:
                return scope[name]
        
        return None

    def symbol_exists(self, name: str) -> bool:
        """
        Check if a symbol exists in any accessible scope.
        
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
            
        Raises:
            ValueError: If scope_level is invalid
        """
        if scope_level is None:
            scope_level = self.current_scope_level
        
        if scope_level < 0 or scope_level >= len(self.scopes):
            raise ValueError(f"Invalid scope level: {scope_level}")
        
        return list(self.scopes[scope_level].values())

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get symbol table performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'lookup_count': self._lookup_count,
            'symbol_count': self._symbol_count,
            'scope_depth': self.current_scope_level,
            'total_scopes': len(self.scopes)
        }

    def __str__(self) -> str:
        """String representation for debugging."""
        result = f"SymbolTable (scope level {self.current_scope_level}):\n"
        for level, scope in enumerate(self.scopes):
            result += f"  Scope {level}: {list(scope.keys())}\n"
        return result


class TypeInfo:
    """
    Represents type information for semantic analysis.
    
    Follows VibeArchitect principles:
    - Immutable type information
    - Clear type relationships
    - Validation on creation
    """
    
    VALID_TYPES = {'integer', 'string', 'boolean', 'real', 'auto'}
    TYPE_HIERARCHY = {
        'integer': 'number',
        'real': 'number',
        'auto': 'any'  # Auto can accept any type during assignment
    }
    
    def __init__(self, type_name: str, is_inferred: bool = False):
        """
        Initialize type information.
        
        Args:
            type_name: Name of the type
            is_inferred: Whether type was inferred vs explicitly declared
            
        Raises:
            ValueError: If type_name is invalid
        """
        if type_name not in self.VALID_TYPES:
            raise ValueError(f"Invalid type: {type_name}. Valid types: {self.VALID_TYPES}")
        
        self.type_name = type_name
        self.is_inferred = is_inferred
    
    def is_compatible_with(self, other_type: 'TypeInfo') -> bool:
        """
        Check if this type is compatible with another type.
        
        Args:
            other_type: Type to check compatibility with
            
        Returns:
            True if types are compatible, False otherwise
        """
        # Auto type accepts any other type during assignment
        if self.type_name == 'auto' or other_type.type_name == 'auto':
            return True
        
        # Same types are compatible
        if self.type_name == other_type.type_name:
            return True
        
        # Check type hierarchy compatibility
        self_base = self.TYPE_HIERARCHY.get(self.type_name, self.type_name)
        other_base = self.TYPE_HIERARCHY.get(other_type.type_name, other_type.type_name)
        
        return self_base == other_base
    
    def __str__(self) -> str:
        """String representation."""
        inferred_marker = " (inferred)" if self.is_inferred else ""
        return f"{self.type_name}{inferred_marker}"
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, TypeInfo):
            return False
        return self.type_name == other.type_name
    
    def __hash__(self) -> int:
        """Hash for using in sets/dicts."""
        return hash(self.type_name)


class ErrorCollector:
    """
    Collects and manages semantic errors during analysis.
    
    Follows VibeArchitect principles:
    - Comprehensive error collection
    - Clear error categorization
    - Performance tracking
    """
    
    def __init__(self):
        """Initialize error collector."""
        self.errors = []
        self.warnings = []
        self._error_count_by_type = {}
    
    def add_error(self, error: SemanticError) -> None:
        """
        Add a semantic error.
        
        Args:
            error: SemanticError to add
        """
        if not isinstance(error, SemanticError):
            raise ValueError("Expected SemanticError instance")
        
        self.errors.append(error)
        
        # Track error types for analytics
        error_type = type(error).__name__
        self._error_count_by_type[error_type] = self._error_count_by_type.get(error_type, 0) + 1
    
    def add_warning(self, message: str, line_number: Optional[int] = None) -> None:
        """
        Add a warning message.
        
        Args:
            message: Warning message
            line_number: Line number (optional)
        """
        warning = {
            'message': message,
            'line_number': line_number
        }
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if any warnings were collected."""
        return len(self.warnings) > 0
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of collected errors.
        
        Returns:
            Dictionary with error statistics
        """
        return {
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'errors_by_type': self._error_count_by_type.copy(),
            'has_errors': self.has_errors()
        }
    
    def clear(self) -> None:
        """Clear all collected errors and warnings."""
        self.errors.clear()
        self.warnings.clear()
        self._error_count_by_type.clear()


# Type checking utilities
def create_type_info(type_name: str, is_inferred: bool = False) -> TypeInfo:
    """Factory function for creating TypeInfo instances."""
    return TypeInfo(type_name, is_inferred)


def check_type_compatibility(type1: TypeInfo, type2: TypeInfo) -> bool:
    """Check if two types are compatible."""
    return type1.is_compatible_with(type2)