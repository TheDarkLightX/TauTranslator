#!/usr/bin/env python3
"""
Simple test for TAU parser without complex imports

Copyright: DarkLightX/Dana Edwards
"""

# Test the TAU parser directly
from domain.tau_parser_service import TauParserService

def main():
    print("Testing TAU Parser")
    print("=" * 50)
    
    parser = TauParserService()
    
    test_cases = [
        "always (x > 0)",
        "forall x : x > 0", 
        "exists y : y = x + 1",
        "solve {x, y} : x + y = 10",
        "if x > 0 then y = 1",
        "always (temperature < 100 and pressure > 50)",
        "x > 0 implies y > 0",
        "not (x = 0)",
        "true",
        "false",
        "42",
        "x + y = 10"
    ]
    
    for tau_code in test_cases:
        print(f"\nParsing: {tau_code}")
        result = parser.parse_tau_code(tau_code)
        
        if hasattr(result, 'is_success') and result.is_success():
            print(f"✅ Success!")
            ast = result.value
            print(f"   Node type: {ast.node_type}")
            print(f"   Location: line {ast.line}, column {ast.column}")
        else:
            if hasattr(result, 'error_code'):
                print(f"❌ Error [{result.error_code}]: {result.message}")
            else:
                print(f"❌ Error: {result}")
    
    # Test TAU to English translation
    print("\n\n" + "=" * 50)
    print("Testing TAU to English Translation")
    print("=" * 50)
    
    from domain.tau_to_english_translator import TauToEnglishService
    
    translator = TauToEnglishService()
    
    for tau_code in test_cases[:6]:  # Test first 6 cases
        print(f"\nTranslating: {tau_code}")
        result = translator.translate_tau_to_english(tau_code)
        
        if hasattr(result, 'is_success') and result.is_success():
            print(f"✅ English: {result.value}")
        else:
            if hasattr(result, 'error_code'):
                print(f"❌ Error [{result.error_code}]: {result.message}")
            else:
                print(f"❌ Error: {result}")


if __name__ == "__main__":
    main()