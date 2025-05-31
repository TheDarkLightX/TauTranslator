#!/usr/bin/env python3
"""
Comprehensive NLP Test Suite
============================

High-quality, refactored test suite for all NLP features in TauTranslator.
Combines all NLP tests with proper organization, logging, and quality standards.
"""

import unittest
import logging
import sys
from pathlib import Path

# Import all test modules
from .test_cnl_parser import (
    TestCNLParserCore,
    TestCNLParserPerformance, 
    TestCNLParserErrorHandling,
    TestCNLParserIntegration
)
from .test_autocomplete import (
    TestAutoCompleteBasics,
    TestAutoCompleteAdvanced,
    TestAutoCompleteIntegration
)
from .test_translation_variants import (
    TestTranslationVariantGeneration,
    TestTranslationEnhancement,
    TestQualityMetrics
)

from .test_utils import create_test_logger, NLPTestConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = create_test_logger('comprehensive')


class NLPTestSuite:
    """
    Comprehensive test suite manager for NLP features.
    Provides organized test execution with detailed reporting.
    """
    
    def __init__(self):
        """Initialize the test suite"""
        self.test_modules = {
            'CNL Parser': [
                TestCNLParserCore,
                TestCNLParserPerformance,
                TestCNLParserErrorHandling,
                TestCNLParserIntegration
            ],
            'Auto-Complete': [
                TestAutoCompleteBasics,
                TestAutoCompleteAdvanced,
                TestAutoCompleteIntegration
            ],
            'Translation Variants': [
                TestTranslationVariantGeneration,
                TestTranslationEnhancement,
                TestQualityMetrics
            ]
        }
        
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'module_results': {}
        }
    
    def run_all_tests(self, verbosity: int = 2) -> unittest.TestResult:
        """
        Run all NLP tests with comprehensive reporting.
        
        Args:
            verbosity: Test output verbosity level
            
        Returns:
            Combined test results
        """
        logger.info("Starting comprehensive NLP test suite")
        logger.info("=" * 60)
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add all test classes
        for module_name, test_classes in self.test_modules.items():
            logger.info(f"Loading {module_name} tests...")
            
            module_suite = unittest.TestSuite()
            for test_class in test_classes:
                class_suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
                module_suite.addTest(class_suite)
            
            suite.addTest(module_suite)
            logger.info(f"  Loaded {module_suite.countTestCases()} tests from {module_name}")
        
        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=verbosity,
            stream=sys.stdout,
            buffer=True
        )
        
        logger.info(f"Running {suite.countTestCases()} total tests...")
        logger.info("=" * 60)
        
        result = runner.run(suite)
        
        # Log results summary
        self._log_results_summary(result)
        
        return result
    
    def run_module_tests(self, module_name: str, verbosity: int = 2) -> unittest.TestResult:
        """
        Run tests for a specific module.
        
        Args:
            module_name: Name of module to test ('CNL Parser', 'Auto-Complete', etc.)
            verbosity: Test output verbosity level
            
        Returns:
            Test results for the module
        """
        if module_name not in self.test_modules:
            raise ValueError(f"Unknown module: {module_name}")
        
        logger.info(f"Running {module_name} tests")
        logger.info("=" * 40)
        
        # Create suite for module
        suite = unittest.TestSuite()
        for test_class in self.test_modules[module_name]:
            class_suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTest(class_suite)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
        result = runner.run(suite)
        
        logger.info(f"{module_name} tests completed")
        return result
    
    def _log_results_summary(self, result: unittest.TestResult) -> None:
        """Log comprehensive test results summary"""
        logger.info("=" * 60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        total_tests = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
        passed = total_tests - failures - errors - skipped
        
        logger.info(f"Total Tests Run: {total_tests}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failures}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Skipped: {skipped}")
        
        if total_tests > 0:
            success_rate = (passed / total_tests) * 100
            logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Log failure details
        if result.failures:
            logger.warning(f"\nFAILURE DETAILS ({len(result.failures)} failures):")
            for test, traceback in result.failures:
                logger.warning(f"  FAIL: {test}")
                logger.debug(f"    {traceback}")
        
        # Log error details
        if result.errors:
            logger.error(f"\nERROR DETAILS ({len(result.errors)} errors):")
            for test, traceback in result.errors:
                logger.error(f"  ERROR: {test}")
                logger.debug(f"    {traceback}")
        
        # Overall assessment
        if failures == 0 and errors == 0:
            logger.info("\n✅ ALL TESTS PASSED!")
        elif passed > failures + errors:
            logger.info(f"\n⚠️  MOSTLY PASSING ({passed} passed, {failures + errors} failed)")
        else:
            logger.warning(f"\n❌ SIGNIFICANT ISSUES ({failures + errors} failed, {passed} passed)")
        
        logger.info("=" * 60)


class TestNLPConfiguration(unittest.TestCase):
    """Test NLP test configuration and setup"""
    
    def test_test_configuration(self):
        """Test that test configuration is properly set up"""
        # Verify configuration constants
        self.assertGreater(NLPTestConfig.MAX_PARSE_TIME, 0)
        self.assertGreater(NLPTestConfig.MAX_TRANSLATION_TIME, 0)
        self.assertGreaterEqual(NLPTestConfig.MIN_CONFIDENCE, 0.0)
        self.assertLessEqual(NLPTestConfig.MIN_CONFIDENCE, 1.0)
        
        logger.info("Test configuration validation passed")
    
    def test_test_utilities_available(self):
        """Test that test utilities are properly imported"""
        from .test_utils import (
            ImportManager, NLPTestMocks, TestDataFactory,
            AutoCompleteTestData, TranslationTestData, TestAssertions
        )
        
        # Test that utilities can be instantiated
        import_manager = ImportManager()
        self.assertIsNotNone(import_manager)
        
        test_data = TestDataFactory()
        self.assertIsNotNone(test_data)
        
        logger.info("Test utilities validation passed")


def run_comprehensive_tests(module_filter: str = None, verbosity: int = 2) -> bool:
    """
    Run comprehensive NLP tests with optional filtering.
    
    Args:
        module_filter: Optional module name to filter tests
        verbosity: Test output verbosity level
        
    Returns:
        True if all tests passed, False otherwise
    """
    suite_manager = NLPTestSuite()
    
    try:
        if module_filter:
            result = suite_manager.run_module_tests(module_filter, verbosity)
        else:
            result = suite_manager.run_all_tests(verbosity)
        
        # Return success status
        return len(result.failures) == 0 and len(result.errors) == 0
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return False


def main():
    """Main entry point for comprehensive test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run comprehensive NLP tests for TauTranslator"
    )
    parser.add_argument(
        '--module', '-m',
        choices=['CNL Parser', 'Auto-Complete', 'Translation Variants'],
        help='Run tests for specific module only'
    )
    parser.add_argument(
        '--verbosity', '-v',
        type=int, choices=[0, 1, 2],
        default=2,
        help='Test output verbosity level'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print header
    print("🧪 TauTranslator NLP Test Suite")
    print("=" * 50)
    print("High-quality, comprehensive testing for NLP features")
    print("=" * 50)
    
    # Run tests
    success = run_comprehensive_tests(args.module, args.verbosity)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()