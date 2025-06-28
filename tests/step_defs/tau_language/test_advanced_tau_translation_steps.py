# Copyright (c) DarkLightX / Dana Edwards

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from pathlib import Path
from dataclasses import dataclass # Added to define ScenarioContext
from typing import Optional # Added for type hints

from backend.unified.translators.orchestrator import BackwardCompatibleFacade

# For type hinting and shared context
@dataclass
class ScenarioContext:
    grammar_content: Optional[str] = None
    translation_manager: Optional[BackwardCompatibleFacade] = None # Updated type hint
    english_text: Optional[str] = None
    formal_text: Optional[str] = None
    translated_formal_text: Optional[str] = None
    translated_english_text: Optional[str] = None
    error_message: Optional[str] = None

# Link to the feature file(s)
# Path is relative to `bdd_features_base_dir` (tests/features/)
# scenarios("tau_language/advanced_tau_translation.feature") # Disabled: Feature file not found

# --- Fixtures ---

@pytest.fixture
def grammar_fixtures_path() -> Path:
    """Provides the path to the grammar fixtures directory."""
    # Path is .../TauTranslator-main/tests/fixtures/grammars/
    return Path(__file__).parent.parent.parent / "fixtures" / "grammars"

@pytest.fixture
def scenario_context() -> ScenarioContext:
    """Provides a ScenarioContext instance for sharing data across steps."""
    return ScenarioContext()

@pytest.fixture
def translator_instance(scenario_context: ScenarioContext):
    """Creates a TranslationManager instance for the scenario."""
    grammar_content = scenario_context.grammar_content
    if not grammar_content:
        # This case should ideally be prevented by the Given step ensuring grammar is loaded
        pytest.fail("Grammar content not found in scenario_context. Cannot initialize BackwardCompatibleFacade.")
    # The BackwardCompatibleFacade is already initialized in the 'given_grammar_from_docstring' or 'given_tau_specification_from_file' steps
    # and stored in scenario_context.translation_manager. This fixture can now just return that.
    if scenario_context.translation_manager is None:
        # This could happen if the grammar given step failed to initialize it or was missed.
        pytest.fail("TranslationManager (BackwardCompatibleFacade) not found in scenario_context. Ensure a grammar 'given' step ran successfully.")
    print(f"INFO: Returning pre-initialized BackwardCompatibleFacade from scenario_context. Grammar: {grammar_content[:50]}...")
    return scenario_context.translation_manager

# --- Step Definitions ---

@given(parsers.parse('the system is configured with the "{grammar_name}" grammar')) # Removed target_fixture
def given_system_configured_with_grammar(scenario_context: ScenarioContext, grammar_fixtures_path: Path, grammar_name: str):
    grammar_file_path = grammar_fixtures_path / grammar_name
    if not grammar_file_path.is_file():
        pytest.fail(f"Grammar file not found: {grammar_file_path}. Please ensure '{grammar_name}' is in '{grammar_fixtures_path}'.")
    
    with open(grammar_file_path, 'r', encoding='utf-8') as f:
        grammar_content = f.read()
    scenario_context.grammar_content = grammar_content
    # scenario_context.grammar_name = grammar_name # grammar_name is not a field in ScenarioContext
    # Initialize the translator here as well, similar to other grammar given steps
    try:
        print(f"INFO: Attempting to initialize BackwardCompatibleFacade with grammar '{grammar_name}' from {grammar_file_path}...")
        scenario_context.translation_manager = BackwardCompatibleFacade(grammar_content=grammar_content)
        print(f"INFO: Successfully initialized BackwardCompatibleFacade with grammar '{grammar_name}'.")
    except Exception as e:
        print(f"ERROR: Failed to initialize BackwardCompatibleFacade with grammar '{grammar_name}': {e}")
        scenario_context.error_message = f"Failed to initialize TranslationManager with grammar '{grammar_name}': {e}"

@given('the English specification:')
def given_english_specification_docstring(scenario_context: ScenarioContext, docstring: str):
    # docstring is injected by pytest-bdd from the Gherkin docstring
    scenario_context.english_text = docstring.strip()
    # No return needed as scenario_context is a mutable object (fixture)

@given(parsers.parse('the following Tau grammar specification:')) # Removed target_fixture
def given_grammar_from_docstring(docstring: str, scenario_context: ScenarioContext):
    print(f"DEBUG: given_grammar_from_docstring received docstring (len: {len(docstring)}):\n{docstring[:200]}...")
    scenario_context.grammar_content = docstring
    try:
        print(f"INFO: Attempting to initialize BackwardCompatibleFacade with grammar content (len: {len(docstring)})...")
        scenario_context.translation_manager = BackwardCompatibleFacade(grammar_content=docstring)
        print("INFO: Successfully initialized BackwardCompatibleFacade.")
    except Exception as e:
        print(f"ERROR: Failed to initialize BackwardCompatibleFacade: {e}")
        scenario_context.error_message = f"Failed to initialize TranslationManager: {e}"

