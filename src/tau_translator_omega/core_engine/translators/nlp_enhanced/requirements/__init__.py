"""
Requirements analysis module.

This module provides comprehensive natural language requirements analysis
following the Intentional Disclosure Principle.

Copyright: DarkLightX / Dana Edwards
"""

from .domain_types import (
    RequirementText, SentenceText, SectionTitle, SectionContent,
    EntityName, PredicateName, ConfidenceScore, LogicalFormula,
    RequirementType, LogicalStructure, FormalConstraint, RequirementItem
)

from .pattern_repository import PatternRepository
from .nlp_processor import SpacyNLPProcessor
from .analyzers import (
    DocumentSplitter, RequirementClassifier, LogicalAnalyzer,
    ConstraintExtractor, ConfidenceCalculator, SectionCategorizer
)
from .service import RequirementAnalysisService

__all__ = [
    # Domain types
    'RequirementText', 'SentenceText', 'SectionTitle', 'SectionContent',
    'EntityName', 'PredicateName', 'ConfidenceScore', 'LogicalFormula',
    'RequirementType', 'LogicalStructure', 'FormalConstraint', 'RequirementItem',
    
    # Infrastructure
    'PatternRepository', 'SpacyNLPProcessor',
    
    # Business logic
    'DocumentSplitter', 'RequirementClassifier', 'LogicalAnalyzer',
    'ConstraintExtractor', 'ConfidenceCalculator', 'SectionCategorizer',
    
    # Service
    'RequirementAnalysisService'
]