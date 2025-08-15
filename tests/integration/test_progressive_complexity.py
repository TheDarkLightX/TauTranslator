#!/usr/bin/env python3
"""
Progressive Complexity Test for English Parsing
Tests increasingly complex English sentences to find the limits of our parsing techniques.

This test helps identify exactly where our NLP parsing capabilities break down
and what specific linguistic structures need enhancement.

Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

# Add project paths
project_root = Path(__file__).parent
backend_path = project_root / "backend/unified"
src_path = project_root / "src"

sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(src_path))

@dataclass
class ComplexityTestCase:
    """Test case with complexity level."""
    level: int
    description: str
    english_sentence: str
    expected_elements: List[str]
    complexity_features: List[str]
    expected_success: bool = True

class ProgressiveComplexityTester:
    """Test English parsing with progressively complex sentences."""
    
    def __init__(self):
        self.test_cases = self._define_progressive_test_cases()
        self.results = []
        self.breaking_point = None
        
    def _define_progressive_test_cases(self) -> List[ComplexityTestCase]:
        """Define test cases in order of increasing complexity."""
        return [
            # Level 1: Simple statements
            ComplexityTestCase(
                level=1,
                description="Simple universal statement",
                english_sentence="All cats are animals",
                expected_elements=["all", "cats", "animals"],
                complexity_features=["universal_quantifier", "simple_predicate"]
            ),
            
            ComplexityTestCase(
                level=1,
                description="Simple existential statement", 
                english_sentence="Some dogs bark",
                expected_elements=["some", "dogs", "bark"],
                complexity_features=["existential_quantifier", "simple_predicate"]
            ),
            
            # Level 2: Simple conditionals
            ComplexityTestCase(
                level=2,
                description="Simple conditional",
                english_sentence="If it rains then I stay home",
                expected_elements=["if", "then", "rains", "stay"],
                complexity_features=["conditional", "simple_clauses"]
            ),
            
            ComplexityTestCase(
                level=2,
                description="Simple logical implication",
                english_sentence="If x is greater than 5 then x is positive",
                expected_elements=["if", "then", "greater", "positive"],
                complexity_features=["conditional", "comparison", "variables"]
            ),
            
            # Level 3: Quantified conditionals
            ComplexityTestCase(
                level=3,
                description="Universal conditional",
                english_sentence="For all x, if x is a cat then x is an animal",
                expected_elements=["for all", "if", "then", "cat", "animal"],
                complexity_features=["universal_quantifier", "conditional", "variable_scoping"]
            ),
            
            ComplexityTestCase(
                level=3,
                description="Existential with condition",
                english_sentence="There exists a person such that if the person is tall then the person plays basketball",
                expected_elements=["exists", "person", "if", "then", "tall", "basketball"],
                complexity_features=["existential_quantifier", "conditional", "coreference"]
            ),
            
            # Level 4: Simple relative clauses
            ComplexityTestCase(
                level=4,
                description="Universal with relative clause",
                english_sentence="All people who own cars must have insurance",
                expected_elements=["all", "people", "who", "own", "cars", "must", "insurance"],
                complexity_features=["universal_quantifier", "relative_clause", "modal_verb"]
            ),
            
            ComplexityTestCase(
                level=4,
                description="Existential with relative clause",
                english_sentence="There exists a student who studies math and likes puzzles",
                expected_elements=["exists", "student", "who", "studies", "math", "likes", "puzzles"],
                complexity_features=["existential_quantifier", "relative_clause", "conjunction"]
            ),
            
            # Level 5: Nested conditions with relative clauses
            ComplexityTestCase(
                level=5,
                description="Nested quantifier with conditional",
                english_sentence="For every person who owns a car, if the car is red then the person must pay extra",
                expected_elements=["every", "person", "who", "owns", "car", "if", "red", "then", "pay", "extra"],
                complexity_features=["universal_quantifier", "relative_clause", "nested_conditional", "coreference", "property_binding"]
            ),
            
            ComplexityTestCase(
                level=5,
                description="Multiple entity relationships",
                english_sentence="Every student who takes a class from a teacher must complete assignments",
                expected_elements=["every", "student", "takes", "class", "teacher", "complete", "assignments"],
                complexity_features=["universal_quantifier", "relative_clause", "three_entity_relationship", "transitive_relations"]
            ),
            
            # Level 6: Complex nested structures
            ComplexityTestCase(
                level=6,
                description="Double nested relative clauses",
                english_sentence="Every student who takes a class from a teacher who has tenure will receive a grade",
                expected_elements=["every", "student", "takes", "class", "teacher", "who", "tenure", "receive", "grade"],
                complexity_features=["universal_quantifier", "nested_relative_clauses", "multi_entity_chain", "scope_nesting"]
            ),
            
            ComplexityTestCase(
                level=6,
                description="Conditional with nested relative clause",
                english_sentence="If a person who owns a house lives in a city that has high taxes then the person pays more",
                expected_elements=["if", "person", "owns", "house", "lives", "city", "high", "taxes", "then", "pays", "more"],
                complexity_features=["conditional", "nested_relative_clauses", "multi_entity_relationships", "complex_conditions"]
            ),
            
            # Level 7: Very complex nested structures
            ComplexityTestCase(
                level=7,
                description="Multiple nested quantifiers with conditions",
                english_sentence="For all companies that employ workers who earn less than the minimum wage in states where unemployment is above 5%, the company must provide additional benefits",
                expected_elements=["all", "companies", "employ", "workers", "earn", "less", "minimum", "wage", "states", "unemployment", "above", "benefits"],
                complexity_features=["universal_quantifier", "deeply_nested_relative_clauses", "numerical_comparisons", "geographic_references", "policy_rules"],
                expected_success=False  # This should be too complex for current system
            ),
            
            # Level 8: Extremely complex with multiple logical operators
            ComplexityTestCase(
                level=8,
                description="Complex policy rule with multiple conditions",
                english_sentence="Every person who either owns a car manufactured before 2010 or lives in a building constructed with materials that contain asbestos must either relocate within 6 months or pay for safety inspections every year until compliance is achieved",
                expected_elements=["every", "person", "either", "owns", "car", "manufactured", "before", "2010", "or", "lives", "building", "materials", "asbestos", "relocate", "months", "pay", "inspections"],
                complexity_features=["universal_quantifier", "disjunctive_conditions", "temporal_references", "material_properties", "alternative_obligations", "temporal_constraints"],
                expected_success=False  # Definitely too complex
            ),
            
            # Level 9: Near-impossible complexity
            ComplexityTestCase(
                level=9,
                description="Multi-layered policy with exceptions and conditions",
                english_sentence="For all organizations that operate in jurisdictions where environmental regulations require companies that produce chemicals which may cause harm to wildlife in ecosystems that are protected by international treaties to submit reports unless the chemicals are used exclusively for medical research approved by ethics committees that meet quarterly, the organization must maintain documentation for at least 10 years",
                expected_elements=["organizations", "jurisdictions", "environmental", "regulations", "companies", "chemicals", "harm", "wildlife", "ecosystems", "protected", "treaties", "reports", "unless", "medical", "research", "ethics", "committees", "quarterly", "documentation", "years"],
                complexity_features=["deeply_nested_quantifiers", "regulatory_exceptions", "multi_domain_references", "temporal_constraints", "conditional_exceptions", "institutional_hierarchies"],
                expected_success=False  # Impossible with current techniques
            )
        ]
    
    async def test_single_complexity_level(self, test_case: ComplexityTestCase) -> Dict[str, Any]:
        """Test a single complexity level and return detailed results."""
        print(f"\n{'='*10} LEVEL {test_case.level} {'='*10}")
        print(f"🎯 {test_case.description}")
        print(f"📝 Sentence: \"{test_case.english_sentence}\"")
        print(f"🔧 Complexity features: {', '.join(test_case.complexity_features)}")
        print("-" * 70)
        
        results = {
            "level": test_case.level,
            "description": test_case.description,
            "sentence": test_case.english_sentence,
            "complexity_features": test_case.complexity_features,
            "translation_results": {},
            "overall_success": False,
            "breaking_point": False
        }
        
        # Test multiple translation approaches
        approaches = [
            ("Pattern-based NLP Service", self._test_nlp_service),
            ("TCE Pipeline", self._test_tce_pipeline),
            ("Enhanced NL Parser", self._test_enhanced_parser),
            ("Bidirectional Engine", self._test_bidirectional_engine)
        ]
        
        successful_approaches = 0
        
        for approach_name, test_method in approaches:
            try:
                print(f"\n🔍 Testing {approach_name}:")
                
                success, output, error_msg = await test_method(test_case.english_sentence)
                
                results["translation_results"][approach_name] = {
                    "success": success,
                    "output": output,
                    "error": error_msg
                }
                
                if success:
                    successful_approaches += 1
                    print(f"  ✅ SUCCESS: '{output}'")
                    
                    # Check if output contains expected elements
                    coverage = self._calculate_coverage(output, test_case.expected_elements)
                    print(f"  📊 Coverage: {coverage:.1%}")
                else:
                    print(f"  ❌ FAILED: {error_msg}")
                
            except Exception as e:
                print(f"  💥 ERROR: {str(e)}")
                results["translation_results"][approach_name] = {
                    "success": False,
                    "output": "",
                    "error": str(e)
                }
        
        # Determine if this complexity level is manageable
        success_rate = successful_approaches / len(approaches)
        results["overall_success"] = success_rate >= 0.5  # At least 50% of approaches work
        results["success_rate"] = success_rate
        
        print(f"\n📊 Level {test_case.level} Results:")
        print(f"   Success Rate: {successful_approaches}/{len(approaches)} ({success_rate:.1%})")
        
        if not results["overall_success"] and test_case.expected_success:
            results["breaking_point"] = True
            print(f"   🚨 BREAKING POINT DETECTED at Level {test_case.level}")
            print(f"   💡 Features that caused failure: {', '.join(test_case.complexity_features)}")
        
        return results
    
    async def _test_nlp_service(self, sentence: str) -> Tuple[bool, str, str]:
        """Test with NLP translation service."""
        try:
            from domain.nlp_translation_service import NLPTranslationService
            from core.domain_types import SourceText
            
            service = NLPTranslationService()
            result = service.translate_to_tce(SourceText(sentence))
            
            if result.is_success():
                return True, str(result.value), ""
            else:
                return False, "", result.error
                
        except Exception as e:
            return False, "", f"NLP Service error: {str(e)}"
    
    async def _test_tce_pipeline(self, sentence: str) -> Tuple[bool, str, str]:
        """Test with English→TCE→TAU pipeline."""
        try:
            # Step 1: English to TCE using simple patterns
            import re
            
            tce_text = sentence.lower()
            
            # Apply basic English to TCE patterns
            patterns = [
                (r'all (\w+)', r'forall \1:'),
                (r'every (\w+)', r'forall \1:'),
                (r'for all (\w+)', r'forall \1:'),
                (r'some (\w+)', r'exists \1 such that'),
                (r'there exists? (?:a |an )?(\w+)', r'exists \1 such that'),
                (r'if (.+?) then (.+)', r'if \1 then \2'),
                (r'is greater than', '>'),
                (r'is less than', '<'),
                (r'who (\w+)', r'such that \1'),
                (r'must (\w+)', r'\1'),
                (r'will (\w+)', r'\1')
            ]
            
            for pattern, replacement in patterns:
                tce_text = re.sub(pattern, replacement, tce_text)
            
            # Step 2: Try to parse as TCE
            from lark import Lark
            from tau_translator_omega.core_engine.tce_tau_transformer import TCEToTauTransformer
            
            grammar_path = project_root / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
            with open(grammar_path, 'r') as f:
                grammar_content = f.read()
            
            parser = Lark(grammar_content, parser='lalr', start='start', propagate_positions=True)
            transformer = TCEToTauTransformer()
            
            # Add terminator if missing
            if not tce_text.endswith('.'):
                tce_text += '.'
            
            parse_tree = parser.parse(tce_text)
            tau_output = transformer.transform(parse_tree)
            
            return True, str(tau_output), ""
            
        except Exception as e:
            return False, "", f"TCE Pipeline error: {str(e)}"
    
    async def _test_enhanced_parser(self, sentence: str) -> Tuple[bool, str, str]:
        """Test with enhanced natural language parser."""
        try:
            from tau_translator_omega.core_engine.parser.domain.natural_language_parser import NaturalLanguageParser
            
            parser = NaturalLanguageParser()
            result = await parser.parse_async(sentence)
            
            if result.is_success():
                return True, str(result.value), ""
            else:
                return False, "", result.error
                
        except Exception as e:
            return False, "", f"Enhanced Parser error: {str(e)}"
    
    async def _test_bidirectional_engine(self, sentence: str) -> Tuple[bool, str, str]:
        """Test with bidirectional translation engine."""
        try:
            from translators.bidirectional_engine import BidirectionalTranslationEngine
            from translators.base import TranslationDirection
            
            engine = BidirectionalTranslationEngine()
            result = engine.translate(sentence, TranslationDirection.TO_TAU)
            
            if result.success:
                return True, result.translated_text, ""
            else:
                return False, "", result.error_message or "Translation failed"
                
        except Exception as e:
            return False, "", f"Bidirectional Engine error: {str(e)}"
    
    def _calculate_coverage(self, output: str, expected_elements: List[str]) -> float:
        """Calculate how many expected elements are present in output."""
        if not expected_elements:
            return 1.0
        
        output_lower = output.lower()
        found_count = sum(1 for element in expected_elements if element.lower() in output_lower)
        return found_count / len(expected_elements)
    
    async def run_progressive_complexity_test(self) -> Dict[str, Any]:
        """Run the complete progressive complexity test."""
        print("🧪 PROGRESSIVE COMPLEXITY ANALYSIS")
        print("=" * 70)
        print("Testing English parsing with progressively complex sentences")
        print("to identify the limits of our current NLP techniques...")
        print()
        
        all_results = []
        breaking_point_found = False
        breaking_point_level = None
        
        for test_case in self.test_cases:
            result = await self.test_single_complexity_level(test_case)
            all_results.append(result)
            
            # Check if we found the breaking point
            if result.get("breaking_point") and not breaking_point_found:
                breaking_point_found = True
                breaking_point_level = test_case.level
                self.breaking_point = test_case.level
                
                print(f"\n🔥 BREAKING POINT IDENTIFIED: Level {test_case.level}")
                print(f"   Sentence that broke the system:")
                print(f"   \"{test_case.english_sentence}\"")
                print(f"   Complex features: {', '.join(test_case.complexity_features)}")
                break
        
        # Generate comprehensive analysis
        return self._generate_complexity_analysis(all_results, breaking_point_level)
    
    def _generate_complexity_analysis(self, results: List[Dict], breaking_point: Optional[int]) -> Dict[str, Any]:
        """Generate comprehensive analysis of complexity limits."""
        print("\n" + "=" * 70)
        print("📊 COMPLEXITY ANALYSIS RESULTS")
        print("=" * 70)
        
        # Calculate statistics
        successful_levels = [r for r in results if r["overall_success"]]
        failed_levels = [r for r in results if not r["overall_success"]]
        
        max_successful_level = max([r["level"] for r in successful_levels]) if successful_levels else 0
        
        print(f"\n🎯 CAPABILITY SUMMARY:")
        print(f"   Maximum Successful Level: {max_successful_level}")
        print(f"   Breaking Point: Level {breaking_point or 'Not reached'}")
        print(f"   Successful Levels: {len(successful_levels)}")
        print(f"   Failed Levels: {len(failed_levels)}")
        
        print(f"\n✅ TECHNIQUES THAT WORK WELL:")
        if successful_levels:
            for result in successful_levels:
                working_approaches = [name for name, data in result["translation_results"].items() if data["success"]]
                print(f"   Level {result['level']}: {', '.join(working_approaches)}")
        
        print(f"\n❌ COMPLEXITY FEATURES THAT CAUSE FAILURES:")
        if failed_levels:
            failure_features = set()
            for result in failed_levels:
                failure_features.update(result["complexity_features"])
            
            for feature in sorted(failure_features):
                print(f"   • {feature}")
        
        print(f"\n🔧 RECOMMENDATIONS FOR IMPROVEMENT:")
        if breaking_point:
            breaking_case = next(r for r in results if r["level"] == breaking_point)
            print(f"   1. Focus on handling: {', '.join(breaking_case['complexity_features'])}")
            print(f"   2. Implement proper relative clause parsing")
            print(f"   3. Add coreference resolution for entity tracking")
            print(f"   4. Enhance nested quantifier scope management")
            print(f"   5. Develop semantic role labeling for complex relationships")
        
        return {
            "max_successful_level": max_successful_level,
            "breaking_point": breaking_point,
            "successful_levels": len(successful_levels),
            "failed_levels": len(failed_levels),
            "detailed_results": results,
            "capability_assessment": "Limited" if max_successful_level <= 3 else "Moderate" if max_successful_level <= 5 else "Good"
        }

async def main():
    """Main test runner."""
    tester = ProgressiveComplexityTester()
    analysis = await tester.run_progressive_complexity_test()
    
    # Exit successfully if we can handle at least Level 3 complexity
    success = analysis["max_successful_level"] >= 3
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())