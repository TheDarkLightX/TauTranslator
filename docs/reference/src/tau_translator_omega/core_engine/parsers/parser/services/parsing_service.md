Module src.tau_translator_omega.core_engine.parsers.parser.services.parsing_service
===================================================================================
Parsing service orchestration following the Intentional Disclosure Principle.

Coordinates parsing workflow with all methods ≤10 lines.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`MetricsCollector()`
:   Collects and aggregates parsing metrics.
    
    Initialize metrics collector.

    ### Methods

    `get_summary(self) ‑> Dict[str, Any]`
    :   Get metrics summary.

    `record_parse(self, metrics: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParsingMetrics) ‑> None`
    :   Record parsing metrics.

`ParseAttemptResult(tree: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseTree | None, errors: List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseError], recovery_attempts: int)`
:   Result of a parse attempt.

    ### Instance variables

    `errors: List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseError]`
    :

    `recovery_attempts: int`
    :

    `tree: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseTree | None`
    :

`ParsingService(parser_adapter: src.tau_translator_omega.core_engine.parsers.parser.infrastructure.lark_adapter.LarkParserAdapter, recovery_strategy: src.tau_translator_omega.core_engine.parsers.parser.domain.error_recovery.ErrorRecoveryStrategy, cache_manager: src.tau_translator_omega.core_engine.parsers.parser.infrastructure.parser_io.CacheManager | None = None, logger: src.tau_translator_omega.core_engine.parsers.parser.infrastructure.parser_io.LoggingService | None = None)`
:   Main service orchestrating the parsing workflow.
    Combines all parsing components into cohesive service.
    
    Initialize parsing service with dependencies.

    ### Methods

    `parse_source_async(self, source: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceCode, parser: Any, config: Any, use_cache: bool = True) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseResult, str]`
    :   Parse source code with caching and metrics.

`TransformationService(transformer_loader: Any, logger: src.tau_translator_omega.core_engine.parsers.parser.infrastructure.parser_io.LoggingService | None = None)`
:   Service for transforming parse trees to ASTs.
    Manages transformer lifecycle and error handling.
    
    Initialize transformation service.

    ### Methods

    `transform_tree_async(self, tree: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseTree, transformer_config: Any) ‑> returns.result.Result[typing.Any, str]`
    :   Transform parse tree to AST.