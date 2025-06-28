# Copyright (c) DarkLightX / Dana Edwards

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from pathlib import Path

# --- Placeholder for actual TauTranslator components ---
# This section will eventually import and use the real translator.
# For now, we use a placeholder function.

def placeholder_translate_english_to_formal(english_text: str, grammar_content: str) -> str:
    """
    Placeholder for the actual TauTranslator translation logic.
    This function simulates the translation process based on the provided
    English text and grammar content. It will be replaced with calls
    to the actual TauTranslator components in subsequent iterations.
    """
    # Basic checks to ensure grammar content is "used"
    if not grammar_content:
        raise ValueError("Grammar content cannot be empty for translation.")

    # Simplified rule-based translation for initial BDD setup.
    # This is NOT how the real translator works but helps test the BDD flow.
    if english_text == "P is true":
        return "P"
    elif english_text == "P is false":
        return "P'"
    elif english_text == "P and Q are true":
        return "P & Q"
    elif english_text == "P or Q is true":
        return "P | Q"
    elif english_text == "P is true and Q is false":
        return "P & Q'"
    elif english_text == "P is false or Q is true":
        return "P' | Q"
    elif english_text == "P is true and (Q is true or R is true)":
        # Assuming the placeholder can handle basic parenthesis from input
        # or the real translator would parse this structure.
        # For boolean.tgf, output should be "P & (Q | R)"
        return "P & (Q | R)"
    elif english_text == "it is not the case that P and Q are true":
        return "(P & Q)'"
    elif english_text == "Var1 is true":
        return "Var1"
    elif english_text == "P Q are true": # Tests space as conjunction
        return "P Q"
    else:
        # Fallback for unhandled cases by the placeholder
        return f"PLACEHOLDER_NO_RULE_FOR: {english_text}"

# --- End Placeholder ---


# Link to the feature file(s)
# The path is relative to `bdd_features_base_dir` set in pytest.ini (tests/features/)
# scenarios("boolean_logic/basic_boolean_translation.feature") # Disabled: Feature file not found

# Fixtures
@pytest.fixture
def grammar_fixtures_path() -> Path:
    """Provides the path to the grammar fixtures directory."""
    # Path is .../TauTranslator-main/tests/fixtures/grammars/
    return Path(__file__).parent.parent.parent / "fixtures" / "grammars"

@pytest.fixture
def scenario_context() -> dict:
    """A dictionary to store context data across steps in a scenario."""
    return {}

# Step Definitions

@given(parsers.parse('the system is configured with the "{grammar_name}" grammar'), target_fixture="scenario_context")
def given_system_configured_with_grammar(scenario_context: dict, grammar_fixtures_path: Path, grammar_name: str):
    """
    Loads the specified grammar file content into the scenario context.
    """
    grammar_file_path = grammar_fixtures_path / grammar_name
    if not grammar_file_path.is_file():
        raise FileNotFoundError(f"Grammar file not found: {grammar_file_path}")
    
    with open(grammar_file_path, 'r', encoding='utf-8') as f:
        scenario_context['grammar_content'] = f.read()
    scenario_context['grammar_name'] = grammar_name
    return scenario_context

@given(parsers.parse('the English input "{english_text}"'), target_fixture="scenario_context")
def given_english_input(scenario_context: dict, english_text: str):
    """
    Stores the English input string in the scenario context.
    """
    scenario_context['english_input'] = english_text
    return scenario_context

@when('the input is translated', target_fixture="scenario_context")
def when_input_is_translated(scenario_context: dict):
    """
    Performs the translation using the placeholder (or eventually, the real) translator.
    Stores the result in the scenario context.
    """
    english_text = scenario_context.get('english_input')
    grammar_content = scenario_context.get('grammar_content')

    if english_text is None:
        raise ValueError("English input not found in scenario context. Ensure 'Given the English input' step runs first.")
    if grammar_content is None:
        raise ValueError("Grammar content not found in scenario context. Ensure 'Given the system is configured' step runs first.")

    # --- Replace this with the actual call to TauTranslator ---
    translated_output = placeholder_translate_english_to_formal(english_text, grammar_content)
    # --- ---    
    scenario_context['translated_output'] = translated_output
    return scenario_context

@then(parsers.parse('the translated output should be "{expected_output}"'))
def then_translated_output_should_be(scenario_context: dict, expected_output: str):
    """
    Compares the actual translated output with the expected output.
    """
    actual_output = scenario_context.get('translated_output')
    
    if actual_output is None:
        raise ValueError("Translated output not found in scenario context. Ensure 'When the input is translated' step runs first.")
        
    assert actual_output == expected_output, \
        f"Translation mismatch: Expected '{expected_output}', but got '{actual_output}'"
