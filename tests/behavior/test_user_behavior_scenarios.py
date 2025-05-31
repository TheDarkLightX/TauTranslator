#!/usr/bin/env python3
"""
User Behavior Testing for TauTranslator
=======================================

Comprehensive behavior-driven tests that validate the system meets user expectations.
Tests actual user workflows and verifies the system behaves as users expect.

Author: DarklightX (Dana Edwards)
"""

import pytest
import time
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.fixtures.security_fixtures import SecureTestFixtures
from src.tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator


class UserExpectation:
    """Represents a user's expectation for system behavior."""
    
    def __init__(self, scenario: str, input_text: str, expected_output: str, 
                 tolerance: str = "exact", context: Optional[Dict] = None):
        self.scenario = scenario
        self.input_text = input_text
        self.expected_output = expected_output
        self.tolerance = tolerance  # "exact", "pattern", "semantic"
        self.context = context or {}


class BehaviorTestFramework:
    """Framework for testing user behavior scenarios."""
    
    def __init__(self):
        self.translator = None
        self.test_results = []
        
    def setup_translator(self):
        """Setup translation engine for testing."""
        try:
            self.translator = LMQLBidirectionalTranslator()
            return True
        except Exception:
            try:
                self.translator = TCETauTranslator()
                return True
            except Exception:
                return False
    
    def validate_expectation(self, expectation: UserExpectation) -> Dict[str, Any]:
        """Validate a single user expectation."""
        start_time = time.time()
        
        try:
            # Attempt translation
            if hasattr(self.translator, 'translate_tce_to_tau'):
                result = self.translator.translate_tce_to_tau(expectation.input_text)
            elif hasattr(self.translator, 'translate'):
                result = self.translator.translate(expectation.input_text)
            else:
                result = "Translation method not available"
            
            # Validate result against expectation
            validation_result = self._validate_result(result, expectation)
            
            test_result = {
                "scenario": expectation.scenario,
                "input": expectation.input_text,
                "expected": expectation.expected_output,
                "actual": result,
                "passed": validation_result["passed"],
                "confidence": validation_result["confidence"],
                "execution_time": time.time() - start_time,
                "errors": validation_result.get("errors", [])
            }
            
        except Exception as e:
            test_result = {
                "scenario": expectation.scenario,
                "input": expectation.input_text,
                "expected": expectation.expected_output,
                "actual": f"ERROR: {str(e)}",
                "passed": False,
                "confidence": 0.0,
                "execution_time": time.time() - start_time,
                "errors": [str(e)]
            }
        
        self.test_results.append(test_result)
        return test_result
    
    def _validate_result(self, actual: Any, expectation: UserExpectation) -> Dict[str, Any]:
        """Validate actual result against user expectation."""
        if expectation.tolerance == "exact":
            passed = str(actual).strip() == expectation.expected_output.strip()
            confidence = 1.0 if passed else 0.0
            
        elif expectation.tolerance == "pattern":
            import re
            pattern = expectation.expected_output
            try:
                passed = bool(re.search(pattern, str(actual), re.IGNORECASE))
                confidence = 0.8 if passed else 0.0
            except re.error:
                passed = False
                confidence = 0.0
                
        elif expectation.tolerance == "semantic":
            # Semantic similarity check (simplified)
            actual_normalized = self._normalize_expression(str(actual))
            expected_normalized = self._normalize_expression(expectation.expected_output)
            passed = actual_normalized == expected_normalized
            confidence = 0.7 if passed else 0.0
            
        else:
            passed = False
            confidence = 0.0
        
        return {
            "passed": passed,
            "confidence": confidence,
            "errors": [] if passed else [f"Expected: {expectation.expected_output}, Got: {actual}"]
        }
    
    def _normalize_expression(self, expr: str) -> str:
        """Normalize expression for semantic comparison."""
        # Remove extra whitespace, normalize operators
        normalized = expr.strip().lower()
        normalized = normalized.replace("&&", "&").replace("||", "|")
        normalized = normalized.replace("and", "&").replace("or", "|")
        return normalized
    
    def generate_behavior_report(self) -> Dict[str, Any]:
        """Generate comprehensive behavior test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        average_confidence = sum(result["confidence"] for result in self.test_results) / total_tests if total_tests > 0 else 0
        average_time = sum(result["execution_time"] for result in self.test_results) / total_tests if total_tests > 0 else 0
        
        return {
            "summary": {
                "total_scenarios": total_tests,
                "passed_scenarios": passed_tests,
                "failed_scenarios": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "average_confidence": average_confidence,
                "average_execution_time": average_time
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if not r["passed"]]
        if failed_tests:
            recommendations.append(f"Address {len(failed_tests)} failing behavior scenarios")
        
        slow_tests = [r for r in self.test_results if r["execution_time"] > 1.0]
        if slow_tests:
            recommendations.append(f"Optimize {len(slow_tests)} slow translation scenarios")
        
        low_confidence = [r for r in self.test_results if r["confidence"] < 0.5]
        if low_confidence:
            recommendations.append(f"Improve accuracy for {len(low_confidence)} low-confidence scenarios")
        
        return recommendations


# User behavior scenarios based on expected usage patterns
USER_BEHAVIOR_SCENARIOS = [
    # Basic temporal logic expectations
    UserExpectation(
        scenario="User expects 'always' statements to translate to temporal logic",
        input_text="Always x is true",
        expected_output="always (x)",
        tolerance="semantic"
    ),
    
    UserExpectation(
        scenario="User expects 'sometimes' statements to translate correctly",
        input_text="Sometimes y equals 5",
        expected_output="sometimes (y = 5)",
        tolerance="semantic"
    ),
    
    # Boolean logic expectations
    UserExpectation(
        scenario="User expects AND operations to work intuitively",
        input_text="x AND y",
        expected_output="x & y",
        tolerance="pattern"
    ),
    
    UserExpectation(
        scenario="User expects OR operations to work intuitively",
        input_text="x OR y",
        expected_output="x | y",
        tolerance="pattern"
    ),
    
    UserExpectation(
        scenario="User expects NOT operations to work intuitively",
        input_text="NOT x",
        expected_output="x'",
        tolerance="pattern"
    ),
    
    # Complex logical statements
    UserExpectation(
        scenario="User expects complex logical expressions to be preserved",
        input_text="Always (x AND y) OR sometimes z",
        expected_output=r"always.*x.*&.*y.*\|.*sometimes.*z",
        tolerance="pattern"
    ),
    
    # Natural language variations
    UserExpectation(
        scenario="User expects natural variations to be understood",
        input_text="x is always true",
        expected_output="always.*x",
        tolerance="pattern"
    ),
    
    # Error handling expectations
    UserExpectation(
        scenario="User expects meaningful feedback for invalid input",
        input_text="This is not valid Tau syntax!!!",
        expected_output="error|invalid|cannot|unable",
        tolerance="pattern"
    ),
    
    # Performance expectations
    UserExpectation(
        scenario="User expects fast response for simple translations",
        input_text="x = 5",
        expected_output="x = 5",
        tolerance="semantic"
    ),
]


class TestUserBehaviorScenarios:
    """Pytest class for user behavior testing."""
    
    @pytest.fixture(autouse=True)
    def setup_framework(self):
        """Setup behavior test framework."""
        self.framework = BehaviorTestFramework()
        self.translator_available = self.framework.setup_translator()
    
    @pytest.mark.behavior
    @pytest.mark.parametrize("expectation", USER_BEHAVIOR_SCENARIOS)
    def test_user_expectation_scenario(self, expectation):
        """Test individual user expectation scenario."""
        if not self.translator_available:
            pytest.skip("Translation engine not available")
        
        result = self.framework.validate_expectation(expectation)
        
        # Assert the user expectation is met
        assert result["passed"], f"""
        User expectation failed:
        Scenario: {result['scenario']}
        Input: {result['input']}
        Expected: {result['expected']}
        Actual: {result['actual']}
        Confidence: {result['confidence']}
        Errors: {result['errors']}
        """
    
    @pytest.mark.behavior
    @pytest.mark.integration
    def test_complete_user_workflow(self):
        """Test complete user workflow from start to finish."""
        if not self.translator_available:
            pytest.skip("Translation engine not available")
        
        # Simulate user workflow: Load -> Translate -> Verify
        workflow_steps = [
            ("Load simple expression", "x = 5", "x = 5"),
            ("Translate temporal logic", "Always x > 0", "always.*x.*>.*0"),
            ("Handle boolean logic", "x AND NOT y", "x.*&.*y'"),
        ]
        
        workflow_results = []
        for step_name, input_text, expected_pattern in workflow_steps:
            expectation = UserExpectation(step_name, input_text, expected_pattern, "pattern")
            result = self.framework.validate_expectation(expectation)
            workflow_results.append(result)
        
        # Verify entire workflow succeeded
        success_rate = sum(1 for r in workflow_results if r["passed"]) / len(workflow_results)
        assert success_rate >= 0.7, f"User workflow success rate {success_rate:.1%} below 70% threshold"
    
    @pytest.mark.behavior
    @pytest.mark.performance
    def test_user_performance_expectations(self):
        """Test that system meets user performance expectations."""
        if not self.translator_available:
            pytest.skip("Translation engine not available")
        
        # Test performance expectations
        performance_scenarios = [
            UserExpectation("Fast simple translation", "x = 1", "x = 1", "semantic"),
            UserExpectation("Reasonable complex translation", "Always (x AND y)", "always.*x.*&.*y", "pattern"),
        ]
        
        for scenario in performance_scenarios:
            result = self.framework.validate_expectation(scenario)
            
            # Users expect translations to complete within reasonable time
            assert result["execution_time"] < 5.0, f"Translation too slow: {result['execution_time']:.2f}s"
    
    @pytest.mark.behavior
    def test_generate_behavior_report(self):
        """Generate comprehensive behavior test report."""
        if not self.translator_available:
            pytest.skip("Translation engine not available")
        
        # Run a subset of scenarios
        test_scenarios = USER_BEHAVIOR_SCENARIOS[:5]
        for scenario in test_scenarios:
            self.framework.validate_expectation(scenario)
        
        # Generate report
        report = self.framework.generate_behavior_report()
        
        # Verify report structure
        assert "summary" in report
        assert "detailed_results" in report
        assert "recommendations" in report
        
        # Verify report contains meaningful data
        assert report["summary"]["total_scenarios"] > 0
        assert len(report["detailed_results"]) > 0
        
        # Print report for analysis
        print(f"\n{'='*60}")
        print("USER BEHAVIOR TEST REPORT")
        print(f"{'='*60}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Average Confidence: {report['summary']['average_confidence']:.2f}")
        print(f"Average Execution Time: {report['summary']['average_execution_time']:.3f}s")
        print(f"Recommendations: {len(report['recommendations'])}")
        for rec in report['recommendations']:
            print(f"  - {rec}")


if __name__ == "__main__":
    # Run behavior tests directly
    framework = BehaviorTestFramework()
    
    if framework.setup_translator():
        print("🧪 Running User Behavior Tests...")
        
        for scenario in USER_BEHAVIOR_SCENARIOS:
            result = framework.validate_expectation(scenario)
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} {scenario.scenario}")
            if not result["passed"]:
                print(f"    Expected: {scenario.expected_output}")
                print(f"    Actual: {result['actual']}")
        
        # Generate final report
        report = framework.generate_behavior_report()
        print(f"\n📊 Final Results: {report['summary']['success_rate']:.1f}% success rate")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
    else:
        print("❌ Translation engine not available - cannot run behavior tests")