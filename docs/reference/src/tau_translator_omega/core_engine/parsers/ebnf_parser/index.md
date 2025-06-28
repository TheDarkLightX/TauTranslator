Module src.tau_translator_omega.core_engine.parsers.ebnf_parser
===============================================================
EBNF Parser Module

High-performance EBNF (Extended Backus-Naur Form) parser for grammar processing.
Part of Phase 1.1 of the TauTranslatorOmega development roadmap.

This module provides:
- EBNF grammar parsing into AST
- Grammar validation and error handling
- Support for standard EBNF constructs
- Integration with LLM control libraries (transformers-CFG, Guidance)

Sub-modules
-----------
* src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes
* src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_parser

Functions
---------

`create_ebnf_parser(debug: bool = False) ‑> src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_parser.EBNFParser`
:   Create an EBNF parser instance.
    
    Args:
        debug: Enable debug output
        
    Returns:
        EBNFParser: Parser instance ready for use

Classes
-------

`ChoiceNode(alternatives: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode])`
:   Node representing choice: A | B | C

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `alternatives: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode]`
    :

`EBNFNode()`
:   Base class for all EBNF AST nodes with memory optimization.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.GrammarNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RuleNode

    ### Methods

    `accept(self, visitor)`
    :   Accept a visitor for traversal.

`EBNFParser(debug: bool = False)`
:   High-performance EBNF parser using recursive descent.
    
    Parses EBNF grammars into memory-optimized AST.
    Designed for integration with LLM control libraries.

    ### Methods

    `clear_cache(self)`
    :   Clear the parsing cache.

    `get_performance_stats(self) ‑> Dict[str, Any]`
    :   Get parser performance statistics.

    `is_available(self) ‑> bool`
    :   Check if parser is available and working.

    `parse(self, text: str, use_cache: bool = True) ‑> src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.GrammarNode`
    :   Parse EBNF text into AST.
        
        Args:
            text: EBNF grammar text
            use_cache: Whether to use caching for repeated grammars
            
        Returns:
            GrammarNode: Root of the AST
            
        Raises:
            ValueError: For invalid input
            RuntimeError: For parsing errors

    `parse_file(self, file_path: str) ‑> src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.GrammarNode`
    :   Parse EBNF grammar from file.

`GrammarNode(rules: List[ForwardRef('RuleNode')])`
:   Root node representing an entire EBNF grammar.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `rules: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RuleNode]`
    :

`GroupNode(expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode)`
:   Node representing grouping: (A B C)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
    :

`LiteralNode(value: str, quote_type: str = '"')`
:   Node representing string literal: "hello" or 'hello'

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.TerminalNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `quote_type: str`
    :

    `value: str`
    :

`NonTerminalNode(name: str)`
:   Node representing non-terminal reference: rule_name

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `name: str`
    :

`OptionalNode(expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode)`
:   Node representing optional: [A] or A?

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
    :

`RegexNode(pattern: str, flags: str = '')`
:   Node representing regex pattern: /pattern/

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.TerminalNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `flags: str`
    :

    `pattern: str`
    :

`RepetitionNode(expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode, min_count: int = 0, max_count: int | None = None)`
:   Node representing repetition: {A} or A* or A+

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
    :

    `max_count: int | None`
    :

    `min_count: int`
    :

`RuleNode(name: str, expression: ExpressionNode)`
:   Node representing a single EBNF rule: name = expression.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
    :

    `name: str`
    :

`SequenceNode(elements: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode])`
:   Node representing sequence: A B C

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `elements: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode]`
    :

`TerminalNode()`
:   Base class for terminal nodes (literals, regex).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.LiteralNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RegexNode