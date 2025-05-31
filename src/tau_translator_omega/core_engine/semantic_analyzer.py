#!/usr/bin/env python3
"""
Semantic Analyzer for TauTranslator
===================================

Comprehensive semantic analysis for Tau Controlled English (TCE) and related languages.
Developed using Test-Driven Development (TDD) methodology.

Features:
- Symbol table management with lexical scoping
- Type checking and inference 
- Predicate and function analysis
- Quantifier variable scoping
- Error detection and reporting
- Integration with AST nodes

Architecture:
- Visitor pattern for AST traversal
- Hierarchical symbol tables for scoping
- Comprehensive error collection and reporting
- Type system integration
"""

from typing import List, Optional, Tuple, Dict, Any

from .cnl_parser.ast_nodes import (
    ASTNode, VariableNode, ConstantNode, NumberNode, StringNode,
    ArithmeticBinaryOpNode, BooleanBinaryOpNode, ComparisonNode,
    PredicateCallNode, VariableDeclNode, AssignmentNode,
    PredicateDefinitionNode, FunctionDefinitionNode,
    QuantifierBlockNode, ConditionNode
)

class SemanticError(Exception):
    """
    Custom exception for semantic errors.
    
    Provides detailed error information including location context
    for precise error reporting and debugging.
    
    Attributes:
        message: Descriptive error message
        line_number: Line number where error occurred (optional)
        column_number: Column number where error occurred (optional)
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
    
    Attributes:
        name: Symbol identifier name
        symbol_type: Type of symbol ('variable', 'predicate', 'function', etc.)
        scope_level: Lexical scope level where symbol is defined
        attributes: Additional metadata (arity, type info, etc.)
        ast_node: AST node that declared this symbol (for location info)
        var_type: Variable type for type checking (variables only)
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
        """
        self.name = name
        self.symbol_type = symbol_type
        self.scope_level = scope_level
        self.attributes = {}  # For storing type info, arity, etc.
        self.ast_node = ast_node
        self.var_type = var_type
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Symbol({self.name}, {self.symbol_type}, scope={self.scope_level})"

class SymbolTable:
    """
    Manages hierarchical symbol tables with lexical scoping.
    
    Implements a stack-based approach to scope management, supporting
    nested scopes for functions, predicates, and quantified expressions.
    
    Attributes:
        scopes: Stack of scope dictionaries (global scope at index 0)
        current_scope_level: Current nesting level (0 = global)
    """
    
    def __init__(self):
        """Initialize symbol table with global scope."""
        self.scopes = [{}]  # Stack of scopes, global scope is at index 0
        self.current_scope_level = 0

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
            self.scopes.pop()
            self.current_scope_level -= 1
        else:
            raise SemanticError("Cannot exit global scope.")

    def define(self, symbol: Symbol) -> bool:
        """
        Define a symbol in the current scope.
        
        Args:
            symbol: Symbol to define
            
        Returns:
            True if symbol was defined successfully, False if already exists
        """
        name = symbol.name
        if name in self.scopes[self.current_scope_level]:
            return False  # Indicates re-declaration in current scope
        self.scopes[self.current_scope_level][name] = symbol
        return True

    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol, searching from current to outer scopes.
        
        Implements lexical scoping by searching from innermost to outermost scope.
        
        Args:
            name: Symbol name to look up
            
        Returns:
            Symbol if found, None otherwise
        """
        for i in range(self.current_scope_level, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None

    def lookup_current_scope(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol only in the current scope.
        
        Used for checking redefinition errors within the same scope.
        
        Args:
            name: Symbol name to look up
            
        Returns:
            Symbol if found in current scope, None otherwise
        """
        return self.scopes[self.current_scope_level].get(name)
    
    def get_scope_info(self) -> str:
        """Get debugging information about current scope state."""
        return f"Scope level {self.current_scope_level}, {len(self.scopes)} total scopes"

