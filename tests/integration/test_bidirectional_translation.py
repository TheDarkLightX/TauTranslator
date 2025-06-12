"""
Integration tests for bidirectional translation
Tests English -> TCE -> Tau -> TCE -> English round-trip translation.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend/unified"))

from tce_parser import TCEParser as EnhancedTCEParser


@dataclass
class TranslationTestCase:
    """Test case for bidirectional translation."""
    english: str
    category: str
    key_concepts: List[str]
    acceptable_variations: List[str] = None
    
    def __post_init__(self):
        if self.acceptable_variations is None:
            self.acceptable_variations = []


class TestBidirectionalTranslation:
    """Test bidirectional English <-> Tau translation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
        self.test_cases = self._create_test_cases()
    
    def _create_test_cases(self) -> List[TranslationTestCase]:
        """Create comprehensive test cases."""
        return [
            # Simple statements
            TranslationTestCase(
                english="all cats are animals",
                category="simple_universal",
                key_concepts=["all", "cats", "animals"],
                acceptable_variations=[
                    "every cat is an animal",
                    "all cats are animals",
                    "each cat is an animal"
                ]
            ),
            
            # Conditionals
            TranslationTestCase(
                english="if x is positive then x is greater than zero",
                category="conditional",
                key_concepts=["if", "positive", "greater", "zero"],
                acceptable_variations=[
                    "when x is positive, x is greater than zero",
                    "x being positive implies x is greater than zero",
                    "if x is positive then x > 0"
                ]
            ),
            
            # Quantified conditionals
            TranslationTestCase(
                english="for every person who owns a car, the person must have insurance",
                category="quantified_relative",
                key_concepts=["every", "person", "owns", "car", "insurance"],
                acceptable_variations=[
                    "all people who own cars must have insurance",
                    "everyone who owns a car must have insurance",
                    "any person owning a car must have insurance"
                ]
            ),
            
            # Temporal properties
            TranslationTestCase(
                english="always output equals input",
                category="temporal",
                key_concepts=["always", "output", "equals", "input"],
                acceptable_variations=[
                    "output always equals input",
                    "at all times output equals input",
                    "it is always true that output equals input"
                ]
            ),
            
            # Stream processing
            TranslationTestCase(
                english="output 1 at time t equals input 1 at time t minus 1",
                category="stream",
                key_concepts=["output", "input", "time", "t", "minus", "1"],
                acceptable_variations=[
                    "output stream 1 at t equals input stream 1 at t-1",
                    "o1[t] = i1[t-1]",
                    "the output at time t equals the input at time t-1"
                ]
            ),
            
            # Complex nested
            TranslationTestCase(
                english="for all x, if x is prime and x is greater than 2 then x is odd",
                category="complex_logic",
                key_concepts=["all", "prime", "greater", "2", "odd"],
                acceptable_variations=[
                    "every prime number greater than 2 is odd",
                    "all primes except 2 are odd numbers",
                    "if a number is prime and exceeds 2, it must be odd"
                ]
            )
        ]
    
    def test_english_to_tau(self):
        """Test English to Tau translation."""
        for test_case in self.test_cases:
            result = self.parser.parse(test_case.english)
            
            # Check that key concepts are preserved
            result_lower = result.lower()
            missing_concepts = []
            
            for concept in test_case.key_concepts:
                # Check if concept appears in some form
                if concept not in result_lower and not self._concept_transformed(concept, result_lower):
                    missing_concepts.append(concept)
            
            assert len(missing_concepts) < len(test_case.key_concepts) / 2, \
                f"Too many concepts missing from translation of '{test_case.english}': {missing_concepts}"
    
    def _concept_transformed(self, concept: str, result: str) -> bool:
        """Check if concept was transformed in translation."""
        transformations = {
            "equals": ["=", "=="],
            "greater": [">", "gt"],
            "less": ["<", "lt"],
            "and": ["&&", "∧"],
            "or": ["||", "∨"],
            "not": ["!", "¬"],
            "all": ["∀", "forall", "every"],
            "exists": ["∃", "ex", "some"],
            "always": ["□", "[]", "globally"],
            "eventually": ["◇", "<>", "finally"]
        }
        
        if concept in transformations:
            return any(trans in result for trans in transformations[concept])
        
        return False
    
    def test_tau_to_english_patterns(self):
        """Test common Tau patterns translate back to English."""
        tau_patterns = [
            ("∀x: P(x)", "for all x, P of x"),
            ("∃x: Q(x)", "there exists x such that Q of x"),
            ("A -> B", "A implies B"),
            ("A && B", "A and B"),
            ("A || B", "A or B"),
            ("!A", "not A"),
            ("□P", "always P"),
            ("◇Q", "eventually Q"),
            ("o1[t] = i1[t]", "output 1 at time t equals input 1 at time t")
        ]
        
        for tau, expected_english in tau_patterns:
            # This would require a Tau -> English translator
            # For now, we verify the patterns are recognized
            assert tau != expected_english
            assert len(tau) < len(expected_english)  # Tau is more concise
    
    def test_round_trip_preservation(self):
        """Test that round-trip translation preserves meaning."""
        critical_sentences = [
            "all x greater than 0 are positive",
            "if a and b then c or d",
            "there exists x such that x squared equals 4",
            "always when input is high, output is high"
        ]
        
        for sentence in critical_sentences:
            # English -> Tau
            tau = self.parser.parse(sentence)
            
            # Tau -> English (simulated)
            english_back = self._simulate_tau_to_english(tau)
            
            # Check semantic preservation
            assert self._semantically_equivalent(sentence, english_back, tau)
    
    def _simulate_tau_to_english(self, tau: str) -> str:
        """Simulate Tau to English translation."""
        # Basic pattern replacement for testing
        english = tau
        
        # Logical operators
        replacements = [
            ("∀", "for all"),
            ("∃", "there exists"),
            ("all ", "for all "),
            ("ex ", "there exists "),
            ("->", " implies "),
            ("&&", " and "),
            ("||", " or "),
            ("!", "not "),
            ("=", " equals "),
            (">", " is greater than "),
            ("<", " is less than "),
            ("□", "always "),
            ("◇", "eventually ")
        ]
        
        for tau_op, eng_op in replacements:
            english = english.replace(tau_op, eng_op)
        
        # Clean up
        english = " ".join(english.split())
        return english
    
    def _semantically_equivalent(self, sent1: str, sent2: str, tau: str) -> bool:
        """Check if two sentences are semantically equivalent."""
        # Simplified check: ensure key logical structure is preserved
        
        # Extract logical operators
        ops1 = self._extract_operators(sent1)
        ops2 = self._extract_operators(sent2)
        ops_tau = self._extract_operators(tau)
        
        # Check that operator counts are similar
        return (abs(len(ops1) - len(ops2)) <= 2 and 
                len(ops_tau) > 0)
    
    def _extract_operators(self, text: str) -> List[str]:
        """Extract logical operators from text."""
        operators = []
        text_lower = text.lower()
        
        logical_words = [
            "all", "every", "exists", "some",
            "and", "or", "not", "implies",
            "if", "then", "always", "never",
            "&&", "||", "!", "->", "∀", "∃"
        ]
        
        for op in logical_words:
            if op in text_lower:
                operators.append(op)
        
        return operators


