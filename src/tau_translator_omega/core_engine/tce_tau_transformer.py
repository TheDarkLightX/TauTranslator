"""
TCE/Tau Lark Transformer
========================

Transforms between TCE (Tau Controlled English) and Tau language using Lark parse trees.
This transformer handles bidirectional translation between natural language and formal syntax.

Author: DarkLightX / Dana Edwards
"""

from lark import Transformer, v_args, Token, Tree
import logging
from typing import Union, Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class TCEToTauTransformer(Transformer):
    """
    Transforms TCE parse tree to Tau language syntax.
    
    This transformer converts natural language expressions parsed by the TCE grammar
    into formal Tau language syntax.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__class__.__module__}.{__class__.__name__}")
        
    # Top-level rules
    def start(self, items):
        """Combine all sentences."""
        return '\n'.join(filter(None, items))
    
    def sentence(self, items):
        """Process a single sentence."""
        # Remove sentence terminator and return the content
        return items[0] if items else ""
    
    def fact(self, items):
        """Process a fact (simple expression)."""
        return items[0] if items else ""
    
    def rule(self, items):
        """Process a rule (if-then statement)."""
        if len(items) >= 3:  # IF condition THEN action
            condition = items[1]
            action = items[2]
            return f"{condition} -> {action}"
        return ""
    
    def definition(self, items):
        """Process a definition."""
        if len(items) >= 3:  # DEFINE predicate AS expr
            predicate = items[1]
            expr = items[2]
            return f"{predicate} := {expr}"
        return ""
    
    def predicate_def(self, items):
        """Process predicate definition."""
        # Extract name and parameters
        name = None
        params = []
        
        for item in items:
            if isinstance(item, Token) and item.type == 'CNAME':
                if name is None:
                    name = str(item)
            elif isinstance(item, list):  # param_list
                params = item
                
        if params:
            return f"{name}({', '.join(params)})"
        return name or ""
    
    def predicate_call(self, items):
        """Process predicate call."""
        name = None
        args = []
        
        for item in items:
            if isinstance(item, Token) and item.type == 'CNAME':
                name = str(item)
            elif isinstance(item, list):  # arg_list
                args = item
                
        if args:
            return f"{name}({', '.join(args)})"
        return f"{name}()" if name else ""
    
    # Expression rules
    def expr(self, items):
        """Process top-level expression."""
        return items[0] if items else ""
    
    def or_expr(self, items):
        """Process OR expressions."""
        if len(items) > 1:
            return ' | '.join(str(item) for item in items if str(item) != 'or')
        return items[0] if items else ""
    
    def xor_expr(self, items):
        """Process XOR expressions."""
        if len(items) > 1:
            return ' ^ '.join(str(item) for item in items if str(item) != 'xor')
        return items[0] if items else ""
    
    def and_expr(self, items):
        """Process AND expressions."""
        if len(items) > 1:
            return ' & '.join(str(item) for item in items if str(item) != 'and')
        return items[0] if items else ""
    
    def comparison_expr(self, items):
        """Process comparison expressions."""
        if len(items) >= 3:
            left = items[0]
            op = items[1]
            right = items[2]
            return f"{left} {op} {right}"
        return items[0] if items else ""
    
    def arithmetic_expr(self, items):
        """Process arithmetic expressions."""
        result = str(items[0]) if items else ""
        i = 1
        while i < len(items) - 1:
            op = str(items[i])
            operand = str(items[i + 1])
            result = f"{result} {op} {operand}"
            i += 2
        return result
    
    def term(self, items):
        """Process multiplication/division terms."""
        result = str(items[0]) if items else ""
        i = 1
        while i < len(items) - 1:
            op = str(items[i])
            operand = str(items[i + 1])
            result = f"{result} {op} {operand}"
            i += 2
        return result
    
    def factor(self, items):
        """Process factors (possibly with unary operators)."""
        if len(items) == 2:  # Unary operator
            op = str(items[0])
            operand = str(items[1])
            if op == '-':
                return f"-{operand}"
            elif op == '+':
                return operand
        return items[0] if items else ""
    
    def atom(self, items):
        """Process atomic expressions."""
        return items[0] if items else ""
    
    # Literals and identifiers
    def constant(self, items):
        """Process constants."""
        return items[0] if items else ""
    
    def variable(self, items):
        """Process variables."""
        return str(items[0]) if items else ""
    
    def boolean_literal(self, items):
        """Process boolean literals."""
        value = str(items[0]).lower()
        return 'true' if value == 'true' else 'false'
    
    def stream_ref(self, items):
        """Process stream references."""
        stream_type = ""
        name = ""
        time_spec = ""
        
        for item in items:
            if isinstance(item, Token):
                if item.type in ['INPUT_KW', 'OUTPUT_KW']:
                    stream_type = 'i' if item.type == 'INPUT_KW' else 'o'
                elif item.type == 'CNAME':
                    name = str(item)
            elif isinstance(item, str):  # time_spec result
                time_spec = item
                
        if time_spec:
            return f"{stream_type}{name}[{time_spec}]"
        return f"{stream_type}{name}" if stream_type else name
    
    def time_spec(self, items):
        """Process time specifications."""
        if len(items) == 1:
            return str(items[0])
        elif len(items) == 3:  # t+1 or t-1
            var = str(items[0])
            op = str(items[1])
            num = str(items[2])
            return f"{var}{op}{num}"
        return "t"
    
    # Quantifiers
    def quant_block(self, items):
        """Process quantifier blocks."""
        quant_type = ""
        var_list = []
        condition = ""
        
        for item in items:
            if isinstance(item, Token):
                if item.type == 'FORALL_KW':
                    quant_type = 'forall'
                elif item.type == 'EXISTS_KW':
                    quant_type = 'exists'
            elif isinstance(item, list):  # var_list
                var_list = item
            elif isinstance(item, str):  # condition expression
                condition = item
                
        vars_str = ', '.join(var_list)
        if condition:
            return f"{quant_type} {vars_str} : {condition}"
        return f"{quant_type} {vars_str}"
    
    # Lists
    def var_list(self, items):
        """Process variable lists."""
        return [str(item) for item in items if isinstance(item, Token) and item.type == 'CNAME']
    
    def arg_list(self, items):
        """Process argument lists."""
        return [str(item) for item in items if str(item) != ',']
    
    def param_list(self, items):
        """Process parameter lists."""
        params = []
        for item in items:
            if hasattr(item, '__iter__') and not isinstance(item, str):
                # This is a param
                param_str = self._process_param(item)
                if param_str:
                    params.append(param_str)
        return params
    
    def param(self, items):
        """Process a single parameter."""
        return self._process_param(items)
    
    def _process_param(self, items):
        """Helper to process parameter with optional type."""
        if not items:
            return ""
        name = str(items[0])
        if len(items) >= 3:  # Has type annotation
            param_type = str(items[2])
            return f"{name}: {param_type}"
        return name
    
    # Token handlers
    def NUMBER(self, token):
        """Process number tokens."""
        return str(token)
    
    def ESCAPED_STRING(self, token):
        """Process string tokens."""
        return str(token)
    
    def CNAME(self, token):
        """Process identifier tokens."""
        return str(token)
    
    def COMPARISON_OP(self, token):
        """Process comparison operators."""
        return str(token)
    
    def ARITHMETIC_OP(self, token):
        """Process arithmetic operators."""
        return str(token)


class TauToTCETransformer(Transformer):
    """
    Transforms Tau parse tree to TCE (natural language).
    
    This transformer converts formal Tau syntax parsed by a Tau grammar
    into natural language TCE expressions.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__class__.__module__}.{__class__.__name__}")
        
    # This would need to be implemented based on the Tau grammar structure
    # For now, we'll provide a placeholder that shows the pattern
    
    def start(self, items):
        """Combine all statements."""
        return '\n'.join(filter(None, items))
    
    def statement(self, items):
        """Process a single Tau statement."""
        # This would convert Tau statements to TCE sentences
        return f"{items[0]}." if items else ""
    
    # Additional methods would be implemented based on Tau grammar rules
    # The pattern would be to convert formal syntax to natural language