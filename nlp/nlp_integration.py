#!/usr/bin/env python3
"""
NLP Integration Service
=====================

Integrates NLP features with the existing translation system.
Provides enhanced translations, auto-complete, and vocabulary search.
"""

from typing import Dict, List, Any, Optional
from .nlp_vocabulary import TauVocabulary, AutoCompleteEngine, EnhancedEnglishGenerator
from .dictionary_manager import DictionaryManager

class NLPTranslationService:
    """Service that integrates NLP features with translation system"""
    
    def __init__(self):
        """Initialize NLP service with vocabulary and engines"""
        self.dictionary_manager = DictionaryManager()
        self.vocabulary = self.dictionary_manager.get_vocabulary()
        self.autocomplete_engine = AutoCompleteEngine(self.vocabulary)
        self.english_generator = EnhancedEnglishGenerator(self.vocabulary)
    
    def translate_with_variants(self, text: str, source: str, target: str, num_variants: int = 3) -> Dict[str, Any]:
        """
        Translate text and provide multiple natural language variants
        
        Args:
            text: Input text to translate
            source: Source language (TAU, PLAIN_ENGLISH, CNL, ILR)
            target: Target language
            num_variants: Number of variants to generate
        
        Returns:
            Dict with original translation and variants
        """
        # For now, simulate the translation (would integrate with working_backend.py)
        if source == "TAU" and target == "PLAIN_ENGLISH":
            # Simulate TAU -> CNL -> Enhanced English pipeline
            cnl_text = "Define paradox for b as: there exists b such that for all X, barber(b, X)."
            
            # Generate variants using our English generator
            variants = self.english_generator.generate_natural_variants(cnl_text, num_variants)
            
            return {
                "original": cnl_text,
                "variants": variants,
                "source_language": source,
                "target_language": target
            }
        
        # Default fallback
        return {
            "original": f"Translated: {text}",
            "variants": [
                {"text": f"Enhanced version: {text}", "style": "enhanced", "formality": "medium", "confidence": 0.8}
            ],
            "source_language": source,
            "target_language": target
        }
    
    def get_autocomplete_suggestions(self, partial_text: str, max_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        Get auto-complete suggestions for partial text input
        
        Args:
            partial_text: Text typed so far
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggestion dictionaries
        """
        return self.autocomplete_engine.suggest_completions(partial_text, max_suggestions)
    
    def search_vocabulary(self, query: str) -> List[Dict[str, Any]]:
        """
        Search vocabulary for terms related to query
        
        Args:
            query: Search term
            
        Returns:
            List of matching vocabulary entries
        """
        results = []
        query_lower = query.lower()
        
        # Search all vocabulary categories
        for category_name, category in [
            ("logical_operators", self.vocabulary.logical_operators),
            ("quantifiers", self.vocabulary.quantifiers), 
            ("temporal_operators", self.vocabulary.temporal_operators),
            ("predicates", self.vocabulary.predicates)
        ]:
            for key, entry in category.items():
                # Check if query matches key or any variant
                if (query_lower in key.lower() or 
                    any(query_lower in variant.lower() for variant in entry.variants)):
                    results.append({
                        "key": key,
                        "canonical": entry.canonical,
                        "category": category_name,
                        "variants": entry.variants,
                        "context": entry.context,
                        "examples": entry.examples
                    })
        
        return results
    
    def enhance_translation_output(self, cnl_text: str, num_variants: int = 3) -> Dict[str, Any]:
        """
        Enhance CNL output with multiple natural English variants
        
        Args:
            cnl_text: Controlled Natural Language text
            num_variants: Number of variants to generate
            
        Returns:
            Dict with enhanced variants and metadata
        """
        variants = self.english_generator.generate_natural_variants(cnl_text, num_variants)
        
        # Add confidence scores based on variant quality
        for i, variant in enumerate(variants):
            variant["confidence"] = 0.9 - (i * 0.1)  # Decreasing confidence
        
        return {
            "original": cnl_text,
            "variants": variants,
            "enhancement_type": "natural_language_variants"
        }
    
    def refresh_vocabulary(self):
        """Refresh vocabulary from dictionary manager (call after loading new dictionaries)"""
        self.vocabulary = self.dictionary_manager.get_vocabulary()
        self.autocomplete_engine.vocab = self.vocabulary
        self.english_generator.vocab = self.vocabulary

# Export main class
__all__ = ['NLPTranslationService']