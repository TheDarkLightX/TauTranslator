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
                # Apply patterns with smart case normalization 
                translated_text = self._apply_patterns_normalize_ascii_case(text, self.tce_to_tau_patterns)
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
            translated_text = self._clean_translation(translated_text, direction)
            
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
    
    def _apply_patterns_normalize_ascii_case(self, text: str, patterns: List[tuple]) -> str:
        """Apply patterns and normalize ASCII letters to lowercase while preserving unicode."""
        result = text
        
        # Apply patterns case-insensitively
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Normalize ASCII identifiers to lowercase while preserving unicode and operators
        # Split on operators and spaces, then process each part
        def normalize_token(token):
            # If it's a pure ASCII identifier, lowercase it
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token) and token.isascii():
                return token.lower()
            else:
                # Keep operators, numbers, unicode, etc. as-is
                return token
        
        # Split on operators and spaces, process each part, then rejoin
        # Use regex to split while keeping delimiters
        # Split more carefully to avoid regex issues
        tokens = re.split(r'([&|=!+*\/\[\]\s-]+)', result)
        normalized_tokens = [normalize_token(token) for token in tokens if token]
        
        return ''.join(normalized_tokens)
    
    def _apply_patterns_preserve_case(self, text: str, patterns: List[tuple]) -> str:
        """Apply patterns case-insensitively but preserve case of identifiers."""
        result = text
        
        # Create a mapping to preserve original case of identifiers
        import re
        words = re.findall(r'\b\w+\b', text)
        word_map = {word.lower(): word for word in words}
        
        for pattern, replacement in patterns:
            # Apply pattern case-insensitively
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Restore original case for identifiers that weren't keywords
        for lower_word, original_word in word_map.items():
            if lower_word not in ['and', 'or', 'not', 'equals', 'plus', 'minus', 'times', 'divided', 'by', 'the', 'at', 'time']:
                # Only replace if it's a standalone word
                result = re.sub(r'\b' + re.escape(lower_word) + r'\b', original_word, result, flags=re.IGNORECASE)
        
        return result
    
    def _clean_translation(self, text: str, direction: TranslationDirection) -> str:
        """Clean up the translated text."""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing spaces - but preserve leading space for TO_TCE
        if direction == TranslationDirection.TO_TAU:
            text = text.strip()
        else:
            text = text.rstrip()  # Only remove trailing spaces for TO_TCE
        # Remove spaces around logical operators
        text = re.sub(r'\s*([&|!])\s*', r'\1', text)
        
        # Remove spaces around equals (but not >= or <=)
        text = re.sub(r'(?<!>)(?<!<)\s*(=)\s*(?![>])', r'\1', text)
        
        # Remove spaces around math operators carefully
        # Don't break >= <= etc.
        text = re.sub(r'(?<!>)\s*([+\-*])\s*', r'\1', text)  # Not after >
        text = re.sub(r'(?<!<)\s*(/)\s*', r'\1', text)  # Division not after <
        
        # Remove spaces around and inside brackets
        text = re.sub(r'\s*\[\s*(\w+)\s*\]', r'[\1]', text)
        return text
    
    def _calculate_confidence(self, original: str, translated: str) -> float:
        """Calculate confidence score based on translation quality."""
        if not translated:
            return 0.0
        
        original_words = len(original.split())
        translated_words = len(translated.split())
        
        if translated_words == 0:
            return 0.0
        
        # Base confidence starts at 0.5
        base_confidence = 0.5
        
        # Boost confidence based on number of operators (more operators = higher confidence)
        operator_count = len(re.findall(r'[&|!+=\-*/\[\]]', translated))
        operator_boost = min(operator_count * 0.1, 0.3)  # Max 0.3 boost
        
        # Small boost for successful translation (non-empty result)
        translation_boost = 0.1 if translated != original else 0.0
        
        # Extra boost if we significantly reduced word count (successful compression)
        if original_words > translated_words:
            compression_boost = 0.1
        else:
            compression_boost = 0.0
        
        confidence = base_confidence + operator_boost + translation_boost + compression_boost
        return min(confidence, 0.95)  # Cap at 95% for pattern-based translation
    
    def _get_patterns_for_direction(self, direction: TranslationDirection) -> List[tuple]:
        """Get patterns for a specific direction."""
        if direction == TranslationDirection.TO_TAU:
            return self.tce_to_tau_patterns
        elif direction == TranslationDirection.TO_TCE:
            return self.tau_to_tce_patterns
        return []