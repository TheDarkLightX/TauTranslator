#!/usr/bin/env python3
"""
TDD Fix for Quantified Constraints Issue
======================================
Targeted tests to fix the specific failure in complex quantified statements.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tau_translator_omega.core_engine.translators.nlp_enhanced.english_to_tau_translator import EnglishToTauTranslator
from tau_translator_omega.core_engine.translators.nlp_enhanced.requirements_analyzer import RequirementsAnalyzer


class TestQuantifiedConstraintsFix(unittest.TestCase):
    """Fix the specific quantified constraints issue found in complex testing"""
    
    def setUp(self):
        """Set up test environment"""
        self.translator = EnglishToTauTranslator()
        self.analyzer = RequirementsAnalyzer()
    
    def test_failing_quantified_constraint(self):
        """Test the exact failing case from complex requirements"""
        text = "For every transaction above $10,000, all approvers in the chain must digitally sign within their respective authority limits before processing."
        
        result = self.translator.translate(text)
        
        # Should extract predicates even from complex sentences
        self.assertGreater(len(result.semantic_analysis.predicates), 0, 
                          "Should extract predicates from quantified constraints")
        
        # Should extract entities even from complex sentences
        self.assertGreater(len(result.semantic_analysis.entities), 0,
                          "Should extract entities from quantified constraints")
        
        # Should have reasonable confidence
        self.assertGreater(result.confidence.overall, 0.6,
                          "Should have confidence > 60% for clear quantified statements")
        
        # Should identify quantification
        self.assertGreater(len(result.semantic_analysis.quantifiers), 0,
                          "Should identify quantifiers like 'every' and 'all'")
    
    def test_complex_entity_extraction(self):
        """Test entity extraction for financial/technical terms"""
        text = "For every transaction above $10,000, all approvers must sign."
        
        semantic_analysis = self.translator.analyze_semantics(text)
        
        # Should extract financial entities
        entities = [e.lower() for e in semantic_analysis.entities]
        self.assertIn("transaction", entities)
        
        # Should extract role-based entities
        self.assertTrue(any("approv" in e for e in entities), 
                       "Should extract 'approvers' or similar")
    
    def test_complex_predicate_extraction(self):
        """Test predicate extraction for action verbs in complex sentences"""
        text = "All approvers must digitally sign within authority limits before processing."
        
        semantic_analysis = self.translator.analyze_semantics(text)
        
        # Should extract action predicates
        predicates = [p.lower() for p in semantic_analysis.predicates]
        self.assertTrue(any("sign" in p for p in predicates),
                       "Should extract signing action")
        
        # Should extract process predicates
        self.assertTrue(any("process" in p for p in predicates),
                       "Should extract processing action")
    
    def test_improved_quantifier_detection(self):
        """Test improved quantifier detection for complex patterns"""
        test_cases = [
            ("For every transaction", ["every"]),
            ("All approvers in the chain", ["all"]), 
            ("Each user with admin rights", ["each"]),
            ("Any request exceeding limits", ["any"]),
            ("Every single validation step", ["every"])
        ]
        
        for text, expected_quantifiers in test_cases:
            with self.subTest(text=text):
                semantic_analysis = self.translator.analyze_semantics(text)
                found_quantifiers = [q.lower() for q in semantic_analysis.quantifiers]
                
                for expected in expected_quantifiers:
                    self.assertIn(expected, found_quantifiers,
                                f"Should find quantifier '{expected}' in '{text}'")


class TestComplexTermExtraction(unittest.TestCase):
    """Test extraction of complex technical and domain-specific terms"""
    
    def setUp(self):
        """Set up test environment"""
        self.translator = EnglishToTauTranslator()
    
    def test_financial_terms(self):
        """Test extraction of financial domain terms"""
        text = "Portfolio exposure must not exceed leverage ratio limits during volatile market conditions."
        
        semantic_analysis = self.translator.analyze_semantics(text)
        
        # Should extract financial entities
        entities = [e.lower() for e in semantic_analysis.entities]
        financial_terms = ["portfolio", "exposure", "leverage", "ratio", "market"]
        
        found_terms = sum(1 for term in financial_terms if any(term in e for e in entities))
        self.assertGreater(found_terms, 2, "Should extract multiple financial terms")
    
    def test_technical_terms(self):
        """Test extraction of technical domain terms"""
        text = "Cryptographic algorithms must implement key derivation with proper entropy."
        
        semantic_analysis = self.translator.analyze_semantics(text)
        
        # Should extract technical entities
        entities = [e.lower() for e in semantic_analysis.entities]
        technical_terms = ["cryptographic", "algorithm", "key", "derivation", "entropy"]
        
        found_terms = sum(1 for term in technical_terms if any(term in e for e in entities))
        self.assertGreater(found_terms, 2, "Should extract multiple technical terms")
    
    def test_medical_terms(self):
        """Test extraction of medical domain terms"""
        text = "Cardiac monitoring devices must detect arrhythmia patterns with high accuracy."
        
        semantic_analysis = self.translator.analyze_semantics(text)
        
        # Should extract medical entities
        entities = [e.lower() for e in semantic_analysis.entities]
        medical_terms = ["cardiac", "monitoring", "device", "arrhythmia", "accuracy"]
        
        found_terms = sum(1 for term in medical_terms if any(term in e for e in entities))
        self.assertGreater(found_terms, 2, "Should extract multiple medical terms")


if __name__ == '__main__':
    unittest.main()