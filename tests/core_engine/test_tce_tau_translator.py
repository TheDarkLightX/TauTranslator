#!/usr/bin/env python3
"""
Comprehensive tests for TCE-to-Tau translator following TDD principles.

Tests cover:
- Basic expression translation
- Mathematical operations
- Function and predicate definitions
- Recurrence relations
- Bitvector operations
- Solver commands
- Temporal logic
- Boolean algebra
- Error handling and edge cases
"""

import pytest
from typing import List

from tau_translator_omega.core_engine.translators.tce_tau_translator import (
    TCETauTranslator, TranslationResult, TauTranslationError
)
from tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes import (
    VariableNode, ConstantNode, NumberNode, StringNode,
    ArithmeticBinaryOpNode, BooleanBinaryOpNode, BooleanUnaryOpNode,
    ComparisonNode, PredicateCallNode, StreamReferenceNode,
    FunctionDefinitionNode, PredicateDefinitionNode, RecurrenceDefinitionNode,
    RecurrenceCaseNode, BitvectorDeclarationNode, BitvectorOperationNode,
    BitvectorLiteralNode, SolverCommandNode, MathematicalAssertionNode,
    TemporalQuantifierNode, ConceptDeclarationNode, StreamDeclarationNode,
    MetaStatementNode, MetaFieldNode, EnhancedArithmeticNode,
    SetOperationNode, QuantifiedExpressionNode, ConditionalExpressionNode,
    FunctionCallWithIndexNode, ParameterNode, TimeLiteralNode
)


