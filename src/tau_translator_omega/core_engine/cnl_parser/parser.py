import pathlib
from lark import Lark, Transformer, v_args, Token
from typing import List, Union, Optional

# Import AST nodes - handle both relative and absolute imports
try:
    from .ast_nodes import (
        ASTNode, SentenceNode, FactNode, RuleNode, DefinitionNode, ParameterNode,
        PredicateCallNode, QuantifierBlockNode, VariableNode, ConstantNode, BooleanBinaryOpNode,
        BooleanUnaryOpNode, ComparisonNode, ArithmeticBinaryOpNode, StreamReferenceNode,
        TimeOffsetNode, ExprNode, TimeLiteralNode, TimeVariableNode, TimeSpecNode, ArithmeticNode,
        ConditionNode, ArithmeticUnaryOpNode, PredicateDefNode
    )
except ImportError:
    # Fallback for direct import
    import ast_nodes
    ASTNode = ast_nodes.ASTNode
    SentenceNode = ast_nodes.SentenceNode
    FactNode = ast_nodes.FactNode
    RuleNode = ast_nodes.RuleNode
    DefinitionNode = ast_nodes.DefinitionNode
    ParameterNode = ast_nodes.ParameterNode
    PredicateCallNode = ast_nodes.PredicateCallNode
    QuantifierBlockNode = ast_nodes.QuantifierBlockNode
    VariableNode = ast_nodes.VariableNode
    ConstantNode = ast_nodes.ConstantNode
    BooleanBinaryOpNode = ast_nodes.BooleanBinaryOpNode
    BooleanUnaryOpNode = ast_nodes.BooleanUnaryOpNode
    ComparisonNode = ast_nodes.ComparisonNode
    ArithmeticBinaryOpNode = ast_nodes.ArithmeticBinaryOpNode
    StreamReferenceNode = ast_nodes.StreamReferenceNode
    TimeOffsetNode = ast_nodes.TimeOffsetNode
    ExprNode = ast_nodes.ExprNode
    TimeLiteralNode = ast_nodes.TimeLiteralNode
    TimeVariableNode = ast_nodes.TimeVariableNode
    TimeSpecNode = ast_nodes.TimeSpecNode
    ArithmeticNode = ast_nodes.ArithmeticNode
    ConditionNode = ast_nodes.ConditionNode
    ArithmeticUnaryOpNode = ast_nodes.ArithmeticUnaryOpNode
    PredicateDefNode = ast_nodes.PredicateDefNode

# Determine the absolute path to the grammar file
# parser.py is in src/tau_translator_omega/core_engine/cnl_parser/
# tce.lark is in src/tau_translator_omega/core_engine/cnl_parser/grammars/
GRAMMAR_FILE_PATH = pathlib.Path(__file__).parent / "grammars" / "tce.lark"

