#!/usr/bin/env python3
"""
Manual Translation Test for TauTranslatorOmega
==============================================

Tests the core translation functionality without GUI dependencies.
Focuses on bidirectional translation quality and backend integration.
"""

import sys
import time
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

def test_translator_availability():
    """Test if the translator module is available."""
    print("🔍 TESTING TRANSLATOR AVAILABILITY")
    print("=" * 50)
    
    try:
        from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
        translator = LMQLBidirectionalTranslator()
        print(f"✅ Translator initialized successfully")
        print(f"   LMQL Available: {translator.use_lmql}")
        return translator
    except Exception as e:
        print(f"❌ Translator initialization failed: {e}")
        return None

def test_tce_to_tau_translations(translator):
    """Test TCE to Tau translations."""
    print("\n🔄 TESTING TCE TO TAU TRANSLATIONS")
    print("=" * 50)
    
    test_cases = [
        "define function myFunction as x + y",
        "rule: if a then b",
        "always x > 5",
        "input stream data from file input.txt",
        "define function factorial as n times factorial of n minus 1"
    ]
    
    results = []
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: TCE to Tau ---")
        print(f"Input: '{test_input}'")
        
        start_time = time.time()
        result = translator.translate_tce_to_tau(test_input)
        end_time = time.time()
        
        print(f"Success: {result.success}")
        print(f"Output: '{result.output}'")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Patterns: {result.patterns_detected}")
        print(f"Time: {end_time - start_time:.3f}s")
        
        if result.errors:
            print(f"Errors: {result.errors}")
        if result.warnings:
            print(f"Warnings: {result.warnings}")
        
        results.append({
            'input': test_input,
            'success': result.success,
            'output': result.output,
            'confidence': result.confidence,
            'time': end_time - start_time
        })
        
        print("✅" if result.success else "❌")
    
    return results

def test_tau_to_tce_translations(translator):
    """Test Tau to TCE translations."""
    print("\n🔄 TESTING TAU TO TCE TRANSLATIONS")
    print("=" * 50)
    
    test_cases = [
        "myFunc() := x + y",
        "always x > 5",
        "r o1[t] = i1[t] & i2[t]",
        "sbf input = ifile(\"data.txt\")",
        "factorial(n) := n = 0 ? 1 : n * factorial(n-1)"
    ]
    
    results = []
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: Tau to TCE ---")
        print(f"Input: '{test_input}'")
        
        start_time = time.time()
        result = translator.translate_tau_to_tce(test_input)
        end_time = time.time()
        
        print(f"Success: {result.success}")
        print(f"Output: '{result.output}'")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Patterns: {result.patterns_detected}")
        print(f"Time: {end_time - start_time:.3f}s")
        
        if result.errors:
            print(f"Errors: {result.errors}")
        if result.warnings:
            print(f"Warnings: {result.warnings}")
        
        results.append({
            'input': test_input,
            'success': result.success,
            'output': result.output,
            'confidence': result.confidence,
            'time': end_time - start_time
        })
        
        print("✅" if result.success else "❌")
    
    return results

