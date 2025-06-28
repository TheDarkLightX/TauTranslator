"""
Refactored Bidirectional Translator for Tau ↔ TCE
================================================

Refactored from 792 lines to <300 lines for improved maintainability.
Uses Strategy pattern for translation approaches and Factory pattern for creation.

Key improvements:
- Strategy pattern for translation methods
- Factory pattern for object creation
- Clear separation of concerns
- Enhanced error handling
- Comprehensive logging

Author: DarkLightX / Dana Edwards
"""

import logging
from typing import Optional

from .translation_strategies import (
    TranslationStrategy,
    TranslationStrategyFactory,
    TranslationDirection,
    TranslationResult
)
from .pattern_analyzers import PatternAnalyzerFactory

logger = logging.getLogger(__name__)


class LMQLBidirectionalTranslator:
    """
    Main translator class using Strategy pattern for bidirectional Tau ↔ TCE translation.
    
    
    - Strategy pattern for flexible translation approaches
    - Factory pattern for strategy creation
    - Single Responsibility: Coordination only
    - Clear error handling and logging
    - Performance monitoring capability
    """

    def __init__(self, strategy_type: str = "lmql"):
        """
        Initialize translator with specified strategy.
        
        Args:
            strategy_type: 'lmql' (default) or 'pattern'
            
        Raises:
            ValueError: If strategy_type is not supported
        """
        self.strategy_type = strategy_type
        self._validate_strategy_type(strategy_type)
        
        # Create strategies using Factory pattern
        self.tau_to_tce_strategy = TranslationStrategyFactory.create_strategy(
            strategy_type, TranslationDirection.TAU_TO_TCE
        )
        self.tce_to_tau_strategy = TranslationStrategyFactory.create_strategy(
            strategy_type, TranslationDirection.TCE_TO_TAU
        )
        
        # Performance tracking
        self._translation_count = 0
        self._error_count = 0
        
        logger.info(f"LMQLBidirectionalTranslator initialized with {strategy_type} strategy")
    
    def _validate_strategy_type(self, strategy_type: str) -> None:
        """Validate strategy type parameter."""
        valid_strategies = ['lmql', 'pattern']
        if strategy_type.lower() not in valid_strategies:
            raise ValueError(f"Invalid strategy type: {strategy_type}. Must be one of {valid_strategies}")
    
    def translate_tce_to_tau(self, tce_text: str) -> TranslationResult:
        """
        Translate TCE to Tau Language using configured strategy.

        Args:
            tce_text: TCE natural language text

        Returns:
            TranslationResult with Tau output
            
        Raises:
            ValueError: If tce_text is None or empty
        """
        if not tce_text or not tce_text.strip():
            raise ValueError("tce_text cannot be None or empty")
        
        self._translation_count += 1
        
        try:
            logger.debug(f"Translating TCE to Tau: {tce_text[:50]}...")
            result = self.tce_to_tau_strategy.translate(tce_text)
            
            if not result.success:
                self._error_count += 1
                logger.warning(f"TCE to Tau translation failed: {result.errors}")
            else:
                logger.debug(f"TCE to Tau translation succeeded: {result.output[:50]}...")
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Unexpected error in TCE to Tau translation: {e}")
            return TranslationResult(
                success=False,
                output="",
                confidence=0.0,
                patterns_detected=[],
                errors=[f"Unexpected translation error: {str(e)}"],
                warnings=[]
            )
    
    def translate_tau_to_tce(self, tau_text: str) -> TranslationResult:
        """
        Translate Tau Language to TCE using configured strategy.

        Args:
            tau_text: Tau language code

        Returns:
            TranslationResult with TCE output
            
        Raises:
            ValueError: If tau_text is None or empty
        """
        if not tau_text or not tau_text.strip():
            raise ValueError("tau_text cannot be None or empty")
        
        self._translation_count += 1
        
        try:
            logger.debug(f"Translating Tau to TCE: {tau_text[:50]}...")
            result = self.tau_to_tce_strategy.translate(tau_text)
            
            if not result.success:
                self._error_count += 1
                logger.warning(f"Tau to TCE translation failed: {result.errors}")
            else:
                logger.debug(f"Tau to TCE translation succeeded: {result.output[:50]}...")
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Unexpected error in Tau to TCE translation: {e}")
            return TranslationResult(
                success=False,
                output="",
                confidence=0.0,
                patterns_detected=[],
                errors=[f"Unexpected translation error: {str(e)}"],
                warnings=[]
            )
    
    def get_translation_stats(self) -> dict:
        """
        Get translation performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'total_translations': self._translation_count,
            'error_count': self._error_count,
            'success_rate': (
                (self._translation_count - self._error_count) / self._translation_count
                if self._translation_count > 0 else 0.0
            ),
            'strategy_type': self.strategy_type
        }
    
    def reset_stats(self) -> None:
        """Reset translation statistics."""
        self._translation_count = 0
        self._error_count = 0
        logger.info("Translation statistics reset")
    
    def switch_strategy(self, new_strategy_type: str) -> None:
        """
        Switch to a different translation strategy.
        
        Args:
            new_strategy_type: 'lmql' or 'pattern'
            
        Raises:
            ValueError: If new_strategy_type is not supported
        """
        self._validate_strategy_type(new_strategy_type)
        
        logger.info(f"Switching translation strategy from {self.strategy_type} to {new_strategy_type}")
        
        self.strategy_type = new_strategy_type
        
        # Create new strategies
        self.tau_to_tce_strategy = TranslationStrategyFactory.create_strategy(
            new_strategy_type, TranslationDirection.TAU_TO_TCE
        )
        self.tce_to_tau_strategy = TranslationStrategyFactory.create_strategy(
            new_strategy_type, TranslationDirection.TCE_TO_TAU
        )
        
        logger.info(f"Strategy switch complete: now using {new_strategy_type}")


# Legacy compatibility - maintain existing interface
class LMQLBidirectionalTranslatorLegacy:
    """
    Legacy compatibility wrapper for the original interface.
    
    Maintains backward compatibility while using refactored implementation.
    """
    
    def __init__(self):
        self._translator = LMQLBidirectionalTranslator()
        self.tau_analyzer = PatternAnalyzerFactory.create_tau_analyzer()
        self.tce_analyzer = PatternAnalyzerFactory.create_tce_analyzer()
        self.use_lmql = True  # Legacy attribute
    
    def translate_tau_to_tce(self, tau_text: str) -> TranslationResult:
        """Legacy method - delegates to refactored implementation."""
        return self._translator.translate_tau_to_tce(tau_text)
    
    def translate_tce_to_tau(self, tce_text: str) -> TranslationResult:
        """Legacy method - delegates to refactored implementation."""
        return self._translator.translate_tce_to_tau(tce_text)


# Factory function for easy instantiation
def create_bidirectional_translator(strategy_type: str = "lmql") -> LMQLBidirectionalTranslator:
    """
    Factory function to create bidirectional translator.
    
    Args:
        strategy_type: 'lmql' (default) or 'pattern'
        
    Returns:
        Configured LMQLBidirectionalTranslator instance
    """
    return LMQLBidirectionalTranslator(strategy_type)


# Convenience functions for direct translation
def translate_tce_to_tau(tce_text: str, strategy_type: str = "lmql") -> TranslationResult:
    """
    Convenience function for TCE to Tau translation.
    
    Args:
        tce_text: TCE text to translate
        strategy_type: Translation strategy to use
        
    Returns:
        TranslationResult with translation outcome
    """
    translator = create_bidirectional_translator(strategy_type)
    return translator.translate_tce_to_tau(tce_text)


def translate_tau_to_tce(tau_text: str, strategy_type: str = "lmql") -> TranslationResult:
    """
    Convenience function for Tau to TCE translation.
    
    Args:
        tau_text: Tau text to translate
        strategy_type: Translation strategy to use
        
    Returns:
        TranslationResult with translation outcome
    """
    translator = create_bidirectional_translator(strategy_type)
    return translator.translate_tau_to_tce(tau_text)