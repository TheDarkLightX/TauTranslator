import pytest
from backend.unified.core.translator_registry import TranslatorRegistry
from backend.unified.translators.tce_lark_translator import TceLarkTranslator
from backend.unified.core.result_enhanced import Success, Failure


def test_tce_lark_basic_translation():
    """TCE sentence with simple equality should map to Tau syntax."""
    translator = TceLarkTranslator()
    result = translator.translate(
        source="always x equals y.",
        source_lang="CONTROLLED_ENGLISH",
        target_lang="TAU",
    )
    assert isinstance(result, Success)
    assert result.value.strip() == "always (x = y)"  # minimal normalization


def test_registry_auto_selects_tce_lark():
    """When source language is CONTROLLED_ENGLISH and engineKey is auto, registry should pick TCE Lark engine."""
    registry = TranslatorRegistry.get_default()
    engine = registry.get_engine(engine_key="auto", source_lang="CONTROLLED_ENGLISH", target_lang="TAU")
    assert isinstance(engine, TceLarkTranslator) 