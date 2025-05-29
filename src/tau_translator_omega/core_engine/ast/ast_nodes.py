from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True, eq=True)
class ASTNode:
    """Base class for all AST nodes."""
    pass

@dataclass(frozen=True, eq=True)
class IdentifierNode(ASTNode):
    """Represents an identifier (e.g., variable name, function name, predicate name)."""
    name: str

    def __post_init__(self):
        """Validate the identifier name after initialization."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Identifier name must be a non-empty string.")
        # Future: Add regex validation for valid Tau identifier characters if specified.
        # For example, if identifiers must start with a letter or underscore:
        # import re
        # if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", self.name):
        #     raise ValueError(f"Invalid identifier format: '{self.name}'")

@dataclass(frozen=True, eq=True)
class BooleanLiteralNode(ASTNode):
    """Represents a boolean literal (True or False)."""
    value: bool

    def __post_init__(self):
        """Validate that the value is a boolean."""
        if not isinstance(self.value, bool):
            raise ValueError("BooleanLiteralNode value must be a boolean.")

@dataclass(frozen=True, eq=True)
class NumberLiteralNode(ASTNode):
    """Represents an integer literal."""
    value: int

    def __post_init__(self):
        """Validate that the value is an integer."""
        if type(self.value) is not int:
            raise ValueError("NumberLiteralNode value must be an integer.")

class StreamTypeEnum(Enum):
    """Enumeration for stream types (input/output)."""
    INPUT = "input"
    OUTPUT = "output"

@dataclass(frozen=True, eq=True)
class StreamVariableNode(ASTNode):
    """Represents a stream variable (e.g., i1[t], o2[5])."""
    stream_type: StreamTypeEnum
    stream_id: int
    index_node: ASTNode

    def __post_init__(self):
        """Validate the fields of the StreamVariableNode."""
        if not isinstance(self.stream_type, StreamTypeEnum):
            raise TypeError("stream_type must be an instance of StreamTypeEnum")
        if not isinstance(self.stream_id, int):
            # Using TypeError as per common practice for type checks, though ValueError for content is also seen.
            # The test expects (ValueError, TypeError) and matches the message, so either is fine.
            raise TypeError("stream_id must be an integer")
        if not isinstance(self.index_node, ASTNode):
            raise TypeError("index_node must be an ASTNode instance")


class UnaryOperatorEnum(Enum):
    """Enumeration for unary operators."""
    LOGICAL_NOT = "!"
    BOOLEAN_NEGATION = "'"
    TEMPORAL_ALWAYS = "[]"
    TEMPORAL_SOMETIMES = "<>"

@dataclass(frozen=True, eq=True)
class UnaryOpNode(ASTNode):
    """Represents a unary operation (e.g., !p, q', []r)."""
    operator: UnaryOperatorEnum
    operand: ASTNode

    def __post_init__(self):
        """Validate the fields of the UnaryOpNode."""
        if not isinstance(self.operator, UnaryOperatorEnum):
            raise TypeError("operator must be an instance of UnaryOperatorEnum")
        if not isinstance(self.operand, ASTNode):
            raise TypeError("operand must be an ASTNode instance")


class BinaryOperatorEnum(Enum):
    """Enumeration for binary operators."""
    # Logical operators for 'spec'
    LOGICAL_AND = "&&"
    LOGICAL_OR = "||"
    LOGICAL_XOR = "^"
    IMPLIES = "->"
    IFF = "<->"
    # Comparison operators for 'local_spec'
    EQUAL = "="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    # NOTE: !< is equivalent to >=, and !<= is equivalent to >.
    # We'll represent them by their simpler canonical forms in the AST.
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    # Boolean function operators for 'term'
    BOOLEAN_AND = "&"
    BOOLEAN_OR = "|"
    BOOLEAN_XOR = "+" # Using '+' as the canonical for term XOR, as '^' is used for logical XOR.

@dataclass(frozen=True, eq=True)
class BinaryOpNode(ASTNode):
    """Represents a binary operation (e.g., p && q, r = 10)."""
    operator: BinaryOperatorEnum
    left_operand: ASTNode
    right_operand: ASTNode

    def __post_init__(self):
        """Validate the fields of the BinaryOpNode."""
        if not isinstance(self.operator, BinaryOperatorEnum):
            raise TypeError("operator must be an instance of BinaryOperatorEnum")
        if not isinstance(self.left_operand, ASTNode):
            raise TypeError("left_operand must be an ASTNode instance")
        if not isinstance(self.right_operand, ASTNode):
            raise TypeError("right_operand must be an ASTNode instance")
