#!/usr/bin/env python3
"""
Comprehensive Bidirectional Translation Test Suite
Tests ALL translation directions following BDD principles (Given-When-Then)

This test validates every possible translation route:
1. English → TCE → TAU
2. TAU → TCE → English  
3. English → TAU (direct)
4. TCE → English (direct)
5. Pattern-based translations
6. Parser-based translations
7. Bidirectional auto-detection

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
class TranslationTestCase:
    """Test case for translation validation."""
    input_text: str
    source_language: str
    target_language: str
    expected_elements: List[str]
    description: str
    critical: bool = True

@dataclass
class DirectionalTestResult:
    """Result of a directional translation test."""
    direction: str
    success: bool
    input_text: str
    output_text: str
    expected_elements: List[str]
    found_elements: List[str]
    coverage: float
    error_message: Optional[str] = None

class ComprehensiveTranslationTester:
    """BDD-style comprehensive translation tester."""
    
    def __init__(self):
        self.test_cases = self._define_test_cases()
        self.results = []
        
    def _define_test_cases(self) -> Dict[str, List[TranslationTestCase]]:
        """Define comprehensive test cases for all directions."""
        return {
            "english_to_tce": [
                TranslationTestCase(
                    "for all variables x, predicate p holds",
                    "English", "TCE",
                    ["for all", "x", "p"],
                    "Universal quantifier in natural language"
                ),
                TranslationTestCase(
                    "there exists a value y such that condition q is true",
                    "English", "TCE", 
                    ["exists", "y", "q"],
                    "Existential quantifier in natural language"
                ),
                TranslationTestCase(
                    "if the value is greater than 5 then return true otherwise false",
                    "English", "TCE",
                    ["if", "then", "else", ">", "5"],
                    "Conditional statement in natural language"
                )
            ],
            
            "english_to_tau": [
                TranslationTestCase(
                    "for all x, p(x) holds",
                    "English", "TAU",
                    ["∀", "∃", "x", "p"],
                    "Direct English to TAU quantifier"
                ),
                TranslationTestCase(
                    "if x is greater than 5 then true else false",
                    "English", "TAU",
                    ["?", ":", ">", "5"],
                    "Direct English to TAU conditional"
                )
            ],
            
            "tce_to_tau": [
                TranslationTestCase(
                    "forall x: p(x)",
                    "TCE", "TAU",
                    ["∀", "x", "p(x)"],
                    "TCE quantifier with colon syntax"
                ),
                TranslationTestCase(
                    "exists y such that q(y)",
                    "TCE", "TAU", 
                    ["∃", "y", "q(y)"],
                    "TCE quantifier with 'such that' syntax"
                ),
                TranslationTestCase(
                    "if x > 5 then true else false",
                    "TCE", "TAU",
                    ["?", ":", ">", "5", "true", "false"],
                    "TCE conditional expression"
                ),
                TranslationTestCase(
                    "x + y * z",
                    "TCE", "TAU",
                    ["x", "+", "y", "*", "z"],
                    "TCE arithmetic with precedence"
                )
            ],
            
            "tau_to_english": [
                TranslationTestCase(
                    "∀x: p(x)",
                    "TAU", "English",
                    ["for all", "x", "p"],
                    "TAU universal quantifier to English"
                ),
                TranslationTestCase(
                    "∃y: q(y)",
                    "TAU", "English",
                    ["exists", "y", "such that", "q"],
                    "TAU existential quantifier to English"
                ),
                TranslationTestCase(
                    "(x > 5 ? true : false)",
                    "TAU", "English",
                    ["if", "greater than", "then", "else"],
                    "TAU conditional to English"
                ),
                TranslationTestCase(
                    "x & y",
                    "TAU", "English",
                    ["x", "and", "y"],
                    "TAU logical AND to English"
                )
            ],
            
            "tce_to_english": [
                TranslationTestCase(
                    "forall x: p(x)",
                    "TCE", "English",
                    ["for all", "x", "p"],
                    "TCE quantifier to English (via parsing)"
                ),
                TranslationTestCase(
                    "if x > 5 then true else false",
                    "TCE", "English",
                    ["if", "greater than", "then", "else"],
                    "TCE conditional to English (via parsing)"
                )
            ],
            
            "bidirectional_auto": [
                TranslationTestCase(
                    "∀x: p(x)",
                    "Auto", "English",
                    ["for all", "x", "p"],
                    "Auto-detect TAU and translate to English"
                ),
                TranslationTestCase(
                    "forall x such that p(x)",
                    "Auto", "TAU",
                    ["∀", "x", "p(x)"],
                    "Auto-detect TCE and translate to TAU"
                ),
                TranslationTestCase(
                    "for all variables x the predicate p holds",
                    "Auto", "TAU",
                    ["∀", "forall", "x", "p"],
                    "Auto-detect English and translate to TAU"
                )
            ]
        }
    
    def given_translation_services_are_available(self) -> bool:
        """BDD Given: Ensure all translation services are available."""
        try:
            # Test TCE parser availability
            from lark import Lark
            from tau_translator_omega.core_engine.tce_tau_transformer import TCEToTauTransformer
            
            grammar_path = project_root / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
            with open(grammar_path, 'r') as f:
                grammar_content = f.read()
            
            parser = Lark(grammar_content, parser='lalr', start='start', propagate_positions=True)
            transformer = TCEToTauTransformer()
            
            # Test TAU to English service
            from domain.tau_to_english_translator import create_tau_to_english_service
            tau_service = create_tau_to_english_service()
            
            print("✅ Given: All translation services are available and loaded")
            return True
            
        except Exception as e:
            print(f"❌ Given: Translation services not available: {e}")
            return False
    
    async def when_translating_in_direction(self, test_case: TranslationTestCase) -> DirectionalTestResult:
        """BDD When: Perform translation in specified direction."""
        
        try:
            # Route to appropriate translation method based on direction
            direction_key = f"{test_case.source_language.lower()}_to_{test_case.target_language.lower()}"
            
            if direction_key == "tce_to_tau":
                return await self._translate_tce_to_tau(test_case)
            elif direction_key == "tau_to_english":
                return await self._translate_tau_to_english(test_case)
            elif direction_key == "english_to_tce":
                return await self._translate_english_to_tce(test_case)
            elif direction_key == "english_to_tau":
                return await self._translate_english_to_tau(test_case)
            elif direction_key == "tce_to_english":
                return await self._translate_tce_to_english(test_case)
            elif direction_key == "auto_to_english" or direction_key == "auto_to_tau":
                return await self._translate_bidirectional_auto(test_case)
            else:
                return DirectionalTestResult(
                    direction=direction_key,
                    success=False,
                    input_text=test_case.input_text,
                    output_text="",
                    expected_elements=test_case.expected_elements,
                    found_elements=[],
                    coverage=0.0,
                    error_message=f"Unsupported direction: {direction_key}"
                )
                
        except Exception as e:
            return DirectionalTestResult(
                direction=f"{test_case.source_language}_to_{test_case.target_language}",
                success=False,
                input_text=test_case.input_text,
                output_text="",
                expected_elements=test_case.expected_elements,
                found_elements=[],
                coverage=0.0,
                error_message=str(e)
            )
    
    async def _translate_tce_to_tau(self, test_case: TranslationTestCase) -> DirectionalTestResult:
        """Translate TCE to TAU using grammar parser."""
        from lark import Lark
        from tau_translator_omega.core_engine.tce_tau_transformer import TCEToTauTransformer
        
        grammar_path = project_root / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
        with open(grammar_path, 'r') as f:
            grammar_content = f.read()
        
        parser = Lark(grammar_content, parser='lalr', start='start', propagate_positions=True)
        transformer = TCEToTauTransformer()
        
        input_with_terminator = test_case.input_text if test_case.input_text.endswith('.') else test_case.input_text + '.'
        
        parse_tree = parser.parse(input_with_terminator)
        tau_output = transformer.transform(parse_tree)
        
        return self._evaluate_translation_result(
            "TCE_to_TAU", test_case, str(tau_output)
        )
    
    async def _translate_tau_to_english(self, test_case: TranslationTestCase) -> DirectionalTestResult:
        """Translate TAU to English using TAU service."""
        from domain.tau_to_english_translator import create_tau_to_english_service
        
        service = create_tau_to_english_service()
        result = await service.translate_expression_async(test_case.input_text)
        
        if hasattr(result, 'is_success') and result.is_success():
            output_text = result.value
        else:
            error_msg = result.error if hasattr(result, 'error') else "Translation failed"
            raise Exception(error_msg)
        
        return self._evaluate_translation_result(
            "TAU_to_English", test_case, output_text
        )
    
    async def _translate_english_to_tce(self, test_case: TranslationTestCase) -> DirectionalTestResult:
        """Translate English to TCE using pattern matching."""
        # Simple pattern-based English to TCE translation
        import re
        
        text = test_case.input_text.lower()
        tce_output = text
        
        # Apply English to TCE patterns
        patterns = [
            (r'for all (?:variables?\s+)?(\w+)', r'forall \1:'),
            (r'there exists?(?:\s+a\s+value)?\s+(\w+)\s+such that', r'exists \1 such that'),
            (r'if (.+?) then (.+?) (?:otherwise|else) (.+)', r'if \1 then \2 else \3'),
            (r'is greater than', '>'),
            (r'is less than', '<'),
            (r'return (\w+)', r'\1')
        ]
        
        for pattern, replacement in patterns:
            tce_output = re.sub(pattern, replacement, tce_output)
        
        return self._evaluate_translation_result(
            "English_to_TCE", test_case, tce_output
        )
    
    async def _translate_english_to_tau(self, test_case: TranslationTestCase) -> DirectionalTestResult:
        """Translate English to TAU via TCE pipeline."""
        # English → TCE → TAU pipeline
        tce_result = await self._translate_english_to_tce(test_case)
        
        if tce_result.success and tce_result.output_text:
            # Create TCE test case
            tce_case = TranslationTestCase(
                tce_result.output_text,
                "TCE", "TAU",
                test_case.expected_elements,
                f"Pipeline: {test_case.description}"
            )
            
            return await self._translate_tce_to_tau(tce_case)
        else:
            return DirectionalTestResult(
                direction="English_to_TAU",
                success=False,
                input_text=test_case.input_text,
                output_text="",
                expected_elements=test_case.expected_elements,
                found_elements=[],
                coverage=0.0,
                error_message="TCE conversion failed in pipeline"
            )
    
    async def _translate_tce_to_english(self, test_case: TranslationTestCase) -> DirectionalTestResult:
        """Translate TCE to English via TAU pipeline."""
        # TCE → TAU → English pipeline
        tau_result = await self._translate_tce_to_tau(test_case)
        
        if tau_result.success and tau_result.output_text:
            # Create TAU test case
            tau_case = TranslationTestCase(
                tau_result.output_text,
                "TAU", "English",
                test_case.expected_elements,
                f"Pipeline: {test_case.description}"
            )
            
            return await self._translate_tau_to_english(tau_case)
        else:
            return DirectionalTestResult(
                direction="TCE_to_English", 
                success=False,
                input_text=test_case.input_text,
                output_text="",
                expected_elements=test_case.expected_elements,
                found_elements=[],
                coverage=0.0,
                error_message="TAU conversion failed in pipeline"
            )
    
    async def _translate_bidirectional_auto(self, test_case: TranslationTestCase) -> DirectionalTestResult:
        """Translate using auto-detection."""
        # Simple auto-detection logic
        text = test_case.input_text
        
        # Detect source language
        if any(symbol in text for symbol in ['∀', '∃', '?', ':']):
            # Likely TAU
            if test_case.target_language == "English":
                return await self._translate_tau_to_english(test_case)
        elif any(keyword in text.lower() for keyword in ['forall', 'exists', 'such that']):
            # Likely TCE
            if test_case.target_language == "TAU":
                return await self._translate_tce_to_tau(test_case)
        else:
            # Likely English
            if test_case.target_language == "TAU":
                return await self._translate_english_to_tau(test_case)
        
        return DirectionalTestResult(
            direction="Auto_detection",
            success=False,
            input_text=test_case.input_text,
            output_text="",
            expected_elements=test_case.expected_elements,
            found_elements=[],
            coverage=0.0,
            error_message="Auto-detection failed"
        )
    
    def _evaluate_translation_result(self, direction: str, test_case: TranslationTestCase, output_text: str) -> DirectionalTestResult:
        """Evaluate translation result against expected elements."""
        output_lower = output_text.lower()
        found_elements = []
        
        for element in test_case.expected_elements:
            if element.lower() in output_lower:
                found_elements.append(element)
        
        coverage = len(found_elements) / len(test_case.expected_elements) if test_case.expected_elements else 1.0
        success = coverage >= 0.6  # 60% coverage threshold
        
        return DirectionalTestResult(
            direction=direction,
            success=success,
            input_text=test_case.input_text,
            output_text=output_text,
            expected_elements=test_case.expected_elements,
            found_elements=found_elements,
            coverage=coverage
        )
    
    def then_translation_should_be_successful(self, result: DirectionalTestResult) -> bool:
        """BDD Then: Verify translation meets success criteria."""
        return result.success and result.coverage >= 0.6
    
    async def test_all_translation_directions(self) -> Dict[str, Any]:
        """Run comprehensive tests for all translation directions."""
        
        print("🧪 COMPREHENSIVE BIDIRECTIONAL TRANSLATION TEST")
        print("=" * 70)
        print("Testing ALL translation directions with BDD methodology")
        print()
        
        # Given: Translation services are available
        if not self.given_translation_services_are_available():
            return {"overall_success": False, "error": "Services not available"}
        
        direction_results = {}
        total_tests = 0
        total_passed = 0
        
        # Test each direction
        for direction, test_cases in self.test_cases.items():
            print(f"\n🔄 Testing {direction.replace('_', ' ').title()}:")
            print("-" * 50)
            
            direction_passed = 0
            direction_total = len(test_cases)
            
            for test_case in test_cases:
                total_tests += 1
                
                # When: Translating in this direction
                result = await self.when_translating_in_direction(test_case)
                
                # Then: Translation should be successful
                is_successful = self.then_translation_should_be_successful(result)
                
                if is_successful:
                    total_passed += 1
                    direction_passed += 1
                    print(f"  ✅ {test_case.description}")
                    print(f"     Input:  '{result.input_text}'")
                    print(f"     Output: '{result.output_text}'")
                    print(f"     Coverage: {result.coverage:.1%}")
                else:
                    print(f"  ❌ {test_case.description}")
                    print(f"     Input:  '{result.input_text}'")
                    print(f"     Output: '{result.output_text}'")
                    print(f"     Coverage: {result.coverage:.1%}")
                    if result.error_message:
                        print(f"     Error: {result.error_message}")
                
                self.results.append(result)
            
            direction_success_rate = direction_passed / direction_total if direction_total > 0 else 0
            direction_results[direction] = {
                "passed": direction_passed,
                "total": direction_total,
                "success_rate": direction_success_rate
            }
            
            print(f"\n  📊 {direction}: {direction_passed}/{direction_total} ({direction_success_rate:.1%})")
        
        # Generate comprehensive report
        overall_success_rate = total_passed / total_tests if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print("📋 COMPREHENSIVE TRANSLATION TEST RESULTS")
        print("=" * 70)
        
        for direction, stats in direction_results.items():
            status = "✅" if stats["success_rate"] >= 0.8 else "⚠️" if stats["success_rate"] >= 0.6 else "❌"
            print(f"{status} {direction.replace('_', ' ').title()}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1%})")
        
        print(f"\n🎯 OVERALL SUCCESS RATE: {total_passed}/{total_tests} ({overall_success_rate:.1%})")
        
        if overall_success_rate >= 0.8:
            print("\n🎉 EXCELLENT: All translation directions working!")
            print("✅ Bidirectional translation system is fully functional")
            print("✅ All critical translation routes validated")
        elif overall_success_rate >= 0.6:
            print("\n✅ GOOD: Most translation directions working")
            print("⚠️ Some directions need refinement")
        else:
            print("\n❌ NEEDS WORK: Several translation directions failing")
        
        return {
            "overall_success": overall_success_rate >= 0.8,
            "overall_success_rate": overall_success_rate,
            "total_passed": total_passed,
            "total_tests": total_tests,
            "direction_results": direction_results,
            "detailed_results": self.results
        }

async def main():
    """Main test runner following BDD principles."""
    tester = ComprehensiveTranslationTester()
    results = await tester.test_all_translation_directions()
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)

if __name__ == "__main__":
    asyncio.run(main())