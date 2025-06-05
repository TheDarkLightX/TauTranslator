"""
TDD Tests for TCE to TAU Translation
====================================

Test-Driven Development for core translation functionality.
Following VibeArchitect principles: Write tests first, then implement.
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tau_translator_omega.core_engine.parser import GrammarDrivenParser as Parser
from src.tau_translator_omega.core_engine.semantic_analyzer import SemanticAnalyzer


class TestTCEToTauTranslation:
    """TDD tests for TCE to TAU translation."""
    
    @pytest.fixture
    def translator(self):
        """Create translator instance."""
        return TCEToTauTranslator()
    
    # Basic constructs
    def test_translate_simple_fact(self, translator):
        """Test: x = 5. -> x = 5"""
        tce_input = "x = 5."
        expected_tau = "x = 5"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_predicate_definition(self, translator):
        """Test: define predicate bottom(x) as x = 0. -> bottom(x) := x = 0"""
        tce_input = "define predicate bottom(x) as x = 0."
        expected_tau = "bottom(x) := x = 0"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_function_definition(self, translator):
        """Test: define function halfAdderSum(a, b) as a xor b. -> halfAdderSum(a, b) := a + b"""
        tce_input = "define function halfAdderSum(a, b) as a xor b."
        expected_tau = "halfAdderSum(a, b) := a + b"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    # Boolean operations
    def test_translate_and_operation(self, translator):
        """Test: x and y. -> x & y"""
        tce_input = "x and y."
        expected_tau = "x & y"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_or_operation(self, translator):
        """Test: x or y. -> x \\ y"""
        tce_input = "x or y."
        expected_tau = "x \\ y"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_xor_operation(self, translator):
        """Test: x xor y. -> x + y"""
        tce_input = "x xor y."
        expected_tau = "x + y"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_not_operation(self, translator):
        """Test: not x. -> x'"""
        tce_input = "not x."
        expected_tau = "x'"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_complement_operation(self, translator):
        """Test: x complement. -> x'"""
        tce_input = "x complement."
        expected_tau = "x'"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    # Complex boolean expressions
    def test_translate_complex_boolean(self, translator):
        """Test: x and y or z. -> x & y \\ z"""
        tce_input = "x and y or z."
        expected_tau = "x & y \\ z"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_parenthesized_boolean(self, translator):
        """Test: (x or y) and z. -> (x \\ y) & z"""
        tce_input = "(x or y) and z."
        expected_tau = "(x \\ y) & z"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    # Quantifiers
    def test_translate_universal_quantifier(self, translator):
        """Test: for every x such that x > 0. -> {all x} (x > 0)"""
        tce_input = "for every x such that x > 0."
        expected_tau = "{all x} (x > 0)"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_existential_quantifier(self, translator):
        """Test: there exists x such that x = y. -> {ex x} (x = y)"""
        tce_input = "there exists x such that x = y."
        expected_tau = "{ex x} (x = y)"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_multiple_quantified_variables(self, translator):
        """Test: for every x, y such that x < y. -> {all x, y} (x < y)"""
        tce_input = "for every x, y such that x < y."
        expected_tau = "{all x, y} (x < y)"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    # Implications
    def test_translate_simple_implication(self, translator):
        """Test: if x > 5 then valid(x). -> (x > 5) -> valid(x)"""
        tce_input = "if x > 5 then valid(x)."
        expected_tau = "(x > 5) -> valid(x)"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_quantified_implication(self, translator):
        """Test: for every x if x > 0 then positive(x). -> {all x} ((x > 0) -> positive(x))"""
        tce_input = "for every x if x > 0 then positive(x)."
        expected_tau = "{all x} ((x > 0) -> positive(x))"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    # Stream operations
    def test_translate_stream_input(self, translator):
        """Test: sbf i1 = input file("input1.in"). -> sbf i1 = i("input1.in")"""
        tce_input = 'sbf i1 = input file("input1.in").'
        expected_tau = 'sbf i1 = i("input1.in")'
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_stream_output(self, translator):
        """Test: sbf o1 = output file("and.out"). -> sbf o1 = o("and.out")"""
        tce_input = 'sbf o1 = output file("and.out").'
        expected_tau = 'sbf o1 = o("and.out")'
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_stream_rule(self, translator):
        """Test: rule o1[t] = i1[t] and i2[t]. -> o1[t] = i1[t] & i2[t]"""
        tce_input = "rule o1[t] = i1[t] and i2[t]."
        expected_tau = "o1[t] = i1[t] & i2[t]"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_stream_time_offset(self, translator):
        """Test: rule o3[t] = i4[t-1] or i5[t+1]. -> o3[t] = i4[t-1] \\ i5[t+1]"""
        tce_input = "rule o3[t] = i4[t-1] or i5[t+1]."
        expected_tau = "o3[t] = i4[t-1] \\ i5[t+1]"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    # Temporal operators
    def test_translate_always_operator(self, translator):
        """Test: always x = 5. -> always (x = 5)"""
        tce_input = "always x = 5."
        expected_tau = "always (x = 5)"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_sometimes_operator(self, translator):
        """Test: sometimes x > 0. -> sometimes (x > 0)"""
        tce_input = "sometimes x > 0."
        expected_tau = "sometimes (x > 0)"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    # Comparisons
    def test_translate_equality(self, translator):
        """Test: x equals 5. -> x = 5"""
        tce_input = "x equals 5."
        expected_tau = "x = 5"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_inequality(self, translator):
        """Test: x != y. -> x != y"""
        tce_input = "x != y."
        expected_tau = "x != y"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_less_than(self, translator):
        """Test: x is less than y. -> x < y"""
        tce_input = "x is less than y."
        expected_tau = "x < y"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_greater_than(self, translator):
        """Test: x is greater than y. -> x > y"""
        tce_input = "x is greater than y."
        expected_tau = "x > y"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    # Complex real-world examples
    def test_translate_binary_adder(self, translator):
        """Test full adder carry function."""
        tce_input = "fullAdderCarry(a, b, c) := (a and b) or (a and c) or (b and c)."
        expected_tau = "fullAdderCarry(a, b, c) := (a & b) \\ (a & c) \\ (b & c)"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_majority_voting(self, translator):
        """Test democracy majority rule."""
        tce_input = "rule o1[t] = (i1[t] and i2[t]) or (i2[t] and i3[t]) or (i1[t] and i3[t])."
        expected_tau = "o1[t] = (i1[t] & i2[t]) \\ (i2[t] & i3[t]) \\ (i1[t] & i3[t])"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    def test_translate_normalize_statement(self, translator):
        """Test normalize statement."""
        tce_input = "normalize bit0(x) and bit1(x) and bit2(x) and bit3(x) and bit4(x)."
        expected_tau = "normalize bit0(x) & bit1(x) & bit2(x) & bit3(x) & bit4(x)"
        
        result = translator.translate(tce_input)
        assert result == expected_tau
    
    # Error cases
    def test_missing_period_error(self, translator):
        """Test error on missing period."""
        tce_input = "x = 5"
        
        with pytest.raises(SyntaxError, match="period"):
            translator.translate(tce_input)
    
    def test_empty_input_error(self, translator):
        """Test error on empty input."""
        tce_input = ""
        
        with pytest.raises(ValueError, match="empty"):
            translator.translate(tce_input)
    
    def test_invalid_syntax_error(self, translator):
        """Test error on invalid syntax."""
        tce_input = "this is not valid TCE."
        
        with pytest.raises(SyntaxError):
            translator.translate(tce_input)


