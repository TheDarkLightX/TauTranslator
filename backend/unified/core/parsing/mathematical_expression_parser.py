"""
Mathematical Expression Parser - Pure logic, no I/O.
Handles parsing of mathematical and temporal expressions.

Copyright: DarkLightX / Dana Edwards
"""

import re
from typing import Optional, Tuple, List
from backend.unified.core.domain.parser_types import (
    TimeExpression, TimeIndex, MathExpression, 
    VariableName, MathematicalParsingError
)


class MathematicalExpressionParser:
    """
    Pure parser for mathematical expressions - no I/O, fully deterministic.
    Follows IDP principles with clear method names and single responsibilities.
    """
    
    def __init__(self):
        """Initialize parser with compiled patterns."""
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
        self.patterns = {
            'time_offset': re.compile(
                r'(\w+)\s+(minus|plus|[\+\-])\s+(\d+)', 
                re.IGNORECASE
            ),
            'simple_arithmetic': re.compile(
                r'(\w+)\s*([\+\-\*/])\s*(\w+)'
            ),
            'number_word': re.compile(
                r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\b',
                re.IGNORECASE
            )
        }
        
        self.number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
    
    def parse_time_expression_to_ast(self, expr: str) -> TimeExpression:
        """
        Transforms time expressions to AST.
        Examples: 't minus 1' -> TimeExpression(base='t', offset=-1)
                 't plus 2' -> TimeExpression(base='t', offset=2)
        """
        normalized = self._normalize_expression(expr)
        base, offset = self._extract_time_components(normalized)
        
        return TimeExpression(base=TimeIndex(base), offset=offset)
    
    def _normalize_expression(self, expr: str) -> str:
        """Normalize expression for parsing."""
        normalized = expr.strip().lower()
        normalized = self._convert_number_words_to_digits(normalized)
        return normalized
    
    def _convert_number_words_to_digits(self, text: str) -> str:
        """Convert number words to digits."""
        result = text
        for word, digit in self.number_words.items():
            result = re.sub(rf'\b{word}\b', str(digit), result, flags=re.IGNORECASE)
        return result
    
    def _extract_time_components(self, expr: str) -> Tuple[str, Optional[int]]:
        """Extract base time variable and offset from expression."""
        # Check for offset pattern
        match = self.patterns['time_offset'].match(expr)
        
        if match:
            base = match.group(1)
            operator = match.group(2).lower()
            offset_value = int(match.group(3))
            
            offset = self._calculate_offset(operator, offset_value)
            return base, offset
        
        # Simple time variable without offset
        if re.match(r'^\w+$', expr):
            return expr, None
            
        raise MathematicalParsingError(f"Cannot parse time expression: {expr}")
    
    def _calculate_offset(self, operator: str, value: int) -> int:
        """Calculate offset based on operator."""
        if operator in ['minus', '-']:
            return -value
        elif operator in ['plus', '+']:
            return value
        else:
            raise MathematicalParsingError(f"Unknown operator: {operator}")
    
    def parse_arithmetic_to_ast(self, expr: str) -> MathExpression:
        """
        Transforms arithmetic expressions to AST.
        Example: 'x + y' -> MathExpression with proper structure
        """
        normalized = self._normalize_expression(expr)
        parsed_form = self._parse_arithmetic_expression(normalized)
        variables = self._extract_variables(normalized)
        
        return MathExpression(
            expression=expr,
            parsed_form=parsed_form,
            variables=[VariableName(v) for v in variables]
        )
    
    def _parse_arithmetic_expression(self, expr: str) -> str:
        """Parse arithmetic expression to formal notation."""
        # Replace word operators with symbols
        replacements = {
            ' plus ': ' + ',
            ' minus ': ' - ',
            ' times ': ' * ',
            ' divided by ': ' / ',
            ' equals ': ' = ',
            ' equal to ': ' = ',
            ' greater than ': ' > ',
            ' less than ': ' < ',
            ' greater than or equal to ': ' >= ',
            ' less than or equal to ': ' <= ',
            ' not equal to ': ' != ',
            ' not equals ': ' != '
        }
        
        result = expr
        for word, symbol in replacements.items():
            result = result.replace(word, symbol)
        
        return result
    
    def _extract_variables(self, expr: str) -> List[str]:
        """Extract variable names from expression."""
        # Remove operators and numbers to find variables
        tokens = re.findall(r'\b[a-zA-Z]\w*\b', expr)
        # Filter out operator words
        operator_words = {'plus', 'minus', 'times', 'divided', 'equals', 
                         'equal', 'greater', 'less', 'than', 'to', 'by', 'not'}
        
        return [t for t in tokens if t.lower() not in operator_words]
    
    def is_mathematical_expression(self, text: str) -> bool:
        """
        Check if text contains mathematical expressions.
        Used to identify segments that need mathematical parsing.
        """
        math_indicators = [
            'plus', 'minus', 'times', 'divided', 'equals',
            '+', '-', '*', '/', '=', '>', '<', '>=', '<=',
            'greater than', 'less than', 'equal to'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in math_indicators)
    
    def extract_stream_time_notation(self, text: str) -> Optional[str]:
        """
        Extract and normalize stream time notation.
        Example: 'at time t minus 1' -> 't-1'
        """
        # Pattern for "at time <expr>" or "at t" 
        time_pattern = r'at\s+(?:time\s+)?([^\s,\.]+(?:\s+(?:plus|minus|\+|\-)\s+\d+)?)'
        match = re.search(time_pattern, text, re.IGNORECASE)
        
        if match:
            time_expr = match.group(1)
            parsed_time = self.parse_time_expression_to_ast(time_expr)
            return parsed_time.to_notation().strip('[]')  # Remove brackets for internal use
        
        return None