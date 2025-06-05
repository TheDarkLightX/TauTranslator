"""
Mock CNL Parser for testing when Lark is not available.

This provides a simplified parser implementation that can handle basic CNL constructs
without relying on Lark, allowing us to test the AST generation and transformer logic.
"""

import re
import logging
from typing import Union, List, Optional

logger = logging.getLogger(__name__)
# Import AST nodes - handle both relative and absolute imports
try:
    from .ast_nodes import (
        ASTNode, SentenceNode, FactNode, ConstantNode, PredicateCallNode,
        VariableNode, ComparisonNode, ArithmeticBinaryOpNode, BooleanBinaryOpNode
    )
except ImportError:
    # Fallback for direct import
    import ast_nodes
    ASTNode = ast_nodes.ASTNode
    SentenceNode = ast_nodes.SentenceNode
    FactNode = ast_nodes.FactNode
    ConstantNode = ast_nodes.ConstantNode
    PredicateCallNode = ast_nodes.PredicateCallNode
    VariableNode = ast_nodes.VariableNode
    ComparisonNode = ast_nodes.ComparisonNode
    ArithmeticBinaryOpNode = ast_nodes.ArithmeticBinaryOpNode
    BooleanBinaryOpNode = ast_nodes.BooleanBinaryOpNode


class MockCNLParser:
    """
    Mock parser that handles basic CNL constructs for testing purposes.
    
    This is a simplified implementation that can parse:
    - Boolean constants: true, false
    - Numeric constants: 42, 3.14
    - String constants: "hello"
    - Simple predicates: is_hot(sun)
    - Basic comparisons: temperature > 30
    - Simple facts ending with period
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        
        # Basic token patterns
        self.patterns = {
            'BOOLEAN': r'\b(true|false)\b',
            'NUMBER': r'-?\d+(\.\d+)?',
            'STRING': r'"[^"]*"',
            'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',
            'COMPARISON': r'(>=|<=|!=|>|<|=)',
            'LPAREN': r'\(',
            'RPAREN': r'\)',
            'COMMA': r',',
            'PERIOD': r'\.',
            'WHITESPACE': r'\s+',
        }
        
        # Compile patterns
        self.compiled_patterns = {
            name: re.compile(pattern) 
            for name, pattern in self.patterns.items()
        }
    
    def tokenize(self, text: str) -> List[tuple]:
        """Simple tokenizer that returns (token_type, value, position) tuples."""
        tokens = []
        position = 0
        
        while position < len(text):
            matched = False
            
            for token_type, pattern in self.compiled_patterns.items():
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
    
    def parse(self, text: str) -> ASTNode:
        """Parse CNL text and return AST."""
        if not text.strip():
            raise ValueError("Input text cannot be empty or whitespace only.")
        
        try:
            tokens = self.tokenize(text.strip())
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
        
        # Parse the content as a fact
        fact_content = self._parse_expression(content_tokens)
        fact = FactNode(statement=fact_content)
        
        return SentenceNode(content=fact)
    
    def _parse_expression(self, tokens: List[tuple]) -> ASTNode:
        """Parse an expression (recursive descent)."""
        if not tokens:
            raise ValueError("Empty expression")
        
        # Handle simple cases first
        if len(tokens) == 1:
            return self._parse_atom(tokens[0])
        
        # Look for comparison operators
        for i, (token_type, value, pos) in enumerate(tokens):
            if token_type == 'COMPARISON':
                left_tokens = tokens[:i]
                right_tokens = tokens[i+1:]
                
                left = self._parse_expression(left_tokens)
                right = self._parse_expression(right_tokens)
                
                return ComparisonNode(left=left, operator=value, right=right)
        
        # Look for function calls (identifier followed by parentheses)
        if (len(tokens) >= 3 and 
            tokens[0][0] == 'IDENTIFIER' and 
            tokens[1][0] == 'LPAREN' and 
            tokens[-1][0] == 'RPAREN'):
            
            return self._parse_predicate_call(tokens)
        
        # If no special structure found, try to parse as single atom
        if len(tokens) == 1:
            return self._parse_atom(tokens[0])
        
        raise ValueError(f"Cannot parse expression: {tokens}")
    
    def _parse_atom(self, token: tuple) -> ASTNode:
        """Parse a single atomic value."""
        token_type, value, pos = token
        
        if token_type == 'BOOLEAN':
            return ConstantNode(value=(value.lower() == 'true'), value_type='BOOLEAN')
        elif token_type == 'NUMBER':
            if '.' in value:
                return ConstantNode(value=float(value), value_type='FLOAT')
            else:
                return ConstantNode(value=int(value), value_type='INTEGER')
        elif token_type == 'STRING':
            # Remove quotes
            return ConstantNode(value=value[1:-1], value_type='STRING')
        elif token_type == 'IDENTIFIER':
            return ConstantNode(value=value, value_type='IDENTIFIER')
        else:
            raise ValueError(f"Cannot parse atom: {token}")
    
    def _parse_predicate_call(self, tokens: List[tuple]) -> PredicateCallNode:
        """Parse a predicate call like 'is_hot(sun)'."""
        name = tokens[0][1]  # Get the identifier value
        
        # Find arguments between parentheses
        if tokens[1][0] != 'LPAREN' or tokens[-1][0] != 'RPAREN':
            raise ValueError("Invalid predicate call syntax")
        
        arg_tokens = tokens[2:-1]  # Tokens between parentheses
        
        # Parse arguments (simple case: comma-separated atoms)
        args = []
        if arg_tokens:
            # Split by commas
            current_arg = []
            for token in arg_tokens:
                if token[0] == 'COMMA':
                    if current_arg:
                        args.append(self._parse_expression(current_arg))
                        current_arg = []
                else:
                    current_arg.append(token)
            
            # Add the last argument
            if current_arg:
                args.append(self._parse_expression(current_arg))
        
        return PredicateCallNode(name=name, args=args)


# Factory function for compatibility
def create_mock_parser(debug: bool = False) -> MockCNLParser:
    """Create a mock parser instance."""
    return MockCNLParser(debug=debug)
