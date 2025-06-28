Module src.tau_translator_omega.core_engine.parsers.parser.domain.types
=======================================================================
Domain types and value objects for the parser following the Intentional Disclosure Principle.

These immutable domain types provide complete type disclosure and eliminate
primitive obsession throughout the parser implementation.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`ASTNode(*args, **kwargs)`
:   Protocol for AST nodes.

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Class variables

    `location: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceLocation | None`
    :

    ### Methods

    `accept(self, visitor: ASTVisitor) ‑> returns.result.Result[typing.Any, str]`
    :   Accept a visitor for processing.

`ASTVisitor(*args, **kwargs)`
:   Protocol for AST visitors.

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Methods

    `visit_expression(self, node: Any) ‑> returns.result.Result[typing.Any, str]`
    :   Visit expression node.

    `visit_program(self, node: Any) ‑> returns.result.Result[typing.Any, str]`
    :   Visit program node.

    `visit_statement(self, node: Any) ‑> returns.result.Result[typing.Any, str]`
    :   Visit statement node.

`CacheKey(source_hash: str, grammar_version: str, parser_config_hash: str)`
:   Key for parser cache.

    ### Static methods

    `from_source(source: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceCode, config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, version: str) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.CacheKey`
    :   Create cache key from source and config.

    ### Instance variables

    `grammar_version: str`
    :

    `parser_config_hash: str`
    :

    `source_hash: str`
    :

`GrammarConfig(grammar_path: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarPath, formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism, parser_config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig, transformer_class: src.tau_translator_omega.core_engine.parsers.parser.domain.types.TransformerClass | None = None, import_paths: List[str] = <factory>)`
:   Grammar configuration extracted from plugin.

    ### Instance variables

    `formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism`
    :

    `grammar_path: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarPath`
    :

    `import_paths: List[str]`
    :

    `parser_config: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig`
    :

    `transformer_class: src.tau_translator_omega.core_engine.parsers.parser.domain.types.TransformerClass | None`
    :

    ### Methods

    `has_transformer(self) ‑> bool`
    :   Check if transformer is configured.

`GrammarFormalism(*args, **kwds)`
:   Supported grammar formalisms.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ANTLR`
    :

    `BNF`
    :

    `EBNF`
    :

    `LARK`
    :

    `PEG`
    :

`ParseError(message: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ErrorMessage, location: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceLocation | None = None, expected_tokens: List[str] = <factory>, found_token: src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token | None = None, recovery_hint: str | None = None)`
:   Immutable parse error representation.

    ### Instance variables

    `expected_tokens: List[str]`
    :

    `found_token: src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token | None`
    :

    `location: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceLocation | None`
    :

    `message: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ErrorMessage`
    :

    `recovery_hint: str | None`
    :

    ### Methods

    `to_string(self) ‑> str`
    :   Convert error to human-readable message.

`ParseNode(node_type: src.tau_translator_omega.core_engine.parsers.parser.domain.types.NodeType, location: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceLocation | None = None)`
:   Base class for parse tree nodes.

    ### Instance variables

    `location: src.tau_translator_omega.core_engine.parsers.parser.domain.types.SourceLocation | None`
    :

    `node_type: src.tau_translator_omega.core_engine.parsers.parser.domain.types.NodeType`
    :

`ParseResult(tree: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseTree | None = None, errors: List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseError] = <factory>, warnings: List[str] = <factory>, metrics: Dict[str, Any] = <factory>)`
:   Result of parsing operation.

    ### Instance variables

    `errors: List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseError]`
    :

    `metrics: Dict[str, Any]`
    :

    `tree: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseTree | None`
    :

    `warnings: List[str]`
    :

    ### Methods

    `add_error(self, error: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseError) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseResult`
    :   Return new result with additional error.

    `add_warning(self, warning: str) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseResult`
    :   Return new result with additional warning.

    `is_success(self) ‑> bool`
    :   Check if parsing succeeded.

    `with_metrics(self, new_metrics: Dict[str, Any]) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseResult`
    :   Return new result with updated metrics.

`ParseTree(root: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, source_file: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarPath | None = None)`
:   Immutable parse tree representation.

    ### Instance variables

    `root: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode`
    :

    `source_file: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarPath | None`
    :

    ### Methods

    `accept(self, visitor: ParseTreeVisitor) ‑> returns.result.Result[typing.Any, str]`
    :   Accept a visitor for tree traversal.

`ParseTreeVisitor(*args, **kwargs)`
:   Protocol for parse tree visitors.

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Methods

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode) ‑> returns.result.Result[typing.Any, str]`
    :   Visit a parse node.

