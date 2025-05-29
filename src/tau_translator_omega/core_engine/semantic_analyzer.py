# Placeholder for Semantic Analyzer
# This will be developed via TDD.

from typing import List, Optional, Tuple

from tau_translator_omega.core_engine.cnl_parser.ast_nodes import ASTNode

class SemanticError(Exception):
    """Custom exception for semantic errors."""
    def __init__(self, message, line_number=None, column_number=None):
        super().__init__(message)
        self.message = message
        self.line_number = line_number
        self.column_number = column_number

    def __str__(self):
        if self.line_number is not None and self.column_number is not None:
            return f"SemanticError (L{self.line_number}, C{self.column_number}): {self.message}"
        elif self.line_number is not None:
            return f"SemanticError (L{self.line_number}): {self.message}"
        return f"SemanticError: {self.message}"

class Symbol:
    """Represents an entry in the symbol table."""
    def __init__(self, name, symbol_type, scope_level, ast_node=None, var_type=None):
        self.name = name
        self.symbol_type = symbol_type  # e.g., 'variable', 'predicate', 'type_name'
        self.scope_level = scope_level
        self.attributes = {}  # For storing type info, arity, etc.
        self.ast_node = ast_node # The AST node that declared this symbol (for location info)
        self.var_type = var_type

class SymbolTable:
    """Manages scopes and symbols."""
    def __init__(self):
        self.scopes = [{}] # Stack of scopes, global scope is at index 0
        self.current_scope_level = 0

    def enter_scope(self):
        """Enters a new nested scope."""
        self.current_scope_level += 1
        self.scopes.append({})

    def exit_scope(self):
        """Exits the current scope."""
        if self.current_scope_level > 0:
            self.scopes.pop()
            self.current_scope_level -= 1
        else:
            # Should not happen in a well-formed program
            raise SemanticError("Cannot exit global scope.")

    def define(self, symbol):
        """Defines a symbol in the current scope."""
        name = symbol.name
        if name in self.scopes[self.current_scope_level]:
            # Handle re-declaration error
            # For now, let's assume the analyzer using this table will check
            # and raise a more specific error based on the AST node.
            # Alternatively, this method could return False or raise an error.
            return False # Indicates re-declaration in current scope
        self.scopes[self.current_scope_level][name] = symbol
        return True

    def lookup(self, name):
        """Looks up a symbol, searching from current to outer scopes."""
        for i in range(self.current_scope_level, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None

    def lookup_current_scope(self, name):
        """Looks up a symbol only in the current scope."""
        return self.scopes[self.current_scope_level].get(name)

class SemanticAnalyzer:
    """Performs semantic analysis on an AST."""
    def __init__(self, vocabulary=None):
        self.vocabulary = vocabulary if vocabulary else {'types': set(['integer', 'string', 'boolean', 'auto'])}
        self.symbol_table = SymbolTable()
        self.errors = []
        # Potentially load built-in types/functions into symbol table from vocabulary

    def _report_error(self, message, node=None):
        """Adds a semantic error to the list of errors."""
        line = getattr(node, 'line', None)
        col = getattr(node, 'column', None)
        self.errors.append(SemanticError(message, line_number=line, column_number=col))

    def analyze(self, node: ASTNode) -> Tuple[ASTNode, List[SemanticError]]:
        """Analyzes the given AST node."""
        self.errors = [] # Reset errors for a new analysis run
        # TODO: Populate symbol table with built-ins from vocabulary if any
        self._visit(node)
        return node, self.errors

    def _visit(self, node):
        """Generic visit method that dispatches to specific node visitors."""
        if node is None:
            return
        method_name = f'_visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        """Default visitor for nodes not handled specifically."""
        # This should be overridden or node-specific visitors should handle children
        # For example, a SentenceNode would iterate self._visit(statement) for statement in node.statements
        # For now, we'll assume specific visitors will handle their children.
        # print(f"Visiting generic node: {type(node).__name__}")
        pass

    # --- Example Visitor Methods (to be expanded by TDD) ---

    def _visit_SentenceNode(self, node):
        for stmt in node.content: # Changed from node.statements
            self._visit(stmt)

    def _visit_VariableDeclNode(self, node):
        # Check if the type is known
        if node.var_type != 'auto' and node.var_type not in self.vocabulary.get('types', set()):
            self._report_error(f"Type '{node.var_type}' is not defined in the vocabulary.", node)
            # Potentially stop further analysis for this declaration if type is crucial

        # Check for redeclaration in the same scope
        # Ensure we are checking the current scope correctly
        existing_symbol_in_current_scope = self.symbol_table.lookup_current_scope(node.name)
        if existing_symbol_in_current_scope:
            self._report_error(f"Variable '{node.name}' already declared in this scope.", node)
        else:
            # TODO: Infer type if 'auto' and node.value is present
            actual_type = node.var_type
            if actual_type == 'auto':
                if node.value:
                    # Placeholder for type inference logic
                    # For now, we'll assume 'auto' is resolved by a later stage or needs explicit type from initializer
                    # We might need to determine the type of node.value here
                    pass 
                else:
                    self._report_error("Variable with 'auto' type requires an initializer.", node)
                    # If auto requires initializer and it's not there, maybe don't define it or define with 'unknown' type
                    # For now, we proceed to define it, but it might be an invalid state.
            
            # Only define the symbol if no redeclaration error in the current scope occurred.
            # The check above handles redeclaration. If we are in the 'else' block, it's safe to define.
            symbol = Symbol(node.name, 'variable', self.symbol_table.current_scope_level, ast_node=node, var_type=actual_type)
            self.symbol_table.define(symbol)

        if node.value: # If there's an initialization expression
            self._visit(node.value)
            # TODO: Type check: Ensure type of node.value is compatible with node.var_type (or inferred type for 'auto')

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
        # TODO: Type check assignment (target type vs value type)
        # For TDD, a separate test will drive this.

    def _visit_ConstantNode(self, node):
        # Constants are usually fine by themselves, type might be inferred or explicit
        # If explicit type on ConstantNode, could validate against vocabulary
        pass

    # Add more _visit_* methods as AST nodes are defined and tests require them