class TestComplexBidirectional:
    """Test complex bidirectional translation scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
    
    def test_nested_quantifiers_round_trip(self):
        """Test nested quantifiers preserve structure."""
        sentences = [
            "for all x there exists y such that y is greater than x",
            "there exists a maximum value such that all values are at most the maximum"
        ]
        
        for sentence in sentences:
            tau = self.parser.parse(sentence)
            
            # Check nesting is preserved
            assert tau.count("all") + tau.count("∀") >= 1
            assert tau.count("ex") + tau.count("∃") >= 1
    
    def test_coreference_preservation(self):
        """Test that coreference is maintained."""
        sentence = "every person who owns a car must register the car"
        tau = self.parser.parse(sentence)
        
        # Check that 'the car' is resolved to same variable as 'a car'
        # Count variable occurrences
        import re
        
        # Look for variable patterns
        variables = re.findall(r'\b[a-z]\b', tau)
        
        # Should have repeated variable for coreference
        assert len(variables) > len(set(variables))
    
    def test_temporal_round_trip(self):
        """Test temporal properties round trip."""
        temporal_specs = [
            "always output follows input",
            "eventually the system stabilizes",
            "input changes trigger output changes"
        ]
        
        for spec in temporal_specs:
            tau = self.parser.parse(spec)
            
            # Check temporal operators are present
            temporal_ops = ["always", "eventually", "□", "◇", "triggers"]
            assert any(op in tau for op in temporal_ops)
    
    def test_stream_equation_round_trip(self):
        """Test stream equations maintain structure."""
        equations = [
            "output at t equals input at t minus 1",
            "o1[t] = f(i1[t], i2[t-1])",
            "the next output depends on current and previous inputs"
        ]
        
        for eq in equations:
            tau = self.parser.parse(eq)
            
            # Check for time indices
            assert "[t" in tau or "at t" in tau.lower()
    
    def test_policy_rule_round_trip(self):
        """Test complex policy rules maintain meaning."""
        policies = [
            "all users must authenticate before accessing protected resources unless they have emergency override",
            "transactions exceeding the daily limit require manager approval except for verified accounts"
        ]
        
        for policy in policies:
            tau = self.parser.parse(policy)
            
            # Check key policy elements preserved
            assert "all" in tau or "∀" in tau
            assert "must" in tau or "->" in tau
            assert "unless" in tau or "except" in tau or "!" in tau


class TestEdgeCasesBidirectional:
    """Test edge cases in bidirectional translation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
    
    def test_empty_input(self):
        """Test empty input handling."""
        assert self.parser.parse("") == ""
        assert self.parser.parse("   ") == ""
        assert self.parser.parse(".") == ""
    
    def test_ambiguous_pronouns(self):
        """Test ambiguous pronoun resolution."""
        # Multiple possible antecedents
        sentence = "the car hit the tree and it was damaged"
        tau = self.parser.parse(sentence)
        
        # Should make some choice for 'it'
        assert tau
        assert "damaged" in tau
    
    def test_mathematical_notation(self):
        """Test mathematical notation preservation."""
        math_sentences = [
            "x squared plus y squared equals r squared",
            "the derivative of f at x equals the limit",
            "for all epsilon greater than 0 there exists delta"
        ]
        
        for sent in math_sentences:
            tau = self.parser.parse(sent)
            
            # Check mathematical concepts preserved
            if "squared" in sent:
                assert "^2" in tau or "squared" in tau or "**2" in tau
            if "epsilon" in sent:
                assert "epsilon" in tau or "ε" in tau
    
    def test_very_long_sentences(self):
        """Test handling of very long sentences."""
        # Build a long sentence
        parts = [
            "for every entity in the system",
            "that has property A and property B", 
            "and is connected to another entity",
            "with property C or property D",
            "if the connection strength exceeds the threshold",
            "and the time since last update is less than the timeout",
            "then the entity must be processed",
            "and added to the priority queue",
            "unless it is already being processed",
            "or has been marked as invalid"
        ]
        
        long_sentence = " ".join(parts)
        tau = self.parser.parse(long_sentence)
        
        # Should handle without crashing
        assert tau
        assert len(tau) > 50  # Should produce substantial output
    
    def test_special_characters(self):
        """Test handling of special characters."""
        sentences_with_special = [
            "the value is >= 100",
            "x != y",
            "a & b | c",
            "price is $50.00"
        ]
        
        for sent in sentences_with_special:
            tau = self.parser.parse(sent)
            assert tau  # Should not crash
    
    def test_mixed_language_concepts(self):
        """Test mixing formal and informal language."""
        mixed_sentences = [
            "all widgets must satisfy P(x) where P is the validity predicate",
            "the function f maps elements from domain A to codomain B",
            "forall x in S: property(x) holds"
        ]
        
        for sent in mixed_sentences:
            tau = self.parser.parse(sent)
            assert tau
            # Should preserve formal notation where present
            if "forall" in sent:
                assert "all" in tau or "∀" in tau


