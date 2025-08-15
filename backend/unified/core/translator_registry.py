"""Translator Registry
=====================
Provides runtime selection of translator engines in a functional,
railway-oriented manner.  Engines are referenced by a short key.

    registry = TranslatorRegistry.get_default()
    translator = registry.get_engine("tce_lark", "CONTROLLED_ENGLISH", "TAU")
    result = translator.translate(source, "CONTROLLED_ENGLISH", "TAU")

Adding a new engine only requires registering a factory in `_factories`.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional
from functools import lru_cache

from backend.unified.core.result_enhanced import Result, Success, Failure
# Avoid heavyweight imports until required


class TranslatorProtocol:  # pragma: no cover – structural typing helper
    def translate(self, source: str, source_lang: str, target_lang: str) -> Result[str]:
        raise NotImplementedError


class TranslatorRegistry:
    """Singleton registry mapping engine keys to translator instances."""

    def __init__(self) -> None:
        self._factories: Dict[str, Callable[[], TranslatorProtocol]] = {}
        self._instances: Dict[str, TranslatorProtocol] = {}

        # Register built-in engines lazily.
        self.register("pattern", self._lazy_import_pattern)
        self.register("nlp", self._lazy_import_nlp)
        self.register("tce_lark", self._lazy_import_tce_lark)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def register(self, key: str, factory: Callable[[], TranslatorProtocol]) -> None:
        self._factories[key] = factory

    def get_engine(
        self,
        engine_key: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslatorProtocol:
        """Return a translator instance.

        If *engine_key* == "auto", heuristically choose an engine.
        """
        if engine_key == "auto":
            engine_key = self._auto_choose(source_lang, target_lang)

        if engine_key not in self._factories:
            raise ValueError(f"Unknown translator engine: {engine_key}")

        # Singleton per key
        if engine_key not in self._instances:
            self._instances[engine_key] = self._factories[engine_key]()
        return self._instances[engine_key]

    # ------------------------------------------------------------------
    # Heuristics
    # ------------------------------------------------------------------
    def _auto_choose(self, source_lang: str, target_lang: str) -> str:
        # If either side is CONTROLLED_ENGLISH use tce_lark
        if source_lang.upper() == "CONTROLLED_ENGLISH" or target_lang.upper() == "CONTROLLED_ENGLISH":
            return "tce_lark"
        # Short text heuristic (≤120 chars) goes to pattern
        if len(source_lang) <= 120:
            return "pattern"
        return "nlp"

    # ------------------------------------------------------------------
    # Internal lazy factories
    # ------------------------------------------------------------------
    @staticmethod
    def _lazy_import_pattern() -> TranslatorProtocol:
        from backend.unified.translators.pattern_translator import PatternTranslator  # type: ignore
        return PatternTranslator()

    @staticmethod
    def _lazy_import_nlp() -> TranslatorProtocol:
        from backend.unified.english_to_tau_translator import EnglishToTauTranslator  # type: ignore
        return EnglishToTauTranslator()  # type: ignore

    @staticmethod
    def _lazy_import_tce_lark() -> TranslatorProtocol:
        from backend.unified.translators.tce_lark_translator import TceLarkTranslator  # type: ignore
        return TceLarkTranslator()

    # ------------------------------------------------------------------
    # Singleton accessor
    # ------------------------------------------------------------------
    _DEFAULT: Optional["TranslatorRegistry"] = None

    @classmethod
    def get_default(cls) -> "TranslatorRegistry":
        if cls._DEFAULT is None:
            cls._DEFAULT = cls()
        return cls._DEFAULT 