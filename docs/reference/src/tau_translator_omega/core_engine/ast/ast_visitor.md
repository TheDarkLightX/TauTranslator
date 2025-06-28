Module src.tau_translator_omega.core_engine.ast.ast_visitor
===========================================================
AST Visitor Pattern Implementation
=================================

Implements the visitor pattern for AST traversal, replacing
isinstance() checks with polymorphic dispatch.

Author: DarkLightX / Dana Edwards

Classes
-------

`ASTVisitor()`
:   Abstract base class for AST visitors.
    
    Implements double-dispatch visitor pattern for type-safe
    AST traversal without isinstance() checks.
    
    Initialize visitor with dispatch table.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.ast.ast_visitor.TypeResolvingVisitor

    ### Methods

    `get_visit_stats(self) ‑> Dict[str, int]`
    :   Get visitation statistics.

    `visit(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode | None) ‑> Any`
    :   Visit a node using polymorphic dispatch.
        
        Args:
            node: AST node to visit
            
        Returns:
            Result of visiting the node

    `visit_arithmetic_binary_op_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticBinaryOpNode) ‑> Any`
    :   Visit arithmetic binary operation node.

    `visit_assignment_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.AssignmentNode) ‑> Any`
    :   Visit assignment node.

    `visit_boolean_binary_op_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.BooleanBinaryOpNode) ‑> Any`
    :   Visit boolean binary operation node.

    `visit_comparison_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ComparisonNode) ‑> Any`
    :   Visit comparison node.

    `visit_condition_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConditionNode) ‑> Any`
    :   Visit condition node.

    `visit_constant_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode) ‑> Any`
    :   Visit constant node.

    `visit_definition_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.DefinitionNode) ‑> Any`
    :   Visit definition node.

    `visit_fact_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.FactNode) ‑> Any`
    :   Visit fact node.

    `visit_function_definition_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.FunctionDefinitionNode) ‑> Any`
    :   Visit function definition node.

    `visit_generic_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ASTNode) ‑> Any`
    :   Fallback visitor for unknown node types.
        
        Args:
            node: Unknown node type
            
        Returns:
            Default result

    `visit_none(self) ‑> Any`
    :   Visit None node.

    `visit_number_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.NumberNode) ‑> Any`
    :   Visit number node.

    `visit_predicate_call_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateCallNode) ‑> Any`
    :   Visit predicate call node.

    `visit_predicate_definition_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateDefinitionNode) ‑> Any`
    :   Visit predicate definition node.

    `visit_quantifier_block_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.QuantifierBlockNode) ‑> Any`
    :   Visit quantifier block node.

    `visit_rule_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.RuleNode) ‑> Any`
    :   Visit rule node.

    `visit_sentence_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.SentenceNode) ‑> Any`
    :   Visit sentence node.

    `visit_string_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.StringNode) ‑> Any`
    :   Visit string node.

    `visit_variable_decl_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableDeclNode) ‑> Any`
    :   Visit variable declaration node.

    `visit_variable_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode) ‑> Any`
    :   Visit variable node.

`TypeResolvingVisitor(symbol_table)`
:   Visitor for resolving expression types.
    
    Replaces the isinstance-based type resolution in ExpressionTypeResolver.
    
    Initialize visitor with dispatch table.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ast.ast_visitor.ASTVisitor
    * abc.ABC

    ### Methods

    `visit_arithmetic_binary_op_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ArithmeticBinaryOpNode) ‑> str | None`
    :   Resolve arithmetic operation type.

    `visit_boolean_binary_op_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.BooleanBinaryOpNode) ‑> str`
    :   Boolean operations always return boolean.

    `visit_comparison_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ComparisonNode) ‑> str`
    :   Comparisons always return boolean.

    `visit_constant_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.ConstantNode) ‑> str | None`
    :   Resolve constant type.

    `visit_number_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.NumberNode) ‑> str`
    :   Number nodes are always integers.

    `visit_predicate_call_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.PredicateCallNode) ‑> str`
    :   Predicate calls return boolean.

    `visit_string_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.StringNode) ‑> str`
    :   String nodes are always strings.

    `visit_variable_node(self, node: src.tau_translator_omega.core_engine.parsers.cnl_parser.ast_nodes.VariableNode) ‑> str | None`
    :   Resolve variable type from symbol table.