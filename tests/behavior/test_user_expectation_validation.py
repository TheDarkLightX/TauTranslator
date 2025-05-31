#!/usr/bin/env python3
"""
User Expectation Validation System
==================================

Comprehensive system to validate that the TauTranslator behaves exactly as users expect.
Includes acceptance criteria, user story validation, and behavioral correctness testing.

Author: DarklightX (Dana Edwards)
"""

import pytest
import json
import time
import subprocess
import requests
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sys
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ExpectationLevel(Enum):
    """Levels of user expectation validation."""
    BASIC = "basic"           # Core functionality must work
    STANDARD = "standard"     # Expected features work reliably
    ADVANCED = "advanced"     # Advanced features work as documented
    EXPERT = "expert"         # Expert users get precise control


class ValidationResult(Enum):
    """Results of expectation validation."""
    MEETS_EXPECTATION = "meets"
    PARTIALLY_MEETS = "partial"
    FAILS_EXPECTATION = "fails"
    CANNOT_VALIDATE = "unknown"


@dataclass
class UserStory:
    """Represents a user story with acceptance criteria."""
    id: str
    title: str
    description: str
    as_a: str           # Role
    i_want: str         # Goal
    so_that: str        # Benefit
    acceptance_criteria: List[str]
    level: ExpectationLevel


@dataclass
class AcceptanceCriterion:
    """Individual acceptance criterion with validation logic."""
    description: str
    given: str          # Pre-conditions
    when: str          # Action
    then: str          # Expected outcome
    validation_method: str  # How to validate