`ParserConfig(formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism, parser_type: Literal['lalr', 'earley', 'cyk'], lexer_type: Literal['contextual', 'standard', 'dynamic', 'dynamic_complete'], start_symbol: str = 'start', keep_all_tokens: bool = False, propagate_positions: bool = True, maybe_placeholders: bool = False, debug_mode: bool = False)`
:   Immutable parser configuration.

    ### Instance variables

    `debug_mode: bool`
    :

    `formalism: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarFormalism`
    :

    `keep_all_tokens: bool`
    :

    `lexer_type: Literal['contextual', 'standard', 'dynamic', 'dynamic_complete']`
    :

    `maybe_placeholders: bool`
    :

    `parser_type: Literal['lalr', 'earley', 'cyk']`
    :

    `propagate_positions: bool`
    :

    `start_symbol: str`
    :

    ### Methods

    `with_debug(self, enabled: bool) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserConfig`
    :   Return new config with debug mode set.

`ParserContext(tokens: List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token], position: int = 0, error_recovery_points: List[int] = <factory>)`
:   Immutable parsing context with lookahead support.

    ### Instance variables

    `error_recovery_points: List[int]`
    :

    `position: int`
    :

    `tokens: List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token]`
    :

    ### Methods

    `advance(self, count: int = 1) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext`
    :   Return new context with advanced position.

    `at_end(self) ‑> bool`
    :   Check if at end of tokens.

    `current_token(self) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token | None`
    :   Get current token without advancing.

    `peek(self, offset: int = 0) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token | None`
    :   Look ahead at token without consuming.

    `with_recovery_point(self) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext`
    :   Add current position as recovery point.

`ParsingMetrics(parse_time_ms: float, token_count: int, node_count: int, error_count: int, recovery_attempts: int, cache_hit: bool = False, incremental: bool = False)`
:   Metrics collected during parsing.

    ### Instance variables

    `cache_hit: bool`
    :

    `error_count: int`
    :

    `incremental: bool`
    :

    `node_count: int`
    :

    `parse_time_ms: float`
    :

    `recovery_attempts: int`
    :

    `token_count: int`
    :

    ### Methods

    `to_dict(self) ‑> Dict[str, Any]`
    :   Convert metrics to dictionary.

`RecoveryAction(*args, **kwds)`
:   Actions for error recovery.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `INSERT_TOKEN`
    :

    `RESTART_AT_STATEMENT`
    :

    `SKIP_TOKEN`
    :

    `SKIP_TO_DELIMITER`
    :

    `SYNCHRONIZE`
    :

`RecoveryResult(action: src.tau_translator_omega.core_engine.parsers.parser.domain.types.RecoveryAction, new_context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext, inserted_token: src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token | None = None, skipped_tokens: List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token] = <factory>)`
:   Result of error recovery attempt.

    ### Instance variables

    `action: src.tau_translator_omega.core_engine.parsers.parser.domain.types.RecoveryAction`
    :

    `inserted_token: src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token | None`
    :

    `new_context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext`
    :

    `skipped_tokens: List[src.tau_translator_omega.core_engine.parsers.parser.domain.types.Token]`
    :

`SourceLocation(line: int, column: int, end_line: int | None = None, end_column: int | None = None, file_path: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarPath | None = None)`
:   Represents a location in source code.

    ### Instance variables

    `column: int`
    :

    `end_column: int | None`
    :

    `end_line: int | None`
    :

    `file_path: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarPath | None`
    :

    `line: int`
    :

    ### Methods

    `to_string(self) ‑> str`
    :   Convert location to human-readable string.

`Token(type: str, value: src.tau_translator_omega.core_engine.parsers.parser.domain.types.TokenValue, line: int, column: int, end_line: int | None = None, end_column: int | None = None)`
:   Immutable token representation.

    ### Instance variables

    `column: int`
    :

    `end_column: int | None`
    :

    `end_line: int | None`
    :

    `line: int`
    :

    `type: str`
    :

    `value: src.tau_translator_omega.core_engine.parsers.parser.domain.types.TokenValue`
    :

`TransformerConfig(class_name: src.tau_translator_omega.core_engine.parsers.parser.domain.types.TransformerClass, module_path: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ModulePath, initialization_args: Dict[str, Any] = <factory>)`
:   Configuration for AST transformer.

    ### Instance variables

    `class_name: src.tau_translator_omega.core_engine.parsers.parser.domain.types.TransformerClass`
    :

    `initialization_args: Dict[str, Any]`
    :

    `module_path: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ModulePath`
    :