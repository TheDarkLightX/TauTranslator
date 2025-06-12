"""
ILR-based Natural Language Translator
====================================

Translates natural language to ILR (Intermediate Logic Representation) in JSON format,
which can then be converted to TAU or other target languages.
"""

import json
import re
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict


@dataclass
class ILRNode:
    """Base class for ILR nodes."""
    node_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass 
class VariableReference(ILRNode):
    """Reference to a variable or stream."""
    name: str
    temporal_qualifier: Optional[Dict[str, Any]] = None
    
    def __init__(self, name: str, temporal_offset: Optional[int] = None):
        super().__init__(node_type="VARIABLE_REFERENCE")
        self.name = name
        if temporal_offset is not None:
            self.temporal_qualifier = {
                "type": "TIME_OFFSET",
                "offset": temporal_offset
            }


@dataclass
class BooleanConstant(ILRNode):
    """Boolean literal value."""
    value: bool
    
    def __init__(self, value: bool):
        super().__init__(node_type="BOOLEAN_CONSTANT")
        self.value = value


@dataclass
class NumericConstant(ILRNode):
    """Numeric literal value."""
    value: Union[int, float]
    
    def __init__(self, value: Union[int, float]):
        super().__init__(node_type="NUMERIC_CONSTANT")
        self.value = value


@dataclass
class StringConstant(ILRNode):
    """String literal value."""
    value: str
    
    def __init__(self, value: str):
        super().__init__(node_type="STRING_CONSTANT")
        self.value = value


@dataclass
class ComparisonExpression(ILRNode):
    """Comparison between two expressions."""
    operator: str  # EQ, NEQ, LT, LTE, GT, GTE
    left_operand: Dict[str, Any]
    right_operand: Dict[str, Any]
    
    def __init__(self, operator: str, left: ILRNode, right: ILRNode):
        super().__init__(node_type="COMPARISON_EXPRESSION")
        self.operator = operator
        self.left_operand = left.to_dict()
        self.right_operand = right.to_dict()


@dataclass
class LogicalExpression(ILRNode):
    """Logical operation (AND, OR, XOR, NOT)."""
    operator: str
    operands: List[Dict[str, Any]]
    
    def __init__(self, operator: str, *operands: ILRNode):
        super().__init__(node_type="LOGICAL_EXPRESSION")
        self.operator = operator
        self.operands = [op.to_dict() for op in operands]


@dataclass
class ArithmeticExpression(ILRNode):
    """Arithmetic operation."""
    operator: str  # ADD, SUB, MUL, DIV, MOD, POW, NEG
    left_operand: Optional[Dict[str, Any]] = None
    right_operand: Optional[Dict[str, Any]] = None
    operand: Optional[Dict[str, Any]] = None  # For unary operations
    
    def __init__(self, operator: str, left: Optional[ILRNode] = None, 
                 right: Optional[ILRNode] = None, operand: Optional[ILRNode] = None):
        super().__init__(node_type="ARITHMETIC_EXPRESSION" if operator != "NEG" 
                         else "UNARY_ARITHMETIC_EXPRESSION")
        self.operator = operator
        if operator == "NEG":
            self.operand = operand.to_dict() if operand else None
        else:
            self.left_operand = left.to_dict() if left else None
            self.right_operand = right.to_dict() if right else None


@dataclass
class FunctionCall(ILRNode):
    """Function call expression."""
    function_name: str
    arguments: List[Dict[str, Any]]
    
    def __init__(self, function_name: str, *arguments: ILRNode):
        super().__init__(node_type="FUNCTION_CALL")
        self.function_name = function_name
        self.arguments = [arg.to_dict() for arg in arguments]


