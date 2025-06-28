Module src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_parser
===========================================================================
EBNF Parser - High-Performance Implementation

Phase 1.1 of TauTranslatorOmega development roadmap.
Parses EBNF (Extended Backus-Naur Form) grammars into AST.

Features:
- Standard EBNF syntax support
- Memory-optimized AST nodes
- Comprehensive error handling
- Integration ready for transformers-CFG and Guidance
- TDD approach with comprehensive testing

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

`EBNFTokenizer()`
:   Optimized tokenizer for EBNF grammars.
    
    Uses compiled regex patterns for efficient tokenization.

    ### Methods

    `tokenize(self, text: str) ‑> List[tuple]`
    :   Tokenize EBNF text into tokens.
        
        Returns list of (token_type, value, position) tuples.