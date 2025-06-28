Module src.tau_translator_omega.core_engine.parsers.cnl_parser.parser
=====================================================================

Classes
-------

`CNLParser(grammar_file_path: str = None, debug: bool = False)`
:   

    ### Methods

    `parse(self, text: str) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Parses a CNL string and returns the corresponding AST.

`TceTransformer(visit_tokens=True)`
:   Transformers work bottom-up (or depth-first), starting with visiting the leaves and working
    their way up until ending at the root of the tree.
    
    For each node visited, the transformer will call the appropriate method (callbacks), according to the
    node's ``data``, and use the returned value to replace the node, thereby creating a new tree structure.
    
    Transformers can be used to implement map & reduce patterns. Because nodes are reduced from leaf to root,
    at any point the callbacks may assume the children have already been transformed (if applicable).
    
    If the transformer cannot find a method with the right name, it will instead call ``__default__``, which by
    default creates a copy of the node.
    
    To discard a node, return Discard (``lark.visitors.Discard``).
    
    ``Transformer`` can do anything ``Visitor`` can do, but because it reconstructs the tree,
    it is slightly less efficient.
    
    A transformer without methods essentially performs a non-memoized partial deepcopy.
    
    All these classes implement the transformer interface:
    
    - ``Transformer`` - Recursively transforms the tree. This is the one you probably want.
    - ``Transformer_InPlace`` - Non-recursive. Changes the tree in-place instead of returning new instances
    - ``Transformer_InPlaceRecursive`` - Recursive. Changes the tree in-place instead of returning new instances
    
    Parameters:
        visit_tokens (bool, optional): Should the transformer visit tokens in addition to rules.
                                       Setting this to ``False`` is slightly faster. Defaults to ``True``.
                                       (For processing ignored tokens, use the ``lexer_callbacks`` options)

    ### Ancestors (in MRO)

    * lark.visitors.Transformer
    * lark.visitors._Decoratable
    * abc.ABC
    * typing.Generic

    ### Methods

    `CNAME(self, token: lark.lexer.Token) ‑> str`
    :

    `ESCAPED_STRING(self, token: lark.lexer.Token) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode`
    :

    `NUMBER(self, token: lark.lexer.Token) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode`
    :

    `and_expr(self, *args) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Transform AND expression.

    `arg_list(self, items: list) ‑> list`
    :   Transform argument list.

    `arithmetic_expr(self, *args) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Transform arithmetic expression.

    `atom(self, first_child: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | lark.lexer.Token, second_child: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | None = None, third_child: lark.lexer.Token | None = None) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :

    `boolean_literal(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode`
    :   Transform boolean literal tokens to ConstantNode.

    `comparison_expr(self, *args) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Transform comparison expression.

    `condition(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConditionNode`
    :   Transform condition.

    `constant(self, value: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode | str) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode`
    :   Transform constant values to ConstantNode.

    `definition(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.DefinitionNode`
    :   Transform definition.

    `expr(self, value: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Transform expression - pass through the value.

    `fact(self, statement: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.FactNode`
    :   Transform fact.

    `factor(self, *args) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Transform factor (unary operations).

    `identifier(self, name: str) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode`
    :   Transform identifier (CNAME) to ConstantNode.

    `literal(self, value: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode`
    :   Transform literal values to ConstantNode.

    `or_expr(self, *args) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Transform OR expression.

    `param(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ParameterNode`
    :   Transform parameter.

    `param_list(self, items: list) ‑> list`
    :   Transform parameter list.

    `predicate_call(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateCallNode`
    :   Transform predicate call.

    `predicate_def(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateDefNode`
    :   Transform predicate definition.

    `quant_block(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.QuantifierBlockNode`
    :   Transform quantifier block.

    `rule(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.RuleNode`
    :   Transform rule.

    `sentence(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.SentenceNode`
    :   Transform sentence.

    `start(self, items: list) ‑> list`
    :   Transform start rule - returns list of sentences.

    `stream_ref(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.StreamReferenceNode`
    :

    `term(self, *args) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Transform term (multiplication/division).

    `time_spec(self, items: list) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.TimeSpecNode | None`
    :

    `var_list(self, items: list) ‑> list`
    :   Transform variable list.

    `variable(self, var_name: str) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode`
    :

    `xor_expr(self, *args) ‑> src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode`
    :   Transform XOR expression.