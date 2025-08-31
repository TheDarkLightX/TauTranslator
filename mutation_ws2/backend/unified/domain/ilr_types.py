"""
ILR (Intermediate Logic Representation) domain types following the Intentional Disclosure Principle.

These immutable domain types replace primitive obsession and provide clear
type boundaries for ILR translation operations.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union, NewType
from enum import Enum

# Domain Type Aliases
VariableName = NewType("VariableName", str)
FunctionName = NewType("FunctionName", str)
PredicateName = NewType("PredicateName", str)
OperatorSymbol = NewType("OperatorSymbol", str)
ExpressionText = NewType("ExpressionText", str)
TauCode = NewType("TauCode", str)
ILRJson = NewType("ILRJson", str)
TemporalOffset = NewType("TemporalOffset", int)

class NodeType(Enum):
    """ILR node types."""
    VARIABLE_REFERENCE = "VARIABLE_REFERENCE"
    BOOLEAN_CONSTANT = "BOOLEAN_CONSTANT"
    NUMERIC_CONSTANT = "NUMERIC_CONSTANT"
    STRING_CONSTANT = "STRING_CONSTANT"
    COMPARISON_EXPRESSION = "COMPARISON_EXPRESSION"
    LOGICAL_EXPRESSION = "LOGICAL_EXPRESSION"
    ARITHMETIC_EXPRESSION = "ARITHMETIC_EXPRESSION"
    FUNCTION_CALL = "FUNCTION_CALL"
    PREDICATE_CALL = "PREDICATE_CALL"
    QUANTIFIER_EXPRESSION = "QUANTIFIER_EXPRESSION"
    CONDITIONAL_EXPRESSION = "CONDITIONAL_EXPRESSION"
    TEMPORAL_STATEMENT = "TEMPORAL_STATEMENT"

class ComparisonOperator(Enum):
    """Comparison operators."""
    EQ = "EQ"
    NEQ = "NEQ"
    LT = "LT"
    LTE = "LTE"
    GT = "GT"
    GTE = "GTE"

class LogicalOperator(Enum):
    """Logical operators."""
    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    NOT = "NOT"
    IMPLIES = "IMPLIES"

class ArithmeticOperator(Enum):
    """Arithmetic operators."""
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    POW = "POW"
    NEG = "NEG"

class QuantifierType(Enum):
    """Quantifier types."""
    FOR_ALL = "FOR_ALL"
    EXISTS = "EXISTS"

class TemporalOperator(Enum):
    """Temporal operators."""
    ALWAYS = "ALWAYS"
    SOMETIMES = "SOMETIMES"
    NEXT = "NEXT"
    UNTIL = "UNTIL"

class DataType(Enum):
    """ILR data types."""
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    STREAM = "STREAM"
    AUTO = "AUTO"

class PatternType(Enum):
    """Natural language pattern types."""
    PREDICATE_DEFINITION = "predicate_definition"
    FUNCTION_DEFINITION = "function_definition"
    UNIVERSAL = "universal"
    EXISTENTIAL = "existential"
    CONDITIONAL = "conditional"
    ASSIGNMENT = "assignment"
    BOOLEAN_EXPR = "boolean_expr"
    NEGATION = "negation"
    STREAM_ASSIGNMENT = "stream_assignment"
    SBF_INPUT = "sbf_input"
    SBF_OUTPUT = "sbf_output"
    STREAM_RULE = "stream_rule"
    TEMPORAL_ALWAYS = "temporal_always"
    ASSERTION = "assertion"

@dataclass(frozen=True)
class TemporalQualifier:
    """Temporal qualifier for variable references."""
    offset: TemporalOffset
    operator: str = "TIME_OFFSET"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.operator,
            "offset": int(self.offset)
        }

@dataclass(frozen=True)
class ILRNode:
    """Base class for all ILR nodes."""
    node_type: NodeType = field(init=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {"node_type": self.node_type.value}

@dataclass(frozen=True)
class VariableReference(ILRNode):
    """Reference to a variable or stream."""
    name: VariableName
    temporal_qualifier: Optional[TemporalQualifier] = None
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.VARIABLE_REFERENCE)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "node_type": self.node_type.value,
            "name": str(self.name)
        }
        if self.temporal_qualifier:
            result["temporal_qualifier"] = self.temporal_qualifier.to_dict()
        return result

@dataclass(frozen=True)
class BooleanConstant(ILRNode):
    """Boolean literal value."""
    value: bool
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.BOOLEAN_CONSTANT)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type.value,
            "value": self.value
        }

@dataclass(frozen=True)
class NumericConstant(ILRNode):
    """Numeric literal value."""
    value: Union[int, float]
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.NUMERIC_CONSTANT)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type.value,
            "value": self.value
        }

@dataclass(frozen=True)
class StringConstant(ILRNode):
    """String literal value."""
    value: str
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.STRING_CONSTANT)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type.value,
            "value": self.value
        }

@dataclass(frozen=True)
class ComparisonExpression(ILRNode):
    """Comparison between two expressions."""
    operator: ComparisonOperator
    left_operand: ILRNode
    right_operand: ILRNode
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.COMPARISON_EXPRESSION)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type.value,
            "operator": self.operator.value,
            "left_operand": self.left_operand.to_dict(),
            "right_operand": self.right_operand.to_dict()
        }

@dataclass(frozen=True)
class LogicalExpression(ILRNode):
    """Logical operation."""
    operator: LogicalOperator
    operands: List[ILRNode]
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.LOGICAL_EXPRESSION)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type.value,
            "operator": self.operator.value,
            "operands": [op.to_dict() for op in self.operands]
        }

@dataclass(frozen=True)
class ArithmeticExpression(ILRNode):
    """Arithmetic operation."""
    operator: ArithmeticOperator
    operands: List[ILRNode]
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.ARITHMETIC_EXPRESSION)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type.value,
            "operator": self.operator.value,
            "operands": [op.to_dict() for op in self.operands]
        }

@dataclass(frozen=True)
class FunctionCall(ILRNode):
    """Function call expression."""
    function_name: FunctionName
    arguments: List[ILRNode]
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.FUNCTION_CALL)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type.value,
            "function_name": str(self.function_name),
            "arguments": [arg.to_dict() for arg in self.arguments]
        }

@dataclass(frozen=True)
class PredicateCall(ILRNode):
    """Predicate call expression."""
    predicate_name: PredicateName
    arguments: List[ILRNode]
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.PREDICATE_CALL)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type.value,
            "predicate_name": str(self.predicate_name),
            "arguments": [arg.to_dict() for arg in self.arguments]
        }

@dataclass(frozen=True)
class QuantifierExpression(ILRNode):
    """Quantifier expression (FOR_ALL, EXISTS)."""
    quantifier: QuantifierType
    bound_variables: List[Dict[str, str]]
    body: ILRNode
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.QUANTIFIER_EXPRESSION)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type.value,
            "quantifier": self.quantifier.value,
            "bound_variables": self.bound_variables,
            "body": self.body.to_dict()
        }

@dataclass(frozen=True)
class ConditionalExpression(ILRNode):
    """Conditional (if-then-else) expression."""
    condition: ILRNode
    then_expression: ILRNode
    else_expression: Optional[ILRNode] = None
    
    def __post_init__(self):
        object.__setattr__(self, 'node_type', NodeType.CONDITIONAL_EXPRESSION)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "node_type": self.node_type.value,
            "condition": self.condition.to_dict(),
            "then_expression": self.then_expression.to_dict()
        }
        if self.else_expression:
            result["else_expression"] = self.else_expression.to_dict()
        return result

@dataclass(frozen=True)
class FunctionParameter:
    """Function parameter definition."""
    name: str
    data_type: DataType
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "data_type": self.data_type.value
        }

@dataclass(frozen=True)
class FunctionDeclaration:
    """Function or predicate declaration."""
    name: FunctionName
    parameters: List[FunctionParameter]
    return_type: DataType
    body: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": str(self.name),
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type.value,
            "body": self.body
        }

@dataclass(frozen=True)
class VariableDeclaration:
    """Variable declaration."""
    name: VariableName
    data_type: DataType
    initial_value: Optional[ILRNode] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": str(self.name),
            "data_type": self.data_type.value
        }
        if self.initial_value:
            result["initial_value"] = self.initial_value.to_dict()
        return result

@dataclass(frozen=True)
class AssignmentStatement:
    """Assignment statement."""
    target: VariableName
    value: ILRNode
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ASSIGNMENT",
            "target": str(self.target),
            "value": self.value.to_dict()
        }

@dataclass(frozen=True)
class AssertionStatement:
    """Assertion statement."""
    expression: ILRNode
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ASSERTION",
            "expression": self.expression.to_dict()
        }

@dataclass(frozen=True)
class TemporalStatement:
    """Temporal statement."""
    operator: TemporalOperator
    expression: ILRNode
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "TEMPORAL",
            "operator": self.operator.value,
            "expression": self.expression.to_dict()
        }

@dataclass(frozen=True)
class ILRProgram:
    """Complete ILR program."""
    declarations: List[Union[FunctionDeclaration, VariableDeclaration]]
    statements: List[Union[AssignmentStatement, AssertionStatement, TemporalStatement]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ilr_version": "1.0",
            "program": {
                "type": "PROGRAM_UNIT",
                "declarations": [d.to_dict() for d in self.declarations],
                "statements": [s.to_dict() for s in self.statements]
            }
        }
    
    def to_json(self) -> ILRJson:
        """Convert to JSON string."""
        import json
        return ILRJson(json.dumps(self.to_dict(), indent=2))

@dataclass(frozen=True)
class PatternMatch:
    """Result of pattern matching."""
    pattern_type: PatternType
    matched_groups: Dict[str, str]
    confidence: float = 1.0
    
    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.8

@dataclass(frozen=True)
class TranslationResult:
    """Result of ILR translation."""
    success: bool
    ilr_json: Optional[ILRJson] = None
    tau_code: Optional[TauCode] = None
    error_message: Optional[str] = None
    
    @classmethod
    def success_ilr(cls, ilr_json: ILRJson) -> 'TranslationResult':
        return cls(success=True, ilr_json=ilr_json)
    
    @classmethod
    def success_tau(cls, tau_code: TauCode) -> 'TranslationResult':
        return cls(success=True, tau_code=tau_code)
    
    @classmethod
    def failure(cls, error: str) -> 'TranslationResult':
        return cls(success=False, error_message=error)

@dataclass(frozen=True)
class ExpressionContext:
    """Context for expression parsing."""
    variables: Dict[VariableName, DataType] = field(default_factory=dict)
    functions: Dict[FunctionName, List[DataType]] = field(default_factory=dict)
    allow_temporal: bool = False
    
    def with_variable(self, name: VariableName, data_type: DataType) -> 'ExpressionContext':
        """Add variable to context."""
        new_vars = dict(self.variables)
        new_vars[name] = data_type
        return ExpressionContext(new_vars, self.functions, self.allow_temporal)
    
    def with_temporal(self) -> 'ExpressionContext':
        """Enable temporal references."""
        return ExpressionContext(self.variables, self.functions, True)