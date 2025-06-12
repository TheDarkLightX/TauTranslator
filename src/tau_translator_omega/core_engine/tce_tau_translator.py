#!/usr/bin/env python3
"""
TCE-to-Tau Translator - Core Translation Engine

Phase 2 of TauTranslatorOmega development roadmap.
Translates TCE (Tau Controlled English) AST to Tau Language constructs.

Features:
- Mathematical expression translation
- Function and predicate definitions
- Recurrence relations
- Bitvector operations
- Solver command integration
- Temporal logic constructs
- Boolean algebra operations

Design Principles:
- 1:1 semantic mapping between TCE and Tau
- Preserve mathematical meaning through translation
- Type safety and validation
- Comprehensive error handling
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import logging

# Import AST nodes
from .cnl_parser.ast_nodes import (
    ASTNode, VariableNode, ConstantNode, NumberNode, StringNode,
    ArithmeticBinaryOpNode, BooleanBinaryOpNode, BooleanUnaryOpNode,
    ComparisonNode, PredicateCallNode, StreamReferenceNode,
    # Sentence-level nodes
    SentenceNode, FactNode, RuleNode, ConditionNode, DefinitionNode,
    # Enhanced mathematical nodes
    FunctionDefinitionNode, PredicateDefinitionNode, RecurrenceDefinitionNode,
    RecurrenceCaseNode, BitvectorDeclarationNode, BitvectorOperationNode,
    BitvectorLiteralNode, SolverCommandNode, MathematicalAssertionNode,
    TemporalQuantifierNode, ConceptDeclarationNode, StreamDeclarationNode,
    MetaStatementNode, MetaFieldNode, EnhancedArithmeticNode,
    SetOperationNode, QuantifiedExpressionNode, ConditionalExpressionNode,
    FunctionCallWithIndexNode
)


@dataclass
class TranslationResult:
    """Result of TCE-to-Tau translation."""
    tau_code: str
    warnings: List[str]
    errors: List[str]
    metadata: Dict[str, Any]


@dataclass
class TranslationContext:
    """Context for translation process."""
    function_definitions: Dict[str, str]
    predicate_definitions: Dict[str, str]
    variable_types: Dict[str, str]
    bitvector_declarations: Dict[str, int]
    current_scope: str
    indentation_level: int = 0


class TauTranslationError(Exception):
    """Exception raised during TCE-to-Tau translation."""
    pass


class TCETauTranslator:
    """
    Core translator from TCE AST to Tau Language.
    
    Implements visitor pattern for systematic AST traversal and translation.
    Maintains translation context for type checking and scope management.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.context = TranslationContext(
            function_definitions={},
            predicate_definitions={},
            variable_types={},
            bitvector_declarations={},
            current_scope="global"
        )
        
        # Accurate operator mapping from TCE to Tau Language
        self.boolean_function_operators = {
            # BF (Boolean Function) operators from Tau grammar
            "union": "|",
            "or": "|",
            "xor": "+",
            "intersection": "&",
            "and": "&",
            "complement": "'",
            "not": "'"
        }

        self.wff_operators = {
            # WFF (Well-Formed Formula) operators from Tau grammar
            "implies": "->",
            "is_implied_by": "<-",
            "if_and_only_if": "<->",
            "or": "||",
            "and": "&&",
            "xor": "^",
            "not": "!"
        }

        self.relational_operators = {
            # Relational operators for BF comparisons
            "equals": "=",
            "not_equals": "!=",
            "less_than": "<",
            "greater_than": ">",
            "less_than_or_equal": "<=",
            "greater_than_or_equal": ">="
        }

        self.temporal_quantifiers = {
            # Temporal logic operators
            "always": "always",
            "sometimes": "sometimes"
        }

        self.quantifiers = {
            # Universal and existential quantifiers
            "for_all": "all",
            "all": "all",
            "there_exists": "ex",
            "ex": "ex"
        }

        self.solver_commands = {
            # CLI commands for solver integration
            "check_satisfiability_of": "sat",
            "sat": "sat",
            "check_validity_of": "valid",
            "valid": "valid",
            "check_unsatisfiability_of": "unsat",
            "unsat": "unsat",
            "solve": "solve",
            "find_solution_to": "solve",
            "normalize": "normalize",
            "simplify": "normalize",
            "eliminate_quantifiers_from": "qelim",
            "qelim": "qelim",
            "disjunctive_normal_form": "dnf",
            "dnf": "dnf",
            "conjunctive_normal_form": "cnf",
            "cnf": "cnf",
            "negation_normal_form": "nnf",
            "nnf": "nnf",
            "minterm_normal_form": "mnf",
            "mnf": "mnf",
            "strong_normal_form": "snf",
            "snf": "snf"
        }

        self.arithmetic_operators = {
            # Arithmetic operators
            "plus": "+",
            "minus": "-",
            "times": "*",
            "divided_by": "/",
            "mod": "%",
            "power": "**"
        }

        self.comparison_operators = {
            # Comparison operators
            "=": "=",
            "equals": "=",
            "not_equals": "!=",
            "!=": "!=",
            "<": "<",
            "less_than": "<",
            ">": ">", 
            "greater_than": ">",
            "<=": "<=",
            "less_than_or_equal": "<=",
            ">=": ">=",
            "greater_than_or_equal": ">="
        }

        self.boolean_operators = {
            # Boolean operators
            "and": "&",
            "or": "|",
            "not": "'",
            "xor": "^"
        }

    def translate(self, ast_node: ASTNode) -> TranslationResult:
        """
        Main translation entry point.
        
        Args:
            ast_node: Root AST node to translate
            
        Returns:
            TranslationResult with Tau code and metadata
        """
        try:
            self.logger.info(f"Starting translation of {type(ast_node).__name__}")
            
            # Reset context for new translation
            self.context = TranslationContext(
                function_definitions={},
                predicate_definitions={},
                variable_types={},
                bitvector_declarations={},
                current_scope="global"
            )
            
            tau_code = self._translate_node(ast_node)
            
            return TranslationResult(
                tau_code=tau_code,
                warnings=[],
                errors=[],
                metadata={
                    "functions": list(self.context.function_definitions.keys()),
                    "predicates": list(self.context.predicate_definitions.keys()),
                    "bitvectors": list(self.context.bitvector_declarations.keys())
                }
            )
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            return TranslationResult(
                tau_code="",
                warnings=[],
                errors=[str(e)],
                metadata={}
            )

    def _translate_node(self, node: ASTNode) -> str:
        """
        Translate a single AST node using visitor pattern.
        
        Args:
            node: AST node to translate
            
        Returns:
            Tau language string representation
        """
        method_name = f"_translate_{type(node).__name__.lower().replace('node', '')}"
        
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            raise TauTranslationError(f"No translation method for {type(node).__name__}")

    # --- Basic Expression Translation ---
    
    def _translate_variable(self, node: VariableNode) -> str:
        """Translate variable references."""
        return node.name.lower()  # Tau uses lowercase variables
    
    def _translate_constant(self, node: ConstantNode) -> str:
        """Translate constant values."""
        if node.value_type == "NUMBER":
            return str(node.value)
        elif node.value_type == "STRING":
            return f'"{node.value}"'
        else:
            return str(node.value)
    
    def _translate_number(self, node: NumberNode) -> str:
        """Translate numeric literals."""
        return str(node.value)
    
    def _translate_string(self, node: StringNode) -> str:
        """Translate string literals."""
        return f'"{node.value}"'

    # --- Arithmetic Expression Translation ---
    
    def _translate_arithmeticbinaryop(self, node: ArithmeticBinaryOpNode) -> str:
        """Translate arithmetic binary operations."""
        left = self._translate_node(node.left)
        right = self._translate_node(node.right)
        
        if node.operator in self.arithmetic_operators:
            tau_op = self.arithmetic_operators[node.operator]
            return f"({left} {tau_op} {right})"
        else:
            raise TauTranslationError(f"Unknown arithmetic operator: {node.operator}")
    
    def _translate_enhancedarithmetic(self, node: EnhancedArithmeticNode) -> str:
        """Translate enhanced arithmetic operations."""
        left = self._translate_node(node.left)
        right = self._translate_node(node.right)
        
        if node.operator in self.arithmetic_operators:
            tau_op = self.arithmetic_operators[node.operator]
            return f"({left} {tau_op} {right})"
        else:
            raise TauTranslationError(f"Unknown enhanced arithmetic operator: {node.operator}")
    
    # Arithmetic unary operations not implemented in simple AST nodes

    # --- Boolean Expression Translation ---
    
    def _translate_booleanbinaryop(self, node: BooleanBinaryOpNode) -> str:
        """Translate boolean binary operations."""
        left = self._translate_node(node.left)
        right = self._translate_node(node.right)
        
        if node.operator in self.boolean_operators:
            tau_op = self.boolean_operators[node.operator]
            return f"({left} {tau_op} {right})"
        else:
            raise TauTranslationError(f"Unknown boolean operator: {node.operator}")
    
    def _translate_booleanunaryop(self, node: BooleanUnaryOpNode) -> str:
        """Translate boolean unary operations."""
        operand = self._translate_node(node.operand)
        
        if node.operator in self.boolean_operators:
            tau_op = self.boolean_operators[node.operator]
            return f"({tau_op} {operand})"
        else:
            raise TauTranslationError(f"Unknown boolean unary operator: {node.operator}")
    
    def _translate_setoperation(self, node: SetOperationNode) -> str:
        """Translate set operations (Boolean algebra)."""
        left = self._translate_node(node.left)
        
        if node.operator == "complemented_by" and node.right is None:
            # Unary complement operation
            return f"({left}')"
        elif node.right is not None:
            right = self._translate_node(node.right)
            if node.operator in self.boolean_operators:
                tau_op = self.boolean_operators[node.operator]
                return f"({left} {tau_op} {right})"
        
        raise TauTranslationError(f"Invalid set operation: {node.operator}")

    # --- Comparison Translation ---
    
    def _translate_comparison(self, node: ComparisonNode) -> str:
        """Translate comparison operations."""
        left = self._translate_node(node.left)
        right = self._translate_node(node.right)
        
        if node.operator in self.comparison_operators:
            tau_op = self.comparison_operators[node.operator]
            return f"({left} {tau_op} {right})"
        else:
            raise TauTranslationError(f"Unknown comparison operator: {node.operator}")

    # --- Function and Predicate Translation ---
    
    def _translate_functiondefinition(self, node: FunctionDefinitionNode) -> str:
        """Translate function definitions."""
        params = ", ".join(param.name.lower() for param in node.parameters)
        body = self._translate_node(node.body)
        
        # Store function definition in context
        self.context.function_definitions[node.name] = f"{node.name}({params}) := {body}"
        
        return f"{node.name}({params}) := {body}"
    
    def _translate_predicatedefinition(self, node: PredicateDefinitionNode) -> str:
        """Translate predicate definitions."""
        params = ", ".join(param.name.lower() for param in node.parameters)
        body = self._translate_node(node.body)
        
        # Store predicate definition in context
        self.context.predicate_definitions[node.name] = f"{node.name}({params}) := {body}"
        
        return f"{node.name}({params}) := {body}"
    
    def _translate_predicatecall(self, node: PredicateCallNode) -> str:
        """Translate predicate/function calls."""
        args = ", ".join(self._translate_node(arg) for arg in node.args)
        return f"{node.name}({args})"

    # --- Recurrence Relations Translation ---

    def _translate_recurrencedefinition(self, node: RecurrenceDefinitionNode) -> str:
        """Translate recurrence relation definitions."""
        translations = []

        # Translate base cases
        for base_case in node.base_cases:
            translations.append(self._translate_recurrencecase(base_case, node.name))

        # Translate recursive cases
        for recursive_case in node.recursive_cases:
            translations.append(self._translate_recurrencecase(recursive_case, node.name))

        return "\n".join(translations)

    def _translate_recurrencecase(self, node: RecurrenceCaseNode, function_name: str) -> str:
        """Translate a single recurrence case."""
        params = ", ".join(param.name.lower() for param in node.parameters)
        body = self._translate_node(node.body)

        return f"{function_name}[{node.index}]({params}) := {body}"

    def _translate_functioncallwithindex(self, node: FunctionCallWithIndexNode) -> str:
        """Translate function calls with index (for recurrence relations)."""
        index = self._translate_node(node.index)
        args = ", ".join(self._translate_node(arg) for arg in node.arguments)
        return f"{node.name}[{index}]({args})"

    # --- Bitvector Translation ---

    def _translate_bitvectordeclaration(self, node: BitvectorDeclarationNode) -> str:
        """Translate bitvector declarations."""
        # Store bitvector declaration in context
        self.context.bitvector_declarations[node.name] = node.width

        # Tau doesn't have explicit bitvector declarations in the syntax we've seen
        # This would be handled by the type system or solver backend
        return f"// bitvector {node.name} : width {node.width}"

    def _translate_bitvectoroperation(self, node: BitvectorOperationNode) -> str:
        """Translate bitvector operations."""
        left = self._translate_node(node.left)
        right = self._translate_node(node.right)

        # Map bitvector operations to Tau equivalents
        bitvector_ops = {
            "and": "&",
            "or": "|",
            "xor": "^",
            "shift_left": "<<",
            "shift_right": ">>",
            "concatenated_with": "++"  # Conceptual - may need adjustment
        }

        if node.operator in bitvector_ops:
            tau_op = bitvector_ops[node.operator]
            return f"({left} {tau_op} {right})"
        else:
            raise TauTranslationError(f"Unknown bitvector operator: {node.operator}")

    def _translate_bitvectorliteral(self, node: BitvectorLiteralNode) -> str:
        """Translate bitvector literals."""
        if node.format == "hex":
            return node.value  # Keep as 0xFF
        elif node.format == "binary":
            return node.value  # Keep as 0b1010
        else:
            return node.value

    # --- Solver Commands Translation ---

    def _translate_solvercommand(self, node: SolverCommandNode) -> str:
        """Translate solver commands."""
        expression = self._translate_node(node.expression)

        if node.command_type in self.solver_commands:
            tau_cmd = self.solver_commands[node.command_type]

            if node.command_type == "solve" and node.variables:
                # For solve commands with specific variables
                vars_str = ", ".join(node.variables)
                return f"{tau_cmd} {expression} for {vars_str}"
            else:
                return f"{tau_cmd} {expression}"
        else:
            raise TauTranslationError(f"Unknown solver command: {node.command_type}")

    # --- Temporal Logic Translation ---

    def _translate_temporalquantifier(self, node: TemporalQuantifierNode) -> str:
        """Translate temporal quantifiers."""
        expression = self._translate_node(node.expression)

        if node.quantifier in self.temporal_quantifiers:
            tau_quantifier = self.temporal_quantifiers[node.quantifier]
            return f"{tau_quantifier} {expression}"
        else:
            raise TauTranslationError(f"Unknown temporal quantifier: {node.quantifier}")

    def _translate_streamreference(self, node: StreamReferenceNode) -> str:
        """Translate stream references."""
        base_name = node.name.lower()

        if node.time_spec:
            time_spec = self._translate_node(node.time_spec)
            return f"{base_name}[{time_spec}]"
        else:
            return base_name

    # Time specification methods removed - not in simple AST nodes

    # --- Quantified Expressions Translation ---

    def _translate_quantifiedexpression(self, node: QuantifiedExpressionNode) -> str:
        """Translate quantified expressions."""
        variables = ", ".join(var.name.lower() for var in node.variables)
        expression = self._translate_node(node.expression)

        if node.quantifier == "for_all":
            return f"all {variables} ({expression})"
        elif node.quantifier == "there_exists":
            return f"ex {variables} ({expression})"
        else:
            raise TauTranslationError(f"Unknown quantifier: {node.quantifier}")

    # Quantifier block methods removed - not in simple AST nodes

    # --- Conditional Expressions Translation ---

    def _translate_conditionalexpression(self, node: ConditionalExpressionNode) -> str:
        """Translate conditional expressions."""
        condition = self._translate_node(node.condition)
        consequent = self._translate_node(node.consequent)

        # All conditional types map to implication in Tau
        return f"({condition} -> {consequent})"

    # --- High-Level Constructs Translation ---

    def _translate_mathematicalassertion(self, node: MathematicalAssertionNode) -> str:
        """Translate mathematical assertions."""
        expression = self._translate_node(node.expression)

        if node.assertion_type == "assert":
            return f"assert {expression}"
        elif node.assertion_type == "constraint":
            return f"constraint {expression}"
        else:
            return expression  # Default to just the expression

    def _translate_conceptdeclaration(self, node: ConceptDeclarationNode) -> str:
        """Translate concept declarations."""
        # Concept declarations are typically comments in Tau
        if node.description:
            return f"// concept: {node.name} - {node.description}"
        else:
            return f"// concept: {node.name}"

    def _translate_streamdeclaration(self, node: StreamDeclarationNode) -> str:
        """Translate stream declarations."""
        if node.version:
            return f"// stream: {node.identifier} {node.version}"
        else:
            return f"// stream: {node.identifier}"

    def _translate_metastatement(self, node: MetaStatementNode) -> str:
        """Translate meta statements."""
        fields = []
        for field in node.fields:
            field_str = self._translate_metafield(field)
            fields.append(field_str)

        return f"// meta: {', '.join(fields)}"

    def _translate_metafield(self, node: MetaFieldNode) -> str:
        """Translate meta fields."""
        if isinstance(node.value, list):
            value_str = f"[{', '.join(node.value)}]"
        else:
            value_str = str(node.value)

        return f"{node.key}: {value_str}"

    # --- Sentence-Level Translation ---

    def _translate_sentence(self, node: SentenceNode) -> str:
        """Translate sentence nodes."""
        translations = []
        for content_node in node.content:
            translation = self._translate_node(content_node)
            translations.append(translation)

        return "\n".join(translations)

    def _translate_fact(self, node: FactNode) -> str:
        """Translate fact nodes."""
        return self._translate_node(node.statement)

    def _translate_rule(self, node: RuleNode) -> str:
        """Translate rule nodes."""
        condition = self._translate_node(node.condition)
        consequent = self._translate_node(node.consequent)

        return f"({condition} -> {consequent})"

    def _translate_condition(self, node: ConditionNode) -> str:
        """Translate condition nodes."""
        expression = self._translate_node(node.expression)

        if node.quant_block:
            quant_block = self._translate_node(node.quant_block)
            return f"{quant_block} {expression}"
        else:
            return expression

    def _translate_definition(self, node: DefinitionNode) -> str:
        """Translate definition nodes."""
        params = ", ".join(param.name.lower() for param in node.parameters)
        body = self._translate_node(node.body)

        if node.is_function:
            return f"{node.name}({params}) := {body}"
        else:
            # Predicate definition
            return f"{node.name}({params}) := {body}"

    # --- Accurate Tau Language Translation Methods ---

    def _translate_stream_definition(self, stream_type: str, variable: str, source: str) -> str:
        """Translate stream definitions (maps to sbf declarations)."""
        return f"sbf {variable} = {source}"

    def _translate_input_stream(self, filename: str) -> str:
        """Translate input stream sources."""
        return f'ifile("{filename}")'

    def _translate_output_stream(self, filename: str) -> str:
        """Translate output stream sources."""
        return f'ofile("{filename}")'

    def _translate_rule_definition(self, stream_ref: str, expression: str) -> str:
        """Translate rule definitions (maps to r stream[t] = expression)."""
        return f"r {stream_ref} = {expression}"

    def _translate_wff_expression(self, node) -> str:
        """Translate WFF (Well-Formed Formula) expressions."""
        # This would handle the complex WFF grammar from Tau
        # For now, delegate to existing boolean expression handling
        return self._translate_node(node)

    def _translate_bf_expression(self, node) -> str:
        """Translate BF (Boolean Function) expressions."""
        # This would handle the BF grammar from Tau
        # For now, delegate to existing boolean expression handling
        return self._translate_node(node)

    def _translate_temporal_quantifier_accurate(self, quantifier: str, expression: str) -> str:
        """Translate temporal quantifiers accurately."""
        if quantifier in self.temporal_quantifiers:
            tau_quantifier = self.temporal_quantifiers[quantifier]
            return f"{tau_quantifier} {expression}"
        else:
            raise TauTranslationError(f"Unknown temporal quantifier: {quantifier}")

    def _translate_quantified_expression_accurate(self, quantifier: str, variables: list, expression: str) -> str:
        """Translate quantified expressions accurately."""
        if quantifier in self.quantifiers:
            tau_quantifier = self.quantifiers[quantifier]
            vars_str = ", ".join(variables)
            return f"{tau_quantifier} {vars_str} ({expression})"
        else:
            raise TauTranslationError(f"Unknown quantifier: {quantifier}")

    def _translate_relational_expression(self, left: str, operator: str, right: str) -> str:
        """Translate relational expressions (BF comparisons)."""
        if operator in self.relational_operators:
            tau_op = self.relational_operators[operator]
            return f"({left} {tau_op} {right})"
        else:
            raise TauTranslationError(f"Unknown relational operator: {operator}")

    def _translate_wff_operator(self, left: str, operator: str, right: str) -> str:
        """Translate WFF operators."""
        if operator in self.wff_operators:
            tau_op = self.wff_operators[operator]
            return f"({left} {tau_op} {right})"
        else:
            raise TauTranslationError(f"Unknown WFF operator: {operator}")

    def _translate_bf_operator(self, left: str, operator: str, right: str = None) -> str:
        """Translate BF operators."""
        if operator in self.boolean_function_operators:
            tau_op = self.boolean_function_operators[operator]
            if right is None:  # Unary operator (complement)
                return f"({left}{tau_op})"
            else:  # Binary operator
                return f"({left} {tau_op} {right})"
        else:
            raise TauTranslationError(f"Unknown BF operator: {operator}")

    def _translate_stream_reference_accurate(self, variable: str, temporal_offset: str = None) -> str:
        """Translate stream references with temporal offsets."""
        if temporal_offset:
            return f"{variable}[{temporal_offset}]"
        else:
            return variable

    def _translate_temporal_offset(self, base: str = "t", offset: int = 0) -> str:
        """Translate temporal offsets."""
        if offset == 0:
            return base
        elif offset > 0:
            return f"{base}+{offset}"
        else:
            return f"{base}{offset}"  # offset is already negative

    def _translate_function_reference_accurate(self, name: str, args: list, temporal_offset: str = None) -> str:
        """Translate function references with optional temporal offsets."""
        args_str = ", ".join(args)
        if temporal_offset:
            return f"{name}[{temporal_offset}]({args_str})"
        else:
            return f"{name}({args_str})"

    def _translate_splitter_function(self, expression: str) -> str:
        """Translate splitter function S(bf)."""
        return f"S({expression})"

    def _translate_constraint_expression(self, variable: str, operator: str, value: str) -> str:
        """Translate constraint expressions [ctnvar op num]."""
        return f"[{variable} {operator} {value}]"

    def _translate_cli_command_accurate(self, command: str, expression: str) -> str:
        """Translate CLI commands accurately."""
        if command in self.solver_commands:
            tau_cmd = self.solver_commands[command]
            return f"{tau_cmd} {expression}"
        else:
            raise TauTranslationError(f"Unknown CLI command: {command}")

    def _translate_substitution_command(self, expression: str, old_expr: str, new_expr: str) -> str:
        """Translate substitution commands."""
        return f"subst {expression} [{new_expr}/{old_expr}]"

    def _translate_instantiation_command(self, expression: str, variable: str, value: str) -> str:
        """Translate instantiation commands."""
        return f"inst {expression} [{variable}/{value}]"
