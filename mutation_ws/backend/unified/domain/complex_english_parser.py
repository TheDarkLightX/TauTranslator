"""
Complex English Parser
Advanced natural language parsing for complex English sentences with relative clauses,
coreference resolution, and nested quantifier scopes.

This parser handles sentences like:
"for every person who owns a car, if the car is red then the person must pay extra"

Copyright: DarkLightX/Dana Edwards
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any
from enum import Enum
import re
from abc import ABC, abstractmethod

# Domain types for the parser
class QuantifierType(Enum):
    UNIVERSAL = "universal"  # all, every, each
    EXISTENTIAL = "existential"  # some, a, there exists
    DEFINITE = "definite"  # the
    
class DependencyType(Enum):
    SUBJECT = "nsubj"
    OBJECT = "dobj"
    MODIFIER = "amod"
    RELATIVE = "relcl"
    CONDITIONAL = "advcl"
    POSSESSION = "poss"

@dataclass
class Entity:
    """Represents an entity in the discourse."""
    id: str
    type: str  # person, car, etc.
    properties: Dict[str, Any] = field(default_factory=dict)
    quantifier: Optional[QuantifierType] = None
    variable: Optional[str] = None
    
@dataclass
class Predicate:
    """Represents a predicate/relation."""
    name: str
    arguments: List[str]  # entity IDs
    negated: bool = False
    
@dataclass
class Scope:
    """Represents a quantifier scope."""
    quantifier: QuantifierType
    variable: str
    entity_type: str
    constraints: List['LogicalForm'] = field(default_factory=list)
    body: Optional['LogicalForm'] = None

# Logical form representation
@dataclass 
class LogicalForm(ABC):
    """Abstract base for logical forms."""
    @abstractmethod
    def to_tau(self) -> str:
        pass

@dataclass
class QuantifiedFormula(LogicalForm):
    """Quantified formula: ∀x: φ or ∃x: φ"""
    quantifier: QuantifierType
    variable: str
    restriction: Optional[LogicalForm]  # type constraint
    body: LogicalForm
    
    def to_tau(self) -> str:
        q_symbol = "∀" if self.quantifier == QuantifierType.UNIVERSAL else "∃"
        if self.restriction:
            return f"{q_symbol}{self.variable}: ({self.restriction.to_tau()} → {self.body.to_tau()})"
        return f"{q_symbol}{self.variable}: {self.body.to_tau()}"

@dataclass
class Conditional(LogicalForm):
    """Conditional: if φ then ψ"""
    condition: LogicalForm
    consequence: LogicalForm
    
    def to_tau(self) -> str:
        return f"({self.condition.to_tau()} → {self.consequence.to_tau()})"

@dataclass
class Conjunction(LogicalForm):
    """Conjunction: φ ∧ ψ"""
    conjuncts: List[LogicalForm]
    
    def to_tau(self) -> str:
        return f"({' ∧ '.join(c.to_tau() for c in self.conjuncts)})"

@dataclass
class AtomicPredicate(LogicalForm):
    """Atomic predicate: p(x,y)"""
    predicate: str
    arguments: List[str]
    
    def to_tau(self) -> str:
        if len(self.arguments) == 0:
            return self.predicate
        return f"{self.predicate}({', '.join(self.arguments)})"

class ComplexEnglishParser:
    """Parser for complex English with advanced linguistic analysis."""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.scopes: List[Scope] = []
        self.coreference_map: Dict[str, str] = {}
        self.variable_counter = 0
        
    def parse(self, sentence: str) -> LogicalForm:
        """Parse complex English sentence into logical form."""
        # Tokenize and analyze
        tokens = self._tokenize(sentence)
        dependencies = self._dependency_parse(tokens)
        
        # Extract entities and predicates
        entities = self._extract_entities(tokens, dependencies)
        predicates = self._extract_predicates(tokens, dependencies)
        
        # Resolve coreferences
        self._resolve_coreferences(entities, tokens)
        
        # Build logical form
        return self._build_logical_form(entities, predicates, dependencies)
    
    def _tokenize(self, sentence: str) -> List[Dict[str, str]]:
        """Basic tokenization with POS tagging."""
        # Simplified tokenization - in production would use spaCy
        words = sentence.lower().replace(",", " , ").replace(".", " . ").split()
        
        # Basic POS patterns
        pos_patterns = {
            'DT': ['the', 'a', 'an', 'every', 'all', 'some', 'each'],
            'NN': ['person', 'car', 'people', 'cars', 'insurance', 'extra'],
            'VB': ['owns', 'own', 'have', 'has', 'pay', 'must', 'is', 'are'],
            'JJ': ['red', 'blue', 'extra'],
            'WP': ['who', 'that', 'which'],
            'IN': ['if', 'then', 'for'],
            'PRP': ['they', 'it', 'he', 'she'],
        }
        
        tokens = []
        for i, word in enumerate(words):
            pos = 'NN'  # default
            for tag, words_list in pos_patterns.items():
                if word in words_list:
                    pos = tag
                    break
            
            tokens.append({
                'index': i,
                'word': word,
                'pos': pos,
                'lemma': word.rstrip('s') if word.endswith('s') and pos == 'VB' else word
            })
        
        return tokens
    
    def _dependency_parse(self, tokens: List[Dict]) -> List[Tuple[int, str, int]]:
        """Simplified dependency parsing."""
        dependencies = []
        
        # Pattern-based dependency extraction
        for i, token in enumerate(tokens):
            word = token['word']
            
            # Subject relations
            if i > 0 and tokens[i-1]['pos'] == 'DT' and token['pos'] == 'NN':
                dependencies.append((i, 'det', i-1))
            
            # Relative clauses
            if word in ['who', 'that', 'which']:
                # Find the noun it modifies
                for j in range(i-1, -1, -1):
                    if tokens[j]['pos'] == 'NN':
                        dependencies.append((i, 'relcl', j))
                        break
            
            # Verb-object relations
            if token['pos'] == 'VB' and i < len(tokens) - 1:
                # Look for object
                for j in range(i+1, min(i+4, len(tokens))):
                    if tokens[j]['pos'] == 'NN':
                        dependencies.append((j, 'dobj', i))
                        break
        
        return dependencies
    
    def _extract_entities(self, tokens: List[Dict], dependencies: List[Tuple]) -> List[Entity]:
        """Extract entities from tokens."""
        entities = []
        
        for i, token in enumerate(tokens):
            if token['pos'] == 'NN':
                # Check for quantifier
                quantifier = None
                if i > 0:
                    prev_word = tokens[i-1]['word']
                    if prev_word in ['every', 'all', 'each']:
                        quantifier = QuantifierType.UNIVERSAL
                    elif prev_word in ['some', 'a', 'an']:
                        quantifier = QuantifierType.EXISTENTIAL
                    elif prev_word == 'the':
                        quantifier = QuantifierType.DEFINITE
                
                # Create entity
                var = self._get_next_variable()
                entity = Entity(
                    id=f"e{i}",
                    type=token['lemma'],
                    quantifier=quantifier,
                    variable=var if quantifier else None
                )
                entities.append(entity)
                self.entities[entity.id] = entity
        
        return entities
    
    def _extract_predicates(self, tokens: List[Dict], dependencies: List[Tuple]) -> List[Predicate]:
        """Extract predicates from tokens."""
        predicates = []
        
        for i, token in enumerate(tokens):
            if token['pos'] == 'VB':
                pred_name = token['lemma']
                
                # Find subject and object
                subj = None
                obj = None
                
                # Look for subject before verb
                for j in range(i-1, max(0, i-5), -1):
                    if tokens[j]['pos'] == 'NN':
                        subj = f"e{j}"
                        break
                
                # Look for object after verb
                for j in range(i+1, min(len(tokens), i+5)):
                    if tokens[j]['pos'] == 'NN':
                        obj = f"e{j}"
                        break
                
                # Create predicate based on arguments
                if pred_name in ['is', 'are'] and obj:
                    # Property predicate: "is red" -> red(x)
                    for j in range(i+1, min(len(tokens), i+3)):
                        if tokens[j]['pos'] == 'JJ':
                            predicates.append(Predicate(
                                name=tokens[j]['word'],
                                arguments=[subj] if subj else []
                            ))
                            break
                elif subj and obj:
                    # Binary predicate: owns(x,y)
                    predicates.append(Predicate(
                        name=pred_name,
                        arguments=[subj, obj]
                    ))
                elif subj:
                    # Unary predicate: pay(x)
                    predicates.append(Predicate(
                        name=pred_name,
                        arguments=[subj]
                    ))
        
        return predicates
    
    def _resolve_coreferences(self, entities: List[Entity], tokens: List[Dict]):
        """Resolve coreferences like 'the car' referring to 'a car'."""
        definite_refs = {}
        
        for entity in entities:
            if entity.quantifier == QuantifierType.DEFINITE:
                # Look for antecedent
                entity_type = entity.type
                
                # Find earlier mention of same type
                for other in entities:
                    if (other.type == entity_type and 
                        other.quantifier in [QuantifierType.EXISTENTIAL, QuantifierType.UNIVERSAL] and
                        other.id < entity.id):
                        # Map definite reference to earlier entity
                        self.coreference_map[entity.id] = other.id
                        entity.variable = other.variable
                        break
    
    def _get_next_variable(self) -> str:
        """Generate next variable name."""
        var = chr(ord('x') + self.variable_counter)
        self.variable_counter += 1
        return var
    
    def _build_logical_form(self, entities: List[Entity], predicates: List[Predicate], 
                           dependencies: List[Tuple]) -> LogicalForm:
        """Build logical form from extracted components."""
        # Group predicates by scope
        scoped_predicates = self._group_by_scope(entities, predicates)
        
        # Build nested quantified formulas
        return self._build_nested_formula(scoped_predicates, entities)
    
    def _group_by_scope(self, entities: List[Entity], predicates: List[Predicate]) -> Dict[str, List[Predicate]]:
        """Group predicates by their quantifier scope."""
        scoped = {}
        
        for pred in predicates:
            # Find the outermost quantified entity in predicate
            scope_entity = None
            for arg in pred.arguments:
                if arg in self.entities:
                    entity = self.entities[arg]
                    if entity.quantifier in [QuantifierType.UNIVERSAL, QuantifierType.EXISTENTIAL]:
                        scope_entity = entity
                        break
            
            if scope_entity:
                scope_key = scope_entity.id
                if scope_key not in scoped:
                    scoped[scope_key] = []
                scoped[scope_key].append(pred)
        
        return scoped
    
    def _build_nested_formula(self, scoped_predicates: Dict[str, List[Predicate]], 
                             entities: List[Entity]) -> LogicalForm:
        """Build nested quantified formula."""
        # Find outermost quantifier
        outermost = None
        for entity in entities:
            if entity.quantifier == QuantifierType.UNIVERSAL:
                outermost = entity
                break
        
        if not outermost:
            # No quantifiers, just conjunction of predicates
            all_preds = []
            for preds in scoped_predicates.values():
                all_preds.extend(preds)
            
            if len(all_preds) == 1:
                return self._predicate_to_logical_form(all_preds[0])
            else:
                return Conjunction([self._predicate_to_logical_form(p) for p in all_preds])
        
        # Build quantified formula
        restriction = AtomicPredicate(outermost.type, [outermost.variable])
        
        # Build body
        body_parts = []
        
        # Add predicates in this scope
        if outermost.id in scoped_predicates:
            for pred in scoped_predicates[outermost.id]:
                body_parts.append(self._predicate_to_logical_form(pred))
        
        # Look for nested quantifiers and conditionals
        nested_formula = self._find_nested_structures(outermost, entities, scoped_predicates)
        if nested_formula:
            body_parts.append(nested_formula)
        
        # Combine body parts
        if len(body_parts) == 0:
            body = AtomicPredicate("true", [])
        elif len(body_parts) == 1:
            body = body_parts[0]
        else:
            body = Conjunction(body_parts)
        
        return QuantifiedFormula(
            quantifier=outermost.quantifier,
            variable=outermost.variable,
            restriction=restriction,
            body=body
        )
    
    def _find_nested_structures(self, parent_entity: Entity, all_entities: List[Entity],
                               scoped_predicates: Dict[str, List[Predicate]]) -> Optional[LogicalForm]:
        """Find nested quantifiers and conditionals."""
        # Look for existential quantifier nested under universal
        # (e.g., "every person who owns a car")
        nested_entities = []
        for entity in all_entities:
            if (entity.quantifier == QuantifierType.EXISTENTIAL and
                entity.id > parent_entity.id):
                # Check if related to parent via predicate
                for preds in scoped_predicates.values():
                    for pred in preds:
                        if (parent_entity.id in pred.arguments or 
                            parent_entity.variable in pred.arguments) and \
                           (entity.id in pred.arguments or
                            entity.variable in pred.arguments):
                            nested_entities.append(entity)
                            break
        
        # Build nested structure
        if nested_entities:
            # For now, handle single nested entity
            nested = nested_entities[0]
            
            # Find predicates involving nested entity
            nested_preds = []
            for pred_list in scoped_predicates.values():
                for pred in pred_list:
                    if nested.id in pred.arguments or nested.variable in pred.arguments:
                        nested_preds.append(pred)
            
            # Look for conditional
            # Pattern: "if [property] then [consequence]"
            condition_preds = []
            consequence_preds = []
            
            for pred in nested_preds:
                # Simple heuristic: color predicates are conditions
                if pred.name in ['red', 'blue', 'green']:
                    condition_preds.append(pred)
                elif pred.name in ['pay', 'must_pay_extra']:
                    consequence_preds.append(pred)
            
            if condition_preds and consequence_preds:
                # Build conditional
                condition = Conjunction([self._predicate_to_logical_form(p) for p in condition_preds]) \
                           if len(condition_preds) > 1 else self._predicate_to_logical_form(condition_preds[0])
                
                consequence = Conjunction([self._predicate_to_logical_form(p) for p in consequence_preds]) \
                             if len(consequence_preds) > 1 else self._predicate_to_logical_form(consequence_preds[0])
                
                conditional = Conditional(condition, consequence)
                
                # Wrap in existential quantifier
                return QuantifiedFormula(
                    quantifier=nested.quantifier,
                    variable=nested.variable,
                    restriction=AtomicPredicate(nested.type, [nested.variable]),
                    body=conditional
                )
        
        return None
    
    def _predicate_to_logical_form(self, predicate: Predicate) -> LogicalForm:
        """Convert predicate to logical form."""
        # Resolve coreferences in arguments
        resolved_args = []
        for arg in predicate.arguments:
            if arg in self.coreference_map:
                # Use variable of referenced entity
                ref_id = self.coreference_map[arg]
                if ref_id in self.entities:
                    resolved_args.append(self.entities[ref_id].variable)
                else:
                    resolved_args.append(arg)
            elif arg in self.entities and self.entities[arg].variable:
                resolved_args.append(self.entities[arg].variable)
            else:
                resolved_args.append(arg)
        
        return AtomicPredicate(predicate.name, resolved_args)


# Convenience function
def parse_complex_english(sentence: str) -> str:
    """Parse complex English sentence and return TAU formula."""
    parser = ComplexEnglishParser()
    logical_form = parser.parse(sentence)
    return logical_form.to_tau()