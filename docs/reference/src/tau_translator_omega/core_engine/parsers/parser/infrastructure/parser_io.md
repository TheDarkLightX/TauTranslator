Module src.tau_translator_omega.core_engine.parsers.parser.infrastructure.parser_io
===================================================================================
Parser I/O infrastructure following the Intentional Disclosure Principle.

All I/O operations are isolated here, with explicit async naming
and complete error handling.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`CacheManager(cache_dir: pathlib.Path | None = None)`
:   Manages parser cache for memoization.
    
    Initialize cache manager.

    ### Methods

    `cache_parse_tree_async(self, key: src.tau_translator_omega.core_engine.parsers.parser.domain.types.CacheKey, tree: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseTree) ‑> returns.result.Result[None, str]`
    :   Cache parse tree for future use.

    `clear_cache(self) ‑> returns.result.Result[int, str]`
    :   Clear all cached entries.

    `get_cached_parse_tree_async(self, key: src.tau_translator_omega.core_engine.parsers.parser.domain.types.CacheKey) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseTree | None, str]`
    :   Retrieve cached parse tree if available.

`FileLoader()`
:   Handles all file I/O operations.

    ### Methods

    `compute_file_hash(self, content: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarContent) ‑> str`
    :   Compute hash of file content for caching.

    `load_grammar_file_async(self, path: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarPath) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarContent, str]`
    :   Load grammar file with explicit async I/O.

    `resolve_import_paths(self, base_path: src.tau_translator_omega.core_engine.parsers.parser.domain.types.GrammarPath, imports: List[str]) ‑> List[pathlib.Path]`
    :   Resolve import paths relative to grammar file.

`LoggingService(logger_name: str = 'parser')`
:   Centralized logging service for parser.
    
    Initialize logging service.

    ### Methods

    `log_cache_hit(self, key: src.tau_translator_omega.core_engine.parsers.parser.domain.types.CacheKey) ‑> None`
    :   Log cache hit.

    `log_debug(self, message: str, **kwargs) ‑> None`
    :   Log debug message.

    `log_error(self, message: str, error: Exception | None = None, **kwargs) ‑> None`
    :   Log error message.

    `log_info(self, message: str, **kwargs) ‑> None`
    :   Log info message.

    `log_parse_attempt(self, source_length: int, grammar_path: str) ‑> None`
    :   Log parse attempt.

    `log_parse_failure(self, error: str, location: str | None = None) ‑> None`
    :   Log parse failure.

    `log_parse_success(self, duration_ms: float, node_count: int) ‑> None`
    :   Log successful parse.

    `log_transformer_loaded(self, class_name: str) ‑> None`
    :   Log transformer loaded.

    `log_warning(self, message: str, **kwargs) ‑> None`
    :   Log warning message.

`ModuleLoader()`
:   Handles dynamic module loading.

    ### Methods

    `create_instance(self, cls: Type, args: Dict[str, Any] = None) ‑> returns.result.Result[typing.Any, str]`
    :   Create instance of loaded class.

    `load_transformer_class_async(self, module_path: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ModulePath, class_name: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ClassName) ‑> returns.result.Result[typing.Type, str]`
    :   Dynamically load transformer class.

`PathResolver(project_root: pathlib.Path | None = None)`
:   Resolves paths relative to project structure.
    
    Initialize with project root.

    ### Methods

    `get_common_grammars_dir(self) ‑> pathlib.Path`
    :   Get directory for common grammar imports.

    `resolve_grammar_path(self, path: str) ‑> pathlib.Path`
    :   Resolve grammar path relative to project.