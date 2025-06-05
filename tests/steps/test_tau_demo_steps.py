"""
BDD Step Definitions for Tau Demo Features
=========================================

Implements the step definitions for IDNI and taumorrow demo scenarios.
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import json
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.tau_translator_omega.lmql_engine.bidirectional_translator import (
    LMQLBidirectionalTranslator
)
from src.tau_translator_omega.lmql_engine.translation_strategies import (
    TranslationDirection,
    TranslationStrategyFactory
)

# Load all tau demo feature scenarios
scenarios('../features/translation/tau_solver_demo.feature')
scenarios('../features/translation/taumorrow_demos.feature')


# Fixtures
@pytest.fixture
def demo_context():
    """Context object to store demo translation state."""
    return {
        'translator': LMQLBidirectionalTranslator(strategy_type="pattern"),
        'tau_input': None,
        'english_output': None,
        'english_input': None,
        'tau_output': None,
        'errors': [],
        'warnings': []
    }


# Given steps
@given('the translation system is initialized')
def given_translation_system_initialized(demo_context):
    """Initialize the translation system."""
    # Already initialized in the fixture
    pass


@given('I have access to the Tau parser')
def given_tau_parser_access(demo_context):
    """Confirm Tau parser access."""
    # Parser is available through the translator
    pass


@given('I am working with taumorrow demo files')
def given_taumorrow_demo_files(demo_context):
    """Confirm working with taumorrow demos."""
    # No special setup needed
    pass


@given(parsers.parse('I have Tau code "{tau_code}"'))
def given_tau_code(demo_context, tau_code):
    """Set the Tau code input."""
    demo_context['tau_input'] = tau_code.strip()


@given(parsers.parse('I have the statement "{english_text}"'))
def given_english_statement(demo_context, english_text):
    """Set the English text input."""
    demo_context['english_input'] = english_text.strip()


# When steps
@when(parsers.parse('I translate "{text}" from {source_lang} to {target_lang}'))
def when_translate_text(demo_context, text, source_lang, target_lang):
    """Translate text between languages."""
    translator = demo_context['translator']
    
    # Determine direction
    if source_lang == "TAU" and target_lang == "PLAIN_ENGLISH":
        direction = TranslationDirection.TAU_TO_TCE
        demo_context['tau_input'] = text
    elif source_lang == "PLAIN_ENGLISH" and target_lang == "TAU":
        direction = TranslationDirection.TCE_TO_TAU
        demo_context['english_input'] = text
    else:
        demo_context['errors'].append(f"Unsupported translation: {source_lang} to {target_lang}")
        return
    
    try:
        if direction == TranslationDirection.TAU_TO_TCE:
            result = translator.translate_tau_to_tce(text)
            if result.success:
                demo_context['english_output'] = result.output
            else:
                demo_context['errors'] = result.errors
        else:
            result = translator.translate_tce_to_tau(text)
            if result.success:
                demo_context['tau_output'] = result.output
            else:
                demo_context['errors'] = result.errors
    except Exception as e:
        demo_context['errors'].append(str(e))


@when('I translate the result back from PLAIN_ENGLISH to TAU')
def when_translate_back_to_tau(demo_context):
    """Translate the previous English output back to Tau."""
    translator = demo_context['translator']
    english_text = demo_context['english_output']
    
    if not english_text:
        demo_context['errors'].append("No English output to translate back")
        return
    
    try:
        result = translator.translate_tce_to_tau(english_text)
        if result.success:
            demo_context['tau_output'] = result.output
        else:
            demo_context['errors'] = result.errors
    except Exception as e:
        demo_context['errors'].append(str(e))


@when('I translate from Tau to English')
def when_translate_tau_to_english(demo_context):
    """Translate from Tau to English."""
    translator = demo_context['translator']
    tau_code = demo_context['tau_input']
    
    try:
        result = translator.translate_tau_to_tce(tau_code)
        if result.success:
            demo_context['english_output'] = result.output
        else:
            demo_context['errors'] = result.errors
    except Exception as e:
        demo_context['errors'].append(str(e))


@when('I translate from English to Tau')
def when_translate_english_to_tau(demo_context):
    """Translate from English to Tau."""
    translator = demo_context['translator']
    english_text = demo_context['english_input']
    
    try:
        result = translator.translate_tce_to_tau(english_text)
        if result.success:
            demo_context['tau_output'] = result.output
        else:
            demo_context['errors'] = result.errors
    except Exception as e:
        demo_context['errors'].append(str(e))


# Then steps
@then(parsers.parse('the translation should be "{expected_output}"'))
def then_translation_should_be(demo_context, expected_output):
    """Check if the translation matches expected output."""
    actual_output = demo_context.get('english_output') or demo_context.get('tau_output')
    
    if demo_context['errors']:
        pytest.fail(f"Translation errors: {demo_context['errors']}")
    
    assert actual_output is not None, "No translation output produced"
    
    # Normalize whitespace for comparison
    actual = ' '.join(actual_output.split())
    expected = ' '.join(expected_output.split())
    
    assert actual == expected, f"Expected: {expected}, Got: {actual}"


@then(parsers.parse('I should get "{expected_output}"'))
def then_check_output(demo_context, expected_output):
    """Check if the output matches expected."""
    actual_output = demo_context.get('english_output') or demo_context.get('tau_output')
    
    if demo_context['errors']:
        pytest.fail(f"Translation errors: {demo_context['errors']}")
    
    assert actual_output is not None, "No translation output produced"
    
    # Normalize whitespace for comparison
    actual = ' '.join(actual_output.split())
    expected = ' '.join(expected_output.split())
    
    assert actual == expected, f"Expected: {expected}, Got: {actual}"


@then(parsers.parse('the translation should contain "{expected_text}"'))
def then_translation_contains(demo_context, expected_text):
    """Check if the translation contains expected text."""
    actual_output = demo_context.get('english_output') or demo_context.get('tau_output')
    
    if demo_context['errors']:
        pytest.fail(f"Translation errors: {demo_context['errors']}")
    
    assert actual_output is not None, "No translation output produced"
    assert expected_text in actual_output, f"Expected text '{expected_text}' not found in output: {actual_output}"


@then('the translation should mention solving for variables')
def then_translation_mentions_solving(demo_context):
    """Check if the translation mentions solving for variables."""
    output = demo_context.get('english_output')
    
    if demo_context['errors']:
        pytest.fail(f"Translation errors: {demo_context['errors']}")
    
    assert output is not None, "No translation output produced"
    
    solving_keywords = ['find', 'solve', 'value', 'such that']
    found_keyword = any(keyword in output.lower() for keyword in solving_keywords)
    
    assert found_keyword, f"Translation doesn't mention solving: {output}"


@then('the translation should describe a type annotation')
def then_translation_describes_type(demo_context):
    """Check if the translation describes a type annotation."""
    output = demo_context.get('english_output')
    
    if demo_context['errors']:
        pytest.fail(f"Translation errors: {demo_context['errors']}")
    
    assert output is not None, "No translation output produced"
    
    type_keywords = ['type', 'integer', 'nat', 'natural number']
    found_keyword = any(keyword in output.lower() for keyword in type_keywords)
    
    assert found_keyword, f"Translation doesn't describe type: {output}"


@then('the translation should describe a temporal rule')
def then_translation_describes_temporal_rule(demo_context):
    """Check if the translation describes a temporal rule."""
    output = demo_context.get('english_output')
    
    if demo_context['errors']:
        pytest.fail(f"Translation errors: {demo_context['errors']}")
    
    assert output is not None, "No translation output produced"
    
    temporal_keywords = ['time', 'at time', 'rule', 'equals', 'output']
    found_keywords = sum(1 for keyword in temporal_keywords if keyword in output.lower())
    
    assert found_keywords >= 2, f"Translation doesn't describe temporal rule: {output}"


@then('the translation should describe stream definitions')
def then_translation_describes_streams(demo_context):
    """Check if the translation describes stream definitions."""
    output = demo_context.get('english_output')
    
    if demo_context['errors']:
        pytest.fail(f"Translation errors: {demo_context['errors']}")
    
    assert output is not None, "No translation output produced"
    
    stream_keywords = ['stream', 'input', 'output', 'file', 'reads', 'writes']
    found_keyword = any(keyword in output.lower() for keyword in stream_keywords)
    
    assert found_keyword, f"Translation doesn't describe streams: {output}"


@then('the translation should describe logic gates')
def then_translation_describes_logic_gates(demo_context):
    """Check if the translation describes logic gates."""
    output = demo_context.get('english_output')
    
    if demo_context['errors']:
        pytest.fail(f"Translation errors: {demo_context['errors']}")
    
    assert output is not None, "No translation output produced"
    
    gate_keywords = ['and', 'or', 'xor', 'gate', 'logic']
    found_keyword = any(keyword in output.lower() for keyword in gate_keywords)
    
    assert found_keyword, f"Translation doesn't describe logic gates: {output}"


@then('the translation should describe voting')
def then_translation_describes_voting(demo_context):
    """Check if the translation describes voting."""
    output = demo_context.get('english_output')
    
    if demo_context['errors']:
        pytest.fail(f"Translation errors: {demo_context['errors']}")
    
    assert output is not None, "No translation output produced"
    
    voting_keywords = ['vote', 'majority', 'democracy', 'consensus']
    found_keyword = any(keyword in output.lower() for keyword in voting_keywords)
    
    assert found_keyword, f"Translation doesn't describe voting: {output}"