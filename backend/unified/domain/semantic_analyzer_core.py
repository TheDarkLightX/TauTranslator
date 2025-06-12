"""
Core semantic analysis components following the Intentional Disclosure Principle.

Provides type resolution, validation, and symbol management services.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Optional, Dict, Any, List
from .semantic_types import (
    Symbol, SymbolTable, ErrorCollector, SemanticError, TypeInfo, create_type_info
)


class ExpressionTypeResolver:
    """Resolves types of expressions during semantic analysis."""
    
    def __init__(self, symbol_table: SymbolTable):
        """Initialize with symbol table reference."""
        self.symbol_table = symbol_table
    
    def get_expression_type(self, expression: Any) -> Optional[str]:
        """Get the type of an expression node."""
        if hasattr(expression, 'value'):
            return self._get_literal_type(expression)
        
        if hasattr(expression, 'name'):
            return self._get_variable_type(expression)
        
        if hasattr(expression, 'operator'):
            return self._get_operation_type(expression)
        
        return None
    
    def _get_literal_type(self, literal: Any) -> str:
        """Get type of a literal value."""
        if hasattr(literal, 'value'):
            value = literal.value
            if isinstance(value, bool):
                return "boolean"
            elif isinstance(value, int):
                return "integer"
            elif isinstance(value, float):
                return "float"
            elif isinstance(value, str):
                return "string"
        return "auto"
    
    def _get_variable_type(self, var_node: Any) -> Optional[str]:
        """Get type of a variable reference."""
        symbol = self.symbol_table.lookup_symbol(var_node.name)
        return symbol.var_type if symbol else None
    
    def _get_operation_type(self, op_node: Any) -> str:
        """Get result type of an operation."""
        # Simplified type inference for operations
        if hasattr(op_node, 'operator'):
            op = op_node.operator
            if op in ['<', '>', '<=', '>=', '==', '!=', 'and', 'or', 'not']:
                return "boolean"
            elif op in ['+', '-', '*', '/', '%']:
                return "number"
        return "auto"


class ValidationEngine:
    """Handles validation logic for semantic analysis."""
    
    def __init__(self, symbol_table: SymbolTable, type_resolver: ExpressionTypeResolver,
                 error_collector: ErrorCollector, vocabulary: Dict[str, Any]):
        """Initialize validation engine."""
        self.symbol_table = symbol_table
        self.type_resolver = type_resolver
        self.error_collector = error_collector
        self.vocabulary = vocabulary
    
    def validate_variable_type(self, node: Any) -> None:
        """Validate variable type is known."""
        if hasattr(node, 'var_type'):
            valid_types = self.vocabulary.get('types', set())
            if node.var_type not in valid_types and node.var_type != 'auto':
                self.error_collector.add_error(
                    SemanticError(
                        f"Unknown type '{node.var_type}'",
                        line_number=getattr(node, 'line', None)
                    )
                )
    
    def check_variable_redeclaration(self, node: Any) -> bool:
        """Check if variable is already declared in current scope."""
        current_scope_symbols = self.symbol_table.scopes[self.symbol_table.current_scope]
        if node.name in current_scope_symbols:
            self.error_collector.add_error(
                SemanticError(
                    f"Variable '{node.name}' already declared in current scope",
                    line_number=getattr(node, 'line', None)
                )
            )
            return True
        return False
    
    def validate_type_compatibility(self, target_type: str, source_type: str, node: Any) -> None:
        """Validate type compatibility for assignment."""
        target_info = create_type_info(target_type)
        source_info = create_type_info(source_type)
        
        if not target_info.is_compatible_with(source_info):
            self.error_collector.add_error(
                SemanticError(
                    f"Type mismatch: cannot assign {source_type} to {target_type}",
                    line_number=getattr(node, 'line', None)
                )
            )
    
    def validate_arithmetic_operation(self, node: Any) -> None:
        """Validate arithmetic operation types."""
        left_type = self.type_resolver.get_expression_type(node.left)
        right_type = self.type_resolver.get_expression_type(node.right)
        
        numeric_types = {"integer", "float", "number"}
        
        if left_type and left_type not in numeric_types:
            self.error_collector.add_error(
                SemanticError(
                    f"Left operand of arithmetic operation must be numeric, got {left_type}",
                    line_number=getattr(node, 'line', None)
                )
            )
        
        if right_type and right_type not in numeric_types:
            self.error_collector.add_error(
                SemanticError(
                    f"Right operand of arithmetic operation must be numeric, got {right_type}",
                    line_number=getattr(node, 'line', None)
                )
            )
    
    def validate_boolean_operation(self, node: Any) -> None:
        """Validate boolean operation types."""
        left_type = self.type_resolver.get_expression_type(node.left)
        right_type = self.type_resolver.get_expression_type(node.right)
        
        if left_type and left_type != "boolean":
            self.error_collector.add_error(
                SemanticError(
                    f"Left operand of boolean operation must be boolean, got {left_type}",
                    line_number=getattr(node, 'line', None)
                )
            )
        
        if right_type and right_type != "boolean":
            self.error_collector.add_error(
                SemanticError(
                    f"Right operand of boolean operation must be boolean, got {right_type}",
                    line_number=getattr(node, 'line', None)
                )
            )
    
    def validate_comparison_operation(self, node: Any) -> None:
        """Validate comparison operation types."""
        left_type = self.type_resolver.get_expression_type(node.left)
        right_type = self.type_resolver.get_expression_type(node.right)
        
        if left_type and right_type and left_type != right_type:
            # Allow comparison between different numeric types
            numeric_types = {"integer", "float", "number"}
            if not (left_type in numeric_types and right_type in numeric_types):
                self.error_collector.add_error(
                    SemanticError(
                        f"Cannot compare {left_type} with {right_type}",
                        line_number=getattr(node, 'line', None)
                    )
                )


class SymbolDefinitionManager:
    """Manages symbol definitions during semantic analysis."""
    
    def __init__(self, symbol_table: SymbolTable, error_collector: ErrorCollector):
        """Initialize symbol manager."""
        self.symbol_table = symbol_table
        self.error_collector = error_collector
    
    def define_variable_symbol(self, node: Any, resolved_type: str) -> None:
        """Define a variable symbol in the symbol table."""
        symbol = Symbol(
            name=node.name,
            symbol_type="variable",
            scope_level=self.symbol_table.current_scope,
            var_type=resolved_type
        )
        
        if hasattr(node, 'is_constant') and node.is_constant:
            symbol.attributes['is_constant'] = True
        
        self.symbol_table.declare_symbol(symbol)
    
    def define_function_symbol(self, node: Any) -> None:
        """Define a function symbol in the symbol table."""
        symbol = Symbol(
            name=node.name,
            symbol_type="function",
            scope_level=self.symbol_table.current_scope
        )
        
        # Store function metadata
        if hasattr(node, 'parameters'):
            symbol.attributes['parameters'] = node.parameters
        if hasattr(node, 'return_type'):
            symbol.attributes['return_type'] = node.return_type
        
        if not self.symbol_table.declare_symbol(symbol):
            self.error_collector.add_error(
                SemanticError(
                    f"Function '{node.name}' already declared",
                    line_number=getattr(node, 'line', None)
                )
            )
    
    def define_predicate_symbol(self, node: Any) -> None:
        """Define a predicate symbol in the symbol table."""
        symbol = Symbol(
            name=node.name,
            symbol_type="predicate",
            scope_level=self.symbol_table.current_scope
        )
        
        # Store predicate metadata
        if hasattr(node, 'arity'):
            symbol.attributes['arity'] = node.arity
        if hasattr(node, 'parameters'):
            symbol.attributes['parameters'] = node.parameters
        
        if not self.symbol_table.declare_symbol(symbol):
            self.error_collector.add_error(
                SemanticError(
                    f"Predicate '{node.name}' already declared",
                    line_number=getattr(node, 'line', None)
                )
            )