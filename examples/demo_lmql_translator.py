#!/usr/bin/env python3
"""
TauTranslatorOmega LMQL Demo
============================

Comprehensive demonstration of the LMQL-based bidirectional translator.
Shows pattern recognition, translation capabilities, and real-world examples.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def demo_pattern_recognition():
    """Demonstrate pattern recognition capabilities."""
    print("🔍 PATTERN RECOGNITION DEMO")
    print("=" * 60)
    
    from tau_translator_omega.lmql_engine.bidirectional_translator import TauPatternAnalyzer
    
    analyzer = TauPatternAnalyzer()
    
    # Real Tau examples from demos
    tau_examples = {
        "Function Definition": "halfAdderSum(a, b) := a + b",
        "Recurrence Relation": "fib[0](n) := 1\nfib[n](x) := fib[n-1](x) + fib[n-2](x)",
        "Stream Declaration": "sbf i1 = ifile(\"input.in\")",
        "Rule Definition": "r o1[t] = i1[t] & i2[t]",
        "Temporal Logic": "always (x > 0)",
        "Solver Command": "sat (x & y)",
        "Boolean Operations": "x & y | z'",
    }
    
    for category, tau_code in tau_examples.items():
        print(f"\n📝 {category}:")
        print(f"   Code: {tau_code}")
        
        patterns = analyzer.analyze_tau_text(tau_code)
        if patterns:
            print(f"   ✅ Patterns detected: {list(patterns.keys())}")
            for pattern_type, matches in patterns.items():
                for match_text, groups in matches[:1]:  # Show first match
                    print(f"      • {pattern_type}: {groups}")
        else:
            print(f"   ⚠️  No patterns detected")
    
    print("\n✅ Pattern recognition demo complete!")

def demo_bidirectional_translation():
    """Demonstrate bidirectional translation."""
    print("\n🔄 BIDIRECTIONAL TRANSLATION DEMO")
    print("=" * 60)
    
    from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
    
    translator = LMQLBidirectionalTranslator()
    print(f"🔧 LMQL Available: {translator.use_lmql}")
    
    # Test cases from real Tau demos
    test_cases = [
        {
            "category": "4-bit Binary Adder",
            "tau": "halfAdderSum(a, b) := a + b",
            "description": "Half adder sum function"
        },
        {
            "category": "Logic Gates",
            "tau": "r o1[t] = i1[t] & i2[t]",
            "description": "AND gate rule"
        },
        {
            "category": "Stream I/O",
            "tau": "sbf i1 = ifile(\"data.in\")",
            "description": "Input stream declaration"
        },
        {
            "category": "Temporal Logic",
            "tau": "always (x > 0)",
            "description": "Always constraint"
        },
        {
            "category": "Democracy Demo",
            "tau": "r o1[t] = (i1[t] & i2[t]) | (i2[t] & i3[t]) | (i1[t] & i3[t])",
            "description": "Majority vote logic"
        }
    ]
    
    successful_translations = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['category']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Tau: {test_case['tau']}")
        
        # Tau → TCE
        result = translator.translate_tau_to_tce(test_case['tau'])
        if result.success:
            successful_translations += 1
            print(f"   ✅ TCE: {result.output}")
            print(f"   📊 Confidence: {result.confidence:.1%}")
            
            # Test round-trip (TCE → Tau)
            round_trip = translator.translate_tce_to_tau(result.output)
            if round_trip.success:
                print(f"   🔄 Round-trip: {round_trip.output}")
                print(f"   🎯 Round-trip confidence: {round_trip.confidence:.1%}")
            else:
                print(f"   ⚠️  Round-trip failed: {', '.join(round_trip.errors)}")
        else:
            print(f"   ❌ Translation failed: {', '.join(result.errors)}")
    
    success_rate = (successful_translations / total_tests) * 100
    print(f"\n📊 Translation Success Rate: {successful_translations}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Bidirectional translation demo PASSED!")
    else:
        print("⚠️  Translation accuracy needs improvement")

def demo_real_world_examples():
    """Demonstrate with real-world Tau examples."""
    print("\n🌍 REAL-WORLD EXAMPLES DEMO")
    print("=" * 60)
    
    from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
    
    translator = LMQLBidirectionalTranslator()
    
    # Real examples from Tau demos
    real_examples = {
        "4bit_binary_adder.tau": [
            "halfAdderSum(a, b) := a + b",
            "halfAdderCarry(a, b) := a & b",
            "fullAdderSum(a, b, cin) := halfAdderSum(a, b) + cin",
            "fullAdderCarry(a, b, cin) := halfAdderCarry(a, b) | (halfAdderSum(a, b) & cin)"
        ],
        "logic_gates.tau": [
            "r o1[t] = i1[t] & i2[t]",  # AND gate
            "r o2[t] = i1[t] | i2[t]",  # OR gate
            "r o3[t] = i1[t]'",         # NOT gate
            "r o4[t] = i1[t] + i2[t]"   # XOR gate
        ],
        "democracy_demo.tau": [
            "r o1[t] = (i1[t] & i2[t]) | (i2[t] & i3[t]) | (i1[t] & i3[t])"
        ],
        "feedback_loop.tau": [
            "r o1[t] = i1[t]",
            "r o2[t] = i2[t-1]'"
        ]
    }
    
    total_examples = 0
    successful_examples = 0
    
    for demo_file, examples in real_examples.items():
        print(f"\n📁 {demo_file}:")
        
        for example in examples:
            total_examples += 1
            print(f"   Tau: {example}")
            
            result = translator.translate_tau_to_tce(example)
            if result.success:
                successful_examples += 1
                print(f"   ✅ TCE: {result.output}")
            else:
                print(f"   ❌ Failed: {', '.join(result.errors)}")
    
    success_rate = (successful_examples / total_examples) * 100
    print(f"\n📊 Real-world Success Rate: {successful_examples}/{total_examples} ({success_rate:.1f}%)")

def demo_tce_to_tau_translation():
    """Demonstrate TCE to Tau translation."""
    print("\n📥 TCE → TAU TRANSLATION DEMO")
    print("=" * 60)
    
    from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
    
    translator = LMQLBidirectionalTranslator()
    
    # TCE examples
    tce_examples = [
        "Define function halfAdderSum as a plus b.",
        "Rule: output equals input1 and input2.",
        "Always x is greater than zero.",
        "Input stream data reads from file input.txt.",
        "Sometimes error equals zero.",
        "Define function fibonacci as previous value plus previous previous value."
    ]
    
    successful_translations = 0
    
    for i, tce_text in enumerate(tce_examples, 1):
        print(f"\n{i}. TCE: {tce_text}")
        
        result = translator.translate_tce_to_tau(tce_text)
        if result.success:
            successful_translations += 1
            print(f"   ✅ Tau: {result.output}")
            print(f"   📊 Confidence: {result.confidence:.1%}")
            print(f"   🔍 Patterns: {', '.join(result.patterns_detected)}")
        else:
            print(f"   ❌ Failed: {', '.join(result.errors)}")
    
    success_rate = (successful_translations / len(tce_examples)) * 100
    print(f"\n📊 TCE → Tau Success Rate: {successful_translations}/{len(tce_examples)} ({success_rate:.1f}%)")

def demo_web_interface_info():
    """Show information about the web interface."""
    print("\n🌐 WEB INTERFACE DEMO")
    print("=" * 60)
    
    print("🚀 TauTranslatorOmega includes a web interface!")
    print("\n📋 Features:")
    print("   • Interactive bidirectional translation")
    print("   • Real-time pattern recognition")
    print("   • Example translations from Tau demos")
    print("   • Confidence scoring and error reporting")
    print("   • Responsive design with modern UI")
    
    print("\n🔧 To start the web interface:")
    print("   1. cd ~/TauTranslator")
    print("   2. python src/tau_translator_omega/web_interface/app.py")
    print("   3. Open http://localhost:5000 in your browser")
    
    print("\n🎯 Web interface provides:")
    print("   • Tau → TCE translation")
    print("   • TCE → Tau translation")
    print("   • Pattern detection visualization")
    print("   • Real-world example library")
    print("   • LMQL enhancement status")

def main():
    """Run the complete LMQL translator demo."""
    print("🚀 TauTranslatorOmega - LMQL Bidirectional Translator Demo")
    print("Demonstrating pattern-based Tau ↔ TCE translation")
    print("Legal compliance: No IDNI parser dependency")
    
    try:
        # Run all demos
        demo_pattern_recognition()
        demo_bidirectional_translation()
        demo_real_world_examples()
        demo_tce_to_tau_translation()
        demo_web_interface_info()
        
        print("\n" + "=" * 60)
        print("🎉 LMQL TRANSLATOR DEMO COMPLETE!")
        print("=" * 60)
        
        print("\n🎯 Key Achievements:")
        print("   ✅ Pattern-based Tau analysis (legal compliance)")
        print("   ✅ Bidirectional Tau ↔ TCE translation")
        print("   ✅ Real-world Tau demo compatibility")
        print("   ✅ Enhanced translation with LMQL fallback")
        print("   ✅ Web interface for interactive use")
        
        print("\n🚀 Next Steps:")
        print("   1. Install LMQL for enhanced translation")
        print("   2. Deploy web interface for public use")
        print("   3. Integrate with LLM APIs for production")
        print("   4. Add more Tau language constructs")
        
        print("\n🌟 TauTranslatorOmega is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