@dataclass
class FunctionDeclaration:
    """Function declaration."""
    name: str
    parameters: List[Dict[str, Any]]
    return_type: str
    node_type: str = "FUNCTION_DECLARATION"
    body: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VariableDeclaration:
    """Variable declaration."""
    name: str
    data_type: Dict[str, Any]
    node_type: str = "VARIABLE_DECLARATION"
    is_constant: bool = False
    is_stream: bool = False
    initial_value: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AssignmentStatement:
    """Assignment statement."""
    target: Dict[str, Any]
    expression: Dict[str, Any]
    node_type: str = "ASSIGNMENT_STATEMENT"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConditionalExpression(ILRNode):
    """If-then-else expression."""
    condition: Dict[str, Any]
    value_if_true: Dict[str, Any]
    value_if_false: Dict[str, Any]
    
    def __init__(self, condition: ILRNode, if_true: ILRNode, if_false: ILRNode):
        super().__init__(node_type="CONDITIONAL_EXPRESSION")
        self.condition = condition.to_dict()
        self.value_if_true = if_true.to_dict()
        self.value_if_false = if_false.to_dict()


class NaturalLanguageToILRTranslator:
    """Translates natural language to ILR (JSON intermediate representation)."""
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        self.vocabulary = vocabulary or {}
        self.ilr_version = "0.1.0"
    
    def translate_to_ilr(self, nl_text: str) -> Dict[str, Any]:
        """Translate natural language to ILR format."""
        if not nl_text:
            raise ValueError("Input cannot be empty")
        
        # Clean input
        nl_text = nl_text.strip()
        
        # TCE requires a period at the end
        if not nl_text.endswith('.'):
            raise SyntaxError("TCE input must end with period")
            
        # Remove the period for processing
        nl_text = nl_text[:-1]
        
        # Analyze the natural language input
        pattern_type, matched_data = self._analyze_pattern(nl_text)
        
        # Generate appropriate ILR based on pattern
        if pattern_type == "sbf_input":
            return self._generate_sbf_input_ilr(matched_data)
        elif pattern_type == "sbf_output":
            return self._generate_sbf_output_ilr(matched_data)
        elif pattern_type == "stream_rule":
            return self._generate_stream_rule_ilr(matched_data)
        elif pattern_type == "temporal_always":
            return self._generate_temporal_always_ilr(matched_data)
        elif pattern_type == "predicate_definition":
            return self._generate_predicate_ilr(matched_data)
        elif pattern_type == "function_definition":
            return self._generate_function_ilr(matched_data)
        elif pattern_type == "universal_quantification":
            return self._generate_universal_ilr(matched_data)
        elif pattern_type == "existential_quantification":
            return self._generate_existential_ilr(matched_data)
        elif pattern_type == "conditional":
            return self._generate_conditional_ilr(matched_data)
        elif pattern_type == "assignment":
            return self._generate_assignment_ilr(matched_data)
        elif pattern_type == "boolean_operation":
            return self._generate_boolean_ilr(matched_data)
        elif pattern_type == "negation":
            return self._generate_negation_ilr(matched_data)
        elif pattern_type == "stream_output":
            return self._generate_stream_ilr(matched_data)
        elif pattern_type == "assertion":
            return self._generate_assertion_ilr(matched_data["text"])
        else:
            # Default to simple assertion
            return self._generate_assertion_ilr(nl_text)
    
    def _create_empty_ilr(self) -> Dict[str, Any]:
        """Create empty ILR document."""
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": []
            }
        }
    
    def _analyze_pattern(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Analyze text to determine pattern type and extract data."""
        from .ilr_pattern_analyzer_refactored import refactored_analyze_pattern
        return refactored_analyze_pattern(text)
    
    def _generate_predicate_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for predicate definition."""
        # Parse the body expression
        body_expr = self._parse_expression(data["body"], {data["param"]: "VARIABLE"})
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [
                    {
                        "node_type": "FUNCTION_DECLARATION",
                        "name": data["name"],
                        "parameters": [
                            {
                                "node_type": "VARIABLE_DECLARATION",
                                "name": data["param"],
                                "data_type": {"core_type": "INTEGER"}
                            }
                        ],
                        "return_type": "BOOLEAN",
                        "body": [
                            {
                                "node_type": "RETURN_STATEMENT",
                                "expression": body_expr
                            }
                        ]
                    }
                ],
                "imports": [],
                "exports": []
            }
        }
    
    def _generate_function_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for function definition."""
        # Create parameter context
        param_context = {param: "VARIABLE" for param in data["params"]}
        
        # Parse the body expression
        body_expr = self._parse_expression(data["body"], param_context)
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [
                    {
                        "node_type": "FUNCTION_DECLARATION",
                        "name": data["name"],
                        "parameters": [
                            {
                                "node_type": "VARIABLE_DECLARATION",
                                "name": param,
                                "data_type": {"core_type": "BOOLEAN"}
                            } for param in data["params"]
                        ],
                        "return_type": "BOOLEAN",
                        "body": [
                            {
                                "node_type": "RETURN_STATEMENT",
                                "expression": body_expr
                            }
                        ]
                    }
                ],
                "imports": [],
                "exports": []
            }
        }
    
    def _generate_universal_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for universal quantification."""
        # Parse the condition
        condition = self._parse_expression(data["condition"], {data["variable"]: "VARIABLE"})
        
        # Create quantifier expression
        quantifier_expr = {
            "node_type": "QUANTIFIER_EXPRESSION",
            "operator": "FOR_ALL",
            "bound_variables": [
                {
                    "name": data["variable"],
                    "data_type": "NUMBER"
                }
            ],
            "expression": condition
        }
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": [],
                "statements": [
                    {
                        "node_type": "ASSERTION_STATEMENT",
                        "condition": quantifier_expr
                    }
                ]
            }
        }
    
    def _generate_existential_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for existential quantification."""
        # Parse the condition
        condition = self._parse_expression(data["condition"], {data["variable"]: "VARIABLE"})
        
        # Create quantifier expression
        quantifier_expr = {
            "node_type": "QUANTIFIER_EXPRESSION",
            "operator": "EXISTS",
            "bound_variables": [
                {
                    "name": data["variable"],
                    "data_type": "NUMBER"
                }
            ],
            "expression": condition
        }
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": [],
                "statements": [
                    {
                        "node_type": "ASSERTION_STATEMENT",
                        "condition": quantifier_expr
                    }
                ]
            }
        }
    
    def _generate_conditional_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for conditional statement."""
        # Parse condition and consequence
        condition = self._parse_expression(data["condition"], {})
        consequence = self._parse_expression(data["consequence"], {})
        
        # Create implication using LOGICAL_EXPRESSION
        implication = {
            "node_type": "LOGICAL_EXPRESSION",
            "operator": "IMPLIES",
            "operands": [condition, consequence]
        }
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": [],
                "statements": [
                    {
                        "node_type": "ASSERTION_STATEMENT",
                        "condition": implication
                    }
                ]
            }
        }
    
    def _generate_assignment_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for assignment statement."""
        # Parse the value expression
        value_expr = self._parse_expression(data["value"], {})
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [
                    {
                        "node_type": "VARIABLE_DECLARATION",
                        "name": data["variable"],
                        "data_type": {"core_type": "INTEGER"},
                        "initial_value": value_expr
                    }
                ],
                "imports": [],
                "exports": []
            }
        }
    
    def _generate_boolean_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for boolean operations."""
        expr = data["expression"]
        parsed = self._parse_expression(expr, {})
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": [],
                "statements": [
                    {
                        "node_type": "ASSERTION_STATEMENT",
                        "condition": parsed
                    }
                ]
            }
        }
    
    def _generate_negation_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for negation."""
        inner_expr = self._parse_expression(data["expression"], {})
        
        negation = {
            "node_type": "LOGICAL_EXPRESSION",
            "operator": "NOT",
            "operands": [inner_expr]
        }
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": [],
                "statements": [
                    {
                        "node_type": "ASSERTION_STATEMENT",
                        "condition": negation
                    }
                ]
            }
        }
    
    def _generate_stream_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for stream output assignment."""
        # Create stream variable with temporal qualifier
        stream_ref = {
            "node_type": "VARIABLE_REFERENCE",
            "name": f"o{data['stream_num']}",
            "temporal_qualifier": {
                "type": "TIME_OFFSET",
                "offset": 0  # Current time [t]
            }
        }
        
        # Value to assign
        value = {
            "node_type": "NUMERIC_CONSTANT",
            "value": data["time"]
        }
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [
                    {
                        "node_type": "VARIABLE_DECLARATION",
                        "name": f"o{data['stream_num']}",
                        "data_type": {"core_type": "INTEGER"},
                        "is_stream": True,
                        "stream_kind": "OUTPUT"
                    }
                ],
                "imports": [],
                "exports": [],
                "statements": [
                    {
                        "node_type": "ASSIGNMENT_STATEMENT",
                        "target": stream_ref,
                        "expression": value
                    }
                ]
            }
        }
    
    def _generate_sbf_input_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for SBF input stream declaration."""
        # For SBF declarations, we'll pass them through directly
        # The TAU translator will handle the conversion
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": [],
                "sbf_declaration": {
                    "type": "input",
                    "name": data["name"],
                    "file": data["file"]
                }
            }
        }
    
    def _generate_sbf_output_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for SBF output stream declaration."""
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": [],
                "sbf_declaration": {
                    "type": "output",
                    "name": data["name"],
                    "file": data["file"]
                }
            }
        }
    
    def _generate_stream_rule_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for stream rule."""
        # Parse the rule: "o1[t] = i1[t] and i2[t]"
        rule = data["rule"]
        parts = rule.split(" = ", 1)
        if len(parts) == 2:
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            
            # Parse the expression with temporal context
            expr = self._parse_temporal_expression(rhs)
            
            # Create assignment statement
            return {
                "ilr_version": self.ilr_version,
                "unit": {
                    "node_type": "PROGRAM_UNIT",
                    "declarations": [],
                    "imports": [],
                    "exports": [],
                    "statements": [
                        {
                            "node_type": "ASSIGNMENT_STATEMENT",
                            "target": self._parse_temporal_reference(lhs),
                            "expression": expr
                        }
                    ]
                }
            }
        
        return self._generate_assertion_ilr(rule)
    
    def _generate_temporal_always_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for temporal always operator."""
        condition = data["condition"]
        
        # Parse the condition
        expr = self._parse_temporal_expression(condition)
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": [],
                "statements": [
                    {
                        "node_type": "TEMPORAL_STATEMENT",
                        "operator": "ALWAYS",
                        "condition": expr
                    }
                ]
            }
        }
    
    def _parse_temporal_expression(self, expr_text: str) -> Dict[str, Any]:
        """Parse expression with temporal stream references like i1[t]."""
        expr_text = expr_text.strip()
        
        # Replace "equals" with "="
        expr_text = expr_text.replace(" equals ", " = ")
        
        # Handle parentheses - only strip if they wrap the entire expression
        if expr_text.startswith('(') and expr_text.endswith(')'):
            # Check if removing the outer parentheses leaves a valid expression
            # by ensuring the parentheses are balanced and the first opening paren
            # matches the last closing paren
            inner = expr_text[1:-1]
            paren_count = 0
            for i, char in enumerate(inner):
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                    if paren_count < 0:
                        # Parentheses close before opening, so outer parens don't wrap everything
                        break
            else:
                # If we get here, parentheses were balanced throughout
                if paren_count == 0:
                    # Outer parentheses do wrap the entire expression
                    return self._parse_temporal_expression(inner)
        
        # Boolean operations (process in order of precedence: OR first, then AND, then XOR)
        for op, ilr_op in [(" or ", "OR"), (" xor ", "XOR"), (" and ", "AND")]:
            if op in expr_text:
                parts = self._split_respecting_parens(expr_text, op)
                if len(parts) >= 2:
                    operands = [self._parse_temporal_expression(p.strip()) for p in parts]
                    return {
                        "node_type": "LOGICAL_EXPRESSION",
                        "operator": ilr_op,
                        "operands": operands
                    }
        
        # Handle complement (NOT)
        if expr_text.endswith(" complement"):
            inner = expr_text[:-11].strip()  # Remove " complement"
            return {
                "node_type": "LOGICAL_EXPRESSION",
                "operator": "NOT",
                "operands": [self._parse_temporal_expression(inner)]
            }
        
        # Comparison operations
        for op, ilr_op in [(" = ", "EQ"), (" != ", "NEQ")]:
            if op in expr_text:
                parts = expr_text.split(op, 1)
                if len(parts) == 2:
                    left = self._parse_temporal_expression(parts[0].strip())
                    right = self._parse_temporal_expression(parts[1].strip())
                    return {
                        "node_type": "COMPARISON_EXPRESSION",
                        "operator": ilr_op,
                        "left_operand": left,
                        "right_operand": right
                    }
        
        # Temporal variable reference: i1[t], o1[t-1], etc.
        temporal_match = re.match(r'(\w+)\[(t(?:[+-]\d+)?)\]', expr_text)
        if temporal_match:
            var_name = temporal_match.group(1)
            time_expr = temporal_match.group(2)
            
            offset = 0
            if time_expr != 't':
                # Extract offset: t-1 -> -1, t+2 -> 2
                offset_match = re.match(r't([+-])(\d+)', time_expr)
                if offset_match:
                    sign = offset_match.group(1)
                    value = int(offset_match.group(2))
                    offset = -value if sign == '-' else value
            
            return {
                "node_type": "VARIABLE_REFERENCE",
                "name": var_name,
                "temporal_qualifier": {
                    "type": "TIME_OFFSET",
                    "offset": offset
                }
            }
        
        # Default: variable reference
        return {
            "node_type": "VARIABLE_REFERENCE",
            "name": expr_text
        }
    
    def _parse_temporal_reference(self, ref_text: str) -> Dict[str, Any]:
        """Parse a temporal reference like o1[t]."""
        temporal_match = re.match(r'(\w+)\[(t(?:[+-]\d+)?)\]', ref_text)
        if temporal_match:
            var_name = temporal_match.group(1)
            time_expr = temporal_match.group(2)
            
            offset = 0
            if time_expr != 't':
                offset_match = re.match(r't([+-])(\d+)', time_expr)
                if offset_match:
                    sign = offset_match.group(1)
                    value = int(offset_match.group(2))
                    offset = -value if sign == '-' else value
            
            return {
                "node_type": "VARIABLE_REFERENCE",
                "name": var_name,
                "temporal_qualifier": {
                    "type": "TIME_OFFSET",
                    "offset": offset
                }
            }
        
        return {
            "node_type": "VARIABLE_REFERENCE",
            "name": ref_text
        }
    
    def _split_respecting_parens(self, text: str, delimiter: str) -> List[str]:
        """Split text by delimiter, respecting parentheses."""
        parts = []
        current = ""
        paren_depth = 0
        i = 0
        
        while i < len(text):
            if text[i] == '(':
                paren_depth += 1
                current += text[i]
            elif text[i] == ')':
                paren_depth -= 1
                current += text[i]
            elif paren_depth == 0 and text[i:i+len(delimiter)] == delimiter:
                parts.append(current)
                current = ""
                i += len(delimiter) - 1
            else:
                current += text[i]
            i += 1
        
        if current:
            parts.append(current)
        
        return parts
    
    def _generate_assertion_ilr(self, text: str) -> Dict[str, Any]:
        """Generate ILR for simple assertion."""
        # Try to parse as expression
        expr = self._parse_expression(text, {})
        
        return {
            "ilr_version": self.ilr_version,
            "unit": {
                "node_type": "PROGRAM_UNIT",
                "declarations": [],
                "imports": [],
                "exports": [],
                "statements": [
                    {
                        "node_type": "ASSERTION_STATEMENT",
                        "condition": expr
                    }
                ]
            }
        }
    
    def _parse_expression(self, expr_text: str, context: Dict[str, str]) -> Dict[str, Any]:
        """Parse an expression string into ILR nodes."""
        expr_text = expr_text.strip()
        
        # Handle parentheses - only strip if they wrap the entire expression
        if expr_text.startswith('(') and expr_text.endswith(')'):
            # Check if removing the outer parentheses leaves a valid expression
            # by ensuring the parentheses are balanced and the first opening paren
            # matches the last closing paren
            inner = expr_text[1:-1]
            paren_count = 0
            for i, char in enumerate(inner):
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                    if paren_count < 0:
                        # Parentheses close before opening, so outer parens don't wrap everything
                        break
            else:
                # If we get here, parentheses were balanced throughout
                if paren_count == 0:
                    # Outer parentheses do wrap the entire expression
                    return self._parse_expression(inner, context)
        
        # Boolean operations (process lowest precedence first: OR, then XOR, then AND)
        for op, ilr_op in [(" or ", "OR"), (" xor ", "XOR"), (" and ", "AND")]:
            if op in expr_text:
                parts = self._split_respecting_parens(expr_text, op)
                if len(parts) >= 2:
                    operands = [self._parse_expression(p.strip(), context) for p in parts]
                    return {
                        "node_type": "LOGICAL_EXPRESSION",
                        "operator": ilr_op,
                        "operands": operands
                    }
        
        # Comparison operations
        for op, ilr_op in [
            (" >= ", "GTE"), (" <= ", "LTE"),
            (" > ", "GT"), (" < ", "LT"),
            (" = ", "EQ"), (" != ", "NEQ")
        ]:
            if op in expr_text:
                parts = expr_text.split(op, 1)
                if len(parts) == 2:
                    left = self._parse_expression(parts[0].strip(), context)
                    right = self._parse_expression(parts[1].strip(), context)
                    return {
                        "node_type": "COMPARISON_EXPRESSION",
                        "operator": ilr_op,
                        "left_operand": left,
                        "right_operand": right
                    }
        
        # Arithmetic operations
        for op, ilr_op in [
            (" + ", "ADD"), (" - ", "SUB"),
            (" * ", "MUL"), (" / ", "DIV"),
            (" % ", "MOD")
        ]:
            if op in expr_text:
                parts = expr_text.split(op, 1)
                if len(parts) == 2:
                    left = self._parse_expression(parts[0].strip(), context)
                    right = self._parse_expression(parts[1].strip(), context)
                    return {
                        "node_type": "ARITHMETIC_EXPRESSION",
                        "operator": ilr_op,
                        "left_operand": left,
                        "right_operand": right
                    }
        
        # Function calls: func(arg1, arg2, ...)
        if '(' in expr_text and expr_text.endswith(')'):
            # Find the function name and opening parenthesis
            func_match = re.match(r'(\w+)\(', expr_text)
            if func_match:
                func_name = func_match.group(1)
                
                # Extract arguments by finding the matching closing parenthesis
                start_paren = expr_text.find('(')
                if start_paren != -1:
                    # Find the matching closing parenthesis
                    paren_count = 0
                    end_paren = -1
                    for i in range(start_paren, len(expr_text)):
                        if expr_text[i] == '(':
                            paren_count += 1
                        elif expr_text[i] == ')':
                            paren_count -= 1
                            if paren_count == 0:
                                end_paren = i
                                break
                    
                    if end_paren != -1:
                        args_str = expr_text[start_paren + 1:end_paren]
                        
                        # Parse arguments using parentheses-respecting split
                        args = []
                        if args_str:
                            arg_parts = self._split_respecting_parens(args_str, ',')
                            for arg in arg_parts:
                                args.append(self._parse_expression(arg.strip(), context))
                        
                        return {
                            "node_type": "FUNCTION_CALL",
                            "function_name": func_name,
                            "arguments": args
                        }
        
        # Numbers
        if re.match(r'^-?\d+(\.\d+)?$', expr_text):
            value = float(expr_text) if '.' in expr_text else int(expr_text)
            return {
                "node_type": "NUMERIC_CONSTANT",
                "value": value
            }
        
        # Booleans
        if expr_text.lower() in ['true', 'false']:
            return {
                "node_type": "BOOLEAN_CONSTANT",
                "value": expr_text.lower() == 'true'
            }
        
        # Variables
        if re.match(r'^\w+$', expr_text) and expr_text in context:
            return {
                "node_type": "VARIABLE_REFERENCE",
                "name": expr_text
            }
        
        # Default to variable reference
        return {
            "node_type": "VARIABLE_REFERENCE",
            "name": expr_text
        }


