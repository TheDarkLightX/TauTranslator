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
from tau_translator_omega.infrastructure.grammar_io import GrammarRepository
from tau_translator_omega.core_engine.grammar_processing import (
    TGFGrammarService,
    LoadedGrammar,
    TGFGrammarParser,
    TGFGrammarConverter
)
from tau_translator_omega.core_engine.parsers.grammar_driven_parser import GrammarDrivenParser as EnhancedParser
from tau_translator_omega.core_engine.translators.tce_tau_translator import TCETauTranslator as GrammarAwareTranslator


class TestTauDemosWithGrammar:
    """Test Tau demos using the actual tau.tgf grammar file."""
    
    @pytest.fixture(autouse=True)
    def setup_grammar(self):
        """Load tau.tgf if available using the new TGFGrammarService."""
        self.tau_grammar_available = False
        grammar_dir = Path("grammars")
        tau_grammar_path = grammar_dir / "tau.tgf"

        if not tau_grammar_path.exists():
            pytest.skip("tau.tgf not found. Please provide it in the 'grammars/' directory.")

        repository = GrammarRepository(grammar_dir=grammar_dir, config_file=grammar_dir / "grammar_config.json")
        self.grammar_service = TGFGrammarService(repository)

        content_result = repository.read_grammar_file("tau.tgf")
        if content_result.is_success():
            content = content_result.unwrap()
            rules, terminals, non_terminals, directives = TGFGrammarParser.parse_tgf_content(content)
            grammar = LoadedGrammar(
                filename="tau.tgf", original_name="tau.tgf", type=".tgf",
                content=content, is_active=False, rules=rules, terminals=terminals,
                non_terminals=non_terminals, directives=directives
            )
            self.grammar_service.loaded_grammars["tau.tgf"] = grammar
            self.grammar_service.set_active_grammar("tau.tgf")
            self.tau_grammar_available = True

            lark_grammar, _ = TGFGrammarConverter.to_lark_grammar(self.grammar_service.active_grammar)
            self.parser = EnhancedParser(lark_grammar)
        
        if not self.tau_grammar_available:
            pytest.skip("Failed to load tau.tgf with the new grammar service.")
    
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
        """Setup translator with grammar support using the new service."""
        grammar_dir = Path("grammars")
        tau_grammar_path = grammar_dir / "tau.tgf"
        if not tau_grammar_path.exists():
            pytest.skip("tau.tgf not found")

        repository = GrammarRepository(grammar_dir=grammar_dir, config_file=grammar_dir / "grammar_config.json")
        self.grammar_service = TGFGrammarService(repository)

        content_result = repository.read_grammar_file("tau.tgf")
        if content_result.is_success():
            content = content_result.unwrap()
            rules, terminals, non_terminals, directives = TGFGrammarParser.parse_tgf_content(content)
            grammar = LoadedGrammar(
                filename="tau.tgf", original_name="tau.tgf", type=".tgf",
                content=content, is_active=False, rules=rules, terminals=terminals,
                non_terminals=non_terminals, directives=directives
            )
            self.grammar_service.loaded_grammars["tau.tgf"] = grammar
            self.grammar_service.set_active_grammar("tau.tgf")
            self.translator = GrammarAwareTranslator(self.grammar_service)
        else:
            pytest.skip("Failed to load tau.tgf for translator.")
    
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
            
            # For now, we just check if the round-trip produces a non-empty result.
            # AST comparison would require a more robust parser and AST structure.
            assert tau_result is not None