#!/usr/bin/env python3
"""
Comprehensive Qt Integration Test Suite
======================================

Tests the Qt version of TauTranslatorOmega with bidirectional translation.
Includes dependency checking, backend integration, and translation quality tests.
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

class QtIntegrationTester:
    """Comprehensive integration tester for Qt version."""
    
    def __init__(self):
        self.test_results = {
            'dependencies': {},
            'backend_status': {},
            'translation_tests': {},
            'bidirectional_tests': {},
            'performance_tests': {},
            'overall_status': 'UNKNOWN'
        }
        
    def check_dependencies(self):
        """Check all required dependencies."""
        print("🔍 CHECKING DEPENDENCIES")
        print("=" * 50)
        
        dependencies = {
            'PyQt5': self._check_pyqt5,
            'LMQL': self._check_lmql,
            'Backend': self._check_backend,
            'Translator': self._check_translator
        }
        
        for dep_name, check_func in dependencies.items():
            try:
                result = check_func()
                self.test_results['dependencies'][dep_name] = result
                status = "✅" if result['available'] else "❌"
                print(f"{status} {dep_name}: {result['message']}")
            except Exception as e:
                self.test_results['dependencies'][dep_name] = {
                    'available': False,
                    'message': f"Error: {e}"
                }
                print(f"❌ {dep_name}: Error - {e}")
        
        print()
    
    def _check_pyqt5(self):
        """Check PyQt5 availability."""
        try:
            import PyQt5.QtWidgets
            return {'available': True, 'message': 'PyQt5 available'}
        except ImportError:
            return {'available': False, 'message': 'PyQt5 not installed'}
    
    def _check_lmql(self):
        """Check LMQL availability."""
        try:
            import lmql
            return {'available': True, 'message': 'LMQL available'}
        except ImportError:
            return {'available': False, 'message': 'LMQL not installed (fallback mode available)'}
    
    def _check_backend(self):
        """Check if backend is running."""
        try:
            import requests
            response = requests.get('http://127.0.0.1:8000/health', timeout=5)
            if response.status_code == 200:
                return {'available': True, 'message': 'Backend running on port 8000'}
            else:
                return {'available': False, 'message': f'Backend error: HTTP {response.status_code}'}
        except Exception as e:
            return {'available': False, 'message': f'Backend not accessible: {e}'}
    
    def _check_translator(self):
        """Check translator module."""
        try:
            from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
            translator = LMQLBidirectionalTranslator()
            return {'available': True, 'message': f'Translator available (LMQL: {translator.use_lmql})'}
        except Exception as e:
            return {'available': False, 'message': f'Translator error: {e}'}
    
    def install_missing_dependencies(self):
        """Install missing dependencies."""
        print("🔧 INSTALLING MISSING DEPENDENCIES")
        print("=" * 50)
        
        if not self.test_results['dependencies']['PyQt5']['available']:
            print("Installing PyQt5...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'PyQt5'], 
                             check=True, capture_output=True)
                print("✅ PyQt5 installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install PyQt5: {e}")
        
        print()
    
    def run_translation_tests(self):
        """Run comprehensive translation tests."""
        print("🧪 RUNNING TRANSLATION TESTS")
        print("=" * 50)
        
        # Check if translator is available
        if not self.test_results['dependencies']['Translator']['available']:
            print("❌ Translator not available - skipping tests")
            return
        
        try:
            from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
            translator = LMQLBidirectionalTranslator()
            
            test_cases = [
                {
                    'name': 'TCE to Tau - Function Definition',
                    'input': 'define function myFunction as x + y',
                    'direction': 'tce_to_tau',
                    'expected_patterns': ['function_def']
                },
                {
                    'name': 'TCE to Tau - Rule',
                    'input': 'rule: if a then b',
                    'direction': 'tce_to_tau',
                    'expected_patterns': ['rule_def']
                },
                {
                    'name': 'Tau to TCE - Function',
                    'input': 'myFunc() := z * 2',
                    'direction': 'tau_to_tce',
                    'expected_patterns': ['function_def']
                },
                {
                    'name': 'Tau to TCE - Always Statement',
                    'input': 'always x > 5',
                    'direction': 'tau_to_tce',
                    'expected_patterns': ['always_stmt']
                }
            ]
            
            for test_case in test_cases:
                print(f"\n--- {test_case['name']} ---")
                print(f"Input: '{test_case['input']}'")
                
                start_time = time.time()
                
                if test_case['direction'] == 'tce_to_tau':
                    result = translator.translate_tce_to_tau(test_case['input'])
                else:
                    result = translator.translate_tau_to_tce(test_case['input'])
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                print(f"Success: {result.success}")
                print(f"Output: '{result.output}'")
                print(f"Confidence: {result.confidence:.2f}")
                print(f"Patterns: {result.patterns_detected}")
                print(f"Processing Time: {processing_time:.3f}s")
                
                if result.errors:
                    print(f"Errors: {result.errors}")
                if result.warnings:
                    print(f"Warnings: {result.warnings}")
                
                # Store test result
                self.test_results['translation_tests'][test_case['name']] = {
                    'success': result.success,
                    'confidence': result.confidence,
                    'patterns_detected': result.patterns_detected,
                    'processing_time': processing_time,
                    'errors': result.errors,
                    'warnings': result.warnings
                }
                
                print("✅" if result.success else "❌")
        
        except Exception as e:
            print(f"❌ Translation test error: {e}")
        
        print()
    
    def run_bidirectional_tests(self):
        """Test bidirectional translation (round-trip)."""
        print("🔄 RUNNING BIDIRECTIONAL TESTS")
        print("=" * 50)
        
        if not self.test_results['dependencies']['Translator']['available']:
            print("❌ Translator not available - skipping tests")
            return
        
        try:
            from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
            translator = LMQLBidirectionalTranslator()
            
            round_trip_tests = [
                {
                    'name': 'Function Round-trip',
                    'original': 'myFunc() := x + y',
                    'start_format': 'tau'
                },
                {
                    'name': 'Rule Round-trip',
                    'original': 'define function test as a plus b',
                    'start_format': 'tce'
                }
            ]
            
            for test in round_trip_tests:
                print(f"\n--- {test['name']} ---")
                print(f"Original: '{test['original']}'")
                
                try:
                    if test['start_format'] == 'tau':
                        # Tau -> TCE -> Tau
                        step1 = translator.translate_tau_to_tce(test['original'])
                        if step1.success:
                            print(f"Step 1 (Tau->TCE): '{step1.output}'")
                            step2 = translator.translate_tce_to_tau(step1.output)
                            if step2.success:
                                print(f"Step 2 (TCE->Tau): '{step2.output}'")
                                
                                # Compare original and final
                                similarity = self._calculate_similarity(test['original'], step2.output)
                                print(f"Similarity: {similarity:.2f}")
                                
                                self.test_results['bidirectional_tests'][test['name']] = {
                                    'success': True,
                                    'similarity': similarity,
                                    'step1_output': step1.output,
                                    'step2_output': step2.output
                                }
                            else:
                                print(f"❌ Step 2 failed: {step2.errors}")
                        else:
                            print(f"❌ Step 1 failed: {step1.errors}")
                    
                    else:  # start_format == 'tce'
                        # TCE -> Tau -> TCE
                        step1 = translator.translate_tce_to_tau(test['original'])
                        if step1.success:
                            print(f"Step 1 (TCE->Tau): '{step1.output}'")
                            step2 = translator.translate_tau_to_tce(step1.output)
                            if step2.success:
                                print(f"Step 2 (Tau->TCE): '{step2.output}'")
                                
                                similarity = self._calculate_similarity(test['original'], step2.output)
                                print(f"Similarity: {similarity:.2f}")
                                
                                self.test_results['bidirectional_tests'][test['name']] = {
                                    'success': True,
                                    'similarity': similarity,
                                    'step1_output': step1.output,
                                    'step2_output': step2.output
                                }
                            else:
                                print(f"❌ Step 2 failed: {step2.errors}")
                        else:
                            print(f"❌ Step 1 failed: {step1.errors}")
                
                except Exception as e:
                    print(f"❌ Round-trip test error: {e}")
                    self.test_results['bidirectional_tests'][test['name']] = {
                        'success': False,
                        'error': str(e)
                    }
        
        except Exception as e:
            print(f"❌ Bidirectional test setup error: {e}")
        
        print()
    
    def _calculate_similarity(self, text1, text2):
        """Calculate simple similarity between two texts."""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def run_qt_gui_test(self):
        """Test Qt GUI if PyQt5 is available."""
        print("🖥️ TESTING QT GUI")
        print("=" * 50)
        
        if not self.test_results['dependencies']['PyQt5']['available']:
            print("❌ PyQt5 not available - skipping GUI test")
            return
        
        try:
            # Import Qt modules
            from PyQt5.QtWidgets import QApplication
            from src.tau_translator_omega.desktop_gui.main_window import MainWindow, run_test_translations
            
            print("✅ Qt modules imported successfully")
            
            # Create QApplication (required for Qt widgets)
            app = QApplication([])
            
            # Create main window
            window = MainWindow()
            print("✅ Main window created successfully")
            
            # Run automated tests
            print("🔄 Running automated UI tests...")
            run_test_translations(window)
            print("✅ Automated UI tests completed")
            
            # Clean up
            app.quit()
            
            self.test_results['qt_gui'] = {'success': True, 'message': 'Qt GUI tests passed'}
            
        except Exception as e:
            print(f"❌ Qt GUI test error: {e}")
            self.test_results['qt_gui'] = {'success': False, 'error': str(e)}
        
        print()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 50)
        
        # Calculate overall status
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results.items():
            if category == 'overall_status':
                continue
            
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    total_tests += 1
                    if isinstance(result, dict) and result.get('success', result.get('available', False)):
                        passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 80:
            self.test_results['overall_status'] = 'EXCELLENT'
            print("🎉 Status: EXCELLENT - Qt version is fully functional!")
        elif success_rate >= 60:
            self.test_results['overall_status'] = 'GOOD'
            print("✅ Status: GOOD - Qt version is mostly functional")
        elif success_rate >= 40:
            self.test_results['overall_status'] = 'FAIR'
            print("⚠️ Status: FAIR - Qt version has some issues")
        else:
            self.test_results['overall_status'] = 'POOR'
            print("❌ Status: POOR - Qt version needs significant work")
        
        # Save detailed report
        report_file = project_root / 'qt_integration_test_report.json'
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print()
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 STARTING COMPREHENSIVE QT INTEGRATION TESTS")
        print("=" * 60)
        print()
        
        self.check_dependencies()
        self.install_missing_dependencies()
        self.run_translation_tests()
        self.run_bidirectional_tests()
        self.run_qt_gui_test()
        self.generate_report()

def main():
    """Run comprehensive Qt integration tests."""
    tester = QtIntegrationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
