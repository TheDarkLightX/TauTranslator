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
        # Filter out parentheses and extract name and args
        name = None
        args = []
        
        for item in items:
            if item is not None:
                item_str = str(item)
                if item_str not in ['(', ')']:
                    if isinstance(item, list):  # arg_list
                        args = item
                    elif name is None:  # First non-paren item is the name
                        name = item_str
                
        if args:
            return f"{name}({', '.join(str(arg) for arg in args)})"
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
        # Filter out None values from optional unary operators
        non_none_items = [item for item in items if item is not None]
        
        if len(non_none_items) == 2:  # Unary operator
            op = str(non_none_items[0])
            operand = str(non_none_items[1])
            if op == '-':
                return f"-{operand}"
            elif op == '+':
                return operand
        return non_none_items[0] if non_none_items else ""
    
    def atom(self, items):
        """Process atomic expressions."""
        return items[0] if items else ""
    
    def conditional_expr(self, items):
        """Process conditional if-then-else expressions."""
        # Filter out keyword tokens
        non_keyword_items = []
        for item in items:
            if item is not None:
                item_str = str(item).lower()
                if item_str not in ['if', 'then', 'else']:
                    non_keyword_items.append(item)
        
        if len(non_keyword_items) >= 3:  # condition, then_expr, else_expr
            condition = non_keyword_items[0]
            then_expr = non_keyword_items[1]
            else_expr = non_keyword_items[2]
            return f"({condition} ? {then_expr} : {else_expr})"
        return items[0] if items else ""
    
    # Literals and identifiers
    def literal(self, items):
        """Process literal values (new grammar rule)."""
        return items[0] if items else ""
    
    def identifier(self, items):
        """Process identifiers (new grammar rule)."""
        return str(items[0]) if items else ""
    
    # Keep backward compatibility
    def constant(self, items):
        """Process constants (legacy)."""
        return items[0] if items else ""
    
    def variable(self, items):
        """Process variables (legacy)."""
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
    
    # Quantifiers - updated for new grammar
    def quantifier_expr(self, items):
        """Process quantifier expressions (new grammar rule)."""
        # Separate the components based on structure
        quant_token = None
        var_list = None
        condition = None
        
        # Filter items and categorize them
        for item in items:
            if item is None:
                continue
            item_str = str(item).lower()
            
            # Skip keywords
            if item_str in [':', 'such', 'that']:
                continue
            
            # Determine the type of item
            if item_str in ['forall', 'exists']:
                quant_token = item
            elif isinstance(item, list):  # var_list result
                var_list = item
            elif quant_token is not None and var_list is not None:
                # This should be the condition expression
                condition = item
                break
        
        # Determine quantifier symbol
        if quant_token:
            quant_str = str(quant_token).lower()
            if 'forall' in quant_str:
                quant_type = '∀'
            elif 'exists' in quant_str:
                quant_type = '∃'
            else:
                quant_type = str(quant_token)
        else:
            quant_type = '?'
        
        # Format variable list
        if isinstance(var_list, list):
            vars_str = ', '.join(str(v) for v in var_list)
        else:
            vars_str = str(var_list) if var_list else '?'
        
        # Return formatted quantifier expression
        if condition:
            return f"{quant_type}{vars_str}: {condition}"
        else:
            return f"{quant_type}{vars_str}"
    
    # Keep backward compatibility
    def quant_block(self, items):
        """Process quantifier blocks (legacy)."""
        return self.quantifier_expr(items)
    
    # Lists
    def var_list(self, items):
        """Process variable lists."""
        # Filter out comma tokens and process identifiers
        variables = []
        for item in items:
            if item is not None and str(item) != ',':
                variables.append(str(item))
        return variables
    
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