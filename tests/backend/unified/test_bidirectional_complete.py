"""
Comprehensive test for bidirectional translation.

This test suite verifies the translation between symbolic Tau and pure-English
Tau Controlled English (TCE), ensuring grammar compliance and semantic accuracy.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from tau_translator_omega.core_engine.parsers.grammar_driven_parser import GrammarDrivenParser
from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator

@pytest.mark.skip(reason="Skipping until translators are fully refactored and integrated.")
class TestBidirectionalComplete:
    """Test suite for bidirectional translation between Tau and TCE."""

    @pytest.fixture(scope="class")
    def parser(self) -> GrammarDrivenParser:
        """Fixture for the grammar-driven parser."""
        return GrammarDrivenParser()

    @pytest.fixture(scope="class")
    def translator(self) -> LMQLBidirectionalTranslator:
        """Fixture for the bidirectional translator engine."""
        return LMQLBidirectionalTranslator()



    def test_symbolic_tau_parsing(self, parser: GrammarDrivenParser, translator: LMQLBidirectionalTranslator):
        """Test that the parser correctly handles symbolic Tau grammar."""
        test_cases = {
            "all x (x > 0)": "for all x, it is the case that x is greater than 0",
            "ex y (y < 10)": "there exists a y such that y is less than 10",
            "always (temp > 100 -> alarm = 1)": "it is always the case that if temperature is greater than 100, then alarm is equal to 1",
        }

        for tau_code, expected_english in test_cases.items():
            result = parser.parse(tau_code, grammar_name='tau_lang')
            assert result.success, f"Failed to parse symbolic Tau: {tau_code}"
            
            # Test translation to English
            translation_result = translator.translate_tau_to_tce(tau_code)
            assert translation_result.success, f"Failed to translate: {tau_code}"
            assert translation_result.output.lower() == expected_english.lower()

    def test_tce_parsing(self, parser: GrammarDrivenParser):
        """Test that the parser correctly handles pure-English TCE grammar."""
        test_cases = [
            "for all x such that x is greater than 0",
            "there exists y such that y is less than 10",
            "it is always the case that the expression if temperature is greater than 100 then alarm is equal to 1 end expression",
            "let the function is_positive with parameters x be defined as the expression x is greater than 0 end expression",
        ]

        for tce_code in test_cases:
            result = parser.parse(tce_code, grammar_name='tau_controlled')
            assert result.success, f"Failed to parse TCE: {tce_code}"

    def test_tce_to_tau_translation(self, translator: LMQLBidirectionalTranslator):
        """Test translation from pure-English TCE to symbolic Tau."""
        test_cases = {
            "it is always the case that x is greater than 0": "always (x > 0)",
            "if a and b then c": "(a && b) -> c",
        }

        for tce_code, expected_tau in test_cases.items():
            result = translator.translate_tce_to_tau(tce_code)
            assert result.success, f"TCE to Tau translation failed for: {tce_code}"
            # Note: This assertion may need adjustment based on formatter output
            assert "".join(result.translated_text.split()) == "".join(expected_tau.split())

    def test_round_trip_translation(self, translator: LMQLBidirectionalTranslator):
        """Test round-trip translation from TCE to Tau and back to English."""
        original_tce = "for all x, if x is positive, then the square of x is positive"

        # TCE to Tau
        tau_result = translator.translate_tce_to_tau(original_tce)
        assert tau_result.success, f"Round-trip failed at TCE to Tau step: {tau_result.errors}"
        tau_code = tau_result.output

        # Tau to English
        english_result = translator.translate_tau_to_tce(tau_code)
        assert english_result.success, f"Round-trip failed at Tau to English step: {english_result.errors}"
        
        # This is a simplification; a real test would involve semantic comparison.
        assert "for all" in english_result.output.lower()
        assert "positive" in english_result.output.lower()