#!/usr/bin/env python3
"""
Refactored Semantic Analyzer for TauTranslator
=============================================

Refactored from 675 lines to <300 lines for improved maintainability.
Uses Strategy pattern for analysis components and Factory pattern for creation.

Key improvements:
- Strategy pattern for analysis components
- Factory pattern for object creation
- Clear separation of concerns
- Enhanced error handling
- Comprehensive type system

Author: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Tuple, Dict, Any

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
from .semantic_analyzer_core import (
    ExpressionTypeResolver, ValidationEngine, SymbolDefinitionManager
)


class SemanticAnalyzer:
    """
    Refactored semantic analyzer using Strategy pattern for component separation.
    
    
    - Strategy pattern for analysis components
    - Factory pattern for component creation
    - Single Responsibility: Coordination only
    - Clear error handling and logging
    - Performance monitoring capability
    """
    
    def __init__(self, vocabulary: Optional[dict] = None):
        """
        Initialize semantic analyzer with strategy components.
        
        Args:
            vocabulary: Dictionary containing available types, predicates, functions.
                       Defaults to basic types if not provided.
        """
        self.vocabulary = vocabulary if vocabulary else {
            'types': {'integer', 'string', 'boolean', 'auto'}
        }
        
        # Initialize core components using Strategy pattern
        self.symbol_table = SymbolTable()
        self.error_collector = ErrorCollector()
        self.type_resolver = ExpressionTypeResolver(self.symbol_table)
        self.validation_engine = ValidationEngine(
            self.symbol_table, self.type_resolver, self.error_collector, self.vocabulary
        )
        self.symbol_manager = SymbolDefinitionManager(self.symbol_table, self.error_collector)
        
        # Performance tracking
        self._analysis_count = 0
        
        self._load_vocabulary_symbols()
    
    def _load_vocabulary_symbols(self):
        """Load vocabulary symbols (predicates, functions) into symbol table"""
        # Load predicates from vocabulary
        for pred_name, pred_info in self.vocabulary.get('predicates', {}).items():
            symbol = Symbol(pred_name, 'predicate', 0)  # Global scope
            symbol.attributes['arity'] = pred_info.get('arity', 0)
            symbol.attributes['signature'] = pred_info.get('signature', [])
            self.symbol_table.declare_symbol(symbol)
        
        # Load functions from vocabulary
        for func_name, func_info in self.vocabulary.get('functions', {}).items():
            symbol = Symbol(func_name, 'function', 0)  # Global scope
            symbol.attributes['arity'] = func_info.get('arity', 0)
            symbol.attributes['signature'] = func_info.get('signature', [])
            symbol.attributes['return_type'] = func_info.get('return', 'auto')
            self.symbol_table.declare_symbol(symbol)
    

    def analyze(self, node: Optional[ASTNode]) -> Tuple[Optional[ASTNode], List[SemanticError]]:
        """
        Perform semantic analysis using Strategy pattern components.
        
        Args:
            node: Root AST node to analyze
            
        Returns:
            Tuple of (analyzed_node, list_of_errors)
        """
        self._analysis_count += 1
        self.error_collector.clear_errors()  # Reset errors for new analysis
        
        if node is not None:
            self._visit(node)
        
        return node, self.error_collector.get_errors()
    
    def get_analysis_stats(self) -> dict:
        """
        Get semantic analysis performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'analysis_count': self._analysis_count,
            'symbol_table_stats': self.symbol_table.get_performance_stats(),
            'type_resolution_stats': self.type_resolver.get_resolution_stats(),
            'error_summary': self.error_collector.get_error_summary()
        }

    def _visit(self, node: Optional[ASTNode]) -> None:
        """
        Generic visit method that dispatches to specific node visitors.
        
        Uses reflection to find the appropriate visitor method based on node type.
        Falls back to generic visitor if no specific visitor is found.
        
        Args:
            node: AST node to visit
        """
        if node is None:
            return
        method_name = f'_visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node: ASTNode) -> None:
        """
        Default visitor for nodes not handled specifically.
        
        This method is called for node types that don't have specific visitors.
        In a complete implementation, all node types should have specific visitors.
        
        Args:
            node: AST node being visited
        """
        # Could traverse children generically here if needed
        pass

    # --- Example Visitor Methods (to be expanded by TDD) ---

    def _visit_SentenceNode(self, node):
        for stmt in node.content: # Changed from node.statements
            self._visit(stmt)

    def _visit_VariableDeclNode(self, node):
        """Visit variable declaration node using validation strategies."""
        self.validation_engine.validate_variable_type(node)
        
        if not self.validation_engine.check_variable_redeclaration(node):
            resolved_type = self._resolve_variable_type(node)
            self.symbol_manager.define_variable_symbol(node, resolved_type)
        
        if node.value:
            self._process_variable_initializer(node)
    
    def _resolve_variable_type(self, node) -> str:
        """Resolve variable type, handling 'auto' type inference"""
        if node.var_type == 'auto' and not node.value:
            error = SemanticError(
                "Variable with 'auto' type requires an initializer.",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)
        return node.var_type
    
    def _process_variable_initializer(self, node) -> None:
        """Process variable initializer using type resolution strategies."""
        self._visit(node.value)
        value_type = self.type_resolver.get_expression_type(node.value)
        
        if node.var_type == 'auto' and value_type:
            self._update_inferred_type(node, value_type)
        elif node.var_type != 'auto' and value_type:
            self.validation_engine.validate_type_compatibility(node.var_type, value_type, node)
    
    def _update_inferred_type(self, node, inferred_type: str) -> None:
        """Update symbol with inferred type for 'auto' variables"""
        symbol = self.symbol_table.lookup_symbol(node.name)
        if symbol:
            symbol.var_type = inferred_type

    def _visit_VariableNode(self, node):
        symbol = self.symbol_table.lookup_symbol(node.name)
        if symbol is None:
            error = SemanticError(
                f"Variable '{node.name}' not declared.",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)
        elif symbol.symbol_type != 'variable':
            error = SemanticError(
                f"Identifier '{node.name}' is not a variable.",
                line_number=getattr(node, 'line', None),
                column_number=getattr(node, 'column', None)
            )
            self.error_collector.add_error(error)

    def _visit_AssignmentNode(self, node):
        self._visit(node.target) # Should be a VariableNode or similar l-value
        self._visit(node.expression)
        
        # Type checking for assignment compatibility
        if isinstance(node.target, VariableNode):
            symbol = self.symbol_table.lookup_symbol(node.target.name)
            if symbol and symbol.var_type and symbol.var_type != 'auto':
                # Get expression type
                expr_type = self.type_resolver.get_expression_type(node.expression)
                if expr_type and expr_type != symbol.var_type:
                    # Check type compatibility
                    type_info1 = create_type_info(symbol.var_type)
                    type_info2 = create_type_info(expr_type)
                    if not type_info1.is_compatible_with(type_info2):
                        error = SemanticError(
                            f"Type mismatch: cannot assign {expr_type} to {symbol.var_type} variable '{node.target.name}'",
                            line_number=getattr(node, 'line', None),
                            column_number=getattr(node, 'column', None)
                        )
                        self.error_collector.add_error(error)

    def _visit_ConstantNode(self, node):
        # Constants are usually fine by themselves, type might be inferred or explicit
        # If explicit type on ConstantNode, could validate against vocabulary
        pass

    def _visit_NumberNode(self, node):
        # Number literals are valid by themselves
        pass

    def _visit_StringNode(self, node):
        # String literals are valid by themselves
        pass

    def _visit_ArithmeticBinaryOpNode(self, node):
        """Visit arithmetic binary operation node using validation strategies."""
        self._visit(node.left)
        self._visit(node.right)
        self.validation_engine.validate_arithmetic_operands(node)

    def _visit_BooleanBinaryOpNode(self, node):
        """Visit boolean binary operation node"""
        # Visit left and right operands
        self._visit(node.left)
        self._visit(node.right)
        
        # Boolean operations should work on boolean operands or expressions that evaluate to boolean

    def _visit_ComparisonNode(self, node):
        """Visit comparison operation node"""
        # Visit left and right operands
        self._visit(node.left)
        self._visit(node.right)
        
        # Comparison operations should work on compatible types

    def _visit_PredicateCallNode(self, node):
        """Visit predicate call node using validation strategies."""
        # Visit all arguments
        if node.args:
            for arg in node.args:
                self._visit(arg)
        
        self.validation_engine.validate_predicate_call(node)

    def _visit_PredicateDefinitionNode(self, node):
        """Visit predicate definition node using symbol management strategies."""
        if self.symbol_manager.define_predicate_symbol(node):
            self._analyze_definition_body(node)
    
    def _analyze_definition_body(self, node) -> None:
        """Analyze predicate/function body with parameter scope"""
        self.symbol_table.enter_scope()
        
        try:
            self.symbol_manager.define_parameters(node)
            if node.body:
                self._visit(node.body)
        finally:
            self.symbol_table.exit_scope()

    def _visit_FunctionDefinitionNode(self, node):
        """Visit function definition node using symbol management strategies."""
        if self.symbol_manager.define_function_symbol(node):
            self._analyze_definition_body(node)

    def _visit_QuantifierBlockNode(self, node):
        """Visit quantifier block node using symbol management strategies."""
        # Enter new scope for quantified variables
        self.symbol_table.enter_scope()
        
        # Define quantified variables in the new scope
        if node.variables:
            for var in node.variables:
                if isinstance(var, VariableNode):
                    symbol = Symbol(
                        name=var.name,
                        symbol_type='variable',
                        scope_level=self.symbol_table.current_scope,
                        var_type='auto'
                    )
                    try:
                        self.symbol_table.declare_symbol(symbol)
                    except SemanticError as e:
                        self.error_collector.add_error(e)
        
        # Analyze condition if present
        if node.condition:
            self._visit(node.condition)
        
        # Exit scope after analyzing quantifier block
        self.symbol_table.exit_scope()

    def _visit_ConditionNode(self, node):
        """Visit condition node"""
        # Visit quantifier block first (if present) to set up scope
        if node.quant_block:
            self._visit(node.quant_block)
        
        # Visit the expression
        if node.expression:
            self._visit(node.expression)
        
        # Exit quantifier scope if we entered one
        if node.quant_block:
            self.symbol_table.exit_scope()

    # Add more _visit_* methods as AST nodes are defined and tests require them
