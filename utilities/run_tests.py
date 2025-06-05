#!/usr/bin/env python3
"""
Test Runner for TauTranslatorOmega
==================================

Comprehensive test runner with multiple test modes and reporting.
"""

import sys
import subprocess
import argparse
import shlex
from pathlib import Path

def run_command(cmd, description):
    """Run a command securely without shell injection risk."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        # Convert string command to safe argument list
        if isinstance(cmd, str):
            # Remove multi-line formatting and extra whitespace
            cmd = ' '.join(cmd.split())
            # Use shlex to safely parse the command
            cmd_args = shlex.split(cmd)
        else:
            cmd_args = cmd
        
        result = subprocess.run(cmd_args, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Command execution error: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-benchmark',
        'cryptography'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r test_requirements.txt")
        return False
    
    print("✅ All dependencies available")
    return True

def run_unit_tests():
    """Run unit tests with coverage."""
    cmd = """
    python3 -m pytest test_secure_core.py \
        -v \
        --cov=secure_core \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-fail-under=90 \
        -m "not performance"
    """
    return run_command(cmd, "Running Unit Tests with Coverage")

def run_security_tests():
    """Run security-focused tests."""
    cmd = """
    python3 -m pytest test_secure_core.py::TestSecureStorageSecurityProperties \
        -v \
        --tb=long
    """
    return run_command(cmd, "Running Security Tests")

def run_performance_tests():
    """Run performance benchmarks."""
    cmd = """
    python3 -m pytest test_secure_core.py::TestSecureStoragePerformanceBenchmarks \
        -v \
        --benchmark-only \
        --benchmark-sort=mean \
        --benchmark-columns=min,max,mean,stddev \
        --benchmark-histogram=benchmark_histogram
    """
    return run_command(cmd, "Running Performance Benchmarks")

def run_all_tests():
    """Run all tests including benchmarks."""
    cmd = """
    python3 -m pytest test_secure_core.py \
        -v \
        --cov=secure_core \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --benchmark-skip
    """
    return run_command(cmd, "Running All Tests")

def run_quick_tests():
    """Run quick tests (no benchmarks, basic coverage)."""
    cmd = """
    python3 -m pytest test_secure_core.py \
        -v \
        --tb=short \
        -x \
        -m "not performance"
    """
    return run_command(cmd, "Running Quick Tests")

def run_code_quality_checks():
    """Run code quality checks."""
    print("\n🔍 Running Code Quality Checks...")
    
    # Check if tools are available
    tools = {
        'black': 'python3 -m black --check --diff secure_core.py test_secure_core.py',
        'flake8': 'python3 -m flake8 secure_core.py test_secure_core.py',
        'mypy': 'python3 -m mypy secure_core.py',
        'bandit': 'python3 -m bandit -r secure_core.py'
    }
    
    results = {}
    for tool, cmd in tools.items():
        try:
            # Safely parse command without shell injection risk
            cmd_args = shlex.split(cmd)
            result = subprocess.run(cmd_args, check=True, capture_output=True, text=True)
            results[tool] = True
            print(f"✅ {tool}: PASSED")
        except subprocess.CalledProcessError as e:
            results[tool] = False
            print(f"❌ {tool}: FAILED")
            if e.stdout:
                print(f"   {e.stdout}")
        except FileNotFoundError:
            print(f"⚠️  {tool}: NOT INSTALLED")
        except Exception as e:
            print(f"⚠️  {tool}: ERROR - {e}")
            results[tool] = False
    
    return all(results.values())

def generate_test_report():
    """Generate comprehensive test report."""
    print("\n📊 Generating Test Report...")
    
    # Run tests with detailed reporting
    cmd = """
    python3 -m pytest test_secure_core.py \
        -v \
        --cov=secure_core \
        --cov-report=html:htmlcov \
        --cov-report=xml:coverage.xml \
        --junit-xml=test_results.xml \
        --benchmark-skip
    """
    
    if run_command(cmd, "Generating Test Report"):
        print("\n📋 Test Report Generated:")
        print("  📄 HTML Coverage: htmlcov/index.html")
        print("  📄 XML Coverage: coverage.xml")
        print("  📄 JUnit Results: test_results.xml")
        return True
    return False

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="TauTranslatorOmega Test Runner")
    parser.add_argument('--mode', choices=[
        'quick', 'unit', 'security', 'performance', 'all', 'quality', 'report'
    ], default='unit', help='Test mode to run')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies only')
    
    args = parser.parse_args()
    
    print("🧪 TauTranslatorOmega Test Runner")
    print("=" * 40)
    
    # Check dependencies first
    if not check_dependencies():
        if args.check_deps:
            return 1
        print("\n⚠️  Some dependencies missing, but continuing...")
    
    if args.check_deps:
        return 0
    
    # Run selected test mode
    success = True
    
    if args.mode == 'quick':
        success = run_quick_tests()
    elif args.mode == 'unit':
        success = run_unit_tests()
    elif args.mode == 'security':
        success = run_security_tests()
    elif args.mode == 'performance':
        success = run_performance_tests()
    elif args.mode == 'all':
        success = run_all_tests()
    elif args.mode == 'quality':
        success = run_code_quality_checks()
    elif args.mode == 'report':
        success = generate_test_report()
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("✅ Tests completed successfully!")
    else:
        print("❌ Some tests failed!")
    print(f"{'='*60}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
