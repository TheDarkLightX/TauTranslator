Module src.tau_translator_omega.core_engine.parsers.cnl_parser.mock_parser
==========================================================================
Mock CNL Parser for testing when Lark is not available.

This provides a simplified parser implementation that can handle basic CNL constructs
without relying on Lark, allowing us to test the AST generation and transformer logic.

Functions
---------

`create_mock_parser(debug: bool = False) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.mock_parser.MockCNLParser`
:   Create a mock parser instance.

Classes
-------

`MockCNLParser(debug: bool = False)`
:   Mock parser that handles basic CNL constructs for testing purposes.
    
    This is a simplified implementation that can parse:
    - Boolean constants: true, false
    - Numeric constants: 42, 3.14
    - String constants: "hello"
    - Simple predicates: is_hot(sun)
    - Basic comparisons: temperature > 30
    - Simple facts ending with period

    ### Methods

    `parse(self, text: str) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Parse CNL text and return AST.

    `tokenize(self, text: str) ‑> List[tuple]`
    :   Simple tokenizer that returns (token_type, value, position) tuples.