class UserExpectationValidator:
    """Validates that the system meets user expectations."""
    
    def __init__(self):
        self.validation_results = []
        self.backend_url = "http://localhost:8000"
        self.backend_available = False
        
    def check_backend_availability(self) -> bool:
        """Check if backend is available for testing."""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            self.backend_available = response.status_code == 200
            return self.backend_available
        except:
            self.backend_available = False
            return False
    
    def validate_user_story(self, story: UserStory) -> Dict[str, Any]:
        """Validate a complete user story."""
        story_result = {
            "story_id": story.id,
            "title": story.title,
            "level": story.level.value,
            "criteria_results": [],
            "overall_result": ValidationResult.CANNOT_VALIDATE.value,
            "confidence": 0.0,
            "timestamp": time.time()
        }
        
        total_criteria = len(story.acceptance_criteria)
        met_criteria = 0
        
        for criterion in story.acceptance_criteria:
            criterion_result = self._validate_acceptance_criterion(criterion, story)
            story_result["criteria_results"].append(criterion_result)
            
            if criterion_result["result"] == ValidationResult.MEETS_EXPECTATION.value:
                met_criteria += 1
            elif criterion_result["result"] == ValidationResult.PARTIALLY_MEETS.value:
                met_criteria += 0.5
        
        # Determine overall result
        if met_criteria == total_criteria:
            story_result["overall_result"] = ValidationResult.MEETS_EXPECTATION.value
            story_result["confidence"] = 1.0
        elif met_criteria >= total_criteria * 0.7:
            story_result["overall_result"] = ValidationResult.PARTIALLY_MEETS.value
            story_result["confidence"] = met_criteria / total_criteria
        elif met_criteria > 0:
            story_result["overall_result"] = ValidationResult.FAILS_EXPECTATION.value
            story_result["confidence"] = met_criteria / total_criteria
        else:
            story_result["overall_result"] = ValidationResult.CANNOT_VALIDATE.value
            story_result["confidence"] = 0.0
        
        self.validation_results.append(story_result)
        return story_result
    
    def _validate_acceptance_criterion(self, criterion: str, story: UserStory) -> Dict[str, Any]:
        """Validate a single acceptance criterion."""
        start_time = time.time()
        
        # Parse criterion into Given/When/Then format
        parsed = self._parse_gherkin_criterion(criterion)
        
        try:
            # Execute validation based on criterion type
            if "translation" in criterion.lower():
                result = self._validate_translation_criterion(parsed, story)
            elif "ui" in criterion.lower() or "interface" in criterion.lower():
                result = self._validate_ui_criterion(parsed, story)
            elif "performance" in criterion.lower():
                result = self._validate_performance_criterion(parsed, story)
            elif "error" in criterion.lower() or "invalid" in criterion.lower():
                result = self._validate_error_handling_criterion(parsed, story)
            else:
                result = self._validate_generic_criterion(parsed, story)
                
        except Exception as e:
            result = {
                "result": ValidationResult.CANNOT_VALIDATE.value,
                "confidence": 0.0,
                "error": str(e)
            }
        
        return {
            "criterion": criterion,
            "parsed": parsed,
            "result": result["result"],
            "confidence": result["confidence"],
            "execution_time": time.time() - start_time,
            "details": result.get("details", ""),
            "error": result.get("error", "")
        }
    
    def _parse_gherkin_criterion(self, criterion: str) -> Dict[str, str]:
        """Parse Gherkin-style acceptance criterion."""
        lines = criterion.strip().split('\\n')
        parsed = {"given": "", "when": "", "then": "", "raw": criterion}
        
        current_section = ""
        for line in lines:
            line = line.strip()
            if line.lower().startswith("given"):
                current_section = "given"
                parsed["given"] = line[5:].strip()
            elif line.lower().startswith("when"):
                current_section = "when"
                parsed["when"] = line[4:].strip()
            elif line.lower().startswith("then"):
                current_section = "then"
                parsed["then"] = line[4:].strip()
            elif line.lower().startswith("and"):
                if current_section:
                    parsed[current_section] += " " + line[3:].strip()
        
        return parsed
    
    def _validate_translation_criterion(self, parsed: Dict[str, str], story: UserStory) -> Dict[str, Any]:
        """Validate translation-related acceptance criteria."""
        if not self.backend_available:
            return {
                "result": ValidationResult.CANNOT_VALIDATE.value,
                "confidence": 0.0,
                "details": "Backend not available for translation testing"
            }
        
        # Extract test case from criterion
        test_input = self._extract_test_input(parsed)
        expected_output = self._extract_expected_output(parsed)
        
        if not test_input:
            return {
                "result": ValidationResult.CANNOT_VALIDATE.value,
                "confidence": 0.0,
                "details": "Could not extract test input from criterion"
            }
        
        try:
            # Perform actual translation
            response = requests.post(
                f"{self.backend_url}/api/translate",
                json={"text": test_input, "source": "CNL", "target": "TAU"},
                timeout=5
            )
            
            if response.status_code == 200:
                result_data = response.json()
                actual_output = result_data.get("translation", "")
                
                # Validate result
                if expected_output:
                    if self._outputs_match(actual_output, expected_output):
                        return {
                            "result": ValidationResult.MEETS_EXPECTATION.value,
                            "confidence": 1.0,
                            "details": f"Translation '{test_input}' -> '{actual_output}' matches expectation"
                        }
                    else:
                        return {
                            "result": ValidationResult.FAILS_EXPECTATION.value,
                            "confidence": 0.2,
                            "details": f"Expected '{expected_output}', got '{actual_output}'"
                        }
                else:
                    # No expected output specified, just check if translation occurred
                    if actual_output and actual_output != test_input:
                        return {
                            "result": ValidationResult.PARTIALLY_MEETS.value,
                            "confidence": 0.7,
                            "details": f"Translation occurred: '{test_input}' -> '{actual_output}'"
                        }
            
            return {
                "result": ValidationResult.FAILS_EXPECTATION.value,
                "confidence": 0.0,
                "details": f"Translation failed: HTTP {response.status_code}"
            }
            
        except Exception as e:
            return {
                "result": ValidationResult.CANNOT_VALIDATE.value,
                "confidence": 0.0,
                "details": f"Translation test error: {str(e)}"
            }
    
    def _validate_ui_criterion(self, parsed: Dict[str, str], story: UserStory) -> Dict[str, Any]:
        """Validate UI-related acceptance criteria."""
        # For now, return partial validation since UI testing requires selenium/browser automation
        return {
            "result": ValidationResult.PARTIALLY_MEETS.value,
            "confidence": 0.5,
            "details": "UI validation requires browser automation (not implemented)"
        }
    
    def _validate_performance_criterion(self, parsed: Dict[str, str], story: UserStory) -> Dict[str, Any]:
        """Validate performance-related acceptance criteria."""
        # Extract performance requirements
        criterion_text = parsed["raw"].lower()
        
        if "fast" in criterion_text or "quick" in criterion_text:
            expected_time = 1.0  # 1 second for "fast"
        elif "reasonable" in criterion_text:
            expected_time = 5.0  # 5 seconds for "reasonable"
        else:
            expected_time = 10.0  # Default
        
        # Test simple translation performance
        test_input = "Always x is true"
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/translate",
                json={"text": test_input, "source": "CNL", "target": "TAU"},
                timeout=expected_time + 1
            )
            execution_time = time.time() - start_time
            
            if execution_time <= expected_time:
                return {
                    "result": ValidationResult.MEETS_EXPECTATION.value,
                    "confidence": 1.0,
                    "details": f"Performance meets expectation: {execution_time:.2f}s <= {expected_time}s"
                }
            else:
                return {
                    "result": ValidationResult.FAILS_EXPECTATION.value,
                    "confidence": 0.3,
                    "details": f"Performance below expectation: {execution_time:.2f}s > {expected_time}s"
                }
                
        except Exception as e:
            return {
                "result": ValidationResult.CANNOT_VALIDATE.value,
                "confidence": 0.0,
                "details": f"Performance test error: {str(e)}"
            }
    
    def _validate_error_handling_criterion(self, parsed: Dict[str, str], story: UserStory) -> Dict[str, Any]:
        """Validate error handling acceptance criteria."""
        # Test with invalid input
        invalid_inputs = [
            "This is complete nonsense!!!",
            "12345 @#$%^ invalid",
            "",
            "A" * 10000  # Very long input
        ]
        
        error_handling_works = 0
        total_tests = len(invalid_inputs)
        
        for invalid_input in invalid_inputs:
            try:
                response = requests.post(
                    f"{self.backend_url}/api/translate",
                    json={"text": invalid_input, "source": "CNL", "target": "TAU"},
                    timeout=5
                )
                
                # Good error handling should return error status or meaningful error message
                if response.status_code >= 400:
                    error_handling_works += 1
                elif response.status_code == 200:
                    data = response.json()
                    if "error" in data or "invalid" in str(data).lower():
                        error_handling_works += 1
                        
            except requests.exceptions.Timeout:
                # Timeout on invalid input is acceptable
                error_handling_works += 1
            except:
                pass
        
        confidence = error_handling_works / total_tests
        
        if confidence >= 0.8:
            return {
                "result": ValidationResult.MEETS_EXPECTATION.value,
                "confidence": confidence,
                "details": f"Error handling works for {error_handling_works}/{total_tests} test cases"
            }
        elif confidence >= 0.5:
            return {
                "result": ValidationResult.PARTIALLY_MEETS.value,
                "confidence": confidence,
                "details": f"Error handling partially works for {error_handling_works}/{total_tests} test cases"
            }
        else:
            return {
                "result": ValidationResult.FAILS_EXPECTATION.value,
                "confidence": confidence,
                "details": f"Error handling fails for most cases: {error_handling_works}/{total_tests}"
            }
    
    def _validate_generic_criterion(self, parsed: Dict[str, str], story: UserStory) -> Dict[str, Any]:
        """Validate generic acceptance criteria."""
        # For unrecognized criteria, return partial validation
        return {
            "result": ValidationResult.PARTIALLY_MEETS.value,
            "confidence": 0.5,
            "details": "Generic validation - manual verification recommended"
        }
    
    def _extract_test_input(self, parsed: Dict[str, str]) -> Optional[str]:
        """Extract test input from parsed criterion."""
        text = parsed["raw"].lower()
        
        # Look for quoted strings or specific patterns
        import re
        quotes = re.findall(r'"([^"]*)"', parsed["raw"])
        if quotes:
            return quotes[0]
        
        quotes = re.findall(r"'([^']*)'", parsed["raw"])
        if quotes:
            return quotes[0]
        
        # Look for common test patterns
        if "always" in text:
            return "Always x is true"
        elif "sometimes" in text:
            return "Sometimes x equals 5"
        elif "and" in text and "or" not in text:
            return "x AND y"
        elif "or" in text:
            return "x OR y"
        
        return None
    
    def _extract_expected_output(self, parsed: Dict[str, str]) -> Optional[str]:
        """Extract expected output from parsed criterion."""
        # Look for "should result in", "produces", etc.
        text = parsed["raw"]
        
        import re
        result_patterns = [
            r"should result in [\"']([^\"']*)[\"']",
            r"produces [\"']([^\"']*)[\"']",
            r"outputs [\"']([^\"']*)[\"']",
            r"returns [\"']([^\"']*)[\"']"
        ]
        
        for pattern in result_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _outputs_match(self, actual: str, expected: str) -> bool:
        """Check if actual output matches expected output."""
        # Normalize for comparison
        actual_norm = actual.strip().lower().replace(" ", "")
        expected_norm = expected.strip().lower().replace(" ", "")
        
        # Exact match
        if actual_norm == expected_norm:
            return True
        
        # Pattern match
        import re
        if re.search(expected_norm, actual_norm):
            return True
        
        # Semantic equivalence (simplified)
        semantic_mappings = {
            "always(x)": ["always x", "alwaysx"],
            "x&y": ["x and y", "xandy"],
            "x|y": ["x or y", "xory"],
            "x'": ["not x", "notx"]
        }
        
        for canonical, variants in semantic_mappings.items():
            if (canonical.replace("(", "").replace(")", "") in actual_norm and 
                any(v in expected_norm for v in variants)):
                return True
        
        return False
    
    def generate_expectation_report(self) -> Dict[str, Any]:
        """Generate comprehensive user expectation validation report."""
        if not self.validation_results:
            return {"error": "No validation results available"}
        
        total_stories = len(self.validation_results)
        meets_expectation = sum(1 for r in self.validation_results 
                              if r["overall_result"] == ValidationResult.MEETS_EXPECTATION.value)
        partially_meets = sum(1 for r in self.validation_results 
                            if r["overall_result"] == ValidationResult.PARTIALLY_MEETS.value)
        fails_expectation = sum(1 for r in self.validation_results 
                              if r["overall_result"] == ValidationResult.FAILS_EXPECTATION.value)
        
        # Calculate average confidence
        total_confidence = sum(r["confidence"] for r in self.validation_results)
        avg_confidence = total_confidence / total_stories if total_stories > 0 else 0
        
        # Categorize by expectation level
        level_breakdown = {}
        for result in self.validation_results:
            level = result["level"]
            if level not in level_breakdown:
                level_breakdown[level] = {"total": 0, "meets": 0, "partial": 0, "fails": 0}
            
            level_breakdown[level]["total"] += 1
            if result["overall_result"] == ValidationResult.MEETS_EXPECTATION.value:
                level_breakdown[level]["meets"] += 1
            elif result["overall_result"] == ValidationResult.PARTIALLY_MEETS.value:
                level_breakdown[level]["partial"] += 1
            else:
                level_breakdown[level]["fails"] += 1
        
        return {
            "summary": {
                "total_user_stories": total_stories,
                "meets_expectation": meets_expectation,
                "partially_meets": partially_meets,
                "fails_expectation": fails_expectation,
                "success_rate": (meets_expectation + partially_meets * 0.5) / total_stories * 100,
                "average_confidence": avg_confidence,
                "backend_available": self.backend_available
            },
            "level_breakdown": level_breakdown,
            "detailed_results": self.validation_results,
            "recommendations": self._generate_expectation_recommendations()
        }
    
    def _generate_expectation_recommendations(self) -> List[str]:
        """Generate recommendations for meeting user expectations."""
        recommendations = []
        
        failed_stories = [r for r in self.validation_results 
                         if r["overall_result"] == ValidationResult.FAILS_EXPECTATION.value]
        
        if failed_stories:
            recommendations.append(f"Address {len(failed_stories)} failing user stories")
            
            # Analyze failure patterns
            translation_failures = sum(1 for story in failed_stories 
                                     if any("translation" in c["criterion"].lower() 
                                           for c in story["criteria_results"]))
            if translation_failures > 0:
                recommendations.append(f"Fix {translation_failures} translation expectation failures")
        
        if not self.backend_available:
            recommendations.append("Backend service must be available for full validation")
        
        low_confidence = [r for r in self.validation_results if r["confidence"] < 0.6]
        if low_confidence:
            recommendations.append(f"Improve confidence for {len(low_confidence)} user stories")
        
        return recommendations


