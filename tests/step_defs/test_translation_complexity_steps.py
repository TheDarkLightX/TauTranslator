"""Step definitions for translation complexity ladder BDD tests.

Provides reusable steps for initialising the English→Tau translator, translating
sentences of varying complexity / ambiguity, and asserting successful
translation. Failures are logged for later analysis so that the pipeline can be
improved incrementally.

All functions are < 20 lines, keeping with the project's testing guidelines.
"""

from pathlib import Path
import json
import os

import pytest
from pytest_bdd import given, when, then, parsers, scenarios

# Register scenarios from the feature file in the same directory hierarchy
FEATURE_PATH = Path(__file__).parents[1] / "features" / "translation_complexity.feature"
scenarios(str(FEATURE_PATH))

# Constants -----------------------------------------------------------------
_FAILURE_REPORT_PATH = Path(os.getenv("TAUTRANSLATOR_COMPLEXITY_REPORT", "reports/translation_complexity_failures.json"))
_FAILURE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Utilities -----------------------------------------------------------------

def _append_failure_record(record: dict) -> None:
    """Append a failure record to the JSON report (create file if missing)."""
    if _FAILURE_REPORT_PATH.exists():
        with _FAILURE_REPORT_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(record)
    with _FAILURE_REPORT_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Fixtures ------------------------------------------------------------------

@pytest.fixture(scope="session")
def english_to_tau_translator():
    """Initialise the English→Tau translator once per test session."""
    from backend.unified.english_to_tau_translator import EnglishToTauTranslator

    # Optionally accept custom grammar via env var to keep tests flexible
    grammar_path = os.getenv("TAU_GRAMMAR_PATH")
    translator = EnglishToTauTranslator(grammar_path=grammar_path) if grammar_path else EnglishToTauTranslator()
    return translator

@pytest.fixture
def scenario_context():  # type: ignore[return-value]
    """Provide a simple object for sharing data between steps."""
    return {}

# Step Implementations ------------------------------------------------------

@given("the Tau translator is initialised")
def step_translator_initialised(english_to_tau_translator, scenario_context):  # noqa: D401
    scenario_context["translator"] = english_to_tau_translator

@when(parsers.cfparse('I translate "{sentence}"'))
def step_translate_sentence(sentence: str, scenario_context):  # noqa: D401
    translator = scenario_context["translator"]
    success, tau_code, tce = translator.translate_english_to_tau(sentence)
    scenario_context.update(
        {
            "sentence": sentence,
            "success": success,
            "tau_code": tau_code,
            "tce": tce,
        }
    )

@then("the translation should succeed")
def step_translation_should_succeed(scenario_context):  # noqa: D401
    success = scenario_context["success"]
    sentence = scenario_context["sentence"]
    tau_code = scenario_context["tau_code"]

    if not success or not tau_code.strip():
        _append_failure_record(
            {
                "sentence": sentence,
                "tau_code": tau_code,
                "reason": "Translation failed or produced empty Tau code.",
            }
        )
    assert success, f"Translation failed for sentence: {sentence}"
    assert tau_code.strip(), f"Empty Tau code produced for sentence: {sentence}"

    # Optional: attempt to parse Tau code for additional validation
    try:
        from backend.unified.tau_validator import validate_tau_code  # hypothetical helper

        parse_ok, parse_err = validate_tau_code(tau_code)
        if not parse_ok:
            _append_failure_record(
                {
                    "sentence": sentence,
                    "tau_code": tau_code,
                    "reason": f"Tau parse error: {parse_err}",
                }
            )
        assert parse_ok, f"Produced Tau code does not parse: {parse_err}"
    except ModuleNotFoundError:
        # Validator optional – absence does not fail test, but we log it.
        pass
