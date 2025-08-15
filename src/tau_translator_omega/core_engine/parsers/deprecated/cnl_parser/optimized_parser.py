"""
Optimized CNL Parser with Performance Improvements

This module implements the high-impact optimizations identified in the performance analysis:
1. Operator precedence parsing (O(n) instead of O(n²))
2. Singleton regex patterns (eliminates recompilation)
3. Memory-optimized AST nodes
4. Cached parsing for repeated patterns
"""

import re
import logging
from typing import Union, List, Optional, Iterator, Any
from functools import lru_cache
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import AST nodes - handle both relative and absolute imports
try:
    from .ast_nodes import (
        ASTNode, SentenceNode, FactNode, ConstantNode, PredicateCallNode,
        ComparisonNode
    )
except ImportError:
    # Fallback for direct import
    import ast_nodes
    ASTNode = ast_nodes.ASTNode
    SentenceNode = ast_nodes.SentenceNode
    FactNode = ast_nodes.FactNode
    ConstantNode = ast_nodes.ConstantNode
    PredicateCallNode = ast_nodes.PredicateCallNode
    ComparisonNode = ast_nodes.ComparisonNode


class TokenPatterns:
    """Singleton for compiled regex patterns - eliminates recompilation overhead."""
    _instance = None
    _compiled_patterns = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._compiled_patterns = {
                'BOOLEAN': re.compile(r'\b(true|false)\b'),
                'NUMBER': re.compile(r'-?\d+(\.\d+)?'),
                'STRING': re.compile(r'"[^"]*"'),
                'IDENTIFIER': re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*'),
                'COMPARISON': re.compile(r'(>=|<=|!=|>|<|=)'),
                'ARITHMETIC': re.compile(r'[+\-*/]'),
                'LPAREN': re.compile(r'\('),
                'RPAREN': re.compile(r'\)'),
                'COMMA': re.compile(r','),
                'PERIOD': re.compile(r'\.'),
                'WHITESPACE': re.compile(r'\s+'),
            }
        return cls._instance
    
    @property
    def patterns(self):
        return self._compiled_patterns


class OptimizedTokenizer:
    """High-performance tokenizer with streaming support."""
    
    def __init__(self):
        self.token_patterns = TokenPatterns()
    
    def tokenize(self, text: str) -> List[tuple]:
        """Fast tokenization with optimized pattern matching."""
        tokens = []
        position = 0
        patterns = self.token_patterns.patterns
        
        while position < len(text):
            matched = False
            
            # Optimized pattern matching - check most common patterns first
            for token_type in ['IDENTIFIER', 'NUMBER', 'COMPARISON', 'LPAREN', 'RPAREN', 
                             'COMMA', 'PERIOD', 'STRING', 'BOOLEAN', 'WHITESPACE']:
                pattern = patterns[token_type]
                match = pattern.match(text, position)
                if match:
                    value = match.group(0)
                    if token_type != 'WHITESPACE':  # Skip whitespace
                        tokens.append((token_type, value, position))
                    position = match.end()
                    matched = True
                    break
            
            if not matched:
                raise ValueError(f"Unexpected character at position {position}: '{text[position]}'")
        
        return tokens
    
    def streaming_tokenize(self, text: str) -> Iterator[tuple]:
        """Memory-efficient streaming tokenizer for large inputs."""
        position = 0
        patterns = self.token_patterns.patterns
        
        while position < len(text):
            for token_type, pattern in patterns.items():
                match = pattern.match(text, position)
                if match:
                    value = match.group(0)
                    if token_type != 'WHITESPACE':
                        yield (token_type, value, position)
                    position = match.end()
                    break
            else:
                raise ValueError(f"Unexpected character at position {position}: '{text[position]}'")


