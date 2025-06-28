import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from returns.result import Success
from backend.unified.core.domain_types import SourceText
from backend.unified.translators.base import TranslationDirection
from backend.unified.translators.manager import TranslationManager
from backend.unified.translators.grammar_translator import GrammarTranslationEngine

@pytest.fixture
def grammar_content():
    """Load the canonical tce_tau_compatible.lark grammar file content."""
    grammar_path = Path(__file__).parent.parent.parent / 'src' / 'tau_translator_omega' / 'core_engine' / 'parsers' / 'cnl_parser' / 'grammars' / 'tce_tau_compatible.lark'
    with open(grammar_path, 'r') as f:
        return f.read()

@pytest.fixture
def translation_manager(grammar_content):
    """Provides a fully configured TranslationManager with the grammar engine."""
    engine = GrammarTranslationEngine(grammar_content=grammar_content, grammar_name='tce_grammar')
    mock_event_bus = Mock()
    mock_cache_repo = AsyncMock()
    mock_cache_repo.get_async.return_value = None
    mock_cache_repo.set_async.return_value = None
    manager = TranslationManager(event_bus=mock_event_bus, cache_repository=mock_cache_repo)
    manager.register_engine(engine, is_default=True)
    return manager

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "source_text, expected_tau",
    [
        (
            "for every X there is some Y such that X is 0 and Y is 0.",
            "all X ex Y (X = 0 && Y = 0)"
        )
    ]
)
async def test_direct_translation_pipeline(translation_manager, source_text, expected_tau):
    """Validates the TCE to Tau translation pipeline with a direct unit test."""
    # WHEN: The text is translated from TCE to Tau
    result = await translation_manager.translate_async(
        SourceText(source_text),
        TranslationDirection.TCE_TO_TAU
    )

    # THEN: The translation should be successful and match the canonical output
    assert isinstance(result, Success), f"Translation failed: {result.failure()}"
    
    translated_text = result.unwrap().translated_text.strip()
    assert translated_text == expected_tau
