Module src.tau_translator_omega.core_engine.parsers.parser.domain.recursive_parser
==================================================================================
Recursive descent parser implementation following the Intentional Disclosure Principle.

Each grammar rule corresponds to a parsing method, with all methods ≤10 lines.
Implements predictive parsing with lookahead and error recovery.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`RecursiveDescentParser()`
:   Implements recursive descent parsing pattern.
    Each method corresponds to a grammar production rule.

    ### Methods

    `parse_array(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: array ::= '[' (expression (',' expression)*)? ']'

    `parse_assignment(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: assignment ::= identifier '=' expression ';'

    `parse_comparison(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: comparison ::= term (('<' | '>' | '<=' | '>=') term)*

    `parse_conditional(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: conditional ::= 'if' '(' expression ')' statement ('else' statement)?

    `parse_equality(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: equality ::= comparison (('==' | '!=') comparison)*

    `parse_expression(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: expression ::= logical_or

    `parse_expression_statement(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: expression_statement ::= expression ';'

    `parse_factor(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: factor ::= unary (('*' | '/' | '%') unary)*

    `parse_identifier(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: identifier ::= IDENTIFIER

    `parse_literal(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: literal ::= NUMBER | STRING | BOOLEAN | NULL

    `parse_logical_and(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: logical_and ::= equality ('&&' equality)*

    `parse_logical_or(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: logical_or ::= logical_and ('||' logical_and)*

    `parse_loop(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: loop ::= 'while' '(' expression ')' statement

    `parse_object(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: object ::= '{' (property (',' property)*)? '}'

    `parse_parenthesized(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: parenthesized ::= '(' expression ')'

    `parse_postfix(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: postfix ::= primary ('[' expression ']' | '.' identifier | '(' args ')')*

    `parse_power(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: power ::= postfix ('^' postfix)*

    `parse_primary(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: primary ::= literal | identifier | '(' expression ')' | array | object

    `parse_program(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: program ::= statement*

    `parse_property(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: property ::= (identifier | string) ':' expression

    `parse_statement(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: statement ::= assignment | expression | conditional | loop

    `parse_term(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: term ::= factor (('+' | '-') factor)*

    `parse_unary(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[typing.Tuple[src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseNode, src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext], str]`
    :   Parse: unary ::= ('!' | '-' | '+')? power