class TestTCETauTranslator:
    """Test suite for TCE-to-Tau translator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.translator = TCETauTranslator()
    
    # --- Basic Expression Tests ---
    
    def test_translate_variable(self):
        """Test variable translation."""
        node = VariableNode(name="X")
        result = self.translator._translate_node(node)
        assert result == "x"  # Tau uses lowercase
    
    def test_translate_number(self):
        """Test number translation."""
        node = NumberNode(value=42)
        result = self.translator._translate_node(node)
        assert result == "42"
    
    def test_translate_string(self):
        """Test string translation."""
        node = StringNode(value="hello")
        result = self.translator._translate_node(node)
        assert result == '"hello"'
    
    def test_translate_constant(self):
        """Test constant translation."""
        node = ConstantNode(value=3.14, value_type="NUMBER")
        result = self.translator._translate_node(node)
        assert result == "3.14"
    
    # --- Arithmetic Expression Tests ---
    
    def test_translate_arithmetic_addition(self):
        """Test arithmetic addition translation."""
        left = VariableNode(name="X")
        right = NumberNode(value=5)
        node = ArithmeticBinaryOpNode(left=left, operator="plus", right=right)
        
        result = self.translator._translate_node(node)
        assert result == "(x + 5)"
    
    def test_translate_arithmetic_multiplication(self):
        """Test arithmetic multiplication translation."""
        left = VariableNode(name="A")
        right = VariableNode(name="B")
        node = ArithmeticBinaryOpNode(left=left, operator="times", right=right)
        
        result = self.translator._translate_node(node)
        assert result == "(a * b)"
    
    def test_translate_enhanced_arithmetic_modulo(self):
        """Test enhanced arithmetic modulo operation."""
        left = VariableNode(name="X")
        right = NumberNode(value=3)
        node = EnhancedArithmeticNode(left=left, operator="modulo", right=right)
        
        result = self.translator._translate_node(node)
        assert result == "(x mod 3)"
    
    def test_translate_enhanced_arithmetic_power(self):
        """Test enhanced arithmetic power operation."""
        left = NumberNode(value=2)
        right = VariableNode(name="N")
        node = EnhancedArithmeticNode(left=left, operator="power", right=right)
        
        result = self.translator._translate_node(node)
        assert result == "(2 ^ n)"
    
    # --- Boolean Expression Tests ---
    
    def test_translate_boolean_and(self):
        """Test boolean AND translation."""
        left = VariableNode(name="P")
        right = VariableNode(name="Q")
        node = BooleanBinaryOpNode(left=left, operator="and", right=right)
        
        result = self.translator._translate_node(node)
        assert result == "(p & q)"
    
    def test_translate_boolean_not(self):
        """Test boolean NOT translation."""
        operand = VariableNode(name="P")
        node = BooleanUnaryOpNode(operator="not", operand=operand)
        
        result = self.translator._translate_node(node)
        assert result == "(~ p)"
    
    def test_translate_set_intersection(self):
        """Test set intersection translation."""
        left = VariableNode(name="A")
        right = VariableNode(name="B")
        node = SetOperationNode(left=left, operator="intersected_with", right=right)
        
        result = self.translator._translate_node(node)
        assert result == "(a & b)"
    
    def test_translate_set_complement(self):
        """Test set complement translation."""
        left = VariableNode(name="A")
        node = SetOperationNode(left=left, operator="complemented_by", right=None)
        
        result = self.translator._translate_node(node)
        assert result == "(a')"
    
    # --- Comparison Tests ---
    
    def test_translate_comparison_equals(self):
        """Test equality comparison translation."""
        left = VariableNode(name="X")
        right = NumberNode(value=10)
        node = ComparisonNode(left=left, operator="equals", right=right)
        
        result = self.translator._translate_node(node)
        assert result == "(x = 10)"
    
    def test_translate_comparison_greater_than(self):
        """Test greater than comparison translation."""
        left = VariableNode(name="Y")
        right = NumberNode(value=0)
        node = ComparisonNode(left=left, operator="is_greater_than", right=right)
        
        result = self.translator._translate_node(node)
        assert result == "(y > 0)"
    
    # --- Function Definition Tests ---
    
    def test_translate_function_definition(self):
        """Test function definition translation."""
        params = [ParameterNode(name="X"), ParameterNode(name="Y")]
        body = ArithmeticBinaryOpNode(
            left=VariableNode(name="X"),
            operator="plus",
            right=VariableNode(name="Y")
        )
        node = FunctionDefinitionNode(name="add", parameters=params, body=body)
        
        result = self.translator._translate_node(node)
        assert result == "add(x, y) := (x + y)"
        
        # Check that function is stored in context
        assert "add" in self.translator.context.function_definitions
    
    def test_translate_predicate_definition(self):
        """Test predicate definition translation."""
        params = [ParameterNode(name="X")]
        body = ComparisonNode(
            left=ArithmeticBinaryOpNode(
                left=VariableNode(name="X"),
                operator="modulo",
                right=NumberNode(value=2)
            ),
            operator="equals",
            right=NumberNode(value=0)
        )
        node = PredicateDefinitionNode(name="even", parameters=params, body=body)
        
        result = self.translator._translate_node(node)
        assert result == "even(x) := ((x mod 2) = 0)"
    
    def test_translate_predicate_call(self):
        """Test predicate call translation."""
        args = [VariableNode(name="X"), NumberNode(value=5)]
        node = PredicateCallNode(name="greater", args=args)
        
        result = self.translator._translate_node(node)
        assert result == "greater(x, 5)"
    
    # --- Recurrence Relations Tests ---
    
    def test_translate_recurrence_definition(self):
        """Test recurrence relation translation."""
        # Base case: fib[0](n) := 1
        base_case = RecurrenceCaseNode(
            index=0,
            parameters=[ParameterNode(name="N")],
            body=NumberNode(value=1)
        )
        
        # Recursive case: fib[n](x) := fib[n-1](x) + fib[n-2](x)
        recursive_case = RecurrenceCaseNode(
            index="n",
            parameters=[ParameterNode(name="X")],
            body=ArithmeticBinaryOpNode(
                left=FunctionCallWithIndexNode(
                    name="fib",
                    index=ArithmeticBinaryOpNode(
                        left=VariableNode(name="n"),
                        operator="minus",
                        right=NumberNode(value=1)
                    ),
                    arguments=[VariableNode(name="X")]
                ),
                operator="plus",
                right=FunctionCallWithIndexNode(
                    name="fib",
                    index=ArithmeticBinaryOpNode(
                        left=VariableNode(name="n"),
                        operator="minus",
                        right=NumberNode(value=2)
                    ),
                    arguments=[VariableNode(name="X")]
                )
            )
        )
        
        node = RecurrenceDefinitionNode(
            name="fib",
            base_cases=[base_case],
            recursive_cases=[recursive_case]
        )
        
        result = self.translator._translate_node(node)
        expected_lines = [
            "fib[0](n) := 1",
            "fib[n](x) := (fib[(n - 1)](x) + fib[(n - 2)](x))"
        ]
        assert result == "\n".join(expected_lines)
    
    def test_translate_function_call_with_index(self):
        """Test function call with index translation."""
        index = ArithmeticBinaryOpNode(
            left=VariableNode(name="n"),
            operator="minus",
            right=NumberNode(value=1)
        )
        args = [VariableNode(name="x")]
        node = FunctionCallWithIndexNode(name="factorial", index=index, arguments=args)
        
        result = self.translator._translate_node(node)
        assert result == "factorial[(n - 1)](x)"
    
    # --- Bitvector Tests ---
    
    def test_translate_bitvector_declaration(self):
        """Test bitvector declaration translation."""
        node = BitvectorDeclarationNode(name="data_word", width=32)
        
        result = self.translator._translate_node(node)
        assert result == "// bitvector data_word : width 32"
        
        # Check that bitvector is stored in context
        assert "data_word" in self.translator.context.bitvector_declarations
        assert self.translator.context.bitvector_declarations["data_word"] == 32
    
    def test_translate_bitvector_operation(self):
        """Test bitvector operation translation."""
        left = VariableNode(name="data")
        right = VariableNode(name="mask")
        node = BitvectorOperationNode(left=left, operator="and", right=right)
        
        result = self.translator._translate_node(node)
        assert result == "(data & mask)"
    
    def test_translate_bitvector_literal_hex(self):
        """Test hexadecimal bitvector literal translation."""
        node = BitvectorLiteralNode(value="0xFF", format="hex")
        
        result = self.translator._translate_node(node)
        assert result == "0xFF"
    
    def test_translate_bitvector_literal_binary(self):
        """Test binary bitvector literal translation."""
        node = BitvectorLiteralNode(value="0b1010", format="binary")
        
        result = self.translator._translate_node(node)
        assert result == "0b1010"
    
    # --- Solver Command Tests ---
    
    def test_translate_solver_satisfiability(self):
        """Test satisfiability check translation."""
        expression = BooleanBinaryOpNode(
            left=VariableNode(name="X"),
            operator="and",
            right=VariableNode(name="Y")
        )
        node = SolverCommandNode(command_type="satisfiability", expression=expression)
        
        result = self.translator._translate_node(node)
        assert result == "sat (x & y)"
    
    def test_translate_solver_solve_with_variables(self):
        """Test solve command with specific variables."""
        expression = ComparisonNode(
            left=ArithmeticBinaryOpNode(
                left=VariableNode(name="X"),
                operator="plus",
                right=VariableNode(name="Y")
            ),
            operator="equals",
            right=NumberNode(value=10)
        )
        node = SolverCommandNode(
            command_type="solve",
            expression=expression,
            variables=["X", "Y"]
        )
        
        result = self.translator._translate_node(node)
        assert result == "solve ((x + y) = 10) for X, Y"
    
    def test_translate_solver_normalize(self):
        """Test normalize command translation."""
        expression = BooleanBinaryOpNode(
            left=VariableNode(name="X"),
            operator="or",
            right=VariableNode(name="X")
        )
        node = SolverCommandNode(command_type="normalize", expression=expression)
        
        result = self.translator._translate_node(node)
        assert result == "normalize (x | x)"

    # --- Temporal Logic Tests ---

    def test_translate_temporal_always(self):
        """Test temporal 'always' quantifier translation."""
        expression = ComparisonNode(
            left=VariableNode(name="output"),
            operator="equals",
            right=NumberNode(value=0)
        )
        node = TemporalQuantifierNode(quantifier="always", expression=expression)

        result = self.translator._translate_node(node)
        assert result == "always (output = 0)"

    def test_translate_temporal_sometimes(self):
        """Test temporal 'sometimes' quantifier translation."""
        expression = VariableNode(name="error_condition")
        node = TemporalQuantifierNode(quantifier="sometimes", expression=expression)

        result = self.translator._translate_node(node)
        assert result == "sometimes error_condition"

    def test_translate_stream_reference_with_time(self):
        """Test stream reference with time specification."""
        time_spec = TimeLiteralNode(value=5)
        node = StreamReferenceNode(name="input_stream", time_spec=time_spec)

        result = self.translator._translate_node(node)
        assert result == "input_stream[5]"

    def test_translate_stream_reference_without_time(self):
        """Test stream reference without time specification."""
        node = StreamReferenceNode(name="output_stream")

        result = self.translator._translate_node(node)
        assert result == "output_stream"

    # --- Quantified Expression Tests ---

    def test_translate_quantified_for_all(self):
        """Test universal quantification translation."""
        variables = [VariableNode(name="X"), VariableNode(name="Y")]
        expression = ComparisonNode(
            left=ArithmeticBinaryOpNode(
                left=VariableNode(name="X"),
                operator="plus",
                right=VariableNode(name="Y")
            ),
            operator="equals",
            right=ArithmeticBinaryOpNode(
                left=VariableNode(name="Y"),
                operator="plus",
                right=VariableNode(name="X")
            )
        )
        node = QuantifiedExpressionNode(
            quantifier="for_all",
            variables=variables,
            expression=expression
        )

        result = self.translator._translate_node(node)
        assert result == "all x, y (((x + y) = (y + x)))"

    def test_translate_quantified_there_exists(self):
        """Test existential quantification translation."""
        variables = [VariableNode(name="Z")]
        expression = ComparisonNode(
            left=ArithmeticBinaryOpNode(
                left=VariableNode(name="Z"),
                operator="times",
                right=VariableNode(name="Z")
            ),
            operator="equals",
            right=NumberNode(value=4)
        )
        node = QuantifiedExpressionNode(
            quantifier="there_exists",
            variables=variables,
            expression=expression
        )

        result = self.translator._translate_node(node)
        assert result == "ex z (((z * z) = 4))"

    # --- Conditional Expression Tests ---

    def test_translate_conditional_if_then(self):
        """Test if-then conditional translation."""
        condition = ComparisonNode(
            left=VariableNode(name="X"),
            operator="is_greater_than",
            right=NumberNode(value=0)
        )
        consequent = VariableNode(name="positive")
        node = ConditionalExpressionNode(
            condition=condition,
            consequent=consequent,
            conditional_type="if_then"
        )

        result = self.translator._translate_node(node)
        assert result == "((x > 0) -> positive)"

    # --- High-Level Construct Tests ---

    def test_translate_mathematical_assertion(self):
        """Test mathematical assertion translation."""
        expression = ComparisonNode(
            left=VariableNode(name="X"),
            operator="equals",
            right=VariableNode(name="Y")
        )
        node = MathematicalAssertionNode(
            assertion_type="assert",
            expression=expression
        )

        result = self.translator._translate_node(node)
        assert result == "assert (x = y)"

    def test_translate_concept_declaration(self):
        """Test concept declaration translation."""
        node = ConceptDeclarationNode(
            name="consistency",
            description="a logical system where no contradiction can be derived"
        )

        result = self.translator._translate_node(node)
        assert result == "// concept: consistency - a logical system where no contradiction can be derived"

    def test_translate_stream_declaration(self):
        """Test stream declaration translation."""
        node = StreamDeclarationNode(
            identifier="mathematics.arithmetic_operations",
            version="v1.0.0"
        )

        result = self.translator._translate_node(node)
        assert result == "// stream: mathematics.arithmetic_operations v1.0.0"

    def test_translate_meta_statement(self):
        """Test meta statement translation."""
        fields = [
            MetaFieldNode(key="provides", value=["addition", "multiplication"]),
            MetaFieldNode(key="complexity", value="O(n)")
        ]
        node = MetaStatementNode(fields=fields)

        result = self.translator._translate_node(node)
        assert result == "// meta: provides: [addition, multiplication], complexity: O(n)"

    # --- Error Handling Tests ---

    def test_translate_unknown_node_type(self):
        """Test error handling for unknown node types."""
        # Create a mock node type that doesn't have a translation method
        class UnknownNode:
            pass

        node = UnknownNode()

        with pytest.raises(TauTranslationError) as exc_info:
            self.translator._translate_node(node)

        assert "No translation method for UnknownNode" in str(exc_info.value)

    def test_translate_unknown_arithmetic_operator(self):
        """Test error handling for unknown arithmetic operators."""
        left = VariableNode(name="X")
        right = VariableNode(name="Y")
        node = ArithmeticBinaryOpNode(left=left, operator="unknown_op", right=right)

        with pytest.raises(TauTranslationError) as exc_info:
            self.translator._translate_node(node)

        assert "Unknown arithmetic operator: unknown_op" in str(exc_info.value)

    def test_translate_unknown_solver_command(self):
        """Test error handling for unknown solver commands."""
        expression = VariableNode(name="X")
        node = SolverCommandNode(command_type="unknown_command", expression=expression)

        with pytest.raises(TauTranslationError) as exc_info:
            self.translator._translate_node(node)

        assert "Unknown solver command: unknown_command" in str(exc_info.value)

    # --- Integration Tests ---

    def test_translate_complete_result(self):
        """Test complete translation with result metadata."""
        # Simple arithmetic expression: X + 5
        left = VariableNode(name="X")
        right = NumberNode(value=5)
        node = ArithmeticBinaryOpNode(left=left, operator="plus", right=right)

        result = self.translator.translate(node)

        assert isinstance(result, TranslationResult)
        assert result.tau_code == "(x + 5)"
        assert result.errors == []
        assert result.warnings == []
        assert isinstance(result.metadata, dict)

    def test_translate_with_function_context(self):
        """Test translation that builds up context."""
        # Define a function first
        params = [ParameterNode(name="X"), ParameterNode(name="Y")]
        body = ArithmeticBinaryOpNode(
            left=VariableNode(name="X"),
            operator="times",
            right=VariableNode(name="Y")
        )
        func_node = FunctionDefinitionNode(name="multiply", parameters=params, body=body)

        # Translate the function
        result = self.translator.translate(func_node)

        assert result.tau_code == "multiply(x, y) := (x * y)"
        assert "multiply" in result.metadata["functions"]
        assert "multiply" in self.translator.context.function_definitions

    def test_translate_error_handling_in_main_method(self):
        """Test error handling in main translate method."""
        # Create a node that will cause an error during translation
        class ErrorNode:
            pass

        node = ErrorNode()
        result = self.translator.translate(node)

        assert result.tau_code == ""
        assert len(result.errors) > 0
        assert "No translation method for ErrorNode" in result.errors[0]
