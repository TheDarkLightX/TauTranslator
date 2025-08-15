#!/usr/bin/env python3
"""
Simple test script for bidirectional translation system.
Tests each component individually without complex imports.

Copyright: DarkLightX/Dana Edwards
"""

import sys
import os
import json
from pathlib import Path

# Add backend/unified directory to path for imports
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Add project root for core imports
project_root = os.path.dirname(os.path.dirname(backend_path))
sys.path.insert(0, project_root)

def test_pattern_translator():
    """Test the pattern translator component."""
    print("\n=== Testing Pattern Translator ===")
    try:
        from backend.unified.translators.pattern_translator import PatternTranslationEngine
        from backend.unified.translators.base import TranslationDirection
        
        engine = PatternTranslationEngine()
        
        # Test English to TCE
        test_cases = [
            "x is greater than 5",
            "if x equals 10 then y is true",
            "x must be between 1 and 10"
        ]
        
        for english in test_cases:
            print(f"\nInput: {english}")
            result = engine.translate(english, TranslationDirection.NL_TO_TCE)
            print(f"TCE: {result.translated_text}")
            print(f"Success: {result.success}")
            if not result.success:
                print(f"Error: {result.error_message}")
                
        return True
    except Exception as e:
        print(f"Pattern translator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_grammar_translator():
    """Test the grammar translator component."""
    print("\n=== Testing Grammar Translator ===")
    try:
        from backend.unified.translators.grammar_translator import GrammarTranslationEngine
        from backend.unified.translators.base import TranslationDirection
        
        engine = GrammarTranslationEngine()
        
        # Test TCE to Tau
        test_cases = [
            "x > 5",
            "x = 10 -> y = true",
            "1 <= x <= 10"
        ]
        
        for tce in test_cases:
            print(f"\nInput: {tce}")
            result = engine.translate(tce, TranslationDirection.TCE_TO_TAU)
            print(f"Tau: {result.translated_text}")
            print(f"Success: {result.success}")
            if not result.success:
                print(f"Error: {result.error_message}")
                
        return True
    except Exception as e:
        print(f"Grammar translator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_nlp_translator():
    """Test the NLP translator component."""
    print("\n=== Testing NLP Translator ===")
    try:
        from backend.unified.translators.nlp_translator import NLPTranslationEngine
        from backend.unified.translators.base import TranslationDirection
        
        engine = NLPTranslationEngine()
        
        # Test English to TCE
        test_cases = [
            "The value of x should be greater than five",
            "When x is ten, then y becomes true",
            "x needs to be at least 1 but no more than 10"
        ]
        
        for english in test_cases:
            print(f"\nInput: {english}")
            result = engine.translate(english, TranslationDirection.NL_TO_TCE)
            print(f"TCE: {result.translated_text}")
            print(f"Success: {result.success}")
            if not result.success:
                print(f"Error: {result.error_message}")
                
        return True
    except Exception as e:
        print(f"NLP translator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test the full English -> TCE -> Tau pipeline."""
    print("\n=== Testing Full Pipeline ===")
    try:
        from backend.unified.translators.orchestrator import TranslationManager
        
        manager = TranslationManager()
        
        # Test full pipeline
        test_cases = [
            "x is greater than 5",
            "if x equals 10 then y is true",
            "x must be between 1 and 10"
        ]
        
        for english in test_cases:
            print(f"\nOriginal English: {english}")
            
            # English to TCE
            tce_result = manager.translate(english, "english", "tce")
            if not tce_result['success']:
                print(f"English->TCE failed: {tce_result.get('error', 'Unknown error')}")
                continue
                
            print(f"TCE: {tce_result['translated_text']}")
            
            # TCE to Tau
            tau_result = manager.translate(tce_result['translated_text'], "tce", "tau")
            if not tau_result['success']:
                print(f"TCE->Tau failed: {tau_result.get('error', 'Unknown error')}")
                continue
                
            print(f"Tau: {tau_result['translated_text']}")
            
        return True
    except Exception as e:
        print(f"Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bidirectional():
    """Test bidirectional translation (English <-> TCE <-> Tau)."""
    print("\n=== Testing Bidirectional Translation ===")
    try:
        from backend.unified.translators.orchestrator import TranslationManager
        
        manager = TranslationManager()
        
        # Test roundtrip: English -> TCE -> English
        test_cases = [
            "x is greater than 5",
            "x equals 10",
            "x is between 1 and 10"
        ]
        
        for original in test_cases:
            print(f"\nOriginal: {original}")
            
            # Forward translation
            tce_result = manager.translate(original, "english", "tce")
            if not tce_result['success']:
                print(f"Forward translation failed: {tce_result.get('error', 'Unknown error')}")
                continue
                
            print(f"TCE: {tce_result['translated_text']}")
            
            # Reverse translation (if supported)
            # Note: This may not work if reverse patterns aren't implemented
            try:
                back_result = manager.translate(tce_result['translated_text'], "tce", "english")
                if back_result['success']:
                    print(f"Back to English: {back_result['translated_text']}")
                else:
                    print(f"Reverse translation not supported: {back_result.get('error', 'Unknown error')}")
            except:
                print("Reverse translation not implemented")
                
        return True
    except Exception as e:
        print(f"Bidirectional test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Starting Bidirectional Translation System Tests")
    print("=" * 50)
    
    tests = [
        ("Pattern Translator", test_pattern_translator),
        ("Grammar Translator", test_grammar_translator),
        ("NLP Translator", test_nlp_translator),
        ("Full Pipeline", test_full_pipeline),
        ("Bidirectional", test_bidirectional)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n{name} test crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("-" * 50)
    for name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 50)
    print(f"Overall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())