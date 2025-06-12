"""
ILR to TCE Transformer following Craftsmanship Principles
Copyright: DarkLightX/Dana Edwards

Transforms ILR nodes to TCE statements with methods ≤10 lines.
"""

from typing import List, Optional, Dict
from returns.result import Result, Success, Failure

from .ilr_types import (
    ILRNode, VariableReference, BooleanConstant, NumericConstant,
    StringConstant, ComparisonExpression, LogicalExpression,
    ArithmeticExpression, FunctionCall, ConditionalExpression,
    FunctionDeclaration, ComparisonOperator, LogicalOperator,
    ArithmeticOperator
)
from .tce_types import TCEStatement, TCEPattern, TCEBinding


class ILRToTCETransformer:
    """Transforms ILR nodes into TCE statements."""
    
    def __init__(self):
        self._operator_map = self._create_operator_map()
        self._pattern_templates = self._create_pattern_templates()
    
    def transform_ilr_to_tce_async(self, ilr: ILRNode) -> Result[List[TCEStatement], str]:
        """Transform ILR node to TCE statements."""
        try:
            statements = self._transform_node(ilr)
            return Success(statements)
        except Exception as e:
            return Failure(f"ILR transformation failed: {str(e)}")
    
    def _transform_node(self, node: ILRNode) -> List[TCEStatement]:
        """Transform a single ILR node."""
        if isinstance(node, FunctionDeclaration):
            return self._transform_function_declaration(node)
        elif isinstance(node, ConditionalExpression):
            return self._transform_conditional(node)
        elif isinstance(node, ComparisonExpression):
            return self._transform_comparison(node)
        else:
            return self._transform_expression(node)
    
    def _transform_function_declaration(self, func: FunctionDeclaration) -> List[TCEStatement]:
        """Transform function declaration to TCE."""
        pattern = f"{func.name} is a function"
        bindings = {"function_name": func.name, "parameters": func.parameters}
        statements = [TCEStatement(pattern=pattern, bindings=bindings)]
        
        if func.body:
            body_statements = self._transform_node(func.body)
            statements.extend(body_statements)
        
        return statements
    
    def _transform_conditional(self, cond: ConditionalExpression) -> List[TCEStatement]:
        """Transform conditional to TCE if-then pattern."""
        condition_tce = self._expression_to_tce(cond.condition)
        then_tce = self._expression_to_tce(cond.then_expr)
        
        pattern = f"if {condition_tce} then {then_tce}"
        bindings = {"condition": condition_tce, "consequence": then_tce}
        
        statements = [TCEStatement(pattern=pattern, bindings=bindings)]
        
        if cond.else_expr:
            else_tce = self._expression_to_tce(cond.else_expr)
            statements[0].bindings["alternative"] = else_tce
            
        return statements
    
    def _transform_comparison(self, comp: ComparisonExpression) -> List[TCEStatement]:
        """Transform comparison to TCE pattern."""
        left_tce = self._expression_to_tce(comp.left_operand)
        right_tce = self._expression_to_tce(comp.right_operand)
        operator_tce = self._map_comparison_operator(comp.operator)
        
        pattern = f"{left_tce} {operator_tce} {right_tce}"
        bindings = {"left": left_tce, "operator": operator_tce, "right": right_tce}
        
        return [TCEStatement(pattern=pattern, bindings=bindings)]
    
    def _transform_expression(self, expr: ILRNode) -> List[TCEStatement]:
        """Transform general expression to TCE."""
        tce_repr = self._expression_to_tce(expr)
        pattern = f"{tce_repr} holds"
        bindings = {"expression": tce_repr}
        
        return [TCEStatement(pattern=pattern, bindings=bindings)]
    
    def _expression_to_tce(self, expr: ILRNode) -> str:
        """Convert ILR expression to TCE string representation."""
        if isinstance(expr, VariableReference):
            return self._variable_to_tce(expr)
        elif isinstance(expr, BooleanConstant):
            return "true" if expr.value else "false"
        elif isinstance(expr, NumericConstant):
            return str(expr.value)
        elif isinstance(expr, StringConstant):
            return f'"{expr.value}"'
        elif isinstance(expr, FunctionCall):
            return self._function_call_to_tce(expr)
        else:
            return self._complex_expression_to_tce(expr)
    
    def _variable_to_tce(self, var: VariableReference) -> str:
        """Convert variable reference to TCE."""
        base = var.name
        if var.temporal_qualifier:
            return f"{base} at {var.temporal_qualifier}"
        return base
    
    def _function_call_to_tce(self, call: FunctionCall) -> str:
        """Convert function call to TCE."""
        args = [self._expression_to_tce(arg) for arg in call.arguments]
        args_str = ", ".join(args)
        return f"{call.function_name}({args_str})"
    
    def _complex_expression_to_tce(self, expr: ILRNode) -> str:
        """Convert complex expressions to TCE."""
        if isinstance(expr, LogicalExpression):
            return self._logical_to_tce(expr)
        elif isinstance(expr, ArithmeticExpression):
            return self._arithmetic_to_tce(expr)
        return str(expr)
    
    def _logical_to_tce(self, expr: LogicalExpression) -> str:
        """Convert logical expression to TCE."""
        if len(expr.operands) == 2:
            left = self._expression_to_tce(expr.operands[0])
            right = self._expression_to_tce(expr.operands[1])
            op = self._map_logical_operator(expr.operator)
            return f"{left} {op} {right}"
        elif len(expr.operands) == 1:
            # Unary operator (NOT)
            operand = self._expression_to_tce(expr.operands[0])
            op = self._map_logical_operator(expr.operator)
            return f"{op} {operand}"
        else:
            # Multiple operands
            parts = [self._expression_to_tce(op) for op in expr.operands]
            op = self._map_logical_operator(expr.operator)
            return f" {op} ".join(parts)
    
    def _arithmetic_to_tce(self, expr: ArithmeticExpression) -> str:
        """Convert arithmetic expression to TCE."""
        if len(expr.operands) >= 2:
            left = self._expression_to_tce(expr.operands[0])
            right = self._expression_to_tce(expr.operands[1])
            op = self._map_arithmetic_operator(expr.operator)
            return f"{left} {op} {right}"
        elif len(expr.operands) == 1:
            # Unary operator (NEG)
            operand = self._expression_to_tce(expr.operands[0])
            return f"-{operand}"
        else:
            return "0"
    
    def _map_comparison_operator(self, op: ComparisonOperator) -> str:
        """Map ILR comparison operator to TCE."""
        return self._operator_map.get(op, op.value)
    
    def _map_logical_operator(self, op: LogicalOperator) -> str:
        """Map ILR logical operator to TCE."""
        return self._operator_map.get(op, op.value)
    
    def _map_arithmetic_operator(self, op: ArithmeticOperator) -> str:
        """Map ILR arithmetic operator to TCE."""
        return self._operator_map.get(op, op.value)
    
    def _create_operator_map(self) -> Dict[str, str]:
        """Create operator mapping dictionary."""
        return {
            ComparisonOperator.EQ: "=",
            ComparisonOperator.NEQ: "!=",
            ComparisonOperator.LT: "<",
            ComparisonOperator.GT: ">",
            ComparisonOperator.LTE: "<=",
            ComparisonOperator.GTE: ">=",
            LogicalOperator.AND: "and",
            LogicalOperator.OR: "or",
            LogicalOperator.NOT: "not",
            ArithmeticOperator.ADD: "plus",
            ArithmeticOperator.SUB: "minus",
            ArithmeticOperator.MUL: "times",
            ArithmeticOperator.DIV: "divided by"
        }
    
    def _create_pattern_templates(self) -> Dict[str, str]:
        """Create TCE pattern templates."""
        return {
            "definition": "{subject} is defined as {definition}",
            "fact": "{fact} holds",
            "rule": "if {condition} then {consequence}",
            "function": "{name} is a function from {domain} to {range}",
            "predicate": "{name} is a predicate on {domain}",
            "constraint": "{constraint} must hold",
            "assertion": "assert that {assertion}"
        }