#!/usr/bin/env python3
"""
TDD Tests for NLP Features
=========================

Test-driven development for:
1. Auto-complete suggestions while typing
2. Enhanced English output variants
3. Vocabulary system integration
4. Context-aware suggestions

These tests define the expected behavior BEFORE implementation.
"""

import unittest
from typing import List, Dict, Any

# Import our NLP classes
from nlp.nlp_vocabulary import TauVocabulary, AutoCompleteEngine, EnhancedEnglishGenerator
from nlp.nlp_integration import NLPTranslationService

class TestAutoCompleteEngine(unittest.TestCase):
    """Test auto-complete functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # This will fail until we implement these classes
        self.vocab = TauVocabulary()
        self.autocomplete = AutoCompleteEngine(self.vocab)
    
    def test_suggest_starter_phrases(self):
        """Test suggestions for empty/beginning input"""
        suggestions = self.autocomplete.suggest_completions("")
        
        # Should suggest common logical starters
        suggestion_texts = [s["text"] for s in suggestions]
        self.assertIn("For all ", suggestion_texts)
        self.assertIn("There exists ", suggestion_texts)
        self.assertIn("If ", suggestion_texts)
        self.assertIn("Define ", suggestion_texts)
        
        # Should have proper metadata
        for suggestion in suggestions:
            self.assertIn("type", suggestion)
            self.assertIn("description", suggestion)
    
    def test_quantifier_completions(self):
        """Test completions after quantifier starts"""
        suggestions = self.autocomplete.suggest_completions("For all x")
        
        # Should suggest "such that" continuation
        suggestion_texts = [s["text"] for s in suggestions]
        self.assertIn("For all x such that ", suggestion_texts)
        self.assertIn("For all x, ", suggestion_texts)
    
    def test_logical_operator_suggestions(self):
        """Test suggestions for logical operators"""
        suggestions = self.autocomplete.suggest_completions("x and")
        
        # Should suggest continuation patterns
        suggestion_texts = [s["text"] for s in suggestions]
        self.assertIn("x and y", suggestion_texts)
        self.assertIn("x and that ", suggestion_texts)
    
    def test_definition_pattern_completions(self):
        """Test completions for definition patterns"""
        suggestions = self.autocomplete.suggest_completions("Define barber")
        
        # Should suggest definition continuations
        suggestion_texts = [s["text"] for s in suggestions]
        any_for_any = any("for any" in text for text in suggestion_texts)
        any_as_case = any("as the case when" in text for text in suggestion_texts)
        
        self.assertTrue(any_for_any or any_as_case, "Should suggest definition patterns")
    
    def test_context_aware_suggestions(self):
        """Test that suggestions are context-aware"""
        # Temporal context
        temporal_suggestions = self.autocomplete.suggest_completions("always")
        temporal_texts = [s["text"] for s in temporal_suggestions]
        
        # Should include temporal operators
        has_temporal = any("eventually" in text or "until" in text for text in temporal_texts)
        self.assertTrue(has_temporal, "Should suggest temporal operators in temporal context")

class TestEnhancedEnglishGenerator(unittest.TestCase):
    """Test enhanced English output generation"""
    
    def setUp(self):
        """Set up test environment"""
        self.vocab = TauVocabulary()
        self.generator = EnhancedEnglishGenerator(self.vocab)
    
    def test_generate_definition_variants(self):
        """Test multiple variants for definition statements"""
        cnl_input = "Define paradox for b as: there exists b such that for all X, barber(b, X)."
        
        variants = self.generator.generate_natural_variants(cnl_input, num_variants=3)
        
        # Should generate multiple variants
        self.assertEqual(len(variants), 3)
        
        # Each variant should have text, style, and formality
        for variant in variants:
            self.assertIn("text", variant)
            self.assertIn("style", variant) 
            self.assertIn("formality", variant)
            self.assertIsInstance(variant["text"], str)
            self.assertGreater(len(variant["text"]), 10)
        
        # Variants should be different from each other
        texts = [v["text"] for v in variants]
        self.assertEqual(len(set(texts)), 3, "All variants should be unique")
        
        # Should have different formality levels
        formalities = [v["formality"] for v in variants]
        self.assertGreater(len(set(formalities)), 1, "Should have different formality levels")
    
    def test_generate_quantifier_variants(self):
        """Test variants for quantifier statements"""
        cnl_input = "For every person, if they work hard then they succeed."
        
        variants = self.generator.generate_natural_variants(cnl_input, num_variants=2)
        
        # Should generate variants
        self.assertGreaterEqual(len(variants), 1)
        
        # Should include alternative phrasings
        variant_texts = [v["text"] for v in variants]
        has_alternative = any("In all cases" in text or "No matter which" in text for text in variant_texts)
        self.assertTrue(has_alternative, "Should provide alternative quantifier phrasings")
    
    def test_formality_levels(self):
        """Test different formality levels in output"""
        cnl_input = "Define success for person as: they achieve their goals."
        
        variants = self.generator.generate_natural_variants(cnl_input, num_variants=3)
        
        # Should have different formality levels
        formalities = [v["formality"] for v in variants]
        self.assertIn("low", formalities, "Should have conversational variant")
        self.assertIn("high", formalities, "Should have formal variant")

class TestVocabularySystem(unittest.TestCase):
    """Test vocabulary system functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.vocab = TauVocabulary()
    
    def test_logical_operators_vocabulary(self):
        """Test logical operators vocabulary"""
        # Should have comprehensive logical operators
        self.assertIn("and", self.vocab.logical_operators)
        self.assertIn("or", self.vocab.logical_operators)
        self.assertIn("implies", self.vocab.logical_operators)
        self.assertIn("not", self.vocab.logical_operators)
        
        # Each entry should have variants
        and_entry = self.vocab.logical_operators["and"]
        self.assertIn("also", and_entry.variants)
        self.assertIn("together with", and_entry.variants)
    
    def test_quantifiers_vocabulary(self):
        """Test quantifiers vocabulary"""
        self.assertIn("forall", self.vocab.quantifiers)
        self.assertIn("exists", self.vocab.quantifiers)
        
        # Should have natural language variants
        forall_entry = self.vocab.quantifiers["forall"] 
        self.assertIn("for every", forall_entry.variants)
        self.assertIn("all", forall_entry.variants)
    
    def test_temporal_operators_vocabulary(self):
        """Test temporal operators vocabulary"""
        self.assertIn("always", self.vocab.temporal_operators)
        self.assertIn("eventually", self.vocab.temporal_operators)
        
        # Should have contextual variants
        always_entry = self.vocab.temporal_operators["always"]
        self.assertIn("constantly", always_entry.variants)
    
    def test_patterns_vocabulary(self):
        """Test pattern templates"""
        self.assertIn("definition", self.vocab.patterns)
        self.assertIn("universal_quantifier", self.vocab.patterns)
        
        # Definition patterns should have placeholders
        def_patterns = self.vocab.patterns["definition"]
        has_placeholders = any("{predicate}" in pattern for pattern in def_patterns)
        self.assertTrue(has_placeholders, "Definition patterns should have placeholders")

