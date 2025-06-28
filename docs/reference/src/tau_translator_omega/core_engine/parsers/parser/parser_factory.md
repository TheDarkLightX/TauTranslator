Module src.tau_translator_omega.core_engine.parsers.parser.parser_factory
=========================================================================
Parser factory for different grammar formalisms.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`FallbackTransformer()`
:   Fallback transformer when no custom transformer is available.

    ### Static methods

    `create_fallback_ast(cst: Any) ‑> Any`
    :   Create basic AST from CST when no transformer available.

`ParserFactory()`
:   Factory for creating parser instances based on formalism.

    ### Static methods

    `create_parser(grammar_config: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarConfig) ‑> Any`
    :   Create parser instance based on formalism.

`TransformerFactory()`
:   Factory for creating transformer instances.

    ### Static methods

    `create_transformer(transformer_config: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerConfig) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.ASTTransformer | None`
    :   Create transformer instance if available.