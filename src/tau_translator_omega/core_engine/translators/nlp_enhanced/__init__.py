"""
Enhanced NLP Module for TauTranslator
===================================

State-of-the-art natural language processing capabilities for Tau Controlled English.

Features:
- Abstract Meaning Representation (AMR) semantic analysis
- Incremental parsing with caching
- Neural constituency parsing integration
- Coreference resolution
- Template-guided neural parsing
- Neuro-symbolic reasoning integration

This module implements cutting-edge NLP algorithms based on academic research
to enhance the natural language understanding capabilities of TauTranslator.
"""

from .amr_semantic_layer import (
    AMRSemanticAnalyzer,
    AMRGraph,
    AMRConcept,
    AMRRelation,
    enhance_semantic_analysis
)

from .incremental_parser import (
    IncrementalTCEParser,
    IncrementalParseCache,
    TextDiffer,
    create_incremental_parser
)

from .requirements_analyzer import (
    RequirementsAnalyzer,
    RequirementType,
    RequirementItem,
    FormalConstraint,
    LogicalStructure,
    create_requirements_analyzer
)

from .english_to_tau_translator import (
    EnglishToTauTranslator,
    TranslationResult,
    DocumentTranslationResult,
    ConfidenceScore,
    SemanticAnalysis,
    create_english_to_tau_translator
)

from .symmetric_translator import (
    SymmetricTranslator,
    SymmetricTranslationResult,
    TranslationDirection,
    LinearizationStrategy,
    create_symmetric_translator
)

__all__ = [
    'AMRSemanticAnalyzer',
    'AMRGraph', 
    'AMRConcept',
    'AMRRelation',
    'enhance_semantic_analysis',
    'IncrementalTCEParser',
    'IncrementalParseCache',
    'TextDiffer',
    'create_incremental_parser',
    'RequirementsAnalyzer',
    'RequirementType', 
    'RequirementItem',
    'FormalConstraint',
    'LogicalStructure',
    'create_requirements_analyzer',
    'EnglishToTauTranslator',
    'TranslationResult',
    'DocumentTranslationResult',
    'ConfidenceScore',
    'SemanticAnalysis',
    'create_english_to_tau_translator',
    'SymmetricTranslator',
    'SymmetricTranslationResult',
    'TranslationDirection',
    'LinearizationStrategy',
    'create_symmetric_translator'
]