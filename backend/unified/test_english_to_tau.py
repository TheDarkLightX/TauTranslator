#!/usr/bin/env python3
"""
Test English to Tau translation using existing components.
Copyright: DarkLightX/Dana Edwards
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import what we need
from backend.unified.translators.base import TranslationDirection
from backend.unified.domain.nlp_types import NaturalLanguageText
from backend.unified.domain.nlp_translation_service import NLPTranslationService

# Import the TCE to Tau translator
from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser


def translate_english_to_tau(english_text: str) -> str:
    """Translate English to Tau using existing components."""
    print(f"\nInput (English): {english_text}")
    
    # Step 1: English to TCE using NLP service
    nlp_service = NLPTranslationService()
    nl_text = NaturalLanguageText(english_text)
    tce_result = nlp_service.translate_nl_to_tce(nl_text)
    
    if not tce_result.success:
        print(f"Failed to convert to TCE: {tce_result.error_message}")
        return ""
    
    tce_text = tce_result.output_text
    print(f"Intermediate (TCE): {tce_text}")
    
    # Step 2: Parse TCE
    parser = CNLParser()
    ast = parser.parse(tce_text)
    
    if not ast:
        print("Failed to parse TCE")
        return ""
    
    # Step 3: TCE to Tau
    translator = TCETauTranslator()
    tau_result = translator.translate(ast)
    
    if tau_result.errors:
        print(f"Translation errors: {tau_result.errors}")
        return ""
    
    print(f"Output (Tau): {tau_result.tau_code}")
    return tau_result.tau_code


def main():
    """Test various English to Tau translations."""
    print("=== English to Tau Translation Test ===")
    
    test_cases = [
        # Simple facts
        "x equals 5",
        "temperature is 25",
        
        # Boolean operations
        "x and y",
        "a or b", 
        "not p",
        
        # Comparisons
        "x is greater than 10",
        "y is less than 5",
        "z is at least 0",
        
        # Conditionals
        "if x then y",
        "if temperature is high then turn on cooling",
        
        # Quantifiers
        "for all x, x equals x",
        "there exists y such that y is prime",
        
        # Complex
        "all users must have valid passwords",
        "the system shall always respond within 5 seconds",
    ]
    
    success_count = 0
    
    for i, english in enumerate(test_cases, 1):
        print(f"\n--- Test {i} ---")
        tau = translate_english_to_tau(english)
        if tau:
            success_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Successful translations: {success_count}/{len(test_cases)}")


if __name__ == "__main__":
    main()