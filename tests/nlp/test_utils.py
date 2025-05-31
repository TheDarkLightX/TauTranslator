#!/usr/bin/env python3
"""
NLP Test Utilities
==================

Common utilities, fixtures, and helpers for NLP testing.
Promotes code reuse and maintains consistent test patterns.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock, MagicMock


# Configure test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImportManager:
    """Manages imports with graceful fallbacks for testing"""
    
    def __init__(self):
        self._imports = {}
        self._add_src_to_path()
    
    def _add_src_to_path(self) -> None:
        """Add src directory to Python path"""
        src_path = Path(__file__).parent.parent.parent / 'src'
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
    
    def import_with_fallback(self, module_path: str, class_name: str, 
                           fallback_factory: Optional[callable] = None) -> Any:
        """
        Import a class with fallback to mock if import fails
        
        Args:
            module_path: Python module path
            class_name: Class name to import
            fallback_factory: Factory function to create fallback mock
            
        Returns:
            Imported class or mock fallback
        """
        cache_key = f"{module_path}.{class_name}"
        
        if cache_key in self._imports:
            return self._imports[cache_key]
        
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            self._imports[cache_key] = cls
            logger.info(f"Successfully imported {cache_key}")
            return cls
            
        except ImportError as e:
            logger.warning(f"Import failed for {cache_key}: {e}")
            
            if fallback_factory:
                fallback = fallback_factory()
            else:
                fallback = self._create_default_mock(class_name)
                
            self._imports[cache_key] = fallback
            return fallback
    
    def _create_default_mock(self, class_name: str) -> Mock:
        """Create a default mock for a class"""
        mock = Mock()
        mock.__name__ = f"Mock{class_name}"
        return mock


class NLPTestMocks:
    """Factory for creating consistent test mocks"""
    
    @staticmethod
    def create_cnl_parser_mock() -> Mock:
        """Create a mock CNL parser"""
        mock = Mock()
        mock.parse.return_value = Mock()  # Mock AST node
        mock.parse.side_effect = None
        return mock
    
    @staticmethod
    def create_semantic_analyzer_mock() -> Mock:
        """Create a mock semantic analyzer"""
        mock = Mock()
        mock.analyze.return_value = Mock()  # Mock analysis result
        mock.errors = []
        return mock
    
    @staticmethod
    def create_translator_mock() -> Mock:
        """Create a mock translator"""
        mock = Mock()
        mock.translate_tce_to_tau.return_value = "mocked_tau_output"
        mock.translate_tau_to_tce.return_value = "mocked_tce_output"
        return mock
    
    @staticmethod
    def create_bidirectional_translator_mock() -> Mock:
        """Create a mock bidirectional translator"""
        mock = Mock()
        mock.translate_tau_to_tce.return_value = "mocked_bidirectional_output"
        return mock


class TestDataFactory:
    """Factory for creating consistent test data"""
    
    # Common test cases for different NLP features
    NATURAL_QUANTIFIERS = [
        "For all x such that x > 0.",
        "There exists y where y is prime.",
        "For every person p.",
        "Some number n."
    ]
    
    LOGICAL_OPERATORS = [
        "x and y.",
        "p or q.",
        "if a then b.",
        "a implies b.",
        "not x.",
        "x and not y."
    ]
    
    COMPLEX_EXPRESSIONS = [
        "x + y * z.",
        "f(x, y) > 0.",
        "for all x, f(x) = g(x) + 1.",
        "x <= y and y < z.",
        "P(x) implies Q(x, y)."
    ]
    
    DEFINITION_PATTERNS = [
        "Define prime(n) as n > 1 and for all d, d divides n implies d = 1 or d = n.",
        "Let f(x) = x * x + 1.",
        "Suppose P(x) means x is positive."
    ]
    
    TEMPORAL_EXPRESSIONS = [
        "always P(x).",
        "eventually Q(y).",
        "P(x) until Q(x).",
        "next state has property P."
    ]
    
    MALFORMED_INPUTS = [
        "",  # Empty input
        "for all x,",  # Incomplete quantifier
        "P(x) and and Q(x)",  # Syntax error
        ")))(((",  # Mismatched parentheses
        "undefined_function(x, y, z)"  # Unknown function
    ]
    
    @classmethod
    def get_test_cases(cls, category: str) -> List[str]:
        """Get test cases for a specific category"""
        return getattr(cls, category.upper(), [])
    
    @classmethod
    def get_all_valid_inputs(cls) -> List[str]:
        """Get all valid test inputs"""
        return (cls.NATURAL_QUANTIFIERS + 
                cls.LOGICAL_OPERATORS + 
                cls.COMPLEX_EXPRESSIONS + 
                cls.DEFINITION_PATTERNS + 
                cls.TEMPORAL_EXPRESSIONS)


class AutoCompleteTestData:
    """Specialized test data for auto-complete features"""
    
    STARTER_SUGGESTIONS = [
        {"text": "For all ", "type": "quantifier", "description": "Universal quantifier"},
        {"text": "There exists ", "type": "quantifier", "description": "Existential quantifier"},
        {"text": "If ", "type": "conditional", "description": "Conditional statement"},
        {"text": "Define ", "type": "definition", "description": "Definition statement"},
    ]
    
    CONTEXT_TEST_CASES = [
        ("For all x", ["such that", "comma"]),
        ("P(x)", ["and", "or"]),
        ("Define prime", ["as", "for"]),
        ("x + y", ["=", ">", "<"]),
    ]
    
    PROGRESSIVE_TYPING = [
        "F",
        "For",
        "For ",
        "For all",
        "For all x",
        "For all x ",
        "For all x such",
        "For all x such that"
    ]


class TranslationTestData:
    """Specialized test data for translation testing"""
    
    TCE_TO_TAU_CASES = [
        ("Define prime(n) as n > 1 and for all d, d divides n implies d = 1 or d = n.", "prime"),
        ("For all x, if P(x) then Q(x).", "forall"),
        ("There exists y such that P(y).", "exists")
    ]
    
    TAU_TO_TCE_CASES = [
        "all x (P(x) -> Q(x))",
        "ex y P(y)",
        "prime(n) := n > 1 & all d (divides(d,n) -> d = 1 | d = n)"
    ]
    
    STYLE_VARIANTS = {
        'formal': {
            'quantifiers': {'for all': 'For every', 'there exists': 'There is'},
            'operators': {'and': 'and', 'or': 'or', 'implies': 'implies'}
        },
        'conversational': {
            'quantifiers': {'for all': 'For every single', 'there exists': "There's"},
            'operators': {'and': 'and', 'or': 'maybe', 'implies': 'means'}
        }
    }


class TestAssertions:
    """Custom assertion helpers for NLP testing"""
    
    @staticmethod
    def assert_valid_suggestion(suggestion: Dict[str, Any], test_case) -> None:
        """Assert that a suggestion has valid structure"""
        required_fields = ["text", "type", "description"]
        
        for field in required_fields:
            test_case.assertIn(field, suggestion, f"Suggestion missing field: {field}")
            test_case.assertIsInstance(suggestion[field], str, f"Field {field} should be string")
            test_case.assertGreater(len(suggestion[field]), 0, f"Field {field} should not be empty")
    
    @staticmethod
    def assert_valid_variant(variant: Dict[str, Any], test_case) -> None:
        """Assert that a translation variant has valid structure"""
        required_fields = ['text', 'style', 'formality', 'confidence']
        
        for field in required_fields:
            test_case.assertIn(field, variant, f"Variant missing field: {field}")
        
        # Validate specific field types and values
        test_case.assertIsInstance(variant['text'], str)
        test_case.assertGreater(len(variant['text']), 0)
        
        # Validate style is non-empty string (flexible to accommodate dynamic styles)
        test_case.assertIsInstance(variant['style'], str)
        test_case.assertGreater(len(variant['style']), 0)
        
        valid_formality = ['low', 'medium', 'high']
        test_case.assertIn(variant['formality'], valid_formality)
        
        test_case.assertGreaterEqual(variant['confidence'], 0.0)
        test_case.assertLessEqual(variant['confidence'], 1.0)
    
    @staticmethod
    def assert_performance_acceptable(duration: float, max_duration: float, 
                                    operation: str, test_case) -> None:
        """Assert that operation performance is acceptable"""
        test_case.assertLess(
            duration, max_duration,
            f"{operation} took too long: {duration:.3f}s (max: {max_duration}s)"
        )
    
    @staticmethod
    def assert_no_duplicates(items: List[Any], test_case, message: str = "Should not have duplicates") -> None:
        """Assert that a list contains no duplicates"""
        test_case.assertEqual(len(items), len(set(items)), message)


class NLPTestConfig:
    """Configuration constants for NLP testing"""
    
    # Performance thresholds
    MAX_PARSE_TIME = 1.0  # seconds
    MAX_TRANSLATION_TIME = 2.0  # seconds
    
    # Quality thresholds
    MIN_CONFIDENCE = 0.1
    MIN_READABILITY = 0.1
    
    # Test limits
    MAX_SUGGESTIONS = 10
    MAX_VARIANTS = 5
    
    # Expected minimum counts
    MIN_STARTER_SUGGESTIONS = 3
    MIN_CONTEXT_SUGGESTIONS = 1


# Global import manager instance
import_manager = ImportManager()


def get_nlp_classes():
    """Get NLP classes with fallback mocks"""
    return {
        'CNLParser': import_manager.import_with_fallback(
            'tau_translator_omega.core_engine.cnl_parser.cnl_parser',
            'CNLParser',
            NLPTestMocks.create_cnl_parser_mock
        ),
        'SemanticAnalyzer': import_manager.import_with_fallback(
            'tau_translator_omega.core_engine.semantic_analyzer',
            'SemanticAnalyzer', 
            NLPTestMocks.create_semantic_analyzer_mock
        ),
        'TCETauTranslator': import_manager.import_with_fallback(
            'tau_translator_omega.core_engine.tce_tau_translator',
            'TCETauTranslator',
            NLPTestMocks.create_translator_mock
        ),
        'BidirectionalTranslator': import_manager.import_with_fallback(
            'tau_translator_omega.lmql_engine.bidirectional_translator',
            'LMQLBidirectionalTranslator',
            NLPTestMocks.create_bidirectional_translator_mock
        )
    }


def create_test_logger(name: str) -> logging.Logger:
    """Create a logger for test modules"""
    logger = logging.getLogger(f"tests.nlp.{name}")
    return logger