"""
Unit tests for refactored ILR translator.

Tests the refactored ILR translation functionality to ensure
backward compatibility and correct behavior.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import asyncio
from backend.unified.translators.ilr_translator_refactored import (
    ILRTranslatorRefactored, ILRTranslatorFactory
)
from backend.unified.domain.ilr_types import TranslationResult


class TestILRTranslatorRefactored:
    """Test suite for refactored ILR translator."""
    
    @pytest.fixture
    def translator(self):
        """Create translator instance."""
        return ILRTranslatorFactory.create_translator()
    
    @pytest.mark.asyncio
    async def test_predicate_definition(self, translator):
        """Test predicate definition translation."""
        text = "for any x, predicate even(x) is x mod 2 = 0."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert result.ilr_json is not None
        assert "even" in result.ilr_json
        assert "PROGRAM_UNIT" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_function_definition(self, translator):
        """Test function definition translation."""
        text = "function square(x) returns x * x."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert result.ilr_json is not None
        assert "square" in result.ilr_json
        assert "MUL" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_universal_quantification(self, translator):
        """Test universal quantification."""
        text = "for all x, x > 0."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert result.ilr_json is not None
        assert "FOR_ALL" in result.ilr_json
        assert "COMPARISON_EXPRESSION" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_existential_quantification(self, translator):
        """Test existential quantification."""
        text = "exists x such that x = 5."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert result.ilr_json is not None
        assert "EXISTS" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_conditional_statement(self, translator):
        """Test conditional statement."""
        text = "if x > 0 then x is positive."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert result.ilr_json is not None
        assert "IMPLIES" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_assignment_statement(self, translator):
        """Test assignment statement."""
        text = "x = 42."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert result.ilr_json is not None
        assert "42" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_stream_rule(self, translator):
        """Test stream rule translation."""
        text = "o1[t] = i1[t] and i2[t]."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert result.ilr_json is not None
        assert "ASSIGNMENT" in result.ilr_json
        assert "AND" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_temporal_always(self, translator):
        """Test temporal always statement."""
        text = "always x > 0."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert result.ilr_json is not None
        assert "ALWAYS" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_sbf_input(self, translator):
        """Test SBF input declaration."""
        text = "sbf_input(i1, i2, i3)."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert result.ilr_json is not None
        assert "SBF_DECLARATION" in result.ilr_json
        assert "INPUT" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_ilr_to_tau_translation(self, translator):
        """Test ILR to TAU translation."""
        # First create ILR
        text = "x = 5."
        ilr_result = await translator.translate_to_ilr_async(text)
        assert ilr_result.success
        
        # Then translate to TAU
        tau_result = await translator.translate_to_tau_async(ilr_result.ilr_json)
        assert tau_result.success
        assert tau_result.tau_code == "x = 5."
    
    @pytest.mark.asyncio
    async def test_direct_nl_to_tau(self, translator):
        """Test direct natural language to TAU translation."""
        text = "for all x, x > 0."
        result = await translator.translate_nl_to_tau_async(text)
        
        assert result.success
        assert result.tau_code is not None
        assert "for all x" in result.tau_code
    
    @pytest.mark.asyncio
    async def test_empty_input(self, translator):
        """Test empty input handling."""
        result = await translator.translate_to_ilr_async("")
        
        assert not result.success
        assert result.error_message == "Input text is empty"
    
    @pytest.mark.asyncio
    async def test_invalid_pattern(self, translator):
        """Test invalid pattern handling."""
        text = "this is not a valid pattern"
        result = await translator.translate_to_ilr_async(text)
        
        assert not result.success
        # The error comes from trying to parse it as an assignment
        assert "Failed to parse" in result.error_message or "Cannot parse" in result.error_message
    
    def test_engine_info(self, translator):
        """Test engine info retrieval."""
        info = translator.get_engine_info()
        
        assert info["engine_type"] == "ilr_translator"
        assert info["version"] == "2.0"
        assert info["capabilities"]["natural_to_ilr"]
        assert info["capabilities"]["ilr_to_tau"]
        assert "pattern_types" in info["capabilities"]


class TestILRExpressionParsing:
    """Test expression parsing functionality."""
    
    @pytest.fixture
    def translator(self):
        """Create translator instance."""
        return ILRTranslatorFactory.create_translator()
    
    @pytest.mark.asyncio
    async def test_arithmetic_expression(self, translator):
        """Test arithmetic expression parsing."""
        text = "x = 2 + 3 * 4."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert "ADD" in result.ilr_json
        assert "MUL" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_comparison_expression(self, translator):
        """Test comparison expression parsing."""
        text = "x > 5 and y <= 10."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert "GT" in result.ilr_json
        assert "LTE" in result.ilr_json
        assert "AND" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_function_call_expression(self, translator):
        """Test function call in expression."""
        text = "x = max(a, b)."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert "FUNCTION_CALL" in result.ilr_json
        assert "max" in result.ilr_json
    
    @pytest.mark.asyncio
    async def test_temporal_reference(self, translator):
        """Test temporal reference parsing."""
        text = "o1[t] = i1[t-1] + i2[t+1]."
        result = await translator.translate_to_ilr_async(text)
        
        assert result.success
        assert "temporal_qualifier" in result.ilr_json
        assert "-1" in result.ilr_json
        assert "1" in result.ilr_json


if __name__ == "__main__":
    pytest.main([__file__, "-v"])