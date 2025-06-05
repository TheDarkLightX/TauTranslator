#!/usr/bin/env python3
"""
Test Tau Demos with Grammar File
=================================

Development tests using tau.tgf grammar file (not distributed).
Users must provide their own tau.tgf file in the grammars directory.

Author: DarkLightX / Dana Edwards
"""

import pytest
from pathlib import Path
from typing import Optional
from src.tau_translator_omega.core_engine.tgf_grammar_loader import TGFGrammarLoader
from src.tau_translator_omega.core_engine.enhanced_parser import EnhancedParser


class TestTauDemosWithGrammar:
    """Test Tau demos using the actual tau.tgf grammar file."""
    
    @pytest.fixture(autouse=True)
    def setup_grammar(self):
        """Load tau.tgf if available."""
        self.grammar_loader = TGFGrammarLoader()
        self.tau_grammar_available = False
        
        # Check if user has provided tau.tgf
        tau_grammar_path = Path("grammars/tau.tgf")
        if tau_grammar_path.exists():
            grammar = self.grammar_loader.load_grammar_file("tau.tgf")
            if grammar:
                self.grammar_loader.set_active_grammar("tau.tgf")
                self.tau_grammar_available = True
                self.parser = EnhancedParser(grammar_loader=self.grammar_loader)
        
        if not self.tau_grammar_available:
            pytest.skip("tau.tgf not found. Please provide your own tau.tgf file in grammars/")
    
    def test_parse_solve_command(self):
        """Test parsing solve command from demo 2.2."""
        test_cases = [
            "solve x = 0",
            "solve x = 0 && y = 0",
            "solve {a}:sbf x = 0",
            "solve x != 0 && x' != 0",
            "solve {ex a a = 0} x != 0 && {ex b b = 0} x != 0",
            "solve {ex x x = 0} a + {ex y y = 0} b = 0",
            "solve a x + b y = 0"
        ]
        
        for tau_code in test_cases:
            # Parse with actual grammar
            result = self.parser.parse(tau_code)
            assert result is not None, f"Failed to parse: {tau_code}"
            
            # Verify it recognized as solve command
            assert result.type == "solve", f"Expected solve command, got {result.type}"
    
    def test_parse_stream_rules(self):
        """Test parsing stream-based rules."""
        test_cases = [
            "r o1[t] = i1[t] & i2[t]",
            "r output[t] = input[t-1]",
            "r y[t+1] = x[t] | z[t]",
            "sbf input_stream = ifile(\"data.txt\")",
            "sbf output_stream = ofile(\"result.txt\")"
        ]
        
        for tau_code in test_cases:
            result = self.parser.parse(tau_code)
            assert result is not None, f"Failed to parse: {tau_code}"
    
    def test_parse_temporal_logic(self):
        """Test parsing temporal logic expressions."""
        test_cases = [
            "always (x > y)",
            "sometimes (error = true)",
            "eventually (ready)",
            "[] (stable -> stable')",
            "<> (finished)"
        ]
        
        for tau_code in test_cases:
            result = self.parser.parse(tau_code)
            assert result is not None, f"Failed to parse: {tau_code}"
            
            # Verify temporal operator was recognized
            assert any(op in str(result) for op in ["always", "sometimes", "eventually", "[]", "<>"])
    
    def test_parse_quantifiers(self):
        """Test parsing quantified expressions."""
        test_cases = [
            "forall x : x > 0",
            "exists y : P(y)",
            "all x y z : x + y = z",
            "ex n : n * n = 4"
        ]
        
        for tau_code in test_cases:
            result = self.parser.parse(tau_code)
            assert result is not None, f"Failed to parse: {tau_code}"
    
    def test_parse_complex_expressions(self):
        """Test parsing complex combined expressions."""
        test_cases = [
            "always (forall x : x > 0 -> f(x) > 0)",
            "r decision[t] = (vote1[t] + vote2[t] + vote3[t]) > 1",
            "if x > y then max = x else max = y",
            "state[t+1] = state[t] & input[t]"
        ]
        
        for tau_code in test_cases:
            result = self.parser.parse(tau_code)
            assert result is not None, f"Failed to parse: {tau_code}"


class TestTranslationWithGrammar:
    """Test translation using parsed AST from tau.tgf grammar."""
    
    @pytest.fixture(autouse=True)
    def setup_translator(self):
        """Setup translator with grammar support."""
        self.grammar_loader = TGFGrammarLoader()
        
        tau_grammar_path = Path("grammars/tau.tgf")
        if not tau_grammar_path.exists():
            pytest.skip("tau.tgf not found")
            
        self.grammar_loader.load_grammar_file("tau.tgf")
        self.grammar_loader.set_active_grammar("tau.tgf")
        
        # Import grammar-aware translator
        from src.tau_translator_omega.core_engine.grammar_aware_translator import GrammarAwareTranslator
        self.translator = GrammarAwareTranslator(self.grammar_loader)
    
    def test_translate_solve_with_ast(self):
        """Test translating solve commands using parsed AST."""
        test_cases = [
            ("solve x = 0", "Find a value for x such that x equals zero"),
            ("solve x != 0 && x' != 0", "Find a value for x such that x is not equal to zero and the complement of x is not equal to zero"),
        ]
        
        for tau_code, expected_english in test_cases:
            result = self.translator.tau_to_english(tau_code)
            assert expected_english.lower() in result.lower()
    
    def test_translate_temporal_with_ast(self):
        """Test translating temporal logic using parsed AST."""
        test_cases = [
            ("always (x > y)", "it is always the case that x is greater than y"),
            ("sometimes (P)", "sometimes P holds"),
            ("eventually (done)", "eventually done will be true")
        ]
        
        for tau_code, expected_english in test_cases:
            result = self.translator.tau_to_english(tau_code)
            assert any(phrase in result.lower() for phrase in expected_english.lower().split())
    
    def test_roundtrip_with_grammar(self):
        """Test round-trip translation using grammar parsing."""
        test_cases = [
            "solve x = 0",
            "forall x : x > 0",
            "r o[t] = i[t]",
            "always (P && Q)"
        ]
        
        for original_tau in test_cases:
            # Tau -> English
            english = self.translator.tau_to_english(original_tau)
            assert english is not None
            
            # English -> Tau
            tau_result = self.translator.english_to_tau(english)
            assert tau_result is not None
            
            # Parse both to compare ASTs
            original_ast = self.translator.parse(original_tau)
            result_ast = self.translator.parse(tau_result)
            
            # ASTs should be equivalent
            assert self.translator.compare_asts(original_ast, result_ast)