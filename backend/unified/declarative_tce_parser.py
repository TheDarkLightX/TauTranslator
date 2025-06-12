"""
Declarative TCE Parser - Enhanced parser for declarative Tau Controlled English
Integrates with existing TCE infrastructure while adding advanced features.

Copyright: DarkLightX / Dana Edwards
"""

import pathlib
from lark import Lark, Transformer, v_args, Token, Tree
from typing import List, Union, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
import logging
from abc import ABC, abstractmethod

# Import existing AST nodes
from src.tau_translator_omega.core_engine.cnl_parser.ast_nodes import (
    ASTNode, ExprNode, QuantifierBlockNode, VariableNode, 
    ConstantNode, PredicateCallNode, ComparisonNode
)


@dataclass
class DeclarativeContext:
    """Context for declarative parsing."""
    entities: Dict[str, 'EntityInfo'] = field(default_factory=dict)
    properties: Dict[str, List[str]] = field(default_factory=dict)
    relationships: List['RelationshipInfo'] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    temporal_properties: List['TemporalProperty'] = field(default_factory=list)


@dataclass  
class EntityInfo:
    """Information about an entity in the specification."""
    name: str
    entity_class: str
    properties: List[str] = field(default_factory=list)
    relationships: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class RelationshipInfo:
    """Information about a relationship."""
    subject: str
    relation: str
    object: str
    quantified: bool = False


@dataclass
class TemporalProperty:
    """Temporal property declaration."""
    quantifier: str  # always, eventually, etc.
    property: str
    stream_refs: List[str] = field(default_factory=list)


