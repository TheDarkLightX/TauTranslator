"""
Unit tests for TAU parser quantifier expressions
Copyright: DarkLightX/Dana Edwards
"""

import pytest
from backend.unified.domain.tau_parser_service import TauParserService


class TestTauParserQuantifiers:
    """Test cases for TAU parser quantifier expressions."""
    
    def setup_method(self):
        """Set up test environment."""
        self.parser = TauParserService()
    
    def test_parse_forall_simple_constraint(self):
        """Test parsing 'forall x : x > 0'."""
        result = self.parser.parse_tau_code("forall x : x > 0")
        
        assert result.is_success()
        ast = result.value
        assert ast.node_type == "quantifier"
        assert ast.quantifier == "forall"
        assert ast.variable == "x"
        assert ast.domain is None
        assert ast.expression.node_type == "binary_op"
        assert ast.expression.operator == ">"
        assert ast.expression.left.name == "x"
        assert ast.expression.right.value == 0
    
    def test_parse_exists_simple_constraint(self):
        """Test parsing 'exists y : y < 10'."""
        result = self.parser.parse_tau_code("exists y : y < 10")
        
        assert result.is_success()
        ast = result.value
        assert ast.node_type == "quantifier"
        assert ast.quantifier == "exists"
        assert ast.variable == "y"
        assert ast.domain is None
        assert ast.expression.node_type == "binary_op"
        assert ast.expression.operator == "<"
    
    def test_parse_forall_compound_expression(self):
        """Test parsing 'forall x : x > 0 and x < 100'."""
        result = self.parser.parse_tau_code("forall x : x > 0 and x < 100")
        
        assert result.is_success()
        ast = result.value
        assert ast.node_type == "quantifier"
        assert ast.expression.node_type == "binary_op"
        assert ast.expression.operator == "and"
        assert ast.expression.left.operator == ">"
        assert ast.expression.right.operator == "<"
    
    def test_parse_exists_multiplication(self):
        """Test parsing 'exists n : n * n = 4'."""
        result = self.parser.parse_tau_code("exists n : n * n = 4")
        
        assert result.is_success()
        ast = result.value
        assert ast.node_type == "quantifier"
        assert ast.expression.node_type == "binary_op"
        assert ast.expression.operator == "="
        assert ast.expression.left.node_type == "binary_op"
        assert ast.expression.left.operator == "*"
    
    def test_parse_nested_quantifiers(self):
        """Test parsing nested quantifiers."""
        result = self.parser.parse_tau_code("forall x : exists y : x + y > 0")
        
        assert result.is_success()
        ast = result.value
        assert ast.node_type == "quantifier"
        assert ast.quantifier == "forall"
        assert ast.expression.node_type == "quantifier"
        assert ast.expression.quantifier == "exists"
    
    def test_parse_quantifier_missing_colon(self):
        """Test error handling for missing colon."""
        result = self.parser.parse_tau_code("forall x x > 0")
        
        assert result.is_failure()
        assert result.error_code == "EXPECTED_COLON"
    
    def test_parse_quantifier_missing_variable(self):
        """Test error handling for missing variable."""
        result = self.parser.parse_tau_code("forall : x > 0")
        
        assert result.is_failure()
        assert result.error_code == "EXPECTED_VARIABLE"
    
    def test_parse_quantifier_empty_expression(self):
        """Test error handling for empty expression."""
        result = self.parser.parse_tau_code("forall x :")
        
        assert result.is_failure()
        assert result.error_code == "UNEXPECTED_EOF"