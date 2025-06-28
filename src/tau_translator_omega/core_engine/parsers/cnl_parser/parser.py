import pathlib
from lark import Lark, Transformer, v_args, Token
from typing import List, Union, Optional

# Import AST nodes - handle both relative and absolute imports
from .ast_nodes import (
    ASTNode, SentenceNode, FactNode, RuleNode, DefinitionNode, ParameterNode,
    PredicateCallNode, QuantifierBlockNode, ConditionalExpressionNode, VariableNode, ConstantNode, BooleanBinaryOpNode,
    BooleanUnaryOpNode, ComparisonNode, ArithmeticBinaryOpNode, StreamReferenceNode,
    TimeOffsetNode, ExprNode, TimeLiteralNode, TimeVariableNode, TimeSpecNode, ArithmeticNode,
    ConditionNode, ArithmeticUnaryOpNode, PredicateDefNode, TemporalQuantifierNode, BitVectorNode, BitVectorType,
    TernaryOpNode, StringNode, TypeAssertionNode, NotNode
)

# Determine the absolute path to the grammar file
# parser.py is in src/tau_translator_omega/core_engine/cnl_parser/
# tau_controlled.lark is in src/tau_translator_omega/core_engine/parsers/grammars/
GRAMMAR_FILE_PATH = pathlib.Path(__file__).parent.parent / "grammars" / "tau_controlled.lark"

def _build_binary_op_tree(items: list, node_type: type) -> ASTNode:
    """Helper to build a left-associative binary operation tree from a flat list."""
    if len(items) == 1:
        return items[0]
    
    # Initial node
    node = node_type(op=str(items[1]), left=items[0], right=items[2])
    
    # Chain the rest of the operations
    for i in range(3, len(items), 2):
        op_token = items[i]
        right_operand = items[i+1]
        node = node_type(op=str(op_token), left=node, right=right_operand)
        
    return node

