Module src.tau_translator_omega.core_engine.semantic.semantic_analyzer_core
===========================================================================
Semantic Analyzer Core Logic
============================

Extracted from semantic_analyzer.py to maintain <600 line limit.
Contains the visitor pattern implementation and AST traversal logic.

Author: DarkLightX / Dana Edwards

Classes
-------

`ExpressionTypeResolver(symbol_table: src.tau_translator_omega.core_engine.semantic.semantic_types.SymbolTable, use_visitor_pattern: bool = False)`
:   Resolves types for expressions during semantic analysis.
    
    Follows VibeArchitect principles:
    - Single Responsibility: Only type resolution
    - Clear type inference rules
    - Performance monitoring
    
    Uses weakref-based caching to prevent memory leaks from AST nodes.

    ### Methods

    `get_cache_stats(self) ‑> dict`
    :   Get cache performance statistics.

    `get_expression_type(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode) ‑> str | None`
    :   Get the type of an expression node with memoization.
        
        Args:
            node: AST node to resolve type for
            
        Returns:
            Type string if resolvable, None otherwise

    `get_resolution_stats(self) ‑> dict`
    :   Get type resolution performance statistics.

`SymbolDefinitionManager(symbol_table: src.tau_translator_omega.core_engine.semantic.semantic_types.SymbolTable, error_collector: src.tau_translator_omega.core_engine.semantic.semantic_types.ErrorCollector)`
:   Manages symbol definition during semantic analysis.
    
    Follows VibeArchitect principles:
    - Single Responsibility: Only symbol management
    - Clear symbol creation rules
    - Comprehensive error handling

    ### Methods

    `define_function_symbol(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.FunctionDefinitionNode) ‑> bool`
    :   Define function symbol in symbol table.

    `define_parameters(self, node) ‑> None`
    :   Define parameters in current scope.

    `define_predicate_symbol(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateDefinitionNode) ‑> bool`
    :   Define predicate symbol in symbol table.

    `define_variable_symbol(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableDeclNode, resolved_type: str) ‑> bool`
    :   Define variable symbol in symbol table.
        
        Args:
            node: Variable declaration node
            resolved_type: Resolved variable type
            
        Returns:
            True if symbol defined successfully, False otherwise

`ValidationEngine(symbol_table: src.tau_translator_omega.core_engine.semantic.semantic_types.SymbolTable, type_resolver: src.tau_translator_omega.core_engine.semantic.semantic_analyzer_core.ExpressionTypeResolver, error_collector: src.tau_translator_omega.core_engine.semantic.semantic_types.ErrorCollector, vocabulary: dict)`
:   Handles validation logic for semantic analysis.
    
    Follows VibeArchitect principles:
    - Single Responsibility: Only validation
    - Clear validation rules
    - Comprehensive error reporting

    ### Methods

    `check_variable_redeclaration(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableDeclNode) ‑> bool`
    :   Check for variable redeclaration in current scope.
        
        Returns:
            True if redeclaration detected, False otherwise

    `validate_arithmetic_operands(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticBinaryOpNode) ‑> None`
    :   Validate arithmetic operation operands.

    `validate_predicate_call(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateCallNode) ‑> None`
    :   Validate predicate call.

    `validate_type_compatibility(self, target_type: str, value_type: str, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode) ‑> bool`
    :   Validate type compatibility between target and value types.
        
        Args:
            target_type: Expected type
            value_type: Actual type
            node: AST node for error reporting
            
        Returns:
            True if compatible, False otherwise

    `validate_variable_type(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableDeclNode) ‑> None`
    :   Validate that variable type exists in vocabulary.