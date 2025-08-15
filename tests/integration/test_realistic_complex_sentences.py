#!/usr/bin/env python3
"""
Realistic Complex Sentence Test Suite
Tests complex but realistic sentences that push our translation limits.

Focus areas:
- Business logic and requirements
- Scientific and mathematical constraints  
- Legal and regulatory specifications
- Software system specifications
- IoT and embedded systems rules

Copyright: DarkLightX / Dana Edwards
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project paths
project_root = Path(__file__).parent
backend_path = project_root / "backend/unified"
sys.path.insert(0, str(backend_path))

@dataclass
class RealisticTestCase:
    """Realistic complex sentence test case."""
    domain: str
    description: str
    english: str
    expected_elements: List[str]
    complexity_features: List[str]
    real_world_scenario: str

class RealisticComplexityTester:
    """Test realistic complex sentences across various domains."""
    
    def __init__(self):
        self.test_cases = self._create_realistic_test_cases()
        self.results = []
        
    def _create_realistic_test_cases(self) -> List[RealisticTestCase]:
        """Create realistic test cases from various domains."""
        return [
            # Business Logic
            RealisticTestCase(
                domain="Business Rules",
                description="Customer discount eligibility",
                english="Every customer who has made purchases totaling more than $1000 in the last 12 months and has no outstanding payments receives a 15% discount on orders over $100",
                expected_elements=["customer", "purchases", "> 1000", "12 months", "!outstanding", "discount", "15%", "orders > 100"],
                complexity_features=["temporal_window", "aggregation", "negation", "percentage", "multiple_conditions"],
                real_world_scenario="E-commerce loyalty program implementation"
            ),
            
            RealisticTestCase(
                domain="Business Rules",
                description="Employee bonus calculation",
                english="All employees who achieve their sales targets for three consecutive quarters and receive positive customer feedback scores above 4.5 qualify for annual bonuses equal to 10% of their base salary",
                expected_elements=["employee", "sales_target", "3 consecutive", "quarters", "feedback > 4.5", "bonus", "10%", "base_salary"],
                complexity_features=["consecutive_time_periods", "performance_metrics", "threshold_conditions", "percentage_calculation"],
                real_world_scenario="HR compensation system rules"
            ),
            
            # Software Specifications
            RealisticTestCase(
                domain="Software Systems",
                description="API rate limiting",
                english="When a client makes more than 100 requests per minute, the system must return a rate limit error and block further requests from that client for 5 minutes",
                expected_elements=["client", "requests > 100", "per minute", "rate_limit_error", "block", "5 minutes"],
                complexity_features=["rate_calculation", "temporal_action", "error_handling", "time_based_blocking"],
                real_world_scenario="API gateway rate limiting implementation"
            ),
            
            RealisticTestCase(
                domain="Software Systems",
                description="Data backup policy",
                english="The system must perform incremental backups every 4 hours during business days and full backups every Sunday at 2 AM, unless a critical update is in progress",
                expected_elements=["incremental_backup", "4 hours", "business_days", "full_backup", "Sunday", "2 AM", "unless", "critical_update"],
                complexity_features=["scheduled_actions", "different_backup_types", "day_of_week", "exception_handling"],
                real_world_scenario="Enterprise backup system configuration"
            ),
            
            # Scientific/Mathematical
            RealisticTestCase(
                domain="Scientific Computing",
                description="Chemical reaction constraints",
                english="For all chemical reactions where the temperature exceeds 300 Kelvin and the pressure is between 1 and 5 atmospheres, the reaction rate increases exponentially with a coefficient of 2.5",
                expected_elements=["reaction", "temperature > 300", "Kelvin", "pressure", "between 1 and 5", "atmospheres", "rate", "exponential", "2.5"],
                complexity_features=["scientific_units", "range_constraints", "exponential_relationship", "coefficient"],
                real_world_scenario="Chemical process control system"
            ),
            
            RealisticTestCase(
                domain="Scientific Computing",
                description="Data validation in experiments",
                english="Experimental data points are valid only if they fall within three standard deviations of the mean and were collected when the instrument calibration was less than 24 hours old",
                expected_elements=["data_points", "valid", "3 standard_deviations", "mean", "calibration < 24 hours"],
                complexity_features=["statistical_constraints", "temporal_validity", "instrument_state", "data_quality"],
                real_world_scenario="Laboratory data acquisition system"
            ),
            
            # Legal/Regulatory
            RealisticTestCase(
                domain="Legal Compliance",
                description="GDPR data retention",
                english="Personal data of European Union residents must be deleted within 30 days of account closure unless required for legal compliance or the user has explicitly consented to extended retention",
                expected_elements=["personal_data", "EU_residents", "delete", "30 days", "account_closure", "unless", "legal_compliance", "consent", "extended_retention"],
                complexity_features=["geographic_scope", "time_limit", "multiple_exceptions", "user_consent"],
                real_world_scenario="GDPR compliance system"
            ),
            
            RealisticTestCase(
                domain="Legal Compliance",
                description="Financial reporting requirements",
                english="Publicly traded companies with annual revenue exceeding $1 billion must file quarterly reports within 45 days of quarter end and annual reports within 90 days of fiscal year end",
                expected_elements=["public_company", "revenue > 1B", "quarterly_report", "45 days", "quarter_end", "annual_report", "90 days", "fiscal_year_end"],
                complexity_features=["company_classification", "revenue_threshold", "multiple_deadlines", "reporting_types"],
                real_world_scenario="SEC compliance reporting system"
            ),
            
            # IoT/Embedded Systems
            RealisticTestCase(
                domain="IoT Systems",
                description="Smart thermostat logic",
                english="When motion is detected in a room and the ambient temperature differs from the set point by more than 2 degrees, the HVAC system adjusts the temperature unless the room has been unoccupied for more than 30 minutes",
                expected_elements=["motion_detected", "temperature", "differs", "set_point", "> 2 degrees", "HVAC", "adjust", "unless", "unoccupied > 30 min"],
                complexity_features=["sensor_input", "threshold_difference", "conditional_action", "occupancy_tracking"],
                real_world_scenario="Smart building automation"
            ),
            
            RealisticTestCase(
                domain="IoT Systems",
                description="Industrial sensor alerts",
                english="If any sensor in the production line reports values outside the acceptable range for more than 5 consecutive readings, the system must alert the supervisor and reduce line speed by 50%",
                expected_elements=["sensor", "production_line", "outside_range", "5 consecutive", "alert", "supervisor", "reduce_speed", "50%"],
                complexity_features=["sensor_network", "consecutive_anomalies", "dual_action", "percentage_adjustment"],
                real_world_scenario="Industrial IoT monitoring system"
            ),
            
            # Healthcare Systems
            RealisticTestCase(
                domain="Healthcare",
                description="Medication interaction warning",
                english="When prescribing a new medication, the system must check for interactions with all current medications and alert the physician if any severe interactions are found or if the patient has documented allergies to the medication class",
                expected_elements=["new_medication", "check_interactions", "current_medications", "alert", "physician", "severe_interactions", "allergies", "medication_class"],
                complexity_features=["drug_interaction_checking", "allergy_verification", "classification_hierarchy", "safety_alerts"],
                real_world_scenario="Electronic health record system"
            ),
            
            RealisticTestCase(
                domain="Healthcare",
                description="Patient monitoring thresholds",
                english="For patients in intensive care, if heart rate exceeds 120 or drops below 50, or if oxygen saturation falls below 90%, the monitoring system must immediately alert nursing staff and log the event with timestamp",
                expected_elements=["intensive_care", "heart_rate > 120", "< 50", "oxygen < 90%", "alert", "nursing_staff", "log", "timestamp"],
                complexity_features=["multiple_vital_signs", "upper_lower_bounds", "immediate_action", "event_logging"],
                real_world_scenario="ICU patient monitoring system"
            ),
            
            # Financial Systems
            RealisticTestCase(
                domain="Financial Systems",
                description="Fraud detection rules",
                english="Transactions are flagged as potentially fraudulent if they exceed 3 times the account's average transaction amount and occur in a different country than the previous transaction within a 2-hour window",
                expected_elements=["transaction", "flagged", "fraudulent", "> 3 times", "average_amount", "different_country", "previous", "2 hour window"],
                complexity_features=["statistical_anomaly", "geographic_analysis", "temporal_proximity", "historical_comparison"],
                real_world_scenario="Credit card fraud detection system"
            ),
            
            RealisticTestCase(
                domain="Financial Systems",
                description="Trading system circuit breaker",
                english="If the market index drops by more than 7% from the previous day's close, trading must be halted for 15 minutes, and if it drops by more than 13%, trading is suspended for the remainder of the day",
                expected_elements=["market_index", "drops > 7%", "previous_close", "halt", "15 minutes", "drops > 13%", "suspended", "remainder_day"],
                complexity_features=["percentage_thresholds", "graduated_response", "market_reference", "time_based_actions"],
                real_world_scenario="Stock exchange circuit breaker implementation"
            ),
            
            # Education Systems
            RealisticTestCase(
                domain="Education",
                description="Student graduation requirements",
                english="Students qualify for graduation when they complete all required courses with a grade of C or better, maintain a cumulative GPA above 2.0, and fulfill the community service requirement of 40 hours",
                expected_elements=["student", "graduation", "required_courses", "grade >= C", "GPA > 2.0", "community_service", "40 hours"],
                complexity_features=["multiple_requirements", "grade_thresholds", "cumulative_metrics", "non_academic_requirements"],
                real_world_scenario="University graduation tracking system"
            ),
            
            # Transportation Systems
            RealisticTestCase(
                domain="Transportation",
                description="Traffic light optimization",
                english="During rush hours between 7-9 AM and 5-7 PM on weekdays, traffic lights on main arterial roads should extend green light duration by 20% when vehicle queue length exceeds 10 cars",
                expected_elements=["rush_hours", "7-9 AM", "5-7 PM", "weekdays", "arterial_roads", "green_light", "extend 20%", "queue > 10"],
                complexity_features=["time_of_day_rules", "day_of_week", "traffic_sensing", "dynamic_adjustment"],
                real_world_scenario="Smart city traffic management"
            )
        ]
    
    def test_sentence(self, test_case: RealisticTestCase) -> Dict[str, any]:
        """Test a single realistic complex sentence."""
        print(f"\n{'='*70}")
        print(f"🏢 Domain: {test_case.domain}")
        print(f"📋 Scenario: {test_case.real_world_scenario}")
        print(f"📝 Description: {test_case.description}")
        print(f"💬 Sentence: \"{test_case.english}\"")
        print(f"🔧 Features: {', '.join(test_case.complexity_features)}")
        print("-" * 70)
        
        result = {
            "domain": test_case.domain,
            "scenario": test_case.real_world_scenario,
            "sentence": test_case.english,
            "translations": {},
            "element_coverage": 0.0,
            "success": False
        }
        
        # Try different translation approaches
        try:
            # Method 1: Pattern-based translation
            print("\n1️⃣ Pattern-based Translation:")
            from translators.pattern_translator import PatternTranslator
            translator = PatternTranslator()
            pattern_result = translator.translate_to_tau(test_case.english)
            
            if pattern_result["success"]:
                print(f"   ✅ Success: {pattern_result['translated']}")
                result["translations"]["pattern"] = pattern_result["translated"]
                coverage = self._calculate_coverage(pattern_result["translated"], test_case.expected_elements)
                print(f"   📊 Element coverage: {coverage:.1%}")
                result["element_coverage"] = max(result["element_coverage"], coverage)
                result["success"] = True
            else:
                print(f"   ❌ Failed: {pattern_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
        
        try:
            # Method 2: NLP Service
            print("\n2️⃣ NLP Service Translation:")
            from api.nlp import NLPService
            service = NLPService()
            nlp_result = service.translate(test_case.english, "english", "tau")
            
            if nlp_result.get("success"):
                print(f"   ✅ Success: {nlp_result['translated']}")
                result["translations"]["nlp"] = nlp_result["translated"]
                coverage = self._calculate_coverage(nlp_result["translated"], test_case.expected_elements)
                print(f"   📊 Element coverage: {coverage:.1%}")
                result["element_coverage"] = max(result["element_coverage"], coverage)
                result["success"] = True
            else:
                print(f"   ❌ Failed: {nlp_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
        
        try:
            # Method 3: Grammar-based parser
            print("\n3️⃣ Grammar-based Parser:")
            from api.grammar import parse_with_grammar
            grammar_result = parse_with_grammar(test_case.english, "tce")
            
            if grammar_result.get("success"):
                print(f"   ✅ Success: {grammar_result.get('result', 'Parsed successfully')}")
                result["translations"]["grammar"] = str(grammar_result.get("result"))
                result["success"] = True
            else:
                print(f"   ❌ Failed: {grammar_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
        
        # Analysis
        print(f"\n📊 Overall Result:")
        print(f"   Success: {'✅ Yes' if result['success'] else '❌ No'}")
        print(f"   Element Coverage: {result['element_coverage']:.1%}")
        print(f"   Working Methods: {len(result['translations'])}")
        
        return result
    
    def _calculate_coverage(self, output: str, expected_elements: List[str]) -> float:
        """Calculate how many expected elements appear in the output."""
        if not expected_elements:
            return 1.0
        
        output_lower = output.lower()
        found = 0
        for element in expected_elements:
            # Handle special cases
            if ">" in element or "<" in element or "=" in element:
                # For comparisons, check if the operator and value are present
                parts = element.split()
                if all(part.lower() in output_lower for part in parts):
                    found += 1
            elif element.lower() in output_lower:
                found += 1
        
        return found / len(expected_elements)
    
    def run_comprehensive_test(self) -> Dict[str, any]:
        """Run comprehensive test on all realistic sentences."""
        print("🌍 REALISTIC COMPLEX SENTENCE TEST SUITE")
        print("=" * 70)
        print("Testing complex but realistic sentences from various domains")
        print("Goal: Assess real-world applicability of translation technology")
        print()
        
        all_results = []
        domain_results = {}
        
        for test_case in self.test_cases:
            result = self.test_sentence(test_case)
            all_results.append(result)
            
            # Group by domain
            if test_case.domain not in domain_results:
                domain_results[test_case.domain] = []
            domain_results[test_case.domain].append(result)
        
        # Generate analysis
        print("\n\n" + "=" * 70)
        print("📊 COMPREHENSIVE ANALYSIS")
        print("=" * 70)
        
        total_cases = len(all_results)
        successful_cases = sum(1 for r in all_results if r["success"])
        
        print(f"\n🎯 Overall Performance:")
        print(f"   Total Test Cases: {total_cases}")
        print(f"   Successful Translations: {successful_cases}/{total_cases} ({successful_cases/total_cases*100:.1f}%)")
        print(f"   Average Element Coverage: {sum(r['element_coverage'] for r in all_results)/total_cases:.1%}")
        
        print(f"\n📈 Performance by Domain:")
        domain_stats = []
        for domain, results in domain_results.items():
            success_rate = sum(1 for r in results if r["success"]) / len(results)
            avg_coverage = sum(r["element_coverage"] for r in results) / len(results)
            domain_stats.append((domain, success_rate, avg_coverage, len(results)))
        
        # Sort by success rate
        domain_stats.sort(key=lambda x: x[1], reverse=True)
        
        for domain, success_rate, avg_coverage, count in domain_stats:
            print(f"   {domain}: {success_rate:.1%} success, {avg_coverage:.1%} coverage ({count} cases)")
        
        print(f"\n💪 Strongest Domains (>80% success):")
        strong_domains = [d for d, rate, _, _ in domain_stats if rate >= 0.8]
        if strong_domains:
            for domain in strong_domains:
                print(f"   ✅ {domain}")
        else:
            print("   ⚠️  No domains reached 80% success rate")
        
        print(f"\n🔧 Challenging Domains (<60% success):")
        weak_domains = [(d, rate) for d, rate, _, _ in domain_stats if rate < 0.6]
        if weak_domains:
            for domain, rate in weak_domains:
                print(f"   ❌ {domain}: {rate:.1%}")
        else:
            print("   ✅ All domains achieved at least 60% success rate")
        
        # Identify common failure patterns
        print(f"\n🔍 Common Success Patterns:")
        success_features = {}
        failure_features = {}
        
        for i, result in enumerate(all_results):
            test_case = self.test_cases[i]
            for feature in test_case.complexity_features:
                if result["success"]:
                    success_features[feature] = success_features.get(feature, 0) + 1
                else:
                    failure_features[feature] = failure_features.get(feature, 0) + 1
        
        # Show features that mostly succeed
        total_by_feature = {}
        for feature in set(list(success_features.keys()) + list(failure_features.keys())):
            total = success_features.get(feature, 0) + failure_features.get(feature, 0)
            if total > 0:
                success_rate = success_features.get(feature, 0) / total
                total_by_feature[feature] = (success_rate, total)
        
        sorted_features = sorted(total_by_feature.items(), key=lambda x: x[1][0], reverse=True)
        
        print("   Features with high success rate:")
        for feature, (rate, count) in sorted_features[:5]:
            if rate >= 0.7:
                print(f"   ✅ {feature}: {rate:.1%} success ({count} cases)")
        
        print(f"\n   Features causing difficulties:")
        for feature, (rate, count) in reversed(sorted_features[-5:]):
            if rate < 0.5:
                print(f"   ❌ {feature}: {rate:.1%} success ({count} cases)")
        
        # Real-world readiness assessment
        print(f"\n🚀 REAL-WORLD READINESS ASSESSMENT:")
        
        if successful_cases / total_cases >= 0.85:
            print("   🏆 PRODUCTION READY: Excellent performance across domains")
            print("   ✅ Suitable for deployment in real-world applications")
        elif successful_cases / total_cases >= 0.70:
            print("   ⭐ NEARLY READY: Good performance with some limitations")
            print("   🔧 Recommended: Address weak domains before production")
        elif successful_cases / total_cases >= 0.50:
            print("   📈 PROMISING: Shows potential but needs improvement")
            print("   💡 Focus on enhancing core translation capabilities")
        else:
            print("   🚧 DEVELOPMENT PHASE: Significant improvements needed")
            print("   📚 Recommend focusing on fundamental enhancements")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("   1. Implement domain-specific vocabularies for better coverage")
        print("   2. Add support for numerical comparisons and calculations")
        print("   3. Enhance temporal logic handling (time windows, schedules)")
        print("   4. Improve handling of exception clauses (unless, except)")
        print("   5. Add support for percentage and statistical operations")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"realistic_complexity_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "total_cases": total_cases,
                "successful_cases": successful_cases,
                "success_rate": successful_cases / total_cases,
                "domain_analysis": {d: {"success_rate": r, "coverage": c, "count": n} 
                                  for d, r, c, n in domain_stats},
                "detailed_results": all_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return {
            "total_cases": total_cases,
            "successful_cases": successful_cases,
            "success_rate": successful_cases / total_cases,
            "domain_stats": domain_stats,
            "results_file": results_file
        }

def main():
    """Run the realistic complexity test suite."""
    tester = RealisticComplexityTester()
    analysis = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    success = analysis["success_rate"] >= 0.6  # 60% threshold for realistic sentences
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()