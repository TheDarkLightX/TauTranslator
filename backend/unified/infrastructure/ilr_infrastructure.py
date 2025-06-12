"""
ILR infrastructure layer following the Intentional Disclosure Principle.

Isolates all pattern matching, parsing, and I/O operations
from business logic according to IDP Rule 4.

Copyright: DarkLightX / Dana Edwards
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from ..core.result_enhanced import Result, Success, Failure

from ..domain.ilr_types import (
    PatternType, PatternMatch, ExpressionText, VariableName,
    TemporalOffset, ComparisonOperator, LogicalOperator,
    ArithmeticOperator
)

logger = logging.getLogger(__name__)


class PatternMatcher:
    """Matches natural language patterns for ILR translation."""
    
    # Pattern definitions
    PATTERNS = {
        PatternType.PREDICATE_DEFINITION: re.compile(
            r'^(?:for any|for all)\s+(\w+(?:\s*,\s*\w+)*),\s*predicate\s+(\w+)\(([^)]+)\)\s+is\s+(.+)\.$'
        ),
        PatternType.FUNCTION_DEFINITION: re.compile(
            r'^function\s+(\w+)\(([^)]+)\)\s+(?:returns?|is)\s+(.+)\.$'
        ),
        PatternType.UNIVERSAL: re.compile(
            r'^for\s+(?:all|every)\s+(\w+)(?:\s*,\s*(\w+))?,\s*(.+)\.$'
        ),
        PatternType.EXISTENTIAL: re.compile(
            r'^(?:there\s+)?exists?\s+(?:an?\s+)?(\w+)(?:\s*(?:and|,)\s*(?:an?\s+)?(\w+))?\s+(?:such\s+that\s+)?(.+)\.$'
        ),
        PatternType.CONDITIONAL: re.compile(
            r'^if\s+(.+?)\s+then\s+(.+)\.$'
        ),
        PatternType.ASSIGNMENT: re.compile(
            r'^(\w+)\s*(?:is|=)\s*(.+)\.$'
        ),
        PatternType.BOOLEAN_EXPR: re.compile(
            r'^(.+)\.$'
        ),
        PatternType.NEGATION: re.compile(
            r'^(?:it\s+is\s+)?not\s+(?:the\s+case\s+that\s+)?(.+)\.$'
        ),
        PatternType.STREAM_ASSIGNMENT: re.compile(
            r'^stream\s+(\w+)\s+at\s+time\s+t\s*(?:is|=)\s*(.+)\.$'
        ),
        PatternType.SBF_INPUT: re.compile(
            r'^sbf_input\((.*)\)\.$'
        ),
        PatternType.SBF_OUTPUT: re.compile(
            r'^sbf_output\((.*)\)\.$'
        ),
        PatternType.STREAM_RULE: re.compile(
            r'^(\w+\[t(?:[+-]\d+)?\])\s*=\s*(.+)\.$'
        ),
        PatternType.TEMPORAL_ALWAYS: re.compile(
            r'^always\s+(.+)\.$'
        )
    }
    
    @classmethod
    def match_pattern(cls, text: str) -> Result[PatternMatch]:
        """Match text against all patterns and return the best match."""
        normalized_text = text.strip()
        
        # Try each pattern in order of specificity
        pattern_order = [
            PatternType.SBF_INPUT,
            PatternType.SBF_OUTPUT,
            PatternType.STREAM_RULE,
            PatternType.PREDICATE_DEFINITION,
            PatternType.FUNCTION_DEFINITION,
            PatternType.TEMPORAL_ALWAYS,
            PatternType.UNIVERSAL,
            PatternType.EXISTENTIAL,
            PatternType.NEGATION,
            PatternType.CONDITIONAL,
            PatternType.STREAM_ASSIGNMENT,
            PatternType.ASSIGNMENT,
            PatternType.BOOLEAN_EXPR  # Most generic, try last
        ]
        
        for pattern_type in pattern_order:
            pattern = cls.PATTERNS[pattern_type]
            match = pattern.match(normalized_text)
            
            if match:
                matched_groups = {
                    f"group_{i}": group 
                    for i, group in enumerate(match.groups()) 
                    if group is not None
                }
                
                logger.debug(f"Matched pattern {pattern_type.value}: {matched_groups}")
                return Success(PatternMatch(
                    pattern_type=pattern_type,
                    matched_groups=matched_groups,
                    confidence=1.0
                ))
        
        return Failure(f"No pattern matched for text: {text}")
    
    @classmethod
    def extract_pattern_components(cls, pattern_match: PatternMatch) -> Dict[str, str]:
        """Extract named components from pattern match."""
        components = {}
        
        if pattern_match.pattern_type == PatternType.PREDICATE_DEFINITION:
            components['quantifier_vars'] = pattern_match.matched_groups.get('group_0', '')
            components['predicate_name'] = pattern_match.matched_groups.get('group_1', '')
            components['parameters'] = pattern_match.matched_groups.get('group_2', '')
            components['body'] = pattern_match.matched_groups.get('group_3', '')
            
        elif pattern_match.pattern_type == PatternType.FUNCTION_DEFINITION:
            components['function_name'] = pattern_match.matched_groups.get('group_0', '')
            components['parameters'] = pattern_match.matched_groups.get('group_1', '')
            components['body'] = pattern_match.matched_groups.get('group_2', '')
            
        elif pattern_match.pattern_type == PatternType.UNIVERSAL:
            components['variable1'] = pattern_match.matched_groups.get('group_0', '')
            components['variable2'] = pattern_match.matched_groups.get('group_1', '')
            components['condition'] = pattern_match.matched_groups.get('group_2', '')
            
        elif pattern_match.pattern_type == PatternType.EXISTENTIAL:
            components['variable1'] = pattern_match.matched_groups.get('group_0', '')
            components['variable2'] = pattern_match.matched_groups.get('group_1', '')
            components['condition'] = pattern_match.matched_groups.get('group_2', '')
            
        elif pattern_match.pattern_type == PatternType.CONDITIONAL:
            components['condition'] = pattern_match.matched_groups.get('group_0', '')
            components['consequence'] = pattern_match.matched_groups.get('group_1', '')
            
        elif pattern_match.pattern_type == PatternType.ASSIGNMENT:
            components['variable'] = pattern_match.matched_groups.get('group_0', '')
            components['value'] = pattern_match.matched_groups.get('group_1', '')
            
        elif pattern_match.pattern_type == PatternType.NEGATION:
            components['expression'] = pattern_match.matched_groups.get('group_0', '')
            
        elif pattern_match.pattern_type == PatternType.STREAM_ASSIGNMENT:
            components['stream_name'] = pattern_match.matched_groups.get('group_0', '')
            components['value'] = pattern_match.matched_groups.get('group_1', '')
            
        elif pattern_match.pattern_type == PatternType.STREAM_RULE:
            components['left_side'] = pattern_match.matched_groups.get('group_0', '')
            components['right_side'] = pattern_match.matched_groups.get('group_1', '')
            
        elif pattern_match.pattern_type == PatternType.TEMPORAL_ALWAYS:
            components['expression'] = pattern_match.matched_groups.get('group_0', '')
            
        elif pattern_match.pattern_type == PatternType.BOOLEAN_EXPR:
            components['expression'] = pattern_match.matched_groups.get('group_0', '')
            
        return components


class ExpressionTokenizer:
    """Tokenizes expressions for parsing."""
    
    # Token patterns
    TOKEN_PATTERNS = [
        ('NUMBER', r'-?\d+(?:\.\d+)?'),
        ('BOOL', r'\b(?:true|false)\b'),
        ('TEMPORAL_REF', r'\w+\[t(?:[+-]\d+)?\]'),
        ('IDENTIFIER', r'\w+'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('COMMA', r','),
        ('COMPLEMENT', r"'"),
        
        # Operators (order matters for multi-character ops)
        ('LEQ', r'<='),
        ('GEQ', r'>='),
        ('NEQ', r'!='),
        ('EQ', r'==?'),
        ('LT', r'<'),
        ('GT', r'>'),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        ('TIMES', r'\*'),
        ('DIVIDE', r'/'),
        ('MOD', r'%'),
        ('POWER', r'\^'),
        
        # Logical operators
        ('AND', r'\band\b'),
        ('OR', r'\bor\b'),
        ('XOR', r'\bxor\b'),
        ('NOT', r'\bnot\b'),
        ('IMPLIES', r'\bimplies\b'),
        
        # Skip whitespace
        ('SKIP', r'[ \t]+'),
    ]
    
    @classmethod
    def tokenize(cls, text: str) -> Result[List[Tuple[str, str]], str]:
        """Tokenize expression text."""
        tokens = []
        position = 0
        
        while position < len(text):
            match_found = False
            
            for token_name, pattern in cls.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(text, position)
                
                if match:
                    value = match.group(0)
                    if token_name != 'SKIP':
                        tokens.append((token_name, value))
                    position = match.end()
                    match_found = True
                    break
            
            if not match_found:
                return Failure(f"Invalid token at position {position}: '{text[position:]}'")
        
        return Success(tokens)


class TemporalReferenceParser:
    """Parses temporal references like o1[t-1]."""
    
    TEMPORAL_PATTERN = re.compile(r'^(\w+)\[t([+-]\d+)?\]$')
    
    @classmethod
    def parse_temporal_reference(cls, text: str) -> Result[Tuple[VariableName, TemporalOffset]]:
        """Parse temporal reference and extract variable name and offset."""
        match = cls.TEMPORAL_PATTERN.match(text.strip())
        
        if not match:
            return Failure(f"Invalid temporal reference: {text}")
        
        var_name = match.group(1)
        offset_str = match.group(2) or "0"
        
        try:
            offset = int(offset_str)
            return Success((VariableName(var_name), TemporalOffset(offset)))
        except ValueError:
            return Failure(f"Invalid temporal offset: {offset_str}")


class ParenthesesSplitter:
    """Splits text while respecting parentheses."""
    
    @staticmethod
    def split_respecting_parens(text: str, delimiter: str) -> List[str]:
        """Split text by delimiter while respecting parentheses."""
        parts = []
        current_part = []
        paren_depth = 0
        
        # Tokenize to handle delimiter properly
        tokens = text.split()
        
        for token in tokens:
            # Count parentheses in token
            paren_depth += token.count('(') - token.count(')')
            
            if token == delimiter and paren_depth == 0:
                if current_part:
                    parts.append(' '.join(current_part))
                    current_part = []
            else:
                current_part.append(token)
        
        # Add final part
        if current_part:
            parts.append(' '.join(current_part))
        
        return parts


class OperatorMapper:
    """Maps operator strings to enum values."""
    
    COMPARISON_MAP = {
        '=': ComparisonOperator.EQ,
        '==': ComparisonOperator.EQ,
        '!=': ComparisonOperator.NEQ,
        '<': ComparisonOperator.LT,
        '<=': ComparisonOperator.LTE,
        '>': ComparisonOperator.GT,
        '>=': ComparisonOperator.GTE,
    }
    
    LOGICAL_MAP = {
        'and': LogicalOperator.AND,
        'or': LogicalOperator.OR,
        'xor': LogicalOperator.XOR,
        'not': LogicalOperator.NOT,
        'implies': LogicalOperator.IMPLIES,
    }
    
    ARITHMETIC_MAP = {
        '+': ArithmeticOperator.ADD,
        '-': ArithmeticOperator.SUB,
        '*': ArithmeticOperator.MUL,
        '/': ArithmeticOperator.DIV,
        '%': ArithmeticOperator.MOD,
        ' mod ': ArithmeticOperator.MOD,
        'mod': ArithmeticOperator.MOD,
        '^': ArithmeticOperator.POW,
    }
    
    TAU_OPERATOR_MAP = {
        ComparisonOperator.EQ: '=',
        ComparisonOperator.NEQ: '!=',
        ComparisonOperator.LT: '<',
        ComparisonOperator.LTE: '<=',
        ComparisonOperator.GT: '>',
        ComparisonOperator.GTE: '>=',
        LogicalOperator.AND: '&',
        LogicalOperator.OR: '|',
        LogicalOperator.XOR: '^',
        LogicalOperator.NOT: '!',
        LogicalOperator.IMPLIES: '->',
        ArithmeticOperator.ADD: '+',
        ArithmeticOperator.SUB: '-',
        ArithmeticOperator.MUL: '*',
        ArithmeticOperator.DIV: '/',
        ArithmeticOperator.MOD: '%',
        ArithmeticOperator.POW: '^',
    }
    
    @classmethod
    def map_comparison_operator(cls, op_str: str) -> Result[ComparisonOperator]:
        """Map string to comparison operator."""
        op = cls.COMPARISON_MAP.get(op_str)
        if op is None:
            return Failure(f"Unknown comparison operator: {op_str}")
        return Success(op)
    
    @classmethod
    def map_logical_operator(cls, op_str: str) -> Result[LogicalOperator]:
        """Map string to logical operator."""
        op = cls.LOGICAL_MAP.get(op_str.lower())
        if op is None:
            return Failure(f"Unknown logical operator: {op_str}")
        return Success(op)
    
    @classmethod
    def map_arithmetic_operator(cls, op_str: str) -> Result[ArithmeticOperator]:
        """Map string to arithmetic operator."""
        op = cls.ARITHMETIC_MAP.get(op_str)
        if op is None:
            return Failure(f"Unknown arithmetic operator: {op_str}")
        return Success(op)
    
    @classmethod
    def get_tau_operator(cls, operator: Union[ComparisonOperator, LogicalOperator, ArithmeticOperator]) -> str:
        """Get TAU representation of operator."""
        return cls.TAU_OPERATOR_MAP.get(operator, str(operator.value))


class JsonSerializer:
    """Handles JSON serialization for ILR."""
    
    @staticmethod
    def serialize_ilr(ilr_dict: Dict[str, Any]) -> Result[str]:
        """Serialize ILR dictionary to JSON string."""
        try:
            json_str = json.dumps(ilr_dict, indent=2)
            return Success(json_str)
        except (TypeError, ValueError) as e:
            return Failure(f"Failed to serialize ILR to JSON: {e}")
    
    @staticmethod
    def deserialize_ilr(json_str: str) -> Result[Dict[str, Any]]:
        """Deserialize JSON string to ILR dictionary."""
        try:
            ilr_dict = json.loads(json_str)
            return Success(ilr_dict)
        except json.JSONDecodeError as e:
            return Failure(f"Failed to parse ILR JSON: {e}")


class TextAnalyzer:
    """Analyzes text for linguistic patterns."""
    
    @staticmethod
    def analyze_sentence_structure(text: str) -> Dict[str, Any]:
        """Analyze basic sentence structure."""
        analysis = {
            'has_if_then': 'if ' in text and ' then ' in text,
            'has_comparison': any(op in text for op in ['equals', 'is greater than', 'is less than']),
            'has_definition': any(pattern in text for pattern in [' is ', ' equals ', ' is defined as ']),
            'has_quantifier': any(q in text for q in ['for all', 'for every', 'exists', 'there is'])
        }
        return analysis


class SentenceClassifier:
    """Classifies sentences by type."""
    
    def classify(self, text: str) -> str:
        """Classify sentence type based on patterns."""
        analysis = TextAnalyzer.analyze_sentence_structure(text)
        
        if analysis['has_if_then']:
            return 'conditional'
        elif analysis['has_comparison']:
            return 'comparison'
        elif analysis['has_definition']:
            return 'definition'
        elif analysis['has_quantifier']:
            return 'quantified'
        else:
            return 'fact'


class ValidationHelper:
    """Provides validation utilities."""
    
    @staticmethod
    def ensure_period_at_end(text: str) -> str:
        """Ensure text ends with a period."""
        text = text.strip()
        if not text.endswith('.'):
            text += '.'
        return text
    
    @staticmethod
    def is_valid_identifier(name: str) -> bool:
        """Check if name is a valid identifier."""
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))
    
    @staticmethod
    def parse_parameter_list(params_str: str) -> List[str]:
        """Parse comma-separated parameter list."""
        if not params_str.strip():
            return []
        
        return [p.strip() for p in params_str.split(',') if p.strip()]
    
    @staticmethod
    def extract_parentheses_content(text: str) -> Tuple[str, str]:
        """Extract content within outermost parentheses."""
        depth = 0
        start_idx = -1
        
        for i, char in enumerate(text):
            if char == '(':
                if depth == 0:
                    start_idx = i
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0 and start_idx >= 0:
                    return text[:start_idx], text[start_idx+1:i]
        
        return text, ""