"""
ILR to TAU translation service following the Intentional Disclosure Principle.

Handles TAU code generation with all methods ≤10 lines following IDP Rule 2.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, Any, List, Optional
from returns.result import Result, Success, Failure

from .ilr_types import (
    TauCode, NodeType, ComparisonOperator, LogicalOperator,
    ArithmeticOperator, QuantifierType, TemporalOperator
)
from ..infrastructure.ilr_infrastructure import OperatorMapper, JsonSerializer


class TauTranslationService:
    """Translates ILR structures to TAU code."""
    
    def translate_ilr_to_tau(self, ilr_json: str) -> Result[TauCode, str]:
        """Translate ILR JSON to TAU code."""
        # Deserialize JSON
        ilr_result = JsonSerializer.deserialize_ilr(ilr_json)
        if isinstance(ilr_result, Failure):
            return ilr_result
        
        ilr_dict = ilr_result.unwrap()
        
        # Handle special case of SBF declarations
        if self._has_sbf_declaration(ilr_dict):
            return self._translate_sbf_declaration(ilr_dict)
        
        # Translate program structure
        return self._translate_program(ilr_dict.get("program", {}))
    
    def _has_sbf_declaration(self, ilr_dict: Dict[str, Any]) -> bool:
        """Check if ILR contains SBF declaration."""
        program = ilr_dict.get("program", {})
        return "sbf_declaration" in program
    
    def _translate_sbf_declaration(self, ilr_dict: Dict[str, Any]) -> Result[TauCode, str]:
        """Translate SBF declaration to TAU."""
        sbf_decl = ilr_dict["program"]["sbf_declaration"]
        direction = sbf_decl["direction"].lower()
        streams = sbf_decl["streams"]
        
        streams_str = ", ".join(streams)
        tau_code = f"sbf_{direction}({streams_str})."
        
        return Success(TauCode(tau_code))
    
    def _translate_program(self, program: Dict[str, Any]) -> Result[TauCode, str]:
        """Translate program structure to TAU."""
        tau_lines = []
        
        # Translate declarations
        for decl in program.get("declarations", []):
            decl_result = self._translate_declaration(decl)
            if isinstance(decl_result, Failure):
                return decl_result
            tau_lines.append(decl_result.unwrap())
        
        # Translate statements
        for stmt in program.get("statements", []):
            stmt_result = self._translate_statement(stmt)
            if isinstance(stmt_result, Failure):
                return stmt_result
            tau_lines.append(stmt_result.unwrap())
        
        # Handle top-level expression
        if "expression" in program:
            expr_result = self._translate_expression(program["expression"])
            if isinstance(expr_result, Failure):
                return expr_result
            tau_lines.append(expr_result.unwrap() + ".")
        
        return Success(TauCode("\n".join(tau_lines)))
    
    def _translate_declaration(self, decl: Dict[str, Any]) -> Result[str, str]:
        """Translate declaration to TAU."""
        if "parameters" in decl:  # Function declaration
            return self._translate_function_declaration(decl)
        else:  # Variable declaration
            return self._translate_variable_declaration(decl)
    
    def _translate_function_declaration(self, decl: Dict[str, Any]) -> Result[str, str]:
        """Translate function declaration to TAU."""
        name = decl["name"]
        params = [p["name"] for p in decl.get("parameters", [])]
        params_str = ", ".join(params)
        
        # Extract return expression from body
        body = decl.get("body", [])
        if body and body[0].get("type") == "RETURN":
            expr_result = self._translate_expression(body[0]["value"])
            if isinstance(expr_result, Failure):
                return expr_result
            
            return Success(f"predicate {name}({params_str}) is {expr_result.unwrap()}.")
        
        return Failure(f"Invalid function body for {name}")
    
    def _translate_variable_declaration(self, decl: Dict[str, Any]) -> Result[str, str]:
        """Translate variable declaration to TAU."""
        name = decl["name"]
        
        if "initial_value" in decl:
            value_result = self._translate_expression(decl["initial_value"])
            if isinstance(value_result, Failure):
                return value_result
            
            return Success(f"{name} = {value_result.unwrap()}.")
        
        # Variable without initial value
        return Success(f"# Variable {name} declared")
    
    def _translate_statement(self, stmt: Dict[str, Any]) -> Result[str, str]:
        """Translate statement to TAU."""
        stmt_type = stmt.get("type")
        
        if stmt_type == "ASSIGNMENT":
            return self._translate_assignment(stmt)
        elif stmt_type == "ASSERTION":
            return self._translate_assertion(stmt)
        elif stmt_type == "TEMPORAL":
            return self._translate_temporal_statement(stmt)
        else:
            return Failure(f"Unknown statement type: {stmt_type}")
    
    def _translate_assignment(self, stmt: Dict[str, Any]) -> Result[str, str]:
        """Translate assignment statement to TAU."""
        target = stmt["target"]
        value_result = self._translate_expression(stmt["value"])
        
        if isinstance(value_result, Failure):
            return value_result
        
        return Success(f"{target} = {value_result.unwrap()}.")
    
    def _translate_assertion(self, stmt: Dict[str, Any]) -> Result[str, str]:
        """Translate assertion statement to TAU."""
        expr_result = self._translate_expression(stmt["expression"])
        
        if isinstance(expr_result, Failure):
            return expr_result
        
        return Success(f"{expr_result.unwrap()}.")
    
    def _translate_temporal_statement(self, stmt: Dict[str, Any]) -> Result[str, str]:
        """Translate temporal statement to TAU."""
        operator = stmt["operator"].lower()
        expr_result = self._translate_expression(stmt["expression"])
        
        if isinstance(expr_result, Failure):
            return expr_result
        
        return Success(f"{operator} {expr_result.unwrap()}.")
    
    def _translate_expression(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate expression to TAU."""
        node_type = expr.get("node_type")
        
        # Route to specific translator based on node type
        translator_map = {
            "VARIABLE_REFERENCE": self._translate_variable_reference,
            "BOOLEAN_CONSTANT": self._translate_boolean_constant,
            "NUMERIC_CONSTANT": self._translate_numeric_constant,
            "STRING_CONSTANT": self._translate_string_constant,
            "COMPARISON_EXPRESSION": self._translate_comparison,
            "LOGICAL_EXPRESSION": self._translate_logical,
            "ARITHMETIC_EXPRESSION": self._translate_arithmetic,
            "FUNCTION_CALL": self._translate_function_call,
            "QUANTIFIER_EXPRESSION": self._translate_quantifier,
            "CONDITIONAL_EXPRESSION": self._translate_conditional,
        }
        
        translator = translator_map.get(node_type)
        if not translator:
            return Failure(f"Unknown node type: {node_type}")
        
        return translator(expr)
    
    def _translate_variable_reference(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate variable reference to TAU."""
        name = expr["name"]
        
        if "temporal_qualifier" in expr:
            qualifier = expr["temporal_qualifier"]
            offset = qualifier["offset"]
            
            if offset == 0:
                return Success(f"{name}[t]")
            elif offset > 0:
                return Success(f"{name}[t+{offset}]")
            else:
                return Success(f"{name}[t{offset}]")
        
        return Success(name)
    
    def _translate_boolean_constant(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate boolean constant to TAU."""
        return Success(str(expr["value"]).lower())
    
    def _translate_numeric_constant(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate numeric constant to TAU."""
        return Success(str(expr["value"]))
    
    def _translate_string_constant(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate string constant to TAU."""
        return Success(f'"{expr["value"]}"')
    
    def _translate_comparison(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate comparison expression to TAU."""
        left_result = self._translate_expression(expr["left_operand"])
        right_result = self._translate_expression(expr["right_operand"])
        
        if isinstance(left_result, Failure):
            return left_result
        if isinstance(right_result, Failure):
            return right_result
        
        # Map operator
        op_enum = ComparisonOperator[expr["operator"]]
        tau_op = OperatorMapper.get_tau_operator(op_enum)
        
        return Success(f"{left_result.unwrap()} {tau_op} {right_result.unwrap()}")
    
    def _translate_logical(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate logical expression to TAU."""
        operator = expr["operator"]
        operands = expr["operands"]
        
        # Handle NOT specially (unary)
        if operator == "NOT":
            operand_result = self._translate_expression(operands[0])
            if isinstance(operand_result, Failure):
                return operand_result
            return Success(f"!({operand_result.unwrap()})")
        
        # Translate all operands
        operand_results = [self._translate_expression(op) for op in operands]
        
        # Check for failures
        for result in operand_results:
            if isinstance(result, Failure):
                return result
        
        # Map operator
        op_enum = LogicalOperator[operator]
        tau_op = OperatorMapper.get_tau_operator(op_enum)
        
        # Join with operator
        operand_strs = [r.unwrap() for r in operand_results]
        
        # Add parentheses for clarity
        if len(operand_strs) > 2 or operator in ["IMPLIES"]:
            joined = f" {tau_op} ".join(f"({op})" for op in operand_strs)
        else:
            joined = f" {tau_op} ".join(operand_strs)
        
        return Success(joined)
    
    def _translate_arithmetic(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate arithmetic expression to TAU."""
        operator = expr["operator"]
        operands = expr["operands"]
        
        # Handle NEG specially (unary)
        if operator == "NEG":
            operand_result = self._translate_expression(operands[0])
            if isinstance(operand_result, Failure):
                return operand_result
            return Success(f"-({operand_result.unwrap()})")
        
        # Translate all operands
        operand_results = [self._translate_expression(op) for op in operands]
        
        # Check for failures
        for result in operand_results:
            if isinstance(result, Failure):
                return result
        
        # Map operator
        op_enum = ArithmeticOperator[operator]
        tau_op = OperatorMapper.get_tau_operator(op_enum)
        
        # Join with operator
        operand_strs = [r.unwrap() for r in operand_results]
        joined = f" {tau_op} ".join(operand_strs)
        
        return Success(f"({joined})")
    
    def _translate_function_call(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate function call to TAU."""
        name = expr["function_name"]
        
        # Translate arguments
        arg_results = [self._translate_expression(arg) for arg in expr.get("arguments", [])]
        
        # Check for failures
        for result in arg_results:
            if isinstance(result, Failure):
                return result
        
        args_str = ", ".join(r.unwrap() for r in arg_results)
        return Success(f"{name}({args_str})")
    
    def _translate_quantifier(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate quantifier expression to TAU."""
        quantifier = expr["quantifier"]
        bound_vars = expr["bound_variables"]
        body_result = self._translate_expression(expr["body"])
        
        if isinstance(body_result, Failure):
            return body_result
        
        # Format bound variables
        var_list = ", ".join(v["name"] for v in bound_vars)
        
        if quantifier == "FOR_ALL":
            return Success(f"for all {var_list}, {body_result.unwrap()}")
        else:  # EXISTS
            return Success(f"exists {var_list} such that {body_result.unwrap()}")
    
    def _translate_conditional(self, expr: Dict[str, Any]) -> Result[str, str]:
        """Translate conditional expression to TAU."""
        cond_result = self._translate_expression(expr["condition"])
        then_result = self._translate_expression(expr["then_expression"])
        
        if isinstance(cond_result, Failure):
            return cond_result
        if isinstance(then_result, Failure):
            return then_result
        
        if "else_expression" in expr:
            else_result = self._translate_expression(expr["else_expression"])
            if isinstance(else_result, Failure):
                return else_result
            
            return Success(
                f"if {cond_result.unwrap()} then {then_result.unwrap()} "
                f"else {else_result.unwrap()}"
            )
        
        return Success(f"if {cond_result.unwrap()} then {then_result.unwrap()}")