"""
Recursive descent parser implementation following the Intentional Disclosure Principle.

Each grammar rule corresponds to a parsing method, with all methods ≤10 lines.
Implements predictive parsing with lookahead and error recovery.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Tuple, Dict, Any, Callable
from returns.result import Result, Success, Failure
from returns.pipeline import pipe

from .types import (
    ParseNode, ParseTree, ParserContext, Token, SourceLocation,
    NodeType, ParseError, ErrorMessage, TokenValue
)


class RecursiveDescentParser:
    """
    Implements recursive descent parsing pattern.
    Each method corresponds to a grammar production rule.
    """
    
    def parse_program(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: program ::= statement*"""
        return self._parse_zero_or_more(
            context,
            self.parse_statement,
            NodeType("PROGRAM")
        )
    
    def parse_statement(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: statement ::= assignment | expression | conditional | loop"""
        return self._parse_first_match(context, [
            self.parse_assignment,
            self.parse_conditional,
            self.parse_loop,
            self.parse_expression_statement
        ])
    
    def parse_assignment(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: assignment ::= identifier '=' expression ';'"""
        return pipe(
            context,
            lambda ctx: self._expect_token_type(ctx, "IDENTIFIER"),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "EQUALS")),
            lambda r: self._chain_parse(r, self.parse_expression),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "SEMICOLON")),
            lambda r: self._build_assignment_node(r)
        )
    
    def parse_conditional(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: conditional ::= 'if' '(' expression ')' statement ('else' statement)?"""
        return pipe(
            context,
            lambda ctx: self._expect_token(ctx, "IF"),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "LPAREN")),
            lambda r: self._chain_parse(r, self.parse_expression),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "RPAREN")),
            lambda r: self._chain_parse(r, self.parse_statement),
            lambda r: self._parse_optional_else(r),
            lambda r: self._build_conditional_node(r)
        )
    
    def parse_loop(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: loop ::= 'while' '(' expression ')' statement"""
        return pipe(
            context,
            lambda ctx: self._expect_token(ctx, "WHILE"),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "LPAREN")),
            lambda r: self._chain_parse(r, self.parse_expression),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "RPAREN")),
            lambda r: self._chain_parse(r, self.parse_statement),
            lambda r: self._build_loop_node(r)
        )
    
    def parse_expression(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: expression ::= logical_or"""
        return self.parse_logical_or(context)
    
    def parse_logical_or(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: logical_or ::= logical_and ('||' logical_and)*"""
        return self._parse_binary_operation(
            context,
            self.parse_logical_and,
            ["OR"],
            NodeType("LOGICAL_OR")
        )
    
    def parse_logical_and(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: logical_and ::= equality ('&&' equality)*"""
        return self._parse_binary_operation(
            context,
            self.parse_equality,
            ["AND"],
            NodeType("LOGICAL_AND")
        )
    
    def parse_equality(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: equality ::= comparison (('==' | '!=') comparison)*"""
        return self._parse_binary_operation(
            context,
            self.parse_comparison,
            ["EQUALS_EQUALS", "NOT_EQUALS"],
            NodeType("EQUALITY")
        )
    
    def parse_comparison(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: comparison ::= term (('<' | '>' | '<=' | '>=') term)*"""
        return self._parse_binary_operation(
            context,
            self.parse_term,
            ["LESS", "GREATER", "LESS_EQUALS", "GREATER_EQUALS"],
            NodeType("COMPARISON")
        )
    
    def parse_term(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: term ::= factor (('+' | '-') factor)*"""
        return self._parse_binary_operation(
            context,
            self.parse_factor,
            ["PLUS", "MINUS"],
            NodeType("TERM")
        )
    
    def parse_factor(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: factor ::= unary (('*' | '/' | '%') unary)*"""
        return self._parse_binary_operation(
            context,
            self.parse_unary,
            ["STAR", "SLASH", "PERCENT"],
            NodeType("FACTOR")
        )
    
    def parse_unary(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: unary ::= ('!' | '-' | '+')? power"""
        current = context.current_token()
        if current and current.type in ["BANG", "MINUS", "PLUS"]:
            return pipe(
                context.advance(),
                self.parse_power,
                lambda r: self._build_unary_node(current.type, r)
            )
        return self.parse_power(context)
    
    def parse_power(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: power ::= postfix ('^' postfix)*"""
        return self._parse_binary_operation(
            context,
            self.parse_postfix,
            ["CARET"],
            NodeType("POWER")
        )
    
    def parse_postfix(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: postfix ::= primary ('[' expression ']' | '.' identifier | '(' args ')')*"""
        return pipe(
            context,
            self.parse_primary,
            lambda r: self._parse_postfix_operations(r)
        )
    
    def parse_primary(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: primary ::= literal | identifier | '(' expression ')' | array | object"""
        return self._parse_first_match(context, [
            self.parse_literal,
            self.parse_identifier,
            self.parse_parenthesized,
            self.parse_array,
            self.parse_object
        ])
    
    def parse_literal(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: literal ::= NUMBER | STRING | BOOLEAN | NULL"""
        current = context.current_token()
        if not current:
            return Failure("Expected literal, found end of input")
        
        if current.type in ["NUMBER", "STRING", "BOOLEAN", "NULL"]:
            return Success((self._create_literal_node(current), context.advance()))
        
        return Failure(f"Expected literal, found {current.type}")
    
    def parse_identifier(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: identifier ::= IDENTIFIER"""
        return self._expect_token_type(context, "IDENTIFIER")
    
    def parse_parenthesized(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: parenthesized ::= '(' expression ')'"""
        return pipe(
            context,
            lambda ctx: self._expect_token(ctx, "LPAREN"),
            lambda r: self._chain_parse(r, self.parse_expression),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "RPAREN")),
            lambda r: Success((r[0][1], r[1]))  # Extract expression, discard parentheses
        )
    
    def parse_array(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: array ::= '[' (expression (',' expression)*)? ']'"""
        return pipe(
            context,
            lambda ctx: self._expect_token(ctx, "LBRACKET"),
            lambda r: self._parse_comma_separated(r[1], self.parse_expression),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "RBRACKET")),
            lambda r: self._build_array_node(r)
        )
    
    def parse_object(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: object ::= '{' (property (',' property)*)? '}'"""
        return pipe(
            context,
            lambda ctx: self._expect_token(ctx, "LBRACE"),
            lambda r: self._parse_comma_separated(r[1], self.parse_property),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "RBRACE")),
            lambda r: self._build_object_node(r)
        )
    
    def parse_property(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: property ::= (identifier | string) ':' expression"""
        return pipe(
            context,
            lambda ctx: self._parse_property_key(ctx),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "COLON")),
            lambda r: self._chain_parse(r, self.parse_expression),
            lambda r: self._build_property_node(r)
        )
    
    def parse_expression_statement(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse: expression_statement ::= expression ';'"""
        return pipe(
            context,
            self.parse_expression,
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "SEMICOLON")),
            lambda r: self._build_expression_statement_node(r)
        )
    
    # Helper methods (all ≤10 lines)
    
    def _expect_token(self, context: ParserContext, expected: str) -> Result[Tuple[Token, ParserContext], str]:
        """Expect specific token type and advance."""
        current = context.current_token()
        if not current:
            return Failure(f"Expected {expected}, found end of input")
        
        if current.type == expected:
            return Success((current, context.advance()))
        
        return Failure(f"Expected {expected}, found {current.type}")
    
    def _expect_token_type(self, context: ParserContext, token_type: str) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Expect token type and create node."""
        result = self._expect_token(context, token_type)
        if isinstance(result, Success):
            token, new_context = result.unwrap()
            node = self._create_token_node(token)
            return Success((node, new_context))
        return result
    
    def _parse_binary_operation(
        self,
        context: ParserContext,
        operand_parser: Callable,
        operators: List[str],
        node_type: NodeType
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse left-associative binary operation."""
        left_result = operand_parser(context)
        if isinstance(left_result, Failure):
            return left_result
        
        left, ctx = left_result.unwrap()
        return self._parse_binary_tail(ctx, left, operand_parser, operators, node_type)
    
    def _parse_binary_tail(
        self,
        context: ParserContext,
        left: ParseNode,
        operand_parser: Callable,
        operators: List[str],
        node_type: NodeType
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse tail of binary operation (iterative to avoid recursion)."""
        current_left = left
        current_ctx = context
        
        while True:
            current = current_ctx.current_token()
            if not current or current.type not in operators:
                return Success((current_left, current_ctx))
            
            op_ctx = current_ctx.advance()
            right_result = operand_parser(op_ctx)
            
            if isinstance(right_result, Failure):
                return right_result
            
            right, new_ctx = right_result.unwrap()
            current_left = self._create_binary_node(node_type, current_left, current.type, right)
            current_ctx = new_ctx
    
    def _parse_first_match(
        self,
        context: ParserContext,
        parsers: List[Callable]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Try parsers in order until one succeeds."""
        errors = []
        
        for parser in parsers:
            result = parser(context)
            if isinstance(result, Success):
                return result
            errors.append(result.failure())
        
        return Failure(f"No matching parser. Tried: {'; '.join(errors)}")
    
    def _parse_zero_or_more(
        self,
        context: ParserContext,
        parser: Callable,
        container_type: NodeType
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse zero or more occurrences."""
        nodes = []
        current_ctx = context
        
        while True:
            result = parser(current_ctx)
            if isinstance(result, Failure):
                break
            
            node, new_ctx = result.unwrap()
            nodes.append(node)
            current_ctx = new_ctx
        
        container = self._create_container_node(container_type, nodes)
        return Success((container, current_ctx))
    
    def _parse_comma_separated(
        self,
        context: ParserContext,
        parser: Callable
    ) -> Result[Tuple[List[ParseNode], ParserContext], str]:
        """Parse comma-separated list of items."""
        if context.current_token() and context.current_token().type in ["RBRACKET", "RBRACE"]:
            return Success(([], context))
        
        items = []
        current_ctx = context
        
        while True:
            result = parser(current_ctx)
            if isinstance(result, Failure):
                return result
            
            item, new_ctx = result.unwrap()
            items.append(item)
            
            if new_ctx.current_token() and new_ctx.current_token().type == "COMMA":
                current_ctx = new_ctx.advance()
            else:
                return Success((items, new_ctx))
    
    def _parse_postfix_operations(
        self,
        initial_result: Result[Tuple[ParseNode, ParserContext], str]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse postfix operations (array access, member access, function call)."""
        if isinstance(initial_result, Failure):
            return initial_result
        
        expr, ctx = initial_result.unwrap()
        current_expr = expr
        current_ctx = ctx
        
        while True:
            postfix_result = self._parse_single_postfix(current_ctx, current_expr)
            if isinstance(postfix_result, Failure):
                return Success((current_expr, current_ctx))
            
            current_expr, current_ctx = postfix_result.unwrap()
    
    def _parse_single_postfix(
        self,
        context: ParserContext,
        expr: ParseNode
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse single postfix operation."""
        current = context.current_token()
        if not current:
            return Failure("No postfix operation")
        
        if current.type == "LBRACKET":
            return self._parse_array_access(context, expr)
        elif current.type == "DOT":
            return self._parse_member_access(context, expr)
        elif current.type == "LPAREN":
            return self._parse_function_call(context, expr)
        
        return Failure("No postfix operation")
    
    def _parse_array_access(
        self,
        context: ParserContext,
        expr: ParseNode
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse array access: expr '[' index ']'"""
        return pipe(
            context,
            lambda ctx: self._expect_token(ctx, "LBRACKET"),
            lambda r: self._chain_parse(r, self.parse_expression),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "RBRACKET")),
            lambda r: Success((self._create_array_access_node(expr, r[0][1]), r[1]))
        )
    
    def _parse_member_access(
        self,
        context: ParserContext,
        expr: ParseNode
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse member access: expr '.' identifier"""
        return pipe(
            context,
            lambda ctx: self._expect_token(ctx, "DOT"),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token_type(ctx, "IDENTIFIER")),
            lambda r: Success((self._create_member_access_node(expr, r[0][1]), r[1]))
        )
    
    def _parse_function_call(
        self,
        context: ParserContext,
        expr: ParseNode
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse function call: expr '(' args ')'"""
        return pipe(
            context,
            lambda ctx: self._expect_token(ctx, "LPAREN"),
            lambda r: self._parse_comma_separated(r[1], self.parse_expression),
            lambda r: self._chain_parse(r, lambda ctx: self._expect_token(ctx, "RPAREN")),
            lambda r: Success((self._create_function_call_node(expr, r[0][0]), r[1]))
        )
    
    def _parse_optional_else(
        self,
        result: Result[Tuple[List[Any], ParserContext], str]
    ) -> Result[Tuple[List[Any], ParserContext], str]:
        """Parse optional else clause."""
        if isinstance(result, Failure):
            return result
        
        parsed_items, ctx = result.unwrap()
        current = ctx.current_token()
        
        if current and current.type == "ELSE":
            else_result = self.parse_statement(ctx.advance())
            if isinstance(else_result, Success):
                else_stmt, new_ctx = else_result.unwrap()
                return Success((parsed_items + [else_stmt], new_ctx))
            return else_result
        
        return Success((parsed_items, ctx))
    
    def _parse_property_key(self, context: ParserContext) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Parse property key (identifier or string)."""
        current = context.current_token()
        if not current:
            return Failure("Expected property key")
        
        if current.type in ["IDENTIFIER", "STRING"]:
            return Success((self._create_token_node(current), context.advance()))
        
        return Failure(f"Expected identifier or string for property key, found {current.type}")
    
    def _chain_parse(
        self,
        prev_result: Result[Tuple[Any, ParserContext], str],
        parser: Callable
    ) -> Result[Tuple[List[Any], ParserContext], str]:
        """Chain parsing operations, accumulating results."""
        if isinstance(prev_result, Failure):
            return prev_result
        
        if isinstance(prev_result.unwrap()[0], list):
            prev_items, ctx = prev_result.unwrap()
        else:
            prev_item, ctx = prev_result.unwrap()
            prev_items = [prev_item]
        
        next_result = parser(ctx)
        if isinstance(next_result, Failure):
            return next_result
        
        next_item, new_ctx = next_result.unwrap()
        return Success((prev_items + [next_item], new_ctx))
    
    # Node creation methods (all pure, ≤10 lines)
    
    def _create_literal_node(self, token: Token) -> ParseNode:
        """Create literal node from token."""
        return ParseNode(
            node_type=NodeType(f"LITERAL_{token.type}"),
            location=self._token_to_location(token)
        )
    
    def _create_token_node(self, token: Token) -> ParseNode:
        """Create node from token."""
        return ParseNode(
            node_type=NodeType(token.type),
            location=self._token_to_location(token)
        )
    
    def _create_binary_node(
        self,
        node_type: NodeType,
        left: ParseNode,
        operator: str,
        right: ParseNode
    ) -> ParseNode:
        """Create binary operation node."""
        return ParseNode(
            node_type=node_type,
            location=self._merge_locations(left.location, right.location)
        )
    
    def _create_container_node(self, node_type: NodeType, children: List[ParseNode]) -> ParseNode:
        """Create container node with children."""
        if children:
            location = self._merge_locations(children[0].location, children[-1].location)
        else:
            location = None
        
        return ParseNode(node_type=node_type, location=location)
    
    def _create_array_access_node(self, array: ParseNode, index: ParseNode) -> ParseNode:
        """Create array access node."""
        return ParseNode(
            node_type=NodeType("ARRAY_ACCESS"),
            location=self._merge_locations(array.location, index.location)
        )
    
    def _create_member_access_node(self, object: ParseNode, member: ParseNode) -> ParseNode:
        """Create member access node."""
        return ParseNode(
            node_type=NodeType("MEMBER_ACCESS"),
            location=self._merge_locations(object.location, member.location)
        )
    
    def _create_function_call_node(self, func: ParseNode, args: List[ParseNode]) -> ParseNode:
        """Create function call node."""
        if args:
            location = self._merge_locations(func.location, args[-1].location)
        else:
            location = func.location
        
        return ParseNode(node_type=NodeType("FUNCTION_CALL"), location=location)
    
    def _build_assignment_node(
        self,
        result: Result[Tuple[List[Any], ParserContext], str]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Build assignment node from parsed components."""
        if isinstance(result, Failure):
            return result
        
        items, ctx = result.unwrap()
        # items: [identifier, equals, expression, semicolon]
        node = ParseNode(
            node_type=NodeType("ASSIGNMENT"),
            location=self._merge_locations(items[0].location, items[3].location)
        )
        return Success((node, ctx))
    
    def _build_conditional_node(
        self,
        result: Result[Tuple[List[Any], ParserContext], str]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Build conditional node from parsed components."""
        if isinstance(result, Failure):
            return result
        
        items, ctx = result.unwrap()
        # items include optional else
        node = ParseNode(
            node_type=NodeType("CONDITIONAL"),
            location=self._merge_locations(items[0].location, items[-1].location)
        )
        return Success((node, ctx))
    
    def _build_loop_node(
        self,
        result: Result[Tuple[List[Any], ParserContext], str]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Build loop node from parsed components."""
        if isinstance(result, Failure):
            return result
        
        items, ctx = result.unwrap()
        node = ParseNode(
            node_type=NodeType("WHILE_LOOP"),
            location=self._merge_locations(items[0].location, items[-1].location)
        )
        return Success((node, ctx))
    
    def _build_unary_node(
        self,
        operator: str,
        operand_result: Result[Tuple[ParseNode, ParserContext], str]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Build unary operation node."""
        if isinstance(operand_result, Failure):
            return operand_result
        
        operand, ctx = operand_result.unwrap()
        node = ParseNode(
            node_type=NodeType(f"UNARY_{operator}"),
            location=operand.location
        )
        return Success((node, ctx))
    
    def _build_array_node(
        self,
        result: Result[Tuple[List[Any], ParserContext], str]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Build array literal node."""
        if isinstance(result, Failure):
            return result
        
        items, ctx = result.unwrap()
        # items: [[elements], rbracket]
        node = ParseNode(
            node_type=NodeType("ARRAY_LITERAL"),
            location=items[1].location if items else None
        )
        return Success((node, ctx))
    
    def _build_object_node(
        self,
        result: Result[Tuple[List[Any], ParserContext], str]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Build object literal node."""
        if isinstance(result, Failure):
            return result
        
        items, ctx = result.unwrap()
        node = ParseNode(
            node_type=NodeType("OBJECT_LITERAL"),
            location=items[1].location if items else None
        )
        return Success((node, ctx))
    
    def _build_property_node(
        self,
        result: Result[Tuple[List[Any], ParserContext], str]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Build property node."""
        if isinstance(result, Failure):
            return result
        
        items, ctx = result.unwrap()
        # items: [key, colon, value]
        node = ParseNode(
            node_type=NodeType("PROPERTY"),
            location=self._merge_locations(items[0].location, items[2].location)
        )
        return Success((node, ctx))
    
    def _build_expression_statement_node(
        self,
        result: Result[Tuple[List[Any], ParserContext], str]
    ) -> Result[Tuple[ParseNode, ParserContext], str]:
        """Build expression statement node."""
        if isinstance(result, Failure):
            return result
        
        items, ctx = result.unwrap()
        # items: [expression, semicolon]
        node = ParseNode(
            node_type=NodeType("EXPRESSION_STATEMENT"),
            location=self._merge_locations(items[0].location, items[1].location)
        )
        return Success((node, ctx))
    
    # Location utilities
    
    def _token_to_location(self, token: Token) -> SourceLocation:
        """Convert token to source location."""
        return SourceLocation(
            line=token.line,
            column=token.column,
            end_line=token.end_line,
            end_column=token.end_column
        )
    
    def _merge_locations(
        self,
        start: Optional[SourceLocation],
        end: Optional[SourceLocation]
    ) -> Optional[SourceLocation]:
        """Merge two locations into span."""
        if not start:
            return end
        if not end:
            return start
        
        return SourceLocation(
            line=start.line,
            column=start.column,
            end_line=end.end_line or end.line,
            end_column=end.end_column or end.column,
            file_path=start.file_path
        )