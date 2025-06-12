#!/usr/bin/env python3
"""
Unit Tests for Enhanced TextToILRService
Copyright: DarkLightX/Dana Edwards

Tests logical operation support following FIRST principles and AAA pattern.
"""

import pytest
import sys
from pathlib import Path
from returns.result import Success, Failure

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.unified.domain.text_to_ilr_service import TextToILRService
from backend.unified.domain.ilr_types import (
    LogicalExpression, LogicalOperator, VariableReference, 
    ComparisonExpression, ComparisonOperator, BooleanConstant,
    VariableName
)


class TestTextToILRServiceLogicalOperations:
    """Test logical operations in TextToILRService following BDD principles."""
    
    def setup_method(self):
        """Arrange: Initialize service for each test."""
        self.service = TextToILRService()
    
    def test_given_simple_and_expression_when_converting_then_creates_logical_and(self):
        """Test: x and y -> LogicalExpression with AND operator."""
        # Given: Simple AND expression
        text = "x and y"
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should create LogicalExpression with AND
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == LogicalOperator.AND
        assert len(ilr_node.operands) == 2
        
        # Verify operands are variable references
        left_operand = ilr_node.operands[0]
        right_operand = ilr_node.operands[1]
        assert isinstance(left_operand, VariableReference)
        assert isinstance(right_operand, VariableReference)
        assert str(left_operand.name) == "x"
        assert str(right_operand.name) == "y"
    
    def test_given_simple_or_expression_when_converting_then_creates_logical_or(self):
        """Test: a or b -> LogicalExpression with OR operator."""
        # Given: Simple OR expression
        text = "a or b"
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should create LogicalExpression with OR
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == LogicalOperator.OR
        assert len(ilr_node.operands) == 2
    
    def test_given_xor_expression_when_converting_then_creates_logical_xor(self):
        """Test: x xor y -> LogicalExpression with XOR operator."""
        # Given: XOR expression
        text = "x xor y"
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should create LogicalExpression with XOR
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == LogicalOperator.XOR
        assert len(ilr_node.operands) == 2
    
    def test_given_negation_with_not_when_converting_then_creates_logical_not(self):
        """Test: not x -> LogicalExpression with NOT operator."""
        # Given: Negation expression
        text = "not x"
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should create LogicalExpression with NOT
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == LogicalOperator.NOT
        assert len(ilr_node.operands) == 1
        
        # Verify operand is variable reference
        operand = ilr_node.operands[0]
        assert isinstance(operand, VariableReference)
        assert str(operand.name) == "x"
    
    def test_given_negation_with_not_keyword_when_converting_then_creates_logical_not(self):
        """Test: not p -> LogicalExpression with NOT operator."""
        # Given: Another negation expression
        text = "not p"
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should create LogicalExpression with NOT
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == LogicalOperator.NOT
        assert len(ilr_node.operands) == 1
    
    def test_given_implies_expression_when_converting_then_creates_logical_implies(self):
        """Test: x implies y -> LogicalExpression with IMPLIES operator."""
        # Given: Implication expression
        text = "x implies y"
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should create LogicalExpression with IMPLIES
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == LogicalOperator.IMPLIES
        assert len(ilr_node.operands) == 2
    
    def test_given_comparison_expression_when_converting_then_still_works(self):
        """Test: x equals 5 -> ComparisonExpression (regression test)."""
        # Given: Comparison expression
        text = "x equals 5"
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should create ComparisonExpression (not affected by changes)
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, ComparisonExpression)
        assert ilr_node.operator == ComparisonOperator.EQ
    
    def test_given_unsupported_expression_when_converting_then_returns_failure(self):
        """Test: Unsupported expressions should fail gracefully."""
        # Given: Truly unsupported expression
        text = "always sometimes eventually"
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should return Failure
        assert isinstance(result, Failure)
        assert "Cannot convert to ILR" in result.failure()
    
    def test_given_empty_string_when_converting_then_returns_failure(self):
        """Test: Empty string should fail gracefully."""
        # Given: Empty string
        text = ""
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should return Failure
        assert isinstance(result, Failure)
    
    def test_given_whitespace_only_when_converting_then_returns_failure(self):
        """Test: Whitespace-only string should fail gracefully."""
        # Given: Whitespace-only string
        text = "   "
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should return Failure
        assert isinstance(result, Failure)


class TestTextToILRServiceEdgeCases:
    """Test edge cases and error scenarios following property-based testing concepts."""
    
    def setup_method(self):
        """Arrange: Initialize service for each test."""
        self.service = TextToILRService()
    
    @pytest.mark.parametrize("text,expected_operator", [
        ("x and y", LogicalOperator.AND),
        ("a or b", LogicalOperator.OR),
        ("p xor q", LogicalOperator.XOR),
        ("x implies y", LogicalOperator.IMPLIES),
    ])
    def test_given_various_binary_operators_when_converting_then_creates_correct_logical_expression(self, text, expected_operator):
        """Parameterized test for binary logical operators."""
        # Given: Various binary logical expressions
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should create correct LogicalExpression
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == expected_operator
        assert len(ilr_node.operands) == 2
    
    @pytest.mark.parametrize("text", [
        "not x",
        "not p", 
        "not variable1",
    ])
    def test_given_various_negations_when_converting_then_creates_not_expression(self, text):
        """Parameterized test for negation expressions."""
        # Given: Various negation expressions
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should create NOT LogicalExpression
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == LogicalOperator.NOT
        assert len(ilr_node.operands) == 1
    
    def test_given_text_with_trailing_period_when_converting_then_normalizes_correctly(self):
        """Test: Text normalization removes trailing periods."""
        # Given: Text with trailing period
        text = "x and y."
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should still work correctly (period normalized away)
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == LogicalOperator.AND
    
    def test_given_text_with_extra_whitespace_when_converting_then_handles_gracefully(self):
        """Test: Extra whitespace should be handled gracefully."""
        # Given: Text with extra whitespace
        text = "  x   and   y  "
        
        # When: Converting to ILR
        result = self.service.convert_text_to_ilr(text)
        
        # Then: Should still work correctly
        assert isinstance(result, Success)
        ilr_node = result.unwrap()
        assert isinstance(ilr_node, LogicalExpression)
        assert ilr_node.operator == LogicalOperator.AND


def test_integration_with_ilr_pipeline():
    """Integration test: Verify enhanced service works with ILR pipeline."""
    # Given: Enhanced TextToILRService
    service = TextToILRService()
    
    # When: Processing basic logical expressions that were failing before
    test_cases = [
        "x and y",
        "a or b", 
        "not x",
        "p xor q"
    ]
    
    success_count = 0
    for text in test_cases:
        result = service.convert_text_to_ilr(text)
        if isinstance(result, Success):
            success_count += 1
    
    # Then: Should have significantly improved success rate
    success_rate = success_count / len(test_cases)
    assert success_rate >= 0.75, f"Expected >75% success rate, got {success_rate*100:.1f}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])