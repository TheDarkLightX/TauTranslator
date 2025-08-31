"""
Refactored grammar translator following the Intentional Disclosure Principle.

This module orchestrates grammar translation operations using the clean architecture layers:
- Domain: GrammarService (business logic)
- Infrastructure: GrammarInfrastructure (I/O operations)
- All methods follow IDP Rule 2 (≤10 lines).

Copyright: DarkLightX / Dana Edwards
"""

import time
from typing import Dict, Any, Optional
from ..core.result_enhanced import Result, Success, Failure

from ..domain.grammar_service import GrammarService, TranslationResultBuilder
from ..domain.grammar_types import (
    GrammarPath, GrammarType, GrammarName, TranslationMetadata,
    ParseError, ParseTreeInfo
)


class GrammarTranslatorRefactored:
    """Orchestrates grammar-based translation operations."""
    
    def __init__(self, grammar_dir: Optional[str] = None):
        self._service = GrammarService(grammar_dir)
        self._initialized = False
    
    async def initialize_async(self) -> Result[Dict[str, Any]]:
        """Initialize the translator with default TCE grammar."""
        result = await self._service.initialize_default_tce_async()
        if isinstance(result, Success):
            self._initialized = True
            return Success({"status": "initialized", "grammar": "TCE (default)"})
        
        return Failure(result.failure())
    
    async def load_tau_grammar_async(self, grammar_path: str) -> Result[Dict[str, Any]]:
        """Load Tau grammar from file path."""
        result = await self._service.load_tau_grammar_async(GrammarPath(grammar_path))
        if isinstance(result, Success):
            load_result = result.unwrap()
            return Success(self._format_load_response(load_result))
        
        return Failure(result.failure())
    
    async def load_cnl_grammar_async(self, grammar_path: str, transformer_class=None) -> Result[Dict[str, Any]]:
        """Load CNL grammar from file path with optional transformer."""
        result = await self._service.load_cnl_grammar_async(
            GrammarPath(grammar_path), 
            transformer_class
        )
        if isinstance(result, Success):
            load_result = result.unwrap()
            return Success(self._format_load_response(load_result))
        
        return Failure(result.failure())
    
    async def translate_async(self, text: str, direction: str) -> Dict[str, Any]:
        """Main translation method with comprehensive error handling."""
        start_time = time.time()
        
        if not self._initialized:
            return self._create_error_response(
                text, direction, "Translator not initialized", start_time
            )
        
        if direction == "cnl_to_tau":
            return await self._translate_cnl_to_tau_async(text, start_time)
        elif direction == "tau_to_cnl":
            return await self._translate_tau_to_cnl_async(text, start_time)
        else:
            return self._create_unsupported_response(
                text, direction, start_time, f"Unknown direction: {direction}"
            )
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get current engine state and capabilities."""
        state = self._service.get_engine_state()
        return {
            "engine_type": "grammar_translator",
            "initialized": self._initialized,
            **state.to_info_dict()
        }
    
    def can_translate(self, direction: str) -> bool:
        """Check if translation direction is supported."""
        if direction == "cnl_to_tau":
            return self._service.can_translate_to_tau()
        elif direction == "tau_to_cnl":
            return self._service.can_translate_to_cnl()
        return False
    
    def set_custom_transformer(self, transformer_class, target: str) -> Result[None]:
        """Set custom transformer for CNL or Tau operations."""
        if target == "cnl":
            return self._service.set_custom_cnl_transformer(transformer_class)
        elif target == "tau":
            return self._service.set_custom_tau_transformer(transformer_class)
        else:
            return Failure(f"Unknown transformer target: {target}")
    
    # Private helper methods (all ≤10 lines following IDP Rule 2)
    
    async def _translate_cnl_to_tau_async(self, text: str, start_time: float) -> Dict[str, Any]:
        """Translate CNL text to Tau with metadata extraction."""
        result = await self._service.parse_and_transform_to_tau_async(text)
        
        if isinstance(result, Success):
            translated_text = result.unwrap()
            metadata = await self._extract_translation_metadata(translated_text)
            
            return TranslationResultBuilder.create_successful_result(
                text, translated_text, "cnl_to_tau", start_time, metadata
            )
        else:
            error = result.failure()
            return TranslationResultBuilder.create_error_result(
                text, "cnl_to_tau", error, start_time
            )
    
    async def _translate_tau_to_cnl_async(self, text: str, start_time: float) -> Dict[str, Any]:
        """Translate Tau text to CNL with metadata extraction."""
        result = await self._service.parse_and_transform_to_cnl_async(text)
        
        if isinstance(result, Success):
            translated_text = result.unwrap()
            metadata = await self._extract_translation_metadata(translated_text)
            
            return TranslationResultBuilder.create_successful_result(
                text, translated_text, "tau_to_cnl", start_time, metadata
            )
        else:
            error = result.failure()
            return TranslationResultBuilder.create_error_result(
                text, "tau_to_cnl", error, start_time
            )
    
    async def _extract_translation_metadata(self, translated_text: str) -> TranslationMetadata:
        """Extract metadata from translation results."""
        # For grammar translation, we have high confidence
        return TranslationMetadata(
            engine_type="grammar_parser",
            parser_type="lark",
            confidence=0.95
        )
    
    def _format_load_response(self, load_result) -> Dict[str, Any]:
        """Format grammar load result for API response."""
        return {
            "success": load_result.success,
            "grammar_type": load_result.grammar_type.value,
            "grammar_name": str(load_result.grammar_name),
            "parser_created": load_result.parser_created,
            "transformer_created": load_result.transformer_created
        }
    
    def _create_error_response(self, text: str, direction: str, error: str, start_time: float) -> Dict[str, Any]:
        """Create error response for translation failures."""
        parse_error = ParseError(error)
        return TranslationResultBuilder.create_error_result(
            text, direction, parse_error, start_time
        )
    
    def _create_unsupported_response(self, text: str, direction: str, start_time: float, reason: str) -> Dict[str, Any]:
        """Create response for unsupported translation requests."""
        return TranslationResultBuilder.create_unsupported_result(
            text, direction, start_time, reason
        )


class GrammarTranslatorFactory:
    """Factory for creating grammar translator instances."""
    
    @staticmethod
    def create_translator(grammar_dir: Optional[str] = None) -> GrammarTranslatorRefactored:
        """Create a new grammar translator instance."""
        return GrammarTranslatorRefactored(grammar_dir)
    
    @staticmethod
    async def create_initialized_translator_async(grammar_dir: Optional[str] = None) -> Result[GrammarTranslatorRefactored]:
        """Create and initialize a grammar translator."""
        translator = GrammarTranslatorFactory.create_translator(grammar_dir)
        
        init_result = await translator.initialize_async()
        if isinstance(init_result, Success):
            return Success(translator)
        else:
            return Failure(init_result.failure())


class LegacyGrammarTranslatorAdapter:
    """Adapter to maintain compatibility with existing code."""
    
    def __init__(self, refactored_translator: GrammarTranslatorRefactored):
        self._translator = refactored_translator
    
    async def translate(self, text: str, direction: str) -> Dict[str, Any]:
        """Legacy translate method signature."""
        return await self._translator.translate_async(text, direction)
    
    def load_tau_grammar(self, grammar_path: str) -> Dict[str, Any]:
        """Legacy synchronous grammar loading (deprecated)."""
        import asyncio
        result = asyncio.run(self._translator.load_tau_grammar_async(grammar_path))
        
        if isinstance(result, Success):
            return result.unwrap()
        else:
            return {"success": False, "error": result.failure()}
    
    def load_cnl_grammar(self, grammar_path: str, transformer_class=None) -> Dict[str, Any]:
        """Legacy synchronous CNL grammar loading (deprecated)."""
        import asyncio
        result = asyncio.run(self._translator.load_cnl_grammar_async(grammar_path, transformer_class))
        
        if isinstance(result, Success):
            return result.unwrap()
        else:
            return {"success": False, "error": result.failure()}
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information (passthrough)."""
        return self._translator.get_engine_info()