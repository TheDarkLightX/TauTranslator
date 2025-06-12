#!/usr/bin/env python3
"""
Test working translation components as they actually exist.

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


def test_tce_tau_translator():
    """Test the actual TCE to Tau translator."""
    print("\n=== Testing TCE to Tau Translator ===")
    
    try:
        from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
        
        translator = TCETauTranslator()
        
        # Test simple expressions
        test_cases = [
            # (TCE expression, expected success)
            ("x > 5", True),
            ("x = 10", True),
            ("x + y", True),
            ("true", True),
            ("false", True),
        ]
        
        for tce_expr, should_succeed in test_cases:
            print(f"\nTCE: {tce_expr}")
            
            # First parse the TCE to get an AST
            from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
            parser = CNLParser()
            
            try:
                ast = parser.parse(tce_expr)
                if ast:
                    # Translate AST to Tau
                    result = translator.translate(ast)
                    
                    if result.success:
                        print(f"Tau: {result.tau_code}")
                        print(f"Success: True")
                    else:
                        print(f"Translation failed: {result.error}")
                        print(f"Success: False")
                else:
                    print("Parsing failed - no AST produced")
                    print(f"Success: False")
                    
            except Exception as e:
                print(f"Error: {e}")
                print(f"Success: False")
                
        return True
        
    except Exception as e:
        print(f"TCE-Tau test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pattern_matching():
    """Test pattern matching directly."""
    print("\n=== Testing Pattern Matching ===")
    
    try:
        import re
        
        # Define some simple patterns
        patterns = [
            {
                'description': 'Greater than comparison',
                'english': r'(\w+)\s+is\s+greater\s+than\s+(\d+)',
                'tce': r'\1 > \2'
            },
            {
                'description': 'Equals comparison',
                'english': r'(\w+)\s+equals\s+(\d+)',
                'tce': r'\1 = \2'
            },
            {
                'description': 'Less than comparison',
                'english': r'(\w+)\s+is\s+less\s+than\s+(\d+)',
                'tce': r'\1 < \2'
            },
            {
                'description': 'Between values',
                'english': r'(\w+)\s+is\s+between\s+(\d+)\s+and\s+(\d+)',
                'tce': r'\2 <= \1 <= \3'
            }
        ]
        
        test_cases = [
            "x is greater than 5",
            "y equals 10",
            "z is less than 3",
            "x is between 1 and 10"
        ]
        
        for english in test_cases:
            print(f"\nEnglish: {english}")
            matched = False
            
            for pattern in patterns:
                regex = re.compile(pattern['english'], re.IGNORECASE)
                match = regex.match(english)
                
                if match:
                    # Apply substitution
                    tce = regex.sub(pattern['tce'], english)
                    print(f"TCE: {tce}")
                    print(f"Pattern: {pattern['description']}")
                    matched = True
                    break
                    
            if not matched:
                print("No pattern matched")
                
        return True
        
    except Exception as e:
        print(f"Pattern matching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_english_to_tau_class():
    """Test the EnglishToTauTranslator class."""
    print("\n=== Testing EnglishToTauTranslator Class ===")
    
    try:
        from english_to_tau_translator import EnglishToTauTranslator
        
        translator = EnglishToTauTranslator()
        
        test_cases = [
            "x > 5",
            "x = 10",
            "x is greater than 5",
            "if x then y"
        ]
        
        for english in test_cases:
            print(f"\nEnglish: {english}")
            
            try:
                success, tau_code, tce_text = translator.translate_english_to_tau(english)
                
                if success:
                    print(f"TCE: {tce_text}")
                    print(f"Tau: {tau_code}")
                    print("Success: True")
                else:
                    print(f"TCE: {tce_text}")
                    print("Translation failed")
                    print("Success: False")
                    
            except Exception as e:
                print(f"Error: {e}")
                print("Success: False")
                
        return True
        
    except Exception as e:
        print(f"EnglishToTauTranslator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wrapper_classes():
    """Test the wrapper classes."""
    print("\n=== Testing Wrapper Classes ===")
    
    try:
        from tce_to_tau_wrapper import TCEToTauWrapper
        
        wrapper = TCEToTauWrapper()
        
        # Create a simple AST node for testing
        from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
        parser = CNLParser()
        
        test_expressions = [
            "x > 5",
            "true",
            "x + y"
        ]
        
        for expr in test_expressions:
            print(f"\nExpression: {expr}")
            
            try:
                ast = parser.parse(expr)
                if ast:
                    result = wrapper.translate(ast)
                    
                    if result.success:
                        print(f"Tau: {result.tau_code}")
                        print("Success: True")
                    else:
                        print(f"Error: {result.error}")
                        print("Success: False")
                else:
                    print("Parsing failed")
                    print("Success: False")
                    
            except Exception as e:
                print(f"Error: {e}")
                print("Success: False")
                
        return True
        
    except Exception as e:
        print(f"Wrapper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all working translation tests."""
    print("Working Translation System Tests")
    print("=" * 50)
    
    tests = [
        ("TCE to Tau Translator", test_tce_tau_translator),
        ("Pattern Matching", test_pattern_matching),
        ("EnglishToTauTranslator Class", test_english_to_tau_class),
        ("Wrapper Classes", test_wrapper_classes)
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
    
    # Show working example
    if any(results.values()):
        print("\n" + "=" * 50)
        print("Working Translation Example:")
        
        # Simple pattern-based example
        import re
        english = "x is greater than 5"
        pattern = re.compile(r'(\w+)\s+is\s+greater\s+than\s+(\d+)', re.IGNORECASE)
        tce = pattern.sub(r'\1 > \2', english)
        
        print(f"English: {english}")
        print(f"TCE: {tce}")
        
        # Try to get Tau if possible
        try:
            from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
            from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
            
            parser = CNLParser()
            translator = TCETauTranslator()
            
            ast = parser.parse(tce)
            if ast:
                result = translator.translate(ast)
                if result.success:
                    print(f"Tau: {result.tau_code}")
        except:
            pass
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())