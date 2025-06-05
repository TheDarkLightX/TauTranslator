"""
Translation engines for the unified TauTranslator backend.

This module provides a unified interface for all translation methods
used across the different backend variants.

Author: DarkLightX / Dana Edwards
"""

from .base import TranslationEngine, TranslationResult
from .lmql_translator import LMQLTranslationEngine
from .grammar_translator import GrammarTranslationEngine
from .nlp_translator import NLPTranslationEngine
from .pattern_translator import PatternTranslationEngine
from .manager import TranslationManager

__all__ = [
    'TranslationEngine',
    'TranslationResult', 
    'LMQLTranslationEngine',
    'GrammarTranslationEngine',
    'NLPTranslationEngine',
    'PatternTranslationEngine',
    'TranslationManager'
]