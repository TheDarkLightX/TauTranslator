"""
Pure functions for text feature extraction.

This module contains functions to analyze input text and extract
various linguistic and structural features relevant for parsing.

Copyright (c) DarkLightX / Dana Edwards
"""

import re
import numpy as np
from typing import List

from .neural_types import ParseFeatures # Assuming neural_types.py is in the same directory

def extract_parsing_features(text: str) -> ParseFeatures:
    """Extract features from input text."""
    words = text.split()
    
    return ParseFeatures(
        word_count=len(words),
        has_quantifier=has_quantifier_words(text),
        has_temporal=has_temporal_words(text),
        has_modal=has_modal_words(text),
        has_causal=has_causal_words(text),
        avg_word_length=calculate_avg_word_length(words),
        sentence_complexity=calculate_sentence_complexity(text),
        pattern_confidence=calculate_pattern_confidence(text),
        semantic_consistency=calculate_semantic_consistency(text)
    )

def has_quantifier_words(text: str) -> bool:
    """Check if text has quantifier words."""
    quantifiers = {'all', 'every', 'some', 'many', 'few', 'most', 'several', 'each'}
    return any(word in text.lower() for word in quantifiers)

def has_temporal_words(text: str) -> bool:
    """Check if text has temporal words."""
    temporal = {'when', 'while', 'before', 'after', 'during', 'until', 'since'}
    return any(word in text.lower() for word in temporal)

def has_modal_words(text: str) -> bool:
    """Check if text has modal words."""
    modals = {'must', 'should', 'can', 'may', 'might', 'could', 'ought', 'will', 'would'}
    return any(word in text.lower() for word in modals)

def has_causal_words(text: str) -> bool:
    """Check if text has causal words."""
    causal = {'causes', 'leads to', 'results in', 'because', 'since', 'therefore', 'thus'}
    return any(phrase in text.lower() for phrase in causal)

def calculate_avg_word_length(words: List[str]) -> float:
    """Calculate average word length."""
    if not words:
        return 0.0
    return sum(len(word) for word in words) / len(words)

def calculate_sentence_complexity(text: str) -> float:
    """Calculate sentence complexity score."""
    complexity_indicators = [
        len(text.split()),  # Word count
        text.count(','),    # Comma count
        text.count('('),    # Parentheses
        text.count('and') + text.count('or'),  # Conjunctions
    ]
    return sum(complexity_indicators) / 100.0  # Normalize

def calculate_pattern_confidence(text: str) -> float:
    """Calculate pattern matching confidence."""
    # Simple heuristic based on structure
    has_subject_verb = bool(re.search(r'\w+\s+(is|are|was|were|has|have)\s+\w+', text))
    has_clear_structure = bool(re.search(r'^(all|every|some|if|when)\s+', text, re.IGNORECASE))
    
    confidence = 0.5  # Base confidence
    if has_subject_verb:
        confidence += 0.2
    if has_clear_structure:
        confidence += 0.3
    
    return min(confidence, 1.0)

def calculate_semantic_consistency(text: str) -> float:
    """Calculate semantic consistency score."""
    # Simple consistency checks
    inconsistency_patterns = [
        r'car.*thinks',
        r'house.*runs',
        r'book.*drives',
        r'system.*sleeps'
    ]
    
    inconsistencies = sum(1 for pattern in inconsistency_patterns 
                         if re.search(pattern, text, re.IGNORECASE))
    
    return max(0.0, 1.0 - (inconsistencies * 0.3))

def features_to_vector(features: ParseFeatures) -> np.ndarray:
    """Convert features to numpy vector."""
    return np.array([
        features.word_count / 20.0,  # Normalize
        float(features.has_quantifier),
        float(features.has_temporal),
        float(features.has_modal),
        float(features.has_causal),
        features.avg_word_length / 10.0,
        features.sentence_complexity,
        features.pattern_confidence,
        features.semantic_consistency
    ])
