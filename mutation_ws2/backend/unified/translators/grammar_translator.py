"""
Grammar-aware translation engine.

Integrates Lark parser-based translation for TCE ↔ Tau conversion.
Users must provide their own grammar files for Tau language.

Author: DarkLightX / Dana Edwards
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

# Correctly import Lark and the new transformer
import asyncio
from lark import Lark, Tree, Token, Transformer, exceptions as lark_exceptions
from returns.result import Result, Success, Failure
from returns.pipeline import is_successful

from .base import TranslationEngine, TranslationResult, TranslationDirection, CachingEngine
from backend.unified.core.domain_types import AppError, SourceText
from backend.unified.core.dependency_injection import ServiceContainer
from backend.unified.enhanced_tce_transformer import EnhancedTCETransformer



logger = logging.getLogger(__name__)


class GrammarTranslationEngine(CachingEngine):
    """Grammar-aware translation engine using Lark parser."""

    def __init__(self, grammar_dir: Optional[str] = None, grammar_content: Optional[str] = None, grammar_name: Optional[str] = None, service_provider: Optional[ServiceContainer] = None):
        super().__init__(
            name="grammar_aware",
            description="Grammar-driven translation with Lark parser",
            cache_size=100
        )

        self.grammar_dir = grammar_dir or os.environ.get('TAU_GRAMMAR_DIR', './grammars')
        self.cnl_parser: Optional[Lark] = None
        self.tau_parser: Optional[Lark] = None
        self.cnl_transformer: Optional[Transformer] = None
        self.tau_transformer: Optional[Transformer] = None
        
        # The concept of a separate "TCE" parser is deprecated. The engine handles "CNL" and "Tau".
        # The default controlled language is handled by the caller providing a grammar.
        self.service_provider = service_provider

        # Track which grammars are loaded
        self.cnl_grammar_loaded = False
        self.tau_grammar_loaded = False
        self.cnl_grammar_name: Optional[str] = None
        self.tau_grammar_name: Optional[str] = None
        
        self.is_available = False
        self.last_error: Optional[str] = None

        if grammar_content and grammar_name:
            logger.info(f"Initializing GrammarTranslationEngine with provided grammar_content for '{grammar_name}'")
            # The test provides a CNL grammar.
            self._initialize_parser_from_content(grammar_content, grammar_type="cnl", grammar_name=grammar_name)
        else:
            logger.warning("GrammarTranslationEngine initialized without grammar content. Engine will not be available.")
            self.is_available = False
            self.last_error = "No grammar provided on initialization."

    def _initialize_parser_from_content(self, content: str, grammar_type: str, grammar_name: str) -> bool:
        """Initialize a parser (CNL or Tau) from a grammar string content."""
        try:
            parser = Lark(
                content,
                parser='lalr',
                start='start',
                propagate_positions=True
            )

            if grammar_type == "cnl":
                self.cnl_parser = parser
                self.cnl_transformer = EnhancedTCETransformer()  # Use the new transformer
                self.cnl_grammar_loaded = True
                self.cnl_grammar_name = grammar_name
                logger.info(f"CNL parser initialized successfully from content: {grammar_name}")
            elif grammar_type == "tau":
                self.tau_parser = parser
                self.tau_transformer = Transformer()  # Use placeholder for reverse
                self.tau_grammar_loaded = True
                self.tau_grammar_name = grammar_name
                logger.info(f"Tau parser initialized successfully from content: {grammar_name}")
            else:
                logger.error(f"Unknown grammar_type '{grammar_type}' for _initialize_parser_from_content")
                return False

            self.is_available = True  # Mark engine as available
            return True

        except ImportError as ie:
            logger.error(f"Failed to import Lark or transformers for parser initialization from content: {ie}")
            self.last_error = f"Import error: {ie}"
            self.is_available = False
            return False
        except Exception as e:
            logger.error(f"Failed to initialize parser from content ({grammar_name}): {e}")
            self.last_error = f"Parser init from content failed: {e}"
            if grammar_type == "cnl":
                self.cnl_parser = None
                self.cnl_grammar_loaded = False
            elif grammar_type == "tau":
                self.tau_parser = None
                self.tau_grammar_loaded = False
            self.is_available = False
            return False

    def load_tau_grammar(self, grammar_path: str) -> bool:
        """
        Load a user-provided Tau grammar file.
        """
        try:
            if not os.path.exists(grammar_path):
                logger.error(f"Grammar file not found: {grammar_path}")
                return False

            with open(grammar_path, 'r') as f:
                grammar_content = f.read()
            
            grammar_name = Path(grammar_path).stem
            return self._initialize_parser_from_content(grammar_content, "tau", grammar_name)

        except Exception as e:
            logger.error(f"Failed to load Tau grammar: {e}")
            return False

    def can_translate(self, text: SourceText, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the translation."""
        if direction == TranslationDirection.TCE_TO_TAU:
            return self.cnl_grammar_loaded
        elif direction == TranslationDirection.TO_TCE:
            # For now, TCE is our only CNL target
            return self.tau_parser is not None and self.cnl_parser is not None
        return False

    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get supported translation directions."""
        directions = []
        if self.cnl_grammar_loaded:
            directions.append(TranslationDirection.TCE_TO_TAU)
        if self.tau_grammar_loaded:
            directions.append(TranslationDirection.TO_TCE)
        return directions

    def translate(self, text: SourceText, direction: TranslationDirection, **kwargs: Any) -> Result[TranslationResult, AppError]:
        """Perform grammar-based translation."""
        start_time = time.time()
        cache_key = self._get_cache_key(text, direction, **kwargs)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return Success(cached_result)

        if not self.is_available:
            return Failure(AppError(error_code="TRANSLATION_ENGINE_NOT_AVAILABLE", message=self.last_error or "Engine not available"))

        if direction == TranslationDirection.TCE_TO_TAU:
            result = self._translate_tce_to_tau(text, start_time)
        elif direction == TranslationDirection.TO_TCE:  # Assuming this is Tau to TCE
            result = self._translate_tau_to_tce(text, start_time)
        else:
            return Failure(AppError(error_code="UNSUPPORTED_DIRECTION", message="Unsupported translation direction"))
        
        if is_successful(result):
            self._store_in_cache(cache_key, result.unwrap())

        return result

    async def translate_async(self, text: SourceText, direction: TranslationDirection, **kwargs: Any) -> Result[TranslationResult, AppError]:
        """Perform the translation asynchronously."""
        # This is a simple async wrapper. For CPU-bound tasks, consider running in a thread pool.
        return self.translate(text, direction, **kwargs)

    def _translate_tce_to_tau(self, tce_text: SourceText, start_time: float) -> Result[TranslationResult, AppError]:
        """Translate TCE to Tau using grammar parser."""
        if not self.cnl_parser or not self.cnl_transformer:
            logger.error("TCE to Tau translation failed: CNL parser or transformer not loaded.")
            return Failure(AppError(error_code="TRANSLATION_ENGINE_NOT_READY", message="CNL parser or transformer not loaded"))

        try:
            text_to_parse = tce_text.text
            logger.debug(f"Attempting to parse TCE text: '{text_to_parse}'")

            # The grammar is designed to handle sentence termination.
            # We pass the raw text directly to the parser.
            tree = self.cnl_parser.parse(text_to_parse)
            logger.debug("TCE text parsed successfully. Transforming tree...")
            
            # Use the enhanced transformer to convert the parse tree to Tau.
            final_translation = self.cnl_transformer.transform(tree)
            logger.debug(f"Transformation successful. Result: {final_translation}")
            
            # Collect metadata for analysis and logging.
            all_patterns = self._extract_patterns_from_tree(tree)

            return Success(self._create_result(
                success=True,
                translated_text=str(final_translation),
                original_text=tce_text.text,
                direction=TranslationDirection.TO_TAU,
                metadata={"patterns": all_patterns},
                start_time=start_time
            ))

        except lark_exceptions.UnexpectedInput as e:
            # If parsing fails, create a detailed error report.
            error_msg = f"Parse error in sentence '{tce_text.text}': {e.get_context(20)}"
            logger.exception(f"Lark parsing failed: {error_msg}")
            return Failure(AppError(
                error_code="GRAMMAR_PARSE_ERROR",
                message=f"Failed to parse TCE: {e}",
                details={"context": e.get_context(3)}
            ))
        except Exception as e:
            logger.exception(f"An unexpected error occurred during TCE to Tau translation: {e}")
            return Failure(AppError(
                error_code="TRANSLATION_ERROR",
                message=f"An unexpected error occurred: {e}"
            ))

    def _translate_tau_to_tce(self, tau_text: SourceText, start_time: float) -> Result[TranslationResult, AppError]:
        """Translate Tau to TCE using grammar parser."""
        if not self.tau_parser or not self.tau_transformer:
            return Failure(AppError(error_code="TRANSLATION_ENGINE_NOT_READY", message="Tau parser or transformer not loaded"))

        try:
            tree = self.tau_parser.parse(tau_text)
            transformed_text = self.tau_transformer.transform(tree)
            
            return Success(self._create_result(
                success=True,
                translated_text=str(transformed_text),
                original_text=tau_text,
                direction=TranslationDirection.TO_TCE,
                metadata={"patterns": self._extract_patterns_from_tree(tree)},
                start_time=start_time
            ))
        except lark_exceptions.UnexpectedInput as e:
            error_msg = f"Parse error at line {e.line}, column {e.column}: {e}"
            logger.debug(f"Tau parse error: {error_msg}")
            return Failure(AppError(
                error_code="GRAMMAR_PARSE_ERROR",
                message=error_msg,
                details={"parse_error": True, "error_line": e.line, "error_column": e.column}
            ))

    def _extract_patterns_from_tree(self, tree: Tree) -> List[str]:
        """Extract pattern types from parse tree for metadata."""
        patterns = set()

        def visit(node):
            if isinstance(node, Tree):
                patterns.add(node.data)
                for child in node.children:
                    visit(child)

        visit(tree)
        return list(patterns)[:10]

    def set_tau_transformer(self, transformer_class: type):
        """
        Allow users to set a custom transformer for their Tau grammar.
        """
        if self.tau_parser:
            self.tau_transformer = transformer_class()
            logger.info(f"Custom Tau transformer set: {transformer_class.__name__}")
        else:
            logger.warning("Cannot set transformer - Tau grammar not loaded")

    def load_cnl_grammar(self, grammar_path: str, transformer_class: Optional[type] = None) -> bool:
        """
        Load a user-provided CNL (Controlled Natural Language) grammar file.
        """
        try:
            if not os.path.exists(grammar_path):
                logger.error(f"CNL grammar file not found: {grammar_path}")
                return False

            with open(grammar_path, 'r') as f:
                cnl_grammar = f.read()

            self.cnl_parser = Lark(
                cnl_grammar,
                parser='lalr',
                start='start',
                propagate_positions=True
            )
            
            if transformer_class:
                self.cnl_transformer = transformer_class()
            else:
                self.cnl_transformer = EnhancedTCETransformer()

            self.cnl_grammar_loaded = True
            self.cnl_grammar_name = Path(grammar_path).stem
            logger.info(f"CNL grammar loaded successfully from {grammar_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load CNL grammar: {e}")
            return False

    def set_cnl_transformer(self, transformer_class: type):
        """
        Set a custom transformer for CNL to Tau conversion.
        """
        if self.cnl_parser:
            self.cnl_transformer = transformer_class()
            logger.info(f"Custom CNL transformer set: {transformer_class.__name__}")
        else:
            logger.warning("Cannot set transformer - CNL grammar not loaded")

    def get_grammar_info(self) -> Dict[str, Any]:
        """
        Get information about loaded grammars.
        """
        return {
            "cnl_grammar": {
                "loaded": self.cnl_grammar_loaded,
                "name": self.cnl_grammar_name,
                "is_default": False # Default concept is removed
            },
            "tau_grammar": {
                "loaded": self.tau_grammar_loaded,
                "name": self.tau_grammar_name
            },
            "can_translate_to_tau": self.cnl_grammar_loaded,
            "can_translate_to_cnl": self.tau_grammar_loaded and self.cnl_grammar_loaded
        }