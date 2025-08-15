"""
Unit Tests for NLP Translator
==============================

Comprehensive tests for natural language processing functionality.
"""

import pytest
from tau_translator_omega.core_engine.translators.nlp_translator import (
    NLPPatternMatcher,
    NaturalLanguageTranslator,
    TCEToTauNLPTranslator
)


class TestNLPPatternMatcher:
    """Test pattern matching functionality."""
    
    def test_universal_quantifier_patterns(self):
        """Test matching universal quantifier patterns."""
        matcher = NLPPatternMatcher()
        
        # Test "all" pattern
        result = matcher.match_pattern("All birds can fly")
        assert result is not None
        pattern_type, template, match = result
        assert pattern_type == 'universal'
        
        # Test "every" pattern
        result = matcher.match_pattern("Every student has a teacher")
        assert result is not None
        assert result[0] == 'universal'
        
    def test_existential_quantifier_patterns(self):
        """Test matching existential quantifier patterns."""
        matcher = NLPPatternMatcher()
        
        # Test "some" pattern
        result = matcher.match_pattern("Some birds are blue")
        assert result is not None
        assert result[0] == 'existential'
        
        # Test "a/an" pattern
        result = matcher.match_pattern("A student is happy")
        assert result is not None
        assert result[0] == 'existential'
        
    def test_conditional_patterns(self):
        """Test matching conditional patterns."""
        matcher = NLPPatternMatcher()
        
        result = matcher.match_pattern("If it's raining, then the ground is wet")
        assert result is not None
        pattern_type, template, match = result
        assert pattern_type == 'conditional'
        assert match.group(1) == "it's raining"
        assert match.group(2) == "the ground is wet"
        
    def test_always_property_patterns(self):
        """Test matching always property patterns."""
        matcher = NLPPatternMatcher()
        
        result = matcher.match_pattern("The sun is always hot")
        assert result is not None
        assert result[0] == 'always_property'
        
    def test_relation_patterns(self):
        """Test matching relation patterns."""
        matcher = NLPPatternMatcher()
        
        # Test love relation
        result = matcher.match_pattern("John loves Mary")
        assert result is not None
        assert result[0] == 'relation'
        
        # Test has relation
        result = matcher.match_pattern("Alice has a book")
        assert result is not None
        assert result[0] == 'relation'
        
    def test_negated_universal_patterns(self):
        """Test matching negated universal patterns."""
        matcher = NLPPatternMatcher()
        
        result = matcher.match_pattern("Nobody is perfect")
        assert result is not None
        assert result[0] == 'neg_universal'
        
    def test_disjunction_patterns(self):
        """Test matching disjunction patterns."""
        matcher = NLPPatternMatcher()
        
        result = matcher.match_pattern("Either it's day or it's night")
        assert result is not None
        assert result[0] == 'disjunction'


class TestNaturalLanguageTranslator:
    """Test natural language to TCE translation."""
    
    def test_translate_universal_quantifiers(self):
        """Test translating universal quantifiers to TCE."""
        translator = NaturalLanguageTranslator()
        
        # Test "all birds can fly"
        result = translator.translate_to_tce("All birds can fly")
        assert result == "for every x such that bird(x) then can_fly(x)."
        
        # Test with direct mapping (override)
        result = translator.translate_to_tce("all birds can fly")
        assert result == "Always x is bird implies x can fly."
        
    def test_translate_existential_quantifiers(self):
        """Test translating existential quantifiers to TCE."""
        translator = NaturalLanguageTranslator()
        
        result = translator.translate_to_tce("Some birds are blue")
        assert result == "there exists x such that bird(x) and blue(x)."
        
    def test_translate_conditionals(self):
        """Test translating conditionals to TCE."""
        translator = NaturalLanguageTranslator()
        
        result = translator.translate_to_tce("If it's raining, then the ground is wet")
        assert result == "if raining then ground is wet."
        
    def test_translate_always_properties(self):
        """Test translating always properties to TCE."""
        translator = NaturalLanguageTranslator()
        
        result = translator.translate_to_tce("The sun is always hot")
        assert result == "Always sun is hot."
        
    def test_translate_relations(self):
        """Test translating relations to TCE."""
        translator = NaturalLanguageTranslator()
        
        result = translator.translate_to_tce("John loves Mary")
        assert result == "love(John, Mary)."
        
    def test_translate_negated_universals(self):
        """Test translating negated universals to TCE."""
        translator = NaturalLanguageTranslator()
        
        result = translator.translate_to_tce("Nobody is perfect")
        assert result == "for every x such that not perfect(x)."
        
    def test_translate_disjunctions(self):
        """Test translating disjunctions to TCE."""
        translator = NaturalLanguageTranslator()
        
        result = translator.translate_to_tce("Either it's day or it's night")
        assert result == "day or night."
        
    def test_normalize_conditions(self):
        """Test condition normalization."""
        translator = NaturalLanguageTranslator()
        
        # Test "it's X" normalization
        result = translator._normalize_condition("it's raining")
        assert result == "raining"
        
        # Test "the X is Y" normalization
        result = translator._normalize_condition("the ground is wet")
        assert result == "ground is wet"
        
    def test_translate_to_natural(self):
        """Test TCE to natural language translation."""
        translator = NaturalLanguageTranslator()
        
        # Test always pattern
        result = translator.translate_to_natural("always sun is hot.")
        assert result == "The sun is always hot."
        
        # Test universal quantifier
        result = translator.translate_to_natural("for every x such that bird(x) then can_fly(x).")
        assert result == "All birds can fly."
        
        # Test existential quantifier
        result = translator.translate_to_natural("there exists x such that happy(x).")
        assert result == "Someone is happy."
        
        # Test conditional
        result = translator.translate_to_natural("if raining then ground is wet.")
        assert result == "If it's raining, then the ground is wet."
        
        # Test relation
        result = translator.translate_to_natural("love(John, Mary).")
        assert result == "John loves Mary."


