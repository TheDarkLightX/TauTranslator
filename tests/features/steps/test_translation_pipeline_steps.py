import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from pathlib import Path
from pytest_bdd import scenarios, given, when, then, parsers

from backend.unified.core.domain_types import SourceText
from backend.unified.translators.base import TranslationDirection
from backend.unified.translators.manager import TranslationManager
from backend.unified.translators.grammar_translator import GrammarTranslationEngine

# Point to the feature file
scenarios('translation_pipeline.feature')

@pytest.fixture
def grammar_content():
    """Load the canonical tau.tgf grammar file content."""
    grammar_path = Path(__file__).parent.parent.parent.parent / 'src' / 'tau_translator_omega' / 'core_engine' / 'parsers' / 'cnl_parser' / 'grammars' / 'tce_tau_compatible.lark'
    with open(grammar_path, 'r') as f:
        return f.read()

@pytest.fixture
def translation_manager(grammar_content):
    """Provides a fully configured TranslationManager with the grammar engine."""
    engine = GrammarTranslationEngine(grammar_content=grammar_content, grammar_name='tce_grammar')
    
    mock_event_bus = Mock()
    mock_cache_repo = Mock()
    mock_cache_repo.get_async = AsyncMock(return_value=None)
    mock_cache_repo.set_async = AsyncMock()

    manager = TranslationManager(event_bus=mock_event_bus, cache_repository=mock_cache_repo)
    manager.register_engine(engine, is_default=True)
    return manager

@pytest.fixture
def translation_context():
    """A dictionary to share state between steps."""
    return {}

@given(parsers.parse('a translation engine initialized with the canonical "{grammar_file}" grammar'))
def given_engine_initialized(translation_manager, grammar_file):
    # The 'translation_manager' fixture already handles this initialization.
    pass

@given('the following multi-line English source text:', target_fixture="source_text")
def given_source_text(step_docstring):
    return step_docstring

@when('I translate the text from TCE to Tau')
def when_translate_text(translation_manager, source_text, translation_context):
    async def do_translate():
        result = await translation_manager.translate_async(
            SourceText(source_text),
            TranslationDirection.TCE_TO_TAU
        )
        translation_context['result'] = result

    asyncio.run(do_translate())

@then('the output should be the following canonical Tau code:')
def then_verify_output(translation_context, step_docstring):
    expected_output = step_docstring.strip()
    actual_result = translation_context['result']

    assert actual_result.is_success(), f"Translation failed: {actual_result.failure()}"
    
    translated_text = actual_result.unwrap().translated_text.strip()
    assert translated_text == expected_output
