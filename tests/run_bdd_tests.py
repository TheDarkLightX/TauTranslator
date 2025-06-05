#!/usr/bin/env python3
"""
BDD Test Runner for TauTranslator
=================================

Comprehensive test runner for all BDD scenarios with reporting.
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime


class BDDTestRunner:
    """Runner for BDD tests with comprehensive reporting."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'features': {},
            'summary': {
                'total_features': 0,
                'total_scenarios': 0,
                'passed_scenarios': 0,
                'failed_scenarios': 0,
                'skipped_scenarios': 0,
                'total_steps': 0,
                'duration': 0
            }
        }
    
    def run_all_tests(self):
        """Run all BDD tests and generate report."""
        print("🧪 TAUTRANSLATOR BDD TEST SUITE")
        print("=" * 60)
        print(f"Starting BDD tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        start_time = time.time()
        
        # Find all feature files
        feature_files = list(Path(self.project_root / "tests/features").glob("**/*.feature"))
        self.results['summary']['total_features'] = len(feature_files)
        
        print(f"Found {len(feature_files)} feature files")
        print()
        
        # Run tests for each feature
        for feature_file in feature_files:
            self.run_feature_tests(feature_file)
        
        self.results['summary']['duration'] = time.time() - start_time
        
        # Generate report
        self.generate_report()
        
        # Return exit code based on failures
        return 1 if self.results['summary']['failed_scenarios'] > 0 else 0
    
    def run_feature_tests(self, feature_file):
        """Run tests for a single feature file."""
        relative_path = feature_file.relative_to(self.project_root)
        feature_name = feature_file.stem
        
        print(f"📋 Testing feature: {feature_name}")
        print(f"   File: {relative_path}")
        
        # Run pytest-bdd for this feature
        cmd = [
            sys.executable, '-m', 'pytest',
            '-v',
            '--tb=short',
            '--no-header',
            '-q',
            f'--feature={feature_file}',
            'tests/steps/'  # Directory containing step definitions
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        # Parse results
        feature_results = self.parse_pytest_output(result.stdout, result.stderr)
        feature_results['file'] = str(relative_path)
        feature_results['exit_code'] = result.returncode
        
        self.results['features'][feature_name] = feature_results
        
        # Update summary
        self.results['summary']['total_scenarios'] += feature_results.get('scenarios', 0)
        self.results['summary']['passed_scenarios'] += feature_results.get('passed', 0)
        self.results['summary']['failed_scenarios'] += feature_results.get('failed', 0)
        self.results['summary']['skipped_scenarios'] += feature_results.get('skipped', 0)
        
        # Print summary for this feature
        if feature_results.get('failed', 0) > 0:
            print(f"   ❌ {feature_results['failed']} scenarios failed")
        else:
            print(f"   ✅ All {feature_results.get('passed', 0)} scenarios passed")
        print()
    
    def parse_pytest_output(self, stdout, stderr):
        """Parse pytest output to extract test results."""
        results = {
            'scenarios': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        # Parse summary line (e.g., "5 passed, 2 failed in 1.23s")
        for line in stdout.split('\n'):
            if 'passed' in line or 'failed' in line or 'skipped' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        results['passed'] = int(parts[i-1])
                    elif part == 'failed' and i > 0:
                        results['failed'] = int(parts[i-1])
                    elif part == 'skipped' and i > 0:
                        results['skipped'] = int(parts[i-1])
        
        results['scenarios'] = results['passed'] + results['failed'] + results['skipped']
        
        # Capture errors
        if stderr:
            results['errors'].append(stderr)
        
        return results
    
    def generate_report(self):
        """Generate comprehensive BDD test report."""
        print("\n" + "=" * 60)
        print("📊 BDD TEST REPORT")
        print("=" * 60)
        
        summary = self.results['summary']
        
        # Overall statistics
        print(f"📈 OVERALL STATISTICS:")
        print(f"   • Total Features: {summary['total_features']}")
        print(f"   • Total Scenarios: {summary['total_scenarios']}")
        print(f"   • Passed: {summary['passed_scenarios']} ({self.percentage(summary['passed_scenarios'], summary['total_scenarios'])}%)")
        print(f"   • Failed: {summary['failed_scenarios']} ({self.percentage(summary['failed_scenarios'], summary['total_scenarios'])}%)")
        print(f"   • Skipped: {summary['skipped_scenarios']} ({self.percentage(summary['skipped_scenarios'], summary['total_scenarios'])}%)")
        print(f"   • Duration: {summary['duration']:.2f} seconds")
        print()
        
        # Feature breakdown
        if summary['failed_scenarios'] > 0:
            print("❌ FAILED FEATURES:")
            for feature_name, results in self.results['features'].items():
                if results.get('failed', 0) > 0:
                    print(f"   • {feature_name}: {results['failed']} failed scenarios")
            print()
        
        # Success rate by feature type
        print("📊 SUCCESS RATE BY FEATURE TYPE:")
        feature_types = {}
        
        for feature_name, results in self.results['features'].items():
            # Categorize by feature type (translation, api, parser, etc.)
            feature_type = self.get_feature_type(feature_name)
            if feature_type not in feature_types:
                feature_types[feature_type] = {'passed': 0, 'total': 0}
            
            feature_types[feature_type]['passed'] += results.get('passed', 0)
            feature_types[feature_type]['total'] += results.get('scenarios', 0)
        
        for ftype, stats in sorted(feature_types.items()):
            success_rate = self.percentage(stats['passed'], stats['total'])
            print(f"   • {ftype.capitalize()}: {success_rate}% ({stats['passed']}/{stats['total']})")
        print()
        
        # Quality assessment
        overall_success_rate = self.percentage(summary['passed_scenarios'], summary['total_scenarios'])
        
        print("🎯 BDD COVERAGE ASSESSMENT:")
        if overall_success_rate >= 90:
            print("   🟢 Excellent BDD coverage - Ready for production")
        elif overall_success_rate >= 75:
            print("   🟡 Good BDD coverage - Some scenarios need attention")
        elif overall_success_rate >= 60:
            print("   🟠 Moderate BDD coverage - Significant improvements needed")
        else:
            print("   🔴 Poor BDD coverage - Major work required")
        
        print(f"   Overall Success Rate: {overall_success_rate}%")
        print()
        
        # Save detailed JSON report
        report_file = f"bdd_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📁 Detailed report saved to: {report_file}")
    
    def percentage(self, part, whole):
        """Calculate percentage safely."""
        if whole == 0:
            return 0
        return round((part / whole) * 100, 1)
    
    def get_feature_type(self, feature_name):
        """Determine feature type from name."""
        if 'translation' in feature_name:
            return 'translation'
        elif 'api' in feature_name:
            return 'api'
        elif 'parser' in feature_name:
            return 'parser'
        elif 'semantic' in feature_name:
            return 'semantic'
        elif 'stream' in feature_name:
            return 'streams'
        else:
            return 'other'


def main():
    """Main entry point."""
    runner = BDDTestRunner()
    
    # Check if pytest-bdd is installed
    try:
        import pytest_bdd
    except ImportError:
        print("❌ pytest-bdd not installed!")
        print("Please run: pip install pytest-bdd")
        return 1
    
    # Run tests
    exit_code = runner.run_all_tests()
    
    # Print recommendations
    print("\n💡 RECOMMENDATIONS:")
    if exit_code == 0:
        print("   ✨ All BDD scenarios passing - excellent test coverage!")
        print("   📈 Consider adding more edge case scenarios")
        print("   🔍 Review scenarios for comprehensive business logic coverage")
    else:
        print("   🔧 Fix failing scenarios to improve system reliability")
        print("   📝 Review feature files for clarity and completeness")
        print("   🧪 Ensure step definitions match current implementation")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())