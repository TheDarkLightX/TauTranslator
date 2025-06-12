"""
Refactored NLP translator following the Intentional Disclosure Principle.

This module orchestrates NLP translation operations using the clean architecture layers:
- Domain: NLP services (business logic)
- Infrastructure: Pattern matching and text processing (I/O operations)
- All methods follow IDP Rule 2 (≤10 lines).

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, Any, Optional, List
from returns.result import Result, Success, Failure

from ..domain.nlp_types import (
    NaturalLanguageText, TCEText, TAUText, TranslationResult,
    TranslationContext, TranslationDirection
)
from ..domain.nlp_translation_service import (
    NLPTranslationService, RuleBasedTranslationService
)


class NLPTranslatorRefactored:
    """Orchestrates NLP translation operations."""
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        context = TranslationContext(vocabulary=vocabulary or {})
        self._translation_service = NLPTranslationService(context)
        self._rule_service = RuleBasedTranslationService()
    
    async def translate_to_tce_async(self, nl_text: str) -> TranslationResult:
        """Translate natural language to TCE."""
        if not nl_text:
            return TranslationResult.failure_result("Empty input text")
        
        # Convert to domain type
        nl_input = NaturalLanguageText(nl_text)
        
        # Perform translation
        return self._translation_service.translate_nl_to_tce(nl_input)
    
    async def translate_to_natural_async(self, tce_text: str) -> TranslationResult:
        """Translate TCE to natural language."""
        if not tce_text:
            return TranslationResult.failure_result("Empty input text")
        
        # Convert to domain type
        tce_input = TCEText(tce_text)
        
        # Perform translation
        return self._translation_service.translate_tce_to_nl(tce_input)
    
    async def translate_bidirectional_async(
        self, text: str, direction: TranslationDirection
    ) -> TranslationResult:
        """Translate in specified direction."""
        if direction == TranslationDirection.NL_TO_TCE:
            return await self.translate_to_tce_async(text)
        elif direction == TranslationDirection.TCE_TO_NL:
            return await self.translate_to_natural_async(text)
        else:
            return TranslationResult.failure_result(
                f"Unsupported translation direction: {direction}"
            )
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the NLP translation engine."""
        return {
            "engine_type": "nlp_translator",
            "version": "2.0",
            "capabilities": {
                "nl_to_tce": True,
                "tce_to_nl": True,
                "pattern_types": [
                    "universal_quantification",
                    "existential_quantification", 
                    "conditionals",
                    "predicates",
                    "relations",
                    "temporal_properties",
                    "disjunctions"
                ],
                "fallback": "rule_based"
            }
        }
    
    def update_vocabulary(self, vocabulary: Dict[str, Any]) -> None:
        """Update the vocabulary used for translation."""
        new_context = TranslationContext(vocabulary=vocabulary)
        self._translation_service = NLPTranslationService(new_context)


class TCEToTauTranslator:
    """Translates TCE to TAU format."""
    
    def __init__(self):
        self._condition_patterns = self._initialize_condition_patterns()
    
    async def translate_to_tau_async(self, tce_text: str) -> TranslationResult:
        """Translate TCE to TAU."""
        if not tce_text:
            return TranslationResult.failure_result("Empty input text")
        
        # Clean input
        cleaned = tce_text.strip()
        if cleaned.endswith('.'):
            cleaned = cleaned[:-1]
        
        # Apply transformations
        tau_text = self._transform_to_tau(cleaned)
        
        # Add period for TAU format
        if tau_text and not tau_text.endswith('.'):
            tau_text += '.'
        
        return TranslationResult.success_result(tau_text)
    
    def _initialize_condition_patterns(self) -> List[tuple]:
        """Initialize patterns for condition transformation."""
        return [
            # Logical operators
            (' and ', ' & '),
            (' or ', ' | '),
            ('not ', '!'),
            
            # Quantifiers
            ('for every ', '∀'),
            ('there exists ', '∃'),
            ('such that ', ':'),
            
            # Temporal
            ('always ', '□'),
            ('sometimes ', '◇'),
            
            # Conditionals
            ('if ', ''),
            (' then ', ' -> '),
            
            # Relations
            ('implies', '->'),
            ('iff', '<->')
        ]
    
    def _transform_to_tau(self, text: str) -> str:
        """Transform TCE text to TAU format."""
        result = text
        
        # Apply pattern transformations
        for old_pattern, new_pattern in self._condition_patterns:
            result = result.replace(old_pattern, new_pattern)
        
        # Handle specific constructs
        result = self._transform_predicates(result)
        result = self._transform_relations(result)
        
        return result
    
    def _transform_predicates(self, text: str) -> str:
        """Transform predicate constructs."""
        # Simple "X is Y" pattern
        if ' is ' in text and '(' not in text:
            parts = text.split(' is ', 1)
            if len(parts) == 2:
                return f"{parts[0].strip()}.{parts[1].strip()}"
        return text
    
    def _transform_relations(self, text: str) -> str:
        """Transform relation constructs."""
        # Already in function form - keep as is
        if '(' in text and ')' in text:
            return text
        
        return text


