#!/usr/bin/env python3
"""
Test script for bidirectional translation functionality
Tests all translation directions including reverse translation

Copyright: DarkLightX/Dana Edwards
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from domain.tau_parser_service import TauParserService
from domain.tau_to_english_translator import TauToEnglishService
from translators.bidirectional_engine import BidirectionalTranslationEngine
from translators.base import TranslationDirection


def test_tau_parser():
    """Test TAU parser functionality."""
    print("\n=== Testing TAU Parser ===")
    
    parser = TauParserService()
    
    test_cases = [
        "always (x > 0)",
        "forall x : x > 0",
        "exists y : y = x + 1",
        "solve {x, y} : x + y = 10",
        "if x > 0 then y = 1 else y = 0",
        "always (temperature < 100 and pressure > 50)"
    ]
    
    for tau_code in test_cases:
        print(f"\nParsing: {tau_code}")
        result = parser.parse_tau_code(tau_code)
        
        if result.is_success():
            print(f"✅ Success: {result.value}")
        else:
            print(f"❌ Error: {result.error}")


def test_tau_to_english():
    """Test TAU to English translation."""
    print("\n\n=== Testing TAU to English Translation ===")
    
    translator = TauToEnglishService()
    
    test_cases = [
        ("always (x > 0)", "it is always the case that x is greater than 0"),
        ("forall x : x > 0", "for all x, x is greater than 0"),
        ("exists y : y = x + 1", "there exists y, y equals x + 1"),
        ("solve {x} : x > 0", "find values for x such that x is greater than 0"),
        ("not (x = 0)", "not x equals 0"),
        ("x > 0 and y < 10", "x is greater than 0 and y is less than 10")
    ]
    
    for tau_code, expected in test_cases:
        print(f"\nTranslating: {tau_code}")
        result = translator.translate_tau_to_english(tau_code)
        
        if result.is_success():
            print(f"✅ Result: {result.value}")
            if expected:
                print(f"   Expected: {expected}")
        else:
            print(f"❌ Error: {result.error}")


def test_bidirectional_engine():
    """Test bidirectional translation engine."""
    print("\n\n=== Testing Bidirectional Translation Engine ===")
    
    engine = BidirectionalTranslationEngine()
    
    # Test English to TAU
    print("\n--- English to TAU ---")
    test_cases = [
        ("All users must have a password", TranslationDirection.TO_TAU),
        ("The temperature is always less than 100", TranslationDirection.TO_TAU),
        ("There exists a solution where x equals 5", TranslationDirection.TO_TAU)
    ]
    
    for text, direction in test_cases:
        print(f"\nTranslating: {text}")
        result = engine.translate(text, direction)
        
        if result.success:
            print(f"✅ TAU: {result.translated_text}")
            print(f"   Confidence: {result.confidence}")
            if result.metadata:
                print(f"   Pipeline: {result.metadata.get('pipeline', 'N/A')}")
        else:
            print(f"❌ Error: {result.error_message}")
    
    # Test TAU to English
    print("\n--- TAU to English ---")
    tau_examples = [
        ("always (x > 0)", TranslationDirection.TO_ENGLISH),
        ("forall user : has_password(user)", TranslationDirection.TO_ENGLISH),
        ("solve {x} : x * x = 16", TranslationDirection.TO_ENGLISH)
    ]
    
    for text, direction in tau_examples:
        print(f"\nTranslating: {text}")
        result = engine.translate(text, direction)
        
        if result.success:
            print(f"✅ English: {result.translated_text}")
            print(f"   Confidence: {result.confidence}")
        else:
            print(f"❌ Error: {result.error_message}")
    
    # Test bidirectional auto-detection
    print("\n--- Bidirectional Auto-Detection ---")
    mixed_examples = [
        "All numbers must be positive",  # English
        "always (temperature < threshold)",  # TAU
        "it is required that every user has an email",  # TCE
        "forall x : x > 0 implies f(x) > 0"  # TAU
    ]
    
    for text in mixed_examples:
        print(f"\nAuto-detecting and translating: {text}")
        result = engine.translate(text, TranslationDirection.BIDIRECTIONAL)
        
        if result.success:
            print(f"✅ Result: {result.translated_text}")
            print(f"   Direction: {result.direction.value}")
            print(f"   Method: {result.translation_method}")
        else:
            print(f"❌ Error: {result.error_message}")


def test_round_trip_translation():
    """Test round-trip translation (English → TAU → English)."""
    print("\n\n=== Testing Round-Trip Translation ===")
    
    engine = BidirectionalTranslationEngine()
    
    test_phrases = [
        "All users must have unique usernames",
        "The system temperature is always below the critical threshold",
        "There exists a configuration where all constraints are satisfied"
    ]
    
    for original in test_phrases:
        print(f"\nOriginal: {original}")
        
        # English to TAU
        tau_result = engine.translate(original, TranslationDirection.TO_TAU)
        if not tau_result.success:
            print(f"❌ Failed to translate to TAU: {tau_result.error_message}")
            continue
        
        tau_text = tau_result.translated_text
        print(f"TAU: {tau_text}")
        
        # TAU back to English
        english_result = engine.translate(tau_text, TranslationDirection.TO_ENGLISH)
        if not english_result.success:
            print(f"❌ Failed to translate back to English: {english_result.error_message}")
            continue
        
        back_to_english = english_result.translated_text
        print(f"Back to English: {back_to_english}")
        
        # Compare similarity (simple check)
        if original.lower() == back_to_english.lower():
            print("✅ Perfect round-trip!")
        else:
            print("⚠️  Round-trip produced different text (this is normal)")


if __name__ == "__main__":
    print("Testing Bidirectional Translation System")
    print("=" * 50)
    
    test_tau_parser()
    test_tau_to_english()
    test_bidirectional_engine()
    test_round_trip_translation()
    
    print("\n\nAll tests completed!")
    print("=" * 50)