Module src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy
======================================================================================
Parsing strategy pattern implementation following the Intentional Disclosure Principle.

Provides different parsing strategies for various grammar formalisms.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`EbnfParsingStrategy(logger: src.tau_translator_omega.core_engine.parsers.parser.infrastructure.parser_io.LoggingService | None = None, cache_manager: Any | None = None)`
:   Parsing strategy for EBNF grammars.
    Converts EBNF to Lark format and uses Lark parser.
    
    Initialize Lark parsing strategy.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.LarkParsingStrategy
    * src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.ParsingStrategy
    * abc.ABC

    ### Methods

    `create_parser_async(self, grammar: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarContent, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, import_paths: List[pathlib.Path]) ‑> returns.result.Result[typing.Any, str]`
    :   Create parser for EBNF grammar.

    `supports_formalism(self, formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism) ‑> bool`
    :   EBNF strategy only supports EBNF.

`FallbackParsingStrategy(supported_strategies: List[src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.ParsingStrategy])`
:   Fallback strategy for unsupported grammar formalisms.
    Provides helpful error messages.
    
    Initialize with list of supported strategies.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.ParsingStrategy
    * abc.ABC

    ### Methods

    `create_parser_async(self, grammar: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarContent, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, import_paths: List[pathlib.Path]) ‑> returns.result.Result[typing.Any, str]`
    :   Report unsupported formalism.

    `parse_source_async(self, parser: Any, source: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceCode, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseResult, str]`
    :   Cannot parse with fallback.

    `supports_formalism(self, formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism) ‑> bool`
    :   Fallback supports nothing.

`LarkParsingStrategy(logger: src.tau_translator_omega.core_engine.parsers.parser.infrastructure.parser_io.LoggingService | None = None, cache_manager: Any | None = None)`
:   Parsing strategy for Lark grammars.
    Supports LALR, Earley, and CYK parsing algorithms.
    
    Initialize Lark parsing strategy.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.ParsingStrategy
    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.EbnfParsingStrategy

    ### Methods

    `create_parser_async(self, grammar: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarContent, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, import_paths: List[pathlib.Path]) ‑> returns.result.Result[typing.Any, str]`
    :   Create Lark parser instance.

    `parse_source_async(self, parser: Any, source: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceCode, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseResult, str]`
    :   Parse source using Lark.

    `supports_formalism(self, formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism) ‑> bool`
    :   Check if Lark supports formalism.

`ParsingStrategy()`
:   Abstract base class for parsing strategies.
    Each strategy handles a specific grammar formalism.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.FallbackParsingStrategy
    * src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.LarkParsingStrategy
    * src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.PegParsingStrategy

    ### Methods

    `create_parser_async(self, grammar: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarContent, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, import_paths: List[pathlib.Path]) ‑> returns.result.Result[typing.Any, str]`
    :   Create parser instance for the strategy.

    `get_strategy_name(self) ‑> str`
    :   Get strategy name for logging.

    `parse_source_async(self, parser: Any, source: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceCode, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseResult, str]`
    :   Parse source code using the strategy.

    `supports_formalism(self, formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism) ‑> bool`
    :   Check if strategy supports given formalism.

`PegParsingStrategy()`
:   Parsing strategy for PEG (Parsing Expression Grammar).
    Placeholder for future PEG parser implementation.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.ParsingStrategy
    * abc.ABC

    ### Methods

    `create_parser_async(self, grammar: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarContent, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, import_paths: List[pathlib.Path]) ‑> returns.result.Result[typing.Any, str]`
    :   Create PEG parser (not implemented).

    `parse_source_async(self, parser: Any, source: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceCode, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseResult, str]`
    :   Parse using PEG (not implemented).

    `supports_formalism(self, formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism) ‑> bool`
    :   Check if PEG is supported.

`StrategySelector(logger: src.tau_translator_omega.core_engine.parsers.parser.infrastructure.parser_io.LoggingService | None = None)`
:   Selects appropriate parsing strategy based on grammar formalism.
    Implements strategy pattern for parser selection.
    
    Initialize strategy selector.

    ### Methods

    `get_supported_formalisms(self) ‑> List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism]`
    :   Get list of supported formalisms.

    `select_strategy(self, formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism) ‑> src.tau_translator_omega.core_engine.parsers.parser.strategies.parsing_strategy.ParsingStrategy`
    :   Select parsing strategy for formalism.