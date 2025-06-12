"""
ILR expression parsing service following the Intentional Disclosure Principle.

Handles expression parsing with all methods ≤10 lines following IDP Rule 2.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Tuple, Optional
from returns.result import Result, Success, Failure

from .ilr_types import (
    ILRNode, VariableReference, BooleanConstant, NumericConstant,
    StringConstant, ComparisonExpression, LogicalExpression,
    ArithmeticExpression, FunctionCall, VariableName, FunctionName,
    TemporalQualifier, TemporalOffset, ComparisonOperator,
    LogicalOperator, ArithmeticOperator, ExpressionContext
)
from ..infrastructure.ilr_infrastructure import (
    ExpressionTokenizer, TemporalReferenceParser, ParenthesesSplitter,
    OperatorMapper
)


class ExpressionParsingService:
    """Pure business logic for parsing expressions into ILR nodes."""
    
    def __init__(self, context: Optional[ExpressionContext] = None):
        self._context = context or ExpressionContext()
    
    def parse_expression(self, text: str) -> Result[ILRNode, str]:
        """Parse expression text into ILR node."""
        text = text.strip()
        
        # Handle empty expression
        if not text:
            return Failure("Empty expression")
        
        # Try parsing in order of precedence
        return (self._try_parse_parentheses(text)
                or self._try_parse_logical_or(text)
                or self._try_parse_logical_and(text)
                or self._try_parse_comparison(text)
                or self._try_parse_arithmetic(text)
                or self._try_parse_predicate(text)
                or self._try_parse_atom(text)
                or Failure(f"Cannot parse expression: {text}"))
    
    def _try_parse_parentheses(self, text: str) -> Optional[Result[ILRNode, str]]:
        """Try to parse parentheses expression."""
        if text.startswith('(') and text.endswith(')'):
            inner = text[1:-1]
            if self._is_balanced_parens(inner):
                return self.parse_expression(inner)
        return None
    
    def _try_parse_logical_or(self, text: str) -> Optional[Result[ILRNode, str]]:
        """Try to parse OR/XOR expression."""
        for op_str in [' or ', ' xor ']:
            parts = text.split(op_str, 1)
            if len(parts) > 1:
                return self._build_logical_expression(parts, op_str.strip())
        return None
    
    def _try_parse_logical_and(self, text: str) -> Optional[Result[ILRNode, str]]:
        """Try to parse AND expression."""
        parts = text.split(' and ', 1)
        if len(parts) > 1:
            return self._build_logical_expression(parts, 'and')
        
        # Also try NOT
        if text.strip().startswith('not '):
            return self._parse_not_expression(text)
        
        return None
    
    def _try_parse_comparison(self, text: str) -> Optional[Result[ILRNode, str]]:
        """Try to parse comparison expression."""
        for op_str in ['<=', '>=', '!=', '=', '<', '>']:
            if op_str in text:
                return self._parse_comparison_with_op(text, op_str)
        return None
    
    def _try_parse_arithmetic(self, text: str) -> Optional[Result[ILRNode, str]]:
        """Try to parse arithmetic expression."""
        # Try addition/subtraction first (lowest precedence)
        for op_str in ['+', '-']:
            parts = self._smart_split_arithmetic(text, op_str)
            if len(parts) > 1:
                return self._build_arithmetic_expression(parts, op_str)
        
        # Then multiplication/division
        for op_str in ['*', '/', '%', ' mod ']:
            parts = text.split(op_str, 1) if op_str != ' mod ' else text.split(' mod ', 1)
            if len(parts) > 1:
                return self._build_arithmetic_expression(parts, op_str.strip())
        
        return None
    
    def _try_parse_predicate(self, text: str) -> Optional[Result[ILRNode, str]]:
        """Try to parse predicate expressions like 'x is positive'."""
        if ' is ' in text:
            parts = text.split(' is ', 1)
            if len(parts) == 2:
                subject = parts[0].strip()
                predicate = parts[1].strip()
                
                # Parse as predicate call
                from ..domain.ilr_types import PredicateCall, PredicateName
                subject_result = self.parse_expression(subject)
                if isinstance(subject_result, Failure):
                    return subject_result
                
                return Success(PredicateCall(
                    predicate_name=PredicateName(predicate),
                    arguments=[subject_result.unwrap()]
                ))
        
        return None
    
    def _try_parse_atom(self, text: str) -> Optional[Result[ILRNode, str]]:
        """Try to parse atomic expression."""
        text = text.strip()
        
        # Boolean constant
        if text.lower() in ['true', 'false']:
            return Success(BooleanConstant(value=text.lower() == 'true'))
        
        # Numeric constant
        try:
            if '.' in text:
                return Success(NumericConstant(value=float(text)))
            return Success(NumericConstant(value=int(text)))
        except ValueError:
            pass
        
        # String constant
        if text.startswith('"') and text.endswith('"'):
            return Success(StringConstant(value=text[1:-1]))
        
        # Function call
        if '(' in text and text.endswith(')'):
            return self._parse_function_call(text)
        
        # Temporal reference
        if '[' in text and ']' in text:
            return self._parse_temporal_reference(text)
        
        # Variable reference
        if text.isidentifier():
            return Success(VariableReference(VariableName(text)))
        
        return None
    
    def _split_by_operator(self, text: str, operator: str) -> List[str]:
        """Split text by operator respecting parentheses."""
        return ParenthesesSplitter.split_respecting_parens(text, operator)
    
    def _is_balanced_parens(self, text: str) -> bool:
        """Check if parentheses are balanced."""
        depth = 0
        for char in text:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            if depth < 0:
                return False
        return depth == 0
    
    def _build_logical_expression(self, parts: List[str], op_str: str) -> Result[ILRNode, str]:
        """Build logical expression from parts."""
        op_result = OperatorMapper.map_logical_operator(op_str)
        if isinstance(op_result, Failure):
            return op_result
        
        operand_results = [self.parse_expression(part) for part in parts]
        
        # Check for failures
        for i, result in enumerate(operand_results):
            if isinstance(result, Failure):
                return Failure(f"Failed to parse operand {i+1}: {result.failure()}")
        
        operands = [r.unwrap() for r in operand_results]
        return Success(LogicalExpression(op_result.unwrap(), operands))
    
    def _parse_not_expression(self, text: str) -> Result[ILRNode, str]:
        """Parse NOT expression."""
        inner_text = text[4:].strip()  # Remove 'not '
        inner_result = self.parse_expression(inner_text)
        
        if isinstance(inner_result, Failure):
            return inner_result
        
        return Success(LogicalExpression(LogicalOperator.NOT, [inner_result.unwrap()]))
    
    def _parse_comparison_with_op(self, text: str, op_str: str) -> Result[ILRNode, str]:
        """Parse comparison with specific operator."""
        parts = text.split(op_str, 1)
        if len(parts) != 2:
            return Failure(f"Invalid comparison expression: {text}")
        
        left_result = self.parse_expression(parts[0])
        right_result = self.parse_expression(parts[1])
        
        if isinstance(left_result, Failure):
            return left_result
        if isinstance(right_result, Failure):
            return right_result
        
        op_result = OperatorMapper.map_comparison_operator(op_str)
        if isinstance(op_result, Failure):
            return op_result
        
        return Success(ComparisonExpression(
            op_result.unwrap(),
            left_result.unwrap(),
            right_result.unwrap()
        ))
    
    def _build_arithmetic_expression(self, parts: List[str], op_str: str) -> Result[ILRNode, str]:
        """Build arithmetic expression from parts."""
        op_result = OperatorMapper.map_arithmetic_operator(op_str)
        if isinstance(op_result, Failure):
            return op_result
        
        operand_results = [self.parse_expression(part) for part in parts]
        
        # Check for failures
        for i, result in enumerate(operand_results):
            if isinstance(result, Failure):
                return Failure(f"Failed to parse operand {i+1}: {result.failure()}")
        
        operands = [r.unwrap() for r in operand_results]
        return Success(ArithmeticExpression(op_result.unwrap(), operands))
    
    def _parse_function_call(self, text: str) -> Result[ILRNode, str]:
        """Parse function call expression."""
        paren_idx = text.index('(')
        func_name = text[:paren_idx].strip()
        
        if not func_name.isidentifier():
            return Failure(f"Invalid function name: {func_name}")
        
        args_text = text[paren_idx+1:-1].strip()
        
        if not args_text:
            return Success(FunctionCall(FunctionName(func_name), []))
        
        # Parse arguments
        arg_parts = self._split_arguments(args_text)
        arg_results = [self.parse_expression(part.strip()) for part in arg_parts]
        
        # Check for failures
        for i, result in enumerate(arg_results):
            if isinstance(result, Failure):
                return Failure(f"Failed to parse argument {i+1}: {result.failure()}")
        
        arguments = [r.unwrap() for r in arg_results]
        return Success(FunctionCall(FunctionName(func_name), arguments))
    
    def _split_arguments(self, text: str) -> List[str]:
        """Split function arguments by comma, respecting parentheses."""
        # Simple implementation for now
        args = []
        current_arg = ""
        paren_depth = 0
        
        for char in text:
            if char == ',' and paren_depth == 0:
                args.append(current_arg)
                current_arg = ""
            else:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                current_arg += char
        
        if current_arg:
            args.append(current_arg)
        
        return args
    
    def _smart_split_arithmetic(self, text: str, op: str) -> List[str]:
        """Split arithmetic expression, respecting brackets and parentheses."""
        parts = []
        current = ""
        bracket_depth = 0
        paren_depth = 0
        i = 0
        
        while i < len(text):
            char = text[i]
            
            # Track depth
            if char == '[':
                bracket_depth += 1
            elif char == ']':
                bracket_depth -= 1
            elif char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            
            # Check for operator at top level
            if (char == op and bracket_depth == 0 and paren_depth == 0 and
                (op != '-' or i == 0 or text[i-1] not in '[(')):
                if current:
                    parts.append(current)
                    current = ""
                    i += 1
                    continue
            
            current += char
            i += 1
        
        if current:
            parts.append(current)
        
        return parts if len(parts) > 1 else [text]
    
    def _parse_temporal_reference(self, text: str) -> Result[ILRNode, str]:
        """Parse temporal reference like o1[t-1]."""
        result = TemporalReferenceParser.parse_temporal_reference(text)
        
        if isinstance(result, Failure):
            return result
        
        var_name, offset = result.unwrap()
        
        if offset == 0:
            return Success(VariableReference(var_name))
        
        temporal_qualifier = TemporalQualifier(offset)
        return Success(VariableReference(var_name, temporal_qualifier))


class TemporalExpressionService(ExpressionParsingService):
    """Expression parser with temporal support."""
    
    def __init__(self):
        super().__init__(ExpressionContext(allow_temporal=True))
    
    def parse_temporal_expression(self, text: str) -> Result[ILRNode, str]:
        """Parse expression that may contain temporal references."""
        # Handle complement operator (o1' for NOT o1)
        if text.endswith("'"):
            base_text = text[:-1].strip()
            base_result = self.parse_expression(base_text)
            
            if isinstance(base_result, Failure):
                return base_result
            
            return Success(LogicalExpression(LogicalOperator.NOT, [base_result.unwrap()]))
        
        return self.parse_expression(text)