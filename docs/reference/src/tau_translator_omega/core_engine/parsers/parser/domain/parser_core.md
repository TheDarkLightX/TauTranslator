Module src.tau_translator_omega.core_engine.parsers.parser.domain.parser_core
=============================================================================
Pure parser core logic following the Intentional Disclosure Principle.

All methods are pure functions with ≤10 lines, providing complete
type disclosure and no side effects.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`ConfigurationMerger()`
:   Merges configurations from multiple sources.

    ### Methods

    `apply_environment_overrides(self, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig`
    :   Apply environment variable overrides (pure function).

    `merge_configs(self, base: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, overrides: Dict) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, str]`
    :   Merge parser configuration with overrides.

`GrammarValidator()`
:   Pure grammar validation logic.

    ### Methods

    `check_for_left_recursion(self, content: str) ‑> returns.result.Result[str | None, str]`
    :   Check for direct left recursion (warning only).

    `validate_grammar_content(self, content: str) ‑> returns.result.Result[str, str]`
    :   Validate grammar content is not empty.

    `validate_grammar_syntax(self, content: str, formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism) ‑> returns.result.Result[str, str]`
    :   Validate grammar syntax based on formalism.

    `validate_start_symbol(self, content: str, start: str) ‑> returns.result.Result[str, str]`
    :   Validate start symbol exists in grammar.

`ParserCore()`
:   Pure business logic for parser configuration and validation.

    ### Methods

    `build_parser_config(self, plugin: src.tau_translator_omega.core_engine.parsers.parser.infrastructure.plugin_types.Plugin) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, str]`
    :   Build parser configuration from plugin.

    `build_transformer_config(self, plugin: src.tau_translator_omega.core_engine.parsers.parser.infrastructure.plugin_types.Plugin) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.TransformerConfig | None, str]`
    :   Build transformer configuration if available.

    `determine_parser_strategy(self, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig) ‑> str`
    :   Determine which parsing strategy to use.

    `validate_formalism_support(self, formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism, str]`
    :   Validate that grammar formalism is supported.