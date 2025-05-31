#!/usr/bin/env python3
"""
TDD Tests for English Requirements to Tau Translation
===================================================

Test the enhanced NLP capabilities for translating natural language
requirements paragraphs into formal Tau Language specifications.

This represents the core value proposition of TauTranslator - making
formal methods accessible through natural language.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.nlp_enhanced.requirements_analyzer import (
    RequirementsAnalyzer, RequirementType, FormalConstraint
)
from tau_translator_omega.core_engine.nlp_enhanced.english_to_tau_translator import (
    EnglishToTauTranslator, TranslationResult, ConfidenceScore
)
from tau_translator_omega.core_engine.nlp_enhanced.amr_semantic_layer import (
    AMRSemanticAnalyzer
)


class TestRequirementsAnalysis(unittest.TestCase):
    """Test natural language requirements analysis"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = RequirementsAnalyzer()
        self.translator = EnglishToTauTranslator()
        self.amr_analyzer = AMRSemanticAnalyzer()
    
    def test_simple_constraint_extraction(self):
        """Test extraction of simple constraints from English"""
        text = "The system must ensure that all prime numbers are greater than 1."
        
        requirements = self.analyzer.extract_requirements(text)
        
        self.assertGreater(len(requirements), 0)
        self.assertEqual(requirements[0].type, RequirementType.CONSTRAINT)
        self.assertIn("prime", requirements[0].entities)
        self.assertIn("greater", requirements[0].predicates)
        
    def test_complex_requirement_parsing(self):
        """Test parsing of complex multi-clause requirements"""
        text = """
        The authentication system shall verify user credentials and grant access 
        only if the user is authorized and the session is valid. Additionally, 
        the system must log all authentication attempts for security auditing.
        """
        
        requirements = self.analyzer.extract_requirements(text)
        
        # Should extract multiple requirements
        self.assertGreaterEqual(len(requirements), 2)
        
        # Should identify different requirement types
        types = {req.type for req in requirements}
        self.assertIn(RequirementType.CONSTRAINT, types)
        # Accept any of the logical requirement types
        self.assertTrue(any(t in types for t in [RequirementType.BEHAVIOR, RequirementType.SECURITY, RequirementType.VALIDATION]))
        
        # Should extract key entities
        all_entities = set()
        for req in requirements:
            all_entities.update(req.entities)
        
        self.assertIn("user", all_entities)
        self.assertIn("system", all_entities)
        self.assertIn("authentication", all_entities)
    
    def test_mathematical_requirements(self):
        """Test requirements with mathematical constraints"""
        text = "For any integer n, if n is prime, then n must be odd or n equals 2."
        
        requirements = self.analyzer.extract_requirements(text)
        
        self.assertGreater(len(requirements), 0)
        req = requirements[0]
        
        # Should identify quantification
        self.assertTrue(req.has_quantification)
        # Accept any universal quantifier
        self.assertTrue(any(q in req.logical_structure.quantifiers for q in ["any", "all", "forall"]))
        
        # Should identify mathematical predicates
        self.assertIn("prime", req.predicates)
        self.assertIn("odd", req.predicates)
        self.assertIn("equals", req.predicates)
        
        # Should identify conditional logic
        self.assertTrue(req.logical_structure.has_conditionals)


