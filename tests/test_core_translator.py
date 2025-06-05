"""
Unit Tests for Core Translator
===============================

Comprehensive tests for core translation functionality.
"""

import pytest
from src.tau_translator_omega.core_engine.core_translator import (
    CoreParser,
    CoreAST,
    CoreSemanticAnalyzer,
    TCEToTauTranslator
)


class TestCoreParser:
    """Test core parser functionality."""
    
    def test_parse_tce_valid(self):
        """Test parsing valid TCE input."""
        parser = CoreParser()
        
        # Test with period
        ast = parser.parse("x = 5.", "TCE")
        assert isinstance(ast, CoreAST)
        assert ast.text == "x = 5."
        assert ast.language == "TCE"
        
        # Test complex expression
        ast = parser.parse("x and y or z.", "TCE")
        assert ast.text == "x and y or z."
        
    def test_parse_tce_invalid(self):
        """Test parsing invalid TCE input."""
        parser = CoreParser()
        
        # Test empty input
        with pytest.raises(ValueError, match="Input cannot be empty"):
            parser.parse("", "TCE")
            
        # Test missing period
        with pytest.raises(SyntaxError, match="TCE input must end with period"):
            parser.parse("x = 5", "TCE")
            
    def test_parse_tau_valid(self):
        """Test parsing valid TAU input."""
        parser = CoreParser()
        
        # TAU doesn't require period
        ast = parser.parse("x & y", "TAU")
        assert isinstance(ast, CoreAST)
        assert ast.text == "x & y"
        assert ast.language == "TAU"
        
    def test_parse_whitespace_handling(self):
        """Test whitespace handling in parser."""
        parser = CoreParser()
        
        # Test with extra whitespace
        ast = parser.parse("  x = 5.  ", "TCE")
        assert ast.text == "  x = 5.  "
        
        # Test tabs and newlines
        ast = parser.parse("\tx = 5.\n", "TCE")
        assert ast.text == "\tx = 5.\n"


class TestCoreAST:
    """Test AST functionality."""
    
    def test_ast_type_detection(self):
        """Test AST type detection."""
        # Test predicate definition
        ast = CoreAST("define predicate p(x) as x > 0.", "TCE")
        assert ast.type == "predicate_definition"
        
        # Test function definition
        ast = CoreAST("define function f(x) as x + 1.", "TCE")
        assert ast.type == "function_definition"
        
        # Test stream definition
        ast = CoreAST("sbf tau bit 1.", "TCE")
        assert ast.type == "stream_definition"
        
        # Test stream rule
        ast = CoreAST("rule o[t] = i[t].", "TCE")
        assert ast.type == "stream_rule"
        
        # Test universal quantifier
        ast = CoreAST("for every x such that p(x).", "TCE")
        assert ast.type == "universal_quantifier"
        
        # Test existential quantifier
        ast = CoreAST("there exists x such that p(x).", "TCE")
        assert ast.type == "existential_quantifier"
        
        # Test implication
        ast = CoreAST("if x then y.", "TCE")
        assert ast.type == "implication"
        
        # Test temporal always
        ast = CoreAST("always x is true.", "TCE")
        assert ast.type == "temporal_always"
        
        # Test temporal sometimes
        ast = CoreAST("sometimes x happens.", "TCE")
        assert ast.type == "temporal_sometimes"
        
        # Test normalize
        ast = CoreAST("normalize x + y.", "TCE")
        assert ast.type == "normalize"
        
        # Test general expression
        ast = CoreAST("x = 5.", "TCE")
        assert ast.type == "expression"
        
    def test_ast_immutability(self):
        """Test that AST properties are set correctly."""
        ast = CoreAST("test text", "TAU")
        assert ast.text == "test text"
        assert ast.language == "TAU"
        assert ast.type == "expression"


class TestCoreSemanticAnalyzer:
    """Test semantic analyzer functionality."""
    
    def test_analyze_valid_tce(self):
        """Test analyzing valid TCE AST."""
        analyzer = CoreSemanticAnalyzer()
        ast = CoreAST("x = 5.", "TCE")
        
        analyzed_ast, errors = analyzer.analyze(ast)
        assert analyzed_ast == ast
        assert errors == []
        
    def test_analyze_invalid_tce(self):
        """Test analyzing invalid TCE AST."""
        analyzer = CoreSemanticAnalyzer()
        ast = CoreAST("x = 5", "TCE")  # Missing period
        
        analyzed_ast, errors = analyzer.analyze(ast)
        assert len(errors) == 1
        assert "Missing period" in errors[0]
        
    def test_analyze_tau(self):
        """Test analyzing TAU AST."""
        analyzer = CoreSemanticAnalyzer()
        ast = CoreAST("x & y", "TAU")
        
        analyzed_ast, errors = analyzer.analyze(ast)
        assert analyzed_ast == ast
        assert errors == []
        
    def test_analyze_with_vocabulary(self):
        """Test analyzing with vocabulary context."""
        vocab = {'predicates': {'valid': {'arity': 1}}}
        analyzer = CoreSemanticAnalyzer(vocab)
        ast = CoreAST("valid(x).", "TCE")
        
        analyzed_ast, errors = analyzer.analyze(ast)
        assert errors == []