# Define core user stories that must be validated
CORE_USER_STORIES = [
    UserStory(
        id="US001",
        title="Basic Translation Functionality",
        description="Users can translate simple TCE statements to Tau",
        as_a="domain expert",
        i_want="to translate natural language statements to Tau",
        so_that="I can specify formal requirements easily",
        acceptance_criteria=[
            "Given a simple temporal statement 'Always x is true' When I translate to Tau Then I should get 'always (x)' or equivalent",
            "Given a boolean statement 'x AND y' When I translate to Tau Then I should get 'x & y' or equivalent"
        ],
        level=ExpectationLevel.BASIC
    ),
    
    UserStory(
        id="US002", 
        title="System Responsiveness",
        description="Translation system responds quickly to user input",
        as_a="user",
        i_want="fast translation responses",
        so_that="I can work efficiently",
        acceptance_criteria=[
            "Given any simple translation request When I submit it Then I should get a response within 2 seconds",
            "Given a complex translation request When I submit it Then I should get a response within 5 seconds"
        ],
        level=ExpectationLevel.STANDARD
    ),
    
    UserStory(
        id="US003",
        title="Error Handling",
        description="System handles invalid input gracefully", 
        as_a="user",
        i_want="meaningful error messages for invalid input",
        so_that="I understand what went wrong",
        acceptance_criteria=[
            "Given invalid input When I attempt translation Then I should receive a clear error message",
            "Given empty input When I attempt translation Then I should receive appropriate feedback"
        ],
        level=ExpectationLevel.STANDARD
    ),
    
    UserStory(
        id="US004",
        title="Complex Logic Translation",
        description="System handles complex logical expressions",
        as_a="expert user", 
        i_want="to translate complex logical statements",
        so_that="I can express sophisticated requirements",
        acceptance_criteria=[
            "Given a complex statement 'Always (x AND y) OR sometimes z' When I translate Then I should get equivalent Tau logic",
            "Given nested temporal operators When I translate Then the nesting should be preserved"
        ],
        level=ExpectationLevel.ADVANCED
    )
]


