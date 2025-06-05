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
from lark import Lark, Tree, Token, exceptions as lark_exceptions
from .base import TranslationEngine, TranslationResult, TranslationDirection, CachingEngine

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class GrammarTranslationEngine(CachingEngine):
    """Grammar-aware translation engine using Lark parser."""
    
    def __init__(self, grammar_dir: Optional[str] = None):
        super().__init__(
            name="grammar_aware",
            description="Grammar-driven translation with Lark parser",
            cache_size=100
        )
        
        self.grammar_dir = grammar_dir or os.environ.get('TAU_GRAMMAR_DIR', './grammars')
        self.cnl_parser = None  # Custom CNL parser
        self.tau_parser = None  # Tau language parser
        self.cnl_transformer = None
        self.tau_transformer = None
        
        # Use default TCE grammar initially
        self.tce_parser = None
        self.tce_transformer = None
        self._initialize_default_tce_parser()
        
        # Track which grammars are loaded
        self.cnl_grammar_loaded = False
        self.tau_grammar_loaded = False
        self.cnl_grammar_name = "TCE (default)"
        self.tau_grammar_name = None
        
        # Parser will be available if at least default TCE is loaded
        self.is_available = self.tce_parser is not None
        
        if not self.is_available:
            self.last_error = "Could not initialize default TCE parser"
    
    def _initialize_default_tce_parser(self):
        """Initialize the default TCE (Tau Controlled English) parser."""
        try:
            from src.tau_translator_omega.core_engine.tce_tau_transformer import TCEToTauTransformer
            
            # Load TCE grammar from embedded file - use fixed version
            tce_grammar_path = Path(__file__).parent.parent.parent.parent / \
                               "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
            
            if not tce_grammar_path.exists():
                logger.error(f"Default TCE grammar not found at {tce_grammar_path}")
                return
            
            with open(tce_grammar_path, 'r') as f:
                tce_grammar = f.read()
            
            # Create parser with transformer
            self.tce_parser = Lark(
                tce_grammar,
                parser='lalr',
                start='start',
                propagate_positions=True
            )
            
            self.tce_transformer = TCEToTauTransformer()
            self.cnl_parser = self.tce_parser  # Use TCE as default CNL
            self.cnl_transformer = self.tce_transformer
            logger.info("Default TCE parser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize default TCE parser: {e}")
            self.tce_parser = None
    
    def load_tau_grammar(self, grammar_path: str) -> bool:
        """
        Load a user-provided Tau grammar file.
        
        Args:
            grammar_path: Path to the Tau grammar file (.lark format)
            
        Returns:
            True if grammar loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(grammar_path):
                logger.error(f"Grammar file not found: {grammar_path}")
                return False
            
            with open(grammar_path, 'r') as f:
                tau_grammar = f.read()
            
            # Create Tau parser
            self.tau_parser = Lark(
                tau_grammar,
                parser='lalr',
                start='start',
                propagate_positions=True
            )
            
            # For now, we'll use a simple transformer that converts to string
            # Users can provide custom transformers for their grammar
            from src.tau_translator_omega.core_engine.tce_tau_transformer import TauToTCETransformer
            self.tau_transformer = TauToTCETransformer()
            
            logger.info(f"Tau grammar loaded successfully from {grammar_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Tau grammar: {e}")
            return False
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the translation."""
        if not self.validate_input(text):
            return False
        
        # For CNL to Tau, we need CNL parser
        if direction == TranslationDirection.TO_TAU:
            return self.cnl_parser is not None
        
        # For Tau to CNL, we need both parsers
        elif direction == TranslationDirection.TO_TCE:
            return self.cnl_parser is not None and self.tau_parser is not None
        
        return False
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get supported translation directions."""
        directions = []
        
        if self.cnl_parser:
            directions.append(TranslationDirection.TO_TAU)
        
        if self.tau_parser and self.cnl_parser:
            directions.append(TranslationDirection.TO_TCE)
            
        return directions
    
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Perform grammar-based translation."""
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(text, direction, **kwargs)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        if not self.can_translate(text, direction):
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message="Grammar engine cannot handle this translation. " +
                             ("Load Tau grammar first." if direction == TranslationDirection.TO_TCE else "Load CNL grammar first."),
                start_time=start_time
            )
        
        try:
            if direction == TranslationDirection.TO_TAU:
                result = self._translate_tce_to_tau(text, start_time)
            else:  # TO_TCE
                result = self._translate_tau_to_tce(text, start_time)
            
            # Cache successful results
            if result.success:
                self._store_in_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Grammar translation error: {e}")
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message=f"Grammar translation failed: {str(e)}",
                start_time=start_time
            )
    
    def _translate_tce_to_tau(self, tce_text: str, start_time: float) -> TranslationResult:
        """Translate TCE to Tau using grammar parser."""
        try:
            # Parse TCE text
            parse_tree = self.tce_parser.parse(tce_text)
            
            # Transform to Tau
            tau_output = self.tce_transformer.transform(parse_tree)
            
            # Extract patterns from parse tree
            patterns = self._extract_patterns_from_tree(parse_tree)
            
            return self._create_result(
                success=True,
                translated_text=tau_output,
                original_text=tce_text,
                direction=TranslationDirection.TO_TAU,
                confidence=0.95,  # Grammar parsing is high confidence
                metadata={
                    "engine_type": "grammar_parser",
                    "parser": "lark",
                    "patterns_detected": patterns
                },
                start_time=start_time
            )
            
        except lark_exceptions.UnexpectedInput as e:
            # Parsing error - provide helpful feedback
            error_msg = f"Parse error at line {e.line}, column {e.column}: {e}"
            logger.debug(f"TCE parse error: {error_msg}")
            
            return self._create_result(
                success=False,
                translated_text="",
                original_text=tce_text,
                direction=TranslationDirection.TO_TAU,
                error_message=error_msg,
                metadata={
                    "parse_error": True,
                    "error_line": e.line,
                    "error_column": e.column
                },
                start_time=start_time
            )
    
    def _translate_tau_to_tce(self, tau_text: str, start_time: float) -> TranslationResult:
        """Translate Tau to TCE using grammar parser."""
        if not self.tau_parser:
            return self._create_result(
                success=False,
                translated_text="",
                original_text=tau_text,
                direction=TranslationDirection.TO_TCE,
                error_message="Tau grammar not loaded. Please load a Tau grammar file first.",
                start_time=start_time
            )
        
        try:
            # Parse Tau text
            parse_tree = self.tau_parser.parse(tau_text)
            
            # Transform to TCE
            tce_output = self.tau_transformer.transform(parse_tree)
            
            # Extract patterns from parse tree
            patterns = self._extract_patterns_from_tree(parse_tree)
            
            return self._create_result(
                success=True,
                translated_text=tce_output,
                original_text=tau_text,
                direction=TranslationDirection.TO_TCE,
                confidence=0.95,  # Grammar parsing is high confidence
                metadata={
                    "engine_type": "grammar_parser",
                    "parser": "lark",
                    "patterns_detected": patterns
                },
                start_time=start_time
            )
            
        except lark_exceptions.UnexpectedInput as e:
            # Parsing error
            error_msg = f"Parse error at line {e.line}, column {e.column}: {e}"
            logger.debug(f"Tau parse error: {error_msg}")
            
            return self._create_result(
                success=False,
                translated_text="",
                original_text=tau_text,
                direction=TranslationDirection.TO_TCE,
                error_message=error_msg,
                metadata={
                    "parse_error": True,
                    "error_line": e.line,
                    "error_column": e.column
                },
                start_time=start_time
            )
    
    def _extract_patterns_from_tree(self, tree: Tree) -> List[str]:
        """Extract pattern types from parse tree for metadata."""
        patterns = set()
        
        def visit(node):
            if isinstance(node, Tree):
                patterns.add(node.data)
                for child in node.children:
                    visit(child)
        
        visit(tree)
        return list(patterns)[:10]  # Limit to first 10 patterns
    
    def set_tau_transformer(self, transformer_class):
        """
        Allow users to set a custom transformer for their Tau grammar.
        
        Args:
            transformer_class: A Lark Transformer class for Tau to TCE conversion
        """
        if self.tau_parser:
            self.tau_transformer = transformer_class()
            logger.info(f"Custom Tau transformer set: {transformer_class.__name__}")
        else:
            logger.warning("Cannot set transformer - Tau grammar not loaded")
    
    def load_cnl_grammar(self, grammar_path: str, transformer_class=None) -> bool:
        """
        Load a user-provided CNL (Controlled Natural Language) grammar file.
        
        Args:
            grammar_path: Path to the CNL grammar file (.lark format)
            transformer_class: Optional custom transformer class for CNL to Tau conversion
            
        Returns:
            True if grammar loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(grammar_path):
                logger.error(f"CNL grammar file not found: {grammar_path}")
                return False
            
            with open(grammar_path, 'r') as f:
                cnl_grammar = f.read()
            
            # Create CNL parser
            self.cnl_parser = Lark(
                cnl_grammar,
                parser='lalr',
                start='start',
                propagate_positions=True
            )
            
            # Use provided transformer or default TCE transformer
            if transformer_class:
                self.cnl_transformer = transformer_class()
            else:
                from src.tau_translator_omega.core_engine.tce_tau_transformer import TCEToTauTransformer
                self.cnl_transformer = TCEToTauTransformer()
            
            self.cnl_grammar_loaded = True
            self.cnl_grammar_name = Path(grammar_path).stem
            logger.info(f"CNL grammar loaded successfully from {grammar_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load CNL grammar: {e}")
            return False
    
    def set_cnl_transformer(self, transformer_class):
        """
        Set a custom transformer for CNL to Tau conversion.
        
        Args:
            transformer_class: A Lark Transformer class for CNL to Tau conversion
        """
        if self.cnl_parser:
            self.cnl_transformer = transformer_class()
            logger.info(f"Custom CNL transformer set: {transformer_class.__name__}")
        else:
            logger.warning("Cannot set transformer - CNL grammar not loaded")
    
    def get_grammar_info(self) -> Dict[str, Any]:
        """
        Get information about loaded grammars.
        
        Returns:
            Dictionary with grammar status information
        """
        return {
            "cnl_grammar": {
                "loaded": self.cnl_parser is not None,
                "name": self.cnl_grammar_name,
                "is_default": self.cnl_grammar_name == "TCE (default)"
            },
            "tau_grammar": {
                "loaded": self.tau_parser is not None,
                "name": self.tau_grammar_name
            },
            "can_translate_to_tau": self.cnl_parser is not None,
            "can_translate_to_cnl": self.tau_parser is not None and self.cnl_parser is not None
        }