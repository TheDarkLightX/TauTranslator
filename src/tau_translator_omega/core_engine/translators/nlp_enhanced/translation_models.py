"""
Data Models for the NLP Enhanced Translation System
=================================================

This module defines the core data structures used throughout the nlp_enhanced
translation pipeline. These classes ensure that data is passed between components
in a consistent and predictable manner.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict

from .amr_semantic_layer import AMRGraph

@dataclass
class ConfidenceScore:
    """Detailed confidence scoring for translations"""
    overall: float
    syntax: float
    semantics: float
    logical_structure: float
    mathematical: float
    issues: List[str]


@dataclass
class SemanticAnalysis:
    """Semantic analysis results"""
    predicates: List[str]
    entities: List[str]
    quantifiers: List[str]
    logical_operators: List[str]
    temporal_expressions: List[str]


@dataclass
class TranslationResult:
    """Result of English to Tau translation"""
    source_text: str
    tau_specification: str
    confidence: ConfidenceScore
    semantic_analysis: SemanticAnalysis
    amr_graph: Optional[AMRGraph] = None
    translation_notes: List[str] = None


@dataclass
class DocumentTranslationResult:
    """Result of translating an entire document"""
    source_document: str
    tau_specification: str
    individual_translations: List[TranslationResult]
    overall_confidence: float
    traceability_map: Dict[str, str]