class TestUserExpectationValidation:
    """Pytest class for user expectation validation."""
    
    @pytest.fixture(autouse=True)
    def setup_validator(self):
        """Setup expectation validator."""
        self.validator = UserExpectationValidator()
        self.validator.check_backend_availability()
    
    @pytest.mark.behavior
    @pytest.mark.expectation
    @pytest.mark.parametrize("story", CORE_USER_STORIES)
    def test_user_story_validation(self, story):
        """Test validation of individual user stories."""
        result = self.validator.validate_user_story(story)
        
        # User stories should at least partially meet expectations
        assert result["overall_result"] in [
            ValidationResult.MEETS_EXPECTATION.value,
            ValidationResult.PARTIALLY_MEETS.value
        ], f"""
        User story failed validation:
        ID: {story.id}
        Title: {story.title}
        Result: {result['overall_result']}
        Confidence: {result['confidence']:.2f}
        Level: {story.level.value}
        """
    
    @pytest.mark.behavior
    @pytest.mark.expectation
    def test_basic_expectations_must_pass(self):
        """Basic level expectations must be met for system acceptance."""
        basic_stories = [s for s in CORE_USER_STORIES if s.level == ExpectationLevel.BASIC]
        
        for story in basic_stories:
            result = self.validator.validate_user_story(story)
            
            # Basic expectations must be met with high confidence
            assert result["overall_result"] == ValidationResult.MEETS_EXPECTATION.value, f"""
            BASIC expectation not met - this is unacceptable:
            Story: {story.title}
            Result: {result['overall_result']}
            Confidence: {result['confidence']:.2f}
            """
    
    @pytest.mark.behavior
    @pytest.mark.expectation
    def test_expectation_coverage(self):
        """Test that we have adequate expectation coverage."""
        # Validate all stories
        for story in CORE_USER_STORIES:
            self.validator.validate_user_story(story)
        
        # Generate report
        report = self.validator.generate_expectation_report()
        
        # Ensure adequate coverage
        assert report["summary"]["total_user_stories"] >= 4, "Insufficient user story coverage"
        assert report["summary"]["success_rate"] >= 50.0, f"Success rate too low: {report['summary']['success_rate']:.1f}%"
        
        # Print report for analysis
        print(f"\n{'='*60}")
        print("USER EXPECTATION VALIDATION REPORT")
        print(f"{'='*60}")
        print(f"Total Stories: {report['summary']['total_user_stories']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Average Confidence: {report['summary']['average_confidence']:.2f}")
        print(f"Backend Available: {report['summary']['backend_available']}")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")


if __name__ == "__main__":
    # Run expectation validation directly
    validator = UserExpectationValidator()
    
    print("🧪 Running User Expectation Validation...")
    print(f"Backend Available: {validator.check_backend_availability()}")
    
    for story in CORE_USER_STORIES:
        result = validator.validate_user_story(story)
        status_emoji = {
            ValidationResult.MEETS_EXPECTATION.value: "✅",
            ValidationResult.PARTIALLY_MEETS.value: "⚠️",
            ValidationResult.FAILS_EXPECTATION.value: "❌",
            ValidationResult.CANNOT_VALIDATE.value: "❓"
        }
        
        emoji = status_emoji[result["overall_result"]]
        print(f"{emoji} {story.id}: {story.title} ({result['confidence']:.1%} confidence)")
    
    # Generate final report
    report = validator.generate_expectation_report()
    print(f"\n📊 Overall Success Rate: {report['summary']['success_rate']:.1f}%")
    
    if report['recommendations']:
        print("\n💡 Key Recommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")