def test_bidirectional_round_trips(translator):
    """Test bidirectional round-trip translations."""
    print("\n🔄 TESTING BIDIRECTIONAL ROUND-TRIPS")
    print("=" * 50)
    
    test_cases = [
        {
            'name': 'Function Definition',
            'original': 'myFunc() := x + y',
            'start_format': 'tau'
        },
        {
            'name': 'Rule Definition',
            'original': 'define function test as a plus b',
            'start_format': 'tce'
        },
        {
            'name': 'Always Statement',
            'original': 'always x > 5',
            'start_format': 'tau'
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n--- Round-trip: {test['name']} ---")
        print(f"Original ({test['start_format']}): '{test['original']}'")
        
        try:
            if test['start_format'] == 'tau':
                # Tau -> TCE -> Tau
                step1 = translator.translate_tau_to_tce(test['original'])
                if step1.success:
                    print(f"Step 1 (Tau->TCE): '{step1.output}'")
                    step2 = translator.translate_tce_to_tau(step1.output)
                    if step2.success:
                        print(f"Step 2 (TCE->Tau): '{step2.output}'")
                        
                        # Calculate similarity
                        similarity = calculate_similarity(test['original'], step2.output)
                        print(f"Similarity: {similarity:.2f}")
                        
                        results.append({
                            'name': test['name'],
                            'success': True,
                            'similarity': similarity,
                            'original': test['original'],
                            'final': step2.output
                        })
                        
                        print("✅" if similarity > 0.5 else "⚠️")
                    else:
                        print(f"❌ Step 2 failed: {step2.errors}")
                        results.append({'name': test['name'], 'success': False, 'error': 'Step 2 failed'})
                else:
                    print(f"❌ Step 1 failed: {step1.errors}")
                    results.append({'name': test['name'], 'success': False, 'error': 'Step 1 failed'})
            
            else:  # start_format == 'tce'
                # TCE -> Tau -> TCE
                step1 = translator.translate_tce_to_tau(test['original'])
                if step1.success:
                    print(f"Step 1 (TCE->Tau): '{step1.output}'")
                    step2 = translator.translate_tau_to_tce(step1.output)
                    if step2.success:
                        print(f"Step 2 (Tau->TCE): '{step2.output}'")
                        
                        similarity = calculate_similarity(test['original'], step2.output)
                        print(f"Similarity: {similarity:.2f}")
                        
                        results.append({
                            'name': test['name'],
                            'success': True,
                            'similarity': similarity,
                            'original': test['original'],
                            'final': step2.output
                        })
                        
                        print("✅" if similarity > 0.5 else "⚠️")
                    else:
                        print(f"❌ Step 2 failed: {step2.errors}")
                        results.append({'name': test['name'], 'success': False, 'error': 'Step 2 failed'})
                else:
                    print(f"❌ Step 1 failed: {step1.errors}")
                    results.append({'name': test['name'], 'success': False, 'error': 'Step 1 failed'})
        
        except Exception as e:
            print(f"❌ Round-trip error: {e}")
            results.append({'name': test['name'], 'success': False, 'error': str(e)})
    
    return results

def calculate_similarity(text1, text2):
    """Calculate simple word-based similarity."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def generate_summary(tce_to_tau_results, tau_to_tce_results, bidirectional_results):
    """Generate test summary."""
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    # TCE to Tau summary
    tce_success = sum(1 for r in tce_to_tau_results if r['success'])
    print(f"TCE to Tau: {tce_success}/{len(tce_to_tau_results)} successful")
    
    # Tau to TCE summary
    tau_success = sum(1 for r in tau_to_tce_results if r['success'])
    print(f"Tau to TCE: {tau_success}/{len(tau_to_tce_results)} successful")
    
    # Bidirectional summary
    bi_success = sum(1 for r in bidirectional_results if r['success'])
    print(f"Bidirectional: {bi_success}/{len(bidirectional_results)} successful")
    
    # Overall success rate
    total_tests = len(tce_to_tau_results) + len(tau_to_tce_results) + len(bidirectional_results)
    total_success = tce_success + tau_success + bi_success
    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({total_success}/{total_tests})")
    
    if success_rate >= 80:
        print("🎉 Status: EXCELLENT - Translation system is working great!")
    elif success_rate >= 60:
        print("✅ Status: GOOD - Translation system is mostly functional")
    elif success_rate >= 40:
        print("⚠️ Status: FAIR - Translation system has some issues")
    else:
        print("❌ Status: POOR - Translation system needs work")
    
    # Performance summary
    all_results = tce_to_tau_results + tau_to_tce_results
    if all_results:
        avg_time = sum(r['time'] for r in all_results) / len(all_results)
        print(f"\nAverage Translation Time: {avg_time:.3f}s")
    
    print()

def main():
    """Run manual translation tests."""
    print("🚀 MANUAL TRANSLATION TESTING")
    print("=" * 60)
    
    # Test translator availability
    translator = test_translator_availability()
    if not translator:
        print("❌ Cannot proceed without translator")
        return
    
    # Run translation tests
    tce_to_tau_results = test_tce_to_tau_translations(translator)
    tau_to_tce_results = test_tau_to_tce_translations(translator)
    bidirectional_results = test_bidirectional_round_trips(translator)
    
    # Generate summary
    generate_summary(tce_to_tau_results, tau_to_tce_results, bidirectional_results)

if __name__ == "__main__":
    main()
