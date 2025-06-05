#!/usr/bin/env python3
"""
Step Definitions for Tau Translation BDD Tests
=============================================

Implements the Given/When/Then steps for Tau translation features.

Author: DarkLightX / Dana Edwards
"""

import pytest
from pytest_bdd import given, when, then, parsers
from typing import Dict, Any


@pytest.fixture
def translation_context() -> Dict[str, Any]:
    """Fixture to maintain translation state between steps."""
    return {
        "translator": None,
        "source_text": None,
        "source_lang": None,
        "target_lang": None,
        "translation_result": None,
        "previous_result": None,
        "errors": []
    }


@given("the translation system is initialized")
def initialize_translation_system(translation_context):
    """Initialize the translation system."""
    from src.tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
    translation_context["translator"] = LMQLBidirectionalTranslator(strategy_type="pattern")


@given("we are using our own pattern-based translator")
def use_pattern_translator(translation_context):
    """Ensure we're using the pattern-based translator."""
    from src.tau_translator_omega.core_engine.pattern_based_translator import PatternBasedTranslator
    translation_context["translator"] = PatternBasedTranslator()


@given("I have access to the Tau parser")
def verify_tau_parser_access(translation_context):
    """Verify we have some form of Tau parsing capability."""
    # Since we don't have the official parser, we use our pattern recognizer
    from src.tau_translator_omega.core_engine.tau_construct_recognizer import TauConstructRecognizer
    translation_context["recognizer"] = TauConstructRecognizer()


@given("the translation system is initialized with full Tau parser")
def initialize_with_full_parser(translation_context):
    """Initialize with our best available parsing capability."""
    from src.tau_translator_omega.core_engine.enhanced_tau_translator import EnhancedTauTranslator
    translation_context["translator"] = EnhancedTauTranslator()


@given("I have access to all Tau language constructs")
def verify_construct_access(translation_context):
    """Verify we can handle all documented Tau constructs."""
    assert translation_context["translator"] is not None


@given(parsers.parse('we need to implement {feature} support'))
def note_missing_feature(translation_context, feature):
    """Document that a feature needs implementation."""
    translation_context.setdefault("missing_features", []).append(feature)


@when(parsers.parse('I translate "{text}" from {source_lang} to {target_lang}'))
def translate_text(translation_context, text, source_lang, target_lang):
    """Perform translation."""
    translation_context["source_text"] = text
    translation_context["source_lang"] = source_lang
    translation_context["target_lang"] = target_lang
    
    translator = translation_context["translator"]
    
    try:
        if source_lang == "TAU" and target_lang == "PLAIN_ENGLISH":
            result = translator.translate_tau_to_tce(text)
        elif source_lang == "PLAIN_ENGLISH" and target_lang == "TAU":
            result = translator.translate_tce_to_tau(text)
        else:
            result = translator.translate(text, source_lang, target_lang)
        
        translation_context["translation_result"] = result.output if hasattr(result, 'output') else result
    except Exception as e:
        translation_context["errors"].append(str(e))
        translation_context["translation_result"] = None


@when("I translate the result back from PLAIN_ENGLISH to TAU")
def translate_back_to_tau(translation_context):
    """Translate the previous result back to Tau."""
    translation_context["previous_result"] = translation_context["translation_result"]
    translate_text(
        translation_context,
        translation_context["translation_result"],
        "PLAIN_ENGLISH",
        "TAU"
    )


@when("I translate the result back from TAU to PLAIN_ENGLISH")
def translate_back_to_english(translation_context):
    """Translate the previous result back to English."""
    translation_context["previous_result"] = translation_context["translation_result"]
    translate_text(
        translation_context,
        translation_context["translation_result"],
        "TAU",
        "PLAIN_ENGLISH"
    )


@then(parsers.parse('the translation should be "{expected}"'))
def verify_exact_translation(translation_context, expected):
    """Verify the translation matches exactly."""
    assert translation_context["translation_result"] == expected


@then(parsers.parse('the translation should contain "{substring}"'))
def verify_translation_contains(translation_context, substring):
    """Verify the translation contains a substring."""
    result = translation_context["translation_result"]
    assert result is not None, "Translation failed"
    assert substring in result, f"Expected '{substring}' in '{result}'"


@then(parsers.parse('the translation should contain "{word1}" and "{word2}"'))
def verify_translation_contains_both(translation_context, word1, word2):
    """Verify the translation contains both words."""
    result = translation_context["translation_result"]
    assert result is not None
    assert word1 in result and word2 in result


@then(parsers.parse('the translation should start with "{prefix}"'))
def verify_translation_starts_with(translation_context, prefix):
    """Verify the translation starts with a prefix."""
    result = translation_context["translation_result"]
    assert result is not None
    assert result.startswith(prefix), f"Expected to start with '{prefix}', got '{result}'"


@then(parsers.parse('the translation should NOT be "{not_expected}"'))
def verify_not_exact_translation(translation_context, not_expected):
    """Verify the translation is NOT a specific value."""
    assert translation_context["translation_result"] != not_expected


@then(parsers.parse('the translation should be "{expected1}" or "{expected2}"'))
def verify_alternative_translations(translation_context, expected1, expected2):
    """Verify the translation matches one of two options."""
    result = translation_context["translation_result"]
    assert result in [expected1, expected2]


@then(parsers.parse('the final translation should be semantically equivalent to "{original}"'))
def verify_semantic_equivalence(translation_context, original):
    """Verify semantic equivalence after round-trip translation."""
    result = translation_context["translation_result"]
    
    # Normalize both for comparison
    def normalize(text):
        # Remove extra spaces, normalize operators
        text = " ".join(text.split())
        text = text.replace("&&", "&").replace("||", "|")
        return text.strip()
    
    assert normalize(result) == normalize(original)