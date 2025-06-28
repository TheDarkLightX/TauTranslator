Module src.tau_translator_omega.core_engine.parsers.parser
==========================================================
Modular grammar-driven parser following the Intentional Disclosure Principle.

Copyright: DarkLightX / Dana Edwards

Sub-modules
-----------
* src.tau_translator_omega.core_engine.parsers.parser.domain
* src.tau_translator_omega.core_engine.parsers.parser.domain_types
* src.tau_translator_omega.core_engine.parsers.parser.infrastructure
* src.tau_translator_omega.core_engine.parsers.parser.parser_factory
* src.tau_translator_omega.core_engine.parsers.parser.parsing_service
* src.tau_translator_omega.core_engine.parsers.parser.path_resolver
* src.tau_translator_omega.core_engine.parsers.parser.services
* src.tau_translator_omega.core_engine.parsers.parser.strategies

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

`ErrorContextBuilder()`
:   Builds detailed error context for parsing failures.

    ### Static methods

    `build_error_context(error: Exception, source_code: src.tau_translator_omega.core_engine.parsers.parser.domain_types.SourceCode) ‑> str`
    :   Build detailed error context from parsing exception.

`FallbackTransformer()`
:   Fallback transformer when no custom transformer is available.

    ### Static methods

    `create_fallback_ast(cst: Any) ‑> Any`
    :   Create basic AST from CST when no transformer available.

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

`GrammarFileLoader()`
:   Loads and validates grammar files.

    ### Static methods

    `load_grammar_content(grammar_path: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarPath) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarContent`
    :   Load grammar content from file.

`GrammarFormalism(*args, **kwds)`
:   Supported grammar formalisms.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ANTLR`
    :

    `LARK`
    :

`GrammarValidator()`
:   Validates grammar configurations.

    ### Static methods

    `validate_formalism(formalism: str) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarFormalism`
    :   Validate and convert formalism string.

    `validate_grammar_config(plugin_config: dict) ‑> None`
    :   Validate grammar configuration completeness.

`LarkParserFactory()`
:   Factory for creating Lark parser instances.

    ### Static methods

    `create_parser(grammar_content: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarContent, config: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarConfig) ‑> Any`
    :   Create Lark parser instance.

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

`ParserFactory()`
:   Factory for creating parser instances based on formalism.

    ### Static methods

    `create_parser(grammar_config: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarConfig) ‑> Any`
    :   Create parser instance based on formalism.

`ParsingService(parser_instance: Any, transformer: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ASTTransformer | None)`
:   Core parsing service that orchestrates the parsing process.
    
    Initialize parsing service with parser and transformer.

    ### Methods

    `parse_source(self, source_code: src.tau_translator_omega.core_engine.parsers.parser.domain_types.SourceCode) ‑> Any`
    :   Parse source code and return AST or CST.

    `transform_cst(self, cst: lark.tree.Tree, source_code: src.tau_translator_omega.core_engine.parsers.parser.domain_types.SourceCode = '') ‑> Any`
    :   Transform existing CST to AST.

`PluginConfigExtractor()`
:   Extracts configuration from plugin objects.

    ### Static methods

    `extract_grammar_config(plugin) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarConfig`
    :   Extract grammar configuration from plugin.

    `extract_transformer_config(plugin) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerConfig`
    :   Extract transformer configuration from plugin.

`ProjectPathResolver()`
:   Resolves project-relative paths.

    ### Static methods

    `resolve_grammars_directory(project_root: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ProjectRoot) ‑> pathlib.Path`
    :   Get the common grammars directory.

    `resolve_project_root(current_file: str) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.ProjectRoot`
    :   Resolve project root from current file path.

`TransformationService(transformer: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ASTTransformer | None)`
:   Handles CST to AST transformation.
    
    Initialize with optional transformer.

    ### Methods

    `transform_to_ast(self, cst: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ParseResult, source_code: src.tau_translator_omega.core_engine.parsers.parser.domain_types.SourceCode) ‑> Any`
    :   Transform CST to AST if transformer available.

`TransformerConfig(class_name: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerName, module_path: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ModulePath, is_available: bool = False)`
:   Transformer configuration data.

    ### Instance variables

    `class_name: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerName`
    :

    `is_available: bool`
    :

    `module_path: src.tau_translator_omega.core_engine.parsers.parser.domain_types.ModulePath`
    :

`TransformerFactory()`
:   Factory for creating transformer instances.

    ### Static methods

    `create_transformer(transformer_config: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerConfig) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.ASTTransformer | None`
    :   Create transformer instance if available.

`TransformerLoader()`
:   Loads transformer classes dynamically.

    ### Static methods

    `load_transformer(config: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerConfig) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.ASTTransformer | None`
    :   Load transformer instance from configuration.

    `parse_transformer_fqn(fqn: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerName) ‑> Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain_types.ModulePath, src.tau_translator_omega.core_engine.parsers.parser.domain_types.ClassName]`
    :   Parse fully qualified name into module and class.