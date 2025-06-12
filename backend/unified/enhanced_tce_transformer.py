"""
Enhanced TCE to Tau Transformer
Handles complex natural language patterns and converts them to Tau language.
Includes coreference resolution, scope management, and advanced transformations.

Copyright: DarkLightX / Dana Edwards
"""

from lark import Transformer, v_args, Token, Tree
import logging
from typing import Union, Optional, List, Dict, Any, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
from abc import ABC, abstractmethod


@dataclass
class Entity:
    """Represents an entity in the discourse."""
    id: str
    name: str
    type: str = "unknown"
    properties: Dict[str, Any] = field(default_factory=dict)
    first_mention: int = 0
    
@dataclass
class Scope:
    """Represents a quantifier scope."""
    quantifier: str  # all, ex
    variable: str
    domain: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    parent: Optional['Scope'] = None
    

class EnhancedTCETransformer(Transformer):
    """
    Enhanced transformer for complex TCE to Tau translation.
    Features:
    - Coreference resolution
    - Scope management for nested quantifiers
    - Relative clause handling
    - Complex sentence pattern recognition
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"{__class__.__module__}.{__class__.__name__}")
        
        # Entity tracking for coreference resolution
        self.entities: Dict[str, Entity] = {}
        self.entity_stack: List[str] = []  # Most recent entities
        self.pronoun_map: Dict[str, str] = {}  # Pronoun -> entity mapping
        
        # Scope management
        self.scope_stack: List[Scope] = []
        self.current_scope: Optional[Scope] = None
        
        # Sentence counter for discourse tracking
        self.sentence_count = 0
        
    # =========================================================================
    # Top-level rules
    # =========================================================================
    
    def specification(self, items):
        """Process complete specification."""
        return '\n'.join(filter(None, items))
    
    def spec_item(self, items):
        """Process individual specification item."""
        return items[0] if items else ""
    
    def tau_spec(self, items):
        """Process Tau specification."""
        if len(items) == 2 and isinstance(items[0], Token):
            # Temporal operator + spec
            operator = items[0].value.strip()
            spec = items[1]
            
            tau_op = {
                'always': '□',
                'sometimes': '◇', 
                'eventually': '◇'
            }.get(operator.lower(), operator)
            
            return f"{tau_op}({spec})"
        
        return items[0] if items else ""
    
    def spec_conjunction(self, items):
        """Process specification-level conjunction."""
        if len(items) >= 2:
            return f"({items[0]}) &&& ({items[1]})"
        return ""
    
    def spec_disjunction(self, items):
        """Process specification-level disjunction."""
        if len(items) >= 2:
            return f"({items[0]}) ||| ({items[1]})"
        return ""
    
    # =========================================================================
    # Local specifications
    # =========================================================================
    
    def local_spec(self, items):
        """Process local specification."""
        return items[0] if items else ""
    
    def boolean_expr(self, items):
        """Process boolean expression."""
        return items[0] if items else ""
    
    def and_expr(self, items):
        """Process AND expression."""
        if len(items) >= 2:
            return f"({items[0]}) && ({items[1]})"
        return items[0] if items else ""
    
    def or_expr(self, items):
        """Process OR expression."""
        if len(items) >= 2:
            return f"({items[0]}) || ({items[1]})"
        return items[0] if items else ""
    
    def not_expr(self, items):
        """Process NOT expression."""
        if items:
            return f"!({items[0]})"
        return ""
    
    def implies_expr(self, items):
        """Process implication."""
        if len(items) >= 2:
            return f"({items[0]}) -> ({items[1]})"
        return ""
    
    def iff_expr(self, items):
        """Process if-and-only-if."""
        if len(items) >= 2:
            return f"({items[0]}) <-> ({items[1]})"
        return ""
    
    # =========================================================================
    # Quantified formulas with scope management
    # =========================================================================
    
    def quantified_formula(self, items):
        """Process quantified formula."""
        return items[0] if items else ""
    
    def universal_formula(self, items):
        """Process universal quantification with scope tracking."""
        variables = []
        spec = ""
        
        for item in items:
            if isinstance(item, list):  # variable_list
                variables = item
            elif isinstance(item, str) and item not in ['all', 'for all', ',']:
                spec = item
        
        if variables and spec:
            # Create scope for each variable
            result_parts = []
            for var in variables:
                scope = Scope(quantifier='all', variable=var, parent=self.current_scope)
                self.scope_stack.append(scope)
                self.current_scope = scope
                result_parts.append(f"all {var}")
            
            # Build nested quantifiers
            result = ': '.join(result_parts) + f": {spec}"
            
            # Pop scopes
            for _ in variables:
                if self.scope_stack:
                    self.scope_stack.pop()
                    self.current_scope = self.scope_stack[-1] if self.scope_stack else None
            
            return result
        
        return ""
    
    def existential_formula(self, items):
        """Process existential quantification with scope tracking."""
        variables = []
        spec = ""
        
        for item in items:
            if isinstance(item, list):  # variable_list
                variables = item
            elif isinstance(item, str) and item not in ['exists', 'there exists', 'such that', ',']:
                spec = item
        
        if variables and spec:
            # Create scope for each variable
            result_parts = []
            for var in variables:
                scope = Scope(quantifier='ex', variable=var, parent=self.current_scope)
                self.scope_stack.append(scope)
                self.current_scope = scope
                result_parts.append(f"ex {var}")
            
            # Build nested quantifiers
            result = ': '.join(result_parts) + f": {spec}"
            
            # Pop scopes
            for _ in variables:
                if self.scope_stack:
                    self.scope_stack.pop()
                    self.current_scope = self.scope_stack[-1] if self.scope_stack else None
            
            return result
        
        return ""
    
    def variable_list(self, items):
        """Process list of variables."""
        return [str(item) for item in items if str(item) != ',']
    
    # =========================================================================
    # Comparisons
    # =========================================================================
    
    def comparison(self, items):
        """Process comparison with natural language support."""
        if len(items) >= 3:
            left = items[0]
            op = items[1]
            right = items[2]
            
            # Handle coreference in comparisons
            left = self._resolve_reference(str(left))
            right = self._resolve_reference(str(right))
            
            return f"{left} {op} {right}"
        return ""
    
    def comparison_op(self, items):
        """Process comparison operator."""
        if items and isinstance(items[0], Token):
            op_text = items[0].value.strip()
            
            # Map natural language to Tau operators
            op_map = {
                'equals': '=',
                'not equals': '!=',
                'less than': '<',
                'greater than': '>',
                'at most': '<=',
                'at least': '>=',
                '=': '=',
                '!=': '!=',
                '<': '<',
                '>': '>',
                '<=': '<=',
                '>=': '>='
            }
            
            return op_map.get(op_text, op_text)
        return "="
    
    # =========================================================================
    # Stream handling
    # =========================================================================
    
    def stream_equation(self, items):
        """Process stream equation."""
        if len(items) >= 2:
            stream = items[0]
            value = items[1]
            return f"{stream} = {value}"
        return ""
    
    def input_stream(self, items):
        """Process input stream reference."""
        stream_name = "1"  # default
        time_index = "[t]"  # default
        
        for item in items:
            if isinstance(item, str):
                if item.startswith('[') or item.startswith('t'):
                    time_index = item
                elif item not in ['input', 'input stream', 'at time']:
                    stream_name = item
        
        # Ensure time index is bracketed
        if not time_index.startswith('['):
            time_index = f"[{time_index}]"
            
        return f"i{stream_name}{time_index}"
    
    def output_stream(self, items):
        """Process output stream reference."""
        stream_name = "1"  # default
        time_index = "[t]"  # default
        
        for item in items:
            if isinstance(item, str):
                if item.startswith('[') or item.startswith('t'):
                    time_index = item
                elif item not in ['output', 'output stream', 'at time']:
                    stream_name = item
        
        # Ensure time index is bracketed
        if not time_index.startswith('['):
            time_index = f"[{time_index}]"
            
        return f"o{stream_name}{time_index}"
    
    def time_index(self, items):
        """Process time index."""
        if items:
            return f"[{items[0]}]"
        return "[t]"
    
    def time_expr(self, items):
        """Process time expression."""
        if not items:
            return "t"
        
        if len(items) == 1:
            # Simple: t or number
            return str(items[0])
        elif len(items) >= 3:
            # Complex: t-1, t+2, etc.
            base = str(items[0])
            op = str(items[1])
            offset = str(items[2])
            
            if op in ['-', 'minus']:
                return f"{base}-{offset}"
            elif op in ['+', 'plus']:
                return f"{base}+{offset}"
        
        return "t"
    
    # =========================================================================
    # Terms and expressions
    # =========================================================================
    
    def term(self, items):
        """Process term."""
        return items[0] if items else ""
    
    def arithmetic_expr(self, items):
        """Process arithmetic expression."""
        if len(items) >= 3:
            left = items[0]
            op_token = items[1]
            right = items[2]
            
            # Map operators
            op_map = {
                'plus': '+',
                'minus': '-',
                'times': '*',
                'divided by': '/',
                '+': '+',
                '-': '-',
                '*': '*',
                '/': '/'
            }
            
            op = op_map.get(str(op_token).strip(), '+')
            return f"({left} {op} {right})"
        
        return items[0] if items else ""
    
    # =========================================================================
    # Atomic elements
    # =========================================================================
    
    def atomic_prop(self, items):
        """Process atomic proposition."""
        if not items:
            return ""
        
        # Could be predicate(args) or just variable
        if len(items) == 1:
            return str(items[0])
        
        # Predicate with arguments
        predicate = str(items[0])
        if len(items) > 1 and isinstance(items[1], list):
            args = items[1]
            return f"{predicate}({', '.join(str(arg) for arg in args)})"
        
        return predicate
    
    def variable(self, items):
        """Process variable reference."""
        if items and isinstance(items[0], Token):
            var_name = str(items[0].value)
            
            # Check if it's a bound variable
            for scope in reversed(self.scope_stack):
                if scope.variable == var_name:
                    return var_name
            
            # Check if it's an entity reference
            if var_name in self.entities:
                return var_name
            
            # Check for pronouns and resolve coreference
            if var_name.lower() in ['it', 'he', 'she', 'they', 'the', 'that']:
                resolved = self._resolve_pronoun(var_name)
                if resolved:
                    return resolved
            
            return var_name
        
        return ""
    
    def number(self, items):
        """Process number."""
        if items and isinstance(items[0], Token):
            return str(items[0].value)
        return "0"
    
    # =========================================================================
    # Helper methods for complex features
    # =========================================================================
    
    def _resolve_pronoun(self, pronoun: str) -> str:
        """Resolve pronoun to its antecedent."""
        pronoun_lower = pronoun.lower()
        
        # Check explicit pronoun map first
        if pronoun_lower in self.pronoun_map:
            return self.pronoun_map[pronoun_lower]
        
        # Use recency heuristic - most recent matching entity
        if self.entity_stack:
            # For 'it', 'that' - refer to most recent entity
            if pronoun_lower in ['it', 'that', 'the']:
                return self.entity_stack[-1]
            
            # For gendered pronouns, try to match type
            # This is simplified - real system would use gender detection
            for entity_id in reversed(self.entity_stack):
                entity = self.entities.get(entity_id)
                if entity:
                    if pronoun_lower in ['he', 'him'] and entity.type == 'person':
                        return entity_id
                    elif pronoun_lower in ['she', 'her'] and entity.type == 'person':
                        return entity_id
                    elif pronoun_lower == 'they' and entity.type in ['people', 'persons']:
                        return entity_id
        
        # Fallback to pronoun itself
        return pronoun
    
    def _resolve_reference(self, ref: str) -> str:
        """Resolve any reference (pronoun or definite description)."""
        # Handle "the X" pattern
        if ref.startswith("the "):
            entity_type = ref[4:]  # Remove "the "
            
            # Find most recent entity of this type
            for entity_id in reversed(self.entity_stack):
                entity = self.entities.get(entity_id)
                if entity and entity.type == entity_type:
                    return entity_id
        
        # Try pronoun resolution
        resolved = self._resolve_pronoun(ref)
        if resolved != ref:
            return resolved
        
        return ref
    
    def _register_entity(self, name: str, entity_type: str = "unknown") -> str:
        """Register a new entity for tracking."""
        entity_id = f"{entity_type}_{len(self.entities)}"
        entity = Entity(
            id=entity_id,
            name=name,
            type=entity_type,
            first_mention=self.sentence_count
        )
        
        self.entities[entity_id] = entity
        self.entity_stack.append(entity_id)
        
        # Keep stack size manageable
        if len(self.entity_stack) > 10:
            self.entity_stack.pop(0)
        
        return entity_id
    
    # =========================================================================
    # Complex sentence patterns (for natural language input)
    # =========================================================================
    
    def handle_relative_clause(self, main_entity: str, relative_clause: str) -> str:
        """
        Handle relative clauses like "who owns a car".
        Returns constraint to add to quantifier.
        """
        # Parse patterns like "who owns X", "that has Y", "which contains Z"
        patterns = [
            (r'who\s+(\w+)\s+(.+)', r'\1(\2, {})'),  # who owns X -> owns(X, entity)
            (r'that\s+(\w+)\s+(.+)', r'\1(\2, {})'),  # that has Y -> has(Y, entity)
            (r'which\s+(\w+)\s+(.+)', r'\1(\2, {})'), # which contains Z -> contains(Z, entity)
        ]
        
        import re
        for pattern, template in patterns:
            match = re.match(pattern, relative_clause.strip(), re.IGNORECASE)
            if match:
                verb = match.group(1)
                object_phrase = match.group(2)
                
                # Register the object as an entity
                obj_entity = self._register_entity(object_phrase, self._guess_entity_type(object_phrase))
                
                # Create the constraint
                constraint = template.format(main_entity, obj_entity)
                return constraint
        
        return relative_clause
    
    def _guess_entity_type(self, phrase: str) -> str:
        """Guess entity type from phrase."""
        phrase_lower = phrase.lower()
        
        if any(word in phrase_lower for word in ['person', 'people', 'man', 'woman', 'user', 'customer', 'employee']):
            return 'person'
        elif any(word in phrase_lower for word in ['car', 'vehicle', 'truck']):
            return 'vehicle'
        elif any(word in phrase_lower for word in ['company', 'organization', 'firm']):
            return 'organization'
        elif any(word in phrase_lower for word in ['system', 'computer', 'server']):
            return 'system'
        else:
            return 'object'
    
    def transform_complex_sentence(self, sentence: str) -> str:
        """
        Transform complex English sentence to Tau.
        This is the main entry point for natural language.
        """
        # Increment sentence counter
        self.sentence_count += 1
        
        # Pattern: "for every X who Y, if Z then W"
        import re
        pattern1 = re.compile(
            r'for\s+every\s+(\w+)\s+who\s+([^,]+),\s*if\s+(.+?)\s+then\s+(.+)',
            re.IGNORECASE
        )
        match = pattern1.match(sentence)
        if match:
            entity_type = match.group(1)
            relative_clause = match.group(2)
            condition = match.group(3)
            consequence = match.group(4)
            
            # Create entity variable
            var = entity_type[0].lower()  # First letter as variable
            entity_id = self._register_entity(var, entity_type)
            
            # Handle relative clause
            constraint = self.handle_relative_clause(var, relative_clause)
            
            # Handle coreference in condition and consequence
            # "the car" -> refers to car from relative clause
            condition = self._resolve_complex_references(condition, entity_type, var)
            consequence = self._resolve_complex_references(consequence, entity_type, var)
            
            # Build Tau formula
            tau = f"all {var}: ({constraint} -> ({condition} -> {consequence}))"
            return tau
        
        # Pattern: "All X must Y"
        pattern2 = re.compile(r'all\s+(\w+)\s+must\s+(.+)', re.IGNORECASE)
        match = pattern2.match(sentence)
        if match:
            entity_type = match.group(1)
            action = match.group(2)
            
            var = entity_type[0].lower()
            tau = f"all {var}: {var}_type({var}) -> must_{action}({var})"
            return tau
        
        # Fallback to basic transformation
        return sentence
    
    def _resolve_complex_references(self, text: str, entity_type: str, variable: str) -> str:
        """Resolve references like 'the car' to the appropriate variable."""
        # Replace "the <entity_type>" with the variable
        text = re.sub(rf'\bthe\s+{entity_type}\b', variable, text, flags=re.IGNORECASE)
        
        # Replace pronouns
        text = re.sub(r'\bit\b', variable, text, flags=re.IGNORECASE)
        
        # Transform natural language operators
        text = text.replace(' is ', ' = ')
        text = text.replace(' are ', ' = ')
        text = text.replace(' has ', '_has_')
        text = text.replace(' must ', '_must_')
        
        return text


# =========================================================================
# Usage example and testing
# =========================================================================

def enhance_existing_parser():
    """
    Enhance the existing TCE parser with advanced features.
    This can be integrated into the existing parsing pipeline.
    """
    from lark import Lark
    import pathlib
    
    # Load the Tau-compatible grammar
    grammar_path = pathlib.Path(__file__).parent / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_tau_compatible.lark"
    
    with open(grammar_path, 'r') as f:
        grammar = f.read()
    
    # Create enhanced parser
    parser = Lark(grammar, start='specification', parser='lalr')
    transformer = EnhancedTCETransformer()
    
    # Test complex sentences
    test_sentences = [
        # Simple
        "always output 1 at time t equals input 1 at time t.",
        
        # Quantified
        "for all x, x greater than 0 implies x not equals 0.",
        
        # Complex with relative clause
        "for all person, person owns car implies person must have insurance.",
        
        # Stream processing
        "always input stream 1 at time t minus 1 equals 1 implies output stream 1 at time t equals 1.",
        
        # Nested quantifiers
        "for all x, there exists y such that y greater than x.",
        
        # Temporal with conditions
        "eventually input 1 at time t equals 1 and output 1 at time t equals 0."
    ]
    
    for sentence in test_sentences:
        print(f"\nInput: {sentence}")
        try:
            # For complex English, use the transformer's special method
            if "who" in sentence or "every" in sentence:
                tau = transformer.transform_complex_sentence(sentence)
            else:
                # For controlled English, use normal parsing
                tree = parser.parse(sentence)
                tau = transformer.transform(tree)
            
            print(f"Tau:   {tau}")
        except Exception as e:
            print(f"Error: {e}")
    
    return parser, transformer


if __name__ == "__main__":
    enhance_existing_parser()