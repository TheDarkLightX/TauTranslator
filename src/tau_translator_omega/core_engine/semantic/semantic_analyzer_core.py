"""
Semantic Analyzer Core Logic
============================

Extracted from semantic_analyzer.py to maintain <600 line limit.
Contains the visitor pattern implementation and AST traversal logic.

Author: DarkLightX / Dana Edwards
"""

from typing import Optional, List, Tuple
from abc import ABC, abstractmethod
from functools import lru_cache
import weakref

from ..parsers.cnl_parser.ast_nodes import (
    ASTNode, VariableNode, ConstantNode, NumberNode, StringNode,
    ArithmeticBinaryOpNode, BooleanBinaryOpNode, ComparisonNode,
    PredicateCallNode, VariableDeclNode, AssignmentNode,
    PredicateDefinitionNode, FunctionDefinitionNode,
    QuantifierBlockNode, ConditionNode
)
from .semantic_types import (
    SemanticError, Symbol, SymbolTable, TypeInfo, ErrorCollector,
    create_type_info, check_type_compatibility
)
from ..ast.ast_visitor import TypeResolvingVisitor


class ExpressionTypeResolver:
    """
    Resolves types for expressions during semantic analysis.
    
    
    - Single Responsibility: Only type resolution
    - Clear type inference rules
    - Performance monitoring
    
    Uses weakref-based caching to prevent memory leaks from AST nodes.
    """
    
    def __init__(self, symbol_table: SymbolTable, use_visitor_pattern: bool = False):
        self.symbol_table = symbol_table
        self._expression_types = weakref.WeakKeyDictionary()  # Weak reference cache
        self._resolution_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        # LRU cache for pure type resolution functions
        self._resolve_arithmetic_type = lru_cache(maxsize=256)(self._resolve_arithmetic_type_impl)
        self._resolve_variable_type = lru_cache(maxsize=512)(self._resolve_variable_type_impl)
        
        # Optional visitor pattern support
        self.use_visitor_pattern = use_visitor_pattern
        if use_visitor_pattern:
            self._type_visitor = TypeResolvingVisitor(symbol_table)
    
    def get_expression_type(self, node: ASTNode) -> Optional[str]:
        """
        Get the type of an expression node with memoization.
        
        Args:
            node: AST node to resolve type for
            
        Returns:
            Type string if resolvable, None otherwise
        """
        if node is None:
            return None
        
        self._resolution_count += 1
        
        # Check cache first
        if node in self._expression_types:
            self._cache_hits += 1
            return self._expression_types[node]
        
        self._cache_misses += 1
        result = self._resolve_type(node)
        
        # Cache the result using weak reference
        if result is not None:
            self._expression_types[node] = result
        
        return result
    
    def get_cache_stats(self) -> dict:
        """Get cache performance statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        
        return {
            'total_resolutions': self._resolution_count,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate': hit_rate,
            'cache_size': len(self._expression_types),
            'arithmetic_cache_info': self._resolve_arithmetic_type.cache_info()._asdict(),
            'variable_cache_info': self._resolve_variable_type.cache_info()._asdict()
        }
    
    def _resolve_type(self, node: ASTNode) -> Optional[str]:
        """Resolve type for specific node types."""
        # Use visitor pattern if enabled
        if self.use_visitor_pattern:
            return self._type_visitor.visit(node)
        
        # Fallback to isinstance checks for backward compatibility
        if isinstance(node, ConstantNode):
            return self._resolve_constant_type(node)
        elif isinstance(node, NumberNode):
            return 'integer'
        elif isinstance(node, StringNode):
            return 'string'
        elif isinstance(node, VariableNode):
            return self._resolve_variable_type(node.name)
        elif isinstance(node, ArithmeticBinaryOpNode):
            left_type = self.get_expression_type(node.left)
            right_type = self.get_expression_type(node.right)
            return self._resolve_arithmetic_type(left_type, right_type, node.operator)
        elif isinstance(node, ComparisonNode):
            return 'boolean'
        elif isinstance(node, BooleanBinaryOpNode):
            return 'boolean'
        elif isinstance(node, PredicateCallNode):
            return self._resolve_predicate_type(node)
        
        return None
    
    def _resolve_constant_type(self, node: ConstantNode) -> Optional[str]:
        """Resolve type for constant node."""
        if hasattr(node, 'value_type'):
            type_map = {
                "NUMBER": 'integer',
                "STRING": 'string',
                "BOOLEAN": 'boolean'
            }
            return type_map.get(node.value_type)
        
        # Fallback inference
        if isinstance(node.value, (int, float)):
            return 'integer' if isinstance(node.value, int) else 'real'
        elif isinstance(node.value, str):
            return 'string'
        elif isinstance(node.value, bool):
            return 'boolean'
        
        return None
    
    def _resolve_variable_type_impl(self, node_name: str) -> Optional[str]:
        """Implementation of variable type resolution (cached)."""
        symbol = self.symbol_table.lookup_symbol(node_name)
        if symbol and symbol.symbol_type == 'variable':
            return symbol.var_type
        return None
    
    def _resolve_arithmetic_type_impl(self, left_type: Optional[str], right_type: Optional[str], operator: str) -> Optional[str]:
        """Implementation of arithmetic type resolution (cached)."""
        if left_type in ('integer', 'real') and right_type in ('integer', 'real'):
            return 'real' if 'real' in (left_type, right_type) else 'integer'
        
        return None
    
    def _resolve_predicate_type(self, node: PredicateCallNode) -> Optional[str]:
        """Resolve type for predicate call (might be function)."""
        symbol = self.symbol_table.lookup_symbol(node.name)
        if symbol and symbol.symbol_type == 'function':
            return symbol.attributes.get('return_type', 'auto')
        return None
    
    def get_resolution_stats(self) -> dict:
        """Get type resolution performance statistics."""
        return {
            'resolution_count': self._resolution_count,
            'cached_types': len(self._expression_types)
        }


class ValidationEngine:
    """
    Handles validation logic for semantic analysis.
    
    
    - Single Responsibility: Only validation
    - Clear validation rules
    - Comprehensive error reporting
    """
    
    def __init__(self, symbol_table: SymbolTable, type_resolver: ExpressionTypeResolver, 
                 error_collector: ErrorCollector, vocabulary: dict):
        self.symbol_table = symbol_table
        self.type_resolver = type_resolver
        self.error_collector = error_collector
        self.vocabulary = vocabulary
    
    def validate_variable_type(self, node: VariableDeclNode) -> None:
        """Validate that variable type exists in vocabulary."""
        if node.var_type != 'auto' and node.var_type not in self.vocabulary.get('types', set()):
            error = SemanticError(
                f"Type '{node.var_type}' is not defined in the vocabulary.",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)
    
    def check_variable_redeclaration(self, node: VariableDeclNode) -> bool:
        """
        Check for variable redeclaration in current scope.
        
        Returns:
            True if redeclaration detected, False otherwise
        """
        existing_symbols = self.symbol_table.scopes[self.symbol_table.current_scope]
        if node.name in existing_symbols:
                error = SemanticError(
                    f"Variable '{node.name}' already declared in this scope.",
                    line_number=getattr(node, 'line', None),
                    column_number=getattr(node, 'column', None)
                )
                self.error_collector.add_error(error)
                return True
        return False
    
    def validate_type_compatibility(self, target_type: str, value_type: str, node: ASTNode) -> bool:
        """
        Validate type compatibility between target and value types.
        
        Args:
            target_type: Expected type
            value_type: Actual type
            node: AST node for error reporting
            
        Returns:
            True if compatible, False otherwise
        """
        target_info = create_type_info(target_type)
        value_info = create_type_info(value_type)
        
        if not check_type_compatibility(target_info, value_info):
            error = SemanticError(
                f"Type mismatch: cannot assign '{value_type}' to variable of type '{target_type}'",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)
            return False
        
        return True
    
    def validate_arithmetic_operands(self, node: ArithmeticBinaryOpNode) -> None:
        """Validate arithmetic operation operands."""
        left_type = self.type_resolver.get_expression_type(node.left)
        right_type = self.type_resolver.get_expression_type(node.right)
        
        arithmetic_types = {'integer', 'real', 'number'}
        
        if left_type and left_type not in arithmetic_types:
            error = SemanticError(
                f"Left operand of '{node.operator}' must be numeric type, got '{left_type}'",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)
        
        if right_type and right_type not in arithmetic_types:
            error = SemanticError(
                f"Right operand of '{node.operator}' must be numeric type, got '{right_type}'",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)
    
    def validate_predicate_call(self, node: PredicateCallNode) -> None:
        """Validate predicate call."""
        symbol = self.symbol_table.lookup_symbol(node.name)
        
        if symbol is None:
            error = SemanticError(
                f"Predicate '{node.name}' not declared.",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)
            return
        
        if symbol.symbol_type != 'predicate':
            error = SemanticError(
                f"'{node.name}' is not a predicate.",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)
            return
        
        # Check arity
        expected_arity = symbol.attributes.get('arity')
        actual_arity = len(node.args) if node.args else 0
        
        if expected_arity is not None and expected_arity != actual_arity:
            error = SemanticError(
                f"Predicate '{node.name}' expects {expected_arity} arguments, got {actual_arity}.",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)


class SymbolDefinitionManager:
    """
    Manages symbol definition during semantic analysis.
    
    
    - Single Responsibility: Only symbol management
    - Clear symbol creation rules
    - Comprehensive error handling
    """
    
    def __init__(self, symbol_table: SymbolTable, error_collector: ErrorCollector):
        self.symbol_table = symbol_table
        self.error_collector = error_collector
    
    def define_variable_symbol(self, node: VariableDeclNode, resolved_type: str) -> bool:
        """
        Define variable symbol in symbol table.
        
        Args:
            node: Variable declaration node
            resolved_type: Resolved variable type
            
        Returns:
            True if symbol defined successfully, False otherwise
        """
        symbol = Symbol(
            name=node.name,
            symbol_type='variable',
            scope_level=self.symbol_table.current_scope,
            var_type=resolved_type
        )
        
        try:
            self.symbol_table.declare_symbol(symbol)
            return True
        except SemanticError as e:
            self.error_collector.add_error(e)
            return False
    
    def define_predicate_symbol(self, node: PredicateDefinitionNode) -> bool:
        """Define predicate symbol in symbol table."""
        arity = len(node.parameters) if node.parameters else 0
        symbol = Symbol(
            name=node.name,
            symbol_type='predicate',
            scope_level=self.symbol_table.current_scope
        )
        symbol.attributes['arity'] = arity
        
        try:
            self.symbol_table.declare_symbol(symbol)
            return True
        except SemanticError as e:
            self.error_collector.add_error(e)
            return False
    
    def define_function_symbol(self, node: FunctionDefinitionNode) -> bool:
        """Define function symbol in symbol table."""
        arity = len(node.parameters) if node.parameters else 0
        symbol = Symbol(
            name=node.name,
            symbol_type='function',
            scope_level=self.symbol_table.current_scope
        )
        symbol.attributes['arity'] = arity
        
        try:
            self.symbol_table.declare_symbol(symbol)
            return True
        except SemanticError as e:
            self.error_collector.add_error(e)
            return False
    
    def define_parameters(self, node) -> None:
        """Define parameters in current scope."""
        if not node.parameters:
            return
        
        for param in node.parameters:
            if isinstance(param, VariableNode):
                symbol = Symbol(
                    name=param.name,
                    symbol_type='variable',
                    scope_level=self.symbol_table.current_scope,
                    var_type='auto'
                )
                
                try:
                    self.symbol_table.declare_symbol(symbol)
                except SemanticError as e:
                    self.error_collector.add_error(e)