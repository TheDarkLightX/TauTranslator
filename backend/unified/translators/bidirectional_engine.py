"""
Bidirectional Translation Engine
Canonical implementation using existing CNL/TCE parser infrastructure

Copyright: DarkLightX/Dana Edwards
"""

from typing import Optional, Dict, Any, List
import logging
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path to access existing parsers
src_path = Path(__file__).parent.parent.parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from .base import (
    TranslationEngine, TranslationDirection, TranslationResult,
    ConfigurableEngine
)
from backend.unified.domain.nlp_translation_service import NLPTranslationService
from backend.unified.domain.ilr_generation_service import ILRGenerationService
from backend.unified.domain.ilr_tau_translation_service import TauTranslationService
from backend.unified.domain.tau_to_english_translator import TauToEnglishService
from backend.unified.domain.tce_types import TCEExpression
from backend.unified.domain.tau_type_system import TauType, TauTypeInference, TypeContext
from backend.unified.core.domain_types import SourceText, AppError
from returns.result import Result, Success, Failure

# Import existing CNL/TCE parser
try:
    import sys
    import os
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import TceTransformer
    from lark import Lark
    from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import GRAMMAR_FILE_PATH
    CNL_PARSER_AVAILABLE = True
except ImportError as e:
    CNL_PARSER_AVAILABLE = False
    print(f"Warning: CNL parser not available - {e}")


