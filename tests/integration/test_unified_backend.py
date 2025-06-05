"""
Test script for the unified TauTranslator backend.

Tests the consolidation of all backend functionality into a single service.

Author: DarkLightX / Dana Edwards
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import json
from typing import Dict, Any
import time


class UnifiedBackendTester:
    """Test the unified backend functionality."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session_token = None
    
    def test_health_endpoints(self) -> Dict[str, Any]:
        """Test all health check endpoints."""
        print("🔍 Testing Health Endpoints...")
        results = {}
        
        # Basic health check
        try:
            response = requests.get(f"{self.base_url}/health/")
            results['basic_health'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results['basic_health'] = {'success': False, 'error': str(e)}
        
        # Detailed health check
        try:
            response = requests.get(f"{self.base_url}/health/detailed")
            results['detailed_health'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results['detailed_health'] = {'success': False, 'error': str(e)}
        
        # Engines status
        try:
            response = requests.get(f"{self.base_url}/health/engines")
            results['engines_status'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results['engines_status'] = {'success': False, 'error': str(e)}
        
        return results
    
    def test_translation_endpoints(self) -> Dict[str, Any]:
        """Test translation functionality."""
        print("🔄 Testing Translation Endpoints...")
        results = {}
        
        # Test basic translation
        test_cases = [
            {
                'name': 'basic_to_tau',
                'data': {
                    'sourceText': 'adder equals i1 plus i2',
                    'direction': 'to_tau'
                }
            },
            {
                'name': 'basic_to_tce',
                'data': {
                    'sourceText': 'adder := i1 + i2',
                    'direction': 'to_tce'
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/translate/",
                    json=test_case['data']
                )
                results[test_case['name']] = {
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'response': response.json() if response.status_code == 200 else response.text
                }
            except Exception as e:
                results[test_case['name']] = {'success': False, 'error': str(e)}
        
        # Test engines list
        try:
            response = requests.get(f"{self.base_url}/api/translate/engines")
            results['engines_list'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results['engines_list'] = {'success': False, 'error': str(e)}
        
        # Test validation
        try:
            response = requests.post(
                f"{self.base_url}/api/translate/validate",
                json={'sourceText': 'test input', 'direction': 'to_tau'}
            )
            results['validation'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results['validation'] = {'success': False, 'error': str(e)}
        
        return results
    
    def test_authentication(self) -> Dict[str, Any]:
        """Test authentication endpoints."""
        print("🔐 Testing Authentication...")
        results = {}
        
        # Test auth status
        try:
            response = requests.get(f"{self.base_url}/auth/status")
            results['auth_status'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results['auth_status'] = {'success': False, 'error': str(e)}
        
        # Test login (will fail without master password, but that's expected)
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={'password': 'test_password'}
            )
            results['login_attempt'] = {
                'status_code': response.status_code,
                'success': response.status_code in [200, 401, 501],  # 401/501 expected without proper setup
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except Exception as e:
            results['login_attempt'] = {'success': False, 'error': str(e)}
        
        return results
    
    def test_legacy_compatibility(self) -> Dict[str, Any]:
        """Test legacy endpoint compatibility."""
        print("🔙 Testing Legacy Compatibility...")
        results = {}
        
        # Test legacy /translate endpoint
        try:
            response = requests.post(
                f"{self.base_url}/translate",
                json={'text': 'test legacy translation'}
            )
            results['legacy_translate'] = {
                'status_code': response.status_code,
                'success': response.status_code in [200, 422],  # 422 expected for simple test
                'response': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results['legacy_translate'] = {'success': False, 'error': str(e)}
        
        return results
    
    def test_system_info(self) -> Dict[str, Any]:
        """Test system information endpoints."""
        print("ℹ️ Testing System Info...")
        results = {}
        
        # Test root endpoint
        try:
            response = requests.get(f"{self.base_url}/")
            results['root'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results['root'] = {'success': False, 'error': str(e)}
        
        # Test system info
        try:
            response = requests.get(f"{self.base_url}/system/info")
            results['system_info'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results['system_info'] = {'success': False, 'error': str(e)}
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return consolidated results."""
        print("🚀 Starting Unified Backend Tests...")
        print(f"Testing backend at: {self.base_url}")
        print("-" * 50)
        
        all_results = {}
        
        # Run test suites
        all_results['health'] = self.test_health_endpoints()
        all_results['translation'] = self.test_translation_endpoints()
        all_results['authentication'] = self.test_authentication()
        all_results['legacy'] = self.test_legacy_compatibility()
        all_results['system'] = self.test_system_info()
        
        return all_results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a summary of test results."""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in results.items():
            print(f"\n{category.upper()}:")
            for test_name, result in tests.items():
                total_tests += 1
                if result.get('success', False):
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                
                print(f"  {test_name}: {status}")
                
                if not result.get('success', False) and 'error' in result:
                    print(f"    Error: {result['error']}")
        
        print(f"\n📈 OVERALL: {passed_tests}/{total_tests} tests passed")
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Unified backend is working well!")
        elif success_rate >= 60:
            print("⚠️ Unified backend has some issues but is mostly functional")
        else:
            print("🚨 Unified backend needs significant fixes")


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the unified TauTranslator backend")
    parser.add_argument("--url", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--save-results", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    tester = UnifiedBackendTester(args.url)
    
    try:
        results = tester.run_all_tests()
        tester.print_summary(results)
        
        if args.save_results:
            with open(args.save_results, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📁 Results saved to: {args.save_results}")
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to backend at {args.url}")
        print("Make sure the unified backend is running:")
        print("  python backend/unified/server.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()