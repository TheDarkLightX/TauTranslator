"""
Refactored ILR translator following the Intentional Disclosure Principle.

This module orchestrates ILR translation operations using the clean architecture layers:
- Domain: ILR services (business logic)
- Infrastructure: Pattern matching and parsing (I/O operations)
- All methods follow IDP Rule 2 (≤10 lines).

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, Any, Optional
from ..core.result_enhanced import Result, Success, Failure

from ..domain.ilr_types import (
    PatternMatch, TranslationResult, ILRJson, TauCode
)
from ..domain.ilr_expression_service import ExpressionParsingService
from ..domain.ilr_generation_service import ILRGenerationService
from ..domain.ilr_tau_translation_service import TauTranslationService
from ..infrastructure.ilr_infrastructure import (
    PatternMatcher, ValidationHelper, JsonSerializer
)


class ILRTranslatorRefactored:
    """Orchestrates ILR translation operations."""
    
    def __init__(self):
        self._generation_service = ILRGenerationService()
        self._tau_service = TauTranslationService()
    
    async def translate_to_ilr_async(self, text: str) -> TranslationResult:
        """Translate natural language to ILR JSON."""
        # Validate and normalize input
        normalized_text = self._prepare_input_text(text)
        if not normalized_text:
            return TranslationResult.failure("Input text is empty")
        
        # Match pattern
        pattern_result = PatternMatcher.match_pattern(normalized_text)
        if isinstance(pattern_result, Failure):
            return TranslationResult.failure(pattern_result.failure())
        
        # Generate ILR
        pattern_match = pattern_result.unwrap()
        ilr_result = self._generation_service.generate_ilr_from_pattern(
            pattern_match, normalized_text
        )
        
        if isinstance(ilr_result, Success):
            return TranslationResult.success_ilr(ilr_result.unwrap())
        else:
            return TranslationResult.failure(ilr_result.failure())
    
    async def translate_to_tau_async(self, ilr_json: str) -> TranslationResult:
        """Translate ILR JSON to TAU code."""
        tau_result = self._tau_service.translate_ilr_to_tau(ilr_json)
        
        if isinstance(tau_result, Success):
            return TranslationResult.success_tau(tau_result.unwrap())
        else:
            return TranslationResult.failure(tau_result.failure())
    
    async def translate_nl_to_tau_async(self, text: str) -> TranslationResult:
        """Direct translation from natural language to TAU."""
        # First translate to ILR
        ilr_result = await self.translate_to_ilr_async(text)
        if not ilr_result.success:
            return ilr_result
        
        # Then translate to TAU
        return await self.translate_to_tau_async(ilr_result.ilr_json)
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the ILR translation engine."""
        return {
            "engine_type": "ilr_translator",
            "version": "2.0",
            "capabilities": {
                "natural_to_ilr": True,
                "ilr_to_tau": True,
                "direct_nl_to_tau": True,
                "pattern_types": [
                    "predicate_definition",
                    "function_definition",
                    "universal_quantification",
                    "existential_quantification",
                    "conditional_statements",
                    "assignments",
                    "boolean_expressions",
                    "stream_operations",
                    "temporal_statements"
                ]
            }
        }
    
    def validate_ilr_json(self, ilr_json: str) -> Result[Dict[str, Any]]:
        """Validate ILR JSON structure."""
        return JsonSerializer.deserialize_ilr(ilr_json)
    
    # Private helper methods (all ≤10 lines)
    
    def _prepare_input_text(self, text: str) -> str:
        """Prepare input text for pattern matching."""
        if not text:
            return ""
        
        # Ensure text ends with period for TCE format
        normalized = ValidationHelper.ensure_period_at_end(text.strip())
        
        # Basic validation
        if len(normalized) < 3:  # Too short to be meaningful
            return ""
        
        return normalized


class NaturalLanguageToILRAdapter:
    """Adapter for backward compatibility with existing code."""
    
    def __init__(self):
        self._translator = ILRTranslatorRefactored()
    
    def translate_to_ilr(self, text: str) -> str:
        """Legacy synchronous translation to ILR."""
        import asyncio
        result = asyncio.run(self._translator.translate_to_ilr_async(text))
        
        if result.success:
            return result.ilr_json
        else:
            # Return error as JSON for compatibility
            error_ilr = {
                "error": True,
                "message": result.error_message
            }
            return JsonSerializer.serialize_ilr(error_ilr).unwrap_or("{}")


class ILRToTauAdapter:
    """Adapter for backward compatibility with existing code."""
    
    def __init__(self):
        self._translator = ILRTranslatorRefactored()
    
    def translate_to_tau(self, ilr_dict: Dict[str, Any]) -> str:
        """Legacy synchronous translation to TAU."""
        # Convert dict to JSON string
        json_result = JsonSerializer.serialize_ilr(ilr_dict)
        if isinstance(json_result, Failure):
            return f"# Error: {json_result.failure()}"
        
        import asyncio
        result = asyncio.run(self._translator.translate_to_tau_async(json_result.unwrap()))
        
        if result.success:
            return result.tau_code
        else:
            return f"# Translation error: {result.error_message}"


class ILRTranslatorFactory:
    """Factory for creating ILR translator instances."""
    
    @staticmethod
    def create_translator() -> ILRTranslatorRefactored:
        """Create a new ILR translator instance."""
        return ILRTranslatorRefactored()
    
    @staticmethod
    def create_nl_to_ilr_adapter() -> NaturalLanguageToILRAdapter:
        """Create adapter for natural language to ILR translation."""
        return NaturalLanguageToILRAdapter()
    
    @staticmethod
    def create_ilr_to_tau_adapter() -> ILRToTauAdapter:
        """Create adapter for ILR to TAU translation."""
        return ILRToTauAdapter()


# Example usage patterns for documentation
class ILRTranslationExamples:
    """Examples of ILR translation patterns."""
    
    @staticmethod
    async def example_predicate_definition():
        """Example: Translate predicate definition."""
        translator = ILRTranslatorFactory.create_translator()
        
        text = "for any x, predicate even(x) is x mod 2 = 0."
        result = await translator.translate_to_ilr_async(text)
        
        if result.success:
            print("ILR JSON:", result.ilr_json)
            
            # Translate to TAU
            tau_result = await translator.translate_to_tau_async(result.ilr_json)
            if tau_result.success:
                print("TAU Code:", tau_result.tau_code)
    
    @staticmethod
    async def example_stream_rule():
        """Example: Translate stream rule."""
        translator = ILRTranslatorFactory.create_translator()
        
        text = "o1[t] = i1[t] and i2[t]."
        result = await translator.translate_nl_to_tau_async(text)
        
        if result.success:
            print("TAU Code:", result.tau_code)
            # Output: o1[t] = i1[t] & i2[t].
    
    @staticmethod
    async def example_temporal_always():
        """Example: Translate temporal always statement."""
        translator = ILRTranslatorFactory.create_translator()
        
        text = "always o1[t] implies o2[t+1]."
        result = await translator.translate_nl_to_tau_async(text)
        
        if result.success:
            print("TAU Code:", result.tau_code)
            # Output: always o1[t] -> o2[t+1].