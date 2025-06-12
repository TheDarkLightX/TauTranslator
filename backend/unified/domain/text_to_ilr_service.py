"""
Text to ILR Service - Direct conversion without pattern matching
Copyright: DarkLightX/Dana Edwards

Converts text directly to ILR following craftsmanship principles.
"""

from typing import Optional
from returns.result import Result, Success, Failure

from .ilr_types import (
    ILRNode, VariableReference, NumericConstant, BooleanConstant,
    ComparisonExpression, LogicalExpression, ArithmeticExpression,
    ConditionalExpression, ComparisonOperator, LogicalOperator,
    ArithmeticOperator, VariableName
)


class TextToILRService:
    """Converts text directly to ILR nodes with logical operation support."""
    
    def convert_text_to_ilr(self, text: str) -> Result[ILRNode, str]:
        """Convert text to ILR node using orchestrator pattern."""
        text = self._normalize_text(text)
        
        # Try different conversions in order (most specific first)
        result = (self._try_conditional(text) or
                 self._try_logical_expression(text) or
                 self._try_comparison(text) or
                 self._try_assignment(text) or
                 self._try_boolean(text))
        
        if result:
            return Success(result)
        return Failure(f"Cannot convert to ILR: {text}")
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing."""
        text = text.strip()
        if text.endswith('.'):
            text = text[:-1]
        return text
    
    def _try_conditional(self, text: str) -> Optional[ILRNode]:
        """Try to parse as conditional."""
        if "if " in text and " then " in text:
            parts = self._split_conditional(text)
            if parts:
                return self._create_conditional(parts)
        return None
    
    def _try_comparison(self, text: str) -> Optional[ILRNode]:
        """Try to parse as comparison."""
        for op_text, op_enum in self._get_comparison_operators():
            if op_text in text:
                parts = text.split(op_text, 1)
                if len(parts) == 2:
                    return self._create_comparison(parts[0], op_enum, parts[1])
        return None
    
    def _try_assignment(self, text: str) -> Optional[ILRNode]:
        """Try to parse as assignment (x is 5)."""
        if " is " in text and " is " not in text.replace(" is ", ""):
            parts = text.split(" is ", 1)
            if len(parts) == 2:
                return self._create_assignment_as_comparison(parts[0], parts[1])
        return None
    
    def _try_logical_expression(self, text: str) -> Optional[ILRNode]:
        """Try to parse as logical expression (AND, OR, NOT, XOR)."""
        # Handle NOT operator first (unary)
        if self._is_negation(text):
            return self._parse_negation(text)
        
        # Handle binary logical operators
        for op_text, op_enum in self._get_logical_operators():
            if op_text in text:
                return self._parse_binary_logical(text, op_text, op_enum)
        
        return None
    
    def _try_boolean(self, text: str) -> Optional[ILRNode]:
        """Try to parse as boolean constant."""
        lower = text.lower()
        if lower in ["true", "false"]:
            return BooleanConstant(value=(lower == "true"))
        return None
    
    def _split_conditional(self, text: str) -> Optional[dict]:
        """Split conditional into parts."""
        if_idx = text.index("if ")
        then_idx = text.index(" then ")
        
        condition = text[if_idx + 3:then_idx].strip()
        rest = text[then_idx + 6:].strip()
        
        else_part = None
        if " else " in rest:
            else_idx = rest.index(" else ")
            then_part = rest[:else_idx].strip()
            else_part = rest[else_idx + 6:].strip()
        else:
            then_part = rest
        
        return {
            'condition': condition,
            'then': then_part,
            'else': else_part
        }
    
    def _create_conditional(self, parts: dict) -> ConditionalExpression:
        """Create conditional expression."""
        condition = self.convert_text_to_ilr(parts['condition']).unwrap()
        then_expr = self.convert_text_to_ilr(parts['then']).unwrap()
        else_expr = None
        
        if parts.get('else'):
            else_result = self.convert_text_to_ilr(parts['else'])
            if isinstance(else_result, Success):
                else_expr = else_result.unwrap()
        
        return ConditionalExpression(
            condition=condition,
            then_expr=then_expr,
            else_expr=else_expr
        )
    
    def _create_comparison(self, left: str, op: ComparisonOperator, right: str) -> ComparisonExpression:
        """Create comparison expression."""
        left_node = self._parse_value(left.strip())
        right_node = self._parse_value(right.strip())
        
        return ComparisonExpression(
            operator=op,
            left_operand=left_node,
            right_operand=right_node
        )
    
    def _create_assignment_as_comparison(self, var: str, value: str) -> ComparisonExpression:
        """Create assignment as equality comparison."""
        return self._create_comparison(var, ComparisonOperator.EQ, value)
    
    def _parse_value(self, text: str) -> ILRNode:
        """Parse a value (variable, number, or boolean)."""
        # Try number
        try:
            num = float(text)
            return NumericConstant(value=num)
        except ValueError:
            pass
        
        # Try boolean
        if text.lower() in ["true", "false"]:
            return BooleanConstant(value=(text.lower() == "true"))
        
        # Default to variable
        return VariableReference(name=VariableName(text))
    
    def _is_negation(self, text: str) -> bool:
        """Check if text represents a negation."""
        return text.startswith("not ") or text.startswith("~")
    
    def _parse_negation(self, text: str) -> LogicalExpression:
        """Parse negation expression."""
        if text.startswith("not "):
            operand_text = text[4:].strip()
        else:  # starts with ~
            operand_text = text[1:].strip()
        
        operand = self._parse_operand(operand_text)
        return LogicalExpression(
            operator=LogicalOperator.NOT,
            operands=[operand]
        )
    
    def _parse_binary_logical(self, text: str, op_text: str, op_enum: LogicalOperator) -> LogicalExpression:
        """Parse binary logical expression."""
        parts = text.split(op_text, 1)
        if len(parts) != 2:
            return None
        
        left_operand = self._parse_operand(parts[0].strip())
        right_operand = self._parse_operand(parts[1].strip())
        
        return LogicalExpression(
            operator=op_enum,
            operands=[left_operand, right_operand]
        )
    
    def _parse_operand(self, text: str) -> ILRNode:
        """Parse an operand (may be recursive for complex expressions)."""
        # Try to convert back to ILR recursively
        result = self.convert_text_to_ilr(text)
        if isinstance(result, Success):
            return result.unwrap()
        
        # Fallback to parsing as a simple value
        return self._parse_value(text)
    
    def _get_logical_operators(self) -> list:
        """Get logical operators in order of precedence."""
        return [
            (" and ", LogicalOperator.AND),
            (" or ", LogicalOperator.OR), 
            (" xor ", LogicalOperator.XOR),
            (" implies ", LogicalOperator.IMPLIES),
        ]
    
    def _get_comparison_operators(self) -> list:
        """Get comparison operators in order of precedence."""
        return [
            ("is greater than or equal to", ComparisonOperator.GTE),
            ("is less than or equal to", ComparisonOperator.LTE),
            ("is greater than", ComparisonOperator.GT),
            ("is less than", ComparisonOperator.LT),
            ("is equal to", ComparisonOperator.EQ),
            ("equals", ComparisonOperator.EQ),
            ("is not equal to", ComparisonOperator.NEQ),
            ("does not equal", ComparisonOperator.NEQ),
            ("is at least", ComparisonOperator.GTE),
            ("is at most", ComparisonOperator.LTE),
        ]