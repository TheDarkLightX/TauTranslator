"""
Expression builder classes for Lark transformer.
Follows the Builder pattern to extract complex expression building logic.
"""

from typing import List, Union, Optional
from lark import Token, Tree
import logging

from .ast_nodes import (
    ASTNode, LiteralNode, BinaryExpressionNode, 
    UnaryExpressionNode, SourceLocation
)


class ExpressionBuilder:
    """Base builder for expressions."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)


class UnaryExpressionBuilder(ExpressionBuilder):
    """Builds unary expressions from tokens and operands."""
    
    def build(self, operator_token: Token, operand: ASTNode) -> Union[ASTNode, UnaryExpressionNode]:
        """
        Build a unary expression node.
        
        Args:
            operator_token: The operator token (PLUS or MINUS)
            operand: The operand AST node
            
        Returns:
            For PLUS: returns operand directly (no-op)
            For MINUS: returns UnaryExpressionNode
        """
        if operator_token.type == 'PLUS':
            # Unary PLUS is a no-op
            return operand
        elif operator_token.type == 'MINUS':
            return UnaryExpressionNode(
                operator=operator_token.value,
                operand=operand,
                location=self._get_location(operator_token)
            )
        else:
            raise ValueError(f"Unsupported unary operator: {operator_token.type}")
    
    def _get_location(self, token: Token) -> SourceLocation:
        """Extract location from token."""
        return SourceLocation(
            line=token.line,
            column=token.column,
            end_line=token.end_line if token.end_line is not None else token.line,
            end_column=token.end_column if token.end_column is not None else token.column + len(token.value),
            absolute_char_start_index=token.start_pos,
            absolute_char_end_index=token.end_pos
        )


class BinaryExpressionBuilder(ExpressionBuilder):
    """Builds binary expressions from left-associative operations."""
    
    def build_from_children(self, children: List[Union[Token, ASTNode]], 
                           valid_operators: set) -> ASTNode:
        """
        Build a binary expression tree from a list of children.
        
        Args:
            children: List of alternating operands and operators
            valid_operators: Set of valid operator types (e.g., {'PLUS', 'MINUS'})
            
        Returns:
            ASTNode representing the expression tree
        """
        if not children:
            raise ValueError("No children provided to build expression")
        
        # Start with the first operand
        result = children[0]
        if not isinstance(result, ASTNode):
            raise ValueError(f"Expected ASTNode as first operand, got {type(result)}")
        
        # If only one child, return it as-is
        if len(children) == 1:
            return result
        
        # Process operator-operand pairs
        i = 1
        while i < len(children):
            if i >= len(children):
                break
                
            # Get operator
            operator_token = children[i]
            if not isinstance(operator_token, Token) or operator_token.type not in valid_operators:
                raise ValueError(
                    f"Expected operator token in {valid_operators}, "
                    f"got {operator_token.type if isinstance(operator_token, Token) else type(operator_token)}"
                )
            
            # Check for right operand
            if i + 1 >= len(children):
                raise ValueError(f"Missing right operand for operator {operator_token.value}")
            
            # Get right operand
            right_operand = children[i + 1]
            if not isinstance(right_operand, ASTNode):
                raise ValueError(f"Expected ASTNode as right operand, got {type(right_operand)}")
            
            # Build binary expression
            result = BinaryExpressionNode(
                left=result,
                operator=operator_token.value,
                right=right_operand
            )
            
            i += 2
        
        return result


class FactorBuilder(ExpressionBuilder):
    """Handles factor rule transformations."""
    
    def __init__(self, unary_builder: UnaryExpressionBuilder, 
                 logger: Optional[logging.Logger] = None):
        super().__init__(logger)
        self.unary_builder = unary_builder
    
    def build(self, children: List[Union[Token, ASTNode]]) -> ASTNode:
        """
        Build a factor from children.
        
        Handles:
        - Unary operations (PLUS/MINUS factor)
        - Parenthesized expressions (LPAR expr RPAR)
        - Single ASTNode pass-through
        """
        if not children:
            raise ValueError("Factor method received no children")
        
        # Case 1: Unary operation
        if (len(children) == 2 and 
            isinstance(children[0], Token) and 
            children[0].type in ['MINUS', 'PLUS'] and 
            isinstance(children[1], ASTNode)):
            
            return self.unary_builder.build(children[0], children[1])
        
        # Case 2: Parenthesized expression
        if (len(children) == 3 and 
            isinstance(children[0], Token) and children[0].type == 'LPAR' and
            isinstance(children[1], ASTNode) and
            isinstance(children[2], Token) and children[2].type == 'RPAR'):
            
            # Return the inner expression
            return children[1]
        
        # Case 3: Single ASTNode
        if len(children) == 1 and isinstance(children[0], ASTNode):
            return children[0]
        
        # Unexpected structure
        type_details = [
            f"Child {i}: {type(c)} Value: {getattr(c, 'value', 'N/A')} "
            f"TypeAttr: {getattr(c, 'type', 'N/A')}" 
            for i, c in enumerate(children)
        ]
        self.logger.error(
            f"FACTOR_ERROR: Unexpected structure. Got {len(children)} children. "
            f"Details: {type_details}"
        )
        raise ValueError(
            f"Factor method received unexpected structure: {len(children)} children"
        )


class LocationExtractor:
    """Extracts source location information from various node types."""
    
    @staticmethod
    def extract(item: Union[Token, Tree, ASTNode]) -> Optional[SourceLocation]:
        """Extract location information from a Token, Tree, or ASTNode."""
        if isinstance(item, Token):
            return SourceLocation(
                line=item.line,
                column=item.column,
                end_line=item.end_line if item.end_line is not None else item.line,
                end_column=(item.end_column if item.end_column is not None 
                           else item.column + len(item.value)),
                absolute_char_start_index=item.start_pos,
                absolute_char_end_index=item.end_pos
            )
        
        elif isinstance(item, Tree):
            return LocationExtractor._extract_from_tree(item)
        
        elif isinstance(item, ASTNode):
            return item.location
        
        return None
    
    @staticmethod
    def _extract_from_tree(tree: Tree) -> Optional[SourceLocation]:
        """Extract location from a Tree node."""
        # Try to get from tree's meta first
        if hasattr(tree, 'meta') and not tree.meta.empty:
            return SourceLocation(
                line=tree.meta.line,
                column=tree.meta.column,
                end_line=tree.meta.end_line,
                end_column=tree.meta.end_column,
                absolute_char_start_index=tree.meta.start_pos,
                absolute_char_end_index=tree.meta.end_pos
            )
        
        # If no children, return None
        if not tree.children:
            return None
        
        # Get location from first and last children
        start_loc = LocationExtractor.extract(tree.children[0])
        end_loc = LocationExtractor.extract(tree.children[-1])
        
        if start_loc and end_loc:
            return SourceLocation(
                line=start_loc.line,
                column=start_loc.column,
                end_line=end_loc.end_line,
                end_column=end_loc.end_column,
                absolute_char_start_index=start_loc.absolute_char_start_index,
                absolute_char_end_index=end_loc.absolute_char_end_index
            )
        
        # Return whichever is available
        return start_loc or end_loc