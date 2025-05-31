#!/usr/bin/env python3
"""
Translation Quality Test
========================

Test the improved translation patterns to ensure better output quality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_translation_improvements():
    """Test the improved translation patterns."""
    print("🧪 Testing Translation Quality Improvements")
    print("=" * 50)
    
    try:
        from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
        
        translator = LMQLBidirectionalTranslator()
        
        # Test cases with expected improvements
        test_cases = [
            {
                "input": "halfAdderSum(a, b) := a + b",
                "expected_improvement": "Should translate 'a + b' to 'a plus b' or 'a XOR b'"
            },
            {
                "input": "r o1[t] = i1[t] & i2[t]",
                "expected_improvement": "Should translate 'i1[t] & i2[t]' to 'input 1 at time t AND input 2 at time t'"
            },
            {
                "input": "always (x > 0)",
                "expected_improvement": "Should translate 'x > 0' to 'x is greater than 0'"
            },
            {
                "input": "r and_gate[t] = i1[t] & i2[t]",
                "expected_improvement": "Should translate stream names and operators properly"
            },
            {
                "input": "sometimes (status = ready)",
                "expected_improvement": "Should translate 'status = ready' to 'status equals ready'"
            }
        ]
        
        print("\\n🔍 Testing Translation Cases:")
        print("-" * 30)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\\n{i}. Input: {test_case['input']}")
            print(f"   Expected: {test_case['expected_improvement']}")
            
            try:
                result = translator.translate_tau_to_tce(test_case['input'])
                
                if result.success:
                    print(f"   ✅ Output: {result.output}")
                    print(f"   📊 Confidence: {result.confidence:.1%}")
                else:
                    print(f"   ❌ Failed: {', '.join(result.errors)}")
                    
            except Exception as e:
                print(f"   💥 Error: {e}")
        
        # Test the specific example from the user
        print("\\n" + "=" * 50)
        print("🎯 Testing User's Example:")
        print("-" * 30)
        
        user_example = """halfAdderSum(a, b) := a + b
r o1[t] = i1[t] & i2[t]
always (x > 0)"""
        
        print(f"Input:\\n{user_example}")
        print("\\nBEFORE (problematic output):")
        print("Define function halfAdderSum as a + b. Rule: o1 at time t equals i1[t] & i2[t]. Always (x > 0).")
        
        print("\\nAFTER (improved output):")
        try:
            result = translator.translate_tau_to_tce(user_example)
            if result.success:
                print(result.output)
                print(f"\\nConfidence: {result.confidence:.1%}")
                print(f"Patterns detected: {', '.join(result.patterns_detected)}")
            else:
                print(f"Failed: {', '.join(result.errors)}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\\n" + "=" * 50)
        print("✅ Translation quality test complete!")
        
    except ImportError as e:
        print(f"❌ Failed to import translator: {e}")
        print("Make sure the translator module is properly set up.")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

def main():
    """Run the translation quality test."""
    test_translation_improvements()

if __name__ == "__main__":
    main()