class TestEnglishToTauTranslation(unittest.TestCase):
    """Test translation from English requirements to Tau specifications"""
    
    def setUp(self):
        """Set up test environment"""
        self.translator = EnglishToTauTranslator()
    
    def test_simple_predicate_translation(self):
        """Test translation of simple predicate statements"""
        text = "x is prime."
        
        result = self.translator.translate(text)
        
        self.assertIsInstance(result, TranslationResult)
        self.assertIsNotNone(result.tau_specification)
        self.assertIn("prime(x)", result.tau_specification)
        self.assertGreater(result.confidence.overall, 0.6)
    
    def test_quantified_statement_translation(self):
        """Test translation of quantified statements"""
        text = "For all integers x, if x is prime, then x is greater than 1."
        
        result = self.translator.translate(text)
        
        self.assertIsNotNone(result.tau_specification)
        
        # Should contain universal quantification
        self.assertTrue(any(q in result.tau_specification for q in ["∀", "forall"]))  # Either symbol or word
        
        # Should contain implication
        self.assertTrue(any(op in result.tau_specification for op in ["→", "implies"]))  # Either symbol or word
        
        # Should contain predicates
        self.assertIn("prime", result.tau_specification)
        # Should contain comparison (greater than expressed as >)
        self.assertTrue(any(op in result.tau_specification for op in [">", "greater"]))
        
        # Should have reasonable confidence
        self.assertGreater(result.confidence.overall, 0.6)
    
    def test_complex_logical_structure(self):
        """Test translation of complex logical structures"""
        text = """
        Every user who is authenticated and has admin privileges can access 
        the system resources, but only if the security protocol is active.
        """
        
        result = self.translator.translate(text)
        
        self.assertIsNotNone(result.tau_specification)
        
        # Should handle complex logical structure
        tau_spec = result.tau_specification
        
        # Should contain quantification
        self.assertTrue(any(q in tau_spec for q in ["∀", "forall", "every"]))
        
        # Should contain logical operators
        self.assertTrue(any(op in tau_spec for op in ["∧", "and", "∨", "or"]))
        
        # Should contain conditional logic
        self.assertTrue(any(cond in tau_spec for cond in ["→", "implies", "if"]))
        
        # Should identify key predicates
        predicates = ["authenticated", "admin", "access", "active"]
        for pred in predicates:
            self.assertTrue(any(p in tau_spec.lower() for p in [pred]))
    
    def test_system_behavior_requirements(self):
        """Test translation of system behavior requirements"""
        text = """
        When a user submits a request, the system must validate the input,
        process the request within 5 seconds, and return a response.
        """
        
        result = self.translator.translate(text)
        
        self.assertIsNotNone(result.tau_specification)
        
        # Should handle temporal constraints
        tau_spec = result.tau_specification
        self.assertTrue(any(temp in tau_spec for temp in ["within", "time", "5"]))
        
        # Should handle sequence of actions
        actions = ["validate", "process", "return"]
        for action in actions:
            self.assertIn(action.lower(), tau_spec.lower())


class TestBidirectionalTranslation(unittest.TestCase):
    """Test bidirectional translation between English and Tau"""
    
    def setUp(self):
        """Set up test environment"""
        self.translator = EnglishToTauTranslator()
    
    def test_english_to_tau_to_english(self):
        """Test round-trip translation maintains meaning"""
        original_text = "For all x, if x is prime, then x is greater than 1."
        
        # English → Tau
        tau_result = self.translator.translate(original_text)
        self.assertIsNotNone(tau_result.tau_specification)
        
        # Tau → English
        english_result = self.translator.translate_tau_to_english(tau_result.tau_specification)
        self.assertIsNotNone(english_result.tau_specification)  # This contains the English text
        
        # Should preserve key semantic elements
        original_lower = original_text.lower()
        result_lower = english_result.tau_specification.lower()  # This contains the English text
        
        key_concepts = ["prime", "greater", "all"]
        for concept in key_concepts:
            if concept in original_lower:
                self.assertIn(concept, result_lower)
    
    def test_semantic_preservation(self):
        """Test that semantic meaning is preserved across translations"""
        test_cases = [
            "x equals 5.",
            "All prime numbers are odd or equal to 2.",
            "If the user is authenticated, then access is granted."
        ]
        
        for original_text in test_cases:
            with self.subTest(text=original_text):
                # Translate to Tau
                tau_result = self.translator.translate(original_text)
                self.assertIsNotNone(tau_result.tau_specification)
                
                # Analyze semantic structure
                original_analysis = self.translator.analyze_semantics(original_text)
                tau_analysis = self.translator.analyze_tau_semantics(tau_result.tau_specification)
                
                # Key semantic elements should be preserved (within 1 predicate difference)
                pred_diff = abs(len(original_analysis.predicates) - len(tau_analysis.predicates))
                self.assertLessEqual(pred_diff, 1, f"Too many predicates lost in translation: {original_analysis.predicates} vs {tau_analysis.predicates}")