class TceTransformer(Transformer):
    def __init__(self, visit_tokens=True):
        super().__init__(visit_tokens=visit_tokens)

    # --- Operator Mapping ---
    COMPARISON_OP_MAP = {
        "is equal to": "==", "equals": "==", "==": "==",
        "is not equal to": "!=", "!=": "!=",
        "is not": "!=",
        "is less than": "<", "<": "<",
        "is less than or equal to": "<=", "<=": "<=",
        "is greater than": ">", ">": ">",
        "is greater than or equal to": ">=", ">=": ">=",
        "is not less than": "!<",
        "is not less than or equal to": "!<=",
        "is not greater than": "!>",
        "is not greater than or equal to": "!>=",

        # RHS Operators
        "less than": "<",
        "less than or equal to": "<=",
        "greater than": ">",
        "greater than or equal to": ">=",
        "equal to": "==",
        "not equal to": "!=",
        "not less than": "!<",
        "not less than or equal to": "!<=",
        "not greater than": "!>",
        "not greater than or equal to": "!>=",
    }

    LOGICAL_OP_MAP = {
        "LOGICAL_AND": "&&",
        "LOGICAL_OR": "||",
        "LOGICAL_XOR": "xor",
        "LOGICAL_IFF": "iff",
    }

    # --- Terminal Processing ---
    def CNAME(self, token: Token) -> str:
        return str(token.value)

    @v_args(inline=True)
    def NUMBER(self, token: Token) -> ConstantNode:
        val_str = str(token.value)
        if '.' in val_str or 'e' in val_str.lower():
            return ConstantNode(value=float(val_str), value_type='FLOAT')
        return ConstantNode(value=int(val_str), value_type='INTEGER')

    # --- Helper for binary operations ---
    def _build_op_tree(self, items: list, node_type: type) -> ASTNode:
            if len(items) == 1:
                return items[0]
            
            node = items[0]
            for i in range(1, len(items), 2):
                op_token = items[i]
                right = items[i+1]
                op_str = self.LOGICAL_OP_MAP.get(op_token.type, str(op_token))
                node = node_type(operator=op_str, left=node, right=right)
            return node


    # --- Top-Level Rules ---
    def spec(self, items: list) -> ASTNode:
        return self._build_op_tree(items, BooleanBinaryOpNode)

    @v_args(inline=True)
    def temporal_spec(self, child: ASTNode) -> ASTNode:
        # Handles parenthesized spec as well
        return child

    @v_args(inline=False)
    def always(self, items) -> TemporalQuantifierNode:
        """Processes an 'always' temporal quantifier."""
        return TemporalQuantifierNode(quantifier='always', operand=items[0])

    @v_args(inline=False)
    def sometimes(self, items) -> TemporalQuantifierNode:
        """Processes a 'sometimes' temporal quantifier."""
        return TemporalQuantifierNode(quantifier='sometimes', operand=items[0])

    @v_args(inline=False)
    def eventually(self, items) -> TemporalQuantifierNode:
        """Processes an 'eventually' temporal quantifier."""
        return TemporalQuantifierNode(quantifier='eventually', operand=items[0])

    @v_args(inline=False)
    def never(self, items) -> TemporalQuantifierNode:
        """Processes a 'never' temporal quantifier."""
        return TemporalQuantifierNode(quantifier='never', operand=items[0])

    @v_args(inline=True)
    def not_spec(self, items) -> NotNode:
        return NotNode(operand=items)

    @v_args(inline=True)
    def local_spec(self, child: ASTNode) -> ASTNode:
        # This rule just passes up the parsed child node.
        # It's useful for grammar organization.
        return child

    def logical_expr(self, items: list) -> ASTNode:
        return self._build_op_tree(items, BooleanBinaryOpNode)

    @v_args(inline=True)
    def is_a_fact(self, subject, object) -> PredicateCallNode:
        """Processes 'X is a Y' facts."""
        if not isinstance(object, VariableNode):
            raise TypeError(f"Expected object of 'is a' fact to be a VariableNode, but got {type(object)}")
        return PredicateCallNode(name=object.name, args=[subject])

    @v_args(inline=True)
    def true_literal(self, *args) -> ConstantNode:
        return ConstantNode(value=True, value_type='BOOLEAN')

    @v_args(inline=True)
    def false_literal(self, *args) -> ConstantNode:
        return ConstantNode(value=False, value_type='BOOLEAN')

    @v_args(inline=True)
    def negated_is_a_fact(self, subject, object) -> NotNode:
        """Processes 'X is not a Y' facts."""
        # This is essentially not(is_a(X, Y))
        inner_fact = self.is_a_fact(subject, object)
        return NotNode(operand=inner_fact)

    def relational_fact(self, items: list) -> PredicateCallNode:
        """Processes 'X verb Y Z...' facts with a variable number of arguments."""
        subject = items[0]
        predicate_token = items[1]
        objects = items[2:]

        # The arguments for the predicate call are the subject followed by all objects.
        all_args = [subject] + objects

        return PredicateCallNode(name=str(predicate_token), args=all_args)

    @v_args(inline=True)
    def type_assertion(self, variable, type_name):
        """Processes a type assertion statement."""
        return TypeAssertionNode(variable=variable, type_name=str(type_name))

    @v_args(inline=True)
    def negated_fact(self, fact_node) -> BooleanUnaryOpNode:
        """Processes 'it is not true that X'."""
        return BooleanUnaryOpNode(operator="NOT", operand=fact_node)

    @v_args(inline=True)
    def and_expr(self, left, op, right) -> BooleanBinaryOpNode:
        return BooleanBinaryOpNode(operator="&&", left=left, right=right)

    @v_args(inline=True)
    def or_expr(self, left, op, right) -> BooleanBinaryOpNode:
        return BooleanBinaryOpNode(operator="||", left=left, right=right)

    @v_args(inline=True)
    def xor_expr(self, left, op, right) -> BooleanBinaryOpNode:
        return BooleanBinaryOpNode(operator="xor", left=left, right=right)

    @v_args(inline=True)
    def iff_expr(self, left, op, right) -> BooleanBinaryOpNode:
        return BooleanBinaryOpNode(operator="iff", left=left, right=right)

    @v_args(inline=True)
    def left_implication(self, consequent, _if, condition) -> ConditionalExpressionNode:
        """Processes 'A if B'."""
        return ConditionalExpressionNode(
            condition=condition,
            consequent=consequent,
            alternative=None  # No 'else' part in this structure
        )

    @v_args(inline=True)
    def not_expr(self, _, operand) -> NotNode:
        return NotNode(operand)

    @v_args(inline=True)
    def implication_expr(self, _if, condition, _then, consequent) -> ConditionalExpressionNode:
        """Processes 'if A then B'."""
        return ConditionalExpressionNode(
            condition=condition,
            consequent=consequent,
            alternative=None  # No 'else' part
        )

    @v_args(inline=True)
    def ternary_expr(self, _if, condition, _then, value_if_true, _else, value_if_false) -> TernaryOpNode:
        """Processes 'if A then B else C'."""
        return TernaryOpNode(
            condition=condition,
            value_if_true=value_if_true,
            value_if_false=value_if_false
        )

    @v_args(inline=True)
    def for_all(self, _token, var_name, _such_that, condition) -> QuantifierBlockNode:
        return QuantifierBlockNode(quantifier="forall", variables=[var_name], condition=condition)

    @v_args(inline=True)
    def exists(self, _token, var_name, _such_that, condition) -> QuantifierBlockNode:
        return QuantifierBlockNode(quantifier="exists", variables=[var_name], condition=condition)

    @v_args(inline=False)
    def comparison_expr(self, items: list) -> Union[ComparisonNode, BooleanBinaryOpNode]:
        """Processes a comparison, which may be a simple or interval expression."""
        left_term = items[0]
        op_token = items[1]
        right_term = items[2]
        
        op_str = self.COMPARISON_OP_MAP.get(op_token.value)
        if op_str is None:
            raise ValueError(f"Unknown comparison operator: {op_token.value}")
        
        main_comparison = ComparisonNode(left=left_term, op=op_str, right=right_term)
        
        if len(items) > 3:
            # This is a chained/interval comparison
            logical_op_token = items[3]
            rhs_comp_op, rhs_term = items[4] # rhs_comparison returns a tuple
            
            # The subject of the second comparison is the same as the first one
            rhs_comparison_node = ComparisonNode(left=left_term, op=rhs_comp_op, right=rhs_term)
            
            logical_op = "&&" if logical_op_token.type == 'BITWISE_AND' else "&&" # Default to logical AND
            return BooleanBinaryOpNode(left=main_comparison, operator=logical_op, right=rhs_comparison_node)
            
        return main_comparison

    @v_args(inline=True)
    def rhs_comparison(self, op, term) -> tuple:
        """Processes the right-hand side of a chained comparison."""
        op_str = self.COMPARISON_OP_MAP.get(op.value)
        if op_str is None:
            raise ValueError(f"Unknown RHS comparison operator: {op.value}")
        return (op_str, term)

    # --- Term Rules ---
    @v_args(inline=True)
    def term(self, items: list) -> ASTNode:
        # Passes up the specific term node (variable, literal, etc.)
        return items

    @v_args(inline=True)
    def bitvector(self, items) -> BitVectorNode:
        """Passes through the specific bitvector node."""
        return items

    @v_args(inline=True)
    def string_literal(self, s) -> StringNode:
        """Processes a string literal."""
        # The STRING_LITERAL from Lark includes the quotes, so we strip them.
        return StringNode(value=s[1:-1])

    @v_args(inline=True)
    def number_literal(self, n) -> ConstantNode:
        # This handles both integers and floats via the NUMBER terminal
        if isinstance(n, float):
            return ConstantNode(value=n, value_type='FLOAT')
        return ConstantNode(value=n, value_type='INTEGER')

    @v_args(inline=True)
    def variable(self, name: str) -> VariableNode:
        return VariableNode(name=name)

    def stream_variable(self, items: list) -> StreamReferenceNode:
        stream_type, stream_num, time_expr = items
        return StreamReferenceNode(name=f"{stream_type.value}{stream_num.value}", time_spec=time_expr, stream_type=stream_type.value)

    @v_args(inline=True)
    def input_stream(self, token: Token) -> Token:
        return token

    @v_args(inline=True)
    def output_stream(self, token: Token) -> Token:
        return token

    def time_expr(self, items: list) -> TimeSpecNode:
        if len(items) == 1: # just "t"
            return TimeSpecNode(base="t", offset=None)
        # "t" MINUS NUMBER
        offset_val = items[2].value
        return TimeSpecNode(base="t", offset=TimeOffsetNode(op="-", value=offset_val))

    def function_call(self, items: list) -> PredicateCallNode:
        name = items[0]
        args = items[1:] if len(items) > 1 else []
        return PredicateCallNode(name=name, args=args)

    def constant(self, items: list) -> ConstantNode:
        # The grammar has spec_constant and term_constant, which embed other expressions.
        # This requires extending the AST or handling it in a post-processing step.
        # For now, we'll represent it as a placeholder.
        const_type = items[0].type
        const_val = items[1]
        return ConstantNode(value=str(const_val), value_type=f"COMPLEX_{const_type}")

    # --- Terminal Aliases from Grammar ---
    def LOGICAL_AND(self, token: Token) -> Token: return token
    def LOGICAL_OR(self, token: Token) -> Token: return token
    def COMPARISON(self, token: Token) -> Token: return token
    def BITWISE_AND(self, token: Token) -> Token: return token
    def BITWISE_OR(self, token: Token) -> Token: return token
    def BITWISE_XOR(self, token: Token) -> Token: return token


