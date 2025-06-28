# tests/step_defs/test_tau_complexity.py

import asyncio
import pytest
from dataclasses import dataclass, field
from pathlib import Path
from pytest_bdd import given, scenarios, then, when
from unittest.mock import AsyncMock
from returns.result import Success, Result, Failure
from typing import Dict, Any, Optional

# Corrected imports based on project structure
from backend.unified.core.domain_types import SourceText, AppError
from backend.unified.translators.base import TranslationDirection, TranslationResult
from backend.unified.translators.manager_v2 import TranslationManager, BestAvailableStrategy
from backend.unified.core.interfaces import ICacheRepository, IEventBus
from backend.unified.translators.lmql_translator import LMQLTranslationEngine
from backend.unified.translators.grammar_translator import GrammarTranslationEngine

# --- Context Class for State Management ---
@dataclass
class ScenarioContext:
    source_text: Optional[SourceText] = None
    grammar_context: Dict[str, str] = field(default_factory=dict)
    result: Optional[Result[TranslationResult, AppError]] = None

# --- Load all scenarios from the feature file ---
scenarios('tau_complexity.feature')

# --- Fixtures ---

@pytest.fixture
def scenario_context() -> ScenarioContext:
    """Provides a shared context object for scenario steps."""
    return ScenarioContext()

@pytest.fixture
def translation_manager() -> TranslationManager:
    """Provides a TranslationManager with mocked dependencies and the LMQL engine."""
    mock_cache = AsyncMock(spec=ICacheRepository)
    mock_cache.get_cached_value_async.return_value = Success(None)
    mock_cache.set_cached_value_async.return_value = Success(None)

    mock_event_bus = AsyncMock(spec=IEventBus)
    mock_event_bus.publish_event_async.return_value = Success(None)

    manager = TranslationManager(
        cache_repository=mock_cache,
        event_bus=mock_event_bus,
        selection_strategies=[BestAvailableStrategy()],
    )

    lmql_engine = LMQLTranslationEngine()
    manager.register_engine(lmql_engine)
    return manager

# --- Step Definitions ---

@given('the natural language input is:')
def given_natural_language_input(scenario_context: ScenarioContext, step_multiline_string: str):
    """Stores the natural language input in the context."""
    scenario_context.source_text = SourceText(step_multiline_string.strip())

@given('the grammar file content is:')
def given_grammar_content(scenario_context: ScenarioContext, step_multiline_string: str):
    """Stores the grammar content in the context."""
    scenario_context.grammar_context = {'content': step_multiline_string, 'name': 'test_grammar.lark'}

@given('the Tau expression is:')
def given_tau_expression(scenario_context: ScenarioContext, step_multiline_string: str):
    """Stores the Tau expression in the context."""
    scenario_context.source_text = SourceText(step_multiline_string.strip())

@when("the system translates the input to TCE using the grammar")
async def when_translate_to_tce(translation_manager: TranslationManager, scenario_context: ScenarioContext):
    """Performs translation from natural language to TCE using a grammar."""
    grammar_engine = GrammarTranslationEngine(
        grammar=scenario_context.grammar_context['content'],
        grammar_name=scenario_context.grammar_context['name']
    )
    translation_manager.register_engine(grammar_engine)

    result = await translation_manager.translate_async(
        text=scenario_context.source_text, direction=TranslationDirection.TO_TCE
    )
    scenario_context.result = result

@when("the system translates the input to a formal specification using an LLM")
async def when_translate_with_llm(translation_manager: TranslationManager, scenario_context: ScenarioContext):
    """Performs translation from NL to a formal spec (Tau) using an LLM."""
    result = await translation_manager.translate_async(
        text=scenario_context.source_text, direction=TranslationDirection.NL_TO_TAU
    )
    scenario_context.result = result

@when("the system translates the Tau expression to natural language using an LLM")
async def when_translate_tau_to_nl_with_llm(translation_manager: TranslationManager, scenario_context: ScenarioContext):
    """Performs translation from Tau to natural language using an LLM."""
    result = await translation_manager.translate_async(
        text=scenario_context.source_text, direction=TranslationDirection.TAU_TO_NL
    )
    scenario_context.result = result

@then('the translated output should be:')
def then_output_should_be(scenario_context: ScenarioContext, step_multiline_string: str):
    """Asserts that the translated output matches the expected text."""
    result = scenario_context.result
    assert result is not None, "Result not found in context. The 'when' step likely failed."
    assert isinstance(result, Success), f"Translation failed: {result.failure()}"
    translated_text = result.unwrap().text.strip()
    assert translated_text == step_multiline_string.strip()