class DeclarativeTCETransformer(Transformer):
    """
    Transformer for declarative TCE that produces Tau code.
    Focuses on declarative patterns and clear semantics.
    """
    
    def __init__(self, visit_tokens=True):
        super().__init__(visit_tokens=visit_tokens)
        self.context = DeclarativeContext()
        self.logger = logging.getLogger(__name__)
        
    # =========================================================================
    # Top-level rules
    # =========================================================================
    
    def specification(self, items):
        """Process complete specification."""
        declarations = [item for item in items if item]
        
        # Combine all declarations into a Tau specification
        tau_parts = []
        
        # First, output definitions
        for decl in declarations:
            if isinstance(decl, dict) and decl.get('type') == 'definition':
                tau_parts.append(decl['tau'])
        
        # Then constraints and properties
        for decl in declarations:
            if isinstance(decl, dict) and decl.get('type') in ['constraint', 'property']:
                tau_parts.append(decl['tau'])
        
        # Finally, temporal properties
        for decl in declarations:
            if isinstance(decl, dict) and decl.get('type') == 'temporal':
                tau_parts.append(decl['tau'])
        
        # Join with appropriate separators
        return ' &&& '.join(tau_parts) if tau_parts else ""
    
    def declaration(self, items):
        """Process a single declaration."""
        if items:
            return items[0]
        return None
    
    def declarative_statement(self, items):
        """Process declarative statement."""
        if items:
            return items[0]
        return None
    
    # =========================================================================
    # Facts and Properties
    # =========================================================================
    
    def fact(self, items):
        """Process fact declaration."""
        if not items:
            return None
            
        # Different fact patterns
        if len(items) >= 3:
            # entity IS/HAS property or term op term
            subject = items[0]
            operator = items[1]
            object = items[2]
            
            if isinstance(operator, Token):
                op_type = operator.type
                if op_type in ['IS', 'ARE']:
                    # Entity is property
                    tau = f"{subject}_is_{object}"
                    return {'type': 'property', 'tau': tau}
                elif op_type in ['HAS', 'HAVE']:
                    # Entity has property
                    tau = f"has({subject}, {object})"
                    return {'type': 'property', 'tau': tau}
                else:
                    # Comparison
                    tau = f"{subject} {self._map_comparison_op(operator)} {object}"
                    return {'type': 'constraint', 'tau': tau}
        
        elif len(items) == 2:
            # entity property (shorthand)
            entity = items[0]
            property = items[1]
            tau = f"{entity}_{property}"
            return {'type': 'property', 'tau': tau}
        
        return None
    
    def property_declaration(self, items):
        """Process property declaration."""
        if items:
            return items[0]
        return None
    
    def quantified_property(self, items):
        """Process quantified property like 'all persons are mortal'."""
        quantifier = None
        entity_class = None
        property_clause = None
        
        for item in items:
            if isinstance(item, Token):
                if item.type in ['ALL', 'EVERY', 'EACH', 'NO', 'SOME']:
                    quantifier = item.value.strip()
                else:
                    entity_class = item.value
            elif isinstance(item, dict):
                property_clause = item
        
        if quantifier and entity_class and property_clause:
            # Map to Tau quantifier
            tau_quantifier = {
                'all': 'all',
                'every': 'all', 
                'each': 'all',
                'no': 'all',  # with negation
                'some': 'ex'
            }.get(quantifier.lower(), 'all')
            
            var = entity_class[0].lower()  # First letter as variable
            
            if quantifier.lower() == 'no':
                # "no X is Y" -> "all x: is_X(x) -> !is_Y(x)"
                tau = f"{tau_quantifier} {var}: is_{entity_class}({var}) -> !{property_clause['tau']}"
            else:
                # "all X are Y" -> "all x: is_X(x) -> is_Y(x)"
                tau = f"{tau_quantifier} {var}: is_{entity_class}({var}) -> {property_clause['tau']}"
            
            return {'type': 'property', 'tau': tau}
        
        return None
    
    def property_clause(self, items):
        """Process property clause like 'is mortal' or 'has wheels'."""
        if len(items) >= 2:
            verb = items[0]
            property = items[1]
            
            if isinstance(verb, Token):
                if verb.type in ['IS', 'ARE']:
                    return {'tau': f"is_{property}"}
                elif verb.type in ['HAS', 'HAVE']:
                    return {'tau': f"has_{property}"}
        
        return {'tau': str(items[-1]) if items else "true"}
    
    # =========================================================================
    # Relationships
    # =========================================================================
    
    def relationship(self, items):
        """Process relationship declaration."""
        if len(items) >= 3:
            subject = items[0]
            relation = items[1]
            object = items[2]
            
            # Store relationship info
            rel_info = RelationshipInfo(
                subject=str(subject),
                relation=str(relation),
                object=str(object)
            )
            self.context.relationships.append(rel_info)
            
            # Generate Tau
            tau = f"{relation}({subject}, {object})"
            return {'type': 'property', 'tau': tau}
        
        return None
    
    def quantified_relationship(self, items):
        """Process quantified relationship like 'every person owns some car'."""
        quantifier = None
        entity_class = None
        relation_clause = None
        
        for item in items:
            if isinstance(item, Token):
                if item.type in ['ALL', 'EVERY', 'EACH', 'SOME']:
                    quantifier = item.value.strip()
                else:
                    entity_class = item.value
            elif isinstance(item, dict):
                relation_clause = item
        
        if quantifier and entity_class and relation_clause:
            tau_quantifier = 'all' if quantifier.lower() in ['all', 'every', 'each'] else 'ex'
            var = entity_class[0].lower()
            
            tau = f"{tau_quantifier} {var}: is_{entity_class}({var}) -> {relation_clause['tau']}"
            return {'type': 'property', 'tau': tau}
        
        return None
    
    # =========================================================================
    # Constraints
    # =========================================================================
    
    def constraint(self, items):
        """Process constraint declaration."""
        constraint_expr = None
        
        for item in items:
            if isinstance(item, dict) or isinstance(item, str):
                constraint_expr = item
                break
        
        if constraint_expr:
            tau = constraint_expr['tau'] if isinstance(constraint_expr, dict) else str(constraint_expr)
            return {'type': 'constraint', 'tau': tau}
        
        return None
    
    def constraint_expr(self, items):
        """Process constraint expression."""
        if items:
            return items[0]
        return None
    
    # =========================================================================
    # Temporal Properties
    # =========================================================================
    
    def temporal_property(self, items):
        """Process temporal property declaration."""
        if len(items) >= 2:
            quantifier = items[0]
            property = items[1]
            
            # Map temporal quantifiers to Tau
            tau_op = {
                'always': '□',
                'eventually': '◇',
                'sometimes': '◇',
                'never': '□!'  # always not
            }.get(str(quantifier).lower(), '□')
            
            if tau_op == '□!':
                # Handle 'never' as 'always not'
                tau = f"□(!({property['tau']}))"
            else:
                tau = f"{tau_op}({property['tau']})"
            
            return {'type': 'temporal', 'tau': tau}
        
        return None
    
    def stream_property(self, items):
        """Process stream property like 'output 1 at time t equals input 1 at time t'."""
        if len(items) >= 2:
            stream = items[0]
            
            if len(items) >= 3 and items[1] == 'equals':
                value = items[2]
                tau = f"{stream} = {value}"
            else:
                # satisfies constraint
                constraint = items[1]
                tau = f"satisfies({stream}, {constraint})"
            
            return {'tau': tau}
        
        return None
    
    # =========================================================================
    # Stream handling
    # =========================================================================
    
    def stream_term(self, items):
        """Process stream term."""
        stream_type = None
        stream_id = "1"
        time_ref = "[t]"
        
        for item in items:
            if isinstance(item, Token):
                if item.type in ['INPUT', 'OUTPUT']:
                    stream_type = item.value.strip().lower()
                else:
                    stream_id = item.value
            elif isinstance(item, str) and (item.startswith('[') or item.startswith('at')):
                time_ref = item
        
        if stream_type:
            prefix = 'i' if stream_type == 'input' else 'o'
            
            # Clean up time reference
            if time_ref.startswith('at '):
                time_ref = time_ref[3:]
            if not time_ref.startswith('['):
                time_ref = f"[{time_ref}]"
            
            return f"{prefix}{stream_id}{time_ref}"
        
        return ""
    
    def time_reference(self, items):
        """Process time reference."""
        if items:
            time_expr = items[-1]  # Get the actual time expression
            return f"[{time_expr}]"
        return "[t]"
    
    def time_expr(self, items):
        """Process time expression."""
        if not items:
            return "t"
        
        if len(items) == 1:
            return str(items[0])
        elif len(items) >= 3:
            # t +/- offset
            base = str(items[0])
            op = str(items[1]).strip()
            offset = str(items[2])
            
            if op in ['-', 'minus']:
                return f"{base}-{offset}"
            elif op in ['+', 'plus']:
                return f"{base}+{offset}"
        
        return "t"
    
    # =========================================================================
    # Definitions
    # =========================================================================
    
    def definition(self, items):
        """Process definition."""
        entity_class = None
        definition_body = None
        
        for item in items:
            if isinstance(item, str) and not entity_class:
                entity_class = item
            elif isinstance(item, dict):
                definition_body = item
        
        if entity_class and definition_body:
            tau = f"{entity_class} := {definition_body['tau']}"
            return {'type': 'definition', 'tau': tau}
        
        return None
    
    # =========================================================================
    # Logical expressions
    # =========================================================================
    
    def logical_expr(self, items):
        """Process logical expression."""
        if not items:
            return {'tau': 'true'}
        
        if len(items) == 1:
            return items[0]
        
        # Binary operators
        if len(items) >= 3:
            left = items[0]
            op = items[1]
            right = items[2]
            
            op_map = {
                'and': '&&',
                'or': '||',
                'implies': '->',
                'iff': '<->'
            }
            
            tau_op = op_map.get(str(op).lower(), '&&')
            
            left_tau = left['tau'] if isinstance(left, dict) else str(left)
            right_tau = right['tau'] if isinstance(right, dict) else str(right)
            
            return {'tau': f"({left_tau} {tau_op} {right_tau})"}
        
        # Unary NOT
        if len(items) == 2 and str(items[0]).lower() == 'not':
            operand = items[1]
            operand_tau = operand['tau'] if isinstance(operand, dict) else str(operand)
            return {'tau': f"!({operand_tau})"}
        
        return {'tau': str(items[0])}
    
    # =========================================================================
    # Helper methods
    # =========================================================================
    
    def _map_comparison_op(self, op_token):
        """Map comparison operator to Tau syntax."""
        if isinstance(op_token, Token):
            op = op_token.value.strip().lower()
        else:
            op = str(op_token).lower()
        
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
        
        return op_map.get(op, '=')
    
    # =========================================================================
    # Terminal handlers
    # =========================================================================
    
    def IDENTIFIER(self, token):
        """Process identifier."""
        return str(token.value)
    
    def NUMBER(self, token):
        """Process number."""
        return str(token.value)
    
    def entity(self, items):
        """Process entity reference."""
        if items:
            # Could be determiner + class + id, or just id
            entity_name = str(items[-1])  # Take the last item as the main identifier
            
            # Register entity if new
            if entity_name not in self.context.entities:
                entity_class = 'unknown'
                if len(items) > 1:
                    # Try to extract class
                    for item in items:
                        if isinstance(item, Token) and item.type == 'NOUN':
                            entity_class = str(item.value)
                            break
                
                self.context.entities[entity_name] = EntityInfo(
                    name=entity_name,
                    entity_class=entity_class
                )
            
            return entity_name
        
        return ""
    
    def property(self, items):
        """Process property."""
        if items:
            return str(items[0])
        return ""
    
    def term(self, items):
        """Process term."""
        if items:
            return str(items[0])
        return ""


