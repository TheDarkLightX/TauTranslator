Module src.tau_translator_omega.core_engine.lark_transformer
============================================================
Provides the CST to AST transformer for Lark-generated parse trees.

Classes
-------

`SimpleMathTransformer(*args, **kwargs)`
:   Transforms a CST from the simple_math.lark grammar into our custom AST nodes.
    
    This transformer uses builder classes to handle complex expression construction,
    following the Single Responsibility Principle.

    ### Ancestors (in MRO)

    * lark.visitors.Transformer
    * lark.visitors._Decoratable
    * abc.ABC
    * typing.Generic

    ### Methods

    `NUMBER(self, token)`
    :   Transform NUMBER token to LiteralNode.

    `expr(self, children)`
    :   Handles 'expr' rule: term ( (ADD|SUB) term )*
        Delegates to BinaryExpressionBuilder for left-associative parsing.

    `factor(self, children)`
    :   Transforms the 'factor' rule.
        Delegates to FactorBuilder for complex logic.

    `factor_from_paren(self, children)`
    :   Handles the 'LPAR expr RPAR' production.
        
        Args:
            children: [Token('LPAR'), transformed_expr_node, Token('RPAR')]
            
        Returns:
            The transformed expression node

    `start(self, top_expression_node)`
    :   Handles 'start' rule: simply returns the top expression.
        The 'start: expr' rule means top_expression_node is the result of transforming 'expr'.

    `term(self, children)`
    :   Handles 'term' rule: factor ( (TIMES|DIVIDE) factor )*
        Delegates to BinaryExpressionBuilder for left-associative parsing.

    `uminus(self, children)`
    :   Handles 'uminus' rule: MINUS factor
        Note: This may be redundant if 'factor' handles unary ops directly.

    `uplus(self, children)`
    :   Handles 'uplus' rule: PLUS factor
        Note: This may be redundant if 'factor' handles unary ops directly.