"""
Domain types for the Enhanced TCE Parser following IDP.
Pure types with no I/O dependencies.

Copyright: DarkLightX / Dana Edwards
"""

from typing import NewType, Union, List, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum, auto


# Domain-specific types instead of primitives (IDP Rule 3)
SentenceText = NewType('SentenceText', str)
VariableName = NewType('VariableName', str)
PredicateName = NewType('PredicateName', str)
EntityType = NewType('EntityType', str)
TimeIndex = NewType('TimeIndex', str)
TauNotation = NewType('TauNotation', str)


class QuantifierType(Enum):
    """Enumeration of logical quantifiers."""
    UNIVERSAL = "all"
    EXISTENTIAL = "exists"
    NO = "no"
    SOME = "some"
    

class TemporalOperator(Enum):
    """Enumeration of temporal operators."""
    ALWAYS = "always"
    EVENTUALLY = "eventually"
    NEVER = "never"
    SOMETIMES = "sometimes"


class LogicalOperator(Enum):
    """Enumeration of logical operators."""
    AND = "and"
    OR = "or"
    NOT = "not"
    IMPLIES = "implies"
    IFF = "iff"


class ComparisonOperator(Enum):
    """Enumeration of comparison operators."""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="


@dataclass(frozen=True)
class TimeExpression:
    """Represents a time expression like t, t+1, t-1."""
    base: TimeIndex
    offset: Optional[int] = None
    
    def to_notation(self) -> str:
        """Convert to formal notation [t], [t+1], etc."""
        if self.offset is None:
            return f"[{self.base}]"
        elif self.offset > 0:
            return f"[{self.base}+{self.offset}]"
        else:
            return f"[{self.base}{self.offset}]"


@dataclass(frozen=True)
class StreamReference:
    """Represents a stream reference like i1[t] or o2[t-1]."""
    stream_type: str  # "input" or "output"
    stream_number: int
    time: TimeExpression
    
    def to_notation(self) -> str:
        """Convert to compact notation i1[t], o2[t], etc."""
        prefix = "i" if self.stream_type == "input" else "o"
        return f"{prefix}{self.stream_number}{self.time.to_notation()}"


@dataclass
class EntityInfo:
    """Information about an entity in the parse context."""
    variable: VariableName
    entity_type: EntityType
    properties: List[PredicateName] = field(default_factory=list)
    quantifier: Optional[QuantifierType] = None


@dataclass
class ParseContext:
    """Context maintained during parsing."""
    entities: Dict[VariableName, EntityInfo] = field(default_factory=dict)
    coreferences: Dict[str, VariableName] = field(default_factory=dict)
    scopes: List[str] = field(default_factory=list)
    
    def add_entity(self, var: VariableName, entity_type: EntityType, 
                  quantifier: Optional[QuantifierType] = None) -> None:
        """Register a new entity in the context."""
        self.entities[var] = EntityInfo(var, entity_type, quantifier=quantifier)
    
    def add_coreference(self, reference: str, variable: VariableName) -> None:
        """Add a coreference mapping."""
        self.coreferences[reference] = variable
    
    def resolve_reference(self, reference: str) -> Optional[VariableName]:
        """Resolve a reference to its variable."""
        return self.coreferences.get(reference)


# Result types using discriminated unions (IDP Rule 3)
@dataclass
class ParseSuccess:
    """Successful parse result."""
    status: str = field(default="SUCCESS", init=False)
    tau_notation: TauNotation = TauNotation("")
    semantic_graph: Optional['SemanticGraph'] = None
    warnings: List[str] = field(default_factory=list)
    context: Optional[ParseContext] = None


@dataclass
class ParseFailure:
    """Failed parse result."""
    status: str = field(default="FAILURE", init=False)
    error_type: str = ""
    error_message: str = ""
    partial_result: Optional[TauNotation] = None
    line: Optional[int] = None
    column: Optional[int] = None


ParseResult = Union[ParseSuccess, ParseFailure]


@dataclass
class Token:
    """Represents a token in the parsed sentence."""
    value: str
    token_type: str
    position: int
    
    
@dataclass
class MathExpression:
    """Represents a parsed mathematical expression."""
    expression: str
    parsed_form: str
    variables: List[VariableName] = field(default_factory=list)


# Semantic graph types
@dataclass
class SemanticNode:
    """Node in the semantic graph."""
    id: str
    node_type: str
    value: str
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class SemanticEdge:
    """Edge in the semantic graph."""
    source: str
    target: str
    relation: str
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class SemanticGraph:
    """Semantic graph representation of parsed content."""
    nodes: Dict[str, SemanticNode] = field(default_factory=dict)
    edges: List[SemanticEdge] = field(default_factory=list)
    
    def add_node(self, node: SemanticNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: SemanticEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)


# Error types
class ParserError(Exception):
    """Base exception for parser errors."""
    pass


class PronounResolutionError(ParserError):
    """Error in pronoun resolution."""
    pass


class MathematicalParsingError(ParserError):
    """Error in mathematical expression parsing."""
    pass


class TemporalParsingError(ParserError):
    """Error in temporal expression parsing."""
    pass