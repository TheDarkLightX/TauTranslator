#!/usr/bin/env python3
"""
Integration tests for ILR Pipeline
Copyright: DarkLightX/Dana Edwards

Tests the complete NL→ILR→TCE→Tau pipeline with semantic structure.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.ilr_pipeline_simple import ILRPipelineSimple


class TestILRPipelineIntegration:
    """Test ILR-integrated translation pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create ILR pipeline instance."""
        return ILRPipelineSimple()
    
    def test_simple_comparison_assignment(self, pipeline):
        """Test x equals 5 → ComparisonExpression → TCE → Tau."""
        result = pipeline.translate("x equals 5")
        
        assert result.success is True
        assert result.ilr_type == "ComparisonExpression"
        assert result.tce_text == "x equals 5.0."
        assert "x" in result.tau_code  # Partial translation expected
    
    def test_semantic_structure_preservation(self, pipeline):
        """Test that ILR preserves semantic structure."""
        result = pipeline.translate("temperature is 25")
        
        assert result.success is True
        assert result.ilr_type == "ComparisonExpression" 
        assert "temperature" in result.tce_text
        assert "25.0" in result.tce_text
        assert result.tau_code != ""
    
    def test_greater_than_comparison(self, pipeline):
        """Test x is greater than 10 → ComparisonExpression."""
        result = pipeline.translate("x is greater than 10")
        
        assert result.success is True
        assert result.ilr_type == "ComparisonExpression"
        assert "greater than" in result.tce_text
        assert "10.0" in result.tce_text
    
    def test_unsupported_logical_expression(self, pipeline):
        """Test that unsupported expressions fail gracefully."""
        result = pipeline.translate("x and y")
        
        # This should fail because ILR generator doesn't handle AND yet
        assert result.success is False
        assert "error" in result.metadata
        assert "Cannot convert to ILR" in result.metadata["error"]
    
    def test_pipeline_metadata(self, pipeline):
        """Test that pipeline metadata is properly recorded."""
        result = pipeline.translate("x equals 5")
        
        assert "pipeline" in result.metadata
        assert result.metadata["pipeline"] == "NL→ILR→TCE→Tau"
    
    def test_ilr_semantic_types(self, pipeline):
        """Test that ILR generates proper semantic types."""
        test_cases = [
            ("x equals 5", "ComparisonExpression"),
            ("temperature is 25", "ComparisonExpression"),
            ("x is greater than 10", "ComparisonExpression"),
        ]
        
        for english, expected_type in test_cases:
            result = pipeline.translate(english)
            if result.success:
                assert result.ilr_type == expected_type
    
    def test_tce_formatting(self, pipeline):
        """Test that TCE is properly formatted for CNL parser."""
        result = pipeline.translate("x equals 5")
        
        assert result.success is True
        assert result.tce_text.endswith(".")
        assert "equals" in result.tce_text
    
    def test_error_handling(self, pipeline):
        """Test error handling for invalid input."""
        # Test empty input
        result = pipeline.translate("")
        assert isinstance(result.success, bool)
        
        # Test malformed input  
        result = pipeline.translate("invalid grammar xyz test")
        assert isinstance(result.success, bool)


def test_ilr_vs_direct_pipeline_comparison():
    """Compare ILR pipeline with direct NL→TCE→Tau pipeline."""
    from backend.unified.english_to_tau_integrated import IntegratedEnglishToTauTranslator
    
    ilr_pipeline = ILRPipelineSimple()
    direct_pipeline = IntegratedEnglishToTauTranslator()
    
    test_case = "x equals 5"
    
    # Test ILR pipeline
    ilr_result = ilr_pipeline.translate(test_case)
    
    # Test direct pipeline
    direct_success, direct_tau, direct_tce = direct_pipeline.translate(test_case)
    
    print(f"\n=== Pipeline Comparison: '{test_case}' ===")
    print(f"ILR Pipeline:")
    print(f"  Success: {ilr_result.success}")
    print(f"  ILR Type: {ilr_result.ilr_type}")
    print(f"  TCE: {ilr_result.tce_text}")
    print(f"  Tau: {ilr_result.tau_code}")
    
    print(f"Direct Pipeline:")
    print(f"  Success: {direct_success}")
    print(f"  TCE: {direct_tce}")
    print(f"  Tau: {direct_tau}")
    
    # Both should succeed
    assert ilr_result.success is True
    assert direct_success is True


if __name__ == "__main__":
    # Run comparison test
    test_ilr_vs_direct_pipeline_comparison()