class DeclarativeTCEParser:
    """
    Enhanced parser for declarative TCE.
    Integrates with existing TCE infrastructure.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_grammar()
        self._create_parser()
        
    def _load_grammar(self):
        """Load the declarative TCE grammar."""
        grammar_path = pathlib.Path(__file__).parent / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_declarative.lark"
        
        # Fallback paths
        if not grammar_path.exists():
            # Try relative to this file
            grammar_path = pathlib.Path(__file__).parent / "tce_declarative.lark"
        
        if not grammar_path.exists():
            # Use inline grammar as fallback
            self.grammar = self._get_inline_grammar()
        else:
            with open(grammar_path, 'r') as f:
                self.grammar = f.read()
    
    def _create_parser(self):
        """Create Lark parser with the grammar."""
        self.parser = Lark(
            self.grammar,
            start='specification',
            parser='lalr',
            transformer=DeclarativeTCETransformer()
        )
    
    def parse(self, text: str) -> str:
        """Parse declarative TCE text to Tau."""
        try:
            # Ensure text ends with period
            if not text.strip().endswith('.'):
                text = text.strip() + '.'
            
            # Parse and transform
            result = self.parser.parse(text)
            return result
            
        except Exception as e:
            self.logger.error(f"Parse error: {e}")
            raise
    
    def _get_inline_grammar(self) -> str:
        """Get a simplified inline grammar for fallback."""
        return """
        ?start: specification
        specification: declaration+
        declaration: statement "."
        
        statement: fact | property | constraint
        
        fact: entity "is" property
            | entity "has" property
            | term "equals" term
        
        property: "all" entity_class "are" property_name
                | "every" entity_class "has" property_name
        
        constraint: "always" expr
                  | "eventually" expr
        
        expr: term
            | expr "and" expr
            | expr "or" expr
            | "not" expr
        
        term: entity | number | "true" | "false"
        entity: WORD
        entity_class: WORD
        property_name: WORD
        number: NUMBER
        
        %import common.WORD
        %import common.NUMBER
        %import common.WS
        %ignore WS
        """


# =========================================================================
# Integration with existing parser
# =========================================================================

def enhance_existing_tce_parser():
    """
    Enhance the existing TCE parser with declarative patterns.
    Returns an enhanced parser that can handle both traditional TCE and declarative TCE.
    """
    
    # Import existing parser components
    try:
        from src.tau_translator_omega.core_engine.cnl_parser.parser import TceTransformer
        from src.tau_translator_omega.core_engine.tce_tau_transformer import TCEToTauTransformer
    except ImportError:
        # Use our declarative parser if imports fail
        return DeclarativeTCEParser()
    
    # Create hybrid parser that tries declarative first, then falls back
    class HybridTCEParser:
        def __init__(self):
            self.declarative_parser = DeclarativeTCEParser()
            self.traditional_transformer = TCEToTauTransformer()
            
        def parse(self, text: str) -> str:
            """Parse text using best available method."""
            # Try declarative parsing first
            try:
                result = self.declarative_parser.parse(text)
                if result:
                    return result
            except:
                pass
            
            # Fallback to traditional parsing
            try:
                # Load traditional grammar
                grammar_path = pathlib.Path(__file__).parent / "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
                with open(grammar_path, 'r') as f:
                    grammar = f.read()
                
                parser = Lark(grammar, start='start', parser='lalr')
                tree = parser.parse(text)
                result = self.traditional_transformer.transform(tree)
                return result
            except:
                # Final fallback - simple pattern matching
                return self._simple_parse(text)
        
        def _simple_parse(self, text: str) -> str:
            """Simple pattern-based parsing as final fallback."""
            text = text.lower().strip()
            
            # Basic patterns
            if text.startswith("all "):
                # all X are Y -> all x: X(x) -> Y(x)
                parts = text[4:].split(" are ")
                if len(parts) == 2:
                    entity = parts[0].strip()
                    property = parts[1].strip().rstrip('.')
                    var = entity[0]
                    return f"all {var}: is_{entity}({var}) -> is_{property}({var})"
            
            elif text.startswith("always "):
                # always P -> □(P)
                prop = text[7:].strip().rstrip('.')
                return f"□({prop})"
            
            elif text.startswith("if ") and " then " in text:
                # if P then Q -> P -> Q
                parts = text[3:].split(" then ")
                if len(parts) == 2:
                    condition = parts[0].strip()
                    consequence = parts[1].strip().rstrip('.')
                    return f"{condition} -> {consequence}"
            
            # Default - return as is
            return text.rstrip('.')
    
    return HybridTCEParser()


# =========================================================================
# Testing
# =========================================================================

def test_declarative_parser():
    """Test the declarative parser with example sentences."""
    parser = enhance_existing_tce_parser()
    
    test_cases = [
        # Simple facts
        "all persons are mortal.",
        "socrates is a person.",
        "x equals 5.",
        
        # Properties
        "every car has wheels.",
        "no student is lazy.",
        
        # Relationships  
        "john owns a car.",
        "every person owns some vehicle.",
        
        # Constraints
        "x greater than 0 implies x not equals 0.",
        "constraint: all values are positive.",
        
        # Temporal properties
        "always output 1 at time t equals input 1 at time t.",
        "eventually the system reaches a stable state.",
        "never the queue is full.",
        
        # Complex declarations
        "all persons who own cars must have insurance.",
        "when input 1 at time t equals 1, output 1 at time t plus 1 equals 1 holds.",
        
        # Definitions
        "positive is defined as greater than zero.",
        "valid_user means authenticated and authorized."
    ]
    
    print("Testing Declarative TCE Parser")
    print("=" * 60)
    
    for sentence in test_cases:
        print(f"\nInput:  {sentence}")
        try:
            result = parser.parse(sentence)
            print(f"Output: {result}")
        except Exception as e:
            print(f"Error:  {e}")
    
    print("\n" + "=" * 60)
    print("Declarative parser test complete.")


if __name__ == "__main__":
    test_declarative_parser()