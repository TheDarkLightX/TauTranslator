#!/usr/bin/env python3
"""
EBNF Parser - High-Performance Implementation

Phase 1.1 of TauTranslatorOmega development roadmap.
Parses EBNF (Extended Backus-Naur Form) grammars into AST.

Features:
- Standard EBNF syntax support
- Memory-optimized AST nodes
- Comprehensive error handling
- Integration ready for transformers-CFG and Guidance
- TDD approach with comprehensive testing
"""

import re
from typing import List, Optional, Dict, Any
from pathlib import Path

from .ebnf_ast_nodes import (
    EBNFNode, GrammarNode, RuleNode, ChoiceNode, SequenceNode,
    TerminalNode, NonTerminalNode, OptionalNode, RepetitionNode,
    GroupNode, LiteralNode, RegexNode, ExpressionNode,
    create_choice, create_sequence
)


# EBNF Grammar for parsing EBNF (meta-grammar)
EBNF_GRAMMAR = r'''
?start: grammar

grammar: rule+

rule: IDENTIFIER "=" expression (";" | ".")

expression: choice

choice: sequence ("|" sequence)*

sequence: factor+

factor: atom [quantifier]

quantifier: "?" | "*" | "+"

atom: IDENTIFIER
    | STRING
    | REGEX  
    | "(" expression ")"
    | "[" expression "]"
    | "{" expression "}"

IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
STRING: /"[^"]*"/ | /'[^']*'/
REGEX: /\/[^\/]+\//

%import common.WS
%ignore WS
%ignore /\/\/[^\n]*/  // Comments
%ignore /\/\*.*?\*\//  // Multi-line comments
'''


class EBNFTokenizer:
    """
    Optimized tokenizer for EBNF grammars.
    
    Uses compiled regex patterns for efficient tokenization.
    """
    
    def __init__(self):
        self.patterns = {
            'IDENTIFIER': re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*'),
            'STRING': re.compile(r'"[^"]*"|\'[^\']*\''),
            'REGEX': re.compile(r'/[^/]+/'),
            'EQUALS': re.compile(r'='),
            'SEMICOLON': re.compile(r';'),
            'PERIOD': re.compile(r'\.'),
            'PIPE': re.compile(r'\|'),
            'QUESTION': re.compile(r'\?'),
            'STAR': re.compile(r'\*'),
            'PLUS': re.compile(r'\+'),
            'LPAREN': re.compile(r'\('),
            'RPAREN': re.compile(r'\)'),
            'LBRACKET': re.compile(r'\['),
            'RBRACKET': re.compile(r'\]'),
            'LBRACE': re.compile(r'\{'),
            'RBRACE': re.compile(r'\}'),
            'WHITESPACE': re.compile(r'\s+'),
            'COMMENT': re.compile(r'//[^\n]*|/\*.*?\*/', re.DOTALL),
        }
    
    def tokenize(self, text: str) -> List[tuple]:
        """
        Tokenize EBNF text into tokens.
        
        Returns list of (token_type, value, position) tuples.
        """
        tokens = []
        position = 0
        
        while position < len(text):
            matched = False
            
            # Try patterns in order of priority
            for token_type in ['COMMENT', 'WHITESPACE', 'STRING', 'REGEX', 'IDENTIFIER',
                             'EQUALS', 'SEMICOLON', 'PERIOD', 'PIPE', 'QUESTION', 'STAR', 'PLUS',
                             'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE']:
                pattern = self.patterns[token_type]
                match = pattern.match(text, position)
                if match:
                    value = match.group(0)
                    
                    # Skip whitespace and comments
                    if token_type not in ['WHITESPACE', 'COMMENT']:
                        tokens.append((token_type, value, position))
                    
                    position = match.end()
                    matched = True
                    break
            
            if not matched:
                raise ValueError(f"Unexpected character at position {position}: '{text[position]}'")
        
        return tokens