class TestTCEToTauTranslator:
    """Test TCE to TAU translator."""
    
    def test_translate_basic_expressions(self):
        """Test translating basic expressions."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        # Test simple assignment
        ast = parser.parse("x = 5.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "x = 5"
        
        # Test boolean operations
        ast = parser.parse("x and y.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "x & y"
        
        ast = parser.parse("x or y.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "x \\\\ y"
        
        ast = parser.parse("x xor y.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "x + y"
        
        ast = parser.parse("not x.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "x'"
        
    def test_translate_definitions(self):
        """Test translating definitions."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        # Test predicate definition
        ast = parser.parse("define predicate valid(x) as x > 0.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "valid(x) := x > 0"
        
        # Test function definition
        ast = parser.parse("define function sum(a, b) as a + b.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "sum(a, b) := a + b"
        
    def test_translate_stream_operations(self):
        """Test translating stream operations."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        # Test stream output
        ast = parser.parse("output 1 at time t = 0.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "o1[t] = 0"
        
        # Test stream rule
        ast = parser.parse("rule o1[t] = i1[t] and i2[t].", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "o1[t] = i1[t] & i2[t]"
        
    def test_translate_quantifiers(self):
        """Test translating quantifiers."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        # Test universal quantifier
        ast = parser.parse("for every x such that x > 0.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "{all x} (x > 0)"
        
        # Test existential quantifier
        ast = parser.parse("there exists x such that x = 0.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "{ex x} (x = 0)"
        
    def test_translate_temporal_operators(self):
        """Test translating temporal operators."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        # Test always - with parentheses
        ast = parser.parse("always (x = 5).", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "always (x = 5)"
        
        # Test sometimes - with parentheses
        ast = parser.parse("sometimes (event occurs).", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "sometimes (event occurs)"
        
    def test_translate_implications(self):
        """Test translating implications."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        ast = parser.parse("if x > 0 then x is positive.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "(x > 0) -> x is positive"
        
    def test_translate_normalize(self):
        """Test translating normalize statements."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        ast = parser.parse("normalize x + y - z.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "normalize x + y - z"
        
    def test_translate_complex_expressions(self):
        """Test translating complex expressions."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        # Test nested operations
        ast = parser.parse("(x and y) or (z and w).", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "(x & y) \\\\ (z & w)"
        
        # Test complement
        ast = parser.parse("x complement.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "x'"
        
        # Test comparisons
        ast = parser.parse("x is less than y.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "x < y"
        
        ast = parser.parse("x is greater than y.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "x > y"
        
        ast = parser.parse("x equals y.", "TCE")
        result = translator.translate_to_tau(ast)
        assert result == "x = y"
        
    def test_translate_to_tce_reverse(self):
        """Test TAU to TCE reverse translation."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        # Test definition reverse
        ast = parser.parse("p(x) := x > 0", "TAU")
        result = translator.translate_to_tce(ast)
        assert result == "define predicate p(x) as x > 0."
        
        # Test simple expression
        ast = parser.parse("x & y", "TAU")
        result = translator.translate_to_tce(ast)
        assert result == "x & y."
        
    def test_edge_cases(self):
        """Test edge cases in translation."""
        translator = TCEToTauTranslator()
        parser = CoreParser()
        
        # Test empty expression body
        ast = CoreAST("", "TCE")
        ast.type = "expression"
        ast.text = "."
        result = translator.translate_to_tau(ast)
        assert result == ""
        
        # Test whitespace preservation
        ast = parser.parse("  x  =  5  .", "TCE")
        result = translator.translate_to_tau(ast)
        assert "x" in result and "5" in result


class TestIntegration:
    """Integration tests for the full translation pipeline."""
    
    def test_full_pipeline_tce_to_tau(self):
        """Test full TCE to TAU translation pipeline."""
        parser = CoreParser()
        analyzer = CoreSemanticAnalyzer()
        translator = TCEToTauTranslator()
        
        # Parse
        tce_input = "for every x such that bird(x) then can_fly(x)."
        ast = parser.parse(tce_input, "TCE")
        
        # Analyze
        analyzed_ast, errors = analyzer.analyze(ast)
        assert errors == []
        
        # Translate
        tau_output = translator.translate_to_tau(analyzed_ast)
        assert "{all x}" in tau_output
        assert "can_fly(x)" in tau_output
        
    def test_full_pipeline_with_errors(self):
        """Test pipeline with semantic errors."""
        parser = CoreParser()
        analyzer = CoreSemanticAnalyzer()
        translator = TCEToTauTranslator()
        
        # Parse invalid TCE (missing period)
        ast = CoreAST("x = 5", "TCE")
        
        # Analyze should catch error
        analyzed_ast, errors = analyzer.analyze(ast)
        assert len(errors) > 0
        
        # Translation should still work
        tau_output = translator.translate_to_tau(analyzed_ast)
        assert tau_output == "x = 5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])