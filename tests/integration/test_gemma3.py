#!/usr/bin/env python3
"""
Gemma 3 Test for TauTranslatorOmega
==================================

Tests Gemma 3 model with real Tau examples.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_gemma3_translation():
    """Test Gemma 3 translation capabilities."""
    print("🤖 Testing Gemma 3 Translation")
    print("=" * 50)
    
    try:
        from tau_translator_omega.gemma3.translator import gemma3_translator
        
        # Load the model
        print("🔄 Loading Gemma 3...")
        if not gemma3_translator.load_model():
            print("❌ Failed to load Gemma 3")
            return False
        
        # Test cases from real Tau demos
        test_cases = [
            {
                "tau": "halfAdderSum(a, b) := a + b",
                "description": "Half adder sum function"
            },
            {
                "tau": "r o1[t] = i1[t] & i2[t]",
                "description": "AND gate rule"
            },
            {
                "tau": "always (x > 0)",
                "description": "Temporal constraint"
            },
            {
                "tau": "sbf i1 = ifile(\"data.in\")",
                "description": "Stream input declaration"
            }
        ]
        
        print("\n📤 Testing Tau → TCE Translation:")
        success_count = 0
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{i}. {case['description']}")
            print(f"   Tau: {case['tau']}")
            
            result = gemma3_translator.translate_tau_to_tce(case['tau'])
            
            if result:
                success_count += 1
                print(f"   ✅ TCE: {result}")
            else:
                print(f"   ❌ Translation failed")
        
        success_rate = (success_count / len(test_cases)) * 100
        print(f"\n📊 Tau → TCE Success Rate: {success_count}/{len(test_cases)} ({success_rate:.1f}%)")
        
        # Test TCE → Tau
        print("\n📥 Testing TCE → Tau Translation:")
        tce_examples = [
            "Define function add as x plus y",
            "Always x is greater than zero",
            "Rule: output equals input1 and input2"
        ]
        
        tce_success = 0
        for i, tce_text in enumerate(tce_examples, 1):
            print(f"\n{i}. TCE: {tce_text}")
            
            result = gemma3_translator.translate_tce_to_tau(tce_text)
            
            if result:
                tce_success += 1
                print(f"   ✅ Tau: {result}")
            else:
                print(f"   ❌ Translation failed")
        
        tce_rate = (tce_success / len(tce_examples)) * 100
        print(f"\n📊 TCE → Tau Success Rate: {tce_success}/{len(tce_examples)} ({tce_rate:.1f}%)")
        
        overall_rate = ((success_count + tce_success) / (len(test_cases) + len(tce_examples))) * 100
        
        if overall_rate >= 70:
            print(f"\n🎉 Gemma 3 test PASSED! Overall: {overall_rate:.1f}%")
            return True
        else:
            print(f"\n⚠️  Gemma 3 needs improvement. Overall: {overall_rate:.1f}%")
            return False
        
    except Exception as e:
        print(f"❌ Gemma 3 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run Gemma 3 tests."""
    print("🚀 TauTranslatorOmega - Gemma 3 Testing")
    
    success = test_gemma3_translation()
    
    if success:
        print("\n✅ Gemma 3 is working great with TauTranslatorOmega!")
    else:
        print("\n⚠️  Gemma 3 needs debugging or fallback to patterns")

if __name__ == "__main__":
    main()
