Module src.tau_translator_omega.core_engine.parsers.enhanced_parser
===================================================================
Enhanced CNL Parser with Dynamic Grammar Support
===============================================

This parser extends the base parser to support dynamic grammar loading,
allowing it to work with grammar files selected in the UI.

Functions
---------

`create_default_parser(debug: bool = False) ‑> src.tau_translator_omega.core_engine.parsers.enhanced_parser.EnhancedParser`
:   Create parser with default TCE grammar.

`create_parser_with_file(grammar_file: str | pathlib.Path, debug: bool = False) ‑> src.tau_translator_omega.core_engine.parsers.enhanced_parser.EnhancedParser`
:   Create parser with grammar file.

`create_parser_with_grammar(grammar_string: str, debug: bool = False) ‑> src.tau_translator_omega.core_engine.parsers.enhanced_parser.EnhancedParser`
:   Create parser with custom grammar string.

Classes
-------

`EnhancedParser(grammar_string: str | None = None, grammar_file_path: str | pathlib.Path | None = None, debug: bool = False)`
:   Enhanced parser that supports dynamic grammar loading.
    
    Can load grammar from:
    1. A string (for dynamically generated grammar)
    2. A file path (for pre-existing grammar files)
    3. Default TCE grammar if nothing specified
    
    Initialize the parser with optional custom grammar.
    
    Args:
        grammar_string: Grammar content as a string (takes precedence)
        grammar_file_path: Path to grammar file
        debug: Enable debug output

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.enhanced_parser.GrammarAwareParser

    ### Methods

    `get_grammar_info(self) ‑> dict`
    :   Get information about the loaded grammar.

    `parse(self, text: str) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Parse text using the loaded grammar.
        
        Args:
            text: Input text to parse
            
        Returns:
            ASTNode: Parsed AST
            
        Raises:
            ValueError: For empty input
            RuntimeError: For parsing errors

    `reload_grammar(self, grammar_string: str | None = None, grammar_file_path: str | pathlib.Path | None = None)`
    :   Reload parser with new grammar.
        
        Args:
            grammar_string: New grammar content as string
            grammar_file_path: Path to new grammar file

    `validate_grammar(self) ‑> bool`
    :   Validate that the loaded grammar is working.
        
        Returns:
            bool: True if grammar is valid

`GrammarAwareParser(grammar_loader=None, debug: bool = False)`
:   Parser that integrates with the TGFGrammarLoader.
    
    Initialize parser with grammar loader integration.
    
    Args:
        grammar_loader: TGFGrammarLoader instance
        debug: Enable debug output

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.enhanced_parser.EnhancedParser

    ### Methods

    `reload_from_loader(self)`
    :   Reload grammar from the grammar loader.