class TceTransformer(Transformer):
    def __init__(self, visit_tokens=True):
        super().__init__(visit_tokens=visit_tokens)

    # Helper to convert Lark Tokens for terminals into our AST nodes or basic types
    def CNAME(self, token: Token) -> str:
        return str(token.value)

    # Terminal transformers
    @v_args(inline=True)
    def NUMBER(self, token: Token) -> ConstantNode: # Renamed from SIGNED_NUMBER
        val_str = str(token.value)
        # Check for float/scientific notation (presence of '.', 'e', or 'E')
        if '.' in val_str or 'e' in val_str.lower():
            return ConstantNode(value=float(val_str), value_type='FLOAT')
        else:
            return ConstantNode(value=int(val_str), value_type='INTEGER')

    @v_args(inline=True)
    def ESCAPED_STRING(self, token: Token) -> ConstantNode:
        # Lark's ESCAPED_STRING already handles unescaping.
        return ConstantNode(value=str(token.value[1:-1]), value_type='STRING') # Remove quotes

    @v_args(inline=True)
    def variable(self, var_name: str) -> VariableNode: # var_name comes from CNAME transformer
        name = var_name
        node = VariableNode(name=name)
        return node

    # --- Atom Level --- 
    # atom: variable | constant | stream_ref | predicate_call | LPAR expr RPAR
    @v_args(inline=True)
    def atom(self, first_child: Union[ASTNode, Token], second_child: Optional[ASTNode] = None, third_child: Optional[Token] = None) -> ASTNode:
        # If second_child or third_child is present, it implies the LPAR expr RPAR rule was matched.
        # In that specific case, first_child is LPAR, second_child is the expr_node, third_child is RPAR.
        if isinstance(first_child, Token) and first_child.type == 'LPAR':
            # This is the (LPAR expr RPAR) case.
            # The actual value we care about is the transformed expression, which is second_child.
            return second_child
        else:
            # This is one of the other cases (stream_ref, predicate_call, constant, variable).
            # first_child is the already transformed node (e.g., StreamReferenceNode, PredicateCallNode, ConstantNode, VariableNode).
            return first_child

    # --- Boolean Literals ---
    @v_args(inline=False)
    def boolean_literal(self, items: list) -> ConstantNode:
        """Transform boolean literal tokens to ConstantNode."""
        if not items:
            raise ValueError("boolean_literal received empty items list")

        token = items[0]
        if isinstance(token, Token):
            if token.type == 'TRUE_KW':
                return ConstantNode(value=True, value_type='BOOLEAN')
            elif token.type == 'FALSE_KW':
                return ConstantNode(value=False, value_type='BOOLEAN')

        raise ValueError(f"boolean_literal expected TRUE_KW or FALSE_KW token, got {token}")

    # --- Literals and Identifiers ---
    @v_args(inline=True)
    def literal(self, value: ConstantNode) -> ConstantNode:
        """Transform literal values to ConstantNode."""
        return value

    @v_args(inline=True)
    def identifier(self, name: str) -> ConstantNode:
        """Transform identifier (CNAME) to ConstantNode."""
        return ConstantNode(value=name, value_type='IDENTIFIER')

    # Legacy support for 'constant' rule (if still used)
    @v_args(inline=True)
    def constant(self, value: Union[ConstantNode, str]) -> ConstantNode:
        """Transform constant values to ConstantNode."""
        if isinstance(value, ConstantNode):
            return value
        elif isinstance(value, str):
            # CNAME as constant
            return ConstantNode(value=value, value_type='IDENTIFIER')
        else:
            raise ValueError(f"constant expected ConstantNode or string, got {type(value)}: {value}")

    # --- Expressions ---
    @v_args(inline=True)
    def expr(self, value: ASTNode) -> ASTNode:
        """Transform expression - pass through the value."""
        return value

    @v_args(inline=True)
    def or_expr(self, *args) -> ASTNode:
        """Transform OR expression."""
        if len(args) == 1:
            return args[0]
        # For multiple args, create BooleanBinaryOpNode
        result = args[0]
        for i in range(1, len(args), 2):  # Skip OR_KW tokens
            if i + 1 < len(args):
                from .ast_nodes import BooleanBinaryOpNode
                result = BooleanBinaryOpNode(left=result, operator='OR', right=args[i + 1])
        return result

    @v_args(inline=True)
    def xor_expr(self, *args) -> ASTNode:
        """Transform XOR expression."""
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                from .ast_nodes import BooleanBinaryOpNode
                result = BooleanBinaryOpNode(left=result, operator='XOR', right=args[i + 1])
        return result

    @v_args(inline=True)
    def and_expr(self, *args) -> ASTNode:
        """Transform AND expression."""
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                from .ast_nodes import BooleanBinaryOpNode
                result = BooleanBinaryOpNode(left=result, operator='AND', right=args[i + 1])
        return result

    @v_args(inline=True)
    def comparison_expr(self, *args) -> ASTNode:
        """Transform comparison expression."""
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:
            left, op_token, right = args
            from .ast_nodes import ComparisonNode
            return ComparisonNode(left=left, operator=str(op_token.value), right=right)
        else:
            raise ValueError(f"comparison_expr expected 1 or 3 args, got {len(args)}: {args}")

    @v_args(inline=True)
    def arithmetic_expr(self, *args) -> ASTNode:
        """Transform arithmetic expression."""
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                from .ast_nodes import ArithmeticBinaryOpNode
                op_token = args[i]
                right = args[i + 1]
                result = ArithmeticBinaryOpNode(left=result, operator=str(op_token.value), right=right)
        return result

    @v_args(inline=True)
    def term(self, *args) -> ASTNode:
        """Transform term (multiplication/division)."""
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                from .ast_nodes import ArithmeticBinaryOpNode
                op_token = args[i]
                right = args[i + 1]
                result = ArithmeticBinaryOpNode(left=result, operator=str(op_token.value), right=right)
        return result

    @v_args(inline=True)
    def factor(self, *args) -> ASTNode:
        """Transform factor (unary operations)."""
        if len(args) == 1:
            return args[0]
        elif len(args) == 2:
            op_token, operand = args
            from .ast_nodes import ArithmeticUnaryOpNode
            return ArithmeticUnaryOpNode(operator=str(op_token.value), operand=operand)
        else:
            raise ValueError(f"factor expected 1 or 2 args, got {len(args)}: {args}")

    # --- Predicate Calls ---
    @v_args(inline=False)
    def predicate_call(self, items: list) -> 'PredicateCallNode':
        """Transform predicate call."""
        if len(items) < 3:
            raise ValueError(f"predicate_call expected at least 3 items (name, LPAR, RPAR), got {len(items)}: {items}")

        name = items[0]  # CNAME -> string
        # items[1] is LPAR
        # items[2] is either RPAR (no args) or arg_list
        # items[3] is RPAR (if args present)

        if len(items) == 3:
            # No arguments: name LPAR RPAR
            args = []
        elif len(items) == 4:
            # With arguments: name LPAR arg_list RPAR
            arg_list = items[2]
            if isinstance(arg_list, list):
                args = arg_list
            else:
                args = [arg_list]
        else:
            raise ValueError(f"predicate_call unexpected number of items: {len(items)}: {items}")

        from .ast_nodes import PredicateCallNode
        return PredicateCallNode(name=name, args=args)

    @v_args(inline=False)
    def arg_list(self, items: list) -> list:
        """Transform argument list."""
        # arg_list: expr (COMMA expr)*
        # Returns list of expressions, filtering out COMMA tokens
        args = []
        for item in items:
            if not isinstance(item, Token) or item.type != 'COMMA':
                args.append(item)
        return args

    # --- Facts and Sentences ---
    @v_args(inline=True)
    def fact(self, statement: ASTNode) -> 'FactNode':
        """Transform fact."""
        from .ast_nodes import FactNode
        return FactNode(statement=statement)

    @v_args(inline=False)
    def sentence(self, items: list) -> 'SentenceNode':
        """Transform sentence."""
        if len(items) < 2:
            raise ValueError(f"sentence expected at least 2 items (content, terminator), got {len(items)}: {items}")

        content = items[0]  # fact, rule, or definition
        # items[1] is SENTENCE_TERMINATOR

        from .ast_nodes import SentenceNode
        return SentenceNode(content=content)

    # --- Start rule ---
    @v_args(inline=False)
    def start(self, items: list) -> list:
        """Transform start rule - returns list of sentences."""
        return [item for item in items if item is not None]

    # --- Rules and Definitions ---
    @v_args(inline=False)
    def rule(self, items: list) -> 'RuleNode':
        """Transform rule."""
        # rule: IF_KW condition THEN_KW predicate_call
        # or: quant_block THEN_KW predicate_call
        if len(items) == 4:
            # IF_KW condition THEN_KW predicate_call
            condition = items[1]
            consequent = items[3]
        elif len(items) == 3:
            # quant_block THEN_KW predicate_call
            condition = items[0]
            consequent = items[2]
        else:
            raise ValueError(f"rule expected 3 or 4 items, got {len(items)}: {items}")

        from .ast_nodes import RuleNode
        return RuleNode(condition=condition, consequent=consequent)

    @v_args(inline=False)
    def definition(self, items: list) -> 'DefinitionNode':
        """Transform definition."""
        # definition: DEFINE_KW predicate_def AS_KW expr
        if len(items) != 4:
            raise ValueError(f"definition expected 4 items, got {len(items)}: {items}")

        predicate_def = items[1]
        body = items[3]

        from .ast_nodes import DefinitionNode
        return DefinitionNode(
            name=predicate_def.name,
            parameters=predicate_def.parameters,
            body=body,
            is_function=predicate_def.is_function
        )

    @v_args(inline=False)
    def predicate_def(self, items: list) -> 'PredicateDefNode':
        """Transform predicate definition."""
        # predicate_def: (PREDICATE_KW | FUNCTION_KW) CNAME LPAR [param_list] RPAR
        if len(items) < 4:
            raise ValueError(f"predicate_def expected at least 4 items, got {len(items)}: {items}")

        keyword = items[0]  # PREDICATE_KW or FUNCTION_KW
        name = items[1]     # CNAME
        # items[2] is LPAR
        # items[3] is either param_list or RPAR
        # items[4] is RPAR (if param_list present)

        is_function = keyword.type == 'FUNCTION_KW'

        if len(items) == 4:
            # No parameters
            parameters = []
        else:
            # With parameters
            parameters = items[3] if isinstance(items[3], list) else [items[3]]

        from .ast_nodes import PredicateDefNode
        return PredicateDefNode(name=name, parameters=parameters, is_function=is_function)

    @v_args(inline=False)
    def condition(self, items: list) -> 'ConditionNode':
        """Transform condition."""
        # condition: [quant_block] expr
        if len(items) == 1:
            # Just expr
            expression = items[0]
            quantifier = None
        else:
            # quant_block expr
            quantifier = items[0]
            expression = items[1]

        from .ast_nodes import ConditionNode
        return ConditionNode(expression=expression, quantifier=quantifier)

    @v_args(inline=False)
    def quant_block(self, items: list) -> 'QuantifierBlockNode':
        """Transform quantifier block."""
        # quant_block: (FORALL_KW | EXISTS_KW) var_list (SUCH_KW THAT_KW expr)?
        if len(items) < 2:
            raise ValueError(f"quant_block expected at least 2 items, got {len(items)}: {items}")

        quant_type = 'forall' if items[0].type == 'FORALL_KW' else 'exists'
        variables = items[1] if isinstance(items[1], list) else [items[1]]

        condition = None
        if len(items) > 2:
            # SUCH_KW THAT_KW expr present
            condition = items[-1]  # Last item is the expression

        from .ast_nodes import QuantifierBlockNode
        return QuantifierBlockNode(quant_type=quant_type, variables=variables, condition=condition)

    @v_args(inline=False)
    def var_list(self, items: list) -> list:
        """Transform variable list."""
        # var_list: variable ("," variable)*
        variables = []
        for item in items:
            if not isinstance(item, Token) or item.type != 'COMMA':
                variables.append(item)
        return variables

    @v_args(inline=False)
    def param_list(self, items: list) -> list:
        """Transform parameter list."""
        # param_list: param (COMMA param)*
        params = []
        for item in items:
            if not isinstance(item, Token) or item.type != 'COMMA':
                params.append(item)
        return params

    @v_args(inline=False)
    def param(self, items: list) -> 'ParameterNode':
        """Transform parameter."""
        # param: CNAME [COLON CNAME]
        name = items[0]
        param_type = None

        if len(items) > 2:  # CNAME COLON CNAME
            param_type = items[2]

        from .ast_nodes import ParameterNode
        return ParameterNode(name=name, param_type=param_type)

    # --- Time Specifications ---
    @v_args(inline=False)
    def time_spec(self, items: list) -> Optional[TimeSpecNode]:
        if not items:
            return None # Or raise ValueError

        base_name_item = items[0]
        base_name_str = None

        if isinstance(base_name_item, VariableNode):
            base_name_str = base_name_item.name
        elif isinstance(base_name_item, str):
            base_name_str = base_name_item
        else:
            raise ValueError(f"time_spec expected CNAME string or VariableNode for base, got {type(base_name_item)}: {base_name_item}")

        if len(items) == 1:
            # Simple CNAME or variable case (e.g., "t", "now")
            return TimeSpecNode(base=base_name_str)
        elif len(items) == 3:
            # Offset case (e.g., "t - 1")
            op_token = items[1]
            offset_val_node = items[2]

            if not (isinstance(op_token, Token) and op_token.type in ["PLUS", "MINUS"]):
                raise ValueError(f"time_spec expected PLUS or MINUS token for operator, got {op_token}")
            if not isinstance(offset_val_node, ConstantNode) or offset_val_node.value_type != 'INTEGER':
                raise ValueError(f"time_spec expected INTEGER ConstantNode for offset, got {offset_val_node}")

            return TimeSpecNode(
                base=base_name_str,
                operator=str(op_token.value),
                offset=offset_val_node.value
            )
        else:
            raise ValueError(f"time_spec received unexpected number of items: {len(items)}. Items: {items}")

    # Stream Reference
    # Grammar: stream_ref: [INPUT_KW | OUTPUT_KW] CNAME [LSQB time_spec RSQB]
    # Expects a 5-element list from Lark due to optional groups when inline=False:
    # items[0]: Optional INPUT_KW/OUTPUT_KW Token, or None
    # items[1]: CNAME string (stream name)
    # items[2]: Optional LSQB Token, or None
    # items[3]: Optional TimeSpecNode (from time_spec transformer), or None
    # items[4]: Optional RSQB Token, or None
    @v_args(inline=False)
    def stream_ref(self, items: list) -> StreamReferenceNode:
        if not items or len(items) != 5:
            raise ValueError(f"stream_ref expected 5 items, got {len(items) if items else 'None'}: {items}")

        stream_type_val = None
        cname_str = None
        actual_time_spec_node = None

        # Item 0: Optional Keyword ([INPUT_KW | OUTPUT_KW])
        opt_kw_item = items[0]
        if isinstance(opt_kw_item, Token) and opt_kw_item.type in ["INPUT_KW", "OUTPUT_KW"]:
            stream_type_val = str(opt_kw_item.value).lower()
        elif opt_kw_item is not None:
            # If it's not None and not the expected token, it's an error.
            raise ValueError(f"stream_ref item 0: Expected INPUT_KW/OUTPUT_KW token or None, got {type(opt_kw_item)}: {opt_kw_item}")

        # Item 1: CNAME (Stream Name) - expected as string due to TceTransformer.CNAME
        cname_item = items[1]
        if isinstance(cname_item, str):
            cname_str = cname_item
        else:
            # This indicates a mismatch with grammar expectation or TceTransformer.CNAME behavior.
            raise ValueError(f"stream_ref item 1: Expected CNAME string, got {type(cname_item)}: {cname_item}")

        # Item 2, 3, 4: Optional Time Specification parts (LSQB, TimeSpecNode, RSQB)
        opt_lsqb_token = items[2]
        opt_ts_node = items[3]
        opt_rsqb_token = items[4]

        if opt_lsqb_token is not None:
            # If LSQB is present, TimeSpecNode and RSQB must also be present and valid
            if not (isinstance(opt_lsqb_token, Token) and opt_lsqb_token.type == "LSQB"):
                 raise ValueError(f"stream_ref item 2: Expected LSQB token or None, got {type(opt_lsqb_token)}: {opt_lsqb_token}")
            if not isinstance(opt_ts_node, TimeSpecNode):
                # This can happen if time_spec transformer returned None or something else
                raise ValueError(f"stream_ref item 3: Expected TimeSpecNode or None, got {type(opt_ts_node)}: {opt_ts_node} when LSQB is present.")
            if not (isinstance(opt_rsqb_token, Token) and opt_rsqb_token.type == "RSQB"):
                raise ValueError(f"stream_ref item 4: Expected RSQB token or None, got {type(opt_rsqb_token)}: {opt_rsqb_token} when LSQB is present.")
            actual_time_spec_node = opt_ts_node
        elif opt_ts_node is not None or opt_rsqb_token is not None:
            # If LSQB is None, but time_spec or RSQB are not, it's an inconsistent state.
            raise ValueError(f"stream_ref: LSQB is None, but time_spec ({opt_ts_node}) or RSQB ({opt_rsqb_token}) is not. Inconsistent items: {items}")

        return StreamReferenceNode(name=cname_str, time_spec=actual_time_spec_node, stream_type=stream_type_val)

    # ... rest of the code remains the same ...

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
        
        # Earley parser doesn't support embedded transformers, so we'll apply it separately
        self.parser = Lark(
            grammar_content,
            parser='earley', # Using Earley as it's robust for complex grammars
            start='start',
            ambiguity='resolve', # A common strategy for ambiguity
            debug=debug,
            import_paths=[str(grammar_dir)] # For %import in grammar
        )
        self.transformer = TceTransformer()

    def parse(self, text: str) -> ASTNode:
        """Parses a CNL string and returns the corresponding AST."""
        if not text.strip():
            raise ValueError("Input text cannot be empty or whitespace only.")
        try:
            # For Earley, the transformer might need to be applied after parsing if not done directly in constructor
            # Depending on Lark version and parser type, transformer can be passed to constructor or .transform() called explicitly.
            # If transformer is passed to Lark constructor, this should directly return the AST.
            # If not, it returns a parse tree, and TceTransformer().transform(tree) is needed.
            # Let's assume for now Lark handles it or we adjust if tree is returned.
            
            parse_tree = self.parser.parse(text)
            # If self.parser was initialized with transformer=TceTransformer(), 
            # then parse_tree here would actually be the transformed AST.
            # If not, we'd need: ast_result = TceTransformer().transform(parse_tree)
            # Given the previous structure often had explicit transform call, let's stick to that for clarity
            # unless Lark(..., transformer=...) with Earley directly returns AST.
            # For Earley, it's common to call transform separately.
            # Apply the transformer to convert parse tree to AST
            ast_result = self.transformer.transform(parse_tree)

            return ast_result
        except Exception as e:
            raise RuntimeError(f"Failed to parse CNL text: {e}") from e

# CNL Parser is ready for use
