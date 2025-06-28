Module src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes
==============================================================================
EBNF AST Node Definitions

Memory-optimized AST nodes for EBNF grammar representation.
Follows the same optimization patterns as the CNL parser.

Functions
---------

`create_choice(*alternatives: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode) ‑> src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
:   Create a choice node, flattening nested choices.

`create_sequence(*elements: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode) ‑> src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
:   Create a sequence node, flattening nested sequences.

Classes
-------

`ChoiceNode(alternatives: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode])`
:   Node representing choice: A | B | C

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `alternatives: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode]`
    :

`EBNFNode()`
:   Base class for all EBNF AST nodes with memory optimization.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.GrammarNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RuleNode

    ### Methods

    `accept(self, visitor)`
    :   Accept a visitor for traversal.

`EBNFVisitor()`
:   Abstract visitor for EBNF AST traversal.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Methods

    `visit_choice(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ChoiceNode)`
    :

    `visit_grammar(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.GrammarNode)`
    :

    `visit_group(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.GroupNode)`
    :

    `visit_literal(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.LiteralNode)`
    :

    `visit_nonterminal(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.NonTerminalNode)`
    :

    `visit_optional(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.OptionalNode)`
    :

    `visit_regex(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RegexNode)`
    :

    `visit_repetition(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RepetitionNode)`
    :

    `visit_rule(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RuleNode)`
    :

    `visit_sequence(self, node: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.SequenceNode)`
    :

`ExpressionNode()`
:   Base class for expression nodes.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ChoiceNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.GroupNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.NonTerminalNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.OptionalNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RepetitionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.SequenceNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.TerminalNode

`GrammarNode(rules: List[ForwardRef('RuleNode')])`
:   Root node representing an entire EBNF grammar.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `rules: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RuleNode]`
    :

`GroupNode(expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode)`
:   Node representing grouping: (A B C)

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
    :

`LiteralNode(value: str, quote_type: str = '"')`
:   Node representing string literal: "hello" or 'hello'

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.TerminalNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `quote_type: str`
    :

    `value: str`
    :

`NonTerminalNode(name: str)`
:   Node representing non-terminal reference: rule_name

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `name: str`
    :

`OptionalNode(expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode)`
:   Node representing optional: [A] or A?

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
    :

`RegexNode(pattern: str, flags: str = '')`
:   Node representing regex pattern: /pattern/

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.TerminalNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `flags: str`
    :

    `pattern: str`
    :

`RepetitionNode(expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode, min_count: int = 0, max_count: int | None = None)`
:   Node representing repetition: {A} or A* or A+

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
    :

    `max_count: int | None`
    :

    `min_count: int`
    :

`RuleNode(name: str, expression: ExpressionNode)`
:   Node representing a single EBNF rule: name = expression.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `expression: src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode`
    :

    `name: str`
    :

`SequenceNode(elements: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode])`
:   Node representing sequence: A B C

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Instance variables

    `elements: List[src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode]`
    :

`TerminalNode()`
:   Base class for terminal nodes (literals, regex).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.ExpressionNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.EBNFNode
    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.LiteralNode
    * src.tau_translator_omega.core_engine.parsers.ebnf_parser.ebnf_ast_nodes.RegexNode