#!/usr/bin/env python3
"""
English Parsing Limits Test
Tests what our current system can actually handle vs. what it cannot.

Focuses on working with existing infrastructure to identify real capabilities
and limitations for complex English parsing.

Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
import asyncio
import re
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
class ParsingTestCase:
    """Test case for parsing capability assessment."""
    level: int
    sentence: str
    features: List[str]
    expected_patterns: List[str]
    difficulty: str

class EnglishParsingLimitsTester:
    """Test the actual limits of our English parsing capabilities."""
    
    def __init__(self):
        self.test_cases = self._define_realistic_test_cases()
        
    def _define_realistic_test_cases(self) -> List[ParsingTestCase]:
        """Define test cases based on what might actually work."""
        return [
            # Level 1: Basic TCE-like patterns
            ParsingTestCase(
                level=1,
                sentence="forall x: p(x)",
                features=["quantifier_colon"],
                expected_patterns=["∀", "x", "p(x)"],
                difficulty="trivial"
            ),
            
            ParsingTestCase(
                level=1,
                sentence="exists y such that q(y)",
                features=["quantifier_such_that"],
                expected_patterns=["∃", "y", "q(y)"],
                difficulty="trivial"
            ),
            
            # Level 2: Simple conditionals
            ParsingTestCase(
                level=2,
                sentence="if x > 5 then true else false",
                features=["conditional", "comparison", "boolean"],
                expected_patterns=["?", ":", ">", "5"],
                difficulty="easy"
            ),
            
            # Level 3: Basic English patterns
            ParsingTestCase(
                level=3,
                sentence="for all x, p holds",
                features=["english_quantifier"],
                expected_patterns=["∀", "x", "p"],
                difficulty="medium"
            ),
            
            ParsingTestCase(
                level=3,
                sentence="there exists x such that p is true",
                features=["english_existential"],
                expected_patterns=["∃", "x", "p"],
                difficulty="medium"
            ),
            
            # Level 4: Simple relative clauses
            ParsingTestCase(
                level=4,
                sentence="all people who work",
                features=["relative_clause_simple"],
                expected_patterns=["∀", "people", "work"],
                difficulty="hard"
            ),
            
            # Level 5: Property relationships
            ParsingTestCase(
                level=5,
                sentence="every person who owns a car",
                features=["property_ownership"],
                expected_patterns=["∀", "person", "owns", "car"],
                difficulty="very_hard"
            ),
            
            # Level 6: Nested conditions
            ParsingTestCase(
                level=6,
                sentence="for every person who owns a car, if the car is red then the person must pay extra",
                features=["nested_conditions", "coreference", "property_chaining"],
                expected_patterns=["∀", "person", "owns", "car", "if", "red", "then", "pay"],
                difficulty="extreme"
            ),
        ]
    
    def test_basic_tce_parsing(self, sentence: str) -> Tuple[bool, str, str]:
        """Test basic TCE parsing capability."""
        try:
            from lark import Lark
            from tau_translator_omega.core_engine.tce_tau_transformer import TCEToTauTransformer
            
            grammar_path = project_root / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
            with open(grammar_path, 'r') as f:
                grammar_content = f.read()
            
            parser = Lark(grammar_content, parser='lalr', start='start', propagate_positions=True)
            transformer = TCEToTauTransformer()
            
            # Add terminator if missing
            test_sentence = sentence if sentence.endswith('.') else sentence + '.'
            
            parse_tree = parser.parse(test_sentence)
            tau_output = transformer.transform(parse_tree)
            
            return True, str(tau_output), ""
            
        except Exception as e:
            return False, "", str(e)
    
    def test_pattern_based_translation(self, sentence: str) -> Tuple[bool, str, str]:
        """Test simple pattern-based English to TCE translation."""
        try:
            # Simple pattern-based transformations
            result = sentence.lower()
            
            # Basic English to TCE patterns
            patterns = [
                # Quantifiers
                (r'\ball\s+(\w+)', r'forall \\1:'),
                (r'\bevery\s+(\w+)', r'forall \\1:'),
                (r'\bfor\s+all\s+(\w+)', r'forall \\1:'),
                (r'\bthere\s+exists?\s+(?:a\s+|an\s+)?(\w+)', r'exists \\1 such that'),
                (r'\bsome\s+(\w+)', r'exists \\1 such that'),
                
                # Conditionals
                (r'\bif\s+(.+?)\s+then\s+(.+?)(?:\s+else\s+(.+))?', r'if \\1 then \\2'),
                
                # Comparisons
                (r'\bis\s+greater\s+than', ' > '),
                (r'\bis\s+less\s+than', ' < '),
                (r'\bis\s+equal\s+to', ' = '),
                
                # Relative clauses (simple)
                (r'\bwho\s+(\w+)', r'such that \\1'),
                (r'\bthat\s+(\w+)', r'such that \\1'),
                
                # Modal verbs
                (r'\bmust\s+(\w+)', r'\\1'),
                (r'\bshould\s+(\w+)', r'\\1'),
                (r'\bwill\s+(\w+)', r'\\1'),
                
                # Properties
                (r'\bowns?\s+(?:a\s+|an\s+)?(\w+)', r'owns(\\1)'),
                (r'\bhas\s+(?:a\s+|an\s+)?(\w+)', r'has(\\1)'),
                (r'\bis\s+(\w+)', r'is(\\1)'),
                
                # Cleanup
                (r'\s+', ' '),
                (r'^\s+|\s+$', ''),
            ]
            
            for pattern, replacement in patterns:
                result = re.sub(pattern, replacement, result)
            
            # Check if we made meaningful changes
            if result != sentence.lower() and len(result.strip()) > 0:
                return True, result, ""
            else:
                return False, result, "No meaningful transformation applied"
                
        except Exception as e:
            return False, "", str(e)
    
    def test_combined_approach(self, sentence: str) -> Tuple[bool, str, str]:
        """Test pattern-based translation followed by TCE parsing."""
        try:
            # Step 1: Pattern-based English to TCE
            pattern_success, tce_result, pattern_error = self.test_pattern_based_translation(sentence)
            
            if not pattern_success:
                return False, "", f"Pattern translation failed: {pattern_error}"
            
            # Step 2: Parse the TCE result
            tce_success, tau_result, tce_error = self.test_basic_tce_parsing(tce_result)
            
            if tce_success:
                return True, tau_result, f"Via pattern: {tce_result}"
            else:
                return False, tce_result, f"TCE parsing failed: {tce_error}"
                
        except Exception as e:
            return False, "", str(e)
    
    def test_single_sentence(self, test_case: ParsingTestCase) -> Dict[str, Any]:
        """Test a single sentence with multiple approaches."""
        print(f"\n{'='*60}")
        print(f"🎯 LEVEL {test_case.level} - {test_case.difficulty.upper()}")
        print(f"📝 \"{test_case.sentence}\"")
        print(f"🔧 Features: {', '.join(test_case.features)}")
        print("-" * 60)
        
        results = {
            "level": test_case.level,
            "sentence": test_case.sentence,
            "features": test_case.features,
            "difficulty": test_case.difficulty,
            "approaches": {},
            "overall_success": False,
            "best_approach": None,
            "best_output": ""
        }
        
        # Test different approaches
        approaches = [
            ("Direct TCE Parsing", self.test_basic_tce_parsing),
            ("Pattern Translation", self.test_pattern_based_translation),
            ("Combined Approach", self.test_combined_approach)
        ]
        
        successful_approaches = []
        
        for approach_name, test_method in approaches:
            print(f"\n🔍 {approach_name}:")
            
            success, output, error = test_method(test_case.sentence)
            
            results["approaches"][approach_name] = {
                "success": success,
                "output": output,
                "error": error
            }
            
            if success:
                successful_approaches.append(approach_name)
                print(f"  ✅ SUCCESS: '{output}'")
                
                # Check coverage of expected patterns
                coverage = self._calculate_coverage(output, test_case.expected_patterns)
                print(f"  📊 Pattern Coverage: {coverage:.1%}")
                
                if not results["best_approach"] or coverage > 0.5:
                    results["best_approach"] = approach_name
                    results["best_output"] = output
            else:
                print(f"  ❌ FAILED: {error}")
        
        results["overall_success"] = len(successful_approaches) > 0
        results["successful_approaches"] = successful_approaches
        
        print(f"\n📊 Result: {len(successful_approaches)} approach(es) worked")
        
        if results["overall_success"]:
            print(f"✅ LEVEL {test_case.level} PASSED ({test_case.difficulty})")
        else:
            print(f"❌ LEVEL {test_case.level} FAILED ({test_case.difficulty})")
            print(f"🚨 This marks our current parsing limit!")
            
        return results
    
    def _calculate_coverage(self, output: str, expected_patterns: List[str]) -> float:
        """Calculate what percentage of expected patterns are found."""
        if not expected_patterns:
            return 1.0
        
        output_str = str(output).lower()
        found = sum(1 for pattern in expected_patterns if pattern.lower() in output_str)
        return found / len(expected_patterns)
    
    def run_parsing_limits_test(self) -> Dict[str, Any]:
        """Run the complete parsing limits assessment."""
        print("🧪 ENGLISH PARSING CAPABILITIES ASSESSMENT")
        print("=" * 70)
        print("Testing what our current system can actually handle...")
        print()
        
        all_results = []
        max_level_passed = 0
        breaking_point = None
        
        for test_case in self.test_cases:
            result = self.test_single_sentence(test_case)
            all_results.append(result)
            
            if result["overall_success"]:
                max_level_passed = test_case.level
            else:
                # Found our breaking point
                if breaking_point is None:
                    breaking_point = test_case.level
                break
        
        # Generate final analysis
        return self._generate_assessment(all_results, max_level_passed, breaking_point)
    
    def _generate_assessment(self, results: List[Dict], max_level: int, breaking_point: Optional[int]) -> Dict[str, Any]:
        """Generate final assessment of parsing capabilities."""
        print("\n" + "=" * 70)
        print("📊 PARSING CAPABILITIES ASSESSMENT")
        print("=" * 70)
        
        successful_results = [r for r in results if r["overall_success"]]
        failed_results = [r for r in results if not r["overall_success"]]
        
        print(f"\n🎯 CAPABILITY SUMMARY:")
        print(f"   Maximum Level Achieved: {max_level}")
        print(f"   Breaking Point: Level {breaking_point or 'Not reached'}")
        print(f"   Successful Tests: {len(successful_results)}")
        print(f"   Failed Tests: {len(failed_results)}")
        
        if max_level == 0:
            capability_level = "None - System cannot parse even basic sentences"
        elif max_level <= 2:
            capability_level = "Basic - Can handle simple TCE-like inputs"
        elif max_level <= 4:
            capability_level = "Intermediate - Can handle some English patterns"
        elif max_level <= 6:
            capability_level = "Advanced - Can handle complex English structures"
        else:
            capability_level = "Expert - Can handle very complex parsing"
        
        print(f"   Overall Capability: {capability_level}")
        
        print(f"\n✅ WHAT WORKS:")
        for result in successful_results:
            best = result["best_approach"]
            print(f"   Level {result['level']}: {result['sentence'][:50]}... ({best})")
        
        print(f"\n❌ WHAT FAILS:")
        for result in failed_results:
            print(f"   Level {result['level']}: {result['sentence'][:50]}...")
            print(f"      Features: {', '.join(result['features'])}")
        
        print(f"\n💡 IMPROVEMENT RECOMMENDATIONS:")
        if breaking_point and breaking_point <= 3:
            print("   🔧 Priority 1: Fix basic English pattern recognition")
            print("   🔧 Priority 2: Improve quantifier handling")
            print("   🔧 Priority 3: Add simple conditional parsing")
        elif breaking_point and breaking_point <= 5:
            print("   🔧 Priority 1: Implement relative clause parsing")
            print("   🔧 Priority 2: Add property relationship handling")
            print("   🔧 Priority 3: Improve coreference resolution")
        else:
            print("   🔧 Focus on nested structure handling")
            print("   🔧 Implement proper semantic analysis")
            print("   🔧 Add context management for complex relationships")
        
        return {
            "max_level_achieved": max_level,
            "breaking_point": breaking_point,
            "capability_level": capability_level,
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "detailed_results": results
        }

def main():
    """Main test runner."""
    tester = EnglishParsingLimitsTester()
    assessment = tester.run_parsing_limits_test()
    
    # Exit successfully if we achieved at least Level 2
    success = assessment["max_level_achieved"] >= 2
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()