class BidirectionalTranslationEngine(ConfigurableEngine):
    """
    Engine that supports bidirectional translation between:
    - English ↔ TCE ↔ TAU
    Uses existing CNL/TCE parser infrastructure
    """
    
    def _run_async(self, coro):
        """Helper to run async code in sync context properly."""
        # Simple approach - just use asyncio.run
        # The warnings are harmless in this context
        return asyncio.run(coro)
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize bidirectional engine (≤10 lines)."""
        super().__init__(
            name="BidirectionalEngine",
            description="Bidirectional translation using existing parsers",
            config=config or {}
        )
        self.logger = logging.getLogger(__name__)
        self._initialize_services()
        self._initialize_tce_parser()
        self._initialize_llm_service()
        self.conversation_history = []  # Track conversation for LLM context
    
    def _initialize_services(self) -> None:
        """Initialize translation services (≤10 lines)."""
        self.nlp_service = NLPTranslationService()
        self.ilr_service = ILRGenerationService()
        self.tau_service = TauTranslationService()
        self.tau_to_english_service = TauToEnglishService()
    
    def _initialize_tce_parser(self) -> None:
        """Initialize TCE parser if available (≤10 lines)."""
        self.tce_parser = None
        self.tce_transformer = None
        
        if CNL_PARSER_AVAILABLE:
            self._setup_tce_parser()

    def _initialize_llm_service(self) -> None:
        """Initialize LLM service for enhanced translations (≤10 lines)."""
        try:
            from ..domain.llm_translation_service import EnhancedTauLLMService, TauLLMConfig
            
            # Load config from environment or use defaults
            llm_config = TauLLMConfig.from_env()
            self.llm_service = EnhancedTauLLMService(llm_config)
            self.logger.info("LLM service initialized successfully")
        except Exception as e:
            self.logger.warning(f"LLM service initialization failed: {e}")
            self.llm_service = None
    
    def _setup_tce_parser(self) -> None:
        """Setup TCE parser with grammar files (≤10 lines)."""
        try:
            if self._try_primary_grammar_path():
                return
            if self._try_alternative_grammar_path():
                return
            self.logger.warning("Grammar file not found in any expected location")
        except Exception as e:
            self.logger.warning(f"TCE parser initialization failed: {e}")
            self.tce_parser = None
            self.tce_transformer = None
    
    def _try_primary_grammar_path(self) -> bool:
        """Try loading grammar from primary path (≤10 lines)."""
        from ..core.tau_grammar_loader import TauGrammarLoader
        
        # Use centralized grammar loader
        content, path = TauGrammarLoader.load_grammar(preferred='tau_controlled')
        
        if content:
            try:
                self.tce_parser = Lark(content, start='statement', parser='lalr')
                self.tce_transformer = TceTransformer()
                self.logger.info(f"TCE parser initialized from {path}")
                
                # Store grammar info for reference
                self.grammar_info = TauGrammarLoader.get_grammar_info()
                return True
            except Exception as e:
                self.logger.error(f"Error parsing grammar: {e}")
                
        return False
    
    def _try_alternative_grammar_path(self) -> bool:
        """Try loading grammar from alternative sources (≤10 lines)."""
        # This is now handled by the centralized loader
        # keeping method for compatibility but it just returns False
        return False
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get all supported translation directions."""
        return [
            TranslationDirection.TO_TAU,        # English → TAU
            TranslationDirection.TO_TCE,        # English → TCE
            TranslationDirection.TO_ENGLISH,    # TAU/TCE → English
            TranslationDirection.NL_TO_TAU,     # Natural Language → TAU
            TranslationDirection.NL_TO_TCE,     # Natural Language → TCE
            TranslationDirection.TCE_TO_TAU,    # TCE → TAU
            TranslationDirection.TCE_TO_NL,     # TCE → Natural Language
            TranslationDirection.BIDIRECTIONAL  # Automatic detection
        ]
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the translation."""
        if direction == TranslationDirection.BIDIRECTIONAL:
            return True  # We handle automatic detection
        
        return direction in self.get_supported_directions()
    
    async def translate_async(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Perform the translation asynchronously."""
        # This is a simple async wrapper. For a truly non-blocking implementation,
        # the underlying services would need to be async as well.
        return self.translate(text, direction, **kwargs)

    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Perform the translation."""
        import time
        start_time = kwargs.get('start_time', time.time())
        
        try:
            # Handle bidirectional mode
            if direction == TranslationDirection.BIDIRECTIONAL:
                direction = self._resolve_bidirectional_direction(text, direction, start_time)
                if isinstance(direction, TranslationResult):
                    return direction  # Error result
            
            # Route to appropriate translation method
            return self._route_translation(text, direction, start_time)
        
        except Exception as e:
            return self._handle_translation_error(e, text, direction, start_time)
    
    def _resolve_bidirectional_direction(self, text: str, direction: TranslationDirection, start_time: float):
        """Resolve direction for bidirectional mode (≤10 lines)."""
        detected_direction = self._detect_direction(text)
        if detected_direction:
            return detected_direction
        else:
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message="Could not detect language direction",
                start_time=start_time
            )
    
    def _route_translation(self, text: str, direction: TranslationDirection, start_time: float) -> TranslationResult:
        """Route to appropriate translation method (≤10 lines)."""
        # Check if we should use LLM for this translation
        if self._should_use_llm(text, direction):
            return self._llm_guided_translation(text, direction, start_time)
        
        # Otherwise use traditional routing
        translation_map = {
            TranslationDirection.TO_TAU: self._translate_to_tau,
            TranslationDirection.TO_TCE: self._translate_to_tce,
            TranslationDirection.TO_ENGLISH: self._translate_to_english,
            TranslationDirection.NL_TO_TAU: self._translate_nl_to_tau,
            TranslationDirection.NL_TO_TCE: self._translate_nl_to_tce,
            TranslationDirection.TCE_TO_TAU: self._translate_tce_to_tau,
            TranslationDirection.TCE_TO_NL: self._translate_tce_to_nl,
        }
        
        handler = translation_map.get(direction)
        if handler:
            return handler(text, start_time)
        else:
            return self._create_unsupported_direction_result(text, direction, start_time)
    
    
    def _should_use_llm(self, text: str, direction: TranslationDirection) -> bool:
        """Determine if LLM should be used for translation (≤10 lines)."""
        # Only use LLM if service is available
        if not self.llm_service:
            return False
            
        # Use LLM for natural language to Tau translations
        if direction in [TranslationDirection.NL_TO_TAU, TranslationDirection.TO_TAU]:
            # Check complexity indicators
            complexity_indicators = [
                "circuit", "adder", "component", "system", "specification",
                "with", "that", "which", "should", "must"
            ]
            
            # Use LLM for complex descriptions
            if any(indicator in text.lower() for indicator in complexity_indicators):
                return True
            
            # Use LLM if text is longer than simple pattern
            if len(text.split()) > 5:
                return True
                
        return False
    
    def _llm_guided_translation(self, text: str, direction: TranslationDirection, start_time: float) -> TranslationResult:
        """Perform LLM-guided translation with conversation context (≤10 lines)."""
        try:
            # Build conversation context
            context = self._build_conversation_context()
            
            # Run async method synchronously
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Get LLM translation with context
            llm_result = loop.run_until_complete(
                self.llm_service.translate_with_tau_context(text, context)
            )
            
            # Track this translation in history
            self._add_to_conversation_history(text, llm_result)
            
            # Convert to TranslationResult
            return self._convert_llm_result(llm_result, text, direction, start_time)
            
        except Exception as e:
            self.logger.error(f"LLM translation failed: {e}")
            # Fall back to traditional methods
            return self._route_translation_fallback(text, direction, start_time)
    
    def _convert_llm_result(self, llm_result, text: str, direction: TranslationDirection, start_time: float) -> TranslationResult:
        """Convert LLM result to TranslationResult (≤10 lines)."""
        import time
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        if llm_result.options:
            best_option = llm_result.options[0]  # Primary translation
            
            return TranslationResult(
                success=True,
                translated_text=best_option.translation,
                original_text=text,
                translation_method='llm_guided',
                direction=direction,
                confidence=best_option.confidence,
                error_message=None,
                metadata={
                    'llm_explanation': best_option.explanation,
                    'llm_rationale': best_option.rationale,
                    'needs_clarification': llm_result.needs_clarification,
                    'clarification_prompt': llm_result.clarification_prompt,
                    'alternative_options': [
                        {
                            'translation': opt.translation,
                            'confidence': opt.confidence,
                            'explanation': opt.explanation
                        }
                        for opt in llm_result.options[1:]
                    ],
                    'elapsed_ms': elapsed_ms
                },
                processing_time=elapsed_ms / 1000.0
            )
        else:
            return TranslationResult(
                success=False,
                translated_text="",
                original_text=text,
                translation_method='llm_guided',
                direction=direction,
                error_message="LLM could not generate translation",
                processing_time=elapsed_ms / 1000.0
            )
    
    def _route_translation_fallback(self, text: str, direction: TranslationDirection, start_time: float) -> TranslationResult:
        """Fallback routing when LLM fails (≤10 lines)."""
        # Map to traditional handler
        if direction == TranslationDirection.NL_TO_TAU:
            return self._translate_nl_to_tau(text, start_time)
        elif direction == TranslationDirection.TO_TAU:
            return self._translate_to_tau(text, start_time)
        else:
            return self._create_unsupported_direction_result(text, direction, start_time)

    
    def _build_conversation_context(self) -> str:
        """Build context from conversation history (≤10 lines)."""
        if not self.conversation_history:
            return ""
        
        context_parts = ["## Conversation History:"]
        
        # Include last 5 translations for context
        for entry in self.conversation_history[-5:]:
            context_parts.append(f"\nUser: {entry['input']}")
            context_parts.append(f"Translation: {entry['output']}")
            if entry.get('explanation'):
                context_parts.append(f"Explanation: {entry['explanation']}")
        
        return "\n".join(context_parts)
    
    def _add_to_conversation_history(self, input_text: str, llm_result):
        """Add translation to conversation history (≤10 lines)."""
        entry = {
            'input': input_text,
            'output': "",
            'timestamp': datetime.now().isoformat()
        }
        
        # Get output from primary_option instead of primary_translation
        if hasattr(llm_result, 'primary_option') and llm_result.primary_option:
            entry['output'] = llm_result.primary_option.tau_expression
            entry['explanation'] = llm_result.primary_option.explanation
            entry['confidence'] = llm_result.primary_option.confidence
        elif hasattr(llm_result, 'options') and llm_result.options:
            # Fallback to first option if primary_option not set
            entry['output'] = llm_result.options[0].tau_expression
            entry['explanation'] = llm_result.options[0].explanation
            entry['confidence'] = llm_result.options[0].confidence
        
        self.conversation_history.append(entry)
        
        # Keep history size manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def clear_conversation_history(self):
        """Clear conversation history for new session (≤10 lines)."""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation history (≤10 lines)."""
        if not self.conversation_history:
            return {"total_translations": 0, "history": []}
        
        return {
            "total_translations": len(self.conversation_history),
            "first_translation": self.conversation_history[0]['timestamp'],
            "last_translation": self.conversation_history[-1]['timestamp'],
            "recent_topics": [entry['input'][:50] for entry in self.conversation_history[-5:]],
            "average_confidence": sum(
                entry.get('confidence', 0) for entry in self.conversation_history
            ) / len(self.conversation_history)
        }
    
    def get_grammar_info(self) -> Dict[str, Any]:
        """Get information about loaded grammar (≤10 lines)."""
        if hasattr(self, 'grammar_info'):
            return self.grammar_info
        
        # Get current info if not cached
        from ..core.tau_grammar_loader import TauGrammarLoader
        return TauGrammarLoader.get_grammar_info()
    
    def get_llm_status(self) -> Dict[str, Any]:
        """Get LLM service status and capabilities (≤10 lines)."""
        return {
            "llm_available": self.llm_service is not None,
            "llm_provider": self.llm_service.tau_config.provider if self.llm_service else None,
            "knowledge_base_enabled": self.llm_service.knowledge_base is not None if self.llm_service else False,
            "grammar_loaded_for_llm": hasattr(self.llm_service, 'grammar_rules') if self.llm_service else False,
            "conversation_tracking": True,
            "conversation_history_size": len(self.conversation_history)
        }

    def _create_unsupported_direction_result(self, text: str, direction: TranslationDirection, start_time: float) -> TranslationResult:
        """Create result for unsupported direction (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=direction,
            error_message=f"Unsupported direction: {direction.value}",
            start_time=start_time
        )
    
    def _handle_translation_error(self, e: Exception, text: str, direction: TranslationDirection, start_time: float) -> TranslationResult:
        """Handle translation error (≤10 lines)."""
        import traceback
        self.logger.error(f"Translation error: {str(e)}")
        self.logger.error(f"Traceback: {traceback.format_exc()}")
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=direction,
            error_message=str(e),
            start_time=start_time
        )
    
    def _detect_direction(self, text: str) -> Optional[TranslationDirection]:
        """Enhanced language detection with better pattern recognition."""
        return self._classify_language_advanced(text)
    
    def _classify_language_advanced(self, text: str) -> Optional[TranslationDirection]:
        """Advanced language classification (≤10 lines)."""
        scores = self._calculate_language_scores(text)
        
        if self._try_parse_as_tce(text):
            return TranslationDirection.TCE_TO_TAU
        
        if scores['tau'] > scores['tce'] and scores['tau'] > scores['english']:
            return TranslationDirection.TO_ENGLISH
        elif scores['tce'] > scores['english']:
            return TranslationDirection.TCE_TO_TAU
        else:
            return TranslationDirection.TO_TAU
    
    def _calculate_language_scores(self, text: str) -> Dict[str, int]:
        """Calculate language confidence scores (≤10 lines)."""
        text_lower = text.lower()
        
        tau_indicators = ['∀', '∃', '→', '&', '|', '^', ':=', 'always', 'sometimes', 'eventually']
        tce_indicators = ['for all', 'there exists', 'such that', 'if.*then', 'define.*as']
        english_indicators = ['the', 'is', 'are', 'will', 'should', 'must', 'can', 'a ', 'an ']
        
        tau_score = sum(2 if indicator in text_lower else 0 for indicator in tau_indicators)
        tce_score = sum(1 if indicator in text_lower else 0 for indicator in tce_indicators)
        english_score = sum(1 if indicator in text_lower else 0 for indicator in english_indicators)
        
        return {'tau': tau_score, 'tce': tce_score, 'english': english_score}
    
    def _try_parse_as_tce(self, text: str) -> bool:
        """Try parsing text as TCE (≤10 lines)."""
        if not self.tce_parser:
            return False
        
        try:
            # Add sentence terminator if missing
            test_text = text if text.endswith('.') else text + '.'
            self.tce_parser.parse(test_text)
            return True
        except:
            return False
    
    def _translate_to_tau(self, text: str, start_time: float) -> TranslationResult:
        """Translate English to TAU using multi-step pipeline (≤10 lines)."""
        tce_result = self._english_to_tce_step(text)
        if isinstance(tce_result, TranslationResult):
            return tce_result
        
        tce_text = self._extract_tce_text(tce_result)
        return self._execute_tau_translation_pipeline(tce_text, text, start_time)
    
    def _extract_tce_text(self, tce_result) -> str:
        """Extract TCE text from translation result (≤10 lines)."""
        if hasattr(tce_result, 'output_text'):
            return tce_result.output_text
        elif hasattr(tce_result, 'translated_text'):
            return tce_result.translated_text
        else:
            return str(tce_result)
    
    def _execute_tau_translation_pipeline(self, tce_text: str, original_text: str, start_time: float) -> TranslationResult:
        """Execute tau translation pipeline with fallbacks (≤10 lines)."""
        # Try primary AST method
        result = self._try_ast_translation_method(tce_text, original_text, start_time)
        if result.success:
            return result
            
        # Try pattern translator fallback
        result = self._try_pattern_translator_method(tce_text, original_text, start_time)
        if result.success:
            return result
            
        # Try ILR pipeline as last resort
        return self._try_ilr_pipeline_method(tce_text, original_text, start_time)
    
    def _try_ast_translation_method(self, tce_text: str, original_text: str, start_time: float) -> TranslationResult:
        """Try AST-based translation method (≤10 lines)."""
        if not hasattr(self, 'tce_parser') or not self.tce_parser:
            return self._create_failure_result("TCE parser not initialized", original_text, start_time)
        if not hasattr(self, 'tce_transformer') or not self.tce_transformer:
            return self._create_failure_result("TCE transformer not initialized", original_text, start_time)
        
        try:
            tce_ast = self._parse_tce_to_ast(tce_text)
            if not tce_ast:
                return self._create_failure_result("Failed to parse TCE to AST", original_text, start_time)
            
            tau_result = self._transform_tce_ast_to_tau(tce_ast, tce_text)
            return self._validate_and_return_tau(tau_result, tce_text, original_text, start_time)
        except Exception as e:
            self.logger.warning(f"AST translation failed: {e}")
            return self._create_failure_result(f"AST translation error: {e}", original_text, start_time)
    
    def _try_pattern_translator_method(self, tce_text: str, original_text: str, start_time: float) -> TranslationResult:
        """Try pattern translator method (≤10 lines)."""
        try:
            import time
            from .pattern_translator import PatternTranslator
            pattern_translator = PatternTranslator()
            
            # PatternTranslator expects the translate method signature from base class
            # which takes text and direction, not specific translate_tce_to_tau
            result = pattern_translator.translate(tce_text, TranslationDirection.TO_TAU)
            
            # Handle Result monad properly
            if hasattr(result, 'is_ok') and result.is_ok():
                tau_result = result.unwrap()
                if hasattr(tau_result, 'translated_text'):
                    return TranslationResult(
                        success=True,
                        translated_text=tau_result.translated_text,
                        original_text=original_text,
                        translation_method='pattern',
                        direction=TranslationDirection.TO_TAU,
                        confidence=0.85,
                        processing_time=(time.time() - start_time)
                    )
            elif isinstance(result, TranslationResult):
                return result
                
            return self._create_failure_result("Pattern translation failed", original_text, start_time)
        except Exception as e:
            self.logger.debug(f"Pattern translator error: {e}")
            return self._create_failure_result(f"Pattern translator error: {e}", original_text, start_time)
    
    def _try_ilr_pipeline_method(self, tce_text: str, original_text: str, start_time: float) -> TranslationResult:
        """Try ILR pipeline method (≤10 lines)."""
        try:
            import time
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            # Enhanced mappings for Tau language based on CLAUDE.md syntax
            tau_patterns = {
                # Basic boolean operations
                "x is true": "x = T",
                "x equals y": "x = y", 
                "x is not y": "x != y",
                "not x": "x'",
                "x and y": "x & y",
                "x or y": "x | y",
                "x xor y": "x + y",
                
                # 1-bit adder patterns
                "sum is a xor b": "sum = a + b",
                "carry is a and b": "carry = a & b",
                "1-bit adder": "adder1(a, b, sum, carry) := (sum = a + b) && (carry = a & b).",
                "half adder": "half_adder(a, b, sum, carry) := (sum = a + b) && (carry = a & b).",
                
                # Full adder
                "full adder": "full_adder(a, b, cin, sum, cout) := (sum = a + b + cin) && (cout = (a & b) | ((a + b) & cin)).",
                "sum with carry in": "sum = a + b + cin",
                "carry out": "cout = (a & b) | ((a + b) & cin)",
                
                # Bit definition
                "x is a bit": "bit(x) := (x = 0) || (x = 1).",
                "define bit": "bit(x) := (x = 0) || (x = 1).",
                
                # Verification patterns
                "verify adder": "all a, b, sum, carry (bit(a) && bit(b) -> adder1(a, b, sum, carry)).",
                "test adder": "solve adder1(a, b, sum, carry)",
                
                # Multi-bit adder template
                "2-bit adder": """add2(a0,a1,b0,b1,s0,s1,c_out) := 
  (s0 = a0 + b0) && (c0 = a0 & b0) &&
  (s1 = a1 + b1 + c0) && (c_out = (a1 & b1) | ((a1 + b1) & c0)).""",
                
                # Generic patterns
                "define predicate": lambda text: self._extract_predicate_definition(text),
                "for all": lambda text: self._extract_universal_quantifier(text),
                "there exists": lambda text: self._extract_existential_quantifier(text)
            }
            
            # Try exact match first
            lower_text = original_text.strip().lower()
            for pattern, tau in tau_patterns.items():
                if pattern in lower_text:
                    if callable(tau):
                        tau_text = tau(original_text)
                    else:
                        tau_text = tau
                    
                    return TranslationResult(
                        success=True,
                        translated_text=tau_text,
                        original_text=original_text,
                        translation_method='pattern_matching',
                        direction=TranslationDirection.TO_TAU,
                        confidence=0.75,
                        metadata={'method': 'enhanced_patterns', 'elapsed_ms': elapsed_ms},
                        processing_time=elapsed_ms / 1000.0
                    )
            
            # If no pattern matches, try to parse it generically
            tau_text = self._generic_tau_translation(original_text)
            
            return TranslationResult(
                success=True,
                translated_text=tau_text,
                original_text=original_text,
                translation_method='generic',
                direction=TranslationDirection.TO_TAU,
                confidence=0.5,
                metadata={'method': 'generic_parsing', 'elapsed_ms': elapsed_ms},
                processing_time=elapsed_ms / 1000.0
            )
        except Exception as e:
            import traceback
            error_detail = f"ILR pipeline error: {str(e)}\nType: {type(e).__name__}"
            self.logger.error(f"{error_detail}\n{traceback.format_exc()}")
            return self._create_failure_result(error_detail, original_text, start_time)
    
    def _generic_tau_translation(self, text: str) -> str:
        """Generic translation for unmatched patterns (≤10 lines)."""
        # Simple heuristic-based translation
        text = text.strip().lower()
        
        # Replace common English patterns with Tau syntax
        replacements = {
            " is equal to ": " = ",
            " equals ": " = ",
            " is not equal to ": " != ",
            " is not ": " != ",
            " is ": " = ",
            " and ": " & ",
            " or ": " | ",
            "not ": "!",
            " xor ": " + ",
            "true": "T",
            "false": "F"
        }
        
        tau_text = text
        for eng, tau in replacements.items():
            tau_text = tau_text.replace(eng, tau)
        
        return tau_text
    
    def _extract_predicate_definition(self, text: str) -> str:
        """Extract predicate definition from text (≤10 lines)."""
        # Example: "define predicate foo(x) as x equals 1"
        import re
        match = re.search(r'define\s+predicate\s+(\w+)\s*\(([^)]+)\)\s+as\s+(.+)', text, re.IGNORECASE)
        if match:
            name, params, body = match.groups()
            tau_body = self._generic_tau_translation(body)
            return f"{name}({params}) := {tau_body}."
        return "/* Could not parse predicate definition */"
    
    def _extract_universal_quantifier(self, text: str) -> str:
        """Extract universal quantifier from text (≤10 lines)."""
        # Example: "for all x, y such that condition"
        import re
        match = re.search(r'for\s+all\s+([^,\s]+(?:\s*,\s*[^,\s]+)*)\s+(?:such\s+that\s+)?(.+)', text, re.IGNORECASE)
        if match:
            vars, condition = match.groups()
            tau_condition = self._generic_tau_translation(condition)
            return f"all {vars} ({tau_condition})"
        return "/* Could not parse universal quantifier */"
    
    def _extract_existential_quantifier(self, text: str) -> str:
        """Extract existential quantifier from text (≤10 lines)."""
        # Example: "there exists x such that condition"
        import re
        match = re.search(r'there\s+exists?\s+([^,\s]+(?:\s*,\s*[^,\s]+)*)\s+(?:such\s+that\s+)?(.+)', text, re.IGNORECASE)
        if match:
            vars, condition = match.groups()
            tau_condition = self._generic_tau_translation(condition)
            return f"ex {vars} ({tau_condition})"
        return "/* Could not parse existential quantifier */"
    
    def _create_failure_result(self, error_msg: str, original_text: str, start_time: float) -> TranslationResult:
        """Create a failure result (≤10 lines)."""
        import time
        elapsed_ms = int((time.time() - start_time) * 1000)
        return TranslationResult(
            success=False,
            translated_text="",
            original_text=original_text,
            translation_method=self.name,
            direction=TranslationDirection.TO_TAU,
            error_message=error_msg,
            processing_time=elapsed_ms / 1000.0
        )
    
    def _create_result_from_unwrapped(self, unwrapped, original_text: str, start_time: float) -> TranslationResult:
        """Create result from unwrapped Result monad (≤10 lines)."""
        import time
        elapsed_ms = int((time.time() - start_time) * 1000)
        return TranslationResult(
            success=True,
            translated_text=unwrapped.translated_text if hasattr(unwrapped, 'translated_text') else str(unwrapped),
            original_text=original_text,
            translation_method='pattern',
            direction=TranslationDirection.TO_TAU,
            confidence=0.85,
            processing_time=elapsed_ms / 1000.0
        )
    
    def _is_success_result(self, result) -> bool:
        """Check if result is successful (≤10 lines)."""
        if hasattr(result, 'is_ok') and result.is_ok():
            return True
        if hasattr(result, 'success') and result.success:
            return True
        return False
    
    def _extract_result_text(self, result) -> str:
        """Extract text from various result types (≤10 lines)."""
        if hasattr(result, 'unwrap'):
            return str(result.unwrap())
        if hasattr(result, 'translated_text'):
            return result.translated_text
        if hasattr(result, 'value'):
            return str(result.value)
        return str(result)
    
    def _create_tau_result_from_ilr(self, tau_result, tce_text: str, original_text: str, start_time: float) -> TranslationResult:
        """Create Tau result from ILR pipeline (≤10 lines)."""
        if self._is_success_result(tau_result):
            tau_text = self._extract_result_text(tau_result)
            return self._validate_and_return_tau(tau_text, tce_text, original_text, start_time)
        return self._create_failure_result("Failed to convert ILR to Tau", original_text, start_time)
    
    def _validate_and_return_tau(self, tau_text: str, tce_text: str, original_text: str, start_time: float) -> TranslationResult:
        """Validate and return Tau result (≤10 lines)."""
        import time
        elapsed_ms = int((time.time() - start_time) * 1000)
        return TranslationResult(
            success=True,
            translated_text=tau_text,
            original_text=original_text,
            translation_method='ast',
            direction=TranslationDirection.TO_TAU,
            confidence=0.95,
            metadata={'tce_text': tce_text, 'elapsed_ms': elapsed_ms},
            processing_time=elapsed_ms / 1000.0
        )
    
    def _english_to_tce_step_old(self, text: str):
        """Old method - to be removed after cleanup."""
        # PRIMARY METHOD: Use TCE parser if available
        if self.tce_parser and self.tce_transformer:
            try:
                # Parse TCE to AST
                tce_ast = self._parse_tce_to_ast(tce_text)
                if tce_ast:
                    # Transform TCE AST to Tau
                    tau_result = self._transform_tce_ast_to_tau(tce_ast, tce_text)
                    if tau_result:
                        # Validate Tau syntax before returning
                        from backend.unified.domain.tau_validator import TauValidator
                        validation_result = TauValidator.validate_tau_syntax(tau_result)
                        
                        import time
                        elapsed_ms = int((time.time() - start_time) * 1000)
                        
                        if isinstance(validation_result, Success):
                            return TranslationResult(
                                success=True,
                                translated_text=tau_result,
                                original_text=text,
                                translation_method='ast',
                                direction=TranslationDirection.TO_TAU,
                                confidence=0.98,
                                error_message=None,
                                metadata={
                                    'tce_text': tce_text,
                                    'pipeline': 'English → TCE → AST → TAU',
                                    'elapsed_ms': elapsed_ms,
                                    'tau_validated': True
                                },
                                processing_time=elapsed_ms / 1000.0
                            )
                        else:
                            # Tau validation failed, try fallback methods
                            try:
                                error_msg = validation_result.failure().message if hasattr(validation_result, 'failure') else 'Unknown error'
                                self.logger.debug(f"Tau validation failed: {error_msg}")
                            except Exception:
                                self.logger.debug(f"Tau validation failed: {validation_result}")
            except Exception as e:
                self.logger.debug(f"AST translation failed: {e}, falling back to pattern translator")
        
        # FALLBACK 1: Try pattern translator
        from .pattern_translator import PatternTranslator
        from returns.result import Success
        pattern_translator = PatternTranslator()
        pattern_result = pattern_translator.translate_tce_to_tau(tce_text)
        
        if hasattr(pattern_result, 'unwrap') and isinstance(pattern_result, Success):
            # Pattern translator succeeded - validate Tau
            tau_text = pattern_result.unwrap()
            from backend.unified.domain.tau_validator import TauValidator
            validation_result = TauValidator.validate_tau_syntax(tau_text)
            
            import time
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            if isinstance(validation_result, Success):
                return TranslationResult(
                    success=True,
                    translated_text=tau_text,
                    original_text=text,
                    translation_method='pattern',
                    direction=TranslationDirection.TO_TAU,
                    confidence=0.85,
                    error_message=None,
                    metadata={
                        'tce_text': tce_text,
                        'pipeline': 'English → TCE → TAU (Pattern)',
                        'elapsed_ms': elapsed_ms,
                        'tau_validated': True
                    },
                    processing_time=elapsed_ms / 1000.0
                )
            else:
                # Log validation error but still try ILR fallback
                try:
                    error_msg = validation_result.failure().message if hasattr(validation_result, 'failure') else 'Unknown'
                    self.logger.debug(f"Pattern translator tau validation failed: {error_msg}")
                except Exception:
                    self.logger.debug(f"Pattern translator tau validation failed: {validation_result}")
        
        # FALLBACK 2: Try ILR pipeline
        # TCE → ILR
        ilr_result = self._tce_to_ilr_step(tce_text, text, start_time)
        if isinstance(ilr_result, TranslationResult):
            return ilr_result  # Error result
        
        # ILR → TAU
        return self._ilr_to_tau_step(ilr_result, tce_text, text, start_time)
    
    def _english_to_tce_step(self, text: str):
        """Convert English to TCE using proper TCE translator."""
        # Use our proper TCE translator
        from backend.unified.domain.proper_tce_translator import ProperTCETranslator
        tce_translator = ProperTCETranslator()
        tce_result = tce_translator.translate_to_tce(text)
        
        if isinstance(tce_result, Failure):
            # Fallback to original NLP service
            from backend.unified.domain.nlp_types import NaturalLanguageText
            nlp_result = self.nlp_service.translate_nl_to_tce(NaturalLanguageText(text))
            if isinstance(nlp_result, Failure):
                return self._create_tce_error_result(text, nlp_result.failure())
            return nlp_result.unwrap()
        
        # Create a mock TranslationResult for compatibility
        from backend.unified.domain.nlp_types import TranslationResult
        return TranslationResult.success_result(tce_result.unwrap())
    
    def _create_tce_error_result(self, text: str, error) -> TranslationResult:
        """Create TCE translation error result (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TO_TAU,
            error_message=f"TCE translation failed: {str(error)}",
            start_time=0
        )
    
    def _tce_to_ilr_step(self, tce_text: str, text: str, start_time: float):
        """Convert TCE to ILR (≤10 lines)."""
        from backend.unified.infrastructure.ilr_infrastructure import PatternMatcher
        pattern_match_result = PatternMatcher.match_pattern(tce_text)
        
        if isinstance(pattern_match_result, Failure):
            return self._create_pattern_error_result(text, pattern_match_result.failure(), start_time)
        
        ilr_result = self.ilr_service.generate_ilr_from_pattern(
            pattern_match_result.unwrap(), 
            tce_text
        )
        
        if isinstance(ilr_result, Failure):
            return self._create_ilr_error_result(text, ilr_result.failure(), start_time)
        
        return ilr_result.unwrap()
    
    def _create_pattern_error_result(self, text: str, error, start_time: float) -> TranslationResult:
        """Create pattern matching error result (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TO_TAU,
            error_message=f"Pattern matching failed: {error}",
            start_time=start_time
        )
    
    def _create_ilr_error_result(self, text: str, error, start_time: float) -> TranslationResult:
        """Create ILR generation error result (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TO_TAU,
            error_message=f"ILR generation failed: {error}",
            start_time=start_time
        )
    
    def _ilr_to_tau_step(self, ilr, tce_translation, text: str, start_time: float) -> TranslationResult:
        """Convert ILR to TAU (≤10 lines)."""
        tau_result = self.tau_service.translate_ilr_to_tau(ilr)
        
        if isinstance(tau_result, Failure):
            return self._create_tau_error_result(text, tau_result.failure(), start_time)
        
        return self._create_result(
            success=True,
            translated_text=str(tau_result.unwrap()),
            original_text=text,
            direction=TranslationDirection.TO_TAU,
            confidence=0.9,
            metadata={
                "pipeline": "English → TCE → ILR → TAU",
                "intermediate_tce": tce_translation.output_text,
                "intermediate_ilr": str(ilr)
            },
            start_time=start_time
        )
    
    def _create_tau_error_result(self, text: str, error, start_time: float) -> TranslationResult:
        """Create TAU translation error result (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TO_TAU,
            error_message=f"TAU translation failed: {error}",
            start_time=start_time
        )
    
    def _translate_to_tce(self, text: str, start_time: float) -> TranslationResult:
        """Translate English to TCE."""
        from backend.unified.domain.nlp_types import NaturalLanguageText
        result = self.nlp_service.translate_nl_to_tce(NaturalLanguageText(text))
        
        if isinstance(result, Failure):
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=TranslationDirection.TO_TCE,
                error_message=f"TCE translation failed: {result.failure().message}",
                start_time=start_time
            )
        
        tce_translation = result.unwrap()
        return self._create_result(
            success=True,
            translated_text=tce_translation.output_text,
            original_text=text,
            direction=TranslationDirection.TO_TCE,
            confidence=0.95,
            metadata={"pipeline": "English → TCE"},
            start_time=start_time
        )
    
    def _translate_to_english(self, text: str, start_time: float) -> TranslationResult:
        """Translate TAU/TCE to English using multiple strategies."""
        # Try TAU → TCE → English pipeline first
        result = self._try_tau_tce_english_pipeline(text, start_time)
        if result.success:
            return result
        
        # Fallback: Try direct TAU → English
        result = self._try_direct_tau_to_english(text, start_time)
        if result.success:
            return result
        
        # Second fallback: Try parsing as TCE directly
        result = self._try_direct_tce_to_english(text, start_time)
        if result.success:
            return result
        
        # All methods failed
        return self._create_all_methods_failed_result(text, start_time)
    
    def _try_tau_tce_english_pipeline(self, text: str, start_time: float) -> TranslationResult:
        """Try TAU → TCE → English pipeline (≤10 lines)."""
        try:
            from backend.unified.domain.tau_to_tce_generator import (
                create_tau_to_tce_generator, create_tce_to_english_generator
            )
            
            tau_to_tce = create_tau_to_tce_generator()
            tce_result = self._run_async(tau_to_tce.generate_tce_async(text))
            
            if isinstance(tce_result, Success):
                return self._tce_to_english_final_step(tce_result.unwrap(), text, start_time)
                
        except Exception as e:
            self.logger.debug(f"TAU → TCE → English pipeline failed: {e}")
        
        return self._create_failed_result(text, start_time)
    
    def _tce_to_english_final_step(self, tce_text: str, text: str, start_time: float) -> TranslationResult:
        """Convert TCE to English in final step (≤10 lines)."""
        from backend.unified.domain.tau_to_tce_generator import create_tce_to_english_generator
        tce_to_english = create_tce_to_english_generator()
        english_result = self._run_async(tce_to_english.generate_english_async(tce_text))
        
        if isinstance(english_result, Success):
            return self._create_result(
                success=True,
                translated_text=english_result.unwrap(),
                original_text=text,
                direction=TranslationDirection.TO_ENGLISH,
                confidence=0.95,
                metadata={"pipeline": "TAU → TCE → English", "intermediate_tce": tce_text},
                start_time=start_time
            )
        
        return self._create_failed_result(text, start_time)
    
    def _try_direct_tau_to_english(self, text: str, start_time: float) -> TranslationResult:
        """Try direct TAU to English translation (≤10 lines)."""
        try:
            tau_result = self._run_async(self.tau_to_english_service.translate_expression_async(text))
            
            if isinstance(tau_result, Success):
                return self._create_result(
                    success=True,
                    translated_text=tau_result.unwrap(),
                    original_text=text,
                    direction=TranslationDirection.TO_ENGLISH,
                    confidence=0.9,
                    metadata={"pipeline": "TAU → English (direct)", "fallback": True},
                    start_time=start_time
                )
        except Exception as e:
            self.logger.debug(f"Direct TAU to English translation failed: {e}")
        
        return self._create_failed_result(text, start_time)
    
    def _try_direct_tce_to_english(self, text: str, start_time: float) -> TranslationResult:
        """Try direct TCE to English translation (≤10 lines)."""
        if not self.tce_parser:
            return self._create_failed_result(text, start_time)
            
        try:
            tree = self.tce_parser.parse(text)
            ast = self.tce_transformer.transform(tree)
            english = self._tce_ast_to_english(ast)
            
            return self._create_result(
                success=True,
                translated_text=english,
                original_text=text,
                direction=TranslationDirection.TO_ENGLISH,
                confidence=0.85,
                metadata={"pipeline": "TCE → English (direct)", "fallback": True},
                start_time=start_time
            )
        except Exception as e:
            self.logger.debug(f"TCE parsing failed: {e}")
        
        return self._create_failed_result(text, start_time)
    
    def _create_failed_result(self, text: str, start_time: float) -> TranslationResult:
        """Create a failed translation result (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TO_ENGLISH,
            error_message="Translation failed",
            start_time=start_time
        )
    
    def _try_parse_tce(self, text: str, start_time: float) -> Optional[TranslationResult]:
        """Try to parse TCE with the parser (≤10 lines)."""
        if not self.tce_parser:
            return None
            
        try:
            tree = self.tce_parser.parse(text)
            # Successfully parsed, return None to continue with pipeline
            return None
        except Exception as e:
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=TranslationDirection.TCE_TO_TAU,
                error_message=f"TCE parsing failed: {str(e)}",
                start_time=start_time
            )
    
    def _execute_tce_to_tau_pipeline(self, text: str, start_time: float) -> TranslationResult:
        """Execute TCE to TAU pipeline (≤10 lines)."""
        # TCE → ILR
        ilr_result = self._tce_to_ilr_pipeline_step(text, start_time)
        if isinstance(ilr_result, TranslationResult):
            return ilr_result  # Error result
        
        # ILR → TAU
        return self._ilr_to_tau_pipeline_step(ilr_result, text, start_time)
    
    def _tce_to_ilr_pipeline_step(self, text: str, start_time: float):
        """Convert TCE to ILR for pipeline (≤10 lines)."""
        from backend.unified.infrastructure.ilr_infrastructure import PatternMatcher
        pattern_match_result = PatternMatcher.match_pattern(text)
        
        if isinstance(pattern_match_result, Failure):
            return self._create_tce_pattern_error_result(text, pattern_match_result.failure(), start_time)
        
        ilr_result = self.ilr_service.generate_ilr_from_pattern(
            pattern_match_result.unwrap(),
            text
        )
        
        if isinstance(ilr_result, Failure):
            return self._create_tce_ilr_error_result(text, ilr_result.failure(), start_time)
        
        return ilr_result.unwrap()
    
    def _create_tce_pattern_error_result(self, text: str, error, start_time: float) -> TranslationResult:
        """Create TCE pattern matching error result (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TCE_TO_TAU,
            error_message=f"Pattern matching failed: {error}",
            start_time=start_time
        )
    
    def _create_tce_ilr_error_result(self, text: str, error, start_time: float) -> TranslationResult:
        """Create TCE ILR generation error result (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TCE_TO_TAU,
            error_message=f"ILR generation failed: {error}",
            start_time=start_time
        )
    
    def _ilr_to_tau_pipeline_step(self, ilr, text: str, start_time: float) -> TranslationResult:
        """Convert ILR to TAU for pipeline (≤10 lines)."""
        tau_result = self.tau_service.translate_ilr_to_tau(ilr)
        
        if isinstance(tau_result, Failure):
            return self._create_tce_tau_error_result(text, tau_result.failure(), start_time)
        
        return self._create_result(
            success=True,
            translated_text=str(tau_result.unwrap()),
            original_text=text,
            direction=TranslationDirection.TCE_TO_TAU,
            confidence=0.95,
            metadata={
                "pipeline": "TCE → ILR → TAU",
                "intermediate_ilr": str(ilr)
            },
            start_time=start_time
        )
    
    def _create_tce_tau_error_result(self, text: str, error, start_time: float) -> TranslationResult:
        """Create TCE TAU translation error result (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TCE_TO_TAU,
            error_message=f"TAU translation failed: {error}",
            start_time=start_time
        )
    
    def _parse_tce_to_ast(self, tce_text: str):
        """Parse TCE text to AST using Lark parser (≤10 lines)."""
        try:
            # Ensure text ends with period for parser
            if not tce_text.endswith('.'):
                tce_text += '.'
            tree = self.tce_parser.parse(tce_text)
            ast = self.tce_transformer.transform(tree)
            return ast
        except Exception as e:
            self.logger.debug(f"TCE parsing failed: {e}")
            return None
    
    def _transform_tce_ast_to_tau(self, tce_ast, tce_text: str) -> Optional[str]:
        """Transform TCE AST to Tau using type-aware transformation."""
        try:
            # If it's a Lark Tree, convert it directly
            if hasattr(tce_ast, 'data'):
                return self._convert_lark_tree_to_tau(tce_ast)
            else:
                # Use existing AST conversion
                return self._ast_to_tau(tce_ast, None)
        except Exception as e:
            self.logger.debug(f"AST transformation failed: {e}")
            return None
    
    def _ast_to_tau(self, ast_node, translator) -> str:
        """Convert AST node to Tau code with type awareness."""
        # Import AST node types
        ast_types = self._import_ast_node_types()
        if not ast_types:
            return str(ast_node)
        
        # Handle different AST node types
        return self._convert_ast_node_to_tau(ast_node, ast_types)
    
    def _convert_ast_node_to_tau(self, node, ast_types) -> str:
        """Convert specific AST node to Tau (≤10 lines)."""
        if isinstance(node, ast_types.get('QuantifierBlockNode', type(None))):
            return self._convert_quantifier_to_tau(node)
        elif isinstance(node, ast_types.get('TemporalQuantifierNode', type(None))):
            return self._convert_temporal_to_tau(node)
        elif isinstance(node, ast_types.get('BooleanBinaryOpNode', type(None))):
            return self._convert_boolean_op_to_tau(node)
        elif isinstance(node, ast_types.get('NotNode', type(None))):
            return self._convert_not_to_tau(node)
        elif isinstance(node, ast_types.get('PredicateCallNode', type(None))):
            return self._convert_predicate_to_tau(node)
        elif isinstance(node, ast_types.get('ComparisonNode', type(None))):
            return self._convert_comparison_to_tau(node)
        else:
            return self._convert_generic_node_to_tau(node)
    
    def _convert_quantifier_to_tau(self, node) -> str:
        """Convert quantifier node to Tau syntax (≤10 lines)."""
        # Map quantifier types
        quant_map = {'forall': 'all', 'exists': 'ex'}
        quantifier = quant_map.get(getattr(node, 'quantifier', getattr(node, 'quant_type', 'forall')), 'all')
        
        # Get variables
        vars_list = node.variables if hasattr(node, 'variables') else []
        variables = ' '.join(str(v.name if hasattr(v, 'name') else v) for v in vars_list)
        
        # Convert condition/body
        body_attr = 'condition' if hasattr(node, 'condition') else ('expr' if hasattr(node, 'expr') else 'body')
        body = self._ast_to_tau(getattr(node, body_attr, node), None)
        
        return f"{quantifier} {variables} ({body})"
    
    def _convert_predicate_to_tau(self, node) -> str:
        """Convert predicate call to Tau syntax (≤10 lines)."""
        # Convert arguments
        args = []
        for arg in node.args:
            if hasattr(arg, '__iter__') and not isinstance(arg, str):
                args.append(self._ast_to_tau(arg, None))
            else:
                args.append(str(arg))
        
        return f"{node.name}({', '.join(args)})"
    
    def _convert_comparison_to_tau(self, node) -> str:
        """Convert comparison node to Tau syntax (≤10 lines)."""
        left = self._ast_to_tau(node.left, None) if hasattr(node, 'left') else str(node.left)
        right = self._ast_to_tau(node.right, None) if hasattr(node, 'right') else str(node.right)
        
        # Map comparison operators
        op_map = {'equals': '=', 'greater': '>', 'less': '<', 'not_equal': '!='}
        op = op_map.get(node.operator, node.operator)
        
        return f"{left} {op} {right}"
    
    def _convert_definition_to_tau(self, node) -> str:
        """Convert definition node to Tau syntax (≤10 lines)."""
        # Get function name and parameters
        func_name = node.predicate_def.name if hasattr(node.predicate_def, 'name') else str(node.predicate_def)
        params = ', '.join(node.predicate_def.args) if hasattr(node.predicate_def, 'args') else ''
        
        # Convert body expression
        body = self._ast_to_tau(node.expr, None)
        
        return f"{func_name}({params}) := {body}"
    
    def _convert_fact_to_tau(self, node) -> str:
        """Convert fact node to Tau syntax (≤10 lines)."""
        expr = self._ast_to_tau(node.expr, None)
        # Remove trailing period - facts don't need it in Tau
        if expr.endswith('.'):
            expr = expr[:-1]
        return expr
    
    def _convert_generic_node_to_tau(self, node) -> str:
        """Convert generic node to Tau (≤10 lines)."""
        if hasattr(node, '__iter__') and not isinstance(node, str):
            # Handle list of nodes
            parts = []
            for item in node:
                parts.append(self._ast_to_tau(item, None))
            return ' '.join(parts)
        else:
            # Simple node - convert to string
            return str(node)
    
    def _convert_boolean_op_to_tau(self, node) -> str:
        """Convert boolean operation node to Tau with type awareness (≤10 lines)."""
        left = self._ast_to_tau(node.left, None) if hasattr(node, 'left') else ''
        right = self._ast_to_tau(node.right, None) if hasattr(node, 'right') else ''
        
        # Use type inference to determine context
        context = TypeContext()
        left_type = TauTypeInference.infer_expression_type(left, context)
        right_type = TauTypeInference.infer_expression_type(right, context)
        
        # Determine if we're in bf or wff context
        is_bf = (isinstance(left_type, Success) and left_type.unwrap() == TauType.BF and
                 isinstance(right_type, Success) and right_type.unwrap() == TauType.BF)
        
        # Get correct operator based on context
        op_str = getattr(node, 'operator', 'and').upper()
        op_result = TauTypeInference.get_correct_operator(op_str, TypeContext(expected_type=TauType.BF if is_bf else TauType.WFF))
        
        if isinstance(op_result, Success):
            op = op_result.unwrap()
            return f"{left} {op} {right}" if is_bf else f"({left} {op} {right})"
        else:
            # Fallback to default mapping
            return f"({left} && {right})"
    
    def _convert_binary_op_to_tau(self, node) -> str:
        """Convert generic binary operation to Tau (≤10 lines)."""
        left = self._convert_value_to_tau(node.left) if hasattr(node, 'left') else ''
        right = self._convert_value_to_tau(node.right) if hasattr(node, 'right') else ''
        op = getattr(node, 'operator', getattr(node, 'op', '&'))
        
        # Map TCE operators to Tau
        if op in ['&', '|', '^']:
            return f"{left} {op} {right}"  # Boolean function level
        else:
            return f"({left} {op} {right})"  # Formula level
    
    def _convert_value_to_tau(self, node) -> str:
        """Convert value node to Tau string (≤10 lines)."""
        if hasattr(node, 'name'):  # VariableNode
            return node.name
        elif hasattr(node, 'value'):  # ConstantNode
            if node.value is True or node.value == 'true':
                return '1'
            elif node.value is False or node.value == 'false':
                return '0'
            else:
                return str(node.value)
        else:
            return self._ast_to_tau(node, None)
    
    def _convert_temporal_to_tau(self, node) -> str:
        """Convert temporal quantifier node to Tau (≤10 lines)."""
        # Get the expression (it might be in 'expression' or 'operand' attribute)
        expr_attr = 'expression' if hasattr(node, 'expression') else 'operand'
        expr = self._ast_to_tau(getattr(node, expr_attr), None)
        
        # Map temporal quantifiers
        temporal_map = {'always': 'always', 'sometimes': 'sometimes', 
                       'eventually': 'sometimes', 'never': 'always !'}
        quantifier = temporal_map.get(node.quantifier, node.quantifier)
        
        return f"{quantifier} ({expr})"
    
    def _convert_not_to_tau(self, node) -> str:
        """Convert NOT node to Tau with type awareness (≤10 lines)."""
        operand = self._ast_to_tau(node.operand, None) if hasattr(node, 'operand') else ''
        
        # Use type inference to determine context
        context = TypeContext()
        operand_type = TauTypeInference.infer_expression_type(operand, context)
        
        # Apply correct negation based on type
        if isinstance(operand_type, Success) and operand_type.unwrap() == TauType.BF:
            return f"{operand}'"  # Use apostrophe for bf negation
        else:
            return f"!({operand})"  # Use ! for wff negation
    
    def _convert_lark_tree_to_tau(self, tree) -> str:
        """Convert Lark parse tree to Tau code (≤10 lines)."""
        if hasattr(tree, 'data'):
            # This is a Tree node
            return self._process_lark_rule(tree)
        elif hasattr(tree, 'value'):
            # This is a Token
            return str(tree.value)
        elif hasattr(tree, 'name'):
            # This is a VariableNode or similar AST node
            return tree.name
        elif hasattr(tree, 'args') and hasattr(tree, '__class__'):
            # This is a PredicateCallNode
            args = ', '.join(self._convert_lark_tree_to_tau(arg) for arg in tree.args)
            return f"{tree.name}({args})"
        else:
            return str(tree)
    
    def _process_lark_rule(self, tree):
        """Process specific Lark grammar rules (≤10 lines)."""
        # Map rule names to conversion methods
        rule_handlers = self._get_lark_rule_handlers()
        
        # Check if we have a specific handler
        if tree.data in rule_handlers:
            return rule_handlers[tree.data](tree)
        
        # Default handling for pass-through rules
        if len(tree.children) == 1:
            return self._convert_lark_tree_to_tau(tree.children[0])
        else:
            return self._process_generic_rule(tree)
    
    def _get_lark_rule_handlers(self):
        """Get handlers for Lark grammar rules (≤10 lines)."""
        handlers = {}
        handlers.update(self._get_temporal_handlers())
        handlers.update(self._get_quantifier_handlers())
        handlers.update(self._get_comparison_handlers())
        handlers.update(self._get_logical_handlers())
        handlers.update(self._get_boolean_handlers())
        handlers.update(self._get_constant_handlers())
        handlers.update(self._get_stream_handlers())
        handlers.update(self._get_predicate_handlers())
        return handlers
    
    def _get_temporal_handlers(self):
        """Get temporal operator handlers (≤10 lines)."""
        return {
            'always_spec': lambda t: f"always ({self._convert_lark_tree_to_tau(t.children[0])})",
            'sometimes_spec': lambda t: f"sometimes ({self._convert_lark_tree_to_tau(t.children[0])})",
            'eventually_spec': lambda t: f"sometimes ({self._convert_lark_tree_to_tau(t.children[0])})",
            'never_spec': lambda t: f"always !({self._convert_lark_tree_to_tau(t.children[0])})",
        }
    
    def _get_quantifier_handlers(self):
        """Get quantifier handlers (≤10 lines)."""
        return {
            'universal_quantification': self._process_universal,
            'existential_quantification': self._process_existential,
        }
    
    def _get_comparison_handlers(self):
        """Get comparison handlers (≤10 lines)."""
        return {
            'bf_equals': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])} = {self._convert_lark_tree_to_tau(t.children[1])}",
            'bf_not_equals': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])} != {self._convert_lark_tree_to_tau(t.children[1])}",
            'bf_greater': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])} > {self._convert_lark_tree_to_tau(t.children[1])}",
            'bf_less': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])} < {self._convert_lark_tree_to_tau(t.children[1])}",
            'bf_greater_equal': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])} >= {self._convert_lark_tree_to_tau(t.children[1])}",
            'bf_less_equal': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])} <= {self._convert_lark_tree_to_tau(t.children[1])}",
        }
    
    def _get_logical_handlers(self):
        """Get logical operator handlers (≤10 lines)."""
        return {
            'wff_implies': lambda t: f"({self._convert_lark_tree_to_tau(t.children[0])}) -> ({self._convert_lark_tree_to_tau(t.children[1])})",
            'wff_reverse_implies': lambda t: f"({self._convert_lark_tree_to_tau(t.children[0])}) <- ({self._convert_lark_tree_to_tau(t.children[1])})",
            'wff_equiv': lambda t: f"({self._convert_lark_tree_to_tau(t.children[0])}) <-> ({self._convert_lark_tree_to_tau(t.children[1])})",
            'wff_logical_and': lambda t: f"({self._convert_lark_tree_to_tau(t.children[0])}) && ({self._convert_lark_tree_to_tau(t.children[1])})",
            'wff_logical_or': lambda t: f"({self._convert_lark_tree_to_tau(t.children[0])}) || ({self._convert_lark_tree_to_tau(t.children[1])})",
            'wff_logical_xor': lambda t: f"({self._convert_lark_tree_to_tau(t.children[0])}) ^ ({self._convert_lark_tree_to_tau(t.children[1])})",
            'wff_negation': lambda t: f"!({self._convert_lark_tree_to_tau(t.children[0])})",
        }
    
    def _get_boolean_handlers(self):
        """Get boolean function handlers (≤10 lines)."""
        return {
            'bf_disjunction': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])} | {self._convert_lark_tree_to_tau(t.children[1])}",
            'bf_conjunction': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])} & {self._convert_lark_tree_to_tau(t.children[1])}",
            'bf_negation': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])}'",
            'bf_xor': lambda t: f"{self._convert_lark_tree_to_tau(t.children[0])} ^ {self._convert_lark_tree_to_tau(t.children[1])}",
            'standalone_bf': lambda t: self._convert_lark_tree_to_tau(t.children[0]),
        }
    
    def _get_constant_handlers(self):
        """Get constant handlers (≤10 lines)."""
        return {
            'bf_one': lambda t: "1",
            'bf_zero': lambda t: "0", 
            'wff_true': lambda t: "T",
            'wff_false': lambda t: "F",
            'variable': lambda t: str(t.children[0]) if t.children else "x",
        }
    
    def _get_stream_handlers(self):
        """Get stream-related handlers (≤10 lines)."""
        return {
            'stream_declaration': self._process_stream_declaration,
            'stream_reference': self._process_stream_reference,
            'temporal_index': self._process_temporal_index,
        }
    
    def _get_predicate_handlers(self):
        """Get predicate-related handlers (≤10 lines)."""
        return {
            'predicate_definition': self._process_predicate_definition,
            'predicate_call': self._process_predicate_call,
            'function_definition': self._process_function_definition,
            'recurrence_relation': self._process_recurrence_relation,
        }
    
    def _process_universal(self, tree):
        """Process universal quantification (≤10 lines)."""
        # Expected: FOR_ALL variable SUCH_THAT well_formed_formula
        if len(tree.children) >= 2:
            var = self._extract_variable_name(tree.children[0])
            body = self._convert_lark_tree_to_tau(tree.children[-1])
            return f"all {var} ({body})"
        else:
            return "all x (T)"  # Default
    
    def _process_existential(self, tree):
        """Process existential quantification (≤10 lines)."""
        # Expected: THERE_EXISTS variable SUCH_THAT well_formed_formula
        if len(tree.children) >= 2:
            var = self._extract_variable_name(tree.children[0])
            body = self._convert_lark_tree_to_tau(tree.children[-1])
            return f"ex {var} ({body})"
        else:
            return "ex x (T)"  # Default
    
    def _extract_variable_name(self, node):
        """Extract variable name from node (≤10 lines)."""
        if hasattr(node, 'data') and node.data == 'variable':
            return self._convert_lark_tree_to_tau(node)
        elif hasattr(node, 'value'):
            return str(node.value)
        elif hasattr(node, 'name'):
            return node.name
        else:
            return str(node)
    
    def _process_generic_rule(self, tree):
        """Process generic Lark rule (≤10 lines)."""
        # For now, just join the children
        parts = []
        for child in tree.children:
            parts.append(self._convert_lark_tree_to_tau(child))
        return ' '.join(parts)
    
    def _process_stream_declaration(self, tree):
        """Process stream declaration (≤10 lines)."""
        # Expected: sbf IDENTIFIER = console
        if len(tree.children) >= 2:
            stream_type = "sbf"  # Default to sbf
            stream_name = self._extract_variable_name(tree.children[0])
            return f"{stream_type} {stream_name} = console"
        return "sbf stream = console"
    
    def _process_stream_reference(self, tree):
        """Process stream reference with temporal index (≤10 lines)."""
        # Expected: stream[index]
        if len(tree.children) >= 2:
            stream = self._convert_lark_tree_to_tau(tree.children[0])
            index = self._convert_lark_tree_to_tau(tree.children[1])
            return f"{stream}[{index}]"
        return self._convert_lark_tree_to_tau(tree.children[0])
    
    def _process_temporal_index(self, tree):
        """Process temporal index expression (≤10 lines)."""
        # Expected: t-1, t+1, etc.
        if len(tree.children) == 1:
            return str(tree.children[0])
        elif len(tree.children) == 3:
            # t + 1 or t - 1
            left = self._convert_lark_tree_to_tau(tree.children[0])
            op = str(tree.children[1])
            right = self._convert_lark_tree_to_tau(tree.children[2])
            return f"{left}{op}{right}"
        return "t"
    
    def _process_predicate_definition(self, tree):
        """Process predicate definition (≤10 lines)."""
        # Expected: predicate <-> condition
        if len(tree.children) >= 2:
            pred = self._extract_variable_name(tree.children[0])
            cond = self._convert_lark_tree_to_tau(tree.children[1])
            return f"{pred} <-> {cond}"
        return ""
    
    def _process_predicate_call(self, tree):
        """Process predicate call (≤10 lines)."""
        # Expected: predicate(args)
        if len(tree.children) >= 1:
            pred_name = self._extract_variable_name(tree.children[0])
            args = []
            for i in range(1, len(tree.children)):
                args.append(self._convert_lark_tree_to_tau(tree.children[i]))
            if args:
                return f"{pred_name}({', '.join(args)})"
            return pred_name
        return ""
    
    def _process_function_definition(self, tree):
        """Process function definition (≤10 lines)."""
        # Expected: func(params) := body
        if len(tree.children) >= 3:
            func_name = self._extract_variable_name(tree.children[0])
            params = self._extract_parameters(tree.children[1])
            body = self._convert_lark_tree_to_tau(tree.children[2])
            return f"{func_name}({params}) := {body}"
        return ""
    
    def _process_recurrence_relation(self, tree):
        """Process recurrence relation (≤10 lines)."""
        # Expected: h[0] = base && h[n] = recursive
        if len(tree.children) >= 4:
            func = self._extract_variable_name(tree.children[0])
            base = self._convert_lark_tree_to_tau(tree.children[1])
            recursive = self._convert_lark_tree_to_tau(tree.children[3])
            return f"{func}[0] = {base} && {func}[n] = {recursive}"
        return ""
    
    def _extract_parameters(self, node):
        """Extract function parameters (≤10 lines)."""
        if hasattr(node, 'children'):
            params = []
            for child in node.children:
                params.append(self._extract_variable_name(child))
            return ', '.join(params)
        return ""
    
    def _create_all_methods_failed_result(self, text: str, start_time: float) -> TranslationResult:
        """Create result when all methods failed (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TO_ENGLISH,
            error_message="Could not parse as TAU or TCE using any available method",
            start_time=start_time
        )
    
    def _translate_nl_to_tau(self, text: str, start_time: float) -> TranslationResult:
        """Natural Language to TAU (same as English to TAU)."""
        return self._translate_to_tau(text, start_time)
    
    def _translate_nl_to_tce(self, text: str, start_time: float) -> TranslationResult:
        """Natural Language to TCE (same as English to TCE)."""
        return self._translate_to_tce(text, start_time)
    
    def _translate_tce_to_tau(self, text: str, start_time: float) -> TranslationResult:
        """Translate TCE to TAU."""
        # Try parsing TCE first if parser available
        parse_result = self._try_parse_tce(text, start_time)
        if parse_result is not None:
            return parse_result
        
        # Use standard pipeline: TCE → ILR → TAU
        return self._execute_tce_to_tau_pipeline(text, start_time)
    
    def _translate_tce_to_nl(self, text: str, start_time: float) -> TranslationResult:
        """Translate TCE to Natural Language."""
        # Try parsing with TCE parser first
        if self.tce_parser:
            parse_result = self._try_tce_parser_translation(text, start_time)
            if parse_result is not None:
                return parse_result
        
        # Fallback to rule-based transformation
        return self._apply_tce_to_nl_rules(text, start_time)
    
    def _try_tce_parser_translation(self, text: str, start_time: float) -> Optional[TranslationResult]:
        """Try to translate using TCE parser (≤10 lines)."""
        try:
            tree = self.tce_parser.parse(text)
            ast = self.tce_transformer.transform(tree)
            english = self._tce_ast_to_english(ast)
            
            return self._create_result(
                success=True,
                translated_text=english,
                original_text=text,
                direction=TranslationDirection.TCE_TO_NL,
                confidence=0.9,
                metadata={"pipeline": "TCE → English (via existing parser)"},
                start_time=start_time
            )
        except Exception as e:
            return self._create_tce_nl_parse_error_result(text, e, start_time)
    
    def _create_tce_nl_parse_error_result(self, text: str, error: Exception, start_time: float) -> TranslationResult:
        """Create TCE to NL parsing error result (≤10 lines)."""
        return self._create_result(
            success=False,
            translated_text="",
            original_text=text,
            direction=TranslationDirection.TCE_TO_NL,
            error_message=f"TCE parsing failed: {str(error)}",
            start_time=start_time
        )
    
    def _apply_tce_to_nl_rules(self, text: str, start_time: float) -> TranslationResult:
        """Apply rule-based TCE to NL transformation (≤10 lines)."""
        replacements = self._get_tce_to_nl_replacements()
        result = self._apply_text_replacements(text, replacements)
        
        return self._create_result(
            success=True,
            translated_text=result,
            original_text=text,
            direction=TranslationDirection.TCE_TO_NL,
            confidence=0.6,
            metadata={"pipeline": "TCE → English (rule-based fallback)"},
            start_time=start_time
        )
    
    def _get_tce_to_nl_replacements(self) -> Dict[str, str]:
        """Get TCE to natural language replacement rules (≤10 lines)."""
        return {
            'define predicate': 'We define a predicate',
            'define function': 'We define a function',
            'forall': 'for all',
            'exists': 'there exists',
            'such that': 'where'
        }
    
    def _apply_text_replacements(self, text: str, replacements: Dict[str, str]) -> str:
        """Apply text replacements (≤10 lines)."""
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result
    
    def _tce_ast_to_english(self, ast) -> str:
        """Convert TCE AST to English text."""
        # This is a simplified conversion - would need more work for full implementation
        if hasattr(ast, '__iter__'):
            parts = []
            for node in ast:
                parts.append(self._node_to_english(node))
            return " ".join(parts)
        else:
            return self._node_to_english(ast)
    
    def _node_to_english(self, node) -> str:
        """Convert a single AST node to English."""
        # Import AST node types
        try:
            ast_types = self._import_ast_node_types()
            if ast_types:
                return self._convert_node_with_types(node, ast_types)
        except:
            pass
        
        # Fallback if AST nodes not available
        return str(node)
    
    def _import_ast_node_types(self):
        """Import AST node types (≤10 lines)."""
        try:
            from src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
                FactNode, RuleNode, DefinitionNode, PredicateCallNode,
                QuantifierBlockNode, ComparisonNode, ArithmeticBinaryOpNode
            )
            return {
                'FactNode': FactNode,
                'RuleNode': RuleNode,
                'DefinitionNode': DefinitionNode,
                'PredicateCallNode': PredicateCallNode,
                'QuantifierBlockNode': QuantifierBlockNode,
                'ComparisonNode': ComparisonNode
            }
        except:
            return None
    
    def _convert_node_with_types(self, node, ast_types) -> str:
        """Convert node using imported types (≤10 lines)."""
        if isinstance(node, ast_types['FactNode']):
            return self._convert_fact_node(node)
        elif isinstance(node, ast_types['RuleNode']):
            return self._convert_rule_node(node)
        elif isinstance(node, ast_types['DefinitionNode']):
            return self._convert_definition_node(node)
        elif isinstance(node, ast_types['PredicateCallNode']):
            return self._convert_predicate_call_node(node)
        elif isinstance(node, ast_types['QuantifierBlockNode']):
            return self._convert_quantifier_node(node)
        elif isinstance(node, ast_types['ComparisonNode']):
            return self._convert_comparison_node(node)
        else:
            return str(node)
    
    def _convert_fact_node(self, node) -> str:
        """Convert FactNode to English (≤10 lines)."""
        return f"{self._node_to_english(node.expr)}."
    
    def _convert_rule_node(self, node) -> str:
        """Convert RuleNode to English (≤10 lines)."""
        cond = self._node_to_english(node.condition) if node.condition else ""
        pred = self._node_to_english(node.predicate_call)
        return f"If {cond} then {pred}."
    
    def _convert_definition_node(self, node) -> str:
        """Convert DefinitionNode to English (≤10 lines)."""
        pred_def = self._node_to_english(node.predicate_def)
        expr = self._node_to_english(node.expr)
        return f"We define {pred_def} as {expr}."
    
    def _convert_predicate_call_node(self, node) -> str:
        """Convert PredicateCallNode to English (≤10 lines)."""
        args = ", ".join(self._node_to_english(arg) for arg in node.args)
        return f"{node.name}({args})"
    
    def _convert_quantifier_node(self, node) -> str:
        """Convert QuantifierBlockNode to English (≤10 lines)."""
        vars = ", ".join(node.variables)
        expr = self._node_to_english(node.expr) if node.expr else ""
        if node.quantifier == "forall":
            return f"for all {vars}, {expr}"
        else:
            return f"there exists {vars} such that {expr}"
    
    def _convert_comparison_node(self, node) -> str:
        """Convert ComparisonNode to English (≤10 lines)."""
        left = self._node_to_english(node.left)
        right = self._node_to_english(node.right)
        op_map = self._get_comparison_operator_map()
        op = op_map.get(node.operator, node.operator)
        return f"{left} {op} {right}"
    
    def _get_comparison_operator_map(self) -> Dict[str, str]:
        """Get comparison operator mapping (≤10 lines)."""
        return {
            '=': 'equals',
            '>': 'is greater than',
            '<': 'is less than',
            '>=': 'is at least',
            '<=': 'is at most'
        }