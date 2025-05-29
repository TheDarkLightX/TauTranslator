"""
EBNF Parser Module

High-performance EBNF (Extended Backus-Naur Form) parser for grammar processing.
Part of Phase 1.1 of the TauTranslatorOmega development roadmap.

This module provides:
- EBNF grammar parsing into AST
- Grammar validation and error handling
- Support for standard EBNF constructs
- Integration with LLM control libraries (transformers-CFG, Guidance)
"""

from .ebnf_parser import EBNFParser, create_ebnf_parser
from .ebnf_ast_nodes import (
    EBNFNode, GrammarNode, RuleNode, ChoiceNode, SequenceNode,
    TerminalNode, NonTerminalNode, OptionalNode, RepetitionNode,
    GroupNode, LiteralNode, RegexNode
)

__all__ = [
    'EBNFParser',
    'create_ebnf_parser',
    'EBNFNode',
    'GrammarNode', 
    'RuleNode',
    'ChoiceNode',
    'SequenceNode',
    'TerminalNode',
    'NonTerminalNode',
    'OptionalNode',
    'RepetitionNode',
    'GroupNode',
    'LiteralNode',
    'RegexNode'
]
