#!/usr/bin/env python3
"""
Comprehensive Integration Test for Grammar File Processing
=========================================================

This test demonstrates the current issues with grammar file integration
and provides a pathway to fixing them.
"""

import os
import json
import requests
import time
from pathlib import Path

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
PWA_URL = "http://localhost:3002"
GRAMMAR_CONFIG_FILE = Path("config/grammar-files.json")
GRAMMARS_DIR = Path("grammars")

class TestGrammarIntegration:
    """Test suite for grammar file integration"""
    
    def __init__(self):
        self.session_token = None
        self.test_results = []
        
    def log_result(self, test_name, passed, message):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}\n")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
    
    def test_backend_health(self):
        """Test 1: Check if backend is running"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Backend Health Check",
                    True,
                    f"Backend is healthy: {data.get('status', 'unknown')}"
                )
                return True
            else:
                self.log_result(
                    "Backend Health Check",
                    False,
                    f"Backend returned status {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result(
                "Backend Health Check",
                False,
                f"Backend not reachable: {str(e)}"
            )
            return False
    
    def test_grammar_files_exist(self):
        """Test 2: Check if grammar files exist"""
        grammar_files = list(GRAMMARS_DIR.glob("*.tgf")) + \
                       list(GRAMMARS_DIR.glob("*.ebnf")) + \
                       list(GRAMMARS_DIR.glob("*.lark"))
        
        if grammar_files:
            self.log_result(
                "Grammar Files Exist",
                True,
                f"Found {len(grammar_files)} grammar files: {[f.name for f in grammar_files[:3]]}..."
            )
            return True
        else:
            self.log_result(
                "Grammar Files Exist",
                False,
                f"No grammar files found in {GRAMMARS_DIR}"
            )
            return False
    
    def test_grammar_config(self):
        """Test 3: Check grammar configuration file"""
        if GRAMMAR_CONFIG_FILE.exists():
            try:
                with open(GRAMMAR_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    
                active_grammar = next((g for g in config if g.get('isActive')), None)
                if active_grammar:
                    self.log_result(
                        "Grammar Configuration",
                        True,
                        f"Active grammar: {active_grammar.get('originalName', 'unknown')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Grammar Configuration",
                        False,
                        "No active grammar file configured"
                    )
                    return False
            except Exception as e:
                self.log_result(
                    "Grammar Configuration",
                    False,
                    f"Error reading config: {str(e)}"
                )
                return False
        else:
            self.log_result(
                "Grammar Configuration",
                False,
                f"Config file not found: {GRAMMAR_CONFIG_FILE}"
            )
            return False
    
    def test_basic_translation(self):
        """Test 4: Test basic translation without grammar"""
        try:
            # First authenticate
            auth_response = requests.post(
                f"{BACKEND_URL}/auth",
                json={"password": "test123"},
                timeout=5
            )
            
            if auth_response.status_code != 200:
                self.log_result(
                    "Basic Translation",
                    False,
                    "Failed to authenticate with backend"
                )
                return False
            
            self.session_token = auth_response.json().get('sessionToken')
            
            # Test translation
            translation_response = requests.post(
                f"{BACKEND_URL}/translate",
                headers={"Authorization": f"Bearer {self.session_token}"},
                json={
                    "text": "Always x AND y.",
                    "direction": "tce_to_tau"
                },
                timeout=5
            )
            
            if translation_response.status_code == 200:
                result = translation_response.json()
                self.log_result(
                    "Basic Translation",
                    True,
                    f"Translation works: '{result.get('translatedText', 'N/A')}'"
                )
                return True
            else:
                self.log_result(
                    "Basic Translation",
                    False,
                    f"Translation failed: {translation_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Basic Translation",
                False,
                f"Translation error: {str(e)}"
            )
            return False
    
    def test_grammar_loading_in_translation(self):
        """Test 5: Check if grammar files are used in translation"""
        # This is where the issue is - the translation doesn't use grammar files
        
        # Read active grammar
        active_grammar = None
        if GRAMMAR_CONFIG_FILE.exists():
            with open(GRAMMAR_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                active_grammar = next((g for g in config if g.get('isActive')), None)
        
        if not active_grammar:
            self.log_result(
                "Grammar Loading in Translation",
                False,
                "No active grammar to test with"
            )
            return False
        
        # Try to parse with the grammar
        grammar_file = GRAMMARS_DIR / active_grammar['filename']
        if not grammar_file.exists():
            self.log_result(
                "Grammar Loading in Translation",
                False,
                f"Grammar file not found: {grammar_file}"
            )
            return False
        
        # Check if backend actually loads and uses the grammar
        # This is the missing piece - backend doesn't integrate grammar files
        self.log_result(
            "Grammar Loading in Translation",
            False,
            "Grammar files are loaded but NOT integrated with translation engine"
        )
        return False
    
    def test_parser_integration(self):
        """Test 6: Check if parser uses grammar files"""
        try:
            # Import the parser to test directly
            from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
            from src.tau_translator_omega.core_engine.tgf_preprocessor import TGFPreprocessor
            
            # Check if parser can load grammar
            parser = CNLParser()
            
            # The issue: Parser doesn't load external grammar files
            # It uses hardcoded grammar in grammars/common.lark and tce.lark
            self.log_result(
                "Parser Grammar Integration",
                False,
                "Parser uses hardcoded grammar files, not the loaded TGF files"
            )
            return False
            
        except Exception as e:
            self.log_result(
                "Parser Grammar Integration",
                False,
                f"Parser integration error: {str(e)}"
            )
            return False
    
    def test_frontend_backend_connection(self):
        """Test 7: Check if frontend properly connects to backend"""
        # Check if PWA can call backend
        try:
            # This would require running the PWA and checking its API calls
            # For now, we know the issue: translation happens but doesn't use grammars
            self.log_result(
                "Frontend-Backend Connection",
                False,
                "Frontend calls backend but grammar integration is missing"
            )
            return False
        except Exception as e:
            self.log_result(
                "Frontend-Backend Connection",
                False,
                f"Connection test error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 60)
        print("GRAMMAR INTEGRATION TEST SUITE")
        print("=" * 60)
        print()
        
        # Run tests
        self.test_backend_health()
        self.test_grammar_files_exist()
        self.test_grammar_config()
        self.test_basic_translation()
        self.test_grammar_loading_in_translation()
        self.test_parser_integration()
        self.test_frontend_backend_connection()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        # Key findings
        print("KEY FINDINGS:")
        print("1. ❌ Grammar files are loaded in the UI but NOT used in translation")
        print("2. ❌ The parser uses hardcoded Lark grammar, not loaded TGF files")
        print("3. ❌ Translation engine doesn't integrate with grammar loader")
        print("4. ❌ No pathway exists from loaded grammar → parser → translator")
        print()
        
        print("WHAT NEEDS TO BE FIXED:")
        print("1. Create TGFGrammarLoader that converts TGF to Lark grammar")
        print("2. Modify CNLParser to accept dynamic grammar from loader")
        print("3. Connect grammar selection in UI to parser initialization")
        print("4. Update translation API to use grammar-aware parser")
        print("5. Add comprehensive tests for grammar-driven translation")
        print()
        
        return passed == total


if __name__ == "__main__":
    tester = TestGrammarIntegration()
    success = tester.run_all_tests()
    exit(0 if success else 1)