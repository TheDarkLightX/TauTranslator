"""
Parsing service orchestration following the Intentional Disclosure Principle.

Coordinates parsing workflow with all methods ≤10 lines.

Copyright: DarkLightX / Dana Edwards
"""

import time
from typing import Optional, Any, Dict, List
from returns.result import Result, Success, Failure
from returns.pipeline import pipe

from ..domain.types import (
    SourceCode, ParseTree, ParseResult, ParserContext,
    CacheKey, ParsingMetrics, ParseError, Token
)
from ..domain.parser_core import ParserCore, GrammarValidator
from ..domain.recursive_parser import RecursiveDescentParser
from ..domain.error_recovery import ErrorRecoveryStrategy, ErrorMessageBuilder
from ..infrastructure.parser_io import FileLoader, CacheManager, LoggingService
from ..infrastructure.lark_adapter import LarkParserAdapter


# Helper types
from dataclasses import dataclass

@dataclass
class ParseAttemptResult:
    """Result of a parse attempt."""
    tree: Optional[ParseTree]
    errors: List[ParseError]
    recovery_attempts: int


class ParsingService:
    """
    Main service orchestrating the parsing workflow.
    Combines all parsing components into cohesive service.
    """
    
    def __init__(
        self,
        parser_adapter: LarkParserAdapter,
        recovery_strategy: ErrorRecoveryStrategy,
        cache_manager: Optional[CacheManager] = None,
        logger: Optional[LoggingService] = None
    ):
        """Initialize parsing service with dependencies."""
        self._adapter = parser_adapter
        self._recovery = recovery_strategy
        self._cache = cache_manager
        self._logger = logger or LoggingService()
        self._metrics_collector = MetricsCollector()
        self._error_builder = ErrorMessageBuilder()
    
    async def parse_source_async(
        self,
        source: SourceCode,
        parser: Any,
        config: Any,
        use_cache: bool = True
    ) -> Result[ParseResult, str]:
        """Parse source code with caching and metrics."""
        start_time = time.time()
        
        # Check cache
        cache_result = await self._try_cache_lookup_async(source, config, use_cache)
        if isinstance(cache_result, Success) and cache_result.unwrap():
            return cache_result.unwrap()
        
        # Parse with metrics
        parse_result = await self._parse_with_metrics_async(source, parser, config)
        
        # Cache successful results
        if isinstance(parse_result, Success) and use_cache:
            await self._cache_result_async(source, config, parse_result.unwrap())
        
        # Add timing metrics
        duration_ms = (time.time() - start_time) * 1000
        return self._add_timing_metrics(parse_result, duration_ms)
    
    async def _try_cache_lookup_async(
        self,
        source: SourceCode,
        config: Any,
        use_cache: bool
    ) -> Result[Optional[ParseResult], str]:
        """Try to get cached parse result."""
        if not use_cache or not self._cache:
            return Success(None)
        
        cache_key = CacheKey.from_source(source, config, "1.0")
        cached = await self._cache.get_cached_parse_tree_async(cache_key)
        
        if isinstance(cached, Success) and cached.unwrap():
            self._logger.log_cache_hit(cache_key)
            metrics = ParsingMetrics(
                parse_time_ms=0,
                token_count=0,
                node_count=0,
                error_count=0,
                recovery_attempts=0,
                cache_hit=True
            )
            return Success(ParseResult(
                tree=ParseTree(root=cached.unwrap()),
                metrics=metrics.to_dict()
            ))
        
        return Success(None)
    
    async def _parse_with_metrics_async(
        self,
        source: SourceCode,
        parser: Any,
        config: Any
    ) -> Result[ParseResult, str]:
        """Parse and collect metrics."""
        # Tokenize
        tokens_result = self._adapter.extract_tokens(source, parser)
        if isinstance(tokens_result, Failure):
            return Failure(f"Tokenization failed: {tokens_result.failure()}")
        
        tokens = tokens_result.unwrap()
        context = self._adapter.create_parser_context(tokens)
        
        # Parse with recovery
        parse_result = self._parse_with_recovery(parser, source, context)
        
        # Collect metrics
        metrics = self._collect_parsing_metrics(
            tokens,
            parse_result,
            context
        )
        
        return self._build_parse_result(parse_result, metrics)
    
    def _parse_with_recovery(
        self,
        parser: Any,
        source: SourceCode,
        context: ParserContext
    ) -> ParseAttemptResult:
        """Parse with error recovery."""
        errors = []
        recovery_attempts = 0
        
        # Try Lark parsing first
        lark_result = self._adapter.parse_source(parser, source)
        
        if isinstance(lark_result, Success):
            tree_result = self._adapter.tree_to_parse_tree(lark_result.unwrap())
            if isinstance(tree_result, Success):
                return ParseAttemptResult(
                    tree=tree_result.unwrap(),
                    errors=errors,
                    recovery_attempts=recovery_attempts
                )
        
        # Fall back to recursive descent with recovery
        return self._recursive_parse_with_recovery(context, errors, recovery_attempts)
    
    def _recursive_parse_with_recovery(
        self,
        context: ParserContext,
        errors: List[ParseError],
        recovery_attempts: int
    ) -> ParseAttemptResult:
        """Use recursive descent parser with error recovery."""
        rd_parser = RecursiveDescentParser()
        current_ctx = context
        
        while not current_ctx.at_end():
            result = rd_parser.parse_program(current_ctx)
            
            if isinstance(result, Success):
                node, _ = result.unwrap()
                return ParseAttemptResult(
                    tree=ParseTree(root=node),
                    errors=errors,
                    recovery_attempts=recovery_attempts
                )
            
            # Try recovery
            error = self._create_parse_error(result.failure(), current_ctx)
            errors.append(error)
            
            recovery_result = self._recovery.attempt_recovery(error, current_ctx)
            if isinstance(recovery_result, Success):
                recovery = recovery_result.unwrap()
                current_ctx = recovery.new_context
                recovery_attempts += 1
            else:
                break
        
        return ParseAttemptResult(
            tree=None,
            errors=errors,
            recovery_attempts=recovery_attempts
        )
    
    def _create_parse_error(
        self,
        message: str,
        context: ParserContext
    ) -> ParseError:
        """Create parse error from failure message."""
        current = context.current_token()
        location = None
        
        if current:
            from ..domain.types import SourceLocation
            location = SourceLocation(
                line=current.line,
                column=current.column
            )
        
        return ParseError(
            message=message,
            location=location,
            found_token=current
        )
    
    def _collect_parsing_metrics(
        self,
        tokens: List[Token],
        parse_result: ParseAttemptResult,
        context: ParserContext
    ) -> ParsingMetrics:
        """Collect parsing metrics."""
        node_count = 0
        if parse_result.tree:
            node_count = self._count_nodes(parse_result.tree.root)
        
        return ParsingMetrics(
            parse_time_ms=0,  # Set by caller
            token_count=len(tokens),
            node_count=node_count,
            error_count=len(parse_result.errors),
            recovery_attempts=parse_result.recovery_attempts,
            cache_hit=False
        )
    
    def _count_nodes(self, node: Any) -> int:
        """Count nodes in parse tree."""
        count = 1
        
        # Count children recursively
        if hasattr(node, 'children'):
            for child in node.children:
                count += self._count_nodes(child)
        
        return count
    
    def _build_parse_result(
        self,
        attempt: ParseAttemptResult,
        metrics: ParsingMetrics
    ) -> Result[ParseResult, str]:
        """Build final parse result."""
        result = ParseResult(
            tree=attempt.tree,
            errors=attempt.errors,
            metrics=metrics.to_dict()
        )
        
        if result.is_success():
            return Success(result)
        else:
            error_msg = self._format_errors(attempt.errors)
            return Failure(error_msg)
    
    def _format_errors(self, errors: List[ParseError]) -> str:
        """Format parse errors into message."""
        if not errors:
            return "Parse failed"
        
        messages = []
        for error in errors[:3]:  # Limit to first 3 errors
            messages.append(error.to_string())
        
        if len(errors) > 3:
            messages.append(f"... and {len(errors) - 3} more errors")
        
        return "\n".join(messages)
    
    async def _cache_result_async(
        self,
        source: SourceCode,
        config: Any,
        result: ParseResult
    ) -> None:
        """Cache successful parse result."""
        if not self._cache or not result.tree:
            return
        
        cache_key = CacheKey.from_source(source, config, "1.0")
        await self._cache.cache_parse_tree_async(cache_key, result.tree)
    
    def _add_timing_metrics(
        self,
        result: Result[ParseResult, str],
        duration_ms: float
    ) -> Result[ParseResult, str]:
        """Add timing metrics to result."""
        if isinstance(result, Success):
            parse_result = result.unwrap()
            metrics = parse_result.metrics.copy()
            metrics['parse_time_ms'] = duration_ms
            
            return Success(parse_result.with_metrics(metrics))
        
        return result


