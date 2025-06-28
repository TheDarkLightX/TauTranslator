"""Golden tests for quantifier + relative‐clause translation.

These lock the behaviour of the helper added in
`EnglishToTauTranslator._quantifier_relative_to_tau` so future refactors
cannot break the deterministic mapping to Tau.
"""
from backend.unified.english_to_tau_translator import EnglishToTauTranslator
import pytest

translator = EnglishToTauTranslator()

# (english sentence, expected tau code)
CASES = [
    (
        "Every user who has administrator privileges must authenticate with two factors.",
        "forall user ( administrator_privileges(user) -> authenticate_with_two_factors(user) ).",
    ),
    (
        "Each transaction that exceeds ten-thousand credits shall be logged before completion.",
        "forall transaction ( exceeds_ten-thousand_credits(transaction) -> be_logged_before_completion(transaction) ).",
    ),
]


@pytest.mark.parametrize("english,expected", CASES)
def test_quantifier_relative_translation(english: str, expected: str) -> None:
    success, tau, _ = translator.translate_english_to_tau(english)
    assert success, f"Translation failed for: {english}"
    assert tau == expected
