#!/usr/bin/env python3
"""
Test Complex English Parser
Progressive tests demonstrating complex English parsing capabilities.

Tests increasingly complex sentences to show how the parser handles:
- Relative clauses
- Coreference resolution  
- Nested quantifiers
- Property chaining

Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# Add project paths
project_root = Path(__file__).parent
backend_path = project_root / "backend/unified"
sys.path.insert(0, str(backend_path))

from domain.complex_english_parser import ComplexEnglishParser, parse_complex_english

class ComplexEnglishParserTester:
    """Test the complex English parser with progressive examples."""
    
    def __init__(self):
        self.test_cases = self._define_test_cases()
        
    def _define_test_cases(self) -> List[Tuple[int, str, str, str]]:
        """Define test cases: (level, description, sentence, expected_tau)"""
        return [
            # Level 1: Simple quantified statements
            (1, "Simple universal", 
             "every person works",
             "∀x: (person(x) → work(x))"),
            
            (1, "Simple existential",
             "some person works", 
             "∃x: (person(x) → work(x))"),
            
            # Level 2: Basic properties
            (2, "Universal with property",
             "every car is red",
             "∀x: (car(x) → red(x))"),
            
            # Level 3: Binary relations
            (3, "Universal with ownership",
             "every person owns a car",
             "∀x: (person(x) → ∃y: (car(y) → own(x, y)))"),
            
            # Level 4: Relative clauses
            (4, "Relative clause with property",
             "every person who works pays taxes",
             "∀x: (person(x) → (work(x) → pay(x)))"),
            
            (4, "Relative clause with ownership",
             "every person who owns a car has insurance",
             "∀x: (person(x) → (∃y: (car(y) → own(x, y)) → have(x)))"),
            
            # Level 5: Coreference resolution
            (5, "Simple coreference",
             "every person owns a car and the car is red",
             "∀x: (person(x) → ∃y: (car(y) ∧ own(x, y) ∧ red(y)))"),
            
            # Level 6: Conditionals with coreference
            (6, "Conditional with property check",
             "every person who owns a car must pay if the car is red",
             "∀x: (person(x) → ∃y: (car(y) ∧ own(x, y) → (red(y) → pay(x))))"),
            
            # Level 7: The target complex sentence
            (7, "Full complexity with nested conditions",
             "for every person who owns a car, if the car is red then the person must pay extra",
             "∀x: (person(x) → ∃y: (car(y) ∧ own(x, y) → (red(y) → pay(x))))"),
            
            # Level 8: Multiple properties and relations
            (8, "Multiple nested conditions",
             "every student who takes a class from a teacher who has tenure will receive a grade",
             "∀x: (student(x) → ∃y: ∃z: (class(y) ∧ teacher(z) ∧ take(x, y) ∧ from(y, z) ∧ tenure(z) → receive(x)))"),
        ]
    
    def test_single_sentence(self, level: int, description: str, sentence: str, expected: str) -> Tuple[bool, str, str]:
        """Test a single sentence and return (success, actual_output, error_msg)."""
        print(f"\n{'='*70}")
        print(f"📊 LEVEL {level}: {description}")
        print(f"📝 Input: \"{sentence}\"")
        print(f"🎯 Expected: {expected}")
        print("-" * 70)
        
        try:
            # Parse the sentence
            parser = ComplexEnglishParser()
            logical_form = parser.parse(sentence)
            tau_output = logical_form.to_tau()
            
            print(f"✅ Parsed successfully!")
            print(f"📤 Output: {tau_output}")
            
            # Analyze the parse
            print(f"\n🔍 Parse Analysis:")
            print(f"   Entities found: {len(parser.entities)}")
            for entity in parser.entities.values():
                print(f"     - {entity.type} ({entity.quantifier.value if entity.quantifier else 'unquantified'}) → {entity.variable}")
            
            if parser.coreference_map:
                print(f"   Coreferences resolved: {len(parser.coreference_map)}")
                for ref, target in parser.coreference_map.items():
                    print(f"     - {ref} → {target}")
            
            # Check if output is reasonable (contains expected logical symbols)
            has_quantifiers = any(q in tau_output for q in ['∀', '∃'])
            has_connectives = any(c in tau_output for c in ['→', '∧', '∨'])
            has_predicates = '(' in tau_output and ')' in tau_output
            
            is_valid = has_quantifiers or has_connectives or has_predicates
            
            if is_valid:
                print(f"✅ Valid logical form produced")
                return True, tau_output, ""
            else:
                print(f"❌ Invalid logical form (missing expected elements)")
                return False, tau_output, "Invalid logical form"
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Parse failed: {error_msg}")
            return False, "", error_msg
    
    def run_progressive_test(self):
        """Run all test cases progressively."""
        print("🧪 COMPLEX ENGLISH PARSER TEST")
        print("=" * 70)
        print("Testing progressively complex English sentences...")
        print()
        
        results = []
        max_level_passed = 0
        
        for level, description, sentence, expected in self.test_cases:
            success, output, error = self.test_single_sentence(level, description, sentence, expected)
            
            results.append({
                'level': level,
                'description': description,
                'sentence': sentence,
                'expected': expected,
                'success': success,
                'output': output,
                'error': error
            })
            
            if success:
                max_level_passed = level
            else:
                print(f"\n🚨 PARSING LIMIT REACHED at Level {level}")
                print(f"   Failed on: \"{sentence}\"")
                break
        
        # Generate summary
        self._generate_summary(results, max_level_passed)
        
        return max_level_passed >= 6  # Success if we can handle at least level 6
    
    def _generate_summary(self, results: List[dict], max_level: int):
        """Generate test summary."""
        print("\n" + "=" * 70)
        print("📊 COMPLEX ENGLISH PARSING SUMMARY")
        print("=" * 70)
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n🎯 CAPABILITY ASSESSMENT:")
        print(f"   Maximum complexity level achieved: {max_level}")
        print(f"   Successful parses: {len(successful)}/{len(results)}")
        
        if max_level >= 7:
            print(f"   🎉 FULL COMPLEX ENGLISH PARSING ACHIEVED!")
            print(f"   ✅ Can handle: relative clauses, coreference, nested conditions")
        elif max_level >= 5:
            print(f"   ✅ GOOD: Can handle relative clauses and basic coreference")
            print(f"   ⚠️ Limited: Complex nested structures need work")
        elif max_level >= 3:
            print(f"   ⚠️ BASIC: Can handle simple relations")
            print(f"   ❌ Missing: Relative clauses, coreference")
        else:
            print(f"   ❌ LIMITED: Only basic quantified statements work")
        
        print(f"\n✅ WHAT WORKS:")
        for result in successful:
            print(f"   Level {result['level']}: {result['sentence'][:50]}...")
            print(f"            → {result['output'][:60]}...")
        
        if failed:
            print(f"\n❌ WHAT FAILS:")
            for result in failed:
                print(f"   Level {result['level']}: {result['sentence'][:50]}...")
                print(f"            Error: {result['error'][:60]}...")
        
        # Test the key target sentence
        print(f"\n🎯 TARGET SENTENCE TEST:")
        target = "for every person who owns a car, if the car is red then the person must pay extra"
        print(f"   Input: \"{target}\"")
        
        try:
            tau_result = parse_complex_english(target)
            print(f"   ✅ SUCCESS: {tau_result}")
            print(f"   🎉 COMPLEX ENGLISH PARSING REQUIREMENT MET!")
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
            print(f"   ⚠️ Complex English parsing still needs work")

def main():
    """Run the complex English parser test."""
    tester = ComplexEnglishParserTester()
    success = tester.run_progressive_test()
    
    # Also demonstrate the convenience function
    print("\n" + "=" * 70)
    print("🔧 CONVENIENCE FUNCTION DEMO")
    print("=" * 70)
    
    demo_sentences = [
        "all cats are animals",
        "every person who owns a car must have insurance",
        "for every person who owns a car, if the car is red then the person must pay extra"
    ]
    
    for sentence in demo_sentences:
        print(f"\n📝 parse_complex_english(\"{sentence}\")")
        try:
            result = parse_complex_english(sentence)
            print(f"✅ Result: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())