Module src.tau_translator_omega.core_engine.parsers.parser.domain_types
=======================================================================
Domain types for grammar-driven parsing.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`ASTTransformer(*args, **kwargs)`
:   Protocol for AST transformers.

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Methods

    `transform(self, cst: Any) ‑> Any`
    :   Transform CST to AST.

`GrammarConfig(formalism: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarFormalism, file_path: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarPath, parser_type: str = 'lalr', start_symbol: str = 'start', keep_all_tokens: bool = False, propagate_positions: bool = True, maybe_placeholders: bool = False, debug_lark: bool = False)`
:   Grammar configuration data.

    ### Instance variables

    `debug_lark: bool`
    :

    `file_path: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarPath`
    :

    `formalism: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarFormalism`
    :

    `keep_all_tokens: bool`
    :

    `maybe_placeholders: bool`
    :

    `parser_type: str`
    :

    `propagate_positions: bool`
    :

    `start_symbol: str`
    :

`GrammarFormalism(*args, **kwds)`
:   Supported grammar formalisms.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ANTLR`
    :

    `LARK`
    :

`ParseResult(*args, **kwargs)`
:   Protocol for parse results.

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Methods

    `pretty(self) ‑> str`
    :   Return pretty-printed representation.

`ParserError(*args, **kwargs)`
:   Custom exception for parser-related errors.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`TransformerConfig(class_name: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerName, module_path: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ModulePath, is_available: bool = False)`
:   Transformer configuration data.

    ### Instance variables

    `class_name: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerName`
    :

    `is_available: bool`
    :

    `module_path: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ModulePath`
    :