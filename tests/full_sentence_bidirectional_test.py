#!/usr/bin/env python3
"""
Full Sentence Bidirectional Translation Test
Copyright: DarkLightX/Dana Edwards

Test: Natural Language ↔ Tau Code (full sentences, both directions)
Goal: Complete natural language specification to executable Tau code
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.unified.ilr_pipeline_simple import ILRPipelineSimple
from backend.unified.english_to_tau_integrated import IntegratedEnglishToTauTranslator


class FullSentenceBidirectionalTest:
    """Test full natural language sentences to Tau code and back."""
    
    def __init__(self):
        self.nl_to_tau = IntegratedEnglishToTauTranslator()
        self.ilr_pipeline = ILRPipelineSimple()
    
    def test_full_sentence_translation(self, sentence: str, category: str):
        """Test full sentence translation to Tau and back."""
        print(f"\n{'='*100}")
        print(f"Category: {category}")
        print(f"Original English: {sentence}")
        print(f"{'='*100}")
        
        # Step 1: English → Tau
        print("\n🌍 English → Tau Translation:")
        success_to_tau, tau_code, tce_intermediate = self.nl_to_tau.translate(sentence)
        
        if success_to_tau:
            print(f"  ✅ Success: {sentence}")
            print(f"  📝 TCE:     {tce_intermediate}")
            print(f"  ⚙️  Tau:     {tau_code}")
        else:
            print(f"  ❌ Failed to translate to Tau")
            return {
                'category': category,
                'original': sentence,
                'to_tau_success': False,
                'tau_code': '',
                'roundtrip_success': False,
                'final_english': ''
            }
        
        # Step 2: Tau → English (simulate reverse translation)
        print(f"\n🔄 Tau → English Translation (Simulated):")
        reverse_english = self._tau_to_english_simulation(tau_code, tce_intermediate)
        print(f"  📝 Reconstructed: {reverse_english}")
        
        # Step 3: Compare roundtrip quality
        print(f"\n📊 Roundtrip Analysis:")
        semantic_match = self._analyze_semantic_match(sentence, reverse_english)
        print(f"  Original:      {sentence}")
        print(f"  Reconstructed: {reverse_english}")
        print(f"  Semantic Match: {'✅' if semantic_match else '❌'}")
        
        return {
            'category': category,
            'original': sentence,
            'to_tau_success': success_to_tau,
            'tau_code': tau_code,
            'tce_intermediate': tce_intermediate,
            'reverse_english': reverse_english,
            'roundtrip_success': semantic_match
        }
    
    def _tau_to_english_simulation(self, tau_code: str, tce: str) -> str:
        """Simulate Tau → English translation using pattern matching."""
        # Use TCE as intermediate form for reverse translation
        if not tau_code:
            return "[Translation failed]"
        
        # Basic patterns for Tau → English
        english = tau_code
        
        # Boolean operators
        english = english.replace('&', ' and ')
        english = english.replace('|', ' or ')
        english = english.replace("'", ' not ')
        english = english.replace('~', ' not ')
        english = english.replace('^', ' xor ')
        
        # Comparison operators
        english = english.replace(' = ', ' equals ')
        english = english.replace(' > ', ' is greater than ')
        english = english.replace(' < ', ' is less than ')
        english = english.replace(' >= ', ' is at least ')
        english = english.replace(' <= ', ' is at most ')
        english = english.replace(' != ', ' is not equal to ')
        
        # Remove extra parentheses and normalize
        english = english.replace('(', '').replace(')', '')
        english = ' '.join(english.split())  # Normalize whitespace
        
        # Use TCE for better reconstruction if available
        if tce and len(tce) > len(english):
            tce_english = tce.replace('.', '')
            # Convert TCE operators back to natural language
            tce_english = tce_english.replace(' = ', ' equals ')
            tce_english = tce_english.replace(' > ', ' is greater than ')
            tce_english = tce_english.replace(' < ', ' is less than ')
            return tce_english
        
        return english
    
    def _analyze_semantic_match(self, original: str, reconstructed: str) -> bool:
        """Analyze if reconstructed sentence has same semantic meaning."""
        # Normalize for comparison
        orig_words = set(original.lower().replace(',', '').split())
        recon_words = set(reconstructed.lower().replace(',', '').split())
        
        # Check for key semantic elements
        key_elements = ['equals', 'and', 'or', 'not', 'greater', 'less', 'if', 'then', 'all', 'some']
        
        orig_elements = orig_words & set(key_elements)
        recon_elements = recon_words & set(key_elements)
        
        # Check variable names
        orig_vars = {w for w in orig_words if len(w) == 1 and w.isalpha()}
        recon_vars = {w for w in recon_words if len(w) == 1 and w.isalpha()}
        
        # Semantic match if key elements and variables preserved
        elements_match = len(orig_elements & recon_elements) >= len(orig_elements) * 0.8
        vars_match = len(orig_vars & recon_vars) >= len(orig_vars) * 0.8
        
        return elements_match and vars_match


def run_full_sentence_test():
    """Test full sentence bidirectional translation."""
    tester = FullSentenceBidirectionalTest()
    
    # Full natural language sentences for testing
    test_sentences = {
        "Simple Logic": [
            "x and y are both true",
            "either a or b must be true",
            "x is not equal to zero",
            "the value of temperature equals 25",
            "pressure is greater than 100",
        ],
        
        "Requirements Specifications": [
            "if the user is authenticated then they can access the database",
            "all users must have valid passwords",
            "the system must always maintain security",
            "when the temperature exceeds 30 degrees then the cooling system activates",
            "file upload must complete successfully within the timeout period",
        ],
        
        "Mathematical Constraints": [
            "x plus y equals z",
            "the sum of a and b is greater than c",
            "if x is prime then x is greater than 1",
            "for all numbers n, if n is even then n is divisible by 2",
            "there exists a value x such that x squared equals 4",
        ],
        
        "System Behavior": [
            "the output signal equals the input signal and the enable flag",
            "when the button is pressed the LED turns on",
            "the alarm triggers if pressure exceeds the safety limit",
            "data is valid only when both checksum and timestamp are correct",
            "the process completes when all inputs have been processed",
        ],
        
        "Temporal Logic": [
            "the system is always secure during operation",
            "sometimes the cache needs to be refreshed",
            "eventually all pending requests will be processed",
            "the backup runs daily at midnight",
            "monitoring continues until the process terminates",
        ],
        
        "Complex Requirements": [
            "authenticated users with valid tokens can access protected resources",
            "the system maintains consistency even when multiple clients connect simultaneously",
            "data synchronization occurs whenever changes are detected in the primary database",
            "error recovery mechanisms activate automatically when failures are detected",
            "the load balancer distributes requests evenly across available servers",
        ]
    }
    
    print("🌍 Full Sentence Bidirectional Translation Test")
    print("="*100)
    print("Testing: Natural Language ↔ Tau Code (complete sentences)")
    print("Goal: Translate full specifications to executable Tau code and back")
    print()
    
    all_results = []
    
    for category, sentences in test_sentences.items():
        print(f"\n📚 Category: {category}")
        print("="*60)
        
        category_results = []
        for sentence in sentences:
            result = tester.test_full_sentence_translation(sentence, category)
            category_results.append(result)
            all_results.append(result)
        
        # Category summary
        to_tau_success = sum(1 for r in category_results if r['to_tau_success'])
        roundtrip_success = sum(1 for r in category_results if r['roundtrip_success'])
        
        print(f"\n📈 {category} Summary:")
        print(f"  English → Tau:    {to_tau_success}/{len(sentences)} ({to_tau_success/len(sentences)*100:.1f}%)")
        print(f"  Roundtrip Quality: {roundtrip_success}/{len(sentences)} ({roundtrip_success/len(sentences)*100:.1f}%)")
    
    # Overall analysis
    print(f"\n{'='*100}")
    print("🎯 FULL SENTENCE TRANSLATION RESULTS")
    print(f"{'='*100}")
    
    total_sentences = len(all_results)
    to_tau_total = sum(1 for r in all_results if r['to_tau_success'])
    roundtrip_total = sum(1 for r in all_results if r['roundtrip_success'])
    
    print(f"Total sentences tested: {total_sentences}")
    print(f"English → Tau success: {to_tau_total}/{total_sentences} ({to_tau_total/total_sentences*100:.1f}%)")
    print(f"Bidirectional quality: {roundtrip_total}/{total_sentences} ({roundtrip_total/total_sentences*100:.1f}%)")
    
    print(f"\n🏆 Best Performing Categories:")
    for category, sentences in test_sentences.items():
        category_results = [r for r in all_results if r['category'] == category]
        success_rate = sum(1 for r in category_results if r['to_tau_success']) / len(sentences) * 100
        if success_rate >= 80:
            print(f"  ✅ {category}: {success_rate:.1f}% translation success")
    
    print(f"\n🔧 Challenging Categories:")
    for category, sentences in test_sentences.items():
        category_results = [r for r in all_results if r['category'] == category]
        success_rate = sum(1 for r in category_results if r['to_tau_success']) / len(sentences) * 100
        if success_rate < 80:
            print(f"  🛠️  {category}: {success_rate:.1f}% translation success")
    
    print(f"\n📊 Translation Quality Analysis:")
    
    # Show some successful examples
    successful_translations = [r for r in all_results if r['to_tau_success']]
    if successful_translations:
        print(f"\n✅ Successful Translation Examples:")
        for i, result in enumerate(successful_translations[:3]):
            print(f"  {i+1}. \"{result['original']}\"")
            print(f"     → {result['tau_code']}")
    
    # Show challenging cases
    failed_translations = [r for r in all_results if not r['to_tau_success']]
    if failed_translations:
        print(f"\n🔧 Challenging Cases Needing Improvement:")
        for i, result in enumerate(failed_translations[:3]):
            print(f"  {i+1}. \"{result['original']}\"")
            print(f"     → Translation failed")
    
    print(f"\n🚀 Full Sentence Translation Capability:")
    if to_tau_total/total_sentences >= 0.8:
        print("  🏆 EXCELLENT: Ready for production natural language specification translation")
    elif to_tau_total/total_sentences >= 0.6:
        print("  ⚡ GOOD: Handles most natural language specifications well")
    elif to_tau_total/total_sentences >= 0.4:
        print("  🔧 DEVELOPING: Handles basic natural language, needs improvement for complex cases")
    else:
        print("  📚 EARLY STAGE: Focus on expanding natural language pattern recognition")
    
    print(f"\n🔄 Bidirectional Translation Capability:")
    if roundtrip_total/total_sentences >= 0.6:
        print("  🏆 EXCELLENT: Strong bidirectional translation preserving semantics")
    elif roundtrip_total/total_sentences >= 0.4:
        print("  ⚡ GOOD: Reasonable semantic preservation in reverse translation")
    else:
        print("  🔧 DEVELOPING: Reverse translation needs improvement for better semantics")


def test_paragraph_translation():
    """Test translation of full paragraphs/specifications."""
    print(f"\n{'='*100}")
    print("📄 PARAGRAPH TRANSLATION TEST")
    print(f"{'='*100}")
    
    tester = FullSentenceBidirectionalTest()
    
    # Test paragraph specifications
    paragraphs = [
        {
            "title": "Authentication System",
            "text": "Users must authenticate with valid credentials. If authentication succeeds then users can access protected resources. The system logs all authentication attempts. Invalid login attempts are blocked after three failures."
        },
        {
            "title": "Temperature Control",
            "text": "The temperature sensor monitors the current temperature. If temperature exceeds 30 degrees then the cooling system activates. The cooling system runs until temperature drops below 28 degrees. An alarm sounds if temperature exceeds 35 degrees."
        },
        {
            "title": "Data Processing Pipeline",
            "text": "Input data is validated before processing. Valid data enters the processing queue. The system processes data in first-in-first-out order. Results are stored when processing completes successfully."
        }
    ]
    
    for para in paragraphs:
        print(f"\n📋 {para['title']}:")
        print(f"Original: {para['text']}")
        
        # Split into sentences and translate each
        sentences = para['text'].split('. ')
        tau_clauses = []
        
        for sentence in sentences:
            if sentence.strip():
                if not sentence.endswith('.'):
                    sentence += '.'
                
                success, tau, tce = tester.nl_to_tau.translate(sentence.strip())
                if success:
                    tau_clauses.append(tau)
                    print(f"  ✅ \"{sentence.strip()}\" → {tau}")
                else:
                    print(f"  ❌ \"{sentence.strip()}\" → Failed")
        
        if tau_clauses:
            print(f"\n🔗 Combined Tau Specification:")
            combined_tau = " && ".join(f"({clause})" for clause in tau_clauses)
            print(f"  {combined_tau}")


if __name__ == "__main__":
    run_full_sentence_test()
    test_paragraph_translation()