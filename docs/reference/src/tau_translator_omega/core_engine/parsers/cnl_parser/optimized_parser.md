Module src.tau_translator_omega.core_engine.parsers.cnl_parser.optimized_parser
===============================================================================
Optimized CNL Parser with Performance Improvements

This module implements the high-impact optimizations identified in the performance analysis:
1. Operator precedence parsing (O(n) instead of O(n²))
2. Singleton regex patterns (eliminates recompilation)
3. Memory-optimized AST nodes
4. Cached parsing for repeated patterns

Functions
---------

`create_optimized_parser(debug: bool = False, enable_caching: bool = True) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.optimized_parser.OptimizedCNLParser`
:   Create an optimized parser instance.

Classes
-------

`OperatorPrecedenceParser(tokens: List[tuple])`
:   O(n) expression parser using operator precedence (Pratt parser).

    ### Class variables

    `PRECEDENCE`
    :

    ### Methods

    `consume_token(self) ‑> tuple | None`
    :   Consume and return current token.

    `current_token(self) ‑> tuple | None`
    :   Get current token without advancing.

    `parse_atom(self) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Parse atomic values.

    `parse_expression(self, min_precedence: int = 0) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Parse expression with operator precedence - O(n) complexity.

    `parse_function_call(self) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateCallNode`
    :   Parse function/predicate calls.

    `parse_primary(self) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Parse primary expressions (atoms, parentheses, function calls).

    `peek_operator_precedence(self) ‑> int`
    :   Get precedence of current operator.

`OptimizedCNLParser(debug: bool = False, enable_caching: bool = True)`
:   High-performance CNL parser with algorithmic optimizations.
    
    Features:
    - O(n) expression parsing instead of O(n²)
    - Singleton pattern for regex compilation
    - Memoized parsing for repeated patterns
    - Streaming tokenization for large inputs

    ### Methods

    `get_performance_stats(self) ‑> dict`
    :   Get performance statistics.

    `parse(self, text: str) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Parse CNL text with optimizations.

`OptimizedTokenizer()`
:   High-performance tokenizer with streaming support.

    ### Methods

    `streaming_tokenize(self, text: str) ‑> Iterator[tuple]`
    :   Memory-efficient streaming tokenizer for large inputs.

    `tokenize(self, text: str) ‑> List[tuple]`
    :   Fast tokenization with optimized pattern matching.

`TokenPatterns()`
:   Singleton for compiled regex patterns - eliminates recompilation overhead.

    ### Instance variables

    `patterns`
    :