@given(parsers.parse('the Tau grammar specification from file "{grammar_file}"')) # Removed target_fixture
def given_tau_specification_from_file(scenario_context: ScenarioContext, grammar_fixtures_path: Path, grammar_file: str):
    grammar_file_path = grammar_fixtures_path / grammar_file
    if not grammar_file_path.is_file():
        pytest.fail(f"Grammar file not found: {grammar_file_path}. Please ensure '{grammar_file}' is in '{grammar_fixtures_path}'.")
    
    with open(grammar_file_path, 'r', encoding='utf-8') as f:
        grammar_content = f.read()
    scenario_context.grammar_content = grammar_content
    # scenario_context.grammar_file = grammar_file # grammar_file is not a field in ScenarioContext
    try:
        print(f"INFO: Attempting to initialize BackwardCompatibleFacade with grammar from {grammar_file_path}...")
        scenario_context.translation_manager = BackwardCompatibleFacade(grammar_content=grammar_content)
        print(f"INFO: Successfully initialized BackwardCompatibleFacade with grammar from {grammar_file_path}.")
    except Exception as e:
        print(f"ERROR: Failed to initialize BackwardCompatibleFacade with grammar from {grammar_file_path}: {e}")
        scenario_context.error_message = f"Failed to initialize TranslationManager: {e}"

@given('the Tau Language specification:')
def given_tau_specification_docstring(scenario_context: ScenarioContext, docstring: str):
    # docstring is injected by pytest-bdd from the Gherkin docstring
    scenario_context.formal_text = docstring.strip()
    # No return needed as scenario_context is a mutable object (fixture)

@when('the English specification is translated to Tau Language') # Removed target_fixture
def when_english_spec_is_translated(scenario_context: ScenarioContext, translator_instance: BackwardCompatibleFacade):
    if scenario_context.english_text is None:
        pytest.fail("English specification (english_text) not found in scenario context.")
    if scenario_context.translation_manager is None:
        pytest.fail("Translation manager not initialized in scenario context.")
    
    print(f"DEBUG: Calling translate_english_to_formal for: {scenario_context.english_text[:100]}...")
    scenario_context.translated_formal_text = scenario_context.translation_manager.translate_english_to_formal(scenario_context.english_text)
    print(f"DEBUG: Received translated_formal_text: {scenario_context.translated_formal_text[:100]}...")

@when('the Tau Language specification is translated to English') # Removed target_fixture
def when_tau_spec_is_translated(scenario_context: ScenarioContext, translator_instance: BackwardCompatibleFacade):
    if scenario_context.formal_text is None:
        pytest.fail("Tau Language specification (formal_text) not found in scenario context.")
    if scenario_context.translation_manager is None:
        pytest.fail("Translation manager not initialized in scenario context.")

    print(f"DEBUG: Calling translate_formal_to_english for: {scenario_context.formal_text[:100]}...")
    scenario_context.translated_english_text = scenario_context.translation_manager.translate_formal_to_english(scenario_context.formal_text)
    print(f"DEBUG: Received translated_english_text: {scenario_context.translated_english_text[:100]}...")

# --- Then Steps (Placeholders - to be refined based on actual Tau output structure) ---

@then('the resulting Tau Language code should be valid')
def then_tau_code_is_valid(scenario_context: ScenarioContext):
    assert scenario_context.error_message is None, f"Setup error: {scenario_context.error_message}"
    assert scenario_context.translated_formal_text is not None, "No translated Tau output (translated_formal_text) found in context."
    # Basic check for now, assuming successful translation doesn't return our error prefix
    assert not scenario_context.translated_formal_text.startswith("ERROR_TRANSLATING_TO_FORMAL:"), \
        f"Translation to formal failed: {scenario_context.translated_formal_text}"
    assert len(scenario_context.translated_formal_text.strip()) > 0, "Translated Tau code is empty."
    print(f"Generated Tau (validation pending):\n{scenario_context.translated_formal_text}")

@then(parsers.parse('the Tau Language code should reflect {expected_feature}'))
def then_tau_code_reflects_feature(scenario_context: ScenarioContext, expected_feature: str):
    assert scenario_context.translated_formal_text is not None, "No translated Tau output found."
    assert not scenario_context.translated_formal_text.startswith("ERROR_TRANSLATING_TO_FORMAL:"), \
        f"Translation to formal failed: {scenario_context.translated_formal_text}"
    assert expected_feature.lower() in scenario_context.translated_formal_text.lower(), \
        f"Expected feature '{expected_feature}' not found in Tau output:\n{scenario_context.translated_formal_text}"

@then('the resulting English description should be clear and accurate')
def then_english_desc_is_clear(scenario_context: ScenarioContext):
    assert scenario_context.error_message is None, f"Setup error: {scenario_context.error_message}"
    assert scenario_context.translated_english_text is not None, "No translated English output (translated_english_text) found in context."
    assert not scenario_context.translated_english_text.startswith("ERROR_TRANSLATING_TO_ENGLISH:"), \
        f"Translation to English failed: {scenario_context.translated_english_text}"
    assert len(scenario_context.translated_english_text.strip()) > 0, "Translated English description is empty."
    print(f"Generated English (validation pending):\n{scenario_context.translated_english_text}")

@then(parsers.parse('the English description should mention {expected_mention}'))
def then_english_desc_mentions_feature(scenario_context: ScenarioContext, expected_mention: str):
    assert scenario_context.translated_english_text is not None, "No translated English output found."
    assert not scenario_context.translated_english_text.startswith("ERROR_TRANSLATING_TO_ENGLISH:"), \
        f"Translation to English failed: {scenario_context.translated_english_text}"
    assert expected_mention.lower() in scenario_context.translated_english_text.lower(), \
        f"Expected mention '{expected_mention}' not found in English output:\n{scenario_context.translated_english_text}"
