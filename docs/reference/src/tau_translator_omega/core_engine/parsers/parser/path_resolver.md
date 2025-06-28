Module src.tau_translator_omega.core_engine.parsers.parser.path_resolver
========================================================================
Infrastructure layer for grammar-driven parsing.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`GrammarFileLoader()`
:   Loads and validates grammar files.

    ### Static methods

    `load_grammar_content(grammar_path: src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarPath) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.GrammarContent`
    :   Load grammar content from file.

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

`TransformerLoader()`
:   Loads transformer classes dynamically.

    ### Static methods

    `load_transformer(config: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerConfig) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain_types.ASTTransformer | None`
    :   Load transformer instance from configuration.

    `parse_transformer_fqn(fqn: src.tau_translator_omega.core_engine.parsers.parser.domain_types.TransformerName) ‑> Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain_types.ModulePath, src.tau_translator_omega.core_engine.parsers.parser.domain_types.ClassName]`
    :   Parse fully qualified name into module and class.