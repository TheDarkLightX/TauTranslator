"""
Unit tests for Natural Language to TCE Translator.
Copyright: DarkLightX/Dana Edwards
"""

import pytest
from backend.unified.domain.nl_to_tce_translator import NaturalLanguageToTCETranslator


class TestNaturalLanguageToTCETranslator:
    """Test Natural Language to TCE translation."""
    
    @pytest.fixture
    def translator(self):
        """Create translator instance."""
        return NaturalLanguageToTCETranslator()
    
    def test_simple_assignment_equals(self, translator):
        """Test x equals 5."""
        result = translator.translate_to_tce("x equals 5")
        assert result == "x = 5."
    
    def test_simple_assignment_is(self, translator):
        """Test temperature is 25."""
        result = translator.translate_to_tce("temperature is 25")
        assert result == "temperature = 25."
    
    def test_boolean_and(self, translator):
        """Test x and y."""
        result = translator.translate_to_tce("x and y")
        assert result == "x and y."
    
    def test_boolean_or(self, translator):
        """Test a or b."""
        result = translator.translate_to_tce("a or b")
        assert result == "a or b."
    
    def test_boolean_not(self, translator):
        """Test not p."""
        result = translator.translate_to_tce("not p")
        assert result == "not p."
    
    def test_greater_than(self, translator):
        """Test x is greater than 10."""
        result = translator.translate_to_tce("x is greater than 10")
        assert result == "x > 10."
    
    def test_less_than(self, translator):
        """Test y is less than 5."""
        result = translator.translate_to_tce("y is less than 5")
        assert result == "y < 5."
    
    def test_at_least(self, translator):
        """Test z is at least 0."""
        result = translator.translate_to_tce("z is at least 0")
        assert result == "z >= 0."
    
    def test_at_most(self, translator):
        """Test w is at most 100."""
        result = translator.translate_to_tce("w is at most 100")
        assert result == "w <= 100."
    
    def test_simple_conditional(self, translator):
        """Test if x then y."""
        result = translator.translate_to_tce("if x then y")
        assert result == "if x then y."
    
    def test_conditional_with_comparison(self, translator):
        """Test if temperature is greater than 30 then cooling is on."""
        result = translator.translate_to_tce("if temperature is greater than 30 then cooling is on")
        assert result == "if temperature > 30 then cooling = on."
    
    def test_universal_quantification_all(self, translator):
        """Test for all x, x equals x."""
        result = translator.translate_to_tce("for all x, x equals x")
        assert result == "for all x, x = x."
    
    def test_universal_quantification_every(self, translator):
        """Test for every student, student has id."""
        result = translator.translate_to_tce("for every student, student has id")
        assert result == "for all student, student has id."
    
    def test_existential_quantification(self, translator):
        """Test there exists x such that x is prime."""
        result = translator.translate_to_tce("there exists x such that x is prime")
        assert result == "exists x such that x is prime."
    
    def test_temporal_always(self, translator):
        """Test always system is secure."""
        result = translator.translate_to_tce("always system is secure")
        assert result == "always system is secure."
    
    def test_temporal_sometimes(self, translator):
        """Test sometimes door is open."""
        result = translator.translate_to_tce("sometimes door is open")
        assert result == "sometimes door is open."
    
    def test_complex_requirement(self, translator):
        """Test all users must have valid passwords."""
        result = translator.translate_to_tce("all users must have valid passwords")
        assert result == "for all users, users have valid passwords."
    
    def test_mathematical_expression(self, translator):
        """Test x plus y equals z."""
        result = translator.translate_to_tce("x plus y equals z")
        assert result == "x + y = z."
    
    def test_multiple_conditions(self, translator):
        """Test x is greater than 0 and y is less than 10."""
        result = translator.translate_to_tce("x is greater than 0 and y is less than 10")
        assert result == "x > 0 and y < 10."


if __name__ == "__main__":
    # Run a quick test
    translator = NaturalLanguageToTCETranslator()
    
    test_cases = [
        "x equals 5",
        "x and y",
        "not p",
        "x is greater than 10",
        "if x then y",
        "for all x, x equals x",
        "there exists x such that x is prime",
        "all users must have valid passwords",
    ]
    
    print("=== Natural Language to TCE Tests ===\n")
    for nl in test_cases:
        tce = translator.translate_to_tce(nl)
        print(f"NL:  {nl}")
        print(f"TCE: {tce}")
        print()