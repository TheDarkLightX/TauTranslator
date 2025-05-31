#!/usr/bin/env python3
"""
Comprehensive TDD Tests for NLP Features (Legacy Compatibility)
==============================================================

This module provides backward compatibility with the old test structure.
New tests should use the refactored modules in tests/nlp/ directory.

For comprehensive NLP testing, use:
    python3 -m tests.nlp.test_nlp_comprehensive
"""

import sys
import warnings
from pathlib import Path

# Ensure nlp test package is importable
nlp_test_path = Path(__file__).parent / 'nlp'
if str(nlp_test_path) not in sys.path:
    sys.path.insert(0, str(nlp_test_path))

# Issue deprecation warning
warnings.warn(
    "This test module is deprecated. Use 'python3 -m tests.nlp.test_nlp_comprehensive' for comprehensive NLP testing.",
    DeprecationWarning,
    stacklevel=2
)

# Import from refactored test suite
try:
    from nlp.test_nlp_comprehensive import run_comprehensive_tests, NLPTestSuite
    
    def main():
        """Legacy main function - redirects to new test suite"""
        print("🔄 Redirecting to refactored NLP test suite...")
        print("=" * 60)
        
        success = run_comprehensive_tests(verbosity=2)
        
        if success:
            print("\n✅ All tests completed successfully!")
        else:
            print("\n❌ Some tests failed. See output above for details.")
        
        return success
    
except ImportError as e:
    print(f"Error importing refactored test suite: {e}")
    print("Falling back to minimal compatibility mode...")
    
    def main():
        print("❌ Refactored test suite not available")
        print("Please ensure tests/nlp/ directory contains the refactored tests")
        return False


if __name__ == "__main__":
    print("🧪 Running Comprehensive NLP Feature Tests")
    print("=" * 60)
    print("Testing TauTranslator's natural language processing capabilities...")
    print("=" * 60)
    
    main()