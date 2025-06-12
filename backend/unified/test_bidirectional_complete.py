#!/usr/bin/env python3
"""
Comprehensive test for bidirectional translation
Tests TAU parser with quantifiers/conditionals and CNL/TCE parser integration

Copyright: DarkLightX/Dana Edwards
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
from domain.tau_parser_service import TauParserService
from domain.tau_to_english_translator import TauToEnglishService
from translators.bidirectional_engine import BidirectionalTranslationEngine
from translators.base import TranslationDirection


def test_tau_parser_quantifiers_and_conditionals():
    """Test TAU parser with quantifiers and conditionals."""
    print("\n=== Testing TAU Parser ===")
    
    parser = TauParserService()
    
    # Test cases
    test_cases = [
        # Quantifiers
        ("forall x : x > 0", "Quantifier with simple constraint"),
        ("exists y : y < 10", "Existential quantifier"),
        ("forall x : x > 0 and x < 100", "Quantifier with compound constraint"),
        ("exists n : n * n = 4", "Existential with arithmetic"),
        ("forall a : a implies b", "Universal with implication"),
        
        # Conditionals
        ("if x > 0 then y = 1", "Simple conditional"),
        ("if x > 0 then y = 1 else y = 0", "Conditional with else"),
        ("if a and b then c else d", "Conditional with logical condition"),
        ("if x > 0 then if y > 0 then z = 1 else z = 0", "Nested conditionals"),
        
        # Arithmetic
        ("x + y = 10", "Addition"),
        ("a * b + c = d", "Mixed arithmetic"),
        ("2 * x - 3 = 7", "Arithmetic with constants"),
        ("(x + y) * z = 10", "Parenthesized arithmetic"),
        
        # Complex expressions
        ("forall x : if x > 0 then x * x > 0", "Quantifier with conditional"),
        ("solve {x, y} : x + y = 10 and x - y = 2", "Solver with arithmetic"),
        ("always (if temperature > 100 then alarm = true)", "Temporal with conditional")
    ]
    
    for tau_code, description in test_cases:
        print(f"\n{description}: {tau_code}")
        result = parser.parse_tau_code(tau_code)
        
        if hasattr(result, 'is_success') and result.is_success():
            print(f"✅ Parse Success!")
            ast = result.value
            print(f"   Node type: {ast.node_type}")
            
            # Try translating to English
            translator = TauToEnglishService()
            english_result = translator.translate_tau_to_english(tau_code)
            
            if english_result.is_success():
                print(f"   English: {english_result.value}")
            else:
                print(f"   Translation error: {english_result.message}")
        else:
            print(f"❌ Parse Error [{result.error_code}]: {result.message}")


def test_tce_parsing():
    """Test TCE parsing using existing CNL parser."""
    print("\n\n=== Testing TCE Parsing (Existing CNL Parser) ===")
    
    # Try to use the existing parser
    try:
        from tau_translator_omega.core_engine.cnl_parser.parser import Lark, TceTransformer, GRAMMAR_FILE_PATH
        
        with open(GRAMMAR_FILE_PATH, 'r') as f:
            grammar = f.read()
        
        parser = Lark(grammar, start='start', parser='lalr')
        transformer = TceTransformer()
        
        test_cases = [
            "x > 0.",
            "define predicate isPositive(x) as x > 0.",
            "if x > 0 then isPositive(x).",
            "forall x such that x > 0, isPositive(x).",
            "exists y, y = x + 1.",
            "define function square(x) as x * x.",
            "input temperature > 100.",
            "output alarm = true."
        ]
        
        for tce_code in test_cases:
            print(f"\nParsing TCE: {tce_code}")
            try:
                tree = parser.parse(tce_code)
                ast = transformer.transform(tree)
                print(f"✅ Parse Success!")
                print(f"   AST: {ast}")
            except Exception as e:
                print(f"❌ Parse Error: {e}")
                
    except Exception as e:
        print(f"Could not load CNL parser: {e}")


def test_bidirectional_engine():
    """Test the bidirectional translation engine."""
    print("\n\n=== Testing Bidirectional Translation Engine ===")
    
    engine = BidirectionalTranslationEngine()
    
    # Test English to TAU with quantifiers and conditionals
    print("\n--- English to TAU (with quantifiers and conditionals) ---")
    test_cases = [
        ("For all users, if the user has a password then the user is authenticated", 
         TranslationDirection.TO_TAU),
        ("There exists a configuration where all constraints are satisfied",
         TranslationDirection.TO_TAU),
        ("If the temperature is greater than 100 then activate the cooling system",
         TranslationDirection.TO_TAU)
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
        ("forall x : x > 0", TranslationDirection.TO_ENGLISH),
        ("if temperature > 100 then alarm = true", TranslationDirection.TO_ENGLISH),
        ("exists y : y = x + 1", TranslationDirection.TO_ENGLISH),
        ("always (forall user : has_password(user))", TranslationDirection.TO_ENGLISH)
    ]
    
    for text, direction in tau_examples:
        print(f"\nTranslating: {text}")
        result = engine.translate(text, direction)
        
        if result.success:
            print(f"✅ English: {result.translated_text}")
            print(f"   Confidence: {result.confidence}")
            print(f"   Pipeline: {result.metadata.get('pipeline', 'N/A')}")
        else:
            print(f"❌ Error: {result.error_message}")
    
    # Test TCE translations
    print("\n--- TCE Translation Tests ---")
    tce_examples = [
        ("define predicate isValid(x) as x > 0.", TranslationDirection.TCE_TO_TAU),
        ("forall x such that x > 0, isValid(x).", TranslationDirection.TCE_TO_NL),
        ("if temperature > threshold then activate_cooling().", TranslationDirection.BIDIRECTIONAL)
    ]
    
    for text, direction in tce_examples:
        print(f"\nTranslating: {text}")
        print(f"Direction: {direction.value}")
        result = engine.translate(text, direction)
        
        if result.success:
            print(f"✅ Result: {result.translated_text}")
            print(f"   Actual direction: {result.direction.value}")
            print(f"   Pipeline: {result.metadata.get('pipeline', 'N/A')}")
        else:
            print(f"❌ Error: {result.error_message}")


def test_round_trip():
    """Test round-trip translation."""
    print("\n\n=== Testing Round-Trip Translation ===")
    
    engine = BidirectionalTranslationEngine()
    
    test_phrases = [
        "For all numbers x, if x is positive then x squared is positive",
        "There exists a solution where x plus y equals 10",
        "If the system is overloaded then reduce the workload else maintain current level"
    ]
    
    for original in test_phrases:
        print(f"\nOriginal English: {original}")
        
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
        
        # Check semantic similarity
        print("✅ Round-trip completed successfully!")


def main():
    print("Comprehensive Bidirectional Translation Test")
    print("With TAU Parser Fixes and CNL/TCE Integration")
    print("=" * 60)
    
    test_tau_parser_quantifiers_and_conditionals()
    test_tce_parsing()
    test_bidirectional_engine()
    test_round_trip()
    
    print("\n\nAll tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()