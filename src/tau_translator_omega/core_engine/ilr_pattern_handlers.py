"""
ILR Pattern Handlers
====================

Handles specific pattern translations for the ILR translator.
Extracted to reduce complexity and improve maintainability.

Author: DarkLightX/Dana Edwards
"""

from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod
import re

from .ilr_nodes import (
    ILRNode, VariableReference, BooleanConstant, NumericConstant,
    StringConstant, ComparisonExpression, LogicalExpression,
    ArithmeticExpression, FunctionCall, ConditionalExpression
)


class PatternHandler(ABC):
    """Abstract base class for pattern handlers."""
    
    @abstractmethod
    def can_handle(self, text: str) -> bool:
        """Check if this handler can process the given text."""
        pass
    
    @abstractmethod
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze the text and extract relevant data."""
        pass
    
    @abstractmethod
    def generate_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR structure from analyzed data."""
        pass


class SBFInputHandler(PatternHandler):
    """Handles SBF input patterns like 'SBF X takes Y'."""
    
    def can_handle(self, text: str) -> bool:
        """Check for SBF input pattern."""
        return bool(re.match(r'SBF\s+(\w+)\s+takes\s+(.+)', text, re.IGNORECASE))
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Extract SBF name and input variable."""
        match = re.match(r'SBF\s+(\w+)\s+takes\s+(.+)', text, re.IGNORECASE)
        if match:
            return {
                'sbf_name': match.group(1),
                'input_var': match.group(2)
            }
        return {}
    
    def generate_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for SBF input declaration."""
        return {
            "type": "SBF_INPUT_DECLARATION",
            "sbf_name": data['sbf_name'],
            "input_variable": data['input_var']
        }


class SBFOutputHandler(PatternHandler):
    """Handles SBF output patterns like 'SBF X produces Y'."""
    
    def can_handle(self, text: str) -> bool:
        """Check for SBF output pattern."""
        return bool(re.match(r'SBF\s+(\w+)\s+produces\s+(.+)', text, re.IGNORECASE))
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Extract SBF name and output variable."""
        match = re.match(r'SBF\s+(\w+)\s+produces\s+(.+)', text, re.IGNORECASE)
        if match:
            return {
                'sbf_name': match.group(1),
                'output_var': match.group(2)
            }
        return {}
    
    def generate_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for SBF output declaration."""
        return {
            "type": "SBF_OUTPUT_DECLARATION",
            "sbf_name": data['sbf_name'],
            "output_variable": data['output_var']
        }


class StreamRuleHandler(PatternHandler):
    """Handles stream rule patterns."""
    
    def can_handle(self, text: str) -> bool:
        """Check for stream rule pattern."""
        return "stream" in text.lower() and ("<-" in text or "→" in text)
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Extract stream name and expression."""
        # Handle both <- and → operators
        if "<-" in text:
            parts = text.split("<-", 1)
            operator = "<-"
        else:
            parts = text.split("→", 1)
            operator = "→"
            
        if len(parts) == 2:
            stream_name = parts[0].strip()
            expression = parts[1].strip()
            
            # Extract stream name from declaration
            stream_match = re.search(r'stream\s+(\w+)', stream_name)
            if stream_match:
                return {
                    'stream_name': stream_match.group(1),
                    'expression': expression,
                    'operator': operator
                }
        return {}
    
    def generate_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for stream rule."""
        return {
            "type": "STREAM_RULE",
            "stream_name": data['stream_name'],
            "expression": data['expression'],
            "operator": data['operator']
        }


class TemporalAlwaysHandler(PatternHandler):
    """Handles temporal always patterns."""
    
    def can_handle(self, text: str) -> bool:
        """Check for temporal always pattern."""
        return bool(re.match(r'always\s+(.+)', text, re.IGNORECASE))
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Extract the condition."""
        match = re.match(r'always\s+(.+)', text, re.IGNORECASE)
        if match:
            return {'condition': match.group(1)}
        return {}
    
    def generate_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for temporal always."""
        return {
            "type": "TEMPORAL_ALWAYS",
            "condition": data['condition']
        }


