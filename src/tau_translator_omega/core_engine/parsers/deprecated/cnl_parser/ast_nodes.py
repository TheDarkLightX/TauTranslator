from typing import List, Union, Optional, Any
from dataclasses import dataclass, field

from enum import Enum, auto
# --- Base Node ---
@dataclass(frozen=True, repr=False) # repr=False to keep custom __repr__
class ASTNode:
    """Base class for all AST nodes."""
    line: Optional[int] = None
    column: Optional[int] = None

    def __repr__(self) -> str:
        # Simple representation to avoid circular reference issues
        # You might want to include line/col here if always present
        return f"{self.__class__.__name__}(...L{self.line}C{self.column})"

# --- Expression Nodes (also serve as base for many others) ---
@dataclass(frozen=True, repr=False)
class ExprNode(ASTNode):
    """Base class for all nodes that can be part of an expression."""
    pass

# --- Atomic & Value Nodes ---
@dataclass(frozen=True, repr=False)
class AtomNode(ExprNode):
    """Base class for atomic elements in expressions."""
    pass

@dataclass(frozen=True, repr=False)
class ArithmeticNode(ExprNode):
    """Base class for nodes that can be part of an arithmetic expression."""
    pass

@dataclass(frozen=True, repr=False)
class ConstantNode(AtomNode, ArithmeticNode):
    line: Optional[int] = None
    column: Optional[int] = None
    value: Any = None
    value_type: str = "UNKNOWN" # e.g., "NUMBER", "STRING"


class BitVectorType(Enum):
    """Enumerates the types of bitvector literals."""
    INT = auto()
    UINT = auto()
    LONG = auto()
    ULONG = auto()
    BITS = auto()


@dataclass(frozen=True, repr=False)
class BitVectorNode(AtomNode, ArithmeticNode):
    """Represents a bitvector literal in the AST."""
    value: str = ""
    type: BitVectorType = BitVectorType.INT
    line: Optional[int] = None
    column: Optional[int] = None
@dataclass(frozen=True, repr=False)
class NumberNode(AtomNode, ArithmeticNode):
    """Represents a numeric literal."""
    line: Optional[int] = None
    column: Optional[int] = None
    value: Union[int, float, str] = 0

@dataclass(frozen=True, repr=False)
class StringNode(AtomNode):
    """Represents a string literal."""
    line: Optional[int] = None
    column: Optional[int] = None
    value: str = ""

@dataclass(frozen=True, repr=False)
class VariableNode(AtomNode, ArithmeticNode):
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""

# --- Time Specification Nodes ---
@dataclass(frozen=True, repr=False)
class TimeSpecNode(ASTNode):
    """Base class for time specifications."""
    pass

@dataclass(frozen=True, repr=False)
class TimeLiteralNode(TimeSpecNode):
    line: Optional[int] = None
    column: Optional[int] = None
    value: int = 0

@dataclass(frozen=True, repr=False)
class TimeVariableNode(TimeSpecNode):
    line: Optional[int] = None
    column: Optional[int] = None
    variable_name: str = ""

@dataclass(frozen=True, repr=False)
class TimeOffsetNode(TimeSpecNode):
    line: Optional[int] = None
    column: Optional[int] = None
    variable: Optional[VariableNode] = None
    operator: str = "+" # "+" or "-"
    offset: int = 0

@dataclass(frozen=True, repr=False)
class StreamReferenceNode(AtomNode):
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    time_spec: Optional[TimeSpecNode] = None
    stream_type: Optional[str] = None # "input" or "output"

# --- Operational Expression Nodes ---
@dataclass(frozen=True, repr=False)
class PredicateCallNode(ArithmeticNode):
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    args: List[ExprNode] = field(default_factory=list)

@dataclass(frozen=True, repr=False)
class ComparisonNode(ExprNode):
    line: Optional[int] = None
    column: Optional[int] = None
    left: Optional[ArithmeticNode] = None
    operator: str = "equals"
    right: Optional[ArithmeticNode] = None

@dataclass(frozen=True, repr=False)
class ArithmeticBinaryOpNode(ArithmeticNode): # Result of an arithmetic op is an arithmetic value
    line: Optional[int] = None
    column: Optional[int] = None
    left: Optional[ArithmeticNode] = None
    operator: str = "plus"
    right: Optional[ArithmeticNode] = None

@dataclass(frozen=True, repr=False)
class BooleanBinaryOpNode(ExprNode): # Result of a boolean op is a boolean value
    line: Optional[int] = None
    column: Optional[int] = None
    left: Optional[ExprNode] = None
    operator: str = "and"
    right: Optional[ExprNode] = None

@dataclass(frozen=True, repr=False)
class BooleanUnaryOpNode(ExprNode): # Result of a boolean op is a boolean value
    line: Optional[int] = None
    column: Optional[int] = None
    operator: str = "not" # e.g., "not"
    operand: Optional[ExprNode] = None

@dataclass(frozen=True, repr=False)
class NotNode(ExprNode):
    """Represents a logical NOT operation."""
    line: Optional[int] = None
    column: Optional[int] = None
    operand: Optional[ExprNode] = None
@dataclass(frozen=True, repr=False)
class ArithmeticUnaryOpNode(ArithmeticNode): # Result of an arithmetic unary op is an arithmetic value
    line: Optional[int] = None
    column: Optional[int] = None
    operator: str = "+" # e.g., "+", "-"
    operand: Optional[ArithmeticNode] = None

# --- Quantifier Nodes ---
@dataclass(frozen=True, repr=False)
class QuantifierBlockNode(ASTNode):
    line: Optional[int] = None
    column: Optional[int] = None
    quant_type: str = "forall" # "forall", "exists"
    variables: List[VariableNode] = field(default_factory=list)
    condition: Optional[ExprNode] = None

@dataclass(frozen=True, repr=False)
class ConditionNode(ASTNode):
    """Represents the conditional part of a rule or a quantified expression."""
    line: Optional[int] = None
    column: Optional[int] = None
    expression: Optional[ExprNode] = None
    quant_block: Optional[QuantifierBlockNode] = None

# --- Sentence Level Nodes ---
@dataclass(frozen=True, repr=False)
class FactNode(ASTNode):
    line: Optional[int] = None
    column: Optional[int] = None
    statement: Optional[ExprNode] = None
    """A fact can contain any expression as its statement."""

@dataclass(frozen=True, repr=False)
class RuleNode(ASTNode):
    line: Optional[int] = None
    column: Optional[int] = None
    condition: Optional[ConditionNode] = None
    consequent: Optional[PredicateCallNode] = None

@dataclass(frozen=True, repr=False)
class ParameterNode(ASTNode):
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    param_type: Optional[str] = None

@dataclass(frozen=True, repr=False)
class PredicateDefNode(ASTNode):
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    parameters: List[ParameterNode] = field(default_factory=list)
    is_function: bool = False

@dataclass(frozen=True, repr=False)
class DefinitionNode(ASTNode):
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    parameters: List[ParameterNode] = field(default_factory=list)
    body: Optional[ASTNode] = None
    is_function: bool = False
    return_type: Optional[str] = None

@dataclass(frozen=True, repr=False)
class VariableDeclNode(ASTNode): # New Node
    """Represents a variable declaration, e.g., 'let x: integer = 5'."""
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    var_type: str = "auto" # The declared type, e.g., 'integer', 'auto'
    value: Optional[ExprNode] = None # The initialization expression, if any

@dataclass(frozen=True, repr=False)
class AssignmentNode(ASTNode): # Added from previous context, ensure it's here
    line: Optional[int] = None
    column: Optional[int] = None
    target: Optional[VariableNode] = None
    expression: Optional[ExprNode] = None

@dataclass(frozen=True, repr=False)
class SentenceNode(ASTNode):
    # content: Union[FactNode, RuleNode, DefinitionNode, VariableDeclNode, AssignmentNode]
    # Making content a list to support multiple statements in a sentence, common in semantic tests
    line: Optional[int] = None
    column: Optional[int] = None
    content: List[Union[ASTNode, ExprNode]] = field(default_factory=list)


# --- Enhanced Mathematical Nodes (for Tau Language integration) ---

@dataclass(frozen=True, repr=False)
class FunctionDefinitionNode(ASTNode):
    """Represents a function definition with mathematical semantics."""
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    parameters: List[ParameterNode] = None
    body: Optional[ExprNode] = None
    is_recurrence: bool = False
    recurrence_index: Optional[str] = None  # For recurrence relations like f[n]

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []

@dataclass(frozen=True, repr=False)
class PredicateDefinitionNode(ASTNode):
    """Represents a predicate definition with logical semantics."""
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    parameters: List[ParameterNode] = None
    body: Optional[ExprNode] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []

@dataclass(frozen=True, repr=False)
class RecurrenceDefinitionNode(ASTNode):
    """Represents a recurrence relation definition."""
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    base_cases: List['RecurrenceCaseNode'] = None
    recursive_cases: List['RecurrenceCaseNode'] = None

    def __post_init__(self):
        if self.base_cases is None:
            self.base_cases = []
        if self.recursive_cases is None:
            self.recursive_cases = []

@dataclass(frozen=True, repr=False)
class RecurrenceCaseNode(ASTNode):
    """Represents a single case in a recurrence relation."""
    line: Optional[int] = None
    column: Optional[int] = None
    index: Union[int, str] = 0  # 0, 1, 2, ... or "n"
    parameters: List[ParameterNode] = None
    body: Optional[ExprNode] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []

@dataclass(frozen=True, repr=False)
class BitvectorDeclarationNode(ASTNode):
    """Represents a bitvector declaration."""
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    width: int = 32

@dataclass(frozen=True, repr=False)
class BitvectorOperationNode(ExprNode):
    """Represents bitvector operations."""
    line: Optional[int] = None
    column: Optional[int] = None
    left: Optional[ExprNode] = None
    operator: str = "and"  # "and", "or", "xor", "shift_left", "shift_right", "concatenated_with"
    right: Optional[ExprNode] = None