class TestTCEToTauNLPTranslator:
    """Test TCE to TAU translation with NLP support."""
    
    def test_translate_always_properties(self):
        """Test translating always properties to TAU."""
        translator = TCEToTauNLPTranslator()
        
        # Test with lowercase
        result = translator.translate_tce_to_tau("always sun is hot.")
        assert result == "□hot(sun)"
        
        # Test with uppercase
        result = translator.translate_tce_to_tau("Always sun is hot.")
        assert result == "□hot(sun)"
        
    def test_translate_universal_quantifiers(self):
        """Test translating universal quantifiers to TAU."""
        translator = TCEToTauNLPTranslator()
        
        # Test simple universal
        result = translator.translate_tce_to_tau("Always x is bird implies x can fly.")
        assert result == "∀x(bird(x) → can_fly(x))"
        
        # Test nested quantifiers
        result = translator.translate_tce_to_tau("Always student exists teacher such that has(student, teacher).")
        assert result == "∀student∃teacher(has(student, teacher))"
        
    def test_translate_implications(self):
        """Test translating implications to TAU."""
        translator = TCEToTauNLPTranslator()
        
        result = translator.translate_tce_to_tau("raining implies ground is wet.")
        assert result == "raining → wet(ground)"
        
    def test_translate_conditionals(self):
        """Test translating conditionals to TAU."""
        translator = TCEToTauNLPTranslator()
        
        result = translator.translate_tce_to_tau("if work_hard(you) then succeed(you).")
        assert result == "work_hard(you) → succeed(you)"
        
    def test_translate_disjunctions(self):
        """Test translating disjunctions to TAU."""
        translator = TCEToTauNLPTranslator()
        
        result = translator.translate_tce_to_tau("day or night.")
        assert result == "day ∨ night"
        
    def test_translate_existential_quantifiers(self):
        """Test translating existential quantifiers to TAU."""
        translator = TCEToTauNLPTranslator()
        
        # Test simple existential
        result = translator.translate_tce_to_tau("there exists x such that happy(x).")
        assert result == "∃x(happy(x))"
        
        # Test with conjunction
        result = translator.translate_tce_to_tau("there exists x such that bird(x) and blue(x).")
        assert result == "∃x(bird(x) ∧ blue(x))"
        
    def test_translate_negated_universals(self):
        """Test translating negated universals to TAU."""
        translator = TCEToTauNLPTranslator()
        
        result = translator.translate_tce_to_tau("for every x such that not perfect(x).")
        assert result == "∀x(¬perfect(x))"
        
    def test_translate_nl_to_tau_direct(self):
        """Test direct natural language to TAU translation."""
        translator = TCEToTauNLPTranslator()
        
        # Test full pipeline
        result = translator.translate_nl_to_tau("The sun is always hot")
        assert result == "□hot(sun)"
        
        result = translator.translate_nl_to_tau("All birds can fly")
        assert result == "∀x(bird(x) → can_fly(x))"
        
        result = translator.translate_nl_to_tau("If it's raining, then the ground is wet")
        assert result == "raining → wet(ground)"
        
        result = translator.translate_nl_to_tau("Every student has a teacher")
        assert result == "∀student∃teacher(has(student, teacher))"


class TestComplexTranslations:
    """Test complex translation scenarios."""
    
    def test_nested_conditions(self):
        """Test translations with nested conditions."""
        translator = TCEToTauNLPTranslator()
        
        # Test nested universal with negation
        tce = "for every x such that person(x) then not perfect(x)."
        tau = translator.translate_tce_to_tau(tce)
        assert "∀x" in tau
        assert "person(x)" in tau
        assert "¬perfect(x)" in tau or "not perfect(x)" in tau
        
    def test_multiple_variables(self):
        """Test translations with multiple variables."""
        translator = TCEToTauNLPTranslator()
        
        # Test multiple bound variables
        tce = "for every x such that for every y such that loves(x, y) then happy(y)."
        tau = translator.translate_tce_to_tau(tce)
        assert "∀x" in tau
        
    def test_edge_cases(self):
        """Test edge cases in translation."""
        nl_translator = NaturalLanguageTranslator()
        tce_translator = TCEToTauNLPTranslator()
        
        # Test empty input
        with pytest.raises(Exception):
            nl_translator.translate_to_tce("")
            
        # Test input without period
        result = nl_translator.translate_to_tce("The sun is hot")
        assert result.endswith(".")
        
        # Test already has period
        result = nl_translator.translate_to_tce("The sun is hot.")
        assert not result.endswith("..")
        
    def test_vocabulary_integration(self):
        """Test translation with vocabulary context."""
        vocab = {
            'concepts': {
                'bird': {'type': 'class', 'properties': ['can_fly', 'has_wings']},
                'student': {'type': 'class', 'relations': ['has', 'studies']}
            }
        }
        
        translator = NaturalLanguageTranslator(vocab)
        # Vocabulary can be used for more sophisticated translations
        result = translator.translate_to_tce("All birds can fly")
        assert "bird" in result
        assert "fly" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])