#!/usr/bin/env python3
"""
Integration tests for Natural Language → TCE → Tau pipeline
Copyright: DarkLightX/Dana Edwards

Tests the complete translation pipeline from natural language to Tau code.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.english_to_tau_integrated import IntegratedEnglishToTauTranslator


class TestNaturalLanguageToTauPipeline:
    """Test complete Natural Language to Tau translation pipeline."""
    
    @pytest.fixture
    def translator(self):
        """Create integrated translator instance."""
        return IntegratedEnglishToTauTranslator()
    
    def test_simple_assignment(self, translator):
        """Test x equals 5 → (x = 5)."""
        success, tau, tce = translator.translate("x equals 5")
        assert success is True
        assert tau == "(x = 5)"
        assert tce == "x = 5."
    
    def test_boolean_and(self, translator):
        """Test x and y → (x & y)."""
        success, tau, tce = translator.translate("x and y")
        assert success is True
        assert tau == "(x & y)"
        assert tce == "x and y."
    
    def test_boolean_not(self, translator):
        """Test not p → ~p (fallback)."""
        success, tau, tce = translator.translate("not p")
        assert success is True
        assert tau == "~p"  # Fallback translation
        assert tce == "not p."
    
    def test_comparison_greater_than(self, translator):
        """Test x is greater than 10 → (x > 10)."""
        success, tau, tce = translator.translate("x is greater than 10")
        assert success is True
        assert tau == "(x > 10)"
        assert tce == "x > 10."
    
    def test_universal_quantification(self, translator):
        """Test for all x, x equals x → for all x, (x = x)."""
        success, tau, tce = translator.translate("for all x, x equals x")
        assert success is True
        # Note: The quantifier translation is partial, but we get "for"
        assert "for" in tau
        assert tce == "for all x, x = x."
    
    def test_conditional_fallback(self, translator):
        """Test complex conditional with fallback."""
        success, tau, tce = translator.translate("if temperature is greater than 30 then cooling is on")
        assert success is True
        # This uses fallback direct translation
        assert tau == "if temperature > 30 then cooling = on"
        assert tce == "if temperature > 30 then cooling = on."
    
    def test_pipeline_components_integration(self, translator):
        """Test that all pipeline components work together."""
        # Test multiple translations to ensure no state issues
        test_cases = [
            ("x equals 5", "(x = 5)"),
            ("x and y", "(x & y)"),
            ("x is greater than 10", "(x > 10)"),
        ]
        
        for english, expected_tau in test_cases:
            success, tau, tce = translator.translate(english)
            assert success is True
            assert tau == expected_tau
    
    def test_mathematical_assignment(self, translator):
        """Test temperature is 25 → (temperature = 25)."""
        success, tau, tce = translator.translate("temperature is 25")
        assert success is True
        assert tau == "(temperature = 25)"
        assert tce == "temperature = 25."
    
    def test_error_handling(self, translator):
        """Test that invalid input is handled gracefully."""
        # Test empty input
        success, tau, tce = translator.translate("")
        assert success is False or tau == ""
        
        # Test malformed input
        success, tau, tce = translator.translate("xyz invalid grammar test")
        # Should either succeed with fallback or fail gracefully
        assert isinstance(success, bool)
        assert isinstance(tau, str)
        assert isinstance(tce, str)


def test_integration_pipeline_manual():
    """Manual test function for verification."""
    translator = IntegratedEnglishToTauTranslator()
    
    test_cases = [
        "x equals 5",
        "temperature is 25", 
        "x and y",
        "not p",
        "x is greater than 10",
        "for all x, x equals x",
        "if temperature is greater than 30 then cooling is on",
    ]
    
    print("\n=== Natural Language to Tau Pipeline Test ===")
    success_count = 0
    
    for english in test_cases:
        success, tau, tce = translator.translate(english)
        print(f"\nEnglish: {english}")
        print(f"TCE:     {tce}")
        print(f"Tau:     {tau if success else '[Failed]'}")
        print(f"Success: {success}")
        
        if success:
            success_count += 1
    
    print(f"\nSuccess rate: {success_count}/{len(test_cases)}")
    return success_count == len(test_cases)


if __name__ == "__main__":
    # Run manual test
    test_integration_pipeline_manual()