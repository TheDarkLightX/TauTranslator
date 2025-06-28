# Copyright (c) DarkLightX / Dana Edwards

import asyncio
import shutil
from pathlib import Path
from pytest_bdd import scenarios, given, when, then, parsers
from returns.pipeline import is_successful

from backend.unified.core.domain_types import SourceText
from backend.unified.translators.base import TranslationDirection
from backend.unified.translators.grammar_translator import GrammarTranslationEngine
from backend.unified.translators.manager import TranslationManager
from .transformers import SimpleMathTransformer
from .conftest import DummyEventBus, DummyCacheRepository

# Link feature files
scenarios('../features/english_to_cnl.feature', '../features/complex_scenarios.feature')

# --- Step Definitions ---

@given("a grammar for arithmetic expressions is loaded")
def given_arithmetic_grammar_loaded(grammar_context):
    """Loads the simple_math.ebnf grammar for complex scenarios."""
    given_custom_grammar(grammar_context, "simple_math.ebnf")
    given_grammar_loaded(grammar_context)

@given(parsers.parse('a custom grammar file "{grammar_file}"'))
def given_custom_grammar(grammar_context, grammar_file):
    """Copies the grammar file and reads its content."""
    source_grammar_path = Path(__file__).parent.parent / 'features' / grammar_file
    dest_path = grammar_context["temp_dir"] / grammar_file
    shutil.copy(source_grammar_path, dest_path)
    with open(dest_path, 'r') as f:
        grammar_context["grammar_content"] = f.read()
    grammar_context["grammar_name"] = "simple_math_cnl"

@given('the grammar is loaded successfully')
def given_grammar_loaded(grammar_context):
    """Initializes and registers the translation engine."""
    engine = GrammarTranslationEngine(
        grammar_content=grammar_context["grammar_content"],
        grammar_name=grammar_context["grammar_name"]
    )
    engine.set_cnl_transformer(SimpleMathTransformer)
    assert engine.is_available, "Engine failed to initialize."
    manager = TranslationManager(
        event_bus=DummyEventBus(),
        cache_repository=DummyCacheRepository()
    )
    manager.register_engine(engine, is_default=True)
    grammar_context["manager"] = manager

@when(parsers.parse('I provide the source text "{sentence}"'))
def when_provide_source_text(grammar_context, sentence):
    """Runs the async transformation and stores the result."""
    manager = grammar_context["manager"]
    source_text = SourceText(sentence)  # Use the actual source text

    async def do_transform():
        # Note: The direction is a bit of a misnomer now, but it's required by the manager.
        # The core logic in GrammarTranslationEngine doesn't use it.
        result = await manager.translate_async(
            text=source_text,
            use_cache=False,
            use_fallback=False,
            direction=TranslationDirection.TCE_TO_TAU
        )
        return result

    result = asyncio.run(do_transform())
    grammar_context["translation_result"] = result

@then(parsers.parse('the transformed output should be "{expected_output}"'))
def then_transformed_output_is(grammar_context, expected_output):
    """Asserts that the transformation output matches the expected result."""
    translation_result = grammar_context["translation_result"]
    assert is_successful(translation_result), f"Transformation failed: {translation_result.failure()}"
    result_obj = translation_result.unwrap()
    assert result_obj.translated_text == expected_output, \
        f"Expected '{expected_output}', but got '{result_obj.translated_text}'"
