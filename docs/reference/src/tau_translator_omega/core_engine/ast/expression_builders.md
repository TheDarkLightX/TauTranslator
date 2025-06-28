Module src.tau_translator_omega.core_engine.ast.expression_builders
===================================================================
Expression builder classes for Lark transformer.
Follows the Builder pattern to extract complex expression building logic.

Classes
-------

`BinaryExpressionBuilder(logger: logging.Logger | None = None)`
:   Builds binary expressions from left-associative operations.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.expression_builders.ExpressionBuilder

    ### Methods

    `build_from_children(self, children: List[lark.lexer.Token | src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode], valid_operators: set) ‑> src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode`
    :   Build a binary expression tree from a list of children.
        
        Args:
            children: List of alternating operands and operators
            valid_operators: Set of valid operator types (e.g., {'PLUS', 'MINUS'})
            
        Returns:
            ASTNode representing the expression tree

`ExpressionBuilder(logger: logging.Logger | None = None)`
:   Base builder for expressions.

    ### Descendants

    * src.tau_translator_omega.core_engine.ast.expression_builders.BinaryExpressionBuilder
    * src.tau_translator_omega.core_engine.ast.expression_builders.FactorBuilder
    * src.tau_translator_omega.core_engine.ast.expression_builders.UnaryExpressionBuilder

`FactorBuilder(unary_builder: src.tau_translator_omega.core_engine.ast.expression_builders.UnaryExpressionBuilder, logger: logging.Logger | None = None)`
:   Handles factor rule transformations.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.expression_builders.ExpressionBuilder

    ### Methods

    `build(self, children: List[lark.lexer.Token | src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode]) ‑> src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode`
    :   Build a factor from children.
        
        Handles:
        - Unary operations (PLUS/MINUS factor)
        - Parenthesized expressions (LPAR expr RPAR)
        - Single ASTNode pass-through

`LocationExtractor()`
:   Extracts source location information from various node types.

    ### Static methods

    `extract(item: lark.lexer.Token | lark.tree.Tree | src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode) ‑> src.tau_translator_omega.core_engine.ast.ast_nodes.SourceLocation | None`
    :   Extract location information from a Token, Tree, or ASTNode.

`UnaryExpressionBuilder(logger: logging.Logger | None = None)`
:   Builds unary expressions from tokens and operands.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.expression_builders.ExpressionBuilder

    ### Methods

    `build(self, operator_token: lark.lexer.Token, operand: src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode) ‑> src.tau_translator_omega.core_engine.ast.ast_nodes.ASTNode | src.tau_translator_omega.core_engine.ast.ast_nodes.UnaryExpressionNode`
    :   Build a unary expression node.
        
        Args:
            operator_token: The operator token (PLUS or MINUS)
            operand: The operand AST node
            
        Returns:
            For PLUS: returns operand directly (no-op)
            For MINUS: returns UnaryExpressionNode