class CNLParser:
    def __init__(self, grammar_file_path: str = None, debug: bool = False):
            if grammar_file_path is None:
                # Use the GRAMMAR_FILE_PATH defined at the top of the module
                effective_grammar_path = GRAMMAR_FILE_PATH
            else:
                effective_grammar_path = pathlib.Path(grammar_file_path)
    
            if not effective_grammar_path.is_file():
                raise FileNotFoundError(f"Grammar file not found: {effective_grammar_path}")
    
            self.grammar_path = str(effective_grammar_path.resolve())
            with open(self.grammar_path, "r") as f:
                grammar_content = f.read()
            
            grammar_dir = effective_grammar_path.parent
            # The common.lark file is in a different directory, so we add its path to import_paths
            common_grammar_dir = grammar_dir.parent / "cnl_parser" / "grammars"
            
            # Earley parser doesn't support embedded transformers, so we'll apply it separately
            self.parser = Lark(
                grammar_content,
                parser='earley', # Using Earley as it's robust for complex grammars
                start='spec',
                ambiguity='resolve', # A common strategy for ambiguity
                debug=debug,
                import_paths=[str(grammar_dir), str(common_grammar_dir)] # For %import in grammar
            )
            self.transformer = TceTransformer()

    def parse(self, text: str) -> ASTNode:
        """Parses a CNL string and returns the corresponding AST."""
        if not text.strip():
            raise ValueError("Input text cannot be empty or whitespace only.")
        try:
            parse_tree = self.parser.parse(text)
            ast_result = self.transformer.transform(parse_tree)
            return ast_result
        except Exception as e:
            raise RuntimeError(f"Failed to parse CNL text: {e}") from e