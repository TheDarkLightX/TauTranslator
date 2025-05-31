"""
NLP Testing Package
==================

Comprehensive test suite for Natural Language Processing features in TauTranslator.
"""

from .test_utils import (
    ImportManager,
    NLPTestMocks,
    TestDataFactory,
    AutoCompleteTestData,
    TranslationTestData,
    TestAssertions,
    NLPTestConfig,
    get_nlp_classes,
    create_test_logger
)

__all__ = [
    'ImportManager',
    'NLPTestMocks', 
    'TestDataFactory',
    'AutoCompleteTestData',
    'TranslationTestData',
    'TestAssertions',
    'NLPTestConfig',
    'get_nlp_classes',
    'create_test_logger'
]