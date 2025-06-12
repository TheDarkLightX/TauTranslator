"""
Grammar translation service with pure business logic following the Intentional Disclosure Principle.

Contains all grammar translation business logic separated from infrastructure concerns.
All methods follow IDP Rule 2 (≤10 lines) and Rule 3 (type disclosure).

Copyright: DarkLightX / Dana Edwards
"""

import time
from typing import List, Optional, Dict, Any
from ..core.result_enhanced import Result, Success, Failure

from .grammar_types import (
    GrammarPath, GrammarType, GrammarLoadResult, GrammarEngineState,
    GrammarName, TranslationMetadata, ParseTreeInfo, ParseError,
    ParserConfiguration, TransformerConfiguration, GrammarDirectoryConfig
)
from ..infrastructure.grammar_infrastructure import (
    GrammarFileLoader, LarkParserFactory, TransformerFactory,
    GrammarDirectoryResolver, ParseTreeAnalyzer, ParseErrorHandler
)

class GrammarService:
    """Pure business logic for grammar translation operations."""
    
    def __init__(self, grammar_dir: Optional[str] = None):
        self._directory_config = GrammarDirectoryConfig(
            directory_path=grammar_dir,
            environment_variable="TAU_GRAMMAR_DIR",
            default_path="./grammars"
        )
        self._directory_resolver = GrammarDirectoryResolver(self._directory_config)
        self._state = self._initialize_state()
        
        # Parser and transformer instances (managed by infrastructure)
        self._cnl_parser = None
        self._tau_parser = None
        self._cnl_transformer = None
        self._tau_transformer = None
    
    def _initialize_state(self) -> GrammarEngineState:
        """Initialize engine state with default values."""
        return GrammarEngineState(
            cnl_grammar_loaded=False,
            tau_grammar_loaded=False,
            cnl_grammar_name=GrammarName(""),
            tau_grammar_name=None,
            default_tce_available=False
        )
    
    async def initialize_default_tce_async(self) -> Result[GrammarLoadResult]:
        """Initialize default TCE parser and transformer."""
        grammar_result = GrammarFileLoader.load_default_tce_grammar()
        if isinstance(grammar_result, Failure):
            return Failure(grammar_result.failure())
        
        config = ParserConfiguration(grammar_content=grammar_result.unwrap())
        parser_result = LarkParserFactory.create_parser(config)
        if isinstance(parser_result, Failure):
            return Failure(parser_result.failure())
        
        transformer_result = TransformerFactory.create_default_tce_transformer()
        if isinstance(transformer_result, Failure):
            return Failure(transformer_result.failure())
        
        self._cnl_parser = parser_result.unwrap()
        self._cnl_transformer = transformer_result.unwrap()
        
        self._state = GrammarEngineState(
            cnl_grammar_loaded=True,
            tau_grammar_loaded=False,
            cnl_grammar_name=GrammarName("TCE (default)"),
            tau_grammar_name=None,
            default_tce_available=True
        )
        
        return Success(GrammarLoadResult.success_result(GrammarType.TCE, "TCE (default)"))
    
    async def load_tau_grammar_async(self, grammar_path: GrammarPath) -> Result[GrammarLoadResult]:
        """Load Tau grammar from file path."""
        grammar_result = GrammarFileLoader.load_grammar_content(grammar_path)
        if isinstance(grammar_result, Failure):
            return Success(GrammarLoadResult.failure_result(GrammarType.TAU, grammar_result.failure()))
        
        config = ParserConfiguration(grammar_content=grammar_result.unwrap())
        parser_result = LarkParserFactory.create_parser(config)
        if isinstance(parser_result, Failure):
            return Success(GrammarLoadResult.failure_result(GrammarType.TAU, parser_result.failure()))
        
        transformer_result = TransformerFactory.create_default_tau_transformer()
        if isinstance(transformer_result, Failure):
            return Success(GrammarLoadResult.failure_result(GrammarType.TAU, transformer_result.failure()))
        
        self._tau_parser = parser_result.unwrap()
        self._tau_transformer = transformer_result.unwrap()
        
        # Update state with new Tau grammar
        self._state = GrammarEngineState(
            cnl_grammar_loaded=self._state.cnl_grammar_loaded,
            tau_grammar_loaded=True,
            cnl_grammar_name=self._state.cnl_grammar_name,
            tau_grammar_name=GrammarName(self._extract_grammar_name(grammar_path)),
            default_tce_available=self._state.default_tce_available
        )
        
        return Success(GrammarLoadResult.success_result(GrammarType.TAU, str(self._state.tau_grammar_name)))
    
    async def load_cnl_grammar_async(self, grammar_path: GrammarPath, transformer_class=None) -> Result[GrammarLoadResult]:
        """Load CNL grammar from file path with optional custom transformer."""
        grammar_result = GrammarFileLoader.load_grammar_content(grammar_path)
        if isinstance(grammar_result, Failure):
            return Success(GrammarLoadResult.failure_result(GrammarType.CNL, grammar_result.failure()))
        
        config = ParserConfiguration(grammar_content=grammar_result.unwrap())
        parser_result = LarkParserFactory.create_parser(config)
        if isinstance(parser_result, Failure):
            return Success(GrammarLoadResult.failure_result(GrammarType.CNL, parser_result.failure()))
        
        # Create transformer (custom or default)
        transformer_result = await self._create_cnl_transformer(transformer_class)
        if isinstance(transformer_result, Failure):
            return Success(GrammarLoadResult.failure_result(GrammarType.CNL, transformer_result.failure()))
        
        self._cnl_parser = parser_result.unwrap()
        self._cnl_transformer = transformer_result.unwrap()
        
        # Update state with new CNL grammar
        self._state = GrammarEngineState(
            cnl_grammar_loaded=True,
            tau_grammar_loaded=self._state.tau_grammar_loaded,
            cnl_grammar_name=GrammarName(self._extract_grammar_name(grammar_path)),
            tau_grammar_name=self._state.tau_grammar_name,
            default_tce_available=False  # No longer using default
        )
        
        return Success(GrammarLoadResult.success_result(GrammarType.CNL, str(self._state.cnl_grammar_name)))
    
    def get_engine_state(self) -> GrammarEngineState:
        """Get current engine state."""
        return self._state
    
    def can_translate_to_tau(self) -> bool:
        """Check if engine can translate to Tau."""
        return self._state.can_translate_to_tau
    
    def can_translate_to_cnl(self) -> bool:
        """Check if engine can translate to CNL."""
        return self._state.can_translate_to_cnl
    
    async def parse_and_transform_to_tau_async(self, cnl_text: str) -> Result[str]:
        """Parse CNL text and transform to Tau."""
        if not self._cnl_parser or not self._cnl_transformer:
            return Failure(ParseError("CNL parser not available"))
        
        try:
            parse_tree = self._cnl_parser.parse(cnl_text)
            tau_output = self._cnl_transformer.transform(parse_tree)
            return Success(str(tau_output))
            
        except Exception as e:
            return Failure(ParseError.from_lark_exception(e))
    
    async def parse_and_transform_to_cnl_async(self, tau_text: str) -> Result[str]:
        """Parse Tau text and transform to CNL."""
        if not self._tau_parser or not self._tau_transformer:
            return Failure(ParseError("Tau parser not available"))
        
        try:
            parse_tree = self._tau_parser.parse(tau_text)
            cnl_output = self._tau_transformer.transform(parse_tree)
            return Success(str(cnl_output))
            
        except Exception as e:
            return Failure(ParseError.from_lark_exception(e))
    
    async def extract_parse_metadata_async(self, parse_tree: Any) -> ParseTreeInfo:
        """Extract metadata from parse tree."""
        patterns_result = ParseTreeAnalyzer.extract_patterns(parse_tree)
        
        if isinstance(patterns_result, Success):
            return ParseTreeInfo.from_patterns(patterns_result.unwrap())
        else:
            return ParseTreeInfo.from_patterns([])
    
    def set_custom_tau_transformer(self, transformer_class) -> Result[None]:
        """Set custom transformer for Tau operations."""
        if not self._tau_parser:
            return Failure("Cannot set transformer - Tau grammar not loaded")
        
        try:
            self._tau_transformer = transformer_class()
            return Success(None)
        except Exception as e:
            return Failure(f"Failed to set custom transformer: {e}")
    
    def set_custom_cnl_transformer(self, transformer_class) -> Result[None]:
        """Set custom transformer for CNL operations."""
        if not self._cnl_parser:
            return Failure("Cannot set transformer - CNL grammar not loaded")
        
        try:
            self._cnl_transformer = transformer_class()
            return Success(None)
        except Exception as e:
            return Failure(f"Failed to set custom transformer: {e}")
    
    # Private helper methods (all ≤10 lines following IDP Rule 2)
    
    def _extract_grammar_name(self, grammar_path: GrammarPath) -> str:
        """Extract grammar name from file path."""
        from pathlib import Path
        return Path(grammar_path).stem
    
    async def _create_cnl_transformer(self, transformer_class=None) -> Result[Any]:
        """Create CNL transformer (custom or default)."""
        if transformer_class:
            try:
                transformer = transformer_class()
                return Success(transformer)
            except Exception as e:
                return Failure(f"Failed to create custom transformer: {e}")
        
        return TransformerFactory.create_default_tce_transformer()

