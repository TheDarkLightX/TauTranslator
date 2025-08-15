"""
Translation engines for the unified TauTranslator backend.

This module provides a unified interface for all translation methods
used across the different backend variants.

Author: DarkLightX / Dana Edwards
"""

# Heavy imports are optional – guard them so the module can be imported
# even when extra dependencies (e.g. `returns`) are not installed.

try:
    from .base import TranslationEngine, TranslationResult  # type: ignore
    from .lmql_translator import LMQLTranslationEngine  # type: ignore
    from .grammar_translator import GrammarTranslationEngine  # type: ignore
    from .nlp_translator import NLPTranslationEngine  # type: ignore
    from .pattern_translator import PatternTranslationEngine  # type: ignore
    from .manager import TranslationManager  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover – optional deps
    # Provide minimal stubs to keep __all__ export intact.
    class _MissingDependency:  # pylint: disable=too-few-public-methods
        def __init__(self, err: ModuleNotFoundError):
            self._err = err

        def __getattr__(self, item):
            raise self._err

    TranslationEngine = _MissingDependency(exc)  # type: ignore
    TranslationResult = _MissingDependency(exc)  # type: ignore
    LMQLTranslationEngine = _MissingDependency(exc)  # type: ignore
    GrammarTranslationEngine = _MissingDependency(exc)  # type: ignore
    NLPTranslationEngine = _MissingDependency(exc)  # type: ignore
    PatternTranslationEngine = _MissingDependency(exc)  # type: ignore
    TranslationManager = _MissingDependency(exc)  # type: ignore

__all__ = [
    'TranslationEngine',
    'TranslationResult', 
    'LMQLTranslationEngine',
    'GrammarTranslationEngine',
    'NLPTranslationEngine',
    'PatternTranslationEngine',
    'TranslationManager'
]