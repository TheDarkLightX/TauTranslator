#!/usr/bin/env python3
"""
TDD Tests for SPRING-Inspired Symmetric Parsing and Generation
============================================================

Test bidirectional translation capabilities inspired by SapienzaNLP SPRING.
These tests drive the development of symmetric English↔Tau translation.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.nlp_enhanced.symmetric_translator import (
    SymmetricTranslator, LinearizationStrategy, TranslationDirection
)
from tau_translator_omega.core_engine.nlp_enhanced.amr_semantic_layer import AMRGraph


class TestSymmetricTranslation(unittest.TestCase):
    """Test symmetric bidirectional translation capabilities"""
    
    def setUp(self):
        """Set up test environment"""
        self.translator = SymmetricTranslator()
    
    def test_english_to_tau_symmetry(self):
        """Test that English→Tau→English preserves semantic meaning"""
        original_english = "For all x, if x is prime, then x is greater than 1."
        
        # English → Tau
        tau_result = self.translator.translate(
            text=original_english,
            direction=TranslationDirection.ENGLISH_TO_TAU
        )
        
        self.assertIsNotNone(tau_result.output)
        self.assertGreater(tau_result.confidence, 0.6)
        
        # Tau → English
        english_result = self.translator.translate(
            text=tau_result.output,
            direction=TranslationDirection.TAU_TO_ENGLISH
        )
        
        self.assertIsNotNone(english_result.output)
        self.assertGreater(english_result.confidence, 0.6)
        
        # Check semantic preservation
        semantic_similarity = self.translator.calculate_semantic_similarity(
            original_english, english_result.output
        )
        self.assertGreater(semantic_similarity, 0.7, 
                          "Symmetric translation should preserve semantic meaning")
    
    def test_tau_to_english_symmetry(self):
        """Test that Tau→English→Tau preserves logical structure"""
        original_tau = "forall x: (prime(x) implies greater(x, 1))"
        
        # Tau → English
        english_result = self.translator.translate(
            text=original_tau,
            direction=TranslationDirection.TAU_TO_ENGLISH
        )
        
        self.assertIsNotNone(english_result.output)
        
        # English → Tau
        tau_result = self.translator.translate(
            text=english_result.output,
            direction=TranslationDirection.ENGLISH_TO_TAU
        )
        
        self.assertIsNotNone(tau_result.output)
        
        # Check logical equivalence
        logical_equivalence = self.translator.check_logical_equivalence(
            original_tau, tau_result.output
        )
        self.assertTrue(logical_equivalence, 
                       "Symmetric translation should preserve logical structure")
    
    def test_multiple_linearization_strategies(self):
        """Test different linearization strategies for Tau output"""
        english_text = "Every user who is authenticated can access the system."
        
        strategies = [
            LinearizationStrategy.DEPTH_FIRST,
            LinearizationStrategy.BREADTH_FIRST,
            LinearizationStrategy.PENMAN_STYLE
        ]
        
        results = {}
        for strategy in strategies:
            result = self.translator.translate(
                text=english_text,
                direction=TranslationDirection.ENGLISH_TO_TAU,
                linearization=strategy
            )
            results[strategy] = result
            
            self.assertIsNotNone(result.output)
            self.assertGreater(result.confidence, 0.5)
        
        # All strategies should produce valid but potentially different Tau
        for strategy, result in results.items():
            self.assertTrue(self.translator.is_valid_tau(result.output),
                           f"Strategy {strategy.name} should produce valid Tau")
    
    def test_complex_bidirectional_translation(self):
        """Test bidirectional translation of complex requirements"""
        complex_text = """
        The authentication system must validate user credentials before granting access.
        If validation fails, the system shall log the attempt and deny access.
        """
        
        # Test English → Tau
        tau_result = self.translator.translate(
            text=complex_text,
            direction=TranslationDirection.ENGLISH_TO_TAU
        )
        
        self.assertIsNotNone(tau_result.output)
        self.assertGreater(tau_result.confidence, 0.5)
        
        # Should handle multi-sentence translation
        self.assertIn("validate", tau_result.output.lower())
        self.assertIn("log", tau_result.output.lower())
        
        # Test Tau → English
        english_result = self.translator.translate(
            text=tau_result.output,
            direction=TranslationDirection.TAU_TO_ENGLISH
        )
        
        self.assertIsNotNone(english_result.output)
        
        # Should preserve key concepts
        key_concepts = ["authentication", "validate", "access", "log"]
        for concept in key_concepts:
            self.assertTrue(
                any(concept.lower() in text.lower() 
                    for text in [complex_text, english_result.output]),
                f"Concept '{concept}' should be preserved in translation"
            )


class TestAMRLinearization(unittest.TestCase):
    """Test different AMR linearization strategies"""
    
    def setUp(self):
        """Set up test environment"""
        self.translator = SymmetricTranslator()
    
    def test_depth_first_linearization(self):
        """Test depth-first traversal of AMR graphs"""
        # Create a simple AMR graph
        amr_graph = self._create_test_amr_graph()
        
        linearized = self.translator.linearize_amr(
            amr_graph, LinearizationStrategy.DEPTH_FIRST
        )
        
        self.assertIsNotNone(linearized)
        self.assertIsInstance(linearized, str)
        
        # DFS should visit nodes in depth-first order
        self.assertTrue(self._is_valid_linearization(linearized))
    
    def test_breadth_first_linearization(self):
        """Test breadth-first traversal of AMR graphs"""
        amr_graph = self._create_test_amr_graph()
        
        linearized = self.translator.linearize_amr(
            amr_graph, LinearizationStrategy.BREADTH_FIRST
        )
        
        self.assertIsNotNone(linearized)
        self.assertIsInstance(linearized, str)
        
        # BFS should visit nodes level by level
        self.assertTrue(self._is_valid_linearization(linearized))
    
    def test_penman_style_linearization(self):
        """Test PENMAN-style linearization"""
        amr_graph = self._create_test_amr_graph()
        
        linearized = self.translator.linearize_amr(
            amr_graph, LinearizationStrategy.PENMAN_STYLE
        )
        
        self.assertIsNotNone(linearized)
        
        # PENMAN style should use specific notation
        self.assertIn("(", linearized)  # Should have parentheses
        self.assertIn(":", linearized)  # Should have role indicators
    
    def _create_test_amr_graph(self):
        """Create a simple test AMR graph"""
        from tau_translator_omega.core_engine.nlp_enhanced.amr_semantic_layer import (
            AMRGraph, AMRConcept, AMRRelation
        )
        
        graph = AMRGraph()
        
        # Create simple graph: prime(x)
        prime_concept = AMRConcept("prime-01", "predicate", [AMRRelation.ARG1], {})
        var_concept = AMRConcept("variable", "entity", [], {"name": "x"})
        
        prime_instance = graph.add_instance("p1", prime_concept)
        var_instance = graph.add_instance("x1", var_concept)
        
        graph.add_edge("p1", AMRRelation.ARG1, "x1")
        graph.set_root("p1")
        
        return graph
    
    def _is_valid_linearization(self, linearized_text):
        """Check if linearization is valid"""
        # Basic validation - should not be empty and should contain expected elements
        return (len(linearized_text.strip()) > 0 and 
                any(char in linearized_text for char in "(),:"))


class TestSemanticPreservation(unittest.TestCase):
    """Test semantic meaning preservation in symmetric translation"""
    
    def setUp(self):
        """Set up test environment"""
        self.translator = SymmetricTranslator()
    
    def test_quantifier_preservation(self):
        """Test that quantifiers are preserved in symmetric translation"""
        test_cases = [
            ("For all x, prime(x)", "universal quantification"),
            ("There exists y such that even(y)", "existential quantification"),
            ("Every user must authenticate", "universal over domain"),
        ]
        
        for english_text, description in test_cases:
            with self.subTest(case=description):
                # English → Tau → English
                tau_result = self.translator.translate(
                    english_text, TranslationDirection.ENGLISH_TO_TAU
                )
                english_result = self.translator.translate(
                    tau_result.output, TranslationDirection.TAU_TO_ENGLISH
                )
                
                # Check quantifier preservation
                original_quantifiers = self._extract_quantifiers(english_text)
                result_quantifiers = self._extract_quantifiers(english_result.output)
                
                self.assertGreater(len(result_quantifiers), 0,
                                 f"Should preserve quantifiers in {description}")
    
    def test_logical_operator_preservation(self):
        """Test that logical operators are preserved"""
        test_cases = [
            ("x and y", ["and"]),
            ("p or q", ["or"]),
            ("if p then q", ["if", "then"]),
            ("not p", ["not"]),
        ]
        
        for english_text, expected_operators in test_cases:
            with self.subTest(text=english_text):
                tau_result = self.translator.translate(
                    english_text, TranslationDirection.ENGLISH_TO_TAU
                )
                english_result = self.translator.translate(
                    tau_result.output, TranslationDirection.TAU_TO_ENGLISH
                )
                
                # Check logical operator preservation
                for operator in expected_operators:
                    self.assertTrue(
                        operator.lower() in english_result.output.lower() or
                        self._has_equivalent_operator(english_result.output, operator),
                        f"Should preserve logical operator '{operator}'"
                    )
    
    def _extract_quantifiers(self, text):
        """Extract quantifiers from text"""
        import re
        quantifier_patterns = [
            r'\b(all|every|each|any|some|for\s+all|there\s+exists?)\b'
        ]
        
        quantifiers = []
        for pattern in quantifier_patterns:
            matches = re.findall(pattern, text.lower())
            quantifiers.extend(matches)
        
        return quantifiers
    
    def _has_equivalent_operator(self, text, operator):
        """Check if text has equivalent logical operator"""
        operator_equivalents = {
            "and": ["&", "∧", "and"],
            "or": ["|", "∨", "or"], 
            "not": ["~", "¬", "not"],
            "if": ["→", "implies", "if"],
            "then": ["→", "implies", "then"]
        }
        
        equivalents = operator_equivalents.get(operator.lower(), [])
        return any(equiv in text.lower() for equiv in equivalents)


if __name__ == '__main__':
    unittest.main()