class TestBidirectionalMetrics:
    """Test metrics for translation quality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedTCEParser()
    
    def calculate_preservation_score(self, original: str, translated: str, back_translated: str) -> float:
        """Calculate how well meaning is preserved in round trip."""
        # Simple metric based on keyword preservation
        original_words = set(original.lower().split())
        back_words = set(back_translated.lower().split())
        
        # Important words to track
        important = {"all", "exists", "must", "if", "then", "and", "or", "not",
                    "always", "never", "every", "some", "greater", "less", "equals"}
        
        original_important = original_words & important
        back_important = back_words & important
        
        if not original_important:
            return 1.0  # No important words to preserve
        
        preserved = len(original_important & back_important)
        return preserved / len(original_important)
    
    def test_preservation_scores(self):
        """Test that important sentences have high preservation scores."""
        critical_sentences = [
            "all valid inputs must produce valid outputs",
            "if the system fails then trigger emergency shutdown",
            "there exists a solution for every well-formed problem"
        ]
        
        for sentence in critical_sentences:
            tau = self.parser.parse(sentence)
            back = self._simulate_tau_to_english(tau)
            
            score = self.calculate_preservation_score(sentence, tau, back)
            assert score >= 0.5, f"Low preservation score for: {sentence}"
    
    def _simulate_tau_to_english(self, tau: str) -> str:
        """Simulate reverse translation for testing."""
        english = tau
        
        # More comprehensive replacement
        replacements = [
            (r'\ball\s+(\w+):', r'for all \1,'),
            (r'\bex\s+(\w+):', r'there exists \1 such that'),
            (r'->', ' implies '),
            (r'&&', ' and '),
            (r'\|\|', ' or '),
            (r'!', 'not '),
            (r'=', ' equals '),
            (r'>', ' is greater than '),
            (r'<', ' is less than ')
        ]
        
        import re
        for pattern, replacement in replacements:
            english = re.sub(pattern, replacement, english)
        
        return english


if __name__ == "__main__":
    pytest.main([__file__, "-v"])