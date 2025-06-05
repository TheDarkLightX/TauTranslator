"""
Grammar-Integrated Translation System
=====================================

Integrates the grammar-driven parser with the existing translation strategies
to provide a unified translation interface.

Author: DarkLightX / Dana Edwards
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

from .translation_strategies import (
    TranslationStrategy, TranslationResult, TranslationDirection,
    PatternBasedTranslationStrategy, LMQLTranslationStrategy,
    TranslationStrategyFactory
)
from ..core_engine.grammar_driven_parser import (
    GrammarDrivenParser, GrammarDrivenTranslationStrategy,
    TranslationMode
)
from ..core_engine.tgf_grammar_loader import get_grammar_loader

logger = logging.getLogger(__name__)


class TranslationMethod(Enum):
    """Available translation methods"""
    PATTERN_BASED = "pattern"
    GRAMMAR_DRIVEN = "grammar"
    LMQL_ENHANCED = "lmql"
    HYBRID = "hybrid"


class GrammarIntegratedTranslator:
    """
    Unified translator that integrates multiple translation strategies.
    
    This translator can:
    1. Use pattern-based translation (with recognizers)
    2. Use grammar-driven translation (with loaded grammars)
    3. Use LMQL-enhanced translation
    4. Use hybrid approach combining multiple methods
    """
    
    def __init__(self):
        self.grammar_loader = get_grammar_loader()
        self.strategies = self._initialize_strategies()
        self.default_method = TranslationMethod.HYBRID
        
    def _initialize_strategies(self) -> Dict[TranslationMethod, TranslationStrategy]:
        """Initialize all available translation strategies"""
        strategies = {}
        
        # Pattern-based strategy (always available)
        strategies[TranslationMethod.PATTERN_BASED] = PatternBasedTranslationStrategy(
            TranslationDirection.TAU_TO_TCE
        )
        
        # Grammar-driven strategy (if grammar is loaded)
        try:
            grammar_strategy = GrammarDrivenTranslationStrategy()
            if grammar_strategy.is_available():
                strategies[TranslationMethod.GRAMMAR_DRIVEN] = grammar_strategy
                logger.info("Grammar-driven translation available")
        except Exception as e:
            logger.warning(f"Grammar-driven translation not available: {e}")
        
        # LMQL strategy (if available)
        try:
            lmql_strategy = LMQLTranslationStrategy(TranslationDirection.TAU_TO_TCE)
            strategies[TranslationMethod.LMQL_ENHANCED] = lmql_strategy
            logger.info("LMQL-enhanced translation available")
        except Exception as e:
            logger.warning(f"LMQL translation not available: {e}")
        
        return strategies
    
    def translate(self, source_text: str, source_lang: str = "tau",
                  target_lang: str = "english", method: Optional[TranslationMethod] = None) -> Dict[str, Any]:
        """
        Translate text using specified or default method.
        
        Args:
            source_text: Text to translate
            source_lang: Source language ("tau" or "english")
            target_lang: Target language ("tau" or "english")
            method: Translation method to use (None for default/hybrid)
            
        Returns:
            Dictionary with translation results
        """
        if not source_text or not source_text.strip():
            return {
                'success': False,
                'output': '',
                'error': 'Empty input text',
                'method': 'none'
            }
        
        # Determine translation direction
        direction = self._determine_direction(source_lang, target_lang)
        if not direction:
            return {
                'success': False,
                'output': '',
                'error': f'Unsupported translation: {source_lang} to {target_lang}',
                'method': 'none'
            }
        
        # Use specified method or default
        method = method or self.default_method
        
        if method == TranslationMethod.HYBRID:
            return self._translate_hybrid(source_text, direction, source_lang, target_lang)
        else:
            return self._translate_single_method(source_text, direction, source_lang, target_lang, method)
    
    def _determine_direction(self, source_lang: str, target_lang: str) -> Optional[TranslationDirection]:
        """Determine translation direction from language names"""
        source_lower = source_lang.lower()
        target_lower = target_lang.lower()
        
        if source_lower == "tau" and target_lower in ["english", "tce", "natural"]:
            return TranslationDirection.TAU_TO_TCE
        elif source_lower in ["english", "tce", "natural"] and target_lower == "tau":
            return TranslationDirection.TCE_TO_TAU
        
        return None
    
    def _translate_single_method(self, text: str, direction: TranslationDirection,
                                source_lang: str, target_lang: str,
                                method: TranslationMethod) -> Dict[str, Any]:
        """Translate using a single method"""
        if method == TranslationMethod.GRAMMAR_DRIVEN:
            # Grammar-driven uses different interface
            if method in self.strategies:
                return self.strategies[method].translate(text, source_lang, target_lang)
            else:
                return {
                    'success': False,
                    'output': '',
                    'error': 'Grammar-driven translation not available',
                    'method': str(method.value)
                }
        
        # Pattern-based and LMQL use TranslationStrategy interface
        if method in self.strategies:
            # Need to create strategy with correct direction
            if method == TranslationMethod.PATTERN_BASED:
                strategy = PatternBasedTranslationStrategy(direction)
            elif method == TranslationMethod.LMQL_ENHANCED:
                strategy = LMQLTranslationStrategy(direction)
            else:
                strategy = self.strategies[method]
            
            result = strategy.translate(text)
            
            return {
                'success': result.success,
                'output': result.output,
                'error': result.errors[0] if result.errors else None,
                'warnings': result.warnings,
                'confidence': result.confidence,
                'patterns_detected': result.patterns_detected,
                'method': str(method.value)
            }
        
        return {
            'success': False,
            'output': '',
            'error': f'Translation method {method.value} not available',
            'method': str(method.value)
        }
    
    def _translate_hybrid(self, text: str, direction: TranslationDirection,
                         source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Use hybrid approach - try multiple methods and select best result.
        
        Priority order:
        1. Grammar-driven (if available and grammar matches)
        2. Pattern-based with recognizers
        3. LMQL-enhanced (if available)
        """
        results = []
        
        # Try grammar-driven first
        if TranslationMethod.GRAMMAR_DRIVEN in self.strategies:
            grammar_result = self.strategies[TranslationMethod.GRAMMAR_DRIVEN].translate(
                text, source_lang, target_lang
            )
            if grammar_result['success']:
                grammar_result['priority'] = 1
                results.append(grammar_result)
        
        # Try pattern-based
        if TranslationMethod.PATTERN_BASED in self.strategies or True:  # Always available
            pattern_strategy = PatternBasedTranslationStrategy(direction)
            pattern_result = pattern_strategy.translate(text)
            
            result_dict = {
                'success': pattern_result.success,
                'output': pattern_result.output,
                'confidence': pattern_result.confidence,
                'patterns_detected': pattern_result.patterns_detected,
                'method': 'pattern',
                'priority': 2
            }
            
            if pattern_result.success:
                results.append(result_dict)
        
        # Try LMQL if available
        if TranslationMethod.LMQL_ENHANCED in self.strategies:
            lmql_strategy = LMQLTranslationStrategy(direction)
            lmql_result = lmql_strategy.translate(text)
            
            result_dict = {
                'success': lmql_result.success,
                'output': lmql_result.output,
                'confidence': lmql_result.confidence,
                'method': 'lmql',
                'priority': 3
            }
            
            if lmql_result.success:
                results.append(result_dict)
        
        # Select best result
        if results:
            # Sort by priority and confidence
            best_result = max(results, key=lambda r: (-r['priority'], r.get('confidence', 0)))
            best_result['method'] = 'hybrid'
            best_result['methods_tried'] = [r['method'] for r in results]
            return best_result
        
        # No successful translation
        return {
            'success': False,
            'output': '',
            'error': 'No translation method succeeded',
            'method': 'hybrid',
            'methods_tried': ['grammar', 'pattern', 'lmql']
        }
    
    def get_available_methods(self) -> List[str]:
        """Get list of available translation methods"""
        methods = ['pattern']  # Always available
        
        if TranslationMethod.GRAMMAR_DRIVEN in self.strategies:
            methods.append('grammar')
        
        if TranslationMethod.LMQL_ENHANCED in self.strategies:
            methods.append('lmql')
        
        methods.append('hybrid')  # Always available
        
        return methods
    
    def set_default_method(self, method: str) -> bool:
        """Set the default translation method"""
        try:
            method_enum = TranslationMethod(method)
            if method_enum == TranslationMethod.HYBRID or method_enum in self.strategies:
                self.default_method = method_enum
                return True
        except ValueError:
            pass
        
        return False
    
    def get_grammar_info(self) -> Optional[Dict[str, Any]]:
        """Get information about loaded grammar"""
        if TranslationMethod.GRAMMAR_DRIVEN in self.strategies:
            return self.strategies[TranslationMethod.GRAMMAR_DRIVEN].translate(
                "", "tau", "english"
            ).get('grammar')
        return None
    
    def reload_strategies(self):
        """Reload translation strategies (e.g., after grammar change)"""
        self.strategies = self._initialize_strategies()


