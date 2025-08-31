"""
NLP-enhanced translation engine.

Integrates NLP features with complex English parsing capabilities.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional
from .base import TranslationEngine, TranslationResult, TranslationDirection
from backend.unified.domain.enhanced_nlp_service import create_enhanced_nlp_service
from backend.unified.domain.complex_english_parser import ComplexEnglishParser
from backend.unified.domain.tau_to_english_translator import TauToEnglishTranslator
from backend.unified.core.domain_types import SourceText
import logging

logger = logging.getLogger(__name__)


class NLPTranslationEngine(TranslationEngine):
    """NLP-enhanced translation engine with complex parsing capabilities."""
    
    def __init__(self):
        super().__init__(
            name="nlp_enhanced",
            description="NLP-enhanced translation with complex English parsing and validation"
        )
        
        # Initialize NLP components
        try:
            self.nlp_service = create_enhanced_nlp_service()
            self.complex_parser = ComplexEnglishParser()
            self.tau_to_english = TauToEnglishTranslator()
            self.is_available = True
            self.last_error = None
            logger.info("NLP translation engine initialized successfully")
        except Exception as e:
            self.is_available = False
            self.last_error = f"Could not initialize NLP translator: {e}"
            logger.error(f"Failed to initialize NLP translator: {e}")
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the translation."""
        if not self.is_available:
            return False
            
        # Analyze text complexity to determine capability
        try:
            complexity = self.nlp_service.analyze_complexity(text)
            complexity_level = complexity.get('complexity_level', 'simple')
            
            # Can handle all complexity levels
            can_handle = True
            
            # Log capability decision
            logger.debug(f"NLP engine can_translate: {can_handle} for complexity: {complexity_level}")
            return can_handle
            
        except Exception as e:
            logger.error(f"Error analyzing text capability: {e}")
            return False
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get supported translation directions."""
        return [
            TranslationDirection.TO_TAU, 
            TranslationDirection.TO_TCE,
            TranslationDirection.TO_ENGLISH
        ]
    
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Perform NLP-enhanced translation."""
        import time
        start_time = time.time()
        
        if not self.is_available:
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message=self.last_error or "NLP engine not available",
                start_time=start_time
            )
        
        try:
            source_text = SourceText(text=text)
            translated_text = ""
            
            if direction == TranslationDirection.TO_TAU:
                # English to TAU
                result = self.nlp_service.translate_to_tau(source_text)
                if result.is_success():
                    translated_text = result.unwrap()
                else:
                    # Try via TCE path
                    tce_result = self.nlp_service.translate_to_tce(source_text)
                    if tce_result.is_success():
                        # Convert TCE to TAU (simplified for now)
                        tce_expr = tce_result.unwrap()
                        translated_text = self._tce_to_tau_simple(tce_expr.expression)
                    else:
                        raise Exception(f"Translation failed: {result.failure()}")
                        
            elif direction == TranslationDirection.TO_TCE:
                # English to TCE
                result = self.nlp_service.translate_to_tce(source_text)
                if result.is_success():
                    translated_text = result.unwrap().expression
                else:
                    raise Exception(f"Translation failed: {result.failure()}")
                    
            elif direction == TranslationDirection.TO_ENGLISH:
                # TAU to English
                if self._looks_like_tau(text):
                    translated_text = self.tau_to_english.translate(text)
                else:
                    # Assume it's already English or TCE
                    translated_text = text
                    
            else:
                raise ValueError(f"Unsupported direction: {direction}")
            
            return self._create_result(
                success=True,
                translated_text=translated_text,
                original_text=text,
                direction=direction,
                start_time=start_time,
                confidence=0.9  # High confidence with NLP engine
            )
            
        except Exception as e:
            logger.error(f"NLP translation error: {e}")
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message=str(e),
                start_time=start_time
            )
    
    def _tce_to_tau_simple(self, tce_text: str) -> str:
        """Simple TCE to TAU conversion."""
        tau = tce_text
        
        # Basic conversions
        conversions = [
            ('forall ', '∀'),
            ('exists ', '∃'),
            ('such that', ':'),
            (' implies ', ' → '),
            (' and ', ' ∧ '),
            (' or ', ' ∨ '),
            ('not ', '¬'),
        ]
        
        for old, new in conversions:
            tau = tau.replace(old, new)
        
        # Handle quantifier variables
        import re
        tau = re.sub(r'∀\s+(\w+):', r'∀\1:', tau)
        tau = re.sub(r'∃\s+(\w+):', r'∃\1:', tau)
        
        return tau
    
    def _looks_like_tau(self, text: str) -> bool:
        """Check if text appears to be TAU formula."""
        tau_indicators = ['∀', '∃', '→', '∧', '∨', '¬', '⊢', '⊨']
        return any(indicator in text for indicator in tau_indicators)