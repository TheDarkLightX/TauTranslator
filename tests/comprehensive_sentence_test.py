#!/usr/bin/env python3
"""
Comprehensive English Sentence to Tau Translation Test
Copyright: DarkLightX/Dana Edwards

Test both ILR and Direct pipelines with various English sentences.
Goal: Master translating one NL sentence to Tau code at a time.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.unified.ilr_pipeline_simple import ILRPipelineSimple
from backend.unified.english_to_tau_integrated import IntegratedEnglishToTauTranslator


class ComprehensiveSentenceTest:
    """Test various English sentences for translation quality."""
    
    def __init__(self):
        self.ilr_pipeline = ILRPipelineSimple()
        self.direct_pipeline = IntegratedEnglishToTauTranslator()
    
    def test_sentence(self, english: str):
        """Test a single sentence with both pipelines."""
        print(f"\n{'='*60}")
        print(f"English: {english}")
        print(f"{'='*60}")
        
        # Test ILR Pipeline
        print("\n🧠 ILR Pipeline (Semantic Structure):")
        ilr_result = self.ilr_pipeline.translate(english)
        print(f"  Success:   {ilr_result.success}")
        print(f"  ILR Type:  {ilr_result.ilr_type}")
        print(f"  TCE:       {ilr_result.tce_text}")
        print(f"  Tau:       {ilr_result.tau_code}")
        if not ilr_result.success and 'error' in ilr_result.metadata:
            print(f"  Error:     {ilr_result.metadata['error']}")
        
        # Test Direct Pipeline
        print("\n⚡ Direct Pipeline (Pattern Matching):")
        direct_success, direct_tau, direct_tce = self.direct_pipeline.translate(english)
        print(f"  Success:   {direct_success}")
        print(f"  TCE:       {direct_tce}")
        print(f"  Tau:       {direct_tau}")
        
        # Analysis
        print("\n📊 Analysis:")
        if ilr_result.success and direct_success:
            print("  ✅ Both pipelines succeeded")
            if ilr_result.tau_code == direct_tau:
                print("  🎯 Identical Tau output")
            else:
                print("  🔄 Different Tau outputs")
                print(f"     ILR:    '{ilr_result.tau_code}'")
                print(f"     Direct: '{direct_tau}'")
        elif ilr_result.success:
            print("  🧠 Only ILR succeeded")
        elif direct_success:
            print("  ⚡ Only Direct succeeded") 
        else:
            print("  ❌ Both pipelines failed")
        
        return {
            'english': english,
            'ilr_success': ilr_result.success,
            'direct_success': direct_success,
            'ilr_tau': ilr_result.tau_code,
            'direct_tau': direct_tau,
            'ilr_type': ilr_result.ilr_type
        }


def run_comprehensive_test():
    """Run comprehensive test with various sentence types."""
    tester = ComprehensiveSentenceTest()
    
    # Test sentences organized by complexity
    test_sentences = {
        "Basic Assignments": [
            "x equals 5",
            "temperature is 25", 
            "y is 10",
            "value equals zero",
        ],
        
        "Comparisons": [
            "x is greater than 10",
            "temperature is less than 30",
            "speed is at least 60",
            "pressure is at most 100",
        ],
        
        "Boolean Logic": [
            "x and y",
            "a or b", 
            "not p",
            "x and not y",
        ],
        
        "Conditionals": [
            "if x then y",
            "if temperature is high then cooling is on",
            "if pressure is greater than 50 then alarm is triggered",
        ],
        
        "Quantifiers": [
            "for all x, x equals x",
            "there exists x such that x is prime",
            "for every student, student has an id",
            "all users must have valid passwords",
        ],
        
        "Temporal Logic": [
            "always system is secure",
            "sometimes door is open", 
            "eventually process completes",
        ],
        
        "Complex Sentences": [
            "if temperature is greater than 30 then cooling system is activated",
            "all authenticated users can access the secure database",
            "when pressure exceeds 100 then safety valve opens automatically",
            "the system maintains security at all times during operation",
        ],
        
        "Real-World Examples": [
            "the user has valid credentials",
            "database connection is established",
            "file upload completed successfully",
            "network timeout occurred after 30 seconds",
            "authentication token expires in 24 hours",
        ]
    }
    
    print("🚀 Comprehensive English to Tau Translation Test")
    print("="*80)
    print("Testing both ILR (semantic) and Direct (pattern) pipelines")
    print("Goal: Master one sentence at a time translation\n")
    
    overall_results = []
    
    for category, sentences in test_sentences.items():
        print(f"\n🔍 Category: {category}")
        print("="*50)
        
        category_results = []
        for sentence in sentences:
            result = tester.test_sentence(sentence)
            category_results.append(result)
            overall_results.append(result)
        
        # Category summary
        ilr_success_count = sum(1 for r in category_results if r['ilr_success'])
        direct_success_count = sum(1 for r in category_results if r['direct_success'])
        print(f"\n📈 {category} Summary:")
        print(f"  ILR Pipeline:    {ilr_success_count}/{len(sentences)} ({ilr_success_count/len(sentences)*100:.1f}%)")
        print(f"  Direct Pipeline: {direct_success_count}/{len(sentences)} ({direct_success_count/len(sentences)*100:.1f}%)")
    
    # Overall summary
    print(f"\n{'='*80}")
    print("🎯 OVERALL RESULTS")
    print(f"{'='*80}")
    
    total_sentences = len(overall_results)
    ilr_total_success = sum(1 for r in overall_results if r['ilr_success'])
    direct_total_success = sum(1 for r in overall_results if r['direct_success'])
    both_success = sum(1 for r in overall_results if r['ilr_success'] and r['direct_success'])
    
    print(f"Total sentences tested: {total_sentences}")
    print(f"ILR Pipeline success:   {ilr_total_success}/{total_sentences} ({ilr_total_success/total_sentences*100:.1f}%)")
    print(f"Direct Pipeline success: {direct_total_success}/{total_sentences} ({direct_total_success/total_sentences*100:.1f}%)")
    print(f"Both succeeded:         {both_success}/{total_sentences} ({both_success/total_sentences*100:.1f}%)")
    
    print(f"\n💡 Best performing categories:")
    for category, sentences in test_sentences.items():
        category_results = [r for r in overall_results if r['english'] in sentences]
        success_rate = sum(1 for r in category_results if r['direct_success']) / len(sentences) * 100
        if success_rate >= 75:
            print(f"  ✅ {category}: {success_rate:.1f}% success")
    
    print(f"\n🔧 Areas needing improvement:")
    for category, sentences in test_sentences.items():
        category_results = [r for r in overall_results if r['english'] in sentences]
        success_rate = sum(1 for r in category_results if r['direct_success']) / len(sentences) * 100
        if success_rate < 75:
            print(f"  🔨 {category}: {success_rate:.1f}% success")


if __name__ == "__main__":
    run_comprehensive_test()