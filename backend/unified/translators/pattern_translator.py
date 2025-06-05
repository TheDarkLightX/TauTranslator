"""
Pattern-based translation engine.

Implements simple pattern-based translation as a fallback mechanism.
Consolidates pattern-based logic from multiple backend files.

Author: DarkLightX / Dana Edwards
"""

import re
import time
from typing import List
from .base import TranslationEngine, TranslationResult, TranslationDirection


class PatternTranslationEngine(TranslationEngine):
    """Simple pattern-based translation engine."""
    
    def __init__(self):
        super().__init__(
            name="pattern_based",
            description="Simple pattern-based translation with regex rules"
        )
        
        # Pattern mappings from the original backend files
        self.tce_to_tau_patterns = [
            (r'\band\b', '&'),
            (r'\bor\b', '|'),
            (r'\bnot\b', '!'),
            (r'\bequals\b', '='),
            (r'\bplus\b', '+'),
            (r'\bminus\b', '-'),
            (r'\btimes\b', '*'),
            (r'\bdivided by\b', '/'),
            (r'\bthe\b', ''),
            (r'\bat time (\w+)', r'[\1]'),
            (r'\s+', ' ')
        ]
        
        self.tau_to_tce_patterns = [
            (r'&', ' and '),
            (r'\|', ' or '),
            (r'!', ' not '),
            (r'=', ' equals '),
            (r'\+', ' plus '),
            (r'-', ' minus '),
            (r'\*', ' times '),
            (r'/', ' divided by '),
            (r'\[(\w+)\]', r' at time \1'),
            (r'\s+', ' ')
        ]
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the translation."""
        if not self.validate_input(text):
            return False
        
        # This engine can handle basic TCE <-> Tau conversions
        return direction in [TranslationDirection.TO_TAU, TranslationDirection.TO_TCE]
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Get supported translation directions."""
        return [TranslationDirection.TO_TAU, TranslationDirection.TO_TCE]
    
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Perform pattern-based translation."""
        start_time = time.time()
        
        if not self.can_translate(text, direction):
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message="Pattern engine cannot handle this translation",
                start_time=start_time
            )
        
        try:
            if direction == TranslationDirection.TO_TAU:
                translated_text = self._apply_patterns(text.lower(), self.tce_to_tau_patterns)
            elif direction == TranslationDirection.TO_TCE:
                translated_text = self._apply_patterns(text, self.tau_to_tce_patterns)
            else:
                return self._create_result(
                    success=False,
                    translated_text="",
                    original_text=text,
                    direction=direction,
                    error_message=f"Direction {direction.value} not supported",
                    start_time=start_time
                )
            
            # Clean up the result
            translated_text = self._clean_translation(translated_text)
            
            # Calculate confidence based on how much the text changed
            confidence = self._calculate_confidence(text, translated_text)
            
            return self._create_result(
                success=True,
                translated_text=translated_text,
                original_text=text,
                direction=direction,
                confidence=confidence,
                metadata={
                    "patterns_applied": len(self._get_patterns_for_direction(direction)),
                    "engine_type": "pattern_based"
                },
                start_time=start_time
            )
            
        except Exception as e:
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message=f"Pattern translation failed: {str(e)}",
                start_time=start_time
            )
    
    def _apply_patterns(self, text: str, patterns: List[tuple]) -> str:
        """Apply a list of regex patterns to text."""
        result = text
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
    
    def _clean_translation(self, text: str) -> str:
        """Clean up the translated text."""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing spaces
        text = text.strip()
        # Remove spaces around operators
        text = re.sub(r'\s*([&|!+=\-*/])\s*', r'\1', text)
        return text
    
    def _calculate_confidence(self, original: str, translated: str) -> float:
        """Calculate confidence score based on translation quality."""
        if not translated:
            return 0.0
        
        # Simple heuristic: more changes usually mean better translation
        # but avoid giving high confidence to very short outputs
        original_words = len(original.split())
        translated_words = len(translated.split())
        
        if translated_words == 0:
            return 0.0
        
        # Base confidence on word count ratio and presence of operators
        word_ratio = min(translated_words / max(original_words, 1), 1.0)
        
        # Boost confidence if we have operators (suggests successful pattern matching)
        has_operators = bool(re.search(r'[&|!+=\-*/\[\]]', translated))
        operator_boost = 0.2 if has_operators else 0.0
        
        confidence = (word_ratio * 0.6) + 0.2 + operator_boost
        return min(confidence, 0.95)  # Cap at 95% for pattern-based translation
    
    def _get_patterns_for_direction(self, direction: TranslationDirection) -> List[tuple]:
        """Get patterns for a specific direction."""
        if direction == TranslationDirection.TO_TAU:
            return self.tce_to_tau_patterns
        elif direction == TranslationDirection.TO_TCE:
            return self.tau_to_tce_patterns
        return []