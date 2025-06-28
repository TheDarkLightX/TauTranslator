Module src.tau_translator_omega.core_engine.translators.tce_tau_transformer
===========================================================================
TCE/Tau Lark Transformer
========================

Transforms between TCE (Tau Controlled English) and Tau language using Lark parse trees.
This transformer handles bidirectional translation between natural language and formal syntax.

Author: DarkLightX / Dana Edwards

Classes
-------

`TCEToTauTransformer()`
:   Transforms TCE parse tree to Tau language syntax.
    
    This transformer converts natural language expressions parsed by the TCE grammar
    into formal Tau language syntax.

    ### Ancestors (in MRO)

    * lark.visitors.Transformer
    * lark.visitors._Decoratable
    * abc.ABC
    * typing.Generic

    ### Methods

    `ARITHMETIC_OP(self, token)`
    :   Process arithmetic operators.

    `CNAME(self, token)`
    :   Process identifier tokens.

    `COMPARISON_OP(self, token)`
    :   Process comparison operators.

    `ESCAPED_STRING(self, token)`
    :   Process string tokens.

    `NUMBER(self, token)`
    :   Process number tokens.

    `and_expr(self, items)`
    :   Process AND expressions.

    `arg_list(self, items)`
    :   Process argument lists.

    `arithmetic_expr(self, items)`
    :   Process arithmetic expressions.

    `atom(self, items)`
    :   Process atomic expressions.

    `boolean_literal(self, items)`
    :   Process boolean literals.

    `comparison_expr(self, items)`
    :   Process comparison expressions.

    `conditional_expr(self, items)`
    :   Process conditional if-then-else expressions.

    `constant(self, items)`
    :   Process constants (legacy).

    `definition(self, items)`
    :   Process a definition.

    `expr(self, items)`
    :   Process top-level expression.

    `fact(self, items)`
    :   Process a fact (simple expression).

    `factor(self, items)`
    :   Process factors (possibly with unary operators).

    `identifier(self, items)`
    :   Process identifiers (new grammar rule).

    `literal(self, items)`
    :   Process literal values (new grammar rule).

    `or_expr(self, items)`
    :   Process OR expressions.

    `param(self, items)`
    :   Process a single parameter.

    `param_list(self, items)`
    :   Process parameter lists.

    `predicate_call(self, items)`
    :   Process predicate call.

    `predicate_def(self, items)`
    :   Process predicate definition.

    `quant_block(self, items)`
    :   Process quantifier blocks (legacy).

    `quantifier_expr(self, items)`
    :   Process quantifier expressions (new grammar rule).

    `rule(self, items)`
    :   Process a rule (if-then statement).

    `sentence(self, items)`
    :   Process a single sentence.

    `start(self, items)`
    :   Combine all sentences.

    `stream_ref(self, items)`
    :   Process stream references.

    `term(self, items)`
    :   Process multiplication/division terms.

    `time_spec(self, items)`
    :   Process time specifications.

    `var_list(self, items)`
    :   Process variable lists.

    `variable(self, items)`
    :   Process variables (legacy).

    `xor_expr(self, items)`
    :   Process XOR expressions.

`TauToTCETransformer()`
:   Transforms Tau parse tree to TCE (natural language).
    
    This transformer converts formal Tau syntax parsed by a Tau grammar
    into natural language TCE expressions.

    ### Ancestors (in MRO)

    * lark.visitors.Transformer
    * lark.visitors._Decoratable
    * abc.ABC
    * typing.Generic

    ### Methods

    `start(self, items)`
    :   Combine all statements.

    `statement(self, items)`
    :   Process a single Tau statement.