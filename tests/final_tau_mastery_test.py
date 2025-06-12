#!/usr/bin/env python3
"""
Final Tau Language Mastery Test
Copyright: DarkLightX/Dana Edwards

Comprehensive test with official IDNI Tau language constructs.
Based on: https://github.com/IDNI/tau-lang
Goal: Demonstrate mastery of English sentence to Tau code translation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.unified.ilr_pipeline_simple import ILRPipelineSimple
from backend.unified.english_to_tau_integrated import IntegratedEnglishToTauTranslator


class FinalTauMasteryTest:
    """Final comprehensive test with official Tau language patterns."""
    
    def __init__(self):
        self.ilr_pipeline = ILRPipelineSimple()
        self.direct_pipeline = IntegratedEnglishToTauTranslator()
    
    def test_translation_mastery(self, english: str, expected_tau: str, category: str, difficulty: str):
        """Test translation mastery with scoring."""
        print(f"\n{'='*90}")
        print(f"Category: {category} | Difficulty: {difficulty}")
        print(f"English: {english}")
        print(f"Target Tau: {expected_tau}")
        print(f"{'='*90}")
        
        # Test Direct Pipeline
        print("\n⚡ Direct Pipeline (Production Ready):")
        direct_success, direct_tau, direct_tce = self.direct_pipeline.translate(english)
        print(f"  Success:   {direct_success}")
        if direct_success:
            print(f"  TCE:       {direct_tce}")
            print(f"  Tau:       {direct_tau}")
            direct_score = self._score_translation(direct_tau, expected_tau, difficulty)
            print(f"  Score:     {direct_score}/10 {'🏆' if direct_score >= 8 else '⚡' if direct_score >= 6 else '🔧'}")
        else:
            direct_score = 0
            print(f"  Score:     0/10 ❌")
        
        # Test ILR Pipeline
        print("\n🧠 ILR Pipeline (Semantic Structure):")
        ilr_result = self.ilr_pipeline.translate(english)
        print(f"  Success:   {ilr_result.success}")
        if ilr_result.success:
            print(f"  ILR Type:  {ilr_result.ilr_type}")
            print(f"  TCE:       {ilr_result.tce_text}")
            print(f"  Tau:       {ilr_result.tau_code}")
            ilr_score = self._score_translation(ilr_result.tau_code, expected_tau, difficulty)
            print(f"  Score:     {ilr_score}/10 {'🏆' if ilr_score >= 8 else '🧠' if ilr_score >= 6 else '🔧'}")
        else:
            ilr_score = 0
            print(f"  Score:     0/10 ❌")
            print(f"  Error:     {ilr_result.metadata.get('error', 'Unknown')}")
        
        return {
            'category': category,
            'difficulty': difficulty,
            'english': english,
            'expected_tau': expected_tau,
            'direct_score': direct_score,
            'ilr_score': ilr_score,
            'direct_success': direct_success,
            'ilr_success': ilr_result.success
        }
    
    def _score_translation(self, actual: str, expected: str, difficulty: str) -> int:
        """Score translation accuracy (0-10)."""
        if not actual:
            return 0
        
        # Normalize for comparison
        actual_norm = actual.lower().replace(" ", "")
        expected_norm = expected.lower().replace(" ", "")
        
        # Perfect match
        if actual_norm == expected_norm:
            return 10
        
        # Check semantic equivalence
        score = 0
        
        # Core operators present
        tau_operators = ['&', '|', "'", '+', '=', '>', '<', '>=', '<=', ':=', '[t]', 'solve']
        for op in tau_operators:
            if op in expected_norm and op in actual_norm:
                score += 1
            elif op in expected_norm:
                # Check alternatives
                if op == '&' and ('and' in actual_norm):
                    score += 0.8
                elif op == '|' and ('or' in actual_norm):
                    score += 0.8
                elif op == "'" and ('not' in actual_norm or '~' in actual_norm):
                    score += 0.8
        
        # Variable names match
        import re
        expected_vars = re.findall(r'\b[a-z][a-z0-9]*\b', expected_norm)
        actual_vars = re.findall(r'\b[a-z][a-z0-9]*\b', actual_norm)
        
        matching_vars = set(expected_vars) & set(actual_vars)
        if expected_vars:
            score += (len(matching_vars) / len(set(expected_vars))) * 3
        
        # Structure similarity
        if '(' in expected_norm and ')' in expected_norm:
            if '(' in actual_norm and ')' in actual_norm:
                score += 1
        
        # Difficulty adjustment
        if difficulty == "Expert":
            score *= 0.8
        elif difficulty == "Advanced":
            score *= 0.9
        
        return min(10, int(score))


def run_final_mastery_test():
    """Run the final mastery test with official Tau constructs."""
    tester = FinalTauMasteryTest()
    
    # Official IDNI Tau language test cases organized by difficulty
    mastery_test_cases = [
        # Beginner: Basic Logic
        {
            "category": "Basic Logic",
            "difficulty": "Beginner",
            "cases": [
                ("x and y", "(x & y)"),
                ("x or y", "(x | y)"),
                ("not x", "x'"),
                ("x equals 0", "x = 0"),
                ("x not equals 0", "x != 0"),
            ]
        },
        
        # Intermediate: Boolean Functions
        {
            "category": "Boolean Functions", 
            "difficulty": "Intermediate",
            "cases": [
                ("x and y complement", "(x & y')"),
                ("x complement or y", "(x' | y)"),
                ("x xor y", "(x ^ y)"),
                ("x implies y", "(x -> y)"),
                ("x if and only if y", "(x <-> y)"),
            ]
        },
        
        # Intermediate: Solver Commands
        {
            "category": "Solver Commands",
            "difficulty": "Intermediate", 
            "cases": [
                ("solve x equals 0", "solve x = 0"),
                ("solve x equals 0 and y equals 0", "solve x = 0 && y = 0"),
                ("solve x not equals 0 and x complement not equals 0", "solve x != 0 && x' != 0"),
            ]
        },
        
        # Advanced: Function Definitions
        {
            "category": "Function Definitions",
            "difficulty": "Advanced",
            "cases": [
                ("f of x is defined as x complement", "f(x) := x'"),
                ("g of x and y is defined as x and y", "g(x,y) := x & y"),
                ("half adder sum of a and b is defined as a xor b", "halfAdderSum(a,b) := a ^ b"),
            ]
        },
        
        # Advanced: Stream Processing
        {
            "category": "Stream Processing",
            "difficulty": "Advanced",
            "cases": [
                ("o1 at time t equals x", "o1[t] = x"),
                ("output at time t equals input at time t and gate", "o[t] = i[t] & gate"),
                ("result o1 at time t equals i1 at time t or i2 at time t", "r o1[t] = i1[t] | i2[t]"),
            ]
        },
        
        # Expert: Temporal Logic  
        {
            "category": "Temporal Logic",
            "difficulty": "Expert",
            "cases": [
                ("always x at time t", "always x[t]"),
                ("sometimes y at time t", "sometimes y[t]"),
                ("o1 at time t equals i1 at time t minus 1", "o1[t] = i1[t-1]"),
                ("stability: output at time t equals output at time t minus 1", "o[t] = o[t-1]"),
            ]
        },
        
        # Expert: Complex Specifications
        {
            "category": "Complex Specifications",
            "difficulty": "Expert",
            "cases": [
                ("for all x, x equals x", "all x (x = x)"),
                ("there exists x such that x equals 0", "ex x (x = 0)"),
                ("always if input then output", "always (i -> o)"),
                ("sometimes harmony and always stability", "sometimes harmony && always stability"),
            ]
        }
    ]
    
    print("🎯 Final Tau Language Mastery Test")
    print("="*100)
    print("Testing English → Tau translation with official IDNI Tau language constructs")
    print("Scoring: 10 = Perfect, 8-9 = Excellent, 6-7 = Good, 4-5 = Fair, 0-3 = Needs Work")
    print()
    
    all_results = []
    total_direct_score = 0
    total_ilr_score = 0
    
    for test_group in mastery_test_cases:
        category = test_group["category"]
        difficulty = test_group["difficulty"]
        cases = test_group["cases"]
        
        print(f"\n📚 {category} ({difficulty})")
        print("="*80)
        
        group_results = []
        for english, expected_tau in cases:
            result = tester.test_translation_mastery(english, expected_tau, category, difficulty)
            group_results.append(result)
            all_results.append(result)
            total_direct_score += result['direct_score']
            total_ilr_score += result['ilr_score']
        
        # Group summary
        avg_direct = sum(r['direct_score'] for r in group_results) / len(group_results)
        avg_ilr = sum(r['ilr_score'] for r in group_results) / len(group_results)
        
        print(f"\n📊 {category} Summary:")
        print(f"  Direct Pipeline: {avg_direct:.1f}/10 {'🏆' if avg_direct >= 8 else '⚡' if avg_direct >= 6 else '🔧'}")
        print(f"  ILR Pipeline:    {avg_ilr:.1f}/10 {'🏆' if avg_ilr >= 8 else '🧠' if avg_ilr >= 6 else '🔧'}")
    
    # Final mastery assessment
    total_cases = len(all_results)
    avg_direct_score = total_direct_score / total_cases
    avg_ilr_score = total_ilr_score / total_cases
    
    print(f"\n{'='*100}")
    print("🏆 FINAL MASTERY ASSESSMENT")
    print(f"{'='*100}")
    
    print(f"Total test cases: {total_cases}")
    print(f"Direct Pipeline average score: {avg_direct_score:.1f}/10")
    print(f"ILR Pipeline average score:    {avg_ilr_score:.1f}/10")
    
    # Mastery levels
    def get_mastery_level(score):
        if score >= 9: return "🏆 Expert Mastery"
        elif score >= 8: return "⭐ Advanced Mastery"
        elif score >= 7: return "✅ Proficient"
        elif score >= 6: return "⚡ Good Understanding"
        elif score >= 4: return "🔧 Developing"
        else: return "📚 Needs Improvement"
    
    print(f"\nDirect Pipeline Mastery Level: {get_mastery_level(avg_direct_score)}")
    print(f"ILR Pipeline Mastery Level:    {get_mastery_level(avg_ilr_score)}")
    
    print(f"\n🎓 Mastery by Difficulty Level:")
    for difficulty in ["Beginner", "Intermediate", "Advanced", "Expert"]:
        diff_results = [r for r in all_results if r['difficulty'] == difficulty]
        if diff_results:
            avg_direct_diff = sum(r['direct_score'] for r in diff_results) / len(diff_results)
            avg_ilr_diff = sum(r['ilr_score'] for r in diff_results) / len(diff_results)
            print(f"  {difficulty:12}: Direct {avg_direct_diff:.1f}/10, ILR {avg_ilr_diff:.1f}/10")
    
    print(f"\n🚀 Translation Pipeline Status:")
    if avg_direct_score >= 8:
        print("  ✅ Direct Pipeline: PRODUCTION READY for English → Tau translation")
    elif avg_direct_score >= 6:
        print("  ⚡ Direct Pipeline: GOOD for most English → Tau translation tasks")
    else:
        print("  🔧 Direct Pipeline: NEEDS IMPROVEMENT for reliable translation")
    
    if avg_ilr_score >= 6:
        print("  ✅ ILR Pipeline: READY for semantic analysis and complex reasoning")
    elif avg_ilr_score >= 4:
        print("  🧠 ILR Pipeline: DEVELOPING semantic understanding capabilities")
    else:
        print("  🔧 ILR Pipeline: EARLY STAGE - good for basic semantic structure")
    
    print(f"\n🎯 Mission Status:")
    if avg_direct_score >= 7:
        print("  🏆 MISSION ACCOMPLISHED: Mastered English sentence → Tau code translation!")
        print("  📈 Ready for production use with English requirements → Tau specifications")
    else:
        print("  🔧 MISSION ONGOING: Good progress, continue improving translation accuracy")


if __name__ == "__main__":
    run_final_mastery_test()