"""
Step definitions for Natural Language to TCE translation.
Copyright: DarkLightX/Dana Edwards
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load scenarios
scenarios('../features/translation/natural_language_to_tce.feature')


@pytest.fixture
def translator():
    """Create Natural Language to TCE translator."""
    from backend.unified.domain.nl_to_tce_translator import NaturalLanguageToTCETranslator
    return NaturalLanguageToTCETranslator()


@given('I have a natural language to TCE translator')
def given_translator(translator):
    """Ensure translator is available."""
    assert translator is not None


@when(parsers.parse('I translate "{input_text}" to TCE'))
def when_translate(translator, input_text):
    """Translate natural language to TCE."""
    result = translator.translate_to_tce(input_text)
    # Store result in pytest context
    pytest.translation_result = result


@then(parsers.parse('the TCE output should be "{expected_output}"'))
def then_check_output(expected_output):
    """Verify TCE output matches expected."""
    assert pytest.translation_result == expected_output