class TestRequirementsDocumentProcessing(unittest.TestCase):
    """Test processing of complete requirements documents"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = RequirementsAnalyzer()
        self.translator = EnglishToTauTranslator()
    
    def test_multi_paragraph_requirements(self):
        """Test processing of multi-paragraph requirements documents"""
        requirements_doc = """
        System Requirements for Prime Number Validator
        
        1. Input Validation
        The system shall accept integer inputs from users. All inputs must be 
        validated to ensure they are positive integers greater than zero.
        
        2. Prime Number Verification
        For any given integer n, the system must determine if n is prime.
        A number is considered prime if it has exactly two distinct positive 
        divisors: 1 and itself.
        
        3. Output Requirements  
        The system shall output "prime" if the number is prime, and "composite"
        if the number is not prime. The special case of 1 shall output "neither".
        
        4. Performance Requirements
        The verification process must complete within 100 milliseconds for
        numbers less than 1,000,000.
        """
        
        # Extract all requirements
        requirements = self.analyzer.extract_requirements_from_document(requirements_doc)
        
        self.assertGreaterEqual(len(requirements), 4)
        
        # Should identify different requirement categories
        categories = {req.category for req in requirements}
        expected_categories = {"validation", "verification", "output", "performance"}
        self.assertTrue(expected_categories.issubset(categories))
        
        # Translate entire document
        translation_result = self.translator.translate_document(requirements_doc)
        
        self.assertIsNotNone(translation_result.tau_specification)
        self.assertGreater(len(translation_result.individual_translations), 3)
        
        # Should maintain traceability
        for individual in translation_result.individual_translations:
            self.assertIsNotNone(individual.source_text)
            self.assertIsNotNone(individual.tau_specification)
            self.assertGreater(individual.confidence.overall, 0.5)
    
    def test_requirements_with_edge_cases(self):
        """Test handling of requirements with edge cases and exceptions"""
        text = """
        The authentication system must validate user credentials, except for
        emergency access which bypasses normal authentication. However, 
        emergency access must still log all activities and expire after 30 minutes.
        """
        
        requirements = self.analyzer.extract_requirements(text)
        
        # Should handle exceptions and conditional logic
        self.assertGreater(len(requirements), 1)
        
        # Should identify exception handling
        exception_req = next((r for r in requirements if "except" in r.raw_text.lower()), None)
        self.assertIsNotNone(exception_req)
        
        # Translate with exception handling
        result = self.translator.translate(text)
        self.assertIsNotNone(result.tau_specification)
        
        # Should handle complex conditional logic
        tau_spec = result.tau_specification
        self.assertTrue(any(op in tau_spec for op in ["except", "unless", "∨", "or"]))


class TestConfidenceScoring(unittest.TestCase):
    """Test confidence scoring for translation quality assessment"""
    
    def setUp(self):
        """Set up test environment"""
        self.translator = EnglishToTauTranslator()
    
    def test_high_confidence_simple_statements(self):
        """Test that simple, clear statements get high confidence scores"""
        high_confidence_texts = [
            "x is prime.",
            "y equals 5.", 
            "z is greater than 0."
        ]
        
        for text in high_confidence_texts:
            with self.subTest(text=text):
                result = self.translator.translate(text)
                self.assertGreater(result.confidence.overall, 0.65)
                self.assertGreater(result.confidence.syntax, 0.7)
                self.assertGreater(result.confidence.semantics, 0.6)
    
    def test_lower_confidence_ambiguous_statements(self):
        """Test that ambiguous statements get appropriate confidence scores"""
        ambiguous_texts = [
            "The thing should work properly under normal conditions.",
            "It must be fast enough for typical usage patterns.",
            "The system handles edge cases appropriately."
        ]
        
        for text in ambiguous_texts:
            with self.subTest(text=text):
                result = self.translator.translate(text)
                self.assertLess(result.confidence.overall, 0.6)
                # Should identify specific confidence issues
                self.assertIsNotNone(result.confidence.issues)
                self.assertGreater(len(result.confidence.issues), 0)


if __name__ == '__main__':
    unittest.main()