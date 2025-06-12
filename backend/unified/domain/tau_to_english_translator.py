"""
TAU to English Translation Service following the Intentional Disclosure Principle.

This service converts formal TAU expressions back to natural English, 
providing the reverse translation capability for bidirectional translation.

Copyright: DarkLightX / Dana Edwards
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..core.domain_types import (
    Result, Success, Failure, success, failure
)
from ..core.functional_utils import guard, guard_not_none


@dataclass(frozen=True)
class TranslationPattern:
    """A pattern for translating TAU symbols to English."""
    tau_pattern: str
    english_template: str
    description: str


class TauToEnglishTranslator:
    """Translates formal TAU expressions to natural English following IDP principles."""
    
    def __init__(self):
        self._patterns = self._create_patterns()
    
    def _create_patterns(self) -> List[TranslationPattern]:
        """Create translation patterns (≤10 lines)."""
        return [
            TranslationPattern(r'∀(\w+): (.+)', r'for all \1, \2', 'Universal quantifier'),
            TranslationPattern(r'∃(\w+): (.+)', r'there exists \1 such that \2', 'Existential quantifier'),
            TranslationPattern(r'\((.+?) \? (.+?) : (.+?)\)', r'if \1 then \2 else \3', 'Conditional'),
            TranslationPattern(r'(.+?) & (.+)', r'\1 and \2', 'Logical AND'),
            TranslationPattern(r'(.+?) \| (.+)', r'\1 or \2', 'Logical OR'),
            TranslationPattern(r'(.+?) \^ (.+)', r'\1 xor \2', 'Logical XOR'),
            TranslationPattern(r'(.+?) = (.+)', r'\1 equals \2', 'Equality'),
            TranslationPattern(r'(.+?) != (.+)', r'\1 does not equal \2', 'Inequality'),
            TranslationPattern(r'(.+?) > (.+)', r'\1 is greater than \2', 'Greater than'),
            TranslationPattern(r'(.+?) < (.+)', r'\1 is less than \2', 'Less than')
        ]
    
    async def translate_async(self, tau_expression: str) -> Result[str]:
        """Translate TAU expression to English (≤10 lines)."""
        cleaned = self._preprocess(tau_expression)
        if not cleaned:
            return failure("EMPTY_INPUT", "Empty TAU expression")
        
        translated = await self._apply_patterns_async(cleaned)
        result = self._postprocess(translated)
        
        return success(result)
    
    def _preprocess(self, expression: str) -> str:
        """Clean and prepare input (≤10 lines)."""
        cleaned = expression.strip()
        if cleaned.endswith('.'):
            cleaned = cleaned[:-1]
        return cleaned
    
    async def _apply_patterns_async(self, expression: str) -> str:
        """Apply translation patterns (≤10 lines)."""
        result = expression
        
        for pattern in self._patterns:
            if re.search(pattern.tau_pattern, result):
                result = re.sub(pattern.tau_pattern, pattern.english_template, result)
                break
        
        return result
    
    def _postprocess(self, translated: str) -> str:
        """Clean up output (≤10 lines)."""
        if not translated:
            return translated
        
        # Capitalize first letter and add period
        result = translated[0].upper() + translated[1:] if len(translated) > 1 else translated.upper()
        if not result.endswith('.'):
            result += '.'
        
        return result


class TauToEnglishService:
    """Service orchestrating TAU to English translation following IDP principles."""
    
    def __init__(self):
        self._translator = TauToEnglishTranslator()
    
    async def translate_expression_async(self, tau_expression: str) -> Result[str]:
        """Main translation method (≤10 lines)."""
        validation_result = self._validate_input(tau_expression)
        if isinstance(validation_result, Failure):
            return validation_result
        
        return await self._translator.translate_async(tau_expression)
    
    def _validate_input(self, expression: str) -> Result[str]:
        """Validate input expression (≤10 lines)."""
        if not expression or not expression.strip():
            return failure("EMPTY_INPUT", "TAU expression cannot be empty")
        
        return success(expression)
    
    async def translate_batch_async(self, expressions: List[str]) -> List[Result[str]]:
        """Translate multiple expressions (≤10 lines)."""
        results = []
        
        for expr in expressions:
            result = await self.translate_expression_async(expr)
            results.append(result)
        
        return results
    
    def can_translate(self, tau_expression: str) -> bool:
        """Check if expression can be translated (≤10 lines)."""
        if not tau_expression or not tau_expression.strip():
            return False
        
        # Check if any pattern matches
        for pattern in self._translator._patterns:
            if re.search(pattern.tau_pattern, tau_expression):
                return True
        
        return False
    
    def get_capabilities(self) -> Dict[str, any]:
        """Get translator capabilities (≤10 lines)."""
        return {
            "supported_patterns": len(self._translator._patterns),
            "pattern_descriptions": [p.description for p in self._translator._patterns],
            "supports_async": True,
            "supports_batch": True
        }


def create_tau_to_english_service() -> TauToEnglishService:
    """Factory function for TAU to English service (≤10 lines)."""
    return TauToEnglishService()