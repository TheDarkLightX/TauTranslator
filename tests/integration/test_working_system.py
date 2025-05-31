#!/usr/bin/env python3
"""
Comprehensive Test of Working System
====================================

Tests the complete translation system with various complexity levels.
"""

import requests
import json
import time
from typing import List, Dict, Tuple

BACKEND_URL = "http://localhost:8003"


class SystemTester:
    """Test the working translation system"""
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def test_translation(self, text: str, direction: str, expected_contains: List[str] = None) -> bool:
        """Test a single translation"""
        self.total_tests += 1
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/translate",
                json={"text": text, "direction": direction},
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"❌ Failed: {text}")
                print(f"   Status: {response.status_code}")
                return False
            
            data = response.json()
            translated = data.get("translatedText", "")
            
            # Check if expected patterns are in result
            if expected_contains:
                for pattern in expected_contains:
                    if pattern not in translated:
                        print(f"❌ Failed: {text}")
                        print(f"   Expected pattern '{pattern}' not found in: {translated}")
                        return False
            
            print(f"✅ Success: {text}")
            print(f"   Result: {translated}")
            self.passed_tests += 1
            
            self.results.append({
                "input": text,
                "output": translated,
                "direction": direction,
                "time": data.get("processingTime", 0)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {text}")
            print(f"   Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("=" * 80)
        print("COMPREHENSIVE TRANSLATION SYSTEM TEST")
        print("=" * 80)
        print()
        
        # Check backend health
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=2)
            if r.status_code == 200:
                print("✅ Backend is healthy")
                print(f"   Status: {r.json()}")
                print()
            else:
                print("❌ Backend not healthy")
                return
        except Exception as e:
            print(f"❌ Backend not accessible: {e}")
            return
        
        # Test categories
        self.test_simple_boolean()
        self.test_temporal_logic()
        self.test_quantifiers()
        self.test_complex_expressions()
        self.test_bidirectional()
        self.test_edge_cases()
        
        # Summary
        self.print_summary()
    
    def test_simple_boolean(self):
        """Test simple boolean expressions"""
        print("TEST CATEGORY: Simple Boolean Logic")
        print("-" * 40)
        
        tests = [
            ("x and y.", ["x & y"]),
            ("p or q.", ["p | q"]),
            ("not x.", ["! x"]),
            ("x implies y.", ["x -> y"]),
            ("x iff y.", ["x <-> y"]),
            ("x xor y.", ["x ^ y"]),
            ("x and y or z.", ["x & y | z"]),
            ("x or y and z.", ["x | y & z"]),
        ]
        
        for text, expected in tests:
            self.test_translation(text, "tce_to_tau", expected)
        print()
    
    def test_temporal_logic(self):
        """Test temporal logic expressions"""
        print("TEST CATEGORY: Temporal Logic")
        print("-" * 40)
        
        tests = [
            ("Always x.", ["always x"]),
            ("Sometimes y.", ["sometimes y"]),
            ("Eventually z.", ["eventually z"]),
            ("Always x and y.", ["always", "&"]),
            ("x at time t.", ["x@t"]),
            ("y at time t-1.", ["y@(t-1)"]),
            ("Always x implies eventually y.", ["always", "->", "eventually"]),
            ("x until y.", ["x until y"]),
        ]
        
        for text, expected in tests:
            self.test_translation(text, "tce_to_tau", expected)
        print()
    
    def test_quantifiers(self):
        """Test quantified expressions"""
        print("TEST CATEGORY: Quantifiers")
        print("-" * 40)
        
        tests = [
            ("For all x such that P(x).", ["forall x :", "P(x)"]),
            ("There exists y such that Q(y).", ["exists y :", "Q(y)"]),
            ("For all x such that x > 0.", ["forall x :", "x > 0"]),
            ("For all x such that x > 0 implies f(x) = 1.", ["forall x :", "x > 0 ->", "f(x) = 1"]),
            ("There exists x such that x < 0 and g(x) > 0.", ["exists x :", "x < 0 &", "g(x) > 0"]),
        ]
        
        for text, expected in tests:
            self.test_translation(text, "tce_to_tau", expected)
        print()
    
    def test_complex_expressions(self):
        """Test complex mixed expressions"""
        print("TEST CATEGORY: Complex Expressions")
        print("-" * 40)
        
        tests = [
            ("If x > 0 then y else z.", ["?", ":"]),
            ("Always for all x such that P(x) implies Q(x).", ["always", "forall x :", "P(x) -> Q(x)"]),
            ("x at time t and y at time t+1 implies z at time t+2.", ["x@t", "y@", "z@"]),
            ("input stream s at time t.", ["input s", "@t"]),
            ("output stream r at time t-1.", ["output r", "@(t-1)"]),
            ("For all t such that x at time t implies x at time t+1.", ["forall t :", "x@t", "x@"]),
        ]
        
        for text, expected in tests:
            self.test_translation(text, "tce_to_tau", expected)
        print()
    
    def test_bidirectional(self):
        """Test bidirectional translation"""
        print("TEST CATEGORY: Bidirectional Translation")
        print("-" * 40)
        
        # Test TCE -> Tau -> TCE roundtrip
        tce_examples = [
            "Always x and y.",
            "For all x such that P(x).",
            "x at time t implies y at time t+1.",
        ]
        
        for tce in tce_examples:
            # Forward
            r1 = requests.post(f"{BACKEND_URL}/translate", 
                             json={"text": tce, "direction": "tce_to_tau"})
            if r1.status_code == 200:
                tau = r1.json()["translatedText"]
                
                # Reverse
                r2 = requests.post(f"{BACKEND_URL}/translate",
                                 json={"text": tau, "direction": "tau_to_tce"})
                if r2.status_code == 200:
                    tce2 = r2.json()["translatedText"]
                    
                    print(f"✅ Roundtrip: {tce}")
                    print(f"   TCE -> Tau: {tau}")
                    print(f"   Tau -> TCE: {tce2}")
                    self.passed_tests += 1
                else:
                    print(f"❌ Reverse failed: {tau}")
            else:
                print(f"❌ Forward failed: {tce}")
            
            self.total_tests += 1
        print()
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("TEST CATEGORY: Edge Cases")
        print("-" * 40)
        
        tests = [
            # Empty/whitespace
            ("", None),  # Should error
            ("   ", None),  # Should error
            
            # Missing period
            ("x and y", ["x & y"]),  # Should still work
            
            # Multiple sentences (only first should be translated)
            ("x. y.", ["x"]),
            
            # Nested parentheses
            ("((x and y) or z).", ["((x & y) | z)"]),
            
            # Mixed case
            ("Always X AND Y.", ["always", "&"]),
            ("ALWAYS x OR y.", ["always", "|"]),
        ]
        
        for text, expected in tests:
            if expected is None:
                # Expect error
                self.total_tests += 1
                try:
                    r = requests.post(f"{BACKEND_URL}/translate",
                                    json={"text": text, "direction": "tce_to_tau"})
                    if r.status_code != 200 or "Error" in r.json().get("translatedText", ""):
                        print(f"✅ Correctly rejected: '{text}'")
                        self.passed_tests += 1
                    else:
                        print(f"❌ Should have failed: '{text}'")
                except:
                    print(f"✅ Correctly errored: '{text}'")
                    self.passed_tests += 1
            else:
                self.test_translation(text, "tce_to_tau", expected)
        print()
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Performance stats
        if self.results:
            times = [r["time"] for r in self.results if "time" in r]
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                print("Performance Stats:")
                print(f"  Average time: {avg_time*1000:.2f} ms")
                print(f"  Min time: {min_time*1000:.2f} ms")
                print(f"  Max time: {max_time*1000:.2f} ms")
        
        print()
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! System is working very well!")
        elif success_rate >= 70:
            print("✅ GOOD! System is mostly working.")
        elif success_rate >= 50:
            print("⚠️  FAIR. System needs improvement.")
        else:
            print("❌ POOR. System has significant issues.")


if __name__ == "__main__":
    tester = SystemTester()
    tester.run_all_tests()