#!/usr/bin/env python3
"""
TDD Tests for Tau Solver Constructs
===================================

Test-driven development for implementing proper Tau language parsing
and translation, based on official IDNI demos.

Author: DarkLightX / Dana Edwards
"""

import pytest
from tau_translator_omega.core_engine.parsers.grammar_driven_parser import GrammarDrivenParser as TauParser
from tau_translator_omega.core_engine.ast.ast_nodes import *


class TestTauSolverConstructs:
    """Test parsing and AST generation for Tau solver constructs."""
    
    def setup_method(self):
        """Initialize parser for each test."""
        self.parser = TauParser()
    
    # Basic solve command tests
    def test_parse_simple_solve_equation(self):
        """Test parsing: solve x = 0"""
        tau_code = "solve x = 0"
        ast = self.parser.parse(tau_code)
        
        assert ast is not None
        assert isinstance(ast, SolveNode)
        assert len(ast.constraints) == 1
        assert isinstance(ast.constraints[0], EquationNode)
        assert ast.constraints[0].left.name == "x"
        assert ast.constraints[0].right.value == 0
    
    def test_parse_solve_conjunction(self):
        """Test parsing: solve x = 0 && y = 0"""
        tau_code = "solve x = 0 && y = 0"
        ast = self.parser.parse(tau_code)
        
        assert isinstance(ast, SolveNode)
        assert len(ast.constraints) == 1
        assert isinstance(ast.constraints[0], ConjunctionNode)
        assert len(ast.constraints[0].operands) == 2
    
    def test_parse_solve_with_type_annotation(self):
        """Test parsing: solve {a}:sbf x = 0"""
        tau_code = "solve {a}:sbf x = 0"
        ast = self.parser.parse(tau_code)
        
        assert isinstance(ast, SolveNode)
        assert ast.type_annotations is not None
        assert "a" in ast.type_annotations
        assert ast.type_annotations["a"] == "sbf"
    
    def test_parse_solve_with_complement(self):
        """Test parsing: solve x != 0 && x' != 0"""
        tau_code = "solve x != 0 && x' != 0"
        ast = self.parser.parse(tau_code)
        
        assert isinstance(ast, SolveNode)
        constraint = ast.constraints[0]
        assert isinstance(constraint, ConjunctionNode)
        
        # Check second part has complement
        second_constraint = constraint.operands[1]
        assert isinstance(second_constraint.left, ComplementNode)
        assert second_constraint.left.operand.name == "x"
    
    def test_parse_solve_with_existential_quantifier(self):
        """Test parsing: solve {ex a a = 0} x != 0"""
        tau_code = "solve {ex a a = 0} x != 0"
        ast = self.parser.parse(tau_code)
        
        assert isinstance(ast, SolveNode)
        assert isinstance(ast.constraints[0], ConditionalConstraintNode)
        assert isinstance(ast.constraints[0].condition, ExistentialQuantifierNode)
        assert ast.constraints[0].condition.variable == "a"
        assert isinstance(ast.constraints[0].condition.constraint, EquationNode)


class TestTauToEnglishTranslation:
    """Test translation from Tau to Plain English."""
    
    def setup_method(self):
        """Initialize translator for each test."""
        from tau_translator_omega.core_engine.tau_to_english_translator import TauToEnglishTranslator
        self.translator = TauToEnglishTranslator()
    
    def test_translate_simple_solve(self):
        """Test: solve x = 0 -> Find a value for x such that x equals zero"""
        result = self.translator.translate("solve x = 0")
        expected = "Find a value for x such that x equals zero"
        assert result == expected
    
    def test_translate_solve_conjunction(self):
        """Test: solve x = 0 && y = 0 -> Find values for x and y such that..."""
        result = self.translator.translate("solve x = 0 && y = 0")
        expected = "Find values for x and y such that x equals zero and y equals zero"
        assert result == expected
    
    def test_translate_typed_solve(self):
        """Test: solve {a}:sbf x = 0 -> Find a value for x where a is of type sbf..."""
        result = self.translator.translate("solve {a}:sbf x = 0")
        expected = "Find a value for x where a is of type sbf such that x equals zero"
        assert result == expected
    
    def test_translate_complement_operator(self):
        """Test: x' -> the complement of x"""
        result = self.translator.translate("x'")
        expected = "the complement of x"
        assert result == expected
    
    def test_translate_existential_in_constraint(self):
        """Test: {ex a a = 0} -> there exists a where a equals zero"""
        result = self.translator.translate("{ex a a = 0}")
        expected = "there exists a where a equals zero"
        assert result == expected


class TestEnglishToTauTranslation:
    """Test translation from Plain English to Tau."""
    
    def setup_method(self):
        """Initialize translator for each test."""
        from tau_translator_omega.core_engine.english_to_tau_translator import EnglishToTauTranslator
        self.translator = EnglishToTauTranslator()
    
    def test_translate_find_value_to_solve(self):
        """Test: Find a value for x such that... -> solve x = ..."""
        english = "Find a value for x such that x equals zero"
        result = self.translator.translate(english)
        expected = "solve x = 0"
        assert result == expected
    
    def test_translate_multiple_values_to_solve(self):
        """Test: Find values for x and y such that... -> solve x = ... && y = ..."""
        english = "Find values for x and y such that x equals zero and y equals zero"
        result = self.translator.translate(english)
        expected = "solve x = 0 && y = 0"
        assert result == expected
    
    def test_translate_complement_phrase(self):
        """Test: the complement of x -> x'"""
        english = "the complement of x"
        result = self.translator.translate(english)
        expected = "x'"
        assert result == expected
    
    def test_translate_there_exists(self):
        """Test: there exists a where a equals zero -> {ex a a = 0}"""
        english = "there exists a where a equals zero"
        result = self.translator.translate(english)
        expected = "{ex a a = 0}"
        assert result == expected


class TestBidirectionalTranslation:
    """Test round-trip translation accuracy."""
    
    def setup_method(self):
        """Initialize bidirectional translator."""
        from tau_translator_omega.core_engine.bidirectional_translator import BidirectionalTranslator
        self.translator = BidirectionalTranslator()
    
    @pytest.mark.parametrize("tau_code", [
        "solve x = 0",
        "solve x = 0 && y = 0",
        "solve {a}:sbf x = 0",
        "solve x != 0 && x' != 0",
        "solve {ex a a = 0} x != 0 && {ex b b = 0} x != 0",
        "solve {ex x x = 0} a + {ex y y = 0} b = 0",
        "solve a x + b y = 0"
    ])
    def test_round_trip_translation(self, tau_code):
        """Test that Tau -> English -> Tau preserves meaning."""
        # Translate to English
        english = self.translator.tau_to_english(tau_code)
        assert english is not None
        
        # Translate back to Tau
        tau_result = self.translator.english_to_tau(english)
        assert tau_result is not None
        
        # Should match original (allowing for normalization)
        assert self.translator.normalize_tau(tau_result) == self.translator.normalize_tau(tau_code)