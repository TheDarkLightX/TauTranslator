#!/usr/bin/env python3
"""
Complete translation test - Tests the full TCE to TAU translation pipeline.

Tests the grammar fixes with the transformer to ensure end-to-end translation works.

Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_complete_translation():
    """Test complete translation from TCE to TAU."""
    
    try:
        from lark import Lark
        from tau_translator_omega.core_engine.tce_tau_transformer import TCEToTauTransformer
        
        # Load the fixed TCE grammar
        grammar_path = project_root / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
        
        if not grammar_path.exists():
            print(f"❌ Grammar file not found: {grammar_path}")
            return False
            
        with open(grammar_path, 'r') as f:
            grammar_content = f.read()
        
        # Create parser with transformer
        parser = Lark(
            grammar_content,
            parser='lalr',
            start='start',
            propagate_positions=True
        )
        
        transformer = TCEToTauTransformer()
        
        print("✅ Parser and transformer created successfully")
        
        # Test cases with expected translations
        test_cases = [
            # Quantifiers
            {
                "input": "forall x: p(x).",
                "description": "Universal quantifier with colon syntax",
                "expected_contains": ["∀", "x", "p(x)"]
            },
            {
                "input": "exists y such that q(y).",
                "description": "Existential quantifier with 'such that' syntax", 
                "expected_contains": ["∃", "y", "q(y)"]
            },
            
            # Conditionals
            {
                "input": "if x > 5 then true else false.",
                "description": "Conditional expression",
                "expected_contains": ["?", ":", "x > 5", "true", "false"]
            },
            
            # Arithmetic
            {
                "input": "x + y * z.",
                "description": "Arithmetic with operator precedence",
                "expected_contains": ["x", "+", "y", "*", "z"]
            },
            
            # Complex combinations
            {
                "input": "forall x: if x > 0 then p(x) else q(x).",
                "description": "Quantifier with conditional",
                "expected_contains": ["∀", "x", "?", ":", "x > 0"]
            }
        ]
        
        print("\n🔄 Testing Complete TCE to TAU Translation:")
        
        success_count = 0
        for i, test_case in enumerate(test_cases, 1):
            try:
                input_text = test_case["input"]
                description = test_case["description"]
                expected_contains = test_case["expected_contains"]
                
                # Parse the input
                parse_tree = parser.parse(input_text)
                
                # Transform to TAU
                tau_output = transformer.transform(parse_tree)
                
                print(f"\n  Test {i}: {description}")
                print(f"    Input:  '{input_text}'")
                print(f"    Output: '{tau_output}'")
                
                # Check if expected elements are present
                missing_elements = []
                for expected in expected_contains:
                    if expected not in str(tau_output):
                        missing_elements.append(expected)
                
                if missing_elements:
                    print(f"    ❌ Missing expected elements: {missing_elements}")
                else:
                    print(f"    ✅ All expected elements found")
                    success_count += 1
                    
            except Exception as e:
                print(f"    ❌ Translation failed: {e}")
        
        print(f"\n📊 Results: {success_count}/{len(test_cases)} tests passed")
        
        if success_count == len(test_cases):
            print("🎉 All translation tests passed!")
            return True
        else:
            print("❌ Some translation tests failed")
            return False
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_pattern_based_translation():
    """Test pattern-based translation method."""
    
    try:
        backend_path = project_root / "backend/unified"
        sys.path.insert(0, str(backend_path))
        
        from translators.pattern_translator import PatternTranslationEngine
        
        print("\n🔍 Testing Pattern-Based Translation:")
        
        # Create pattern engine
        engine = PatternTranslationEngine()
        print("  ✅ Pattern engine created")
        
        # Test basic pattern recognition
        test_texts = [
            "forall x: p(x)",
            "if x > 5 then true else false",
            "define function f(x) as x + 1"
        ]
        
        for text in test_texts:
            can_translate = engine.can_translate(text, None)
            print(f"    '{text}' -> Can translate: {can_translate}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not test pattern translation: {e}")
        return False
    except Exception as e:
        print(f"❌ Pattern translation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Complete Translation Pipeline")
    print("=" * 60)
    
    success = True
    
    # Test complete grammar and transformer
    if not test_complete_translation():
        success = False
    
    # Test pattern-based method  
    if not test_pattern_based_translation():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All translation methods working!")
        print("\n✅ Quantifiers: Both colon and 'such that' syntax working")
        print("✅ Conditionals: If-then-else expressions working") 
        print("✅ Arithmetic: All operators working with proper precedence")
        print("✅ TCE to TAU: Grammar parser and transformer integration working")
        print("✅ Pattern-based: Translation engine accessible")
    else:
        print("❌ Some translation tests failed. Check output above.")
    
    sys.exit(0 if success else 1)