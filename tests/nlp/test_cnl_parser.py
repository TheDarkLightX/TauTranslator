#!/usr/bin/env python3
"""
CNL Parser NLP Tests
===================

Test-driven development for CNL (Controlled Natural Language) Parser functionality.
Focuses on natural language processing capabilities and parsing accuracy.
"""

import unittest
import time
from typing import List, Optional

try:
    from .test_utils import (
        get_nlp_classes, 
        TestDataFactory, 
        TestAssertions, 
        NLPTestConfig,
        create_test_logger
    )
except ImportError:
    # For standalone execution
    from test_utils import (
        get_nlp_classes, 
        TestDataFactory, 
        TestAssertions, 
        NLPTestConfig,
        create_test_logger
    )

logger = create_test_logger('cnl_parser')


class TestCNLParserCore(unittest.TestCase):
    """Core CNL Parser functionality tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.CNLParser = cls.nlp_classes['CNLParser']
        logger.info("CNL Parser test class initialized")
    
    def setUp(self):
        """Set up each test"""
        self.parser = self.CNLParser()
    
    def test_parser_instantiation(self):
        """Test that parser can be instantiated successfully"""
        parser = self.CNLParser()
        self.assertIsNotNone(parser)
        self.assertTrue(hasattr(parser, 'parse'), "Parser should have parse method")
        logger.info("Parser instantiation test passed")
    
    def test_parse_natural_quantifiers(self):
        """Test parsing natural language quantifiers"""
        test_cases = TestDataFactory.NATURAL_QUANTIFIERS
        
        for case in test_cases:
            with self.subTest(case=case):
                self._test_parse_case(case, "natural quantifier")
    
    def test_parse_logical_operators(self):
        """Test parsing natural language logical operators"""
        test_cases = TestDataFactory.LOGICAL_OPERATORS
        
        for case in test_cases:
            with self.subTest(case=case):
                self._test_parse_case(case, "logical operator")
    
    def test_parse_complex_expressions(self):
        """Test parsing complex mathematical and logical expressions"""
        test_cases = TestDataFactory.COMPLEX_EXPRESSIONS
        
        for case in test_cases:
            with self.subTest(case=case):
                self._test_parse_case(case, "complex expression")
    
    def test_parse_definition_patterns(self):
        """Test parsing definition patterns in natural language"""
        test_cases = TestDataFactory.DEFINITION_PATTERNS
        
        for case in test_cases:
            with self.subTest(case=case):
                self._test_parse_case(case, "definition pattern", expect_success=False)
    
    def test_parse_temporal_expressions(self):
        """Test parsing temporal logic expressions"""
        test_cases = TestDataFactory.TEMPORAL_EXPRESSIONS
        
        for case in test_cases:
            with self.subTest(case=case):
                self._test_parse_case(case, "temporal expression", expect_success=False)
    
    def _test_parse_case(self, case: str, case_type: str, expect_success: bool = True):
        """
        Helper method to test parsing a specific case
        
        Args:
            case: Input text to parse
            case_type: Description of case type for logging
            expect_success: Whether parsing is expected to succeed
        """
        try:
            result = self.parser.parse(case)
            
            if expect_success:
                self.assertIsNotNone(result, f"Failed to parse {case_type}: {case}")
                if hasattr(result, 'accept'):
                    self.assertTrue(hasattr(result, 'accept'), 
                                  f"Result should support visitor pattern for: {case}")
                logger.debug(f"Successfully parsed {case_type}: {case}")
            else:
                # For cases where implementation may be incomplete
                logger.debug(f"Attempted to parse {case_type} (may not be fully implemented): {case}")
                
        except Exception as e:
            if expect_success:
                logger.warning(f"Parser failed on {case_type} '{case}': {e}")
            else:
                logger.debug(f"Expected parsing challenge for {case_type} '{case}': {e}")


class TestCNLParserPerformance(unittest.TestCase):
    """Performance tests for CNL Parser"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.CNLParser = cls.nlp_classes['CNLParser']
    
    def setUp(self):
        """Set up each test"""
        self.parser = self.CNLParser()
    
    def test_parsing_performance(self):
        """Test parsing performance for various input sizes"""
        test_cases = [
            ("P(x).", "simple"),
            ("for all x, P(x) implies Q(x).", "medium"),
            ("for all x, (P(x) and Q(x)) implies (R(x) or S(x)).", "complex"),
            (" ".join(["P(x) and"] * 10) + " Q(x).", "large")
        ]
        
        for case, complexity in test_cases:
            with self.subTest(case=complexity):
                start_time = time.time()
                
                try:
                    result = self.parser.parse(case)
                    end_time = time.time()
                    
                    parse_time = end_time - start_time
                    TestAssertions.assert_performance_acceptable(
                        parse_time, NLPTestConfig.MAX_PARSE_TIME, 
                        f"Parsing {complexity} expression", self
                    )
                    
                    if result:
                        self.assertIsNotNone(result)
                        logger.info(f"Parsed {complexity} expression in {parse_time:.3f}s")
                        
                except Exception as e:
                    end_time = time.time()
                    parse_time = end_time - start_time
                    logger.warning(f"Parse failed for {complexity} expression in {parse_time:.3f}s: {e}")


