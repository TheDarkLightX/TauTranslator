"""
EBNF AST node hierarchy and utilities used by unit tests.

Focus: Keep the API minimal yet complete for tests, optimizing for
clarity and low cognitive complexity. All node classes are lightweight
dataclasses with slots for memory efficiency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Any, Iterable
from abc import ABC, abstractmethod


class EBNFNode(ABC):
    """Abstract base for all EBNF AST nodes."""

    __slots__ = ()

    @abstractmethod
    def accept(self, visitor: "EBNFVisitor") -> Any:
        raise NotImplementedError


class ExpressionNode(EBNFNode, ABC):
    """Abstract base for EBNF expressions."""


class TerminalNode(ExpressionNode, ABC):
    """Abstract base for terminal-like expressions (literal/regex)."""


@dataclass(slots=True)
class GrammarNode(EBNFNode):
    rules: List["RuleNode"]

    def __repr__(self) -> str:  # pragma: no cover - representation detail
        return f"GrammarNode(rules={len(self.rules)})"

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_grammar(self)


@dataclass(slots=True)
class RuleNode(EBNFNode):
    name: str
    expression: ExpressionNode

    def __repr__(self) -> str:  # pragma: no cover - representation detail
        return f"RuleNode(name={self.name!r})"

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_rule(self)


@dataclass(slots=True)
class ChoiceNode(ExpressionNode):
    alternatives: List[ExpressionNode]

    def __repr__(self) -> str:  # pragma: no cover
        return f"ChoiceNode(alternatives={len(self.alternatives)})"

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_choice(self)


@dataclass(slots=True)
class SequenceNode(ExpressionNode):
    elements: List[ExpressionNode]

    def __repr__(self) -> str:  # pragma: no cover
        return f"SequenceNode(elements={len(self.elements)})"

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_sequence(self)


@dataclass(slots=True)
class OptionalNode(ExpressionNode):
    expression: ExpressionNode

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_optional(self)


@dataclass(slots=True)
class RepetitionNode(ExpressionNode):
    expression: ExpressionNode
    min_count: int = 0
    max_count: Optional[int] = None

    def __repr__(self) -> str:  # pragma: no cover
        span = (
            f"{self.min_count}-{self.max_count}" if self.max_count is not None else f"{self.min_count}+"
        )
        return f"RepetitionNode({span})"

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_repetition(self)


@dataclass(slots=True)
class GroupNode(ExpressionNode):
    expression: ExpressionNode

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_group(self)


@dataclass(slots=True)
class LiteralNode(TerminalNode):
    value: str
    quote_type: str = '"'

    def __repr__(self) -> str:  # pragma: no cover
        return f"LiteralNode({self.quote_type}{self.value}{self.quote_type})"

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_literal(self)


@dataclass(slots=True)
class RegexNode(TerminalNode):
    pattern: str
    flags: str = ""

    def __repr__(self) -> str:  # pragma: no cover
        return f"RegexNode(/{self.pattern}/{self.flags})"

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_regex(self)


@dataclass(slots=True)
class NonTerminalNode(ExpressionNode):
    name: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"NonTerminalNode({self.name})"

    def accept(self, visitor: "EBNFVisitor") -> Any:
        return visitor.visit_nonterminal(self)


class EBNFVisitor(ABC):
    """Visitor for EBNF nodes."""

    @abstractmethod
    def visit_grammar(self, node: GrammarNode) -> Any: ...

    @abstractmethod
    def visit_rule(self, node: RuleNode) -> Any: ...

    @abstractmethod
    def visit_choice(self, node: ChoiceNode) -> Any: ...

    @abstractmethod
    def visit_sequence(self, node: SequenceNode) -> Any: ...

    @abstractmethod
    def visit_optional(self, node: OptionalNode) -> Any: ...

    @abstractmethod
    def visit_repetition(self, node: RepetitionNode) -> Any: ...

    @abstractmethod
    def visit_group(self, node: GroupNode) -> Any: ...

    @abstractmethod
    def visit_literal(self, node: LiteralNode) -> Any: ...

    @abstractmethod
    def visit_regex(self, node: RegexNode) -> Any: ...

    @abstractmethod
    def visit_nonterminal(self, node: NonTerminalNode) -> Any: ...


def _flatten_choice_items(items: Iterable[ExpressionNode]) -> List[ExpressionNode]:
    flat: List[ExpressionNode] = []
    for item in items:
        if isinstance(item, ChoiceNode):
            flat.extend(_flatten_choice_items(item.alternatives))
        else:
            flat.append(item)
    return flat


def _flatten_sequence_items(items: Iterable[ExpressionNode]) -> List[ExpressionNode]:
    flat: List[ExpressionNode] = []
    for item in items:
        if isinstance(item, SequenceNode):
            flat.extend(_flatten_sequence_items(item.elements))
        else:
            flat.append(item)
    return flat


def create_choice(*alternatives: ExpressionNode) -> ExpressionNode:
    """Utility: normalize alternatives into a flattened ChoiceNode or single element."""
    if len(alternatives) == 1 and not isinstance(alternatives[0], ChoiceNode):
        return alternatives[0]
    return ChoiceNode(alternatives=_flatten_choice_items(list(alternatives)))


def create_sequence(*elements: ExpressionNode) -> ExpressionNode:
    """Utility: normalize elements into a flattened SequenceNode or single element."""
    if len(elements) == 1 and not isinstance(elements[0], SequenceNode):
        return elements[0]
    return SequenceNode(elements=_flatten_sequence_items(list(elements)))