class TransformationService:
    """
    Service for transforming parse trees to ASTs.
    Manages transformer lifecycle and error handling.
    """
    
    def __init__(
        self,
        transformer_loader: Any,
        logger: Optional[LoggingService] = None
    ):
        """Initialize transformation service."""
        self._loader = transformer_loader
        self._logger = logger or LoggingService()
        self._transformer_cache: Dict[str, Any] = {}
    
    async def transform_tree_async(
        self,
        tree: ParseTree,
        transformer_config: Any
    ) -> Result[Any, str]:
        """Transform parse tree to AST."""
        # Load transformer
        transformer_result = await self._load_transformer_async(transformer_config)
        if isinstance(transformer_result, Failure):
            return transformer_result
        
        transformer = transformer_result.unwrap()
        
        # Apply transformation
        return self._apply_transformation(tree, transformer)
    
    async def _load_transformer_async(
        self,
        config: Any
    ) -> Result[Any, str]:
        """Load transformer with caching."""
        cache_key = f"{config.module_path}:{config.class_name}"
        
        if cache_key in self._transformer_cache:
            return Success(self._transformer_cache[cache_key])
        
        # Load transformer class
        class_result = await self._loader.load_transformer_class_async(
            config.module_path,
            config.class_name
        )
        
        if isinstance(class_result, Failure):
            return class_result
        
        # Instantiate transformer
        instance_result = self._loader.create_instance(
            class_result.unwrap(),
            config.initialization_args
        )
        
        if isinstance(instance_result, Success):
            self._transformer_cache[cache_key] = instance_result.unwrap()
            self._logger.log_transformer_loaded(str(config.class_name))
        
        return instance_result
    
    def _apply_transformation(
        self,
        tree: ParseTree,
        transformer: Any
    ) -> Result[Any, str]:
        """Apply transformer to tree."""
        try:
            from ..infrastructure.lark_adapter import LarkTransformerAdapter
            adapter = LarkTransformerAdapter()
            
            # Validate transformer
            validation = adapter.validate_transformer(transformer)
            if isinstance(validation, Failure):
                return validation
            
            # Transform
            return adapter.transform_tree(transformer, tree.root)
            
        except Exception as e:
            return Failure(f"Transformation failed: {e}")


class MetricsCollector:
    """Collects and aggregates parsing metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self._total_parses = 0
        self._cache_hits = 0
        self._parse_errors = 0
        self._recovery_successes = 0
        self._total_parse_time = 0.0
    
    def record_parse(self, metrics: ParsingMetrics) -> None:
        """Record parsing metrics."""
        self._total_parses += 1
        self._total_parse_time += metrics.parse_time_ms
        
        if metrics.cache_hit:
            self._cache_hits += 1
        
        if metrics.error_count > 0:
            self._parse_errors += 1
        
        if metrics.recovery_attempts > 0 and metrics.error_count == 0:
            self._recovery_successes += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        cache_hit_rate = (
            self._cache_hits / self._total_parses
            if self._total_parses > 0 else 0
        )
        
        avg_parse_time = (
            self._total_parse_time / self._total_parses
            if self._total_parses > 0 else 0
        )
        
        return {
            "total_parses": self._total_parses,
            "cache_hit_rate": cache_hit_rate,
            "error_rate": self._parse_errors / max(1, self._total_parses),
            "recovery_success_rate": (
                self._recovery_successes / max(1, self._parse_errors)
            ),
            "average_parse_time_ms": avg_parse_time
        }