# Now implement the translator to make tests pass
class TCEToTauTranslator:
    """TCE to TAU translator implementation."""
    
    def __init__(self):
        self.parser = Parser()
        self.analyzer = SemanticAnalyzer()
    
    def translate(self, tce_input: str) -> str:
        """Translate TCE input to TAU output."""
        if not tce_input:
            raise ValueError("Input cannot be empty")
        
        if not tce_input.strip().endswith('.'):
            raise SyntaxError("TCE input must end with period")
        
        # Remove trailing period for processing
        input_text = tce_input.strip()[:-1]
        
        # Handle different statement types
        if input_text.startswith("define predicate"):
            return self._translate_predicate_definition(input_text)
        elif input_text.startswith("define function"):
            return self._translate_function_definition(input_text)
        elif input_text.startswith("sbf"):
            return self._translate_stream_definition(input_text)
        elif input_text.startswith("rule"):
            return self._translate_stream_rule(input_text)
        elif input_text.startswith("for every"):
            return self._translate_universal_quantifier(input_text)
        elif input_text.startswith("there exists"):
            return self._translate_existential_quantifier(input_text)
        elif input_text.startswith("if"):
            return self._translate_implication(input_text)
        elif input_text.startswith("always"):
            return self._translate_temporal_always(input_text)
        elif input_text.startswith("sometimes"):
            return self._translate_temporal_sometimes(input_text)
        elif input_text.startswith("normalize"):
            return self._translate_normalize(input_text)
        else:
            return self._translate_expression(input_text)
    
    def _translate_predicate_definition(self, text: str) -> str:
        """Translate predicate definition."""
        # Extract parts: define predicate NAME(ARGS) as EXPR
        parts = text.split(" as ")
        if len(parts) != 2:
            raise SyntaxError("Invalid predicate definition")
        
        header = parts[0].replace("define predicate ", "")
        expr = self._translate_expression(parts[1])
        
        return f"{header} := {expr}"
    
    def _translate_function_definition(self, text: str) -> str:
        """Translate function definition."""
        # Extract parts: define function NAME(ARGS) as EXPR
        parts = text.split(" as ")
        if len(parts) != 2:
            raise SyntaxError("Invalid function definition")
        
        header = parts[0].replace("define function ", "")
        expr = self._translate_expression(parts[1])
        
        return f"{header} := {expr}"
    
    def _translate_stream_definition(self, text: str) -> str:
        """Translate stream definition."""
        if "input file" in text:
            # sbf i1 = input file("input1.in") -> sbf i1 = i("input1.in")
            text = text.replace("input file", "i")
        elif "output file" in text:
            # sbf o1 = output file("and.out") -> sbf o1 = o("and.out")
            text = text.replace("output file", "o")
        return text
    
    def _translate_stream_rule(self, text: str) -> str:
        """Translate stream rule."""
        # Remove "rule" prefix
        text = text[5:].strip()
        
        # Split on = to get left and right sides
        parts = text.split(" = ", 1)
        if len(parts) != 2:
            raise SyntaxError("Invalid rule syntax")
        
        left = parts[0]
        right = self._translate_expression(parts[1])
        
        return f"{left} = {right}"
    
    def _translate_universal_quantifier(self, text: str) -> str:
        """Translate universal quantifier."""
        # for every x such that EXPR -> {all x} (EXPR)
        # for every x, y such that EXPR -> {all x, y} (EXPR)
        
        # Extract variables
        var_part = text[10:]  # Remove "for every "
        if " such that " in var_part:
            vars_text, expr_text = var_part.split(" such that ", 1)
            expr = self._translate_expression(expr_text)
            return f"{{all {vars_text}}} ({expr})"
        else:
            # No condition, just variables
            return f"{{all {var_part}}}"
    
    def _translate_existential_quantifier(self, text: str) -> str:
        """Translate existential quantifier."""
        # there exists x such that EXPR -> {ex x} (EXPR)
        
        # Extract variables
        var_part = text[13:]  # Remove "there exists "
        if " such that " in var_part:
            vars_text, expr_text = var_part.split(" such that ", 1)
            expr = self._translate_expression(expr_text)
            return f"{{ex {vars_text}}} ({expr})"
        else:
            # No condition, just variables
            return f"{{ex {var_part}}}"
    
    def _translate_implication(self, text: str) -> str:
        """Translate implication."""
        # if COND then EXPR -> (COND) -> EXPR
        text = text[3:]  # Remove "if "
        
        parts = text.split(" then ", 1)
        if len(parts) != 2:
            raise SyntaxError("Invalid implication syntax")
        
        condition = self._translate_expression(parts[0])
        consequent = self._translate_expression(parts[1])
        
        return f"({condition}) -> {consequent}"
    
    def _translate_temporal_always(self, text: str) -> str:
        """Translate temporal always."""
        expr = text[7:].strip()  # Remove "always "
        translated_expr = self._translate_expression(expr)
        return f"always ({translated_expr})"
    
    def _translate_temporal_sometimes(self, text: str) -> str:
        """Translate temporal sometimes."""
        expr = text[10:].strip()  # Remove "sometimes "
        translated_expr = self._translate_expression(expr)
        return f"sometimes ({translated_expr})"
    
    def _translate_normalize(self, text: str) -> str:
        """Translate normalize statement."""
        expr = text[10:].strip()  # Remove "normalize "
        translated_expr = self._translate_expression(expr)
        return f"normalize {translated_expr}"
    
    def _translate_expression(self, expr: str) -> str:
        """Translate general expression."""
        # Handle boolean operators
        expr = self._translate_boolean_ops(expr)
        
        # Handle comparison operators
        expr = self._translate_comparisons(expr)
        
        # Handle complement
        expr = expr.replace(" complement", "'")
        
        return expr
    
    def _translate_boolean_ops(self, expr: str) -> str:
        """Translate boolean operators preserving precedence."""
        # Need to handle parentheses properly
        
        # Simple approach: replace operators
        # More sophisticated parsing would use AST
        
        # Replace operators (be careful with order)
        expr = expr.replace(" xor ", " + ")
        expr = expr.replace(" and ", " & ")
        expr = expr.replace(" or ", " \\ ")
        
        # Handle "not" prefix
        if expr.startswith("not "):
            expr = expr[4:] + "'"
        
        return expr
    
    def _translate_comparisons(self, expr: str) -> str:
        """Translate comparison operators."""
        expr = expr.replace(" equals ", " = ")
        expr = expr.replace(" is less than ", " < ")
        expr = expr.replace(" is greater than ", " > ")
        
        return expr