@dataclass(frozen=True, repr=False)
class BitvectorLiteralNode(AtomNode):
    """Represents bitvector literals (0xFF, 0b1010)."""
    line: Optional[int] = None
    column: Optional[int] = None
    value: str = "0"
    format: str = "decimal"  # "hex", "binary", "decimal"

@dataclass(frozen=True, repr=False)
class SolverCommandNode(ASTNode):
    """Represents solver commands."""
    line: Optional[int] = None
    column: Optional[int] = None
    command_type: str = "sat"  # "satisfiability", "solve", "normalize", "qelim"
    expression: Optional[ExprNode] = None
    variables: Optional[List[str]] = None

@dataclass(frozen=True, repr=False)
class MathematicalAssertionNode(ASTNode):
    """Represents mathematical assertions."""
    line: Optional[int] = None
    column: Optional[int] = None
    assertion_type: str = "assert"  # "assert", "constraint"
    expression: Optional[ExprNode] = None

@dataclass(frozen=True, repr=False)
class TypeAssertionNode(ExprNode):
    """Represents a type assertion, e.g., 'x : integer'."""
    variable: Optional[VariableNode] = None
    type_name: str = ""
    line: Optional[int] = None
    column: Optional[int] = None

@dataclass(frozen=True, repr=False)
class TemporalQuantifierNode(ExprNode):
    """Represents temporal quantifiers (always, sometimes, eventually, never)."""
    line: Optional[int] = None
    column: Optional[int] = None
    quantifier: str = "always"  # "always", "sometimes", "eventually", "never"
    expression: Optional[ExprNode] = None

@dataclass(frozen=True, repr=False)
class ConceptDeclarationNode(ASTNode):
    """Represents concept declarations."""
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    description: Optional[str] = None

@dataclass(frozen=True, repr=False)
class StreamDeclarationNode(ASTNode):
    """Represents stream declarations."""
    line: Optional[int] = None
    column: Optional[int] = None
    identifier: str = ""
    version: Optional[str] = None

@dataclass(frozen=True, repr=False)
class MetaStatementNode(ASTNode):
    """Represents meta statements with metadata."""
    line: Optional[int] = None
    column: Optional[int] = None
    fields: List['MetaFieldNode'] = field(default_factory=list)

@dataclass(frozen=True, repr=False)
class MetaFieldNode(ASTNode):
    """Represents a single meta field."""
    line: Optional[int] = None
    column: Optional[int] = None
    key: str = ""
    value: Union[str, List[str]] = ""

@dataclass(frozen=True, repr=False)
class EnhancedArithmeticNode(ArithmeticNode):
    """Enhanced arithmetic operations including power, root, modulo."""
    line: Optional[int] = None
    column: Optional[int] = None
    left: Optional[ArithmeticNode] = None
    operator: str = "plus"  # "plus", "minus", "times", "divided_by", "modulo", "power", "root"
    right: Optional[ArithmeticNode] = None

@dataclass(frozen=True, repr=False)
class SetOperationNode(ExprNode):
    """Represents set operations (intersection, union, complement)."""
    line: Optional[int] = None
    column: Optional[int] = None
    left: Optional[ExprNode] = None
    operator: str = "intersected_with"  # "intersected_with", "united_with", "complemented_by"
    right: Optional[ExprNode] = None  # None for unary operations like complement

@dataclass(frozen=True, repr=False)
class QuantifiedExpressionNode(ExprNode):
    """Represents quantified expressions (for all, there exists)."""
    line: Optional[int] = None
    column: Optional[int] = None
    quantifier: str = "for_all"  # "for_all", "there_exists"
    variables: List[VariableNode] = field(default_factory=list)
    expression: Optional[ExprNode] = None

@dataclass(frozen=True, repr=False)
class ConditionalExpressionNode(ExprNode):
    """Represents conditional expressions (if-then, when-then)."""
    line: Optional[int] = None
    column: Optional[int] = None
    condition: Optional[ExprNode] = None
    consequent: Optional[ExprNode] = None
    conditional_type: str = "if_then"  # "if_then", "when_then", "implies"


@dataclass(frozen=True, repr=False)
class TernaryOpNode(ExprNode):
    """Represents a ternary expression (if C then A else B)."""
    line: Optional[int] = None
    column: Optional[int] = None
    condition: Optional[ExprNode] = None
    value_if_true: Optional[ExprNode] = None
    value_if_false: Optional[ExprNode] = None

@dataclass(frozen=True, repr=False)
class FunctionCallWithIndexNode(ExprNode):
    """Represents function calls with index (for recurrence relations)."""
    line: Optional[int] = None
    column: Optional[int] = None
    name: str = ""
    index: Optional[ExprNode] = None  # Can be "n-1", "n+1", etc.
    arguments: List[ExprNode] = field(default_factory=list)

# Note: Consider a more unified ExpressionNode or ValueNode structure in future refactoring


# AST nodes are ready for use