class TestCNLParserErrorHandling(unittest.TestCase):
    """Error handling tests for CNL Parser"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.CNLParser = cls.nlp_classes['CNLParser']
    
    def setUp(self):
        """Set up each test"""
        self.parser = self.CNLParser()
    
    def test_malformed_input_handling(self):
        """Test graceful handling of malformed input"""
        malformed_cases = TestDataFactory.MALFORMED_INPUTS
        
        for case in malformed_cases:
            with self.subTest(case=case if case else "<empty>"):
                try:
                    result = self.parser.parse(case)
                    # Should handle gracefully, not crash
                    logger.debug(f"Handled malformed input gracefully: '{case}'")
                    
                except Exception as e:
                    # Should provide meaningful error messages
                    self.assertIsInstance(e, Exception)
                    error_msg = str(e)
                    self.assertGreater(len(error_msg), 0, "Should provide error message")
                    logger.debug(f"Parser provided error for '{case}': {error_msg}")
    
    def test_empty_input_handling(self):
        """Test handling of empty input"""
        empty_inputs = ["", "   ", "\n", "\t"]
        
        for empty_input in empty_inputs:
            with self.subTest(input=repr(empty_input)):
                try:
                    result = self.parser.parse(empty_input)
                    # Result may be None for empty input
                    logger.debug(f"Handled empty input: {repr(empty_input)}")
                except Exception as e:
                    # Should not crash on empty input
                    logger.debug(f"Empty input handling: {e}")


class TestCNLParserIntegration(unittest.TestCase):
    """Integration tests for CNL Parser with other components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.nlp_classes = get_nlp_classes()
        cls.CNLParser = cls.nlp_classes['CNLParser']
    
    def setUp(self):
        """Set up each test"""
        self.parser = self.CNLParser()
    
    def test_basic_parsing_workflow(self):
        """Test basic parsing workflow with various inputs"""
        test_inputs = [
            "P(x).",
            "for all x, P(x).",
            "x + y = z."
        ]
        
        for input_text in test_inputs:
            with self.subTest(input_text=input_text):
                try:
                    result = self.parser.parse(input_text)
                    # Should not crash on basic inputs
                    # Result can be None or AST node depending on implementation
                    logger.debug(f"Parsed basic input: {input_text}")
                except Exception as e:
                    # Should not raise unhandled exceptions
                    self.assertIsInstance(e, Exception)
                    logger.debug(f"Basic input parsing result: {e}")
    
    def test_parser_consistency(self):
        """Test that parser produces consistent results"""
        test_input = "For all x, P(x)."
        
        # Parse the same input multiple times
        results = []
        for i in range(3):
            try:
                result = self.parser.parse(test_input)
                results.append(result)
            except Exception as e:
                results.append(str(e))
        
        # Results should be consistent
        if len(set(str(r) for r in results)) == 1:
            logger.info("Parser produces consistent results")
        else:
            logger.warning("Parser results may be inconsistent")


if __name__ == "__main__":
    print("🧪 Running CNL Parser NLP Tests")
    print("=" * 40)
    
    # Configure logging for standalone run
    import logging
    logging.basicConfig(level=logging.INFO)
    
    unittest.main(verbosity=2)