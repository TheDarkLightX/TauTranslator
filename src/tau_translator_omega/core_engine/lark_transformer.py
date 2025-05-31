# src/tau_translator_omega/core_engine/lark_transformer.py
"""
Provides the CST to AST transformer for Lark-generated parse trees.
"""

from lark import Transformer, v_args, Token, Tree
import logging # Import logging
from typing import Union, Optional # Import Union and Optional

# Configure basic logging to a file. This will be effective only once.
# If parser.py is imported first and also configures it, that one will take precedence if it runs first.
# logging.basicConfig(
#     filename='transformer_debug.log', 
#     filemode='w',  # Overwrite log file on each run
#     level=logging.ERROR, 
#     format='%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
# )

# Use absolute imports for ASTNode and other node types
from tau_translator_omega.core_engine.ast_nodes import ASTNode, LiteralNode, BinaryExpressionNode, UnaryExpressionNode, SourceLocation

# We might not need ModuleNode if the grammar only produces a single expression.


class SimpleMathTransformer(Transformer):
    """
    Transforms a CST from the simple_math.lark grammar into our custom AST nodes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize a logger for this transformer instance
        # Using a logger specific to this class for better log filtering if needed
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        # You can set a default logging level for this specific logger if desired, e.g.:
        # self.logger.setLevel(logging.DEBUG) 
        # Ensure the root logger is configured elsewhere in your application for messages to appear.
        logging.error("SimpleMathTransformer: Initialized") # LOGGING

    @v_args(inline=True)
    def NUMBER(self, token):
        # logging.error(f"DEBUG: NUMBER received token: {token}") # DEBUG PRINT
        return LiteralNode(value=int(token.value), location=self._get_location(token))

    @v_args(inline=False) # This method handles the 'LPAR expr RPAR' production for 'factor'
    def factor_from_paren(self, children):
        """Handles the 'LPAR expr RPAR' production, now aliased as 'factor_from_paren'."""
        # This method is called when 'factor' is (expr)
        # children will be [Token('LPAR'), transformed_expr_node, Token('RPAR')]
        logging.error(f"DEBUG: factor_from_paren received children: {children}, types: {[type(c) for c in children]}") # DEBUG PRINT

        if not children or len(children) != 3:
            logging.error(f"FACTOR_FROM_PAREN_ERROR: Unexpected children structure: {children}")
            # This case should ideally not be reached if grammar is LPAR expr RPAR
            # and alias factor_from_paren is correctly mapped.
            raise ValueError(f"factor_from_paren expected 3 children (LPAR, expr, RPAR), got {len(children)}: {children}")

        # children should be [Token('LPAR'), expr_node, Token('RPAR')]
        lpar_token, expr_node, rpar_token = children

        logging.error(f"FACTOR_FROM_PAREN_PROCESSING: lpar={lpar_token}, expr_node={expr_node}, rpar={rpar_token}")

        if not isinstance(expr_node, ASTNode):
            logging.error(f"FACTOR_FROM_PAREN_ERROR: expr_node is not an ASTNode: {type(expr_node)}, {expr_node}")
            raise ValueError(f"factor_from_paren: Expected expr_node to be ASTNode, got {type(expr_node)}")

        # The transformed expression node is what we want to return.
        # Location note: expr_node already has its location. If we wanted the location of the
        # entire parenthesized expression, we'd need to calculate it from lpar_token and rpar_token.
        logging.error(f"FACTOR_FROM_PAREN_RETURNING: {expr_node}")
        return expr_node

    @v_args(inline=False)
    def factor(self, children):
        """Transforms the 'factor' rule.
        Handles various factor structures: numbers, parenthesized expressions, and unary operations.
        """
        # Log factor method inputs at info level if needed for diagnostics

        if not children:
            self.logger.error("FACTOR_METHOD_ERROR: No children received.")
            raise ValueError("Factor method received no children.")

        # Case 1: Unary operation (e.g., MINUS factor, PLUS factor)
        if len(children) == 2 and isinstance(children[0], Token) and children[0].type in ['MINUS', 'PLUS'] and isinstance(children[1], ASTNode):
            operator_token = children[0]
            operand_node = children[1]
            
            if operator_token.type == 'PLUS':
                # For unary PLUS, effectively a no-op, return the operand directly
                # This aligns with test_parse_unary_plus expecting LiteralNode for '+number'
                # Unary PLUS - return operand directly
                return operand_node 
            elif operator_token.type == 'MINUS':
                # For unary MINUS, create a UnaryExpressionNode
                # Unary MINUS - create UnaryExpressionNode
                return UnaryExpressionNode(operator=operator_token.value, 
                                           operand=operand_node, 
                                           location=self._get_location(operator_token))
            # Should not happen if types are MINUS or PLUS as per outer if, but good for safety
            else: 
                 self.logger.error(f"Factor: Unhandled unary operator type '{operator_token.type}'. This should not be reached.")
                 raise ValueError(f"Factor: Unhandled unary operator type '{operator_token.type}'")

        # Case 2: Parenthesized expression (e.g., LPAREN expr RPAR)
        # Assumes grammar rule like 'factor: LPAREN expr RPAR'
        if len(children) == 3 and isinstance(children[0], Token) and children[0].type == 'LPAR' and \
           isinstance(children[1], ASTNode) and \
           isinstance(children[2], Token) and children[2].type == 'RPAR':
            # Parenthesized expression - return inner expression
            # The middle child is the transformed expression node.
            return children[1] 

        # Case 3: Single ASTNode (e.g., a LiteralNode from NUMBER, or already processed factor)
        if len(children) == 1 and isinstance(children[0], ASTNode):
            # Single ASTNode child - pass through
            return children[0]
        
        # If none of the above, it's an unexpected structure
        self.logger.error(f"FACTOR_METHOD_ERROR: Unexpected children structure. Got {len(children)} children: {children}")
        type_details = [f"Child {i}: {type(c)} Value: {getattr(c, 'value', 'N/A')} TypeAttr: {getattr(c, 'type', 'N/A')}" for i, c in enumerate(children)]
        self.logger.error("FACTOR_METHOD_ERROR: Children details: " + " | ".join(type_details))
        raise ValueError(f"Factor method received unexpected structure: {len(children)} children. Details: {type_details}")

    @v_args(inline=False) # children are [factor_node, Token(OP), factor_node, Token(OP), factor_node ...]
    def term(self, children):
        """Handles 'term' rule: factor ( (TIMES|DIVIDE) factor )*"""
        # Process term with received children

        left = children[0]
        if not isinstance(left, ASTNode):
             raise ValueError(f"Term expected ASTNode for left operand (from factor transform), got {type(left)}")

        if len(children) == 1:
            return left

        current_result = left
        i = 1
        while i < len(children):
            operator_token = children[i]
            if not (isinstance(operator_token, Token) and operator_token.type in ('TIMES', 'DIVIDE')):
                raise ValueError(f"Term expected TIMES or DIVIDE token, got {operator_token}")
            
            if i + 1 >= len(children):
                raise ValueError(f"Term parsing error: Missing right operand for operator {operator_token.value}")
            
            right = children[i+1]
            if not isinstance(right, ASTNode):
                raise ValueError(f"Term expected ASTNode for right operand (from factor transform), got {type(right)}")

            # Process binary operation
            current_result = BinaryExpressionNode(left=current_result, operator=operator_token.value, right=right)
            # Binary operation completed
            i += 2
        return current_result

    @v_args(inline=False)
    def expr(self, children):
        """Handles 'expr' rule: term ( (ADD|SUB) term )*"""
        # Process expression with received children

        left = children[0]
        if not isinstance(left, ASTNode):
            raise ValueError(f"Expr expected ASTNode for left operand (from term transform), got {type(left)}")

        if len(children) == 1:
            return left

        current_result = left
        i = 1
        while i < len(children):
            operator_token = children[i]
            if not (isinstance(operator_token, Token) and operator_token.type in ('PLUS', 'MINUS')):
                 raise ValueError(f"Expr expected ADD or SUB token, got {operator_token}")

            if i + 1 >= len(children):
                raise ValueError(f"Expr parsing error: Missing right operand for operator {operator_token.value}")

            right = children[i+1]
            if not isinstance(right, ASTNode):
                # This case should ideally not happen if term/factor correctly return ASTNodes
                self.logger.error(f"EXPR_UNEXPECTED_RIGHT_OPERAND: Expected ASTNode at children[{i+1}] (from term transform), got {type(right)}. Children: {children}")
                raise ValueError(f"Expr expected ASTNode for right operand (from term transform), got {type(right)}")
            
            # Process binary operation
            current_result = BinaryExpressionNode(left=current_result, operator=operator_token.value, right=right)
            # Binary operation completed
            i += 2
        return current_result

    # This method might become redundant if 'factor' handles unary ops directly.
    @v_args(inline=False) # children are [Token(MINUS), factor_node]
    def uminus(self, children):
        """Handles 'uminus' rule: MINUS factor"""
        # This method might be superseded if the main 'factor' method handles unary ops directly.
        # Process unary minus
        if len(children) == 2 and isinstance(children[0], Token) and children[0].type == 'MINUS' and isinstance(children[1], ASTNode):
            operator_token = children[0]
            operand_node = children[1]
            return UnaryExpressionNode(operator=operator_token.value, operand=operand_node, location=self._get_location(operator_token))
        self.logger.error(f"UMINUS_ERROR: Unexpected children for uminus: {children}")
        raise ValueError(f"uminus expected Token(MINUS) and ASTNode, got: {children}")

    # This method might become redundant if 'factor' handles unary ops directly.
    @v_args(inline=False) # children are [Token(PLUS), factor_node]
    def uplus(self, children):
        """Handles 'uplus' rule: PLUS factor"""
        # This method might be superseded if the main 'factor' method handles unary ops directly.
        # Process unary plus
        if len(children) == 2 and isinstance(children[0], Token) and children[0].type == 'PLUS' and isinstance(children[1], ASTNode):
            operator_token = children[0]
            operand_node = children[1]
            return UnaryExpressionNode(operator=operator_token.value, operand=operand_node, location=self._get_location(operator_token))
        self.logger.error(f"UPLUS_ERROR: Unexpected children for uplus: {children}")
        raise ValueError(f"uplus expected Token(PLUS) and ASTNode, got: {children}")

    @v_args(inline=True) # Assuming 'start: expr' means expr is the only child
    def start(self, top_expression_node):
        # Process start node with top expression
        # 'start: expr', so top_expression_node is the result of transforming 'expr'
        return top_expression_node
    # The 'start' rule of simple_math.lark is 'start: expr'.
    # If the root of the CST is 'expr' (as observed), Lark might call 'expr' method directly for the root.

    def _get_location(self, item: Union[Token, Tree, ASTNode]) -> Optional[SourceLocation]:
        """Extracts source location information from a Token, Tree, or ASTNode."""
        if isinstance(item, Token):
            # Ensure end_line and end_column are not None before passing to SourceLocation
            # Lark's Token might have None for these if it's a zero-width token or at EOF.
            # However, for typical operators and numbers, they should be populated.
            return SourceLocation(line=item.line, column=item.column, 
                                  end_line=item.end_line if item.end_line is not None else item.line, 
                                  end_column=item.end_column if item.end_column is not None else item.column + len(item.value),
                                  absolute_char_start_index=item.start_pos,
                                  absolute_char_end_index=item.end_pos)
        elif isinstance(item, Tree):
            # For a Tree, try to get location from its first and last tokens/children
            if not item.children:
                # If tree has no children, try to use its own meta if available (might be empty)
                if hasattr(item, 'meta') and not item.meta.empty:
                    return SourceLocation(line=item.meta.line, column=item.meta.column,
                                          end_line=item.meta.end_line, end_column=item.meta.end_column,
                                          absolute_char_start_index=item.meta.start_pos,
                                          absolute_char_end_index=item.meta.end_pos)
                return None

            first_loc_item = item.children[0]
            last_loc_item = item.children[-1]

            start_loc = self._get_location(first_loc_item)
            end_loc = self._get_location(last_loc_item)

            if start_loc and end_loc:
                return SourceLocation(line=start_loc.line, column=start_loc.column,
                                      end_line=end_loc.end_line, end_column=end_loc.end_column,
                                      absolute_char_start_index=start_loc.absolute_char_start_index,
                                      absolute_char_end_index=end_loc.absolute_char_end_index)
            elif start_loc: # Only start is valid
                return start_loc
            elif end_loc: # Only end is valid (unlikely if start isn't)
                return end_loc
            # Fallback if children don't provide good locations, try tree's own meta
            if hasattr(item, 'meta') and not item.meta.empty:
                 return SourceLocation(line=item.meta.line, column=item.meta.column,
                                      end_line=item.meta.end_line, end_column=item.meta.end_column,
                                      absolute_char_start_index=item.meta.start_pos,
                                      absolute_char_end_index=item.meta.end_pos)
        elif isinstance(item, ASTNode):
            return item.location # ASTNodes now store their own location
        return None
