"""
Parsing strategy pattern implementation following the Intentional Disclosure Principle.

Provides different parsing strategies for various grammar formalisms.

Copyright: DarkLightX / Dana Edwards
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from pathlib import Path
from returns.result import Result, Success, Failure

from ..domain.types import (
    GrammarContent, ParserConfig, SourceCode, ParseTree,
    ParseResult, GrammarFormalism
)
from ..infrastructure.parser_io import FileLoader, ModuleLoader, LoggingService
from ..infrastructure.lark_adapter import LarkParserAdapter, GrammarImportResolver
from ..services.parsing_service import ParsingService


class ParsingStrategy(ABC):
    """
    Abstract base class for parsing strategies.
    Each strategy handles a specific grammar formalism.
    """
    
    @abstractmethod
    async def create_parser_async(
        self,
        grammar: GrammarContent,
        config: ParserConfig,
        import_paths: List[Path]
    ) -> Result[Any, str]:
        """Create parser instance for the strategy."""
        pass
    
    @abstractmethod
    async def parse_source_async(
        self,
        parser: Any,
        source: SourceCode,
        config: ParserConfig
    ) -> Result[ParseResult, str]:
        """Parse source code using the strategy."""
        pass
    
    @abstractmethod
    def supports_formalism(self, formalism: GrammarFormalism) -> bool:
        """Check if strategy supports given formalism."""
        pass
    
    def get_strategy_name(self) -> str:
        """Get strategy name for logging."""
        return self.__class__.__name__


class LarkParsingStrategy(ParsingStrategy):
    """
    Parsing strategy for Lark grammars.
    Supports LALR, Earley, and CYK parsing algorithms.
    """
    
    def __init__(
        self,
        logger: Optional[LoggingService] = None,
        cache_manager: Optional[Any] = None
    ):
        """Initialize Lark parsing strategy."""
        self._adapter = LarkParserAdapter()
        self._import_resolver = GrammarImportResolver()
        self._logger = logger or LoggingService()
        self._cache_manager = cache_manager
        self._parsing_service = None
    
    async def create_parser_async(
        self,
        grammar: GrammarContent,
        config: ParserConfig,
        import_paths: List[Path]
    ) -> Result[Any, str]:
        """Create Lark parser instance."""
        # Resolve imports
        imports_result = self._resolve_grammar_imports(grammar, import_paths)
        if isinstance(imports_result, Failure):
            return imports_result
        
        all_import_paths = imports_result.unwrap()
        
        # Create parser
        parser_result = self._adapter.create_parser(
            grammar,
            config,
            all_import_paths
        )
        
        if isinstance(parser_result, Success):
            self._logger.log_info(
                "Lark parser created successfully",
                parser_type=config.parser_type,
                start_symbol=config.start_symbol
            )
        
        return parser_result
    
    async def parse_source_async(
        self,
        parser: Any,
        source: SourceCode,
        config: ParserConfig
    ) -> Result[ParseResult, str]:
        """Parse source using Lark."""
        # Initialize parsing service if needed
        if not self._parsing_service:
            from ..domain.error_recovery import TauSpecificRecovery
            self._parsing_service = ParsingService(
                parser_adapter=self._adapter,
                recovery_strategy=TauSpecificRecovery(),
                cache_manager=self._cache_manager,
                logger=self._logger
            )
        
        # Parse with service
        return await self._parsing_service.parse_source_async(
            source,
            parser,
            config,
            use_cache=True
        )
    
    def supports_formalism(self, formalism: GrammarFormalism) -> bool:
        """Check if Lark supports formalism."""
        return formalism in [
            GrammarFormalism.LARK,
            GrammarFormalism.EBNF,
            GrammarFormalism.BNF
        ]
    
    def _resolve_grammar_imports(
        self,
        grammar: GrammarContent,
        base_paths: List[Path]
    ) -> Result[List[Path], str]:
        """Resolve all grammar imports."""
        all_paths = base_paths.copy()
        
        # Extract imports from grammar
        for base_path in base_paths:
            imports_result = self._import_resolver.resolve_imports(
                str(grammar),
                base_path
            )
            
            if isinstance(imports_result, Success):
                all_paths.extend(imports_result.unwrap())
        
        return Success(all_paths)


class EbnfParsingStrategy(LarkParsingStrategy):
    """
    Parsing strategy for EBNF grammars.
    Converts EBNF to Lark format and uses Lark parser.
    """
    
    async def create_parser_async(
        self,
        grammar: GrammarContent,
        config: ParserConfig,
        import_paths: List[Path]
    ) -> Result[Any, str]:
        """Create parser for EBNF grammar."""
        # Convert EBNF to Lark format
        converted_result = self._convert_ebnf_to_lark(grammar)
        if isinstance(converted_result, Failure):
            return converted_result
        
        converted_grammar = converted_result.unwrap()
        
        # Use parent class to create Lark parser
        return await super().create_parser_async(
            converted_grammar,
            config,
            import_paths
        )
    
    def _convert_ebnf_to_lark(self, grammar: GrammarContent) -> Result[GrammarContent, str]:
        """Convert EBNF grammar to Lark format."""
        try:
            content = str(grammar)
            
            # Basic EBNF to Lark conversions
            conversions = [
                ("::=", ":"),  # Rule definition
                ("{", "("),    # Repetition start
                ("}", ")*"),   # Repetition end
                ("[", "("),    # Optional start
                ("]", ")?"),   # Optional end
            ]
            
            for old, new in conversions:
                content = content.replace(old, new)
            
            # Remove semicolons at end of rules
            import re
            content = re.sub(r';\s*\n', '\n', content)
            
            return Success(GrammarContent(content))
            
        except Exception as e:
            return Failure(f"Failed to convert EBNF to Lark: {e}")
    
    def supports_formalism(self, formalism: GrammarFormalism) -> bool:
        """EBNF strategy only supports EBNF."""
        return formalism == GrammarFormalism.EBNF


class PegParsingStrategy(ParsingStrategy):
    """
    Parsing strategy for PEG (Parsing Expression Grammar).
    Placeholder for future PEG parser implementation.
    """
    
    async def create_parser_async(
        self,
        grammar: GrammarContent,
        config: ParserConfig,
        import_paths: List[Path]
    ) -> Result[Any, str]:
        """Create PEG parser (not implemented)."""
        return Failure("PEG parsing not yet implemented")
    
    async def parse_source_async(
        self,
        parser: Any,
        source: SourceCode,
        config: ParserConfig
    ) -> Result[ParseResult, str]:
        """Parse using PEG (not implemented)."""
        return Failure("PEG parsing not yet implemented")
    
    def supports_formalism(self, formalism: GrammarFormalism) -> bool:
        """Check if PEG is supported."""
        return formalism == GrammarFormalism.PEG


class FallbackParsingStrategy(ParsingStrategy):
    """
    Fallback strategy for unsupported grammar formalisms.
    Provides helpful error messages.
    """
    
    def __init__(self, supported_strategies: List[ParsingStrategy]):
        """Initialize with list of supported strategies."""
        self._supported = supported_strategies
    
    async def create_parser_async(
        self,
        grammar: GrammarContent,
        config: ParserConfig,
        import_paths: List[Path]
    ) -> Result[Any, str]:
        """Report unsupported formalism."""
        supported_names = [
            s.get_strategy_name() for s in self._supported
        ]
        
        return Failure(
            f"No parsing strategy available for {config.formalism.value}. "
            f"Supported strategies: {', '.join(supported_names)}"
        )
    
    async def parse_source_async(
        self,
        parser: Any,
        source: SourceCode,
        config: ParserConfig
    ) -> Result[ParseResult, str]:
        """Cannot parse with fallback."""
        return Failure("No parser available")
    
    def supports_formalism(self, formalism: GrammarFormalism) -> bool:
        """Fallback supports nothing."""
        return False


class StrategySelector:
    """
    Selects appropriate parsing strategy based on grammar formalism.
    Implements strategy pattern for parser selection.
    """
    
    def __init__(self, logger: Optional[LoggingService] = None):
        """Initialize strategy selector."""
        self._logger = logger or LoggingService()
        self._strategies = self._initialize_strategies()
    
    def _initialize_strategies(self) -> Dict[GrammarFormalism, ParsingStrategy]:
        """Initialize available strategies."""
        lark_strategy = LarkParsingStrategy(logger=self._logger)
        ebnf_strategy = EbnfParsingStrategy(logger=self._logger)
        peg_strategy = PegParsingStrategy()
        
        return {
            GrammarFormalism.LARK: lark_strategy,
            GrammarFormalism.EBNF: ebnf_strategy,
            GrammarFormalism.BNF: lark_strategy,  # BNF uses Lark
            GrammarFormalism.PEG: peg_strategy,
            GrammarFormalism.ANTLR: FallbackParsingStrategy([
                lark_strategy, ebnf_strategy, peg_strategy
            ])
        }
    
    def select_strategy(self, formalism: GrammarFormalism) -> ParsingStrategy:
        """Select parsing strategy for formalism."""
        strategy = self._strategies.get(formalism)
        
        if strategy:
            self._logger.log_info(
                "Selected parsing strategy",
                formalism=formalism.value,
                strategy=strategy.get_strategy_name()
            )
            return strategy
        
        # Return fallback for unknown formalisms
        self._logger.log_warning(
            "No strategy for formalism, using fallback",
            formalism=formalism.value
        )
        
        return FallbackParsingStrategy(list(self._strategies.values()))
    
    def get_supported_formalisms(self) -> List[GrammarFormalism]:
        """Get list of supported formalisms."""
        return [
            formalism for formalism, strategy in self._strategies.items()
            if not isinstance(strategy, FallbackParsingStrategy)
        ]