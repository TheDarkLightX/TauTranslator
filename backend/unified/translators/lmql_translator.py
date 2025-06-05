"""
LMQL-based translation engine.

Integrates the LMQL bidirectional translator from the original backends.

Author: DarkLightX / Dana Edwards
"""

import sys
from pathlib import Path
from typing import List
from .base import TranslationEngine, TranslationResult, TranslationDirection, CachingEngine

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class LMQLTranslationEngine(CachingEngine):
    """LMQL-based translation engine with caching."""
    
    def __init__(self):
        super().__init__(
            name="lmql_bidirectional",
            description="LMQL-based bidirectional translator",
            cache_size=50
        )
        
        # Try to import and initialize LMQL translator
        try:
            from src.tau_translator_omega.lmql_engine.bidirectional_translator import BidirectionalTranslator
            self.translator = BidirectionalTranslator()
            self.is_available = True
        except Exception as e:
            self.translator = None
            self.is_available = False
            self.last_error = f"Could not initialize LMQL translator: {e}"
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the translation."""
        if not self.is_available or not self.validate_input(text):
            return False
        
        # LMQL translator can handle bidirectional translation
        return direction in self.get_supported_directions()
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get supported translation directions."""
        return [
            TranslationDirection.TO_TAU,
            TranslationDirection.TO_TCE,
            TranslationDirection.BIDIRECTIONAL
        ]
    
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Perform LMQL-based translation."""
        import time
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(text, direction, **kwargs)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        if not self.can_translate(text, direction):
            result = self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message="LMQL engine not available or cannot handle this translation",
                start_time=start_time
            )
            return result
        
        try:
            # Use the LMQL translator
            if direction == TranslationDirection.TO_TAU:
                translated_text = self.translator.translate_to_tau(text)
            elif direction == TranslationDirection.TO_TCE:
                translated_text = self.translator.translate_to_tce(text)
            else:  # BIDIRECTIONAL
                # For bidirectional, detect the input type and translate accordingly
                if self._looks_like_tau(text):
                    translated_text = self.translator.translate_to_tce(text)
                else:
                    translated_text = self.translator.translate_to_tau(text)
            
            # Calculate confidence (LMQL is usually high quality)
            confidence = 0.85 if translated_text and translated_text != text else 0.3
            
            result = self._create_result(
                success=True,
                translated_text=translated_text,
                original_text=text,
                direction=direction,
                confidence=confidence,
                metadata={
                    "engine_type": "lmql_bidirectional",
                    "cache_hit": False
                },
                start_time=start_time
            )
            
            # Store in cache
            self._store_in_cache(cache_key, result)
            return result
            
        except Exception as e:
            result = self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message=f"LMQL translation failed: {str(e)}",
                start_time=start_time
            )
            return result
    
    def _looks_like_tau(self, text: str) -> bool:
        """Heuristic to detect if text looks like Tau syntax."""
        tau_indicators = ['[', ']', ':=', '&', '|', '!']
        return any(indicator in text for indicator in tau_indicators)