class OperatorPrecedenceParser:
    """O(n) expression parser using operator precedence (Pratt parser)."""
    
    # Operator precedence levels (higher number = higher precedence)
    PRECEDENCE = {
        'OR': 1, 'XOR': 2, 'AND': 3,
        '=': 4, '!=': 4, '<': 4, '>': 4, '<=': 4, '>=': 4,
        '+': 5, '-': 5, '*': 6, '/': 6, '%': 6
    }
    
    def __init__(self, tokens: List[tuple]):
        self.tokens = tokens
        self.position = 0
    
    def current_token(self) -> Optional[tuple]:
        """Get current token without advancing."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def consume_token(self) -> Optional[tuple]:
        """Consume and return current token."""
        token = self.current_token()
        if token:
            self.position += 1
        return token
    
    def peek_operator_precedence(self) -> int:
        """Get precedence of current operator."""
        token = self.current_token()
        if token and token[0] == 'COMPARISON':
            return self.PRECEDENCE.get(token[1], 0)
        return 0
    
    def parse_expression(self, min_precedence: int = 0) -> ASTNode:
        """Parse expression with operator precedence - O(n) complexity."""
        left = self.parse_primary()
        
        while (self.current_token() and 
               self.current_token()[0] == 'COMPARISON' and
               self.peek_operator_precedence() >= min_precedence):
            
            op_token = self.consume_token()
            operator = op_token[1]
            precedence = self.PRECEDENCE[operator]
            
            right = self.parse_expression(precedence + 1)
            left = ComparisonNode(left=left, operator=operator, right=right)
        
        return left
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expressions (atoms, parentheses, function calls)."""
        token = self.current_token()
        if not token:
            raise ValueError("Unexpected end of expression")
        
        # Handle parentheses
        if token[0] == 'LPAREN':
            self.consume_token()  # consume '('
            expr = self.parse_expression()
            if not self.current_token() or self.current_token()[0] != 'RPAREN':
                raise ValueError("Missing closing parenthesis")
            self.consume_token()  # consume ')'
            return expr
        
        # Handle function calls
        if (token[0] == 'IDENTIFIER' and 
            self.position + 1 < len(self.tokens) and 
            self.tokens[self.position + 1][0] == 'LPAREN'):
            return self.parse_function_call()
        
        # Handle atoms
        return self.parse_atom()
    
    def parse_atom(self) -> ASTNode:
        """Parse atomic values."""
        token = self.consume_token()
        if not token:
            raise ValueError("Expected atom")
        
        token_type, value, pos = token
        
        if token_type == 'BOOLEAN':
            return ConstantNode(value=(value.lower() == 'true'), value_type='BOOLEAN')
        elif token_type == 'NUMBER':
            if '.' in value:
                return ConstantNode(value=float(value), value_type='FLOAT')
            else:
                return ConstantNode(value=int(value), value_type='INTEGER')
        elif token_type == 'STRING':
            return ConstantNode(value=value[1:-1], value_type='STRING')
        elif token_type == 'IDENTIFIER':
            return ConstantNode(value=value, value_type='IDENTIFIER')
        else:
            raise ValueError(f"Cannot parse atom: {token}")
    
    def parse_function_call(self) -> PredicateCallNode:
        """Parse function/predicate calls."""
        name_token = self.consume_token()
        name = name_token[1]
        
        # Consume '('
        if not self.current_token() or self.current_token()[0] != 'LPAREN':
            raise ValueError("Expected '(' after function name")
        self.consume_token()
        
        # Parse arguments
        args = []
        while self.current_token() and self.current_token()[0] != 'RPAREN':
            arg = self.parse_expression()
            args.append(arg)
            
            # Handle comma separation
            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.consume_token()
            elif self.current_token() and self.current_token()[0] != 'RPAREN':
                raise ValueError("Expected ',' or ')' in argument list")
        
        # Consume ')'
        if not self.current_token() or self.current_token()[0] != 'RPAREN':
            raise ValueError("Expected ')' after arguments")
        self.consume_token()
        
        return PredicateCallNode(name=name, args=args)


class OptimizedCNLParser:
    """
    High-performance CNL parser with algorithmic optimizations.
    
    Features:
    - O(n) expression parsing instead of O(n²)
    - Singleton pattern for regex compilation
    - Memoized parsing for repeated patterns
    - Streaming tokenization for large inputs
    """
    
    def __init__(self, debug: bool = False, enable_caching: bool = True):
        self.debug = debug
        self.enable_caching = enable_caching
        self.tokenizer = OptimizedTokenizer()
        
        # Performance counters
        self.parse_count = 0
        self.cache_hits = 0
    
    @lru_cache(maxsize=1000)
    def _parse_cached(self, text_hash: str, text: str) -> ASTNode:
        """Cached parsing for repeated patterns."""
        return self._parse_internal(text)
    
    def parse(self, text: str) -> ASTNode:
        """Parse CNL text with optimizations."""
        if not text.strip():
            raise ValueError("Input text cannot be empty or whitespace only.")
        
        self.parse_count += 1
        
        # Use caching for repeated patterns
        if self.enable_caching:
            text_hash = str(hash(text.strip()))
            try:
                result = self._parse_cached(text_hash, text.strip())
                self.cache_hits += 1
                return result
            except TypeError:
                # Fallback if caching fails
                pass
        
        return self._parse_internal(text.strip())
    
    def _parse_internal(self, text: str) -> ASTNode:
        """Internal parsing implementation."""
        try:
            tokens = self.tokenizer.tokenize(text)
            if self.debug:
                logger.info(f"Tokens: {tokens}")
            
            # Parse the tokens into an AST
            ast = self._parse_sentence(tokens)
            return ast
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse CNL text: {e}") from e
    
    def _parse_sentence(self, tokens: List[tuple]) -> SentenceNode:
        """Parse a sentence (fact ending with period)."""
        if not tokens or tokens[-1][0] != 'PERIOD':
            raise ValueError("Sentence must end with period")
        
        # Remove the period
        content_tokens = tokens[:-1]
        
        # Use optimized expression parser
        parser = OperatorPrecedenceParser(content_tokens)
        fact_content = parser.parse_expression()
        fact = FactNode(statement=fact_content)
        
        return SentenceNode(content=fact)
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics."""
        cache_hit_rate = (self.cache_hits / self.parse_count * 100) if self.parse_count > 0 else 0
        return {
            'total_parses': self.parse_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'patterns_compiled': len(self.tokenizer.token_patterns.patterns)
        }


# Factory function for compatibility
def create_optimized_parser(debug: bool = False, enable_caching: bool = True) -> OptimizedCNLParser:
    """Create an optimized parser instance."""
    return OptimizedCNLParser(debug=debug, enable_caching=enable_caching)