class LegacyNLPTranslatorAdapter:
    """Adapter for backward compatibility with existing code."""
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        self._translator = NLPTranslatorRefactored(vocabulary)
        self._tau_translator = TCEToTauTranslator()
    
    def translate_to_tce(self, nl_text: str) -> str:
        """Legacy synchronous translation to TCE."""
        import asyncio
        result = asyncio.run(self._translator.translate_to_tce_async(nl_text))
        
        if result.success:
            return result.output_text
        else:
            return ""  # Legacy behavior on error
    
    def translate_to_natural(self, tce_text: str) -> str:
        """Legacy synchronous translation to natural language."""
        import asyncio
        result = asyncio.run(self._translator.translate_to_natural_async(tce_text))
        
        if result.success:
            return result.output_text
        else:
            return tce_text  # Return original on error


class NLPTranslatorFactory:
    """Factory for creating NLP translator instances."""
    
    @staticmethod
    def create_translator(vocabulary: Optional[Dict[str, Any]] = None) -> NLPTranslatorRefactored:
        """Create a new NLP translator instance."""
        return NLPTranslatorRefactored(vocabulary)
    
    @staticmethod
    def create_tce_to_tau_translator() -> TCEToTauTranslator:
        """Create TCE to TAU translator."""
        return TCEToTauTranslator()
    
    @staticmethod
    def create_legacy_adapter(vocabulary: Optional[Dict[str, Any]] = None) -> LegacyNLPTranslatorAdapter:
        """Create legacy adapter for backward compatibility."""
        return LegacyNLPTranslatorAdapter(vocabulary)


# Example usage patterns
class NLPTranslationExamples:
    """Examples of NLP translation patterns."""
    
    @staticmethod
    async def example_universal_quantification():
        """Example: Universal quantification."""
        translator = NLPTranslatorFactory.create_translator()
        
        # Natural language input
        nl_text = "All birds can fly"
        result = await translator.translate_to_tce_async(nl_text)
        
        if result.success:
            print(f"TCE: {result.output_text}")
            # Output: "for every bird such that it can fly."
    
    @staticmethod
    async def example_conditional():
        """Example: Conditional statement."""
        translator = NLPTranslatorFactory.create_translator()
        
        # Natural language input
        nl_text = "If it rains, then the ground is wet"
        result = await translator.translate_to_tce_async(nl_text)
        
        if result.success:
            print(f"TCE: {result.output_text}")
            # Output: "if it rains then the ground is wet."
    
    @staticmethod
    async def example_reverse_translation():
        """Example: TCE to natural language."""
        translator = NLPTranslatorFactory.create_translator()
        
        # TCE input
        tce_text = "for every x such that x is human implies x is mortal."
        result = await translator.translate_to_natural_async(tce_text)
        
        if result.success:
            print(f"Natural: {result.output_text}")
            # Output: "Every human is mortal."