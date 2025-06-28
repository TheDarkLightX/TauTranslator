"""
Unit tests for refactored NLP translator.

Tests the refactored NLP translation functionality to ensure
backward compatibility and correct behavior.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import asyncio
from backend.unified.translators.nlp_translator_refactored import (
    NLPTranslatorRefactored, TCEToTauTranslator, LegacyNLPTranslatorAdapter,
    NLPTranslatorFactory
)
from backend.unified.domain.nlp_types import TranslationDirection


class TestNLPTranslatorRefactored:
    """Test suite for refactored NLP translator."""
    
    @pytest.fixture
    def translator(self):
        """Create translator instance."""
        return NLPTranslatorFactory.create_translator()
    
    @pytest.fixture
    def custom_vocabulary(self):
        """Create custom vocabulary for testing."""
        return {
            "predicates": {
                "flying": {"arity": 1},
                "mortal": {"arity": 1}
            },
            "types": ["bird", "human", "animal"]
        }
    
    # @pytest.mark.asyncio
    async def test_universal_quantification_simple(self, translator):
        """Test simple universal quantification."""
        nl_text = "All birds can fly"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "for every" in result.output_text
        assert "bird" in result.output_text
        assert result.output_text.endswith(".")
    
    # @pytest.mark.asyncio
    async def test_universal_quantification_complex(self, translator):
        """Test complex universal quantification."""
        nl_text = "Every student who studies passes the exam"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "for every" in result.output_text
        assert "student" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_existential_quantification(self, translator):
        """Test existential quantification."""
        nl_text = "Some birds cannot fly"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "there exists" in result.output_text
        assert "bird" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_conditional_statement(self, translator):
        """Test conditional statement translation."""
        nl_text = "If it rains, then the ground is wet"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "if" in result.output_text
        assert "then" in result.output_text
        assert "rains" in result.output_text
        assert "wet" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_predicate_definition(self, translator):
        """Test predicate definition."""
        nl_text = "A number is even if it is divisible by 2"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "even" in result.output_text
        assert "divisible" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_relation_statement(self, translator):
        """Test relation statement."""
        nl_text = "John is the father of Mary"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "John" in result.output_text
        assert "Mary" in result.output_text
        assert "father" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_temporal_property(self, translator):
        """Test temporal property."""
        nl_text = "It always rains in Seattle"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "always" in result.output_text
        assert "rains" in result.output_text
        assert "Seattle" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_disjunction(self, translator):
        """Test disjunction."""
        nl_text = "Either it's sunny or it's cloudy"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "or" in result.output_text
        assert "sunny" in result.output_text
        assert "cloudy" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_empty_input(self, translator):
        """Test empty input handling."""
        result = await translator.translate_to_tce_async("")
        
        assert not result.success
        assert result.error_message == "Empty input text"
    
    # @pytest.mark.asyncio
    async def test_unsupported_pattern(self, translator):
        """Test unsupported pattern fallback."""
        nl_text = "This is a completely random sentence without any logical structure"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        # Should fall back to rule-based translation
        # The translator may apply some normalization (like removing articles)
        assert "completely random sentence" in result.output_text
        assert result.output_text.endswith(".")
    
    # @pytest.mark.asyncio
    async def test_reverse_translation_simple(self, translator):
        """Test TCE to natural language translation."""
        tce_text = "for every x such that x is human implies x is mortal."
        result = await translator.translate_to_natural_async(tce_text)
        
        assert result.success
        assert "Every" in result.output_text
        assert "human" in result.output_text
        assert "mortal" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_reverse_translation_conditional(self, translator):
        """Test conditional reverse translation."""
        tce_text = "if it rains then the ground is wet."
        result = await translator.translate_to_natural_async(tce_text)
        
        assert result.success
        assert "If" in result.output_text
        assert "ground" in result.output_text
        assert "wet" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_bidirectional_nl_to_tce(self, translator):
        """Test bidirectional translation NL to TCE."""
        nl_text = "All dogs are animals"
        result = await translator.translate_bidirectional_async(
            nl_text, TranslationDirection.NL_TO_TCE
        )
        
        assert result.success
        assert "for every" in result.output_text
        assert "dog" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_bidirectional_tce_to_nl(self, translator):
        """Test bidirectional translation TCE to NL."""
        tce_text = "there exists x such that x is prime and x is even."
        result = await translator.translate_bidirectional_async(
            tce_text, TranslationDirection.TCE_TO_NL
        )
        
        assert result.success
        assert "Some" in result.output_text or "There exists" in result.output_text
        assert "prime" in result.output_text
        assert "even" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_invalid_direction(self, translator):
        """Test invalid translation direction."""
        # Create invalid direction
        invalid_direction = "INVALID"
        result = await translator.translate_bidirectional_async(
            "test", invalid_direction
        )
        
        assert not result.success
        assert "Unsupported translation direction" in result.error_message
    
    def test_engine_info(self, translator):
        """Test engine info retrieval."""
        info = translator.get_engine_info()
        
        assert info["engine_type"] == "nlp_translator"
        assert info["version"] == "2.0"
        assert info["capabilities"]["nl_to_tce"]
        assert info["capabilities"]["tce_to_nl"]
        assert "universal_quantification" in info["capabilities"]["pattern_types"]
        assert info["capabilities"]["fallback"] == "rule_based"
    
    def test_vocabulary_update(self, translator, custom_vocabulary):
        """Test vocabulary update."""
        # Update vocabulary
        translator.update_vocabulary(custom_vocabulary)
        
        # The translator should accept the new vocabulary
        # (actual vocabulary usage would be tested through translation results)
        info = translator.get_engine_info()
        assert info["engine_type"] == "nlp_translator"


class TestTCEToTauTranslator:
    """Test TCE to TAU translator."""
    
    @pytest.fixture
    def translator(self):
        """Create TCE to TAU translator."""
        return NLPTranslatorFactory.create_tce_to_tau_translator()
    
    # @pytest.mark.asyncio
    async def test_logical_operators(self, translator):
        """Test logical operator transformation."""
        tce_text = "x > 0 and y < 10 or z = 5"
        result = await translator.translate_to_tau_async(tce_text)
        
        assert result.success
        assert "&" in result.output_text
        assert "|" in result.output_text
        assert result.output_text.endswith(".")
    
    # @pytest.mark.asyncio
    async def test_quantifiers(self, translator):
        """Test quantifier transformation."""
        tce_text = "for every x such that x > 0"
        result = await translator.translate_to_tau_async(tce_text)
        
        assert result.success
        assert "∀" in result.output_text
        assert ":" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_temporal_operators(self, translator):
        """Test temporal operator transformation."""
        tce_text = "always x > 0"
        result = await translator.translate_to_tau_async(tce_text)
        
        assert result.success
        assert "□" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_conditionals(self, translator):
        """Test conditional transformation."""
        tce_text = "if x > 0 then y = 1"
        result = await translator.translate_to_tau_async(tce_text)
        
        assert result.success
        assert "->" in result.output_text
        assert "if " not in result.output_text  # 'if' should be removed
    
    # @pytest.mark.asyncio
    async def test_predicate_transformation(self, translator):
        """Test predicate transformation."""
        tce_text = "x is even"
        result = await translator.translate_to_tau_async(tce_text)
        
        assert result.success
        assert result.output_text == "x.even."
    
    # @pytest.mark.asyncio
    async def test_function_form_preservation(self, translator):
        """Test that function forms are preserved."""
        tce_text = "even(x) and prime(y)"
        result = await translator.translate_to_tau_async(tce_text)
        
        assert result.success
        assert "even(x)" in result.output_text
        assert "prime(y)" in result.output_text
        assert "&" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_empty_input_tau(self, translator):
        """Test empty input handling."""
        result = await translator.translate_to_tau_async("")
        
        assert not result.success
        assert result.error_message == "Empty input text"
    
    # @pytest.mark.asyncio
    async def test_period_handling(self, translator):
        """Test period handling in TAU output."""
        # Input with period
        tce_text = "x > 0."
        result = await translator.translate_to_tau_async(tce_text)
        assert result.success
        assert result.output_text.endswith(".")
        assert not result.output_text.endswith("..")
        
        # Input without period
        tce_text = "x > 0"
        result = await translator.translate_to_tau_async(tce_text)
        assert result.success
        assert result.output_text.endswith(".")


class TestLegacyAdapter:
    """Test legacy adapter for backward compatibility."""
    
    @pytest.fixture
    def adapter(self):
        """Create legacy adapter."""
        return NLPTranslatorFactory.create_legacy_adapter()
    
    def test_legacy_translate_to_tce(self, adapter):
        """Test legacy synchronous translation to TCE."""
        nl_text = "All birds can fly"
        result = adapter.translate_to_tce(nl_text)
        
        assert result  # Non-empty result
        assert "for every" in result
        assert "bird" in result
    
    def test_legacy_translate_to_natural(self, adapter):
        """Test legacy synchronous translation to natural language."""
        tce_text = "for every x such that x is human implies x is mortal."
        result = adapter.translate_to_natural(tce_text)
        
        assert result  # Non-empty result
        assert "Every" in result or "All" in result
        assert "human" in result
        assert "mortal" in result
    
    def test_legacy_error_handling(self, adapter):
        """Test legacy error handling behavior."""
        # Empty input should return empty string
        result = adapter.translate_to_tce("")
        assert result == ""
        
        # Invalid TCE should return original
        invalid_tce = "invalid tce text"
        result = adapter.translate_to_natural(invalid_tce)
        assert result == invalid_tce


class TestNLPTranslatorFactory:
    """Test NLP translator factory."""
    
    def test_create_translator(self):
        """Test creating standard translator."""
        translator = NLPTranslatorFactory.create_translator()
        assert isinstance(translator, NLPTranslatorRefactored)
        
        # With vocabulary
        vocab = {"types": ["test"]}
        translator = NLPTranslatorFactory.create_translator(vocab)
        assert isinstance(translator, NLPTranslatorRefactored)
    
    def test_create_tce_to_tau_translator(self):
        """Test creating TCE to TAU translator."""
        translator = NLPTranslatorFactory.create_tce_to_tau_translator()
        assert isinstance(translator, TCEToTauTranslator)
    
    def test_create_legacy_adapter(self):
        """Test creating legacy adapter."""
        adapter = NLPTranslatorFactory.create_legacy_adapter()
        assert isinstance(adapter, LegacyNLPTranslatorAdapter)
        
        # With vocabulary
        vocab = {"types": ["test"]}
        adapter = NLPTranslatorFactory.create_legacy_adapter(vocab)
        assert isinstance(adapter, LegacyNLPTranslatorAdapter)


class TestComplexTranslations:
    """Test complex translation scenarios."""
    
    @pytest.fixture
    def translator(self):
        """Create translator with rich vocabulary."""
        vocabulary = {
            "predicates": {
                "prime": {"arity": 1, "type": "number -> boolean"},
                "even": {"arity": 1, "type": "number -> boolean"},
                "divisible": {"arity": 2, "type": "(number, number) -> boolean"}
            },
            "functions": {
                "square": {"arity": 1, "type": "number -> number"},
                "gcd": {"arity": 2, "type": "(number, number) -> number"}
            },
            "types": ["number", "person", "animal", "object"]
        }
        return NLPTranslatorFactory.create_translator(vocabulary)
    
    # @pytest.mark.asyncio
    async def test_nested_quantifiers(self, translator):
        """Test nested quantifier translation."""
        nl_text = "For every number, there exists a prime greater than it"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "every" in result.output_text.lower()
        assert "exists" in result.output_text.lower()
        assert "prime" in result.output_text
        assert "greater" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_complex_conditional(self, translator):
        """Test complex conditional with multiple clauses."""
        nl_text = "If a number is even and greater than 2, then it is not prime"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "if" in result.output_text
        assert "and" in result.output_text
        assert "then" in result.output_text
        assert "not" in result.output_text
    
    # @pytest.mark.asyncio
    async def test_mixed_operators(self, translator):
        """Test mixed logical operators."""
        nl_text = "All animals are either mammals or birds but not both"
        result = await translator.translate_to_tce_async(nl_text)
        
        assert result.success
        assert "for every" in result.output_text
        assert "or" in result.output_text
        assert "not" in result.output_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])