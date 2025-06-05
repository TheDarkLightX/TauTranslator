"""
ILR Node Definitions
===================

Defines the Intermediate Logic Representation (ILR) node types
used for translating between natural language and formal languages.

Author: DarkLightX/Dana Edwards
"""

from typing import Dict, Any, Optional, List
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
    value: float
    
    def __init__(self, value: float):
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
    left: 'ILRNode'
    operator: str
    right: 'ILRNode'
    
    def __init__(self, left: 'ILRNode', operator: str, right: 'ILRNode'):
        super().__init__(node_type="COMPARISON")
        self.left = left
        self.operator = operator
        self.right = right


@dataclass
class LogicalExpression(ILRNode):
    """Logical operation between expressions."""
    operator: str
    operands: List['ILRNode']
    
    def __init__(self, operator: str, operands: List['ILRNode']):
        super().__init__(node_type="LOGICAL_EXPRESSION")
        self.operator = operator
        self.operands = operands


@dataclass
class ArithmeticExpression(ILRNode):
    """Arithmetic operation between expressions."""
    operator: str
    operands: List['ILRNode']
    
    def __init__(self, operator: str, operands: List['ILRNode']):
        super().__init__(node_type="ARITHMETIC_EXPRESSION")
        self.operator = operator
        self.operands = operands
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper operand serialization."""
        return {
            "node_type": self.node_type,
            "operator": self.operator,
            "operands": [op.to_dict() if hasattr(op, 'to_dict') else op 
                        for op in self.operands]
        }


@dataclass
class FunctionCall(ILRNode):
    """Function or predicate call."""
    name: str
    arguments: List['ILRNode']
    
    def __init__(self, name: str, arguments: List['ILRNode']):
        super().__init__(node_type="FUNCTION_CALL")
        self.name = name
        self.arguments = arguments


@dataclass
class FunctionDeclaration:
    """Function or predicate declaration."""
    name: str
    parameters: List[str]
    body: Optional['ILRNode'] = None
    return_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "parameters": self.parameters,
            "body": self.body.to_dict() if self.body else None,
            "return_type": self.return_type
        }


@dataclass
class VariableDeclaration:
    """Variable declaration with optional type and initial value."""
    name: str
    var_type: Optional[str] = None
    initial_value: Optional['ILRNode'] = None
    is_stream: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.var_type,
            "initial_value": self.initial_value.to_dict() if self.initial_value else None,
            "is_stream": self.is_stream
        }


@dataclass
class AssignmentStatement:
    """Assignment of value to variable."""
    variable: str
    value: 'ILRNode'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "variable": self.variable,
            "value": self.value.to_dict() if hasattr(self.value, 'to_dict') else self.value
        }


@dataclass
class ConditionalExpression(ILRNode):
    """Conditional (if-then-else) expression."""
    condition: 'ILRNode'
    then_branch: 'ILRNode'
    else_branch: Optional['ILRNode'] = None
    
    def __init__(self, condition: 'ILRNode', then_branch: 'ILRNode', 
                 else_branch: Optional['ILRNode'] = None):
        super().__init__(node_type="CONDITIONAL")
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch