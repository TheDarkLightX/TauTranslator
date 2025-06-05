"""
ILR-based Natural Language Translator (Refactored)
=================================================

Translates natural language to ILR (Intermediate Logic Representation) in JSON format.
Refactored for better maintainability, lower complexity, and optimal entropy.

Author: DarkLightX/Dana Edwards
"""

import json
import re
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict

from .ilr_nodes import (
    ILRNode, VariableReference, BooleanConstant, NumericConstant,
    StringConstant, ComparisonExpression, LogicalExpression,
    ArithmeticExpression, FunctionCall, FunctionDeclaration,
    VariableDeclaration, AssignmentStatement, ConditionalExpression
)
from .ilr_pattern_handlers import PatternHandlerRegistry


class NaturalLanguageToILRTranslator:
    """
    Translates natural language to ILR using a modular pattern-based approach.
    
    This refactored version achieves:
    - Lower cyclomatic complexity through pattern delegation
    - Optimal Shannon entropy (targeted 4.0-5.0 range)
    - Better maintainability and testability
    """
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        """
        Initialize translator with optional vocabulary.
        
        Args:
            vocabulary: Domain-specific vocabulary dictionary
        """
        self.vocabulary = vocabulary or {}
        self.ilr_version = "0.2.0"
        self.pattern_registry = PatternHandlerRegistry()
    
    def translate_to_ilr(self, nl_text: str) -> Dict[str, Any]:
        """
        Translate natural language to ILR format.
        
        Args:
            nl_text: Natural language input text
            
        Returns:
            ILR representation as dictionary
            
        Raises:
            ValueError: If input is empty
            SyntaxError: If input format is invalid
        """
        # Validate input
        nl_text = self._validate_input(nl_text)
        
        # Find appropriate pattern handler
        handler = self.pattern_registry.find_handler(nl_text)
        
        if handler:
            # Use pattern handler
            data = handler.analyze(nl_text)
            ilr_content = handler.generate_ilr(data)
        else:
            # Default to assertion pattern
            ilr_content = self._generate_default_assertion(nl_text)
        
        # Wrap in ILR structure
        return self._wrap_ilr_content(ilr_content)
    
    def _validate_input(self, nl_text: str) -> str:
        """Validate and clean input text."""
        if not nl_text:
            raise ValueError("Input cannot be empty")
        
        nl_text = nl_text.strip()
        
        # TCE requires a period at the end
        if not nl_text.endswith('.'):
            raise SyntaxError("TCE input must end with period")
            
        # Remove the period for processing
        return nl_text[:-1]
    
    def _wrap_ilr_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Wrap content in standard ILR structure."""
        return {
            "version": self.ilr_version,
            "type": "ILR",
            "content": content,
            "metadata": {
                "source": "natural_language",
                "target": "tau"
            }
        }
    
    def _generate_default_assertion(self, text: str) -> Dict[str, Any]:
        """Generate default assertion ILR for unrecognized patterns."""
        # Parse as simple expression
        expression = self._parse_expression(text)
        
        return {
            "type": "ASSERTION",
            "expression": expression
        }
    
    def _parse_expression(self, expr: str) -> Dict[str, Any]:
        """Parse a simple expression into ILR node."""
        expr = expr.strip()
        
        # Try to parse as comparison
        comparison = self._try_parse_comparison(expr)
        if comparison:
            return comparison
        
        # Try to parse as arithmetic
        arithmetic = self._try_parse_arithmetic(expr)
        if arithmetic:
            return arithmetic
        
        # Try to parse as function call
        function_call = self._try_parse_function_call(expr)
        if function_call:
            return function_call
        
        # Default to variable reference or constant
        return self._parse_simple_value(expr)
    
    def _try_parse_comparison(self, expr: str) -> Optional[Dict[str, Any]]:
        """Try to parse expression as comparison."""
        # Comparison operators
        operators = ['>=', '<=', '!=', '==', '>', '<', '=']
        
        for op in operators:
            if op in expr:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    left = self._parse_simple_value(parts[0].strip())
                    right = self._parse_simple_value(parts[1].strip())
                    
                    return {
                        "node_type": "COMPARISON",
                        "left": left,
                        "operator": op,
                        "right": right
                    }
        
        return None
    
    def _try_parse_arithmetic(self, expr: str) -> Optional[Dict[str, Any]]:
        """Try to parse expression as arithmetic operation."""
        # Simple binary operators
        operators = ['+', '-', '*', '/', '%']
        
        for op in operators:
            if op in expr:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    left = self._parse_simple_value(parts[0].strip())
                    right = self._parse_simple_value(parts[1].strip())
                    
                    return {
                        "node_type": "ARITHMETIC_EXPRESSION",
                        "operator": op,
                        "operands": [left, right]
                    }
        
        return None
    
    def _try_parse_function_call(self, expr: str) -> Optional[Dict[str, Any]]:
        """Try to parse expression as function call."""
        match = re.match(r'(\w+)\s*\((.*)\)', expr)
        if match:
            func_name = match.group(1)
            args_str = match.group(2)
            
            # Parse arguments
            arguments = []
            if args_str:
                for arg in args_str.split(','):
                    arguments.append(self._parse_simple_value(arg.strip()))
            
            return {
                "node_type": "FUNCTION_CALL",
                "name": func_name,
                "arguments": arguments
            }
        
        return None
    
    def _parse_simple_value(self, value: str) -> Dict[str, Any]:
        """Parse a simple value (constant or variable)."""
        value = value.strip()
        
        # Boolean literals
        if value.lower() == "true":
            return {"node_type": "BOOLEAN_CONSTANT", "value": True}
        elif value.lower() == "false":
            return {"node_type": "BOOLEAN_CONSTANT", "value": False}
        
        # Numeric literals
        try:
            if '.' in value:
                return {"node_type": "NUMERIC_CONSTANT", "value": float(value)}
            else:
                return {"node_type": "NUMERIC_CONSTANT", "value": int(value)}
        except ValueError:
            pass
        
        # String literals
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return {"node_type": "STRING_CONSTANT", "value": value[1:-1]}
        
        # Variable reference
        if re.match(r'^[a-zA-Z_]\w*$', value):
            return {"node_type": "VARIABLE_REFERENCE", "name": value}
        
        # Default to string
        return {"node_type": "STRING_CONSTANT", "value": value}


class ILRToTauTranslator:
    """
    Translates ILR to Tau language.
    
    This class handles the conversion from the intermediate representation
    to the target Tau language syntax.
    """
    
    def __init__(self):
        """Initialize the ILR to Tau translator."""
        self.indentation_level = 0
        self.indent_size = 2
    
    def translate(self, ilr: Dict[str, Any]) -> str:
        """
        Translate ILR to Tau language.
        
        Args:
            ilr: ILR representation as dictionary
            
        Returns:
            Tau language code as string
        """
        if ilr.get("type") != "ILR":
            raise ValueError("Invalid ILR format")
        
        content = ilr.get("content", {})
        return self._translate_content(content)
    
    def _translate_content(self, content: Dict[str, Any]) -> str:
        """Translate ILR content based on type."""
        content_type = content.get("type")
        
        # Use dispatch dictionary for lower complexity
        translators = {
            "ASSERTION": self._translate_assertion,
            "ASSIGNMENT": self._translate_assignment,
            "CONDITIONAL": self._translate_conditional,
            "FUNCTION_DECLARATION": self._translate_function,
            "VARIABLE_DECLARATION": self._translate_variable,
            "TEMPORAL_ALWAYS": self._translate_temporal_always,
            "SBF_INPUT_DECLARATION": self._translate_sbf_input,
            "SBF_OUTPUT_DECLARATION": self._translate_sbf_output,
            "STREAM_RULE": self._translate_stream_rule
        }
        
        translator = translators.get(content_type)
        if translator:
            return translator(content)
        
        # Default fallback
        return f"// Unsupported ILR type: {content_type}"
    
    def _translate_assertion(self, content: Dict[str, Any]) -> str:
        """Translate assertion to Tau."""
        expr = content.get("expression", {})
        return self._translate_expression(expr) + "."
    
    def _translate_assignment(self, content: Dict[str, Any]) -> str:
        """Translate assignment to Tau."""
        var = content.get("variable", "")
        value = content.get("value", {})
        
        value_str = self._translate_expression(value)
        return f"{var} := {value_str}."
    
    def _translate_conditional(self, content: Dict[str, Any]) -> str:
        """Translate conditional to Tau."""
        condition = content.get("condition", "")
        then_branch = content.get("then", "")
        else_branch = content.get("else")
        
        result = f"if {condition} then {then_branch}"
        if else_branch:
            result += f" else {else_branch}"
        
        return result + "."
    
    def _translate_function(self, content: Dict[str, Any]) -> str:
        """Translate function declaration to Tau."""
        name = content.get("name", "")
        params = content.get("parameters", [])
        body = content.get("body")
        
        param_str = ", ".join(params)
        result = f"{name}({param_str})"
        
        if body:
            body_str = self._translate_expression(body)
            result += f" := {body_str}"
        
        return result + "."
    
    def _translate_variable(self, content: Dict[str, Any]) -> str:
        """Translate variable declaration to Tau."""
        name = content.get("name", "")
        var_type = content.get("type")
        initial_value = content.get("initial_value")
        is_stream = content.get("is_stream", False)
        
        if is_stream:
            result = f"stream {name}"
        else:
            result = name
        
        if var_type:
            result = f"{var_type} {result}"
        
        if initial_value:
            value_str = self._translate_expression(initial_value)
            result += f" := {value_str}"
        
        return result + "."
    
    def _translate_temporal_always(self, content: Dict[str, Any]) -> str:
        """Translate temporal always to Tau."""
        condition = content.get("condition", "")
        return f"always {condition}."
    
    def _translate_sbf_input(self, content: Dict[str, Any]) -> str:
        """Translate SBF input declaration to Tau."""
        sbf_name = content.get("sbf_name", "")
        input_var = content.get("input_variable", "")
        return f"SBF {sbf_name} takes {input_var}."
    
    def _translate_sbf_output(self, content: Dict[str, Any]) -> str:
        """Translate SBF output declaration to Tau."""
        sbf_name = content.get("sbf_name", "")
        output_var = content.get("output_variable", "")
        return f"SBF {sbf_name} produces {output_var}."
    
    def _translate_stream_rule(self, content: Dict[str, Any]) -> str:
        """Translate stream rule to Tau."""
        stream_name = content.get("stream_name", "")
        expression = content.get("expression", "")
        operator = content.get("operator", "<-")
        return f"stream {stream_name} {operator} {expression}."
    
    def _translate_expression(self, expr: Union[Dict[str, Any], str]) -> str:
        """Translate an expression node to Tau syntax."""
        if isinstance(expr, str):
            return expr
        
        node_type = expr.get("node_type", "")
        
        # Expression type dispatch
        expr_translators = {
            "VARIABLE_REFERENCE": self._translate_variable_ref,
            "BOOLEAN_CONSTANT": self._translate_boolean,
            "NUMERIC_CONSTANT": self._translate_numeric,
            "STRING_CONSTANT": self._translate_string,
            "COMPARISON": self._translate_comparison_expr,
            "ARITHMETIC_EXPRESSION": self._translate_arithmetic_expr,
            "FUNCTION_CALL": self._translate_function_call_expr
        }
        
        translator = expr_translators.get(node_type)
        if translator:
            return translator(expr)
        
        return str(expr)
    
    def _translate_variable_ref(self, expr: Dict[str, Any]) -> str:
        """Translate variable reference."""
        name = expr.get("name", "")
        temporal = expr.get("temporal_qualifier")
        
        if temporal and temporal.get("type") == "TIME_OFFSET":
            offset = temporal.get("offset", 0)
            if offset < 0:
                return f"{name}[t{offset}]"
            elif offset > 0:
                return f"{name}[t+{offset}]"
        
        return name
    
    def _translate_boolean(self, expr: Dict[str, Any]) -> str:
        """Translate boolean constant."""
        value = expr.get("value", False)
        return "true" if value else "false"
    
    def _translate_numeric(self, expr: Dict[str, Any]) -> str:
        """Translate numeric constant."""
        return str(expr.get("value", 0))
    
    def _translate_string(self, expr: Dict[str, Any]) -> str:
        """Translate string constant."""
        value = expr.get("value", "")
        return f'"{value}"'
    
    def _translate_comparison_expr(self, expr: Dict[str, Any]) -> str:
        """Translate comparison expression."""
        left = self._translate_expression(expr.get("left", {}))
        right = self._translate_expression(expr.get("right", {}))
        op = expr.get("operator", "=")
        
        # Map operators if needed
        op_map = {"==": "=", "!=": "≠"}
        op = op_map.get(op, op)
        
        return f"{left} {op} {right}"
    
    def _translate_arithmetic_expr(self, expr: Dict[str, Any]) -> str:
        """Translate arithmetic expression."""
        operator = expr.get("operator", "+")
        operands = expr.get("operands", [])
        
        if len(operands) == 2:
            left = self._translate_expression(operands[0])
            right = self._translate_expression(operands[1])
            return f"{left} {operator} {right}"
        
        # Multi-operand expression
        translated = [self._translate_expression(op) for op in operands]
        return f" {operator} ".join(translated)
    
    def _translate_function_call_expr(self, expr: Dict[str, Any]) -> str:
        """Translate function call expression."""
        name = expr.get("name", "")
        arguments = expr.get("arguments", [])
        
        arg_strs = [self._translate_expression(arg) for arg in arguments]
        arg_list = ", ".join(arg_strs)
        
        return f"{name}({arg_list})"


# Module exports
__all__ = ['NaturalLanguageToILRTranslator', 'ILRToTauTranslator']