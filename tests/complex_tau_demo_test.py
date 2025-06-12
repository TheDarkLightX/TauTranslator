#!/usr/bin/env python3
"""
Complex Tau Demo Cases Test
Copyright: DarkLightX/Dana Edwards

Test our pipelines with real Tau language constructs from the demos.
Goal: Handle complex logical formulas, temporal logic, stream processing, etc.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.unified.ilr_pipeline_simple import ILRPipelineSimple
from backend.unified.english_to_tau_integrated import IntegratedEnglishToTauTranslator


class ComplexTauDemoTest:
    """Test complex Tau language constructs from real demos."""
    
    def __init__(self):
        self.ilr_pipeline = ILRPipelineSimple()
        self.direct_pipeline = IntegratedEnglishToTauTranslator()
    
    def test_complex_case(self, english: str, category: str):
        """Test a complex case with both pipelines."""
        print(f"\n{'='*80}")
        print(f"Category: {category}")
        print(f"English: {english}")
        print(f"{'='*80}")
        
        # Test ILR Pipeline
        print("\n🧠 ILR Pipeline (Semantic):")
        ilr_result = self.ilr_pipeline.translate(english)
        print(f"  Success:   {ilr_result.success}")
        if ilr_result.success:
            print(f"  ILR Type:  {ilr_result.ilr_type}")
            print(f"  TCE:       {ilr_result.tce_text}")
            print(f"  Tau:       {ilr_result.tau_code}")
        else:
            print(f"  Error:     {ilr_result.metadata.get('error', 'Unknown error')}")
        
        # Test Direct Pipeline
        print("\n⚡ Direct Pipeline (Pattern):")
        direct_success, direct_tau, direct_tce = self.direct_pipeline.translate(english)
        print(f"  Success:   {direct_success}")
        if direct_success:
            print(f"  TCE:       {direct_tce}")
            print(f"  Tau:       {direct_tau}")
        else:
            print(f"  Failed to translate")
        
        # Analysis
        print("\n📊 Analysis:")
        if ilr_result.success and direct_success:
            print("  ✅ Both pipelines succeeded")
        elif ilr_result.success:
            print("  🧠 Only ILR succeeded")
        elif direct_success:
            print("  ⚡ Only Direct succeeded")
        else:
            print("  ❌ Both pipelines failed")
        
        return {
            'category': category,
            'english': english,
            'ilr_success': ilr_result.success,
            'direct_success': direct_success,
            'ilr_tau': ilr_result.tau_code if ilr_result.success else "",
            'direct_tau': direct_tau if direct_success else ""
        }


def run_complex_demo_test():
    """Run comprehensive test with complex Tau demo cases."""
    tester = ComplexTauDemoTest()
    
    # Complex demo cases organized by Tau language features
    demo_cases = {
        "Binary Arithmetic": [
            "half adder sum of a and b equals a xor b",
            "half adder carry of a and b equals a and b", 
            "full adder sum of a, b, and c equals a xor b xor c",
            "normalize bit0 and bit1 and bit2 and bit3",
        ],
        
        "Function Definitions": [
            "halfAdderSum of a and b is defined as a xor b",
            "fullAdderCarry of a, b, and c is defined as (a and b) or (a and c) or (b and c)",
            "complexFormula of x, y, and z is defined as (x and y) or (y and z) or (x and z)",
        ],
        
        "Stream Processing": [
            "i1 is input file named input1.in",
            "o1 is output file named and.out", 
            "rule o1 at time t equals i1 at time t and i2 at time t",
            "rule o3 at time t equals i1 at time t complement",
        ],
        
        "Temporal Logic": [
            "always x at time t implies sometimes x at time t plus 1",
            "always system is secure at all times",
            "sometimes door is open eventually",
            "eventually output at time t equals output at time t minus 1",
            "always o1 at time t equals i1 at time t",
        ],
        
        "Logic Gates": [
            "AND gate: output equals input1 and input2",
            "OR gate: output equals input1 or input2",
            "NOT gate: output equals input1 complement", 
            "XOR gate: output equals (input1 and input2 complement) or (input1 complement and input2)",
        ],
        
        "Democracy System": [
            "majority rule: any two voters agree",
            "perfect harmony: all voters agree",
            "consensus equals (i1 and i2) or (i2 and i3) or (i1 and i3)",
            "harmony equals i1 and i2 and i3",
        ],
        
        "Feedback Systems": [
            "output at time t equals input at time t",
            "delayed output at time t equals input at time t minus 1 complement",
            "feedback combination equals input and secondary input",
            "complex feedback equals (previous feedback xor secondary) and combination",
        ],
        
        "Temporal Stability": [
            "output changes only when input is stable",
            "stability means output changes only when input stable for 2 time steps", 
            "output at time t not equals output at time t minus 1 implies input at time t equals input at time t minus 1",
        ],
        
        "Solver Commands": [
            "check satisfiability of complexFormula with a, b, c",
            "check validity of for all x, y, complexFormula implies (x or y)",
            "solve complexFormula with x, y, 0 and (x xor y)",
            "find solution to there exists z, complexFormula with 1, z, 0",
        ],
        
        "Advanced Quantifiers": [
            "for all x, y, if complexFormula of x, y, 1 then x or y",
            "there exists z such that complexFormula of 1, z, 0",
            "for all voters, if authenticated then can access database",
            "there exists x such that x is prime and x is greater than 10",
        ],
        
        "Complex Conditionals": [
            "if temperature is greater than 30 then cooling system activates",
            "if pressure exceeds 100 then safety valve opens automatically",
            "if all voters agree then decision is unanimous",
            "if system maintains security at all times then system is trusted",
        ],
        
        "Real-World Requirements": [
            "authenticated users can access the secure database", 
            "the system maintains security at all times during operation",
            "when network timeout occurs after 30 seconds then retry connection",
            "authentication token expires in 24 hours unless renewed",
            "file upload must complete successfully within 5 minutes",
        ]
    }
    
    print("🚀 Complex Tau Demo Cases Test")
    print("="*100)
    print("Testing real Tau language constructs from demos")
    print("Goal: Handle complex logical formulas, temporal logic, stream processing")
    print()
    
    overall_results = []
    
    for category, cases in demo_cases.items():
        print(f"\n🔍 Category: {category}")
        print("="*60)
        
        category_results = []
        for case in cases:
            result = tester.test_complex_case(case, category)
            category_results.append(result)
            overall_results.append(result)
        
        # Category summary
        ilr_success_count = sum(1 for r in category_results if r['ilr_success'])
        direct_success_count = sum(1 for r in category_results if r['direct_success'])
        both_success_count = sum(1 for r in category_results if r['ilr_success'] and r['direct_success'])
        
        print(f"\n📈 {category} Summary:")
        print(f"  ILR Pipeline:    {ilr_success_count}/{len(cases)} ({ilr_success_count/len(cases)*100:.1f}%)")
        print(f"  Direct Pipeline: {direct_success_count}/{len(cases)} ({direct_success_count/len(cases)*100:.1f}%)")
        print(f"  Both Succeeded:  {both_success_count}/{len(cases)} ({both_success_count/len(cases)*100:.1f}%)")
    
    # Overall summary
    print(f"\n{'='*100}")
    print("🎯 COMPLEX TAU DEMO RESULTS")
    print(f"{'='*100}")
    
    total_cases = len(overall_results)
    ilr_total_success = sum(1 for r in overall_results if r['ilr_success'])
    direct_total_success = sum(1 for r in overall_results if r['direct_success'])
    both_success = sum(1 for r in overall_results if r['ilr_success'] and r['direct_success'])
    
    print(f"Total complex cases tested: {total_cases}")
    print(f"ILR Pipeline success:       {ilr_total_success}/{total_cases} ({ilr_total_success/total_cases*100:.1f}%)")
    print(f"Direct Pipeline success:     {direct_total_success}/{total_cases} ({direct_total_success/total_cases*100:.1f}%)")
    print(f"Both succeeded:             {both_success}/{total_cases} ({both_success/total_cases*100:.1f}%)")
    
    print(f"\n💪 Best performing categories for complex cases:")
    for category, cases in demo_cases.items():
        category_results = [r for r in overall_results if r['category'] == category]
        direct_success_rate = sum(1 for r in category_results if r['direct_success']) / len(cases) * 100
        ilr_success_rate = sum(1 for r in category_results if r['ilr_success']) / len(cases) * 100
        
        if direct_success_rate >= 50 or ilr_success_rate >= 25:
            print(f"  ✅ {category}: Direct {direct_success_rate:.1f}%, ILR {ilr_success_rate:.1f}%")
    
    print(f"\n🛠️  Categories needing improvement:")
    for category, cases in demo_cases.items():
        category_results = [r for r in overall_results if r['category'] == category]
        direct_success_rate = sum(1 for r in category_results if r['direct_success']) / len(cases) * 100
        ilr_success_rate = sum(1 for r in category_results if r['ilr_success']) / len(cases) * 100
        
        if direct_success_rate < 50 and ilr_success_rate < 25:
            print(f"  🔧 {category}: Direct {direct_success_rate:.1f}%, ILR {ilr_success_rate:.1f}%")
    
    print(f"\n🔬 Analysis:")
    print(f"  • Complex Tau constructs are challenging for both pipelines")
    print(f"  • Direct pipeline performs better on pattern-matching cases")
    print(f"  • ILR pipeline provides semantic structure but needs more operators")
    print(f"  • Both pipelines excel at basic logic but struggle with temporal/stream constructs")
    print(f"  • Real-world requirements translation is the most challenging")


if __name__ == "__main__":
    run_complex_demo_test()