class ILRToTauTranslator:
    """Translates ILR (JSON) to TAU format."""
    
    def translate_to_tau(self, ilr: Dict[str, Any]) -> str:
        """Translate ILR to TAU syntax."""
        if "unit" not in ilr:
            return ""
        
        unit = ilr["unit"]
        tau_parts = []
        
        # Check for SBF declarations
        if "sbf_declaration" in unit:
            sbf = unit["sbf_declaration"]
            if sbf["type"] == "input":
                return f'sbf {sbf["name"]} = i(\\"{sbf["file"]}\\")' 
            elif sbf["type"] == "output":
                return f'sbf {sbf["name"]} = o(\\"{sbf["file"]}\\")' 
        
        # Check if this is a simple stream assignment
        decls = unit.get("declarations", [])
        stmts = unit.get("statements", [])
        
        # Special handling for stream output assignments
        if (len(decls) == 1 and len(stmts) == 1 and 
            decls[0].get("is_stream") and 
            stmts[0].get("node_type") == "ASSIGNMENT_STATEMENT"):
            # Just return the assignment
            return self._translate_statement(stmts[0])
        
        # Process declarations
        for decl in decls:
            tau_decl = self._translate_declaration(decl)
            if tau_decl:
                tau_parts.append(tau_decl)
        
        # Process statements
        for stmt in stmts:
            tau_stmt = self._translate_statement(stmt)
            if tau_stmt:
                tau_parts.append(tau_stmt)
        
        # Process expressions at top level  
        if "expression" in unit:
            tau_expr = self._translate_expression(unit["expression"])
            tau_parts.append(tau_expr)
        
        return "\n".join(tau_parts) if tau_parts else ""
    
    def _translate_declaration(self, decl: Dict[str, Any]) -> str:
        """Translate a declaration to TAU."""
        node_type = decl.get("node_type")
        
        if node_type == "FUNCTION_DECLARATION":
            name = decl["name"]
            params = decl.get("parameters", [])
            param_names = [p["name"] for p in params]
            
            # Handle body if present
            body = decl.get("body", [])
            if body and len(body) > 0:
                # Look for return statement
                for stmt in body:
                    if stmt.get("node_type") == "RETURN_STATEMENT":
                        expr = self._translate_expression(stmt["expression"])
                        return f"{name}({', '.join(param_names)}) := {expr}"
            
            # No body, just declaration
            return f"{name}({', '.join(param_names)})"
            
        elif node_type == "VARIABLE_DECLARATION":
            name = decl["name"]
            if decl.get("initial_value"):
                value = self._translate_expression(decl["initial_value"])
                return f"{name} = {value}"
            else:
                return f"{name}"
        
        return ""
    
    def _translate_statement(self, stmt: Dict[str, Any]) -> str:
        """Translate a statement to TAU."""
        node_type = stmt.get("node_type")
        
        if node_type == "ASSIGNMENT_STATEMENT":
            target = self._translate_expression(stmt["target"])
            expr = self._translate_expression(stmt["expression"])
            return f"{target} = {expr}"
            
        elif node_type == "ASSERTION_STATEMENT":
            condition = self._translate_expression(stmt["condition"])
            return condition
            
        elif node_type == "TEMPORAL_STATEMENT":
            operator = stmt["operator"]
            condition = self._translate_expression(stmt["condition"])
            if operator == "ALWAYS":
                return f"always ({condition})"
            elif operator == "SOMETIMES":
                return f"sometimes ({condition})"
            # Add other temporal operators as needed
        
        return ""
    
    def _translate_expression(self, expr: Dict[str, Any]) -> str:
        """Translate an expression to TAU."""
        if not expr:
            return ""
        
        node_type = expr.get("node_type")
        
        if node_type == "VARIABLE_REFERENCE":
            name = expr["name"]
            if expr.get("temporal_qualifier"):
                offset = expr["temporal_qualifier"]["offset"]
                if offset == 0:
                    return f"{name}[t]"
                elif offset < 0:
                    return f"{name}[t{offset}]"
                else:
                    return f"{name}[t+{offset}]"
            return name
            
        elif node_type == "NUMERIC_CONSTANT":
            return str(expr["value"])
            
        elif node_type == "BOOLEAN_CONSTANT":
            return "true" if expr["value"] else "false"
            
        elif node_type == "STRING_CONSTANT":
            return f'"{expr["value"]}"'
            
        elif node_type == "COMPARISON_EXPRESSION":
            left = self._translate_expression(expr["left_operand"])
            right = self._translate_expression(expr["right_operand"])
            
            # Add parentheses around logical expressions in comparisons
            if expr["right_operand"].get("node_type") == "LOGICAL_EXPRESSION":
                right = f"({right})"
            if expr["left_operand"].get("node_type") == "LOGICAL_EXPRESSION":
                left = f"({left})"
            
            op_map = {
                "EQ": "=", "NEQ": "!=",
                "LT": "<", "LTE": "<=",
                "GT": ">", "GTE": ">="
            }
            op = op_map.get(expr["operator"], expr["operator"])
            return f"{left} {op} {right}"
            
        elif node_type == "LOGICAL_EXPRESSION":
            op = expr["operator"]
            operands = expr["operands"]
            
            if op == "NOT":
                inner = self._translate_expression(operands[0])
                return f"{inner}'"
            elif op == "AND":
                parts = [self._translate_expression(op) for op in operands]
                return " & ".join(parts)
            elif op == "OR":
                parts = []
                for operand in operands:
                    part = self._translate_expression(operand)
                    # Add parentheses around AND expressions in OR operations 
                    # when there are multiple OR operands or the AND contains NOT
                    if (operand.get("node_type") == "LOGICAL_EXPRESSION" and 
                        operand.get("operator") == "AND" and 
                        (len(operands) > 2 or  # Multiple OR operands 
                         any(op.get("node_type") == "LOGICAL_EXPRESSION" and op.get("operator") == "NOT" 
                             for op in operand.get("operands", [])))):  # AND contains NOT
                        part = f"({part})"
                    parts.append(part)
                return " \\\\ ".join(parts)
            elif op == "XOR":
                parts = [self._translate_expression(op) for op in operands]
                return " + ".join(parts)
            elif op == "IMPLIES":
                left = self._translate_expression(operands[0])
                right = self._translate_expression(operands[1])
                return f"({left}) -> {right}"
                
        elif node_type == "ARITHMETIC_EXPRESSION":
            left = self._translate_expression(expr["left_operand"])
            right = self._translate_expression(expr["right_operand"])
            op_map = {
                "ADD": "+", "SUB": "-",
                "MUL": "*", "DIV": "/",
                "MOD": "%"
            }
            op = op_map.get(expr["operator"], expr["operator"])
            return f"{left} {op} {right}"
            
        elif node_type == "UNARY_ARITHMETIC_EXPRESSION":
            if expr["operator"] == "NEG":
                inner = self._translate_expression(expr["operand"])
                return f"-{inner}"
                
        elif node_type == "FUNCTION_CALL":
            name = expr["function_name"]
            args = [self._translate_expression(arg) for arg in expr.get("arguments", [])]
            return f"{name}({', '.join(args)})"
            
        elif node_type == "QUANTIFIER_EXPRESSION":
            op = expr["operator"]
            vars = expr["bound_variables"]
            body = self._translate_expression(expr["expression"])
            
            if op == "FOR_ALL":
                var_names = [v["name"] for v in vars]
                if len(var_names) == 1:
                    return f"{{all {var_names[0]}}} ({body})"
                else:
                    return f"{{all {', '.join(var_names)}}} ({body})"
            elif op == "EXISTS":
                var_names = [v["name"] for v in vars]
                if len(var_names) == 1:
                    return f"{{ex {var_names[0]}}} ({body})"
                else:
                    return f"{{ex {', '.join(var_names)}}} ({body})"
        
        return str(expr)