# Global instance for easy access
_integrated_translator = None

def get_integrated_translator() -> GrammarIntegratedTranslator:
    """Get or create the global integrated translator instance"""
    global _integrated_translator
    if _integrated_translator is None:
        _integrated_translator = GrammarIntegratedTranslator()
    return _integrated_translator


# Example usage
def demonstrate_integrated_translation():
    """Demonstrate the integrated translation system"""
    translator = get_integrated_translator()
    
    # Show available methods
    print("Available translation methods:", translator.get_available_methods())
    
    # Example Tau expressions
    examples = [
        "solve x > 5 & x < 10",
        "sbf input = ifile(\"data.txt\")",
        "r output[t] = input[t] + input[t-1]",
        "always (trigger[t] -> action[t+1])"
    ]
    
    for expr in examples:
        print(f"\nTranslating: {expr}")
        
        # Try hybrid translation
        result = translator.translate(expr)
        if result['success']:
            print(f"Success ({result['method']}): {result['output']}")
        else:
            print(f"Failed: {result['error']}")
        
        # Try specific methods
        for method in ['pattern', 'grammar']:
            if method in translator.get_available_methods():
                result = translator.translate(expr, method=TranslationMethod(method))
                if result['success']:
                    print(f"  {method}: {result['output']}")


if __name__ == "__main__":
    demonstrate_integrated_translation()