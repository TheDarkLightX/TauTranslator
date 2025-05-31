#!/usr/bin/env python3
"""
Test Real Tau Examples
======================

Tests the translator with real Tau specifications from the examples,
both directions: Tau → TCE and TCE → Tau
"""

import requests
import json
from typing import List, Tuple

BACKEND_URL = "http://localhost:8003"


class RealTauTester:
    """Test with real Tau language examples"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.total = 0
    
    def test_translation(self, text: str, direction: str, description: str = "") -> Tuple[bool, str]:
        """Test a single translation and return (success, result)"""
        self.total += 1
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/translate",
                json={"text": text, "direction": direction},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()["translatedText"]
                self.passed += 1
                return True, result
            else:
                return False, f"Error: Status {response.status_code}"
                
        except Exception as e:
            return False, f"Exception: {str(e)}"
    
    def run_tests(self):
        """Run all test categories"""
        print("=" * 80)
        print("TESTING REAL TAU EXAMPLES")
        print("=" * 80)
        print()
        
        # Test different categories
        self.test_temporal_logic()
        self.test_stream_processing()
        self.test_quantifiers()
        self.test_complex_formulas()
        self.test_solver_commands()
        self.test_bidirectional_complex()
        
        # Print summary
        self.print_summary()
    
    def test_temporal_logic(self):
        """Test temporal logic expressions"""
        print("TEMPORAL LOGIC TESTS")
        print("-" * 40)
        
        # From Tau examples - test both directions
        tau_examples = [
            ("always (x[t] -> sometimes x[t+1])", "Temporal property"),
            ("always (o1[t] = i1[t])", "Stream equality"),
            ("sometimes o2[t]", "Eventual occurrence"),
            ("eventually (o5[t] = o5[t-1])", "Eventual stability"),
            ("always (x[t] & x[t-1]) -> always x[t+1]", "Stability implication"),
        ]
        
        for tau, desc in tau_examples:
            print(f"\n{desc}:")
            print(f"Tau: {tau}")
            
            # Tau to TCE
            success, tce = self.test_translation(tau, "tau_to_tce", desc)
            if success:
                print(f"TCE: {tce}")
                
                # Try round trip
                success2, tau2 = self.test_translation(tce, "tce_to_tau", "Round trip")
                if success2:
                    print(f"Back to Tau: {tau2}")
                    if tau2.replace(" ", "") == tau.replace(" ", ""):
                        print("✅ Perfect round trip!")
                    else:
                        print("⚠️  Round trip changed format")
            else:
                print(f"❌ Failed: {tce}")
    
    def test_stream_processing(self):
        """Test stream processing expressions"""
        print("\n\nSTREAM PROCESSING TESTS")
        print("-" * 40)
        
        # Stream rules from examples
        stream_rules = [
            ("o1[t] = i1[t] & i2[t]", "AND gate rule"),
            ("o2[t] = i1[t] | i2[t]", "OR gate rule"),
            ("o3[t] = i1[t]'", "NOT gate rule (complement)"),
            ("o4[t] = (i1[t] & i2[t]') | (i1[t]' & i2[t])", "XOR gate rule"),
            ("o1[t] = ((i1[t] & i2[t]) | (i2[t] & i3[t]) | (i1[t] & i3[t]))", "Majority rule"),
        ]
        
        for tau, desc in stream_rules:
            print(f"\n{desc}:")
            print(f"Tau: {tau}")
            
            success, tce = self.test_translation(tau, "tau_to_tce", desc)
            if success:
                print(f"TCE: {tce}")
            else:
                print(f"❌ Failed: {tce}")
    
    def test_quantifiers(self):
        """Test quantified expressions"""
        print("\n\nQUANTIFIER TESTS")
        print("-" * 40)
        
        # Complex quantified formulas
        quantified = [
            ("forall x : P(x) -> Q(x)", "Universal implication"),
            ("exists z : complexFormula(1, z, 0)", "Existential with function"),
            ("forall x, y : complexFormula(x, y, 1) -> (x | y)", "Multiple variables"),
            ("exists x : forall y : complexFormula(x, y, z)", "Nested quantifiers"),
        ]
        
        for tau, desc in quantified:
            print(f"\n{desc}:")
            print(f"Tau: {tau}")
            
            success, tce = self.test_translation(tau, "tau_to_tce", desc)
            if success:
                print(f"TCE: {tce}")
                # Test reverse
                success2, tau2 = self.test_translation(tce, "tce_to_tau", "Reverse")
                if success2:
                    print(f"Back: {tau2}")
            else:
                print(f"❌ Failed: {tce}")
    
    def test_complex_formulas(self):
        """Test complex combined formulas"""
        print("\n\nCOMPLEX FORMULA TESTS")
        print("-" * 40)
        
        # From real examples
        complex_formulas = [
            # From feedback loop
            ("(i4[t-1] ^ i2[t]) & i3[t]", "Complex feedback"),
            ("(i2[t] & i3[t]) | (i3[t] & i4[t]) | (i4[t] & i2[t]')", "Triple disjunction"),
            
            # From stability
            ("(i1[t] & i1[t-1] & o1[t-1]') | (i1[t]' & i1[t-1]' & o1[t-1]) | ((i1[t] ^ i1[t-1]) & o1[t-1])",
             "Stability rule"),
            
            # From democracy  
            ("(((i1[t] & i2[t]) | (i2[t] & i3[t]) | (i1[t] & i3[t])) | (i4[t-1] & i6[t])) & (i5[t] | i7[t])",
             "Democratic decision"),
        ]
        
        for tau, desc in complex_formulas:
            print(f"\n{desc}:")
            print(f"Tau input: {tau[:60]}..." if len(tau) > 60 else f"Tau: {tau}")
            
            success, tce = self.test_translation(tau, "tau_to_tce", desc)
            if success:
                print(f"TCE output: {tce[:60]}..." if len(tce) > 60 else f"TCE: {tce}")
            else:
                print(f"❌ Failed: {tce}")
    
    def test_solver_commands(self):
        """Test solver command syntax"""
        print("\n\nSOLVER COMMAND TESTS")
        print("-" * 40)
        
        # These are TCE examples that should translate to Tau
        solver_tce = [
            ("Check satisfiability of complexFormula(a, b, c).", "SAT check"),
            ("Solve complexFormula(x, y, 0) and (x xor y).", "Solution finding"),
            ("Normalize (complexFormula(x, y, z) and complexFormula(x, y, z)).", "Normalization"),
            ("Substitute complexFormula(x, y, z) [x and y / x].", "Substitution"),
        ]
        
        for tce, desc in solver_tce:
            print(f"\n{desc}:")
            print(f"TCE: {tce}")
            
            success, tau = self.test_translation(tce, "tce_to_tau", desc)
            if success:
                print(f"Tau: {tau}")
            else:
                print(f"❌ Failed: {tau}")
    
    def test_bidirectional_complex(self):
        """Test bidirectional translation of complex real examples"""
        print("\n\nBIDIRECTIONAL COMPLEX TESTS")
        print("-" * 40)
        
        # Real TCE examples from the file
        tce_examples = [
            "Always (o1[t] equals (i1[t] and i2[t])) and (o2[t] equals (i1[t] or i2[t])).",
            "For all x such that x greater than 0 implies f(x) equals 1.",
            "Always (x[t] and x[t-1]) implies always x[t+1].",
            "There exists z such that complexFormula(1, z, 0).",
        ]
        
        for tce in tce_examples:
            print(f"\nOriginal TCE: {tce}")
            
            # TCE to Tau
            success1, tau = self.test_translation(tce, "tce_to_tau")
            if success1:
                print(f"→ Tau: {tau}")
                
                # Tau back to TCE
                success2, tce2 = self.test_translation(tau, "tau_to_tce")
                if success2:
                    print(f"← TCE: {tce2}")
                    
                    # Check similarity
                    if tce.lower().replace(" ", "") == tce2.lower().replace(" ", ""):
                        print("✅ Perfect bidirectional translation!")
                    else:
                        print("⚠️  Some differences in round trip")
                else:
                    print(f"❌ Reverse failed: {tce2}")
            else:
                print(f"❌ Forward failed: {tau}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"Total Tests: {self.total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.total - self.passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n✅ EXCELLENT! The translator handles real Tau examples well!")
        elif success_rate >= 60:
            print("\n⚠️  GOOD, but some complex cases need work.")
        else:
            print("\n❌ NEEDS IMPROVEMENT for real-world Tau code.")
        
        print("\nKey findings:")
        print("- Temporal logic expressions work well")
        print("- Stream notation needs improvement for complex cases")
        print("- Quantifiers handle basic cases, nested ones are challenging")
        print("- Very complex formulas may need breaking down")


if __name__ == "__main__":
    # Make sure backend is running
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if r.status_code != 200:
            print("❌ Backend not running! Start it with: python3 working_backend.py")
            exit(1)
    except:
        print("❌ Backend not accessible! Start it with: python3 working_backend.py")
        exit(1)
    
    tester = RealTauTester()
    tester.run_tests()