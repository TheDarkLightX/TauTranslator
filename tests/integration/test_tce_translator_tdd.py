"""
TDD Tests for TCE to TAU Translation
====================================

Test-driven development tests for core TCE to TAU translation functionality.
"""

import pytest


class TestTCETranslator:
    """TDD tests for core TCE translator."""
    
    def test_translate_basic_fact(self):
        """Test: x = 5. -> x = 5"""
        translator = TCETranslator()
        result = translator.translate("x = 5.")
        assert result == "x = 5"
    
    def test_translate_and_operation(self):
        """Test: x and y. -> x & y"""
        translator = TCETranslator()
        result = translator.translate("x and y.")
        assert result == "x & y"
    
    def test_translate_or_operation(self):
        """Test: x or y. -> x \\ y"""
        translator = TCETranslator()
        result = translator.translate("x or y.")
        assert result == "x \\ y"
    
    def test_translate_xor_operation(self):
        """Test: x xor y. -> x + y"""
        translator = TCETranslator()
        result = translator.translate("x xor y.")
        assert result == "x + y"
    
    def test_translate_not_operation(self):
        """Test: not x. -> x'"""
        translator = TCETranslator()
        result = translator.translate("not x.")
        assert result == "x'"
    
    def test_translate_complex_boolean(self):
        """Test: (x and y) or z. -> (x & y) \\ z"""
        translator = TCETranslator()
        result = translator.translate("(x and y) or z.")
        assert result == "(x & y) \\ z"
    
    def test_missing_period_error(self):
        """Test error on missing period."""
        translator = TCETranslator()
        with pytest.raises(ValueError, match="^Input must end with period$"):
            translator.translate("x = 5")
    
    def test_empty_input_error(self):
        """Test error on empty input."""
        translator = TCETranslator()
        with pytest.raises(ValueError, match="^Input cannot be empty$"):
            translator.translate("")


class TCETranslator:
    """Core TCE to TAU translator - GREEN phase of TDD."""
    
    def translate(self, tce_input: str) -> str:
        """Translate TCE to TAU."""
        # GREEN: Make tests pass with minimal implementation
        
        # Validation
        if not tce_input:
            raise ValueError("Input cannot be empty")
        
        if not tce_input.strip().endswith('.'):
            raise ValueError("Input must end with period")
        
        # Remove period for processing
        text = tce_input.strip()[:-1]
        
        # Simple string replacements
        text = text.replace(" xor ", " + ")
        text = text.replace(" and ", " & ")
        text = text.replace(" or ", " \\ ")
        
        # Handle "not" prefix
        if text.startswith("not "):
            text = text[4:] + "'"
        
        return text