class TestNLPIntegration(unittest.TestCase):
    """Test integration with existing translation system"""
    
    def setUp(self):
        """Set up test environment"""
        # This will fail until we create the integration service
        self.nlp_service = NLPTranslationService()
    
    def test_enhanced_tau_to_english_translation(self):
        """Test enhanced translation with NLP variants"""
        tau_input = "paradox(b) := ex b all X barber(b, X)"
        
        result = self.nlp_service.translate_with_variants(
            tau_input, 
            source="TAU", 
            target="PLAIN_ENGLISH",
            num_variants=3
        )
        
        # Should return original translation plus variants
        self.assertIn("original", result)
        self.assertIn("variants", result)
        self.assertEqual(len(result["variants"]), 3)
        
        # Each variant should be different and meaningful
        variants = result["variants"]
        variant_texts = [v["text"] for v in variants]
        self.assertEqual(len(set(variant_texts)), 3, "All variants should be unique")
        
        # Should not contain malformed syntax
        for variant in variants:
            self.assertNotIn("such that=", variant["text"])
            self.assertNotIn("{", variant["text"])  # No JSON artifacts
    
    def test_autocomplete_api_endpoint(self):
        """Test auto-complete API integration"""
        # This tests the API endpoint that will provide suggestions
        suggestions = self.nlp_service.get_autocomplete_suggestions("For all x")
        
        # Should return structured suggestions
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Each suggestion should have required fields
        for suggestion in suggestions:
            self.assertIn("text", suggestion)
            self.assertIn("type", suggestion)
            self.assertIn("description", suggestion)
    
    def test_vocabulary_search(self):
        """Test vocabulary search functionality"""
        # Should be able to search vocabulary
        results = self.nlp_service.search_vocabulary("exists")
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Should find existential quantifier
        has_existential = any("existential" in str(result) for result in results)
        self.assertTrue(has_existential, "Should find existential quantifier")

class TestRealWorldNLPScenarios(unittest.TestCase):
    """Test real-world scenarios with NLP features"""
    
    def test_user_typing_workflow(self):
        """Test complete user typing workflow with suggestions"""
        nlp_service = NLPTranslationService()
        
        # User starts typing
        step1 = nlp_service.get_autocomplete_suggestions("For")
        self.assertGreater(len(step1), 0)
        
        # User continues
        step2 = nlp_service.get_autocomplete_suggestions("For all x")
        self.assertGreater(len(step2), 0)
        
        # User completes
        step3 = nlp_service.get_autocomplete_suggestions("For all x such that")
        self.assertGreater(len(step3), 0)
        
        # Each step should provide relevant suggestions
        step1_texts = [s["text"] for s in step1]
        self.assertTrue(any("For all" in text for text in step1_texts))
    
    def test_translation_enhancement_workflow(self):
        """Test workflow for enhancing translated output"""
        nlp_service = NLPTranslationService()
        
        # Basic CNL output
        cnl_text = "Define paradox for b as: there exists b such that for all X, barber(b, X)."
        
        # Generate enhanced variants
        enhanced = nlp_service.enhance_translation_output(cnl_text)
        
        # Should provide multiple options with different styles
        self.assertIn("variants", enhanced)
        self.assertGreaterEqual(len(enhanced["variants"]), 2)
        
        # Should have metadata for each variant
        for variant in enhanced["variants"]:
            self.assertIn("style", variant)
            self.assertIn("formality", variant)
            self.assertIn("confidence", variant)

def run_failing_tests():
    """Run all tests - they should fail initially"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    print("🔴 TDD RED Phase: Running Failing Tests")
    print("=" * 50)
    print("These tests define the expected NLP functionality.")
    print("They SHOULD fail initially - that's the point of TDD!")
    print("=" * 50)
    
    run_failing_tests()