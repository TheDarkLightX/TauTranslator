Module src.tau_translator_omega.core_engine.parsers.parser.parsing_service
==========================================================================
Core parsing service with business logic.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`ErrorContextBuilder()`
:   Builds detailed error context for parsing failures.

    ### Static methods

    `build_error_context(error: Exception, source_code: src.tau_translator_omega.core_engine.parsers.parser.domain_types.SourceCode) ‑> str`
    :   Build detailed error context from parsing exception.

`ParseResultValidator()`
:   Validates parsing results.

    ### Static methods

    `validate_parse_result(result: Any, source_code: src.tau_translator_omega.core_engine.parsers.parser.domain_types.SourceCode) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.ParseResult`
    :   Validate that parse result is valid.

`ParsingService(parser_instance: Any, transformer: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ASTTransformer | None)`
:   Core parsing service that orchestrates the parsing process.
    
    Initialize parsing service with parser and transformer.

    ### Methods

    `parse_source(self, source_code: src.tau_translator_omega.core_engine.parsers.parser.domain_types.SourceCode) ‑> Any`
    :   Parse source code and return AST or CST.

    `transform_cst(self, cst: lark.tree.Tree, source_code: src.tau_translator_omega.core_engine.parsers.parser.domain_types.SourceCode = '') ‑> Any`
    :   Transform existing CST to AST.

`TransformationService(transformer: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ASTTransformer | None)`
:   Handles CST to AST transformation.
    
    Initialize with optional transformer.

    ### Methods

    `transform_to_ast(self, cst: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ParseResult, source_code: src.tau_translator_omega.core_engine.parsers.parser.domain_types.SourceCode) ‑> Any`
    :   Transform CST to AST if transformer available.