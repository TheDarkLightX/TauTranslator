"""
Integration tests for the multi-stage parser pipeline.
Copyright: DarkLightX/Dana Edwards

Tests: Natural Language → ILR → TCE → Tau Code
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.unified.translators.integrated_parser_pipeline import IntegratedParserPipeline
from backend.unified.translators.base import TranslationDirection


class TestParserPipeline:
    """Test the integrated parser pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create pipeline instance."""
        return IntegratedParserPipeline()
    
    def test_natural_language_to_tce(self, pipeline):
        """Test Natural Language → TCE translation."""
        # Simple fact
        result = pipeline.translate(
            "x equals 5",
            TranslationDirection.NL_TO_TCE
        )
        assert result.success
        assert "equals" in result.translated_text or "=" in result.translated_text
        
    def test_natural_language_to_tau(self, pipeline):
        """Test full pipeline: Natural Language → Tau."""
        # Variable assignment
        result = pipeline.translate(
            "x is 10",
            TranslationDirection.NL_TO_TAU
        )
        assert result.success
        assert result.translated_text  # Should produce Tau code
        
    def test_conditional_translation(self, pipeline):
        """Test conditional statement translation."""
        result = pipeline.translate(
            "if x is greater than 5 then y equals true",
            TranslationDirection.NL_TO_TCE
        )
        assert result.success
        assert "if" in result.translated_text
        assert "then" in result.translated_text
        
    def test_tce_to_tau_direct(self, pipeline):
        """Test direct TCE → Tau translation."""
        result = pipeline.translate(
            "x equals 5.",
            TranslationDirection.TCE_TO_TAU
        )
        assert result.success
        assert result.confidence > 0.9
        
    def test_quantified_statement(self, pipeline):
        """Test quantified statement translation."""
        result = pipeline.translate(
            "for all x, x plus 0 equals x",
            TranslationDirection.NL_TO_TCE
        )
        assert result.success
        assert "for all" in result.translated_text or "∀" in result.translated_text
        
    def test_function_definition(self, pipeline):
        """Test function definition translation."""
        result = pipeline.translate(
            "function square(x) returns x times x",
            TranslationDirection.NL_TO_TAU
        )
        assert result.success
        assert "square" in result.translated_text
        
    def test_comparison_expressions(self, pipeline):
        """Test various comparison expressions."""
        comparisons = [
            ("x is greater than y", ["greater than", ">"]),
            ("a is less than b", ["less than", "<"]),
            ("m equals n", ["equals", "="]),
            ("p is at least q", ["at least", ">="]),
            ("r is at most s", ["at most", "<="])
        ]
        
        for nl_text, expected_patterns in comparisons:
            result = pipeline.translate(nl_text, TranslationDirection.NL_TO_TCE)
            assert result.success
            assert any(pattern in result.translated_text for pattern in expected_patterns)
            
    def test_error_handling(self, pipeline):
        """Test error handling for invalid input."""
        result = pipeline.translate(
            "",  # Empty input
            TranslationDirection.NL_TO_TAU
        )
        assert not result.success
        assert result.error
        
    def test_pipeline_metadata(self, pipeline):
        """Test that pipeline adds proper metadata."""
        result = pipeline.translate(
            "x equals 5",
            TranslationDirection.NL_TO_TAU
        )
        assert result.success
        assert result.engine_used == "integrated_parser"
        assert "pipeline" in result.metadata
        
    def test_complex_logical_expression(self, pipeline):
        """Test complex logical expressions."""
        result = pipeline.translate(
            "if x is greater than 0 and y is less than 10 then z equals x plus y",
            TranslationDirection.NL_TO_TAU
        )
        assert result.success
        assert result.translated_text  # Should produce valid Tau code


class TestPipelineComponents:
    """Test individual pipeline components."""
    
    def test_ilr_generation_from_natural_language(self):
        """Test ILR generation from natural language."""
        from backend.unified.domain.ilr_generation_service import ILRGenerationService
        
        service = ILRGenerationService()
        
        # Test simple fact
        ilr = service.generate_from_text("x equals 5")
        assert ilr is not None
        
        # Test conditional
        ilr = service.generate_from_text("if x then y")
        assert ilr is not None
        
    def test_ilr_to_tce_transformation(self):
        """Test ILR to TCE transformation."""
        from backend.unified.domain.ilr_to_tce_transformer import ILRToTCETransformer
        from backend.unified.domain.ilr_types import (
            ComparisonExpression, VariableReference, NumericConstant,
            ComparisonOperator, VariableName
        )
        
        transformer = ILRToTCETransformer()
        
        # Create a simple comparison ILR node
        ilr_node = ComparisonExpression(
            left=VariableReference(VariableName("x")),
            operator=ComparisonOperator.EQUALS,
            right=NumericConstant(5)
        )
        
        result = transformer.transform_ilr_to_tce_async(ilr_node)
        assert result.is_ok()
        
        statements = result.unwrap()
        assert len(statements) > 0
        assert "x" in statements[0].pattern
        
    def test_tce_parsing(self):
        """Test TCE parsing functionality."""
        from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
        
        parser = CNLParser()
        
        # Test simple TCE statement
        ast = parser.parse("x equals 5.")
        assert ast is not None
        
        # Test conditional
        ast = parser.parse("if x > 0 then y = true.")
        assert ast is not None
        
    def test_tau_generation(self):
        """Test Tau code generation."""
        from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator
        from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
        
        parser = CNLParser()
        translator = TCETauTranslator()
        
        # Parse and translate simple statement
        ast = parser.parse("x equals 5.")
        if ast:
            result = translator.translate(ast)
            assert result.tau_code
            assert not result.errors