class ConditionalHandler(PatternHandler):
    """Handles conditional patterns (if-then-else)."""
    
    def can_handle(self, text: str) -> bool:
        """Check for conditional pattern."""
        return bool(re.search(r'\bif\b.*\bthen\b', text, re.IGNORECASE))
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Extract condition, then branch, and optional else branch."""
        # Match if-then-else pattern
        match = re.match(
            r'if\s+(.+?)\s+then\s+(.+?)(?:\s+else\s+(.+))?$',
            text, re.IGNORECASE
        )
        if match:
            return {
                'condition': match.group(1),
                'then_branch': match.group(2),
                'else_branch': match.group(3) if match.group(3) else None
            }
        return {}
    
    def generate_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for conditional."""
        ilr = {
            "type": "CONDITIONAL",
            "condition": data['condition'],
            "then": data['then_branch']
        }
        if data['else_branch']:
            ilr['else'] = data['else_branch']
        return ilr


class AssignmentHandler(PatternHandler):
    """Handles assignment patterns."""
    
    def can_handle(self, text: str) -> bool:
        """Check for assignment pattern."""
        return ":=" in text and not "(" in text.split(":=")[0]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Extract variable and value."""
        parts = text.split(":=", 1)
        if len(parts) == 2:
            return {
                'variable': parts[0].strip(),
                'value': parts[1].strip()
            }
        return {}
    
    def generate_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for assignment."""
        return {
            "type": "ASSIGNMENT",
            "variable": data['variable'],
            "value": self._parse_expression(data['value'])
        }
    
    def _parse_expression(self, expr: str) -> Any:
        """Parse a simple expression into ILR node."""
        expr = expr.strip()
        
        # Boolean literals
        if expr.lower() == "true":
            return {"node_type": "BOOLEAN_CONSTANT", "value": True}
        elif expr.lower() == "false":
            return {"node_type": "BOOLEAN_CONSTANT", "value": False}
        
        # Numeric literals
        try:
            if '.' in expr:
                return {"node_type": "NUMERIC_CONSTANT", "value": float(expr)}
            else:
                return {"node_type": "NUMERIC_CONSTANT", "value": int(expr)}
        except ValueError:
            pass
        
        # String literals
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return {"node_type": "STRING_CONSTANT", "value": expr[1:-1]}
        
        # Variable reference
        if expr.isidentifier():
            return {"node_type": "VARIABLE_REFERENCE", "name": expr}
        
        # Default to string
        return {"node_type": "STRING_CONSTANT", "value": expr}


class BooleanOperationHandler(PatternHandler):
    """Handles boolean operation patterns."""
    
    def can_handle(self, text: str) -> bool:
        """Check for boolean operation pattern."""
        return (any(op in text.lower() for op in [' and ', ' or ']) or 
                text.lower().startswith('not '))
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Extract operator and operands."""
        # Check for AND
        if ' and ' in text.lower():
            parts = text.split(' and ', 1)
            return {
                'operator': 'AND',
                'left': parts[0].strip(),
                'right': parts[1].strip() if len(parts) > 1 else None
            }
        
        # Check for OR
        if ' or ' in text.lower():
            parts = text.split(' or ', 1)
            return {
                'operator': 'OR',
                'left': parts[0].strip(),
                'right': parts[1].strip() if len(parts) > 1 else None
            }
        
        # Check for NOT
        if text.lower().startswith('not '):
            return {
                'operator': 'NOT',
                'operand': text[4:].strip()
            }
        
        return {}
    
    def generate_ilr(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ILR for boolean operation."""
        if data['operator'] == 'NOT':
            return {
                "type": "NEGATION",
                "operand": data['operand']
            }
        else:
            return {
                "type": "BOOLEAN_OPERATION",
                "operator": data['operator'],
                "left": data['left'],
                "right": data.get('right')
            }


class PatternHandlerRegistry:
    """Registry for pattern handlers."""
    
    def __init__(self):
        """Initialize with default handlers."""
        self.handlers = [
            SBFInputHandler(),
            SBFOutputHandler(),
            StreamRuleHandler(),
            TemporalAlwaysHandler(),
            ConditionalHandler(),
            AssignmentHandler(),
            BooleanOperationHandler()
        ]
    
    def find_handler(self, text: str) -> Optional[PatternHandler]:
        """Find appropriate handler for the given text."""
        for handler in self.handlers:
            if handler.can_handle(text):
                return handler
        return None
    
    def register_handler(self, handler: PatternHandler):
        """Register a new pattern handler."""
        self.handlers.insert(0, handler)  # Add at beginning for priority