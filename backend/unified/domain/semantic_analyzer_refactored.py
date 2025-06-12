"""
Refactored Semantic Analyzer following the Intentional Disclosure Principle.

All methods follow IDP Rule 2 (≤10 lines) with clear separation of concerns.
Uses Strategy pattern for analysis components and clean error handling.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Tuple, Dict, Any
from ..core.result_enhanced import Result, Success, Failure

from ..domain.semantic_types import (
    SemanticError, Symbol, SymbolTable, TypeInfo, ErrorCollector,
    create_type_info, check_type_compatibility
)
from ..infrastructure.semantic_infrastructure import (
    VocabularyLoader, MethodResolver, NodeChildrenExtractor
)


class SemanticAnalyzerRefactored:
    """Semantic analyzer with all methods ≤10 lines following IDP."""
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        """Initialize semantic analyzer with clean component creation."""
        self.vocabulary = self._initialize_vocabulary(vocabulary)
        self._create_core_components()
        self._analysis_count = 0
        self._load_vocabulary_symbols()
    
    def analyze(self, node: Optional[Any]) -> Tuple[Optional[Any], List[SemanticError]]:
        """Perform semantic analysis on AST node."""
        self._analysis_count += 1
        self.error_collector.clear_errors()
        
        if node is not None:
            self._visit(node)
        
        return node, self.error_collector.get_errors()
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        return {
            'analysis_count': self._analysis_count,
            'symbols_declared': self.symbol_table.get_symbol_count(),
            'scopes_created': self.symbol_table.get_scope_count(),
            'errors_found': len(self.error_collector.get_errors())
        }
    
    # Initialization helpers (all ≤10 lines)
    
    def _initialize_vocabulary(self, vocabulary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Initialize vocabulary with defaults."""
        if vocabulary:
            return vocabulary
        return {'types': {'integer', 'string', 'boolean', 'auto'}}
    
    def _create_core_components(self) -> None:
        """Create strategy components for analysis."""
        self.symbol_table = SymbolTable()
        self.error_collector = ErrorCollector()
        from .semantic_analyzer_core import (
            ExpressionTypeResolver, ValidationEngine, SymbolDefinitionManager
        )
        self.type_resolver = ExpressionTypeResolver(self.symbol_table)
        self.validation_engine = ValidationEngine(
            self.symbol_table, self.type_resolver, self.error_collector, self.vocabulary
        )
        self.symbol_manager = SymbolDefinitionManager(self.symbol_table, self.error_collector)
    
    def _load_vocabulary_symbols(self) -> None:
        """Load symbols from vocabulary."""
        self._load_predicates_from_vocabulary()
        self._load_functions_from_vocabulary()
    
    def _load_predicates_from_vocabulary(self) -> None:
        """Load predicate symbols from vocabulary."""
        for pred_name, pred_info in self.vocabulary.get('predicates', {}).items():
            symbol = self._create_predicate_symbol(pred_name, pred_info)
            self.symbol_table.declare_symbol(symbol)
    
    def _load_functions_from_vocabulary(self) -> None:
        """Load function symbols from vocabulary."""
        for func_name, func_info in self.vocabulary.get('functions', {}).items():
            symbol = self._create_function_symbol(func_name, func_info)
            self.symbol_table.declare_symbol(symbol)
    
    def _create_predicate_symbol(self, name: str, info: Dict[str, Any]) -> Symbol:
        """Create predicate symbol from vocabulary info."""
        symbol = Symbol(name, 'predicate', 0)
        symbol.attributes['arity'] = info.get('arity', 0)
        symbol.attributes['signature'] = info.get('signature', [])
        return symbol
    
    def _create_function_symbol(self, name: str, info: Dict[str, Any]) -> Symbol:
        """Create function symbol from vocabulary info."""
        symbol = Symbol(name, 'function', 0)
        symbol.attributes['arity'] = info.get('arity', 0)
        symbol.attributes['signature'] = info.get('signature', [])
        symbol.attributes['return_type'] = info.get('return', 'auto')
        return symbol
    
    # Visitor pattern implementation (all ≤10 lines)
    
    def _visit(self, node: Any) -> Any:
        """Visit a node using visitor pattern."""
        if node is None:
            return None
        
        method_name = MethodResolver.get_visitor_method_name(node)
        method = getattr(self, method_name, None)
        
        if method:
            return method(node)
        else:
            return self._generic_visit(node)
    
    def _generic_visit(self, node: Any) -> None:
        """Default visitor for nodes without specific handlers."""
        # Base implementation - subclasses can override
        pass
    
    # Specific node visitors (all ≤10 lines)
    
    def _visit_SentenceNode(self, node) -> None:
        """Visit sentence node."""
        for stmt in node.content:
            self._visit(stmt)
    
    def _visit_VariableDeclNode(self, node) -> None:
        """Visit variable declaration node."""
        self.validation_engine.validate_variable_type(node)
        
        if not self.validation_engine.check_variable_redeclaration(node):
            resolved_type = self._resolve_variable_type(node)
            self.symbol_manager.define_variable_symbol(node, resolved_type)
        
        if node.value:
            self._process_variable_initializer(node)
    
    def _visit_VariableNode(self, node) -> None:
        """Visit variable reference node."""
        symbol = self.symbol_table.lookup_symbol(node.name)
        
        if not symbol:
            self._add_undeclared_variable_error(node)
        elif not self._is_variable_symbol(symbol):
            self._add_not_variable_error(node)
    
    def _visit_AssignmentNode(self, node) -> None:
        """Visit assignment node."""
        self._visit(node.target)
        self._visit(node.expression)
        
        if hasattr(node.target, 'name'):  # Check if it's a variable-like node
            self._validate_assignment_types(node)
    
    def _visit_QuantifierBlockNode(self, node) -> None:
        """Visit quantifier block node."""
        self.symbol_table.enter_scope()
        
        self._define_quantified_variables(node)
        
        if node.condition:
            self._visit(node.condition)
        
        self.symbol_table.exit_scope()
    
    def _visit_ConditionNode(self, node) -> None:
        """Visit condition node."""
        if node.quantifier_block:
            self._visit(node.quantifier_block)
        
        if node.expression:
            self._visit(node.expression)
            
        if node.quantifier_block:
            self.symbol_table.exit_scope()
    
    # Helper methods (all ≤10 lines)
    
    def _resolve_variable_type(self, node) -> str:
        """Resolve variable type, handling 'auto' inference."""
        if node.var_type == 'auto' and not node.value:
            self._add_auto_without_initializer_error(node)
        return node.var_type
    
    def _process_variable_initializer(self, node) -> None:
        """Process variable initializer with type checking."""
        self._visit(node.value)
        value_type = self.type_resolver.get_expression_type(node.value)
        
        if node.var_type == 'auto' and value_type:
            self._update_inferred_type(node, value_type)
        elif node.var_type != 'auto' and value_type:
            self.validation_engine.validate_type_compatibility(node.var_type, value_type, node)
    
    def _update_inferred_type(self, node, inferred_type: str) -> None:
        """Update symbol with inferred type for 'auto' variables."""
        symbol = self.symbol_table.lookup_symbol(node.name)
        if symbol:
            symbol.var_type = inferred_type
    
    def _is_variable_symbol(self, symbol: Symbol) -> bool:
        """Check if symbol represents a variable."""
        return symbol.symbol_type == 'variable'
    
    def _add_undeclared_variable_error(self, node) -> None:
        """Add error for undeclared variable."""
        error = SemanticError(
            f"Variable '{node.name}' not declared.",
            line_number=getattr(node, 'line', None),
            column_number=getattr(node, 'column', None)
        )
        self.error_collector.add_error(error)
    
    def _add_not_variable_error(self, node) -> None:
        """Add error for non-variable identifier."""
        error = SemanticError(
            f"Identifier '{node.name}' is not a variable.",
            line_number=getattr(node, 'line', None),
            column_number=getattr(node, 'column', None)
        )
        self.error_collector.add_error(error)
    
    def _add_auto_without_initializer_error(self, node) -> None:
        """Add error for 'auto' variable without initializer."""
        error = SemanticError(
            "Variable with 'auto' type requires an initializer.",
            line_number=getattr(node, 'line', None),
            column_number=getattr(node, 'column', None)
        )
        self.error_collector.add_error(error)
    
    def _validate_assignment_types(self, node) -> None:
        """Validate type compatibility in assignment."""
        
        symbol = self.symbol_table.lookup_symbol(node.target.name)
        if not symbol or not symbol.var_type or symbol.var_type == 'auto':
            return
            
        expr_type = self.type_resolver.get_expression_type(node.expression)
        if expr_type and not self._are_types_compatible(symbol.var_type, expr_type):
            self._add_type_mismatch_error(node, symbol, expr_type)
    
    def _are_types_compatible(self, target_type: str, source_type: str) -> bool:
        """Check if types are compatible for assignment."""
        type_info1 = create_type_info(target_type)
        type_info2 = create_type_info(source_type)
        return type_info1.is_compatible_with(type_info2)
    
    def _add_type_mismatch_error(self, node, symbol: Symbol, expr_type: str) -> None:
        """Add type mismatch error for assignment."""
        error = SemanticError(
            f"Type mismatch: cannot assign {expr_type} to {symbol.var_type} "
            f"variable '{node.target.name}'",
            line_number=getattr(node, 'line', None),
            column_number=getattr(node, 'column', None)
        )
        self.error_collector.add_error(error)
    
    def _define_quantified_variables(self, node) -> None:
        """Define variables in quantifier block."""
        for var in node.variables:
            if isinstance(var, dict):
                self._define_single_quantified_variable(var)
            else:
                self._define_simple_quantified_variable(var)
    
    def _define_single_quantified_variable(self, var_dict: Dict[str, Any]) -> None:
        """Define a single quantified variable from dictionary."""
        var_name = var_dict.get('name', '')
        var_type = var_dict.get('type', 'auto')
        symbol = self._create_quantified_symbol(var_name, var_type)
        
        if not self.symbol_table.declare_symbol(symbol):
            self._add_redeclaration_error(var_name)
    
    def _define_simple_quantified_variable(self, var_name: str) -> None:
        """Define a simple quantified variable."""
        symbol = self._create_quantified_symbol(var_name, 'auto')
        
        if not self.symbol_table.declare_symbol(symbol):
            self._add_redeclaration_error(var_name)
    
    def _create_quantified_symbol(self, name: str, var_type: str) -> Symbol:
        """Create symbol for quantified variable."""
        symbol = Symbol(name, 'variable', self.symbol_table.current_scope)
        symbol.var_type = var_type
        symbol.attributes['quantified'] = True
        return symbol
    
    def _add_redeclaration_error(self, var_name: str) -> None:
        """Add error for variable redeclaration."""
        error = SemanticError(
            f"Variable '{var_name}' already declared in current scope."
        )
        self.error_collector.add_error(error)
    
    # Additional visitor methods for other node types
    
    def _visit_ConstantNode(self, node) -> None:
        """Visit constant node."""
        pass  # Constants are valid by themselves
    
    def _visit_NumberNode(self, node) -> None:
        """Visit number node."""
        pass  # Number literals are valid by themselves
    
    def _visit_StringNode(self, node) -> None:
        """Visit string node."""
        pass  # String literals are valid by themselves
    
    def _visit_ArithmeticBinaryOpNode(self, node) -> None:
        """Visit arithmetic binary operation node."""
        self._visit(node.left)
        self._visit(node.right)
        self.validation_engine.validate_arithmetic_operation(node)
    
    def _visit_BooleanBinaryOpNode(self, node) -> None:
        """Visit boolean binary operation node."""
        self._visit(node.left)
        self._visit(node.right)
        self.validation_engine.validate_boolean_operation(node)
    
    def _visit_ComparisonNode(self, node) -> None:
        """Visit comparison node."""
        self._visit(node.left)
        self._visit(node.right)
        self.validation_engine.validate_comparison_operation(node)
    
    def _visit_PredicateCallNode(self, node) -> None:
        """Visit predicate call node."""
        self._validate_predicate_call(node)
        for arg in node.arguments:
            self._visit(arg)
    
    def _visit_FunctionDefinitionNode(self, node) -> None:
        """Visit function definition node."""
        self.symbol_table.enter_scope()
        self._define_function_parameters(node)
        self._visit(node.body)
        self.symbol_table.exit_scope()
    
    def _validate_predicate_call(self, node) -> None:
        """Validate predicate call against symbol table."""
        symbol = self.symbol_table.lookup_symbol(node.name)
        
        if not symbol:
            self._add_undefined_predicate_error(node)
        elif symbol.symbol_type != 'predicate':
            self._add_not_predicate_error(node)
        else:
            self._validate_predicate_arity(node, symbol)
    
    def _add_undefined_predicate_error(self, node) -> None:
        """Add error for undefined predicate."""
        error = SemanticError(
            f"Predicate '{node.name}' not defined.",
            line_number=getattr(node, 'line', None),
            column_number=getattr(node, 'column', None)
        )
        self.error_collector.add_error(error)
    
    def _add_not_predicate_error(self, node) -> None:
        """Add error for non-predicate identifier."""
        error = SemanticError(
            f"'{node.name}' is not a predicate.",
            line_number=getattr(node, 'line', None),
            column_number=getattr(node, 'column', None)
        )
        self.error_collector.add_error(error)
    
    def _validate_predicate_arity(self, node, symbol: Symbol) -> None:
        """Validate predicate argument count."""
        expected_arity = symbol.attributes.get('arity', 0)
        actual_arity = len(node.arguments)
        
        if expected_arity != actual_arity:
            self._add_arity_mismatch_error(node, expected_arity, actual_arity)
    
    def _add_arity_mismatch_error(self, node, expected: int, actual: int) -> None:
        """Add error for predicate arity mismatch."""
        error = SemanticError(
            f"Predicate '{node.name}' expects {expected} arguments, got {actual}.",
            line_number=getattr(node, 'line', None),
            column_number=getattr(node, 'column', None)
        )
        self.error_collector.add_error(error)
    
    def _define_function_parameters(self, node) -> None:
        """Define function parameters in scope."""
        for param in node.parameters:
            param_symbol = Symbol(param.name, 'variable', self.symbol_table.current_scope)
            param_symbol.var_type = param.param_type
            self.symbol_table.declare_symbol(param_symbol)