class SemanticAnalyzer:
    """
    Comprehensive semantic analyzer for Tau Controlled English (TCE).
    
    Performs semantic analysis on AST nodes including:
    - Variable declaration and usage validation
    - Type checking and inference
    - Predicate and function definition analysis
    - Quantifier variable scoping
    - Error detection and collection
    
    The analyzer uses the visitor pattern to traverse AST nodes and maintains
    a hierarchical symbol table for lexical scoping.
    
    Attributes:
        vocabulary: Available types, predicates, and functions
        symbol_table: Hierarchical symbol table for scoping
        errors: Accumulated semantic errors
    """
    
    def __init__(self, vocabulary: Optional[dict] = None):
        """
        Initialize semantic analyzer.
        
        Args:
            vocabulary: Dictionary containing available types, predicates, functions.
                       Defaults to basic types if not provided.
        """
        self.vocabulary = vocabulary if vocabulary else {
            'types': {'integer', 'string', 'boolean', 'auto'}
        }
        self.symbol_table = SymbolTable()
        self.errors = []
        self._init_type_system()
        self._load_vocabulary_symbols()
    
    def _init_type_system(self):
        """Initialize the type system with built-in types"""
        # Type tracking for expressions during analysis
        self._expression_types = {}  # Maps node id() to their inferred types
    
    def _load_vocabulary_symbols(self):
        """Load vocabulary symbols (predicates, functions) into symbol table"""
        # Load predicates from vocabulary
        for pred_name, pred_info in self.vocabulary.get('predicates', {}).items():
            symbol = Symbol(pred_name, 'predicate', 0)  # Global scope
            symbol.attributes['arity'] = pred_info.get('arity', 0)
            symbol.attributes['signature'] = pred_info.get('signature', [])
            self.symbol_table.define(symbol)
        
        # Load functions from vocabulary
        for func_name, func_info in self.vocabulary.get('functions', {}).items():
            symbol = Symbol(func_name, 'function', 0)  # Global scope
            symbol.attributes['arity'] = func_info.get('arity', 0)
            symbol.attributes['signature'] = func_info.get('signature', [])
            symbol.attributes['return_type'] = func_info.get('return', 'auto')
            self.symbol_table.define(symbol)
    
    def _get_expression_type(self, node: ASTNode) -> Optional[str]:
        """Get the type of an expression node"""
        # Check if we've already computed the type
        node_id = id(node)
        if node_id in self._expression_types:
            return self._expression_types[node_id]
        
        result = None
        
        # Infer type based on node type
        if isinstance(node, ConstantNode):
            if hasattr(node, 'value_type'):
                if node.value_type == "NUMBER":
                    result = 'integer'  # Could be enhanced to detect real vs integer
                elif node.value_type == "STRING":
                    result = 'string'
                elif node.value_type == "BOOLEAN":
                    result = 'boolean'
            # Fallback inference
            elif isinstance(node.value, (int, float)):
                result = 'integer' if isinstance(node.value, int) else 'real'
            elif isinstance(node.value, str):
                result = 'string'
            elif isinstance(node.value, bool):
                result = 'boolean'
        
        elif isinstance(node, NumberNode):
            result = 'integer'  # Could check for real numbers
        
        elif isinstance(node, StringNode):
            result = 'string'
        
        elif isinstance(node, VariableNode):
            symbol = self.symbol_table.lookup(node.name)
            if symbol and symbol.symbol_type == 'variable':
                result = symbol.var_type
        
        elif isinstance(node, ArithmeticBinaryOpNode):
            # Result of arithmetic is numeric
            left_type = self._get_expression_type(node.left)
            right_type = self._get_expression_type(node.right)
            if left_type in ('integer', 'real') and right_type in ('integer', 'real'):
                result = 'real' if 'real' in (left_type, right_type) else 'integer'
        
        elif isinstance(node, ComparisonNode):
            result = 'boolean'
        
        elif isinstance(node, BooleanBinaryOpNode):
            result = 'boolean'
        
        elif isinstance(node, PredicateCallNode):
            # Check if it's actually a function call
            symbol = self.symbol_table.lookup(node.name)
            if symbol and symbol.symbol_type == 'function':
                result = symbol.attributes.get('return_type', 'auto')
        
        # Cache the computed type
        if result is not None:
            self._expression_types[node_id] = result
        
        return result
    
    def _is_type_compatible(self, target_type: str, value_type: str) -> bool:
        """Check if value_type can be assigned to target_type
        
        Note: This could be optimized with BDDs for complex type hierarchies,
        but the current implementation is sufficient for TCE's type system.
        """
        if target_type == value_type:
            return True
        
        # Auto type accepts anything
        if target_type == 'auto':
            return True
        
        # Numeric type hierarchy
        if target_type == 'number' and value_type in ('integer', 'real'):
            return True
        
        # No implicit conversions for now
        return False

    def _report_error(self, message: str, node: Optional[ASTNode] = None) -> None:
        """
        Add a semantic error to the error collection.
        
        Args:
            message: Descriptive error message
            node: AST node where error occurred (for location info)
        """
        line = getattr(node, 'line', None)
        col = getattr(node, 'column', None)
        self.errors.append(SemanticError(message, line_number=line, column_number=col))

    def analyze(self, node: Optional[ASTNode]) -> Tuple[Optional[ASTNode], List[SemanticError]]:
        """
        Perform semantic analysis on the given AST node.
        
        This is the main entry point for semantic analysis. It resets the error
        state and traverses the AST using the visitor pattern.
        
        Args:
            node: Root AST node to analyze
            
        Returns:
            Tuple of (analyzed_node, list_of_errors)
        """
        self.errors = []  # Reset errors for a new analysis run
        # Could populate built-in types/functions from vocabulary here
        if node is not None:
            self._visit(node)
        return node, self.errors

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
        """Visit variable declaration node with comprehensive validation"""
        self._validate_variable_type(node)
        
        if not self._check_variable_redeclaration(node):
            self._define_variable_symbol(node)
        
        if node.value:
            self._process_variable_initializer(node)
    
    def _validate_variable_type(self, node) -> None:
        """Validate that the variable type exists in vocabulary"""
        if node.var_type != 'auto' and node.var_type not in self.vocabulary.get('types', set()):
            self._report_error(f"Type '{node.var_type}' is not defined in the vocabulary.", node)
    
    def _check_variable_redeclaration(self, node) -> bool:
        """Check for variable redeclaration in current scope
        
        Returns:
            True if redeclaration detected, False otherwise
        """
        existing_symbol = self.symbol_table.lookup_current_scope(node.name)
        if existing_symbol:
            self._report_error(f"Variable '{node.name}' already declared in this scope.", node)
            return True
        return False
    
    def _define_variable_symbol(self, node) -> None:
        """Define variable symbol in symbol table with type validation"""
        actual_type = self._resolve_variable_type(node)
        symbol = Symbol(node.name, 'variable', self.symbol_table.current_scope_level, 
                       ast_node=node, var_type=actual_type)
        self.symbol_table.define(symbol)
    
    def _resolve_variable_type(self, node) -> str:
        """Resolve variable type, handling 'auto' type inference"""
        if node.var_type == 'auto' and not node.value:
            self._report_error("Variable with 'auto' type requires an initializer.", node)
        return node.var_type
    
    def _process_variable_initializer(self, node) -> None:
        """Process variable initializer and perform type checking"""
        self._visit(node.value)
        value_type = self._get_expression_type(node.value)
        
        if node.var_type == 'auto' and value_type:
            self._update_inferred_type(node, value_type)
        elif node.var_type != 'auto' and value_type:
            self._validate_assignment_type_compatibility(node, value_type)
    
    def _update_inferred_type(self, node, inferred_type: str) -> None:
        """Update symbol with inferred type for 'auto' variables"""
        symbol = self.symbol_table.lookup(node.name)
        if symbol:
            symbol.var_type = inferred_type
    
    def _validate_assignment_type_compatibility(self, node, value_type: str) -> None:
        """Validate type compatibility for explicit type assignments"""
        if not self._is_type_compatible(node.var_type, value_type):
            self._report_error(
                f"Type mismatch: cannot assign '{value_type}' to variable of type '{node.var_type}'", 
                node
            )

    def _visit_VariableNode(self, node):
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            self._report_error(f"Variable '{node.name}' not declared.", node)
        elif symbol.symbol_type != 'variable':
            self._report_error(f"Identifier '{node.name}' is not a variable.", node)
        # Store resolved symbol or type info on the node for later stages (e.g. type checking expressions)
        # node.resolved_symbol = symbol 

    def _visit_AssignmentNode(self, node):
        self._visit(node.target) # Should be a VariableNode or similar l-value
        self._visit(node.expression)
        # Type checking for assignment compatibility will be implemented as needed

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
        """Visit arithmetic binary operation node"""
        self._visit(node.left)
        self._visit(node.right)
        self._validate_arithmetic_operands(node)
    
    def _validate_arithmetic_operands(self, node) -> None:
        """Validate that operands are compatible with arithmetic operations"""
        left_symbol = self._get_operand_symbol(node.left)
        right_symbol = self._get_operand_symbol(node.right)
        
        arithmetic_types = {'integer', 'real', 'number'}
        
        if left_symbol and left_symbol.var_type not in arithmetic_types:
            self._report_error(
                f"Left operand of '{node.operator}' must be numeric type, got '{left_symbol.var_type}'", 
                node
            )
        
        if right_symbol and right_symbol.var_type not in arithmetic_types:
            self._report_error(
                f"Right operand of '{node.operator}' must be numeric type, got '{right_symbol.var_type}'", 
                node
            )
    
    def _get_operand_symbol(self, operand) -> Optional[Symbol]:
        """Get symbol for an operand if it's a variable"""
        if hasattr(operand, 'name') and isinstance(operand, VariableNode):
            return self.symbol_table.lookup(operand.name)
        return None

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
        """Visit predicate call node"""
        # Visit all arguments
        if node.args:
            for arg in node.args:
                self._visit(arg)
        
        # Check if predicate is declared and arity matches
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            self._report_error(f"Predicate '{node.name}' not declared.", node)
        elif symbol.symbol_type != 'predicate':
            self._report_error(f"'{node.name}' is not a predicate.", node)
        else:
            # Check arity if predicate has arity information
            expected_arity = symbol.attributes.get('arity')
            actual_arity = len(node.args) if node.args else 0
            
            if expected_arity is not None and expected_arity != actual_arity:
                self._report_error(f"Predicate '{node.name}' expects {expected_arity} arguments, got {actual_arity}.", node)

    def _visit_PredicateDefinitionNode(self, node):
        """Visit predicate definition node"""
        if self._check_definition_redeclaration(node, 'predicate'):
            return
        
        symbol = self._create_predicate_symbol(node)
        self.symbol_table.define(symbol)
        
        self._analyze_definition_body(node)
    
    def _check_definition_redeclaration(self, node, definition_type: str) -> bool:
        """Check for redefinition of predicates/functions
        
        Returns:
            True if redefinition detected, False otherwise
        """
        existing_symbol = self.symbol_table.lookup_current_scope(node.name)
        if existing_symbol:
            self._report_error(f"{definition_type.capitalize()} '{node.name}' already defined in this scope.", node)
            return True
        return False
    
    def _create_predicate_symbol(self, node) -> Symbol:
        """Create symbol for predicate definition"""
        arity = len(node.parameters) if node.parameters else 0
        symbol = Symbol(node.name, 'predicate', self.symbol_table.current_scope_level, ast_node=node)
        symbol.attributes['arity'] = arity
        return symbol
    
    def _analyze_definition_body(self, node) -> None:
        """Analyze predicate/function body with parameter scope"""
        self.symbol_table.enter_scope()
        
        try:
            self._define_parameters(node)
            if node.body:
                self._visit(node.body)
        finally:
            self.symbol_table.exit_scope()
    
    def _define_parameters(self, node) -> None:
        """Define parameters in current scope"""
        if not node.parameters:
            return
        
        for param in node.parameters:
            if isinstance(param, VariableNode):
                param_symbol = Symbol(
                    param.name, 'variable', 
                    self.symbol_table.current_scope_level,
                    ast_node=param, var_type='auto'
                )
                if not self.symbol_table.define(param_symbol):
                    self._report_error(f"Parameter '{param.name}' already defined.", param)

    def _visit_FunctionDefinitionNode(self, node):
        """Visit function definition node"""
        if self._check_definition_redeclaration(node, 'function'):
            return
        
        symbol = self._create_function_symbol(node)
        self.symbol_table.define(symbol)
        
        self._analyze_definition_body(node)
    
    def _create_function_symbol(self, node) -> Symbol:
        """Create symbol for function definition"""
        arity = len(node.parameters) if node.parameters else 0
        symbol = Symbol(node.name, 'function', self.symbol_table.current_scope_level, ast_node=node)
        symbol.attributes['arity'] = arity
        return symbol

    def _visit_QuantifierBlockNode(self, node):
        """Visit quantifier block node"""
        # Enter new scope for quantified variables
        self.symbol_table.enter_scope()
        
        # Define quantified variables in the new scope
        if node.variables:
            for var in node.variables:
                if isinstance(var, VariableNode):
                    var_symbol = Symbol(var.name, 'variable', self.symbol_table.current_scope_level,
                                      ast_node=var, var_type='auto')
                    if not self.symbol_table.define(var_symbol):
                        self._report_error(f"Quantified variable '{var.name}' already defined.", var)
        
        # Analyze condition if present
        if node.condition:
            self._visit(node.condition)
        
        # Note: We don't exit scope here because the parent node (ConditionNode) 
        # needs to analyze the expression with these variables in scope
        # The exit_scope will be called by the parent

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
