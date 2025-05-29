"""
EBNF AST Node Definitions

Memory-optimized AST nodes for EBNF grammar representation.
Follows the same optimization patterns as the CNL parser.
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Union
from abc import ABC, abstractmethod


class EBNFNode(ABC):
    """Base class for all EBNF AST nodes with memory optimization."""
    __slots__ = ()
    
    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for traversal."""
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"


@dataclass
class GrammarNode(EBNFNode):
    """Root node representing an entire EBNF grammar."""
    __slots__ = ('rules',)
    
    rules: List['RuleNode']
    
    def accept(self, visitor):
        return visitor.visit_grammar(self)
    
    def __repr__(self):
        return f"GrammarNode(rules={len(self.rules)})"


@dataclass
class RuleNode(EBNFNode):
    """Node representing a single EBNF rule: name = expression."""
    __slots__ = ('name', 'expression')
    
    name: str
    expression: 'ExpressionNode'
    
    def accept(self, visitor):
        return visitor.visit_rule(self)
    
    def __repr__(self):
        return f"RuleNode(name='{self.name}')"


# Expression nodes (right-hand side of rules)
class ExpressionNode(EBNFNode):
    """Base class for expression nodes."""
    __slots__ = ()


@dataclass
class ChoiceNode(ExpressionNode):
    """Node representing choice: A | B | C"""
    __slots__ = ('alternatives',)
    
    alternatives: List[ExpressionNode]
    
    def accept(self, visitor):
        return visitor.visit_choice(self)
    
    def __repr__(self):
        return f"ChoiceNode(alternatives={len(self.alternatives)})"


@dataclass
class SequenceNode(ExpressionNode):
    """Node representing sequence: A B C"""
    __slots__ = ('elements',)
    
    elements: List[ExpressionNode]
    
    def accept(self, visitor):
        return visitor.visit_sequence(self)
    
    def __repr__(self):
        return f"SequenceNode(elements={len(self.elements)})"


@dataclass
class OptionalNode(ExpressionNode):
    """Node representing optional: [A] or A?"""
    __slots__ = ('expression',)
    
    expression: ExpressionNode
    
    def accept(self, visitor):
        return visitor.visit_optional(self)
    
    def __repr__(self):
        return f"OptionalNode({self.expression})"


@dataclass
class RepetitionNode(ExpressionNode):
    """Node representing repetition: {A} or A* or A+"""
    __slots__ = ('expression', 'min_count', 'max_count')
    
    expression: ExpressionNode
    min_count: int = 0  # 0 for *, 1 for +
    max_count: Optional[int] = None  # None for unlimited
    
    def accept(self, visitor):
        return visitor.visit_repetition(self)
    
    def __repr__(self):
        return f"RepetitionNode({self.expression}, {self.min_count}-{self.max_count})"


@dataclass
class GroupNode(ExpressionNode):
    """Node representing grouping: (A B C)"""
    __slots__ = ('expression',)
    
    expression: ExpressionNode
    
    def accept(self, visitor):
        return visitor.visit_group(self)
    
    def __repr__(self):
        return f"GroupNode({self.expression})"


@dataclass
class TerminalNode(ExpressionNode):
    """Base class for terminal nodes (literals, regex)."""
    __slots__ = ()


@dataclass
class LiteralNode(TerminalNode):
    """Node representing string literal: "hello" or 'hello'"""
    __slots__ = ('value', 'quote_type')
    
    value: str
    quote_type: str = '"'  # " or '
    
    def accept(self, visitor):
        return visitor.visit_literal(self)
    
    def __repr__(self):
        return f"LiteralNode({self.quote_type}{self.value}{self.quote_type})"


@dataclass
class RegexNode(TerminalNode):
    """Node representing regex pattern: /pattern/"""
    __slots__ = ('pattern', 'flags')
    
    pattern: str
    flags: str = ''
    
    def accept(self, visitor):
        return visitor.visit_regex(self)
    
    def __repr__(self):
        return f"RegexNode(/{self.pattern}/{self.flags})"


@dataclass
class NonTerminalNode(ExpressionNode):
    """Node representing non-terminal reference: rule_name"""
    __slots__ = ('name',)
    
    name: str
    
    def accept(self, visitor):
        return visitor.visit_nonterminal(self)
    
    def __repr__(self):
        return f"NonTerminalNode('{self.name}')"


# Visitor pattern for AST traversal
class EBNFVisitor(ABC):
    """Abstract visitor for EBNF AST traversal."""
    
    @abstractmethod
    def visit_grammar(self, node: GrammarNode):
        pass
    
    @abstractmethod
    def visit_rule(self, node: RuleNode):
        pass
    
    @abstractmethod
    def visit_choice(self, node: ChoiceNode):
        pass
    
    @abstractmethod
    def visit_sequence(self, node: SequenceNode):
        pass
    
    @abstractmethod
    def visit_optional(self, node: OptionalNode):
        pass
    
    @abstractmethod
    def visit_repetition(self, node: RepetitionNode):
        pass
    
    @abstractmethod
    def visit_group(self, node: GroupNode):
        pass
    
    @abstractmethod
    def visit_literal(self, node: LiteralNode):
        pass
    
    @abstractmethod
    def visit_regex(self, node: RegexNode):
        pass
    
    @abstractmethod
    def visit_nonterminal(self, node: NonTerminalNode):
        pass


# Utility functions for AST manipulation
def create_choice(*alternatives: ExpressionNode) -> ExpressionNode:
    """Create a choice node, flattening nested choices."""
    flattened = []
    for alt in alternatives:
        if isinstance(alt, ChoiceNode):
            flattened.extend(alt.alternatives)
        else:
            flattened.append(alt)

    if len(flattened) == 1:
        return flattened[0]
    return ChoiceNode(alternatives=flattened)


def create_sequence(*elements: ExpressionNode) -> ExpressionNode:
    """Create a sequence node, flattening nested sequences."""
    flattened = []
    for elem in elements:
        if isinstance(elem, SequenceNode):
            flattened.extend(elem.elements)
        else:
            flattened.append(elem)

    if len(flattened) == 1:
        return flattened[0]
    return SequenceNode(elements=flattened)
