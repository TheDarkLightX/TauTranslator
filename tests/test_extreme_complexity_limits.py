#!/usr/bin/env python3
"""
Extreme Complexity Test for Bidirectional Translation
Tests the absolute limits of what our translation technology can handle.

This test pushes boundaries with:
- Deeply nested quantifiers and logical structures
- Multiple entity relationships with complex constraints
- Temporal logic and stream processing
- Policy rules with exceptions, conditions, and institutional hierarchies
- Mathematical theorems and proofs
- Regulatory compliance specifications

Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Add project paths
project_root = Path(__file__).parent
backend_path = project_root / "backend/unified"
src_path = project_root / "src"

sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(src_path))

class ComplexityType(Enum):
    NESTED_QUANTIFIERS = "nested_quantifiers"
    TEMPORAL_LOGIC = "temporal_logic"
    MULTI_ENTITY = "multi_entity_relationships"
    REGULATORY = "regulatory_compliance"
    MATHEMATICAL = "mathematical_theorems"
    STREAM_PROCESSING = "stream_processing"
    POLICY_EXCEPTIONS = "policy_exceptions"
    RECURSIVE_DEFINITIONS = "recursive_definitions"
    META_CONSTRAINTS = "meta_constraints"
    HYBRID_COMPLEXITY = "hybrid_complexity"

@dataclass
class ExtremeTestCase:
    """Test case for extreme complexity testing."""
    id: str
    complexity_type: ComplexityType
    complexity_level: int  # 1-10 scale
    description: str
    english_sentence: str
    expected_tau_patterns: List[str]  # Key patterns that should appear in Tau
    linguistic_features: List[str]
    expected_to_break: bool = False
    notes: str = ""

class ExtremeLimitsTranslationTester:
    """Test extreme complexity limits of bidirectional translation."""
    
    def __init__(self):
        self.test_cases = self._generate_extreme_test_cases()
        self.results = []
        self.complexity_threshold = None
        
    def _generate_extreme_test_cases(self) -> List[ExtremeTestCase]:
        """Generate progressively extreme test cases."""
        return [
            # Level 1-3: Advanced but manageable
            ExtremeTestCase(
                id="ADV-1",
                complexity_type=ComplexityType.NESTED_QUANTIFIERS,
                complexity_level=3,
                description="Nested universal and existential quantifiers",
                english_sentence="For every company, there exists at least one employee such that if the employee is a manager then all projects managed by that employee must be profitable",
                expected_tau_patterns=["all company", "ex employee", "all project", "->", "profitable"],
                linguistic_features=["nested_quantifiers", "conditional_constraints", "transitive_relations"]
            ),
            
            ExtremeTestCase(
                id="ADV-2",
                complexity_type=ComplexityType.TEMPORAL_LOGIC,
                complexity_level=3,
                description="Simple temporal constraints",
                english_sentence="The system must always maintain security and eventually process all requests",
                expected_tau_patterns=["always", "security", "&&", "eventually", "process", "request"],
                linguistic_features=["temporal_operators", "conjunctive_requirements"]
            ),
            
            # Level 4-5: Complex but potentially parseable
            ExtremeTestCase(
                id="COMP-1",
                complexity_type=ComplexityType.MULTI_ENTITY,
                complexity_level=5,
                description="Four-entity relationship with constraints",
                english_sentence="Every student who enrolls in a course taught by a professor who supervises a research project must submit assignments to that professor before the project deadline",
                expected_tau_patterns=["all student", "course", "professor", "project", "assignment", "deadline", "->"],
                linguistic_features=["4_entity_chain", "temporal_constraint", "coreference_complex", "relative_clauses_nested"]
            ),
            
            ExtremeTestCase(
                id="COMP-2",
                complexity_type=ComplexityType.STREAM_PROCESSING,
                complexity_level=5,
                description="Stream processing with time windows",
                english_sentence="When the input stream contains three consecutive high values within a 5-second window, the output stream must signal an alert for the next 10 seconds",
                expected_tau_patterns=["i1[t]", "i1[t-1]", "i1[t-2]", "high", "->", "o1[t]", "alert"],
                linguistic_features=["stream_variables", "time_windows", "consecutive_patterns", "delayed_effects"]
            ),
            
            # Level 6-7: Very complex, likely to challenge the system
            ExtremeTestCase(
                id="VCOMP-1",
                complexity_type=ComplexityType.REGULATORY,
                complexity_level=7,
                description="Multi-jurisdictional regulatory compliance",
                english_sentence="Organizations operating in jurisdictions where data protection laws require consent for processing personal information of individuals who are either minors or residents of countries with enhanced privacy rights must implement age verification systems unless the data is processed solely for medical research approved by an ethics committee that meets international standards",
                expected_tau_patterns=["all organization", "jurisdiction", "data_protection", "consent", "personal_information", "minor", "||", "resident", "->", "age_verification", "unless", "medical_research", "ethics_committee"],
                linguistic_features=["multi_level_conditions", "disjunctive_subjects", "exception_clauses", "institutional_references", "nested_requirements"],
                expected_to_break=True
            ),
            
            ExtremeTestCase(
                id="VCOMP-2",
                complexity_type=ComplexityType.MATHEMATICAL,
                complexity_level=7,
                description="Mathematical theorem with multiple conditions",
                english_sentence="For all positive integers n greater than 2, if n is prime then there exists no pair of positive integers a and b such that a raised to the power n plus b raised to the power n equals c raised to the power n for any positive integer c",
                expected_tau_patterns=["all n", "n > 2", "prime(n)", "->", "!ex a", "!ex b", "!ex c", "pow(a,n)", "+", "pow(b,n)", "=", "pow(c,n)"],
                linguistic_features=["mathematical_quantifiers", "negated_existence", "power_operations", "fermat_reference"],
                expected_to_break=True
            ),
            
            # Level 8-9: Extreme complexity, expected to break
            ExtremeTestCase(
                id="EXT-1",
                complexity_type=ComplexityType.POLICY_EXCEPTIONS,
                complexity_level=8,
                description="Nested policy with multiple exception layers",
                english_sentence="Every financial institution that processes transactions exceeding $10,000 must report to the regulatory authority within 24 hours unless the transaction is between verified business accounts that have been active for more than 5 years and have no history of suspicious activity, except when the transaction involves cryptocurrency or is flagged by the AI monitoring system that uses machine learning models trained on patterns identified by international financial crime units",
                expected_tau_patterns=["all institution", "transaction", "> 10000", "->", "report", "unless", "verified", "active > 5", "!suspicious", "except", "cryptocurrency", "||", "ai_flag"],
                linguistic_features=["nested_exceptions", "multiple_unless_clauses", "compound_conditions", "technical_domain_mixing", "temporal_thresholds"],
                expected_to_break=True
            ),
            
            ExtremeTestCase(
                id="EXT-2",
                complexity_type=ComplexityType.RECURSIVE_DEFINITIONS,
                complexity_level=9,
                description="Recursive definition with self-reference",
                english_sentence="A valid configuration is one where every component that depends on another valid configuration must itself be valid, and a component is valid if all its sub-components are valid configurations or atomic elements that satisfy the base requirements",
                expected_tau_patterns=["valid_config", "component", "depends", "valid_config", "valid", "sub_component", "||", "atomic", "base_req"],
                linguistic_features=["recursive_definition", "self_reference", "circular_dependency", "base_case_definition"],
                expected_to_break=True
            ),
            
            # Level 10: Theoretically impossible complexity
            ExtremeTestCase(
                id="IMP-1",
                complexity_type=ComplexityType.META_CONSTRAINTS,
                complexity_level=10,
                description="Meta-level constraints about constraints",
                english_sentence="For any system specification that contains rules about how other rules can be modified, if a rule states that it cannot be overridden by rules created after a certain date, then any meta-rule that attempts to modify such immutable rules must either have been created before that date or have explicit authorization from a quorum of stakeholders who were registered in the system before the immutability declaration, unless the system is operating in emergency mode as determined by real-time analysis of at least three independent monitoring systems that each use different anomaly detection algorithms",
                expected_tau_patterns=["all spec", "rule", "meta_rule", "immutable", "date", "quorum", "stakeholder", "emergency_mode", "monitor", "anomaly"],
                linguistic_features=["meta_level_reasoning", "temporal_dependencies", "authorization_chains", "conditional_immutability", "multi_system_consensus", "algorithmic_references"],
                expected_to_break=True,
                notes="This represents the theoretical limit of complexity - meta-rules about rules with temporal, authorization, and algorithmic constraints"
            ),
            
            ExtremeTestCase(
                id="IMP-2",
                complexity_type=ComplexityType.HYBRID_COMPLEXITY,
                complexity_level=10,
                description="Ultimate hybrid complexity combining all features",
                english_sentence="In distributed systems where nodes can dynamically join or leave, for every consensus protocol that guarantees eventual consistency, there must exist a proof that demonstrates that if any subset of nodes experiences Byzantine failures while processing transactions that involve smart contracts which themselves can spawn child contracts that inherit permissions from parent contracts created by users who have multi-signature wallets requiring m-of-n signatures where m and n are determined by a governance token voting mechanism, then the system still maintains safety properties unless more than one-third of the total stake is controlled by adversarial actors who coordinate their actions through channels unobservable to the honest nodes",
                expected_tau_patterns=["all protocol", "eventual_consistency", "ex proof", "Byzantine", "smart_contract", "child_contract", "inherit", "multi_sig", "m_of_n", "governance", "safety", "unless", "stake > 1/3", "adversarial", "coordinate", "unobservable"],
                linguistic_features=["distributed_systems", "byzantine_fault_tolerance", "smart_contract_inheritance", "cryptographic_primitives", "governance_mechanisms", "threshold_conditions", "adversarial_modeling", "observability_constraints"],
                expected_to_break=True,
                notes="The ultimate test - combines distributed systems, cryptography, game theory, and governance in one sentence"
            )
        ]
    
    async def test_single_case(self, test_case: ExtremeTestCase) -> Dict[str, Any]:
        """Test a single extreme complexity case."""
        print(f"\n{'='*80}")
        print(f"🆔 {test_case.id} - Level {test_case.complexity_level}/10")
        print(f"🏷️  Type: {test_case.complexity_type.value}")
        print(f"📋 {test_case.description}")
        print(f"📝 Sentence: \"{test_case.english_sentence}\"")
        print(f"🔬 Features: {', '.join(test_case.linguistic_features)}")
        if test_case.notes:
            print(f"📌 Notes: {test_case.notes}")
        print("-" * 80)
        
        result = {
            "id": test_case.id,
            "complexity_level": test_case.complexity_level,
            "complexity_type": test_case.complexity_type.value,
            "sentence": test_case.english_sentence,
            "translations": {},
            "pattern_coverage": 0.0,
            "success": False,
            "breaking_features": []
        }
        
        # Test with multiple translation approaches
        translation_methods = [
            ("Pattern-based Translation", self._test_pattern_translation),
            ("Grammar-based Parser", self._test_grammar_parser),
            ("NLP Service", self._test_nlp_service),
            ("Bidirectional Engine", self._test_bidirectional),
            ("Enhanced ILR Pipeline", self._test_ilr_pipeline)
        ]
        
        successful_methods = []
        
        for method_name, method_func in translation_methods:
            try:
                print(f"\n🔧 Testing {method_name}:")
                success, output, error = await method_func(test_case.english_sentence)
                
                result["translations"][method_name] = {
                    "success": success,
                    "output": output,
                    "error": error
                }
                
                if success:
                    successful_methods.append(method_name)
                    print(f"  ✅ SUCCESS")
                    print(f"  📤 Output: {output[:100]}..." if len(output) > 100 else f"  📤 Output: {output}")
                    
                    # Check pattern coverage
                    coverage = self._calculate_pattern_coverage(output, test_case.expected_tau_patterns)
                    print(f"  📊 Pattern coverage: {coverage:.1%}")
                    result["pattern_coverage"] = max(result["pattern_coverage"], coverage)
                else:
                    print(f"  ❌ FAILED: {error}")
                    
                    # Identify breaking features
                    if error and any(feature in error.lower() for feature in ["parse", "syntax", "grammar"]):
                        result["breaking_features"].extend(test_case.linguistic_features)
                        
            except Exception as e:
                print(f"  💥 EXCEPTION: {str(e)}")
                result["translations"][method_name] = {
                    "success": False,
                    "output": "",
                    "error": f"Exception: {str(e)}"
                }
        
        # Overall success determination
        result["success"] = len(successful_methods) > 0
        result["successful_methods"] = successful_methods
        result["success_rate"] = len(successful_methods) / len(translation_methods)
        
        # Analysis
        print(f"\n📊 Case Analysis:")
        print(f"   Success Rate: {len(successful_methods)}/{len(translation_methods)} ({result['success_rate']:.1%})")
        print(f"   Pattern Coverage: {result['pattern_coverage']:.1%}")
        
        if not result["success"] and not test_case.expected_to_break:
            print(f"   🚨 UNEXPECTED FAILURE - This case should have worked!")
        elif result["success"] and test_case.expected_to_break:
            print(f"   🎉 UNEXPECTED SUCCESS - Exceeded expectations!")
        
        return result
    
    async def _test_pattern_translation(self, sentence: str) -> Tuple[bool, str, str]:
        """Test pattern-based translation."""
        try:
            from translators.pattern_translator import PatternTranslator
            translator = PatternTranslator()
            result = translator.translate_to_tau(sentence)
            return result["success"], result.get("translated", ""), result.get("error", "")
        except Exception as e:
            return False, "", f"Pattern translation error: {str(e)}"
    
    async def _test_grammar_parser(self, sentence: str) -> Tuple[bool, str, str]:
        """Test grammar-based parsing."""
        try:
            from tau_translator_omega.core_engine.parser_refactored import ParserRefactored
            parser = ParserRefactored()
            result = await parser.parse_natural_language(sentence)
            if result.success:
                return True, str(result.data), ""
            else:
                return False, "", result.error or "Grammar parsing failed"
        except Exception as e:
            return False, "", f"Grammar parser error: {str(e)}"
    
    async def _test_nlp_service(self, sentence: str) -> Tuple[bool, str, str]:
        """Test NLP translation service."""
        try:
            from api.nlp import translate_endpoint
            from core.domain_types import SourceText
            
            # Simulate API call
            result = await translate_endpoint(
                source_text=sentence,
                source_lang="english",
                target_lang="tau"
            )
            
            if "translated" in result:
                return True, result["translated"], ""
            else:
                return False, "", result.get("error", "NLP translation failed")
        except Exception as e:
            return False, "", f"NLP service error: {str(e)}"
    
    async def _test_bidirectional(self, sentence: str) -> Tuple[bool, str, str]:
        """Test bidirectional translation engine."""
        try:
            from translators.bidirectional_engine import BidirectionalTranslationEngine
            from translators.base import TranslationDirection
            
            engine = BidirectionalTranslationEngine()
            result = engine.translate(sentence, TranslationDirection.TO_TAU)
            
            if result.success:
                return True, result.translated_text, ""
            else:
                return False, "", result.error_message or "Bidirectional translation failed"
        except Exception as e:
            return False, "", f"Bidirectional engine error: {str(e)}"
    
    async def _test_ilr_pipeline(self, sentence: str) -> Tuple[bool, str, str]:
        """Test ILR pipeline translation."""
        try:
            from ilr_pipeline_simple import ILRPipelineSimple
            
            pipeline = ILRPipelineSimple()
            result = pipeline.translate_to_tau(sentence)
            
            if result["success"]:
                return True, result["tau"], ""
            else:
                return False, "", result.get("error", "ILR pipeline failed")
        except Exception as e:
            return False, "", f"ILR pipeline error: {str(e)}"
    
    def _calculate_pattern_coverage(self, output: str, expected_patterns: List[str]) -> float:
        """Calculate how many expected patterns appear in the output."""
        if not expected_patterns:
            return 1.0
        
        output_lower = output.lower()
        found = sum(1 for pattern in expected_patterns if pattern.lower() in output_lower)
        return found / len(expected_patterns)
    
    async def run_extreme_limits_test(self) -> Dict[str, Any]:
        """Run the complete extreme limits test."""
        print("🚀 EXTREME COMPLEXITY LIMITS TEST")
        print("=" * 80)
        print("Testing the absolute boundaries of bidirectional translation capability")
        print("Complexity scale: 1 (advanced) to 10 (theoretically impossible)")
        print()
        
        all_results = []
        max_successful_level = 0
        breaking_point = None
        
        # Group by complexity level
        for level in range(1, 11):
            level_cases = [tc for tc in self.test_cases if tc.complexity_level == level]
            if not level_cases:
                continue
                
            print(f"\n\n{'#'*80}")
            print(f"📈 COMPLEXITY LEVEL {level}/10")
            print(f"{'#'*80}")
            
            level_results = []
            for test_case in level_cases:
                result = await self.test_single_case(test_case)
                all_results.append(result)
                level_results.append(result)
                
                if result["success"]:
                    max_successful_level = max(max_successful_level, level)
            
            # Level summary
            level_success_rate = sum(1 for r in level_results if r["success"]) / len(level_results)
            print(f"\n📊 Level {level} Summary: {level_success_rate:.1%} success rate")
            
            # Check for breaking point
            if level_success_rate == 0 and breaking_point is None:
                breaking_point = level
                print(f"🚨 BREAKING POINT REACHED at Level {level}")
        
        # Generate comprehensive analysis
        return self._generate_extreme_analysis(all_results, max_successful_level, breaking_point)
    
    def _generate_extreme_analysis(self, results: List[Dict], max_level: int, breaking_point: Optional[int]) -> Dict[str, Any]:
        """Generate analysis of extreme complexity testing."""
        print("\n\n" + "=" * 80)
        print("🏁 EXTREME COMPLEXITY TEST RESULTS")
        print("=" * 80)
        
        # Group results by complexity type
        by_type = {}
        for result in results:
            ctype = result["complexity_type"]
            if ctype not in by_type:
                by_type[ctype] = []
            by_type[ctype].append(result)
        
        print("\n📊 CAPABILITY ASSESSMENT:")
        print(f"   Maximum Successful Complexity Level: {max_level}/10")
        print(f"   Breaking Point: Level {breaking_point}/10" if breaking_point else "   No definitive breaking point found")
        print(f"   Total Test Cases: {len(results)}")
        print(f"   Successful Cases: {sum(1 for r in results if r['success'])}")
        
        print("\n🎯 SUCCESS BY COMPLEXITY TYPE:")
        for ctype, type_results in by_type.items():
            success_rate = sum(1 for r in type_results if r["success"]) / len(type_results)
            print(f"   {ctype}: {success_rate:.1%} ({sum(1 for r in type_results if r['success'])}/{len(type_results)})")
        
        print("\n💪 STRONGEST CAPABILITIES:")
        strong_types = [(ctype, sum(1 for r in results if r["success"]) / len(results)) 
                       for ctype, results in by_type.items() if sum(1 for r in results if r["success"]) > 0]
        strong_types.sort(key=lambda x: x[1], reverse=True)
        for ctype, rate in strong_types[:3]:
            print(f"   ✅ {ctype}: {rate:.1%} success")
        
        print("\n🔧 AREAS NEEDING IMPROVEMENT:")
        weak_types = [(ctype, sum(1 for r in results if r["success"]) / len(results)) 
                     for ctype, results in by_type.items() if sum(1 for r in results if r["success"]) == 0]
        for ctype, rate in weak_types:
            print(f"   ❌ {ctype}: No successful translations")
        
        # Identify common breaking features
        all_breaking_features = []
        for result in results:
            if not result["success"]:
                all_breaking_features.extend(result["breaking_features"])
        
        if all_breaking_features:
            print("\n🚫 COMMON BREAKING FEATURES:")
            feature_counts = {}
            for feature in all_breaking_features:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
            
            sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
            for feature, count in sorted_features[:5]:
                print(f"   • {feature}: {count} failures")
        
        # Show unexpected results
        unexpected_successes = [r for r in results if r["success"] and r["complexity_level"] >= 7]
        unexpected_failures = [r for r in results if not r["success"] and r["complexity_level"] <= 5]
        
        if unexpected_successes:
            print("\n🎉 UNEXPECTED SUCCESSES (Level 7+):")
            for result in unexpected_successes:
                print(f"   • {result['id']}: Level {result['complexity_level']} - {result['complexity_type']}")
        
        if unexpected_failures:
            print("\n😟 UNEXPECTED FAILURES (Level 5-):")
            for result in unexpected_failures:
                print(f"   • {result['id']}: Level {result['complexity_level']} - {result['complexity_type']}")
        
        print("\n🔮 RECOMMENDATIONS FOR REACHING HIGHER COMPLEXITY:")
        print("   1. Implement proper coreference resolution for complex entity chains")
        print("   2. Add support for nested exception clauses (unless...except)")
        print("   3. Develop temporal logic operators (always, eventually, until)")
        print("   4. Handle recursive and self-referential definitions")
        print("   5. Implement meta-level reasoning about rules and constraints")
        print("   6. Add domain-specific parsers for regulatory/mathematical language")
        print("   7. Develop Byzantine fault tolerance semantics")
        print("   8. Implement stream processing temporal windows")
        
        print("\n📈 OVERALL ASSESSMENT:")
        if max_level >= 8:
            print("   🏆 EXCEPTIONAL: Can handle extremely complex specifications")
        elif max_level >= 6:
            print("   ⭐ EXCELLENT: Handles complex real-world specifications")
        elif max_level >= 4:
            print("   ✅ GOOD: Suitable for most practical applications")
        elif max_level >= 2:
            print("   🔧 DEVELOPING: Handles basic to intermediate complexity")
        else:
            print("   📚 EARLY STAGE: Focus on fundamental improvements")
        
        return {
            "max_complexity_level": max_level,
            "breaking_point": breaking_point,
            "total_cases": len(results),
            "successful_cases": sum(1 for r in results if r["success"]),
            "success_rate": sum(1 for r in results if r["success"]) / len(results),
            "by_type_analysis": by_type,
            "unexpected_successes": len(unexpected_successes),
            "unexpected_failures": len(unexpected_failures)
        }

async def main():
    """Run the extreme complexity test."""
    tester = ExtremeLimitsTranslationTester()
    analysis = await tester.run_extreme_limits_test()
    
    # Consider test successful if we can handle at least level 4 complexity
    success = analysis["max_complexity_level"] >= 4
    
    print(f"\n{'='*80}")
    print(f"🏁 Test {'PASSED' if success else 'FAILED'}")
    print(f"   Achieved complexity level: {analysis['max_complexity_level']}/10")
    print(f"{'='*80}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())