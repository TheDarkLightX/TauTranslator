"""
Semantic analysis types following the Intentional Disclosure Principle.

Domain types for semantic analysis with immutable data structures.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class SymbolType(str, Enum):
    """Types of symbols in the symbol table."""
    VARIABLE = "variable"
    FUNCTION = "function"
    PREDICATE = "predicate"
    TYPE = "type"
    CONSTANT = "constant"


@dataclass(frozen=True)
class TypeInfo:
    """Immutable type information."""
    base_type: str
    is_array: bool = False
    element_type: Optional[str] = None
    
    def is_compatible_with(self, other: 'TypeInfo') -> bool:
        """Check if this type is compatible with another."""
        if self.base_type == "auto" or other.base_type == "auto":
            return True
        return self.base_type == other.base_type


@dataclass(frozen=True)
class SemanticError:
    """Immutable semantic error information."""
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    error_type: str = "semantic"
    
    def __str__(self) -> str:
        """String representation of the error."""
        location = ""
        if self.line_number:
            location = f" at line {self.line_number}"
            if self.column_number:
                location += f", column {self.column_number}"
        return f"{self.error_type.capitalize()} error{location}: {self.message}"


@dataclass
class Symbol:
    """Mutable symbol table entry."""
    name: str
    symbol_type: str  # Using string instead of enum for compatibility
    scope_level: int
    var_type: Optional[str] = None
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


class SymbolTable:
    """Symbol table with scope management."""
    
    def __init__(self):
        """Initialize empty symbol table."""
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Start with global scope
        self.current_scope = 0
        self._scope_count = 1
        self._symbol_count = 0
    
    def enter_scope(self) -> None:
        """Enter a new scope."""
        self.scopes.append({})
        self.current_scope += 1
        self._scope_count += 1
    
    def exit_scope(self) -> None:
        """Exit current scope."""
        if self.current_scope > 0:
            self.scopes.pop()
            self.current_scope -= 1
    
    def declare_symbol(self, symbol: Symbol) -> bool:
        """Declare a symbol in current scope."""
        if symbol.name in self.scopes[self.current_scope]:
            return False
        self.scopes[self.current_scope][symbol.name] = symbol
        self._symbol_count += 1
        return True
    
    def lookup_symbol(self, name: str) -> Optional[Symbol]:
        """Look up symbol in all visible scopes."""
        for i in range(self.current_scope, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None
    
    def get_symbol_count(self) -> int:
        """Get total number of symbols declared."""
        return self._symbol_count
    
    def get_scope_count(self) -> int:
        """Get total number of scopes created."""
        return self._scope_count


class ErrorCollector:
    """Collects semantic errors during analysis."""
    
    def __init__(self):
        """Initialize empty error collector."""
        self._errors: List[SemanticError] = []
    
    def add_error(self, error: SemanticError) -> None:
        """Add an error to the collection."""
        self._errors.append(error)
    
    def get_errors(self) -> List[SemanticError]:
        """Get all collected errors."""
        return self._errors.copy()
    
    def clear_errors(self) -> None:
        """Clear all errors."""
        self._errors.clear()
    
    def has_errors(self) -> bool:
        """Check if any errors have been collected."""
        return len(self._errors) > 0


# Helper functions for type management

def create_type_info(type_str: str) -> TypeInfo:
    """Create TypeInfo from type string."""
    if type_str.endswith("[]"):
        base_type = type_str[:-2]
        return TypeInfo(base_type="array", is_array=True, element_type=base_type)
    return TypeInfo(base_type=type_str)


def check_type_compatibility(type1: str, type2: str) -> bool:
    """Check if two type strings are compatible."""
    info1 = create_type_info(type1)
    info2 = create_type_info(type2)
    return info1.is_compatible_with(info2)


# Domain validation rules

@dataclass(frozen=True)
class ValidationRule:
    """Immutable validation rule."""
    rule_id: str
    description: str
    severity: str  # "error", "warning", "info"
    

@dataclass(frozen=True)
class AnalysisContext:
    """Immutable context for semantic analysis."""
    file_path: Optional[str] = None
    strict_mode: bool = False
    type_inference_enabled: bool = True
    max_errors: int = 100