class TranslationResultBuilder:
    """Builds translation results with proper metadata."""
    
    @staticmethod
    def create_successful_result(
        original_text: str,
        translated_text: str,
        direction: str,
        start_time: float,
        metadata: Optional[TranslationMetadata] = None
    ) -> Dict[str, Any]:
        """Create successful translation result."""
        base_result = {
            "success": True,
            "translated_text": translated_text,
            "original_text": original_text,
            "direction": direction,
            "processing_time": time.time() - start_time,
            "confidence": 0.95  # Grammar parsing is high confidence
        }
        
        if metadata:
            base_result["metadata"] = metadata.to_dict()
        
        return base_result
    
    @staticmethod
    def create_error_result(
        original_text: str,
        direction: str,
        error: ParseError,
        start_time: float
    ) -> Dict[str, Any]:
        """Create error translation result."""
        return {
            "success": False,
            "translated_text": "",
            "original_text": original_text,
            "direction": direction,
            "processing_time": time.time() - start_time,
            "error_message": error.message,
            "metadata": error.to_metadata_dict()
        }
    
    @staticmethod
    def create_unsupported_result(
        original_text: str,
        direction: str,
        start_time: float,
        reason: str
    ) -> Dict[str, Any]:
        """Create result for unsupported translation."""
        return {
            "success": False,
            "translated_text": "",
            "original_text": original_text,
            "direction": direction,
            "processing_time": time.time() - start_time,
            "error_message": f"Translation not supported: {reason}",
            "metadata": {"unsupported": True, "reason": reason}
        }