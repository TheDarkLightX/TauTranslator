# src/tau_translator_omega/core_engine/lark_transformer.py
"""
Provides the CST to AST transformer for Lark-generated parse trees.
"""

from lark import Transformer, v_args, Token, Tree
import logging
from typing import Union, Optional

# Use absolute imports for ASTNode and other node types
from .ast_nodes import ASTNode, LiteralNode, BinaryExpressionNode, UnaryExpressionNode, SourceLocation
from .expression_builders import (
    UnaryExpressionBuilder, BinaryExpressionBuilder, 
    FactorBuilder, LocationExtractor
)


class SimpleMathTransformer(Transformer):
    """
    Transforms a CST from the simple_math.lark grammar into our custom AST nodes.
    
    This transformer uses builder classes to handle complex expression construction,
    following the Single Responsibility Principle.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # Initialize builders
        self.unary_builder = UnaryExpressionBuilder(self.logger)
        self.binary_builder = BinaryExpressionBuilder(self.logger)
        self.factor_builder = FactorBuilder(self.unary_builder, self.logger)
        self.location_extractor = LocationExtractor()
        
        logging.error("SimpleMathTransformer: Initialized")

    @v_args(inline=True)
    def NUMBER(self, token):
        """Transform NUMBER token to LiteralNode."""
        return LiteralNode(
            value=int(token.value), 
            location=self.location_extractor.extract(token)
        )

    @v_args(inline=False)
    def factor_from_paren(self, children):
        """
        Handles the 'LPAR expr RPAR' production.
        
        Args:
            children: [Token('LPAR'), transformed_expr_node, Token('RPAR')]
            
        Returns:
            The transformed expression node
        """
        logging.error(f"DEBUG: factor_from_paren received children: {children}, types: {[type(c) for c in children]}")
        
        if not children or len(children) != 3:
            logging.error(f"FACTOR_FROM_PAREN_ERROR: Unexpected children structure: {children}")
            raise ValueError(
                f"factor_from_paren expected 3 children (LPAR, expr, RPAR), "
                f"got {len(children)}: {children}"
            )
        
        lpar_token, expr_node, rpar_token = children
        
        logging.error(f"FACTOR_FROM_PAREN_PROCESSING: lpar={lpar_token}, expr_node={expr_node}, rpar={rpar_token}")
        
        if not isinstance(expr_node, ASTNode):
            logging.error(f"FACTOR_FROM_PAREN_ERROR: expr_node is not an ASTNode: {type(expr_node)}, {expr_node}")
            raise ValueError(f"factor_from_paren: Expected expr_node to be ASTNode, got {type(expr_node)}")
        
        logging.error(f"FACTOR_FROM_PAREN_RETURNING: {expr_node}")
        return expr_node

    @v_args(inline=False)
    def factor(self, children):
        """
        Transforms the 'factor' rule.
        Delegates to FactorBuilder for complex logic.
        """
        return self.factor_builder.build(children)

    @v_args(inline=False)
    def term(self, children):
        """
        Handles 'term' rule: factor ( (TIMES|DIVIDE) factor )*
        Delegates to BinaryExpressionBuilder for left-associative parsing.
        """
        valid_operators = {'TIMES', 'DIVIDE'}
        return self.binary_builder.build_from_children(children, valid_operators)

    @v_args(inline=False)
    def expr(self, children):
        """
        Handles 'expr' rule: term ( (ADD|SUB) term )*
        Delegates to BinaryExpressionBuilder for left-associative parsing.
        """
        valid_operators = {'PLUS', 'MINUS'}
        return self.binary_builder.build_from_children(children, valid_operators)

    @v_args(inline=False)
    def uminus(self, children):
        """
        Handles 'uminus' rule: MINUS factor
        Note: This may be redundant if 'factor' handles unary ops directly.
        """
        if (len(children) == 2 and 
            isinstance(children[0], Token) and children[0].type == 'MINUS' and 
            isinstance(children[1], ASTNode)):
            
            return self.unary_builder.build(children[0], children[1])
        
        self.logger.error(f"UMINUS_ERROR: Unexpected children for uminus: {children}")
        raise ValueError(f"uminus expected Token(MINUS) and ASTNode, got: {children}")

    @v_args(inline=False)
    def uplus(self, children):
        """
        Handles 'uplus' rule: PLUS factor
        Note: This may be redundant if 'factor' handles unary ops directly.
        """
        if (len(children) == 2 and 
            isinstance(children[0], Token) and children[0].type == 'PLUS' and 
            isinstance(children[1], ASTNode)):
            
            return self.unary_builder.build(children[0], children[1])
        
        self.logger.error(f"UPLUS_ERROR: Unexpected children for uplus: {children}")
        raise ValueError(f"uplus expected Token(PLUS) and ASTNode, got: {children}")

    @v_args(inline=True)
    def start(self, top_expression_node):
        """
        Handles 'start' rule: simply returns the top expression.
        The 'start: expr' rule means top_expression_node is the result of transforming 'expr'.
        """
        return top_expression_node

    def _get_location(self, item: Union[Token, Tree, ASTNode]) -> Optional[SourceLocation]:
        """
        Extracts source location information.
        Delegates to LocationExtractor for consistency.
        """
        return self.location_extractor.extract(item)