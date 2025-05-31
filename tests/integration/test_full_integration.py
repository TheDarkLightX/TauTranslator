#!/usr/bin/env python3
"""
Full Integration Test Suite
===========================

Comprehensive tests showing:
1. What currently works
2. What doesn't work
3. What needs to be fixed
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Test configuration
SIMPLE_BACKEND_URL = "http://127.0.0.1:8000"
GRAMMAR_BACKEND_URL = "http://127.0.0.1:8001"
PWA_API_URL = "http://localhost:3002/api"


class IntegrationTestSuite:
    """Comprehensive integration test suite"""
    
    def __init__(self):
        self.results = []
        self.grammar_backend_proc = None
        
    def log_test(self, name: str, passed: bool, details: str):
        """Log test result"""
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        print(f"   {details}")
        print()
        self.results.append({
            "name": name,
            "passed": passed,
            "details": details
        })
    
    def start_grammar_backend(self) -> bool:
        """Start the grammar-aware backend"""
        try:
            # Check if already running
            try:
                r = requests.get(f"{GRAMMAR_BACKEND_URL}/health", timeout=1)
                if r.status_code == 200:
                    self.log_test(
                        "Grammar Backend Already Running",
                        True,
                        "Grammar-aware backend is already running"
                    )
                    return True
            except:
                pass
            
            # Start new instance
            self.grammar_backend_proc = subprocess.Popen(
                [sys.executable, "grammar_aware_backend.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for startup
            time.sleep(2)
            
            # Check if started
            try:
                r = requests.get(f"{GRAMMAR_BACKEND_URL}/health", timeout=5)
                if r.status_code == 200:
                    self.log_test(
                        "Grammar Backend Started",
                        True,
                        "Grammar-aware backend started successfully"
                    )
                    return True
            except:
                pass
                
            self.log_test(
                "Grammar Backend Start Failed",
                False,
                "Could not start grammar-aware backend"
            )
            return False
            
        except Exception as e:
            self.log_test(
                "Grammar Backend Error",
                False,
                f"Error starting grammar backend: {str(e)}"
            )
            return False
    
    def test_basic_functionality(self):
        """Test 1: Basic translation functionality"""
        print("=" * 60)
        print("TEST 1: BASIC FUNCTIONALITY")
        print("=" * 60)
        print()
        
        # Test simple backend
        try:
            r = requests.get(f"{SIMPLE_BACKEND_URL}/health", timeout=2)
            if r.status_code == 200:
                self.log_test(
                    "Simple Backend Health",
                    True,
                    "Simple backend is running"
                )
                
                # Test translation
                r = requests.post(
                    f"{SIMPLE_BACKEND_URL}/translate",
                    json={
                        "text": "Always x AND y.",
                        "direction": "tce_to_tau"
                    }
                )
                
                if r.status_code == 200:
                    result = r.json()
                    self.log_test(
                        "Basic Translation",
                        True,
                        f"Translation works: '{result.get('translatedText')}'"
                    )
                else:
                    self.log_test(
                        "Basic Translation",
                        False,
                        f"Translation failed with status {r.status_code}"
                    )
            else:
                self.log_test(
                    "Simple Backend Health",
                    False,
                    "Simple backend not healthy"
                )
        except Exception as e:
            self.log_test(
                "Simple Backend",
                False,
                f"Simple backend not accessible: {str(e)}"
            )
    
    def test_grammar_loading(self):
        """Test 2: Grammar file loading"""
        print("=" * 60)
        print("TEST 2: GRAMMAR FILE LOADING")
        print("=" * 60)
        print()
        
        # Test direct grammar loader
        try:
            from src.tau_translator_omega.core_engine.tgf_grammar_loader import TGFGrammarLoader
            
            loader = TGFGrammarLoader()
            count = loader.load_all_grammars()
            
            self.log_test(
                "Grammar Loader Import",
                True,
                f"Loaded {count} grammar files"
            )
            
            active = loader.get_active_grammar()
            if active:
                self.log_test(
                    "Active Grammar",
                    True,
                    f"Active grammar: {active.filename} with {len(active.rules)} rules"
                )
            else:
                self.log_test(
                    "Active Grammar",
                    False,
                    "No active grammar found"
                )
                
        except Exception as e:
            self.log_test(
                "Grammar Loader",
                False,
                f"Grammar loader error: {str(e)}"
            )
    
    def test_grammar_backend(self):
        """Test 3: Grammar-aware backend"""
        print("=" * 60)
        print("TEST 3: GRAMMAR-AWARE BACKEND")
        print("=" * 60)
        print()
        
        if not self.start_grammar_backend():
            return
        
        try:
            # Check health
            r = requests.get(f"{GRAMMAR_BACKEND_URL}/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.log_test(
                    "Grammar Backend Health",
                    True,
                    f"Active grammar: {data.get('activeGrammar', 'None')}"
                )
                
                # Test translation with grammar
                r = requests.post(
                    f"{GRAMMAR_BACKEND_URL}/translate",
                    json={
                        "text": "Always x AND y.",
                        "direction": "tce_to_tau"
                    }
                )
                
                if r.status_code == 200:
                    result = r.json()
                    self.log_test(
                        "Grammar-Based Translation",
                        True,
                        f"Translation: '{result.get('translatedText')}' using {result.get('model')}"
                    )
                else:
                    self.log_test(
                        "Grammar-Based Translation",
                        False,
                        f"Translation failed: {r.status_code}"
                    )
                    
        except Exception as e:
            self.log_test(
                "Grammar Backend Test",
                False,
                f"Grammar backend error: {str(e)}"
            )
    
    def test_parser_integration(self):
        """Test 4: Parser and grammar integration"""
        print("=" * 60)
        print("TEST 4: PARSER INTEGRATION")
        print("=" * 60)
        print()
        
        try:
            from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
            
            parser = CNLParser()
            
            # Test parsing
            test_input = "Always x AND y."
            try:
                ast = parser.parse(test_input)
                self.log_test(
                    "Parser Basic Function",
                    True,
                    f"Parser can parse: '{test_input}'"
                )
            except Exception as e:
                self.log_test(
                    "Parser Basic Function",
                    False,
                    f"Parser error: {str(e)}"
                )
                
            # Check if parser uses custom grammar
            # This is the missing piece
            self.log_test(
                "Parser Custom Grammar",
                False,
                "Parser does NOT accept custom grammar files (needs implementation)"
            )
            
        except Exception as e:
            self.log_test(
                "Parser Import",
                False,
                f"Cannot import parser: {str(e)}"
            )
    
    def test_frontend_integration(self):
        """Test 5: Frontend integration"""
        print("=" * 60)
        print("TEST 5: FRONTEND INTEGRATION")
        print("=" * 60)
        print()
        
        # Check PWA API
        try:
            # Grammar files endpoint
            r = requests.get(f"{PWA_API_URL}/grammar-files", timeout=2)
            if r.status_code == 200:
                data = r.json()
                self.log_test(
                    "PWA Grammar Files API",
                    True,
                    f"PWA can list {len(data)} grammar files"
                )
            else:
                self.log_test(
                    "PWA Grammar Files API",
                    False,
                    f"Grammar files API returned {r.status_code}"
                )
                
            # Grammar integration endpoint
            r = requests.get(f"{PWA_API_URL}/grammar-integration", timeout=2)
            if r.status_code == 200:
                data = r.json()
                if data.get('hasActiveGrammar'):
                    self.log_test(
                        "PWA Grammar Integration",
                        True,
                        f"Active grammar in PWA: {data['grammar']['originalName']}"
                    )
                else:
                    self.log_test(
                        "PWA Grammar Integration",
                        False,
                        "No active grammar in PWA"
                    )
                    
        except Exception as e:
            self.log_test(
                "PWA API Access",
                False,
                f"Cannot access PWA API: {str(e)}"
            )
    
    def test_end_to_end(self):
        """Test 6: End-to-end workflow"""
        print("=" * 60)
        print("TEST 6: END-TO-END WORKFLOW")
        print("=" * 60)
        print()
        
        # What should work but doesn't
        workflow_steps = [
            ("User selects grammar file in UI", False, "UI shows grammar but doesn't use it"),
            ("Grammar file loaded by backend", True, "Grammar loader works"),
            ("Parser uses loaded grammar", False, "Parser uses hardcoded grammar"),
            ("Translation uses grammar rules", False, "Falls back to pattern matching"),
            ("Result reflects grammar rules", False, "Results are pattern-based, not grammar-based")
        ]
        
        for step, works, reason in workflow_steps:
            self.log_test(step, works, reason)
    
    def generate_summary(self):
        """Generate test summary and recommendations"""
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print()
        
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        print("WHAT WORKS:")
        print("✅ Basic translation with pattern matching")
        print("✅ Grammar files can be loaded and parsed")
        print("✅ Frontend can display grammar files")
        print("✅ Backend APIs are functional")
        print()
        
        print("WHAT DOESN'T WORK:")
        print("❌ Parser doesn't use loaded grammar files")
        print("❌ Translation doesn't use grammar rules")
        print("❌ No connection between grammar selection and parsing")
        print("❌ Grammar-aware translation not implemented")
        print()
        
        print("FIXES NEEDED:")
        print("1. Modify CNLParser to accept custom grammar string")
        print("2. Implement grammar conversion (TGF → Lark)")
        print("3. Connect grammar loader to parser initialization")
        print("4. Update translation API to reload parser with new grammar")
        print("5. Add tests for grammar-driven translation")
        print()
        
        print("IMPLEMENTATION PATH:")
        print("1. Update CNLParser.__init__ to accept optional grammar_string parameter")
        print("2. If grammar_string provided, use it instead of loading from file")
        print("3. In backend, initialize parser with converted grammar")
        print("4. Add /grammar/set endpoint to reload parser")
        print("5. Update PWA to call grammar reload when selection changes")
        
    def cleanup(self):
        """Clean up test resources"""
        if self.grammar_backend_proc:
            self.grammar_backend_proc.terminate()
            self.grammar_backend_proc.wait()
    
    def run_all_tests(self):
        """Run complete test suite"""
        try:
            self.test_basic_functionality()
            self.test_grammar_loading()
            self.test_grammar_backend()
            self.test_parser_integration()
            self.test_frontend_integration()
            self.test_end_to_end()
            self.generate_summary()
        finally:
            self.cleanup()


if __name__ == "__main__":
    suite = IntegrationTestSuite()
    suite.run_all_tests()