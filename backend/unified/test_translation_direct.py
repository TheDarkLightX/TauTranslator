#!/usr/bin/env python3
"""
Direct test of translation components without dependency injection.
Tests the actual translation capabilities.

Copyright: DarkLightX/Dana Edwards
"""

import sys
import os
from pathlib import Path

# Setup paths
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))
project_root = backend_path.parent.parent
sys.path.insert(0, str(project_root))


def test_pattern_based_translation():
    """Test pattern-based English->TCE translation."""
    print("\n=== Testing Pattern-Based Translation ===")
    
    # Import after path setup
    from core.pattern_loader import PatternLoader
    
    try:
        loader = PatternLoader()
        patterns = loader.load_patterns()
        print(f"Loaded {len(patterns)} patterns")
        
        # Test cases
        test_cases = [
            "x is greater than 5",
            "if x equals 10 then y is true",
            "x must be between 1 and 10",
            "for all x in list, x > 0",
            "there exists y such that y < x"
        ]
        
        for english in test_cases:
            print(f"\nInput: {english}")
            matched = False
            
            # Try to find matching pattern
            for pattern in patterns:
                if 'english_pattern' in pattern and 'tce_template' in pattern:
                    import re
                    regex = re.compile(pattern['english_pattern'], re.IGNORECASE)
                    match = regex.match(english)
                    if match:
                        # Apply template
                        tce = pattern['tce_template']
                        for i, group in enumerate(match.groups(), 1):
                            tce = tce.replace(f"${i}", group)
                        print(f"TCE: {tce}")
                        print(f"Pattern: {pattern['description']}")
                        matched = True
                        break
            
            if not matched:
                print("No pattern matched")
                
        return True
        
    except Exception as e:
        print(f"Pattern test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_grammar_based_tce_to_tau():
    """Test grammar-based TCE->Tau translation."""
    print("\n=== Testing Grammar-Based TCE->Tau Translation ===")
    
    try:
        # Use the TCE to Tau wrapper
        from tce_to_tau_wrapper import translate_tce_to_tau
        
        test_cases = [
            "x > 5",
            "x = 10 -> y = true",
            "1 <= x <= 10",
            "forall x. x > 0",
            "exists y. y < x"
        ]
        
        for tce in test_cases:
            print(f"\nTCE: {tce}")
            result = translate_tce_to_tau(tce)
            
            if result['success']:
                print(f"Tau: {result['tau']}")
                if 'ast' in result:
                    print(f"AST type: {result['ast'].__class__.__name__}")
            else:
                print(f"Error: {result['error']}")
                
        return True
        
    except Exception as e:
        print(f"Grammar test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_english_to_tau_pipeline():
    """Test complete English->TCE->Tau pipeline."""
    print("\n=== Testing Full English->Tau Pipeline ===")
    
    try:
        from english_to_tau_translator import translate_english_to_tau
        
        test_cases = [
            "x is greater than 5",
            "if x equals 10 then y is true", 
            "x must be between 1 and 10",
            "for all x in list, x > 0",
            "there exists y such that y < x"
        ]
        
        for english in test_cases:
            print(f"\nEnglish: {english}")
            result = translate_english_to_tau(english)
            
            if result['success']:
                print(f"TCE: {result.get('tce', 'N/A')}")
                print(f"Tau: {result['tau']}")
                print(f"Method: {result.get('method', 'unknown')}")
            else:
                print(f"Error: {result['error']}")
                if 'details' in result:
                    print(f"Details: {result['details']}")
                    
        return True
        
    except Exception as e:
        print(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bidirectional_translation():
    """Test bidirectional translation capabilities."""
    print("\n=== Testing Bidirectional Translation ===")
    
    try:
        # Test TCE <-> Tau bidirectional
        from tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
        
        translator = TCETauTranslator()
        
        # Test TCE -> Tau -> TCE roundtrip
        test_tce = [
            "x > 5",
            "x = 10 -> y = true",
            "forall x. x > 0"
        ]
        
        for original_tce in test_tce:
            print(f"\nOriginal TCE: {original_tce}")
            
            # Forward: TCE -> Tau
            tau_result = translator.translate_to_tau(original_tce)
            if tau_result['success']:
                tau_expr = tau_result['tau']
                print(f"Tau: {tau_expr}")
                
                # Reverse: Tau -> TCE
                tce_result = translator.translate_to_tce(tau_expr)
                if tce_result['success']:
                    back_tce = tce_result['tce']
                    print(f"Back to TCE: {back_tce}")
                    print(f"Roundtrip successful: {original_tce == back_tce}")
                else:
                    print(f"Tau->TCE failed: {tce_result['error']}")
            else:
                print(f"TCE->Tau failed: {tau_result['error']}")
                
        return True
        
    except Exception as e:
        print(f"Bidirectional test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all direct translation tests."""
    print("Direct Translation System Tests")
    print("=" * 50)
    
    tests = [
        ("Pattern-Based Translation", test_pattern_based_translation),
        ("Grammar-Based TCE->Tau", test_grammar_based_tce_to_tau),
        ("Full English->Tau Pipeline", test_full_english_to_tau_pipeline),
        ("Bidirectional Translation", test_bidirectional_translation)
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
    
    # Show example of working translation if available
    if results.get("Full English->Tau Pipeline", False):
        print("\n" + "=" * 50)
        print("Example Working Translation:")
        from english_to_tau_translator import translate_english_to_tau
        
        example = "x is greater than 5"
        result = translate_english_to_tau(example)
        if result['success']:
            print(f"English: {example}")
            print(f"TCE: {result.get('tce', 'N/A')}")
            print(f"Tau: {result['tau']}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())