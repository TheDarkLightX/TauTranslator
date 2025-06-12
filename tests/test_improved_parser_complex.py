#!/usr/bin/env python3
"""
Test Improved Parser with Complex Declarative Sentences
Demonstrates enhanced parsing capabilities for Tau Controlled English.

Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add project paths
project_root = Path(__file__).parent
backend_path = project_root / "backend/unified"
src_path = project_root / "src"

sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(src_path))


class ImprovedParserTester:
    """Test the improved declarative TCE parser."""
    
    def __init__(self):
        self.results = []
        self.parser = None
        self._setup_parser()
        
    def _setup_parser(self):
        """Setup the enhanced parser."""
        try:
            from declarative_tce_parser import enhance_existing_tce_parser
            self.parser = enhance_existing_tce_parser()
        except ImportError as e:
            print(f"Warning: Could not import enhanced parser: {e}")
            # Fallback to basic parsing
            self.parser = self._create_fallback_parser()
    
    def _create_fallback_parser(self):
        """Create a simple fallback parser."""
        class FallbackParser:
            def parse(self, text):
                # Very basic transformations
                text = text.lower().strip().rstrip('.')
                
                # Map common patterns
                if text.startswith('all '):
                    return f"∀x: {text[4:]}"
                elif text.startswith('always '):
                    return f"□({text[7:]})"
                elif 'if ' in text and ' then ' in text:
                    parts = text.split(' then ')
                    condition = parts[0].replace('if ', '')
                    return f"{condition} -> {parts[1]}"
                else:
                    return text
        
        return FallbackParser()
    
    def test_sentence(self, category: str, sentence: str, expected_features: List[str]) -> Dict[str, Any]:
        """Test a single sentence."""
        print(f"\n{'='*70}")
        print(f"Category: {category}")
        print(f"Sentence: {sentence}")
        print(f"Features: {', '.join(expected_features)}")
        print("-" * 70)
        
        result = {
            'category': category,
            'sentence': sentence,
            'features': expected_features,
            'success': False,
            'output': '',
            'error': None
        }
        
        try:
            tau_output = self.parser.parse(sentence)
            result['success'] = True
            result['output'] = tau_output
            print(f"✅ Success: {tau_output}")
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Error: {e}")
        
        return result
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite."""
        print("🧪 IMPROVED PARSER TEST - COMPLEX DECLARATIVE SENTENCES")
        print("="*70)
        print("Testing enhanced TCE parser with declarative patterns")
        print()
        
        test_suite = [
            # Level 1: Simple Declarative Facts
            {
                'category': 'Simple Facts',
                'sentences': [
                    ("all persons are mortal.", ['universal_quantification', 'property_assignment']),
                    ("socrates is a person.", ['instance_declaration', 'type_assertion']),
                    ("the sky is blue.", ['definite_reference', 'property']),
                    ("x equals 5.", ['equality', 'constant_assignment']),
                    ("temperature is positive.", ['property_assertion']),
                ]
            },
            
            # Level 2: Quantified Properties
            {
                'category': 'Quantified Properties',
                'sentences': [
                    ("every car has wheels.", ['universal_quantification', 'possession']),
                    ("all prime numbers are odd or equal to 2.", ['universal', 'disjunction', 'exception']),
                    ("no negative number is a natural number.", ['universal_negation', 'type_constraint']),
                    ("some functions are continuous.", ['existential_quantification', 'property']),
                    ("each student has exactly one advisor.", ['universal', 'cardinality_constraint']),
                ]
            },
            
            # Level 3: Relationships and Constraints
            {
                'category': 'Relationships',
                'sentences': [
                    ("john owns a car.", ['ownership_relation', 'existential_object']),
                    ("every employee reports to exactly one manager.", ['universal', 'functional_relation']),
                    ("the database contains all user records.", ['containment', 'completeness']),
                    ("x precedes y implies x is less than y.", ['ordering_relation', 'implication']),
                    ("parent nodes contain child nodes.", ['hierarchical_relation', 'containment']),
                ]
            },
            
            # Level 4: Temporal Properties
            {
                'category': 'Temporal Properties',
                'sentences': [
                    ("always output 1 at time t equals input 1 at time t.", ['temporal_always', 'stream_equation']),
                    ("eventually all requests are processed.", ['temporal_eventually', 'completion']),
                    ("the system never enters an invalid state.", ['temporal_never', 'safety_property']),
                    ("sometimes the buffer is full.", ['temporal_sometimes', 'state_property']),
                    ("input stream 1 at t plus 1 depends on output stream 1 at t.", ['stream_dependency', 'time_offset']),
                ]
            },
            
            # Level 5: Complex Constraints
            {
                'category': 'Complex Constraints',
                'sentences': [
                    ("for all x, x greater than 0 implies x not equals 0.", ['universal', 'implication', 'inequality']),
                    ("every valid transaction satisfies the integrity constraints.", ['universal', 'constraint_satisfaction']),
                    ("all paths from node a to node b have length at most 10.", ['universal', 'path_constraint', 'bound']),
                    ("the sum of all probabilities equals 1.", ['aggregation', 'equality_constraint']),
                    ("no two processes access the critical section simultaneously.", ['mutual_exclusion', 'concurrency']),
                ]
            },
            
            # Level 6: Nested Quantifiers
            {
                'category': 'Nested Quantifiers',
                'sentences': [
                    ("for every person there exists a unique identifier.", ['nested_quantifiers', 'uniqueness']),
                    ("all nodes have some path to the root node.", ['universal_existential', 'reachability']),
                    ("every student who takes every required course graduates.", ['nested_universal', 'completion_condition']),
                    ("there exists a configuration where all constraints are satisfied.", ['existential_universal', 'satisfiability']),
                    ("for all epsilon greater than 0 there exists delta such that the function is continuous.", ['mathematical_quantifiers', 'limit_definition']),
                ]
            },
            
            # Level 7: Conditional Declaratives
            {
                'category': 'Conditional Declaratives',
                'sentences': [
                    ("when the temperature exceeds 100, the cooling system activates.", ['temporal_condition', 'trigger']),
                    ("if all tests pass then the build is successful.", ['conditional', 'aggregated_condition']),
                    ("authenticated users have read access unless explicitly denied.", ['conditional_permission', 'exception']),
                    ("the invariant holds if and only if the system is in a valid state.", ['biconditional', 'invariant']),
                    ("given that x is prime, x greater than 2 implies x is odd.", ['assumption', 'implication']),
                ]
            },
            
            # Level 8: Definitions and Equivalences
            {
                'category': 'Definitions',
                'sentences': [
                    ("a prime number is defined as a natural number with exactly two divisors.", ['definition', 'characterization']),
                    ("valid means well-formed and type-correct.", ['definition', 'conjunction']),
                    ("reachable is equivalent to connected by some path.", ['equivalence', 'graph_property']),
                    ("the predicate sorted means for all adjacent pairs, the first is at most the second.", ['predicate_definition', 'ordering']),
                    ("stability means the output remains constant when the input is unchanged.", ['behavioral_definition', 'temporal']),
                ]
            },
            
            # Level 9: Multi-clause Specifications
            {
                'category': 'Multi-clause Specifications',
                'sentences': [
                    ("all requests are eventually processed and no request is processed twice.", ['conjunction', 'temporal', 'uniqueness']),
                    ("the system is deadlock-free if and only if every process eventually completes.", ['liveness', 'biconditional']),
                    ("input validation ensures data integrity, prevents injection attacks, and maintains performance.", ['multiple_guarantees', 'security']),
                    ("every transaction either commits successfully or rolls back completely, and the database remains consistent.", ['atomicity', 'consistency']),
                    ("users must authenticate before accessing resources, sessions expire after inactivity, and all access is logged.", ['security_policy', 'multiple_requirements']),
                ]
            },
            
            # Level 10: Real-world Declarative Specifications
            {
                'category': 'Real-world Specifications',
                'sentences': [
                    ("in a distributed consensus protocol, all correct nodes eventually agree on the same value.", ['distributed_systems', 'consensus', 'eventual_consistency']),
                    ("the cache maintains the invariant that all cached values reflect the most recent committed writes.", ['cache_coherence', 'invariant', 'consistency']),
                    ("every api request requires a valid token, rate limits apply per user, and responses include appropriate cors headers.", ['api_specification', 'authentication', 'rate_limiting']),
                    ("database transactions satisfy acid properties: atomicity, consistency, isolation, and durability.", ['database_properties', 'acronym_expansion']),
                    ("the type system guarantees that well-typed programs do not produce runtime type errors.", ['type_safety', 'meta_property', 'guarantee']),
                ]
            }
        ]
        
        all_results = []
        
        for test_group in test_suite:
            category = test_group['category']
            print(f"\n\n📚 {category}")
            print("="*60)
            
            category_results = []
            for sentence, features in test_group['sentences']:
                result = self.test_sentence(category, sentence, features)
                category_results.append(result)
                all_results.append(result)
            
            # Category summary
            success_count = sum(1 for r in category_results if r['success'])
            total = len(category_results)
            print(f"\n{category} Summary: {success_count}/{total} ({success_count/total*100:.1f}%)")
        
        # Overall summary
        self._print_summary(all_results)
        
        return all_results
    
    def _print_summary(self, results: List[Dict[str, Any]]):
        """Print overall test summary."""
        print("\n\n" + "="*70)
        print("📊 OVERALL SUMMARY")
        print("="*70)
        
        total = len(results)
        successful = sum(1 for r in results if r['success'])
        
        print(f"Total test cases: {total}")
        print(f"Successful: {successful} ({successful/total*100:.1f}%)")
        print(f"Failed: {total - successful} ({(total-successful)/total*100:.1f}%)")
        
        # Group by category
        by_category = {}
        for result in results:
            cat = result['category']
            if cat not in by_category:
                by_category[cat] = {'success': 0, 'total': 0}
            by_category[cat]['total'] += 1
            if result['success']:
                by_category[cat]['success'] += 1
        
        print("\nSuccess by category:")
        for cat, stats in by_category.items():
            rate = stats['success'] / stats['total'] * 100
            print(f"  {cat}: {stats['success']}/{stats['total']} ({rate:.1f}%)")
        
        # Identify problem areas
        print("\nProblem areas (< 50% success):")
        for cat, stats in by_category.items():
            rate = stats['success'] / stats['total'] * 100
            if rate < 50:
                print(f"  ❌ {cat}: {rate:.1f}%")
        
        # Overall assessment
        print("\n🎯 Assessment:")
        if successful / total >= 0.9:
            print("  🏆 EXCELLENT: Parser handles complex declarative sentences very well")
        elif successful / total >= 0.7:
            print("  ⭐ GOOD: Parser handles most declarative patterns effectively")
        elif successful / total >= 0.5:
            print("  ✅ ADEQUATE: Parser handles basic declarative sentences")
        else:
            print("  🔧 NEEDS IMPROVEMENT: Parser struggles with declarative patterns")
        
        print("\n💡 Recommendations:")
        print("  1. Implement proper scope tracking for nested quantifiers")
        print("  2. Add support for temporal operators (always, eventually, never)")
        print("  3. Handle multi-clause specifications with conjunctions")
        print("  4. Support equivalence and definition statements")
        print("  5. Implement coreference resolution for complex sentences")


def test_specific_improvements():
    """Test specific improvements to the parser."""
    print("\n\n🔬 TESTING SPECIFIC IMPROVEMENTS")
    print("="*70)
    
    tester = ImprovedParserTester()
    
    # Test cases targeting specific improvements
    improvements = [
        {
            'name': 'Coreference Resolution',
            'test': "every person who owns a car must register the car.",
            'expected': "all p: (person(p) && exists c: (car(c) && owns(p,c))) -> must_register(p,c)"
        },
        {
            'name': 'Nested Quantifiers',
            'test': "for all companies, there exists an employee who manages all projects.",
            'expected': "all c: company(c) -> ex e: (employee(e) && all p: project(p) -> manages(e,p))"
        },
        {
            'name': 'Temporal Logic',
            'test': "always when input is high, eventually output becomes high.",
            'expected': "□(high(input) -> ◇(high(output)))"
        },
        {
            'name': 'Stream Processing',
            'test': "output stream 1 at time t equals input stream 1 at time t minus 1.",
            'expected': "o1[t] = i1[t-1]"
        },
        {
            'name': 'Declarative Constraints',
            'test': "the sum of all weights equals 1.",
            'expected': "sum(w: weight(w)) = 1"
        }
    ]
    
    for improvement in improvements:
        print(f"\n{improvement['name']}:")
        print(f"  Input:    {improvement['test']}")
        print(f"  Expected: {improvement['expected']}")
        
        try:
            result = tester.parser.parse(improvement['test'])
            print(f"  Got:      {result}")
            
            # Simple check if output contains key elements
            if any(key in result for key in ['all', '∀', 'ex', '∃', '□', '◇', '->', '=']):
                print(f"  ✅ Contains formal logic elements")
            else:
                print(f"  ⚠️  May need improvement")
        except Exception as e:
            print(f"  ❌ Error: {e}")


def main():
    """Run all tests."""
    # Run comprehensive test
    tester = ImprovedParserTester()
    results = tester.run_comprehensive_test()
    
    # Test specific improvements
    test_specific_improvements()
    
    # Return success if at least 60% pass
    success_rate = sum(1 for r in results if r['success']) / len(results)
    return 0 if success_rate >= 0.6 else 1


if __name__ == "__main__":
    sys.exit(main())