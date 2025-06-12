#!/usr/bin/env python3
"""
Test Runner for TCE Parser Test Suite
Runs all unit and integration tests and provides a summary report.

Copyright: DarkLightX / Dana Edwards
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json


class TestRunner:
    """Runs all tests and generates reports."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'unit_tests': {},
            'integration_tests': {},
            'summary': {}
        }
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🧪 TCE PARSER COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Unit tests
        print("📋 Running Unit Tests...")
        print("-" * 70)
        self.run_unit_tests()
        
        # Integration tests
        print("\n📋 Running Integration Tests...")
        print("-" * 70)
        self.run_integration_tests()
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
        
        # Print summary
        self.print_summary()
    
    def run_unit_tests(self):
        """Run all unit tests."""
        unit_test_files = [
            'tests/unit/test_semantic_graph.py',
            'tests/unit/test_scope_manager.py',
            'tests/unit/test_coreference_resolver.py',
            'tests/unit/test_parser_combinators.py',
            'tests/unit/test_enhanced_tce_parser.py',
            'tests/unit/test_declarative_parser.py'
        ]
        
        for test_file in unit_test_files:
            test_path = self.project_root / test_file
            if test_path.exists():
                print(f"\n🔸 Running {test_file}...")
                result = self.run_pytest(test_path)
                self.results['unit_tests'][test_file] = result
            else:
                print(f"⚠️  Test file not found: {test_file}")
                self.results['unit_tests'][test_file] = {
                    'status': 'not_found',
                    'passed': 0,
                    'failed': 0,
                    'skipped': 0
                }
    
    def run_integration_tests(self):
        """Run all integration tests."""
        integration_test_files = [
            'tests/integration/test_complex_translation_pipeline.py',
            'tests/integration/test_bidirectional_translation.py'
        ]
        
        for test_file in integration_test_files:
            test_path = self.project_root / test_file
            if test_path.exists():
                print(f"\n🔸 Running {test_file}...")
                result = self.run_pytest(test_path)
                self.results['integration_tests'][test_file] = result
            else:
                print(f"⚠️  Test file not found: {test_file}")
                self.results['integration_tests'][test_file] = {
                    'status': 'not_found',
                    'passed': 0,
                    'failed': 0,
                    'skipped': 0
                }
    
    def run_pytest(self, test_path):
        """Run pytest on a specific file and capture results."""
        try:
            # Run pytest with JSON output
            cmd = [
                sys.executable, '-m', 'pytest',
                str(test_path),
                '-v',
                '--tb=short',
                '--no-header'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Parse output
            output_lines = result.stdout.strip().split('\n')
            test_results = {
                'status': 'completed',
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'errors': [],
                'duration': 0
            }
            
            # Count results
            for line in output_lines:
                if ' PASSED' in line:
                    test_results['passed'] += 1
                elif ' FAILED' in line:
                    test_results['failed'] += 1
                    test_results['errors'].append(line.strip())
                elif ' SKIPPED' in line:
                    test_results['skipped'] += 1
            
            # Print summary for this file
            total = test_results['passed'] + test_results['failed'] + test_results['skipped']
            if total > 0:
                print(f"   ✅ Passed: {test_results['passed']}")
                print(f"   ❌ Failed: {test_results['failed']}")
                print(f"   ⏭️  Skipped: {test_results['skipped']}")
            else:
                print("   ⚠️  No tests found or pytest error")
                test_results['status'] = 'error'
            
            return test_results
            
        except Exception as e:
            print(f"   💥 Error running tests: {str(e)}")
            return {
                'status': 'error',
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'errors': [str(e)]
            }
    
    def generate_summary(self):
        """Generate test summary statistics."""
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        
        # Count unit tests
        for result in self.results['unit_tests'].values():
            if result['status'] in ['completed', 'error']:
                total_passed += result['passed']
                total_failed += result['failed']
                total_skipped += result['skipped']
        
        # Count integration tests
        for result in self.results['integration_tests'].values():
            if result['status'] in ['completed', 'error']:
                total_passed += result['passed']
                total_failed += result['failed']
                total_skipped += result['skipped']
        
        self.results['summary'] = {
            'total_tests': total_passed + total_failed + total_skipped,
            'passed': total_passed,
            'failed': total_failed,
            'skipped': total_skipped,
            'success_rate': total_passed / (total_passed + total_failed) if (total_passed + total_failed) > 0 else 0
        }
    
    def save_results(self):
        """Save test results to file."""
        results_dir = self.project_root / 'test_results'
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'test_results_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to: {results_file}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        summary = self.results['summary']
        
        print(f"\n🎯 Overall Results:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   ⏭️  Skipped: {summary['skipped']}")
        print(f"   📈 Success Rate: {summary['success_rate']*100:.1f}%")
        
        # Component breakdown
        print(f"\n🔧 Component Test Results:")
        
        print("\n   Unit Tests:")
        for test_file, result in self.results['unit_tests'].items():
            status_icon = "✅" if result['failed'] == 0 else "❌"
            print(f"   {status_icon} {Path(test_file).name}: {result['passed']}/{result['passed'] + result['failed']}")
        
        print("\n   Integration Tests:")
        for test_file, result in self.results['integration_tests'].items():
            status_icon = "✅" if result['failed'] == 0 else "❌"
            print(f"   {status_icon} {Path(test_file).name}: {result['passed']}/{result['passed'] + result['failed']}")
        
        # Final assessment
        print(f"\n🏆 FINAL ASSESSMENT:")
        if summary['success_rate'] >= 0.95:
            print("   ⭐ EXCELLENT: Parser is production-ready!")
        elif summary['success_rate'] >= 0.80:
            print("   ✅ GOOD: Parser works well with minor issues")
        elif summary['success_rate'] >= 0.60:
            print("   🔧 NEEDS WORK: Several components need improvement")
        else:
            print("   ❌ CRITICAL: Major issues need to be addressed")
        
        # Failed tests details
        if summary['failed'] > 0:
            print(f"\n⚠️  Failed Tests Details:")
            for category in ['unit_tests', 'integration_tests']:
                for test_file, result in self.results[category].items():
                    if result['failed'] > 0 and result.get('errors'):
                        print(f"\n   {test_file}:")
                        for error in result['errors'][:3]:  # Show first 3 errors
                            print(f"     - {error}")


def run_quick_validation():
    """Run a quick validation test."""
    print("\n🚀 Quick Validation Test")
    print("-" * 70)
    
    # Test the enhanced parser directly
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend/unified"))
    
    try:
        from enhanced_tce_parser_simple import EnhancedTCEParser
        parser = EnhancedTCEParser()
        
        test_sentences = [
            "all cats are animals",
            "for every person who owns a car, the person must have insurance",
            "always output equals input",
            "if x is greater than 0 then x is positive"
        ]
        
        print("Testing enhanced parser with sample sentences:")
        success_count = 0
        
        for sentence in test_sentences:
            try:
                result = parser.parse(sentence)
                if result and len(result) > len(sentence) * 0.5:
                    print(f"✅ '{sentence}' -> SUCCESS")
                    success_count += 1
                else:
                    print(f"❌ '{sentence}' -> FAILED (trivial output)")
            except Exception as e:
                print(f"❌ '{sentence}' -> ERROR: {str(e)}")
        
        print(f"\nQuick validation: {success_count}/{len(test_sentences)} passed")
        
    except Exception as e:
        print(f"❌ Could not run quick validation: {str(e)}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run TCE Parser Test Suite')
    parser.add_argument('--quick', action='store_true', help='Run quick validation only')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    
    args = parser.parse_args()
    
    if args.quick:
        run_quick_validation()
    else:
        runner = TestRunner()
        
        if args.unit:
            print("Running unit tests only...")
            runner.run_unit_tests()
            runner.generate_summary()
            runner.print_summary()
        elif args.integration:
            print("Running integration tests only...")
            runner.run_integration_tests()
            runner.generate_summary()
            runner.print_summary()
        else:
            runner.run_all_tests()


if __name__ == "__main__":
    main()