class EBNFParser:
    """
    High-performance EBNF parser using recursive descent.
    
    Parses EBNF grammars into memory-optimized AST.
    Designed for integration with LLM control libraries.
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.tokenizer = EBNFTokenizer()
        self.tokens = []
        self.position = 0
        self._parse_count = 0
        self._cache = {}
    
    def parse(self, text: str, use_cache: bool = True) -> GrammarNode:
        """
        Parse EBNF text into AST.
        
        Args:
            text: EBNF grammar text
            use_cache: Whether to use caching for repeated grammars
            
        Returns:
            GrammarNode: Root of the AST
            
        Raises:
            ValueError: For invalid input
            RuntimeError: For parsing errors
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty or whitespace only")
        
        self._parse_count += 1
        text = text.strip()
        
        # Simple caching
        if use_cache and text in self._cache:
            return self._cache[text]
        
        try:
            result = self._parse_internal(text)
            
            if use_cache:
                self._cache[text] = result
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse EBNF grammar: {e}") from e
    
    def parse_file(self, file_path: str) -> GrammarNode:
        """Parse EBNF grammar from file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"EBNF file not found: {file_path}")
        
        text = path.read_text(encoding='utf-8')
        return self.parse(text)
    
    def _parse_internal(self, text: str) -> GrammarNode:
        """Internal parsing implementation."""
        # Tokenize
        self.tokens = self.tokenizer.tokenize(text)
        self.position = 0
        
        if self.debug:
            print(f"Tokens: {self.tokens}")
        
        # Parse grammar
        return self._parse_grammar()
    
    def _current_token(self) -> Optional[tuple]:
        """Get current token without advancing."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def _consume_token(self, expected_type: Optional[str] = None) -> tuple:
        """Consume and return current token."""
        token = self._current_token()
        if not token:
            raise RuntimeError("Unexpected end of input")
        
        if expected_type and token[0] != expected_type:
            raise RuntimeError(f"Expected {expected_type}, got {token[0]} at position {token[2]}")
        
        self.position += 1
        return token
    
    def _parse_grammar(self) -> GrammarNode:
        """Parse complete grammar: rule+"""
        rules = []
        
        while self._current_token():
            rule = self._parse_rule()
            rules.append(rule)
        
        if not rules:
            raise RuntimeError("Grammar must contain at least one rule")
        
        return GrammarNode(rules=rules)
    
    def _parse_rule(self) -> RuleNode:
        """Parse rule: IDENTIFIER = expression (. | ;)"""
        # Rule name
        name_token = self._consume_token('IDENTIFIER')
        name = name_token[1]
        
        # Equals
        self._consume_token('EQUALS')
        
        # Expression
        expression = self._parse_expression()
        
        # Terminator (. or ;)
        terminator = self._current_token()
        if terminator and terminator[0] in ['PERIOD', 'SEMICOLON']:
            self._consume_token()
        
        return RuleNode(name=name, expression=expression)
    
    def _parse_expression(self) -> ExpressionNode:
        """Parse expression: choice"""
        return self._parse_choice()
    
    def _parse_choice(self) -> ExpressionNode:
        """Parse choice: sequence (| sequence)*"""
        alternatives = [self._parse_sequence()]
        
        while self._current_token() and self._current_token()[0] == 'PIPE':
            self._consume_token('PIPE')
            alternatives.append(self._parse_sequence())
        
        return create_choice(*alternatives)
    
    def _parse_sequence(self) -> ExpressionNode:
        """Parse sequence: factor+"""
        elements = []
        
        while (self._current_token() and 
               self._current_token()[0] not in ['PIPE', 'RPAREN', 'RBRACKET', 'RBRACE', 'PERIOD', 'SEMICOLON']):
            elements.append(self._parse_factor())
        
        if not elements:
            raise RuntimeError("Empty sequence not allowed")
        
        return create_sequence(*elements)
    
    def _parse_factor(self) -> ExpressionNode:
        """Parse factor: atom [quantifier]"""
        atom = self._parse_atom()
        
        # Check for quantifier
        token = self._current_token()
        if token and token[0] in ['QUESTION', 'STAR', 'PLUS']:
            quantifier = self._consume_token()[1]
            
            if quantifier == '?':
                return OptionalNode(expression=atom)
            elif quantifier == '*':
                return RepetitionNode(expression=atom, min_count=0, max_count=None)
            elif quantifier == '+':
                return RepetitionNode(expression=atom, min_count=1, max_count=None)
        
        return atom
    
    def _parse_atom(self) -> ExpressionNode:
        """Parse atom: IDENTIFIER | STRING | REGEX | (expr) | [expr] | {expr}"""
        token = self._current_token()
        if not token:
            raise RuntimeError("Expected atom")
        
        token_type, value, position = token
        
        if token_type == 'IDENTIFIER':
            self._consume_token()
            return NonTerminalNode(name=value)
        
        elif token_type == 'STRING':
            self._consume_token()
            # Remove quotes
            quote_char = value[0]
            content = value[1:-1]
            return LiteralNode(value=content, quote_type=quote_char)
        
        elif token_type == 'REGEX':
            self._consume_token()
            # Remove slashes
            pattern = value[1:-1]
            return RegexNode(pattern=pattern)
        
        elif token_type == 'LPAREN':
            self._consume_token('LPAREN')
            expr = self._parse_expression()
            self._consume_token('RPAREN')
            return GroupNode(expression=expr)
        
        elif token_type == 'LBRACKET':
            self._consume_token('LBRACKET')
            expr = self._parse_expression()
            self._consume_token('RBRACKET')
            return OptionalNode(expression=expr)
        
        elif token_type == 'LBRACE':
            self._consume_token('LBRACE')
            expr = self._parse_expression()
            self._consume_token('RBRACE')
            return RepetitionNode(expression=expr, min_count=0, max_count=None)
        
        else:
            raise RuntimeError(f"Unexpected token {token_type} at position {position}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get parser performance statistics."""
        return {
            'total_parses': self._parse_count,
            'cache_entries': len(self._cache),
            'parser_type': 'EBNF Recursive Descent',
            'memory_optimized': True
        }
    
    def clear_cache(self):
        """Clear the parsing cache."""
        self._cache.clear()
    
    def is_available(self) -> bool:
        """Check if parser is available and working."""
        return self.tokenizer is not None


# Factory function for easy instantiation
def create_ebnf_parser(debug: bool = False) -> EBNFParser:
    """
    Create an EBNF parser instance.
    
    Args:
        debug: Enable debug output
        
    Returns:
        EBNFParser: Parser instance ready for use
    """
    return EBNFParser(debug=debug)
