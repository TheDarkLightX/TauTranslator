"""
NLP pattern handler services following the Intentional Disclosure Principle.

Each pattern type has its own handler with methods ≤10 lines following IDP Rule 2.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, Optional
from returns.result import Result, Success, Failure

from .nlp_types import (
    PatternType, PatternMatch, Entity, Predicate, Relation,
    Quantifier, Condition, EntityName, PredicateName, RelationName
)
from ..infrastructure.nlp_infrastructure import (
    EntityExtractor, PhraseMapper, TemplateProcessor
)


class PatternHandlerBase:
    """Base class for pattern handlers."""
    
    def handle(self, match: PatternMatch) -> Result[str, str]:
        """Handle pattern match and generate output."""
        raise NotImplementedError("Subclasses must implement handle method")
    
    def extract_components(self, groups: Dict[str, str]) -> Dict[str, str]:
        """Extract semantic components from matched groups."""
        return groups


class UniversalPatternHandler(PatternHandlerBase):
    """Handles universal quantification patterns."""
    
    def handle(self, match: PatternMatch) -> Result[str, str]:
        """Handle universal quantifier pattern."""
        components = self.extract_components(match.matched_groups)
        
        entity_name = components.get('entity', '')
        constraint = components.get('constraint', '')
        
        if not entity_name:
            return Failure("No entity found in universal pattern")
        
        # Build TCE format
        tce_format = f"for every {entity_name} such that {constraint}"
        return Success(tce_format)
    
    def extract_components(self, groups: Dict[str, str]) -> Dict[str, str]:
        """Extract entity and constraint from groups."""
        # group_0: quantifier (all/every/each)
        # group_1: entity
        # group_2: constraint
        
        entity = groups.get('group_1', '').lower()
        entity = EntityExtractor.singularize(entity)
        
        constraint = groups.get('group_2', '')
        constraint = self._normalize_constraint(constraint)
        
        return {
            'entity': entity,
            'constraint': constraint
        }
    
    def _normalize_constraint(self, constraint: str) -> str:
        """Normalize constraint text."""
        # Handle modal verbs
        if constraint.startswith('can '):
            predicate = constraint[4:]
            return f"it can {predicate}"
        elif constraint.startswith('must '):
            predicate = constraint[5:]
            return f"it must {predicate}"
        
        return constraint


class ExistentialPatternHandler(PatternHandlerBase):
    """Handles existential quantification patterns."""
    
    def handle(self, match: PatternMatch) -> Result[str, str]:
        """Handle existential quantifier pattern."""
        components = self.extract_components(match.matched_groups)
        
        entity_name = components.get('entity', '')
        constraint = components.get('constraint', '')
        
        if not entity_name:
            return Failure("No entity found in existential pattern")
        
        # Build TCE format
        tce_format = f"there exists {entity_name} such that {constraint}"
        return Success(tce_format)
    
    def extract_components(self, groups: Dict[str, str]) -> Dict[str, str]:
        """Extract entity and constraint from groups."""
        # group_0: quantifier (some/a/an)
        # group_1: entity
        # group_2: constraint
        
        entity = groups.get('group_1', '').lower()
        constraint = groups.get('group_2', '')
        
        # Process constraint for common patterns
        constraint = self._process_existential_constraint(constraint)
        
        return {
            'entity': entity,
            'constraint': constraint
        }
    
    def _process_existential_constraint(self, constraint: str) -> str:
        """Process existential constraint patterns."""
        # Handle "that/which" relative clauses
        if constraint.startswith(('that ', 'which ')):
            constraint = constraint.split(' ', 1)[1]
        
        # Replace "it" with variable reference
        constraint = constraint.replace(' it ', ' x ')
        
        return constraint


class ConditionalPatternHandler(PatternHandlerBase):
    """Handles conditional (if-then) patterns."""
    
    def handle(self, match: PatternMatch) -> Result[str, str]:
        """Handle conditional pattern."""
        components = self.extract_components(match.matched_groups)
        
        antecedent = components.get('antecedent', '')
        consequent = components.get('consequent', '')
        
        if not antecedent or not consequent:
            return Failure("Incomplete conditional statement")
        
        # Build TCE format
        tce_format = f"if {antecedent} then {consequent}"
        return Success(tce_format)
    
    def extract_components(self, groups: Dict[str, str]) -> Dict[str, str]:
        """Extract antecedent and consequent."""
        # group_0: antecedent (condition)
        # group_1: consequent (result)
        
        antecedent = groups.get('group_0', '').strip()
        consequent = groups.get('group_1', '').strip()
        
        # Normalize both parts
        antecedent = self._normalize_clause(antecedent)
        consequent = self._normalize_clause(consequent)
        
        return {
            'antecedent': antecedent,
            'consequent': consequent
        }
    
    def _normalize_clause(self, clause: str) -> str:
        """Normalize a conditional clause."""
        # Remove trailing punctuation
        clause = clause.rstrip('.,;')
        
        # Ensure proper format
        if ' is ' not in clause and ' are ' not in clause:
            # Try to infer predicate structure
            words = clause.split()
            if len(words) >= 2:
                return f"{words[0]} is {' '.join(words[1:])}"
        
        return clause


class PredicatePatternHandler(PatternHandlerBase):
    """Handles simple predicate patterns."""
    
    def handle(self, match: PatternMatch) -> Result[str, str]:
        """Handle predicate pattern."""
        components = self.extract_components(match.matched_groups)
        
        subject = components.get('subject', '')
        predicate = components.get('predicate', '')
        
        if not subject or not predicate:
            return Failure("Incomplete predicate statement")
        
        # Build TCE format (already in correct form)
        tce_format = f"{subject} is {predicate}"
        return Success(tce_format)
    
    def extract_components(self, groups: Dict[str, str]) -> Dict[str, str]:
        """Extract subject and predicate."""
        # group_0: subject
        # group_1: predicate
        
        return {
            'subject': groups.get('group_0', '').lower(),
            'predicate': groups.get('group_1', '').lower()
        }


class RelationPatternHandler(PatternHandlerBase):
    """Handles relation patterns."""
    
    def handle(self, match: PatternMatch) -> Result[str, str]:
        """Handle relation pattern."""
        components = self.extract_components(match.matched_groups)
        
        relation = components.get('relation', '')
        subject = components.get('subject', '')
        object_entity = components.get('object', '')
        
        if not all([relation, subject, object_entity]):
            return Failure("Incomplete relation statement")
        
        # Build TCE format
        tce_format = f"{relation}({subject}, {object_entity})"
        return Success(tce_format)
    
    def extract_components(self, groups: Dict[str, str]) -> Dict[str, str]:
        """Extract relation components."""
        # group_0: subject
        # group_1: relation verb
        # group_2: object
        
        subject = groups.get('group_0', '').lower()
        relation = groups.get('group_1', '').lower()
        obj = groups.get('group_2', '').lower()
        
        # Normalize relation verb to base form
        relation = self._normalize_relation_verb(relation)
        
        return {
            'subject': subject,
            'relation': relation,
            'object': obj
        }
    
    def _normalize_relation_verb(self, verb: str) -> str:
        """Normalize relation verb to base form."""
        # Remove 's' from third person singular
        if verb.endswith('s') and not verb.endswith('ss'):
            return verb[:-1]
        return verb


class AlwaysPropertyHandler(PatternHandlerBase):
    """Handles 'always' property patterns."""
    
    def handle(self, match: PatternMatch) -> Result[str, str]:
        """Handle always property pattern."""
        components = self.extract_components(match.matched_groups)
        
        entity = components.get('entity', '')
        property_name = components.get('property', '')
        
        if not entity or not property_name:
            return Failure("Incomplete always property statement")
        
        # Build TCE format
        tce_format = f"always {entity} is {property_name}"
        return Success(tce_format)
    
    def extract_components(self, groups: Dict[str, str]) -> Dict[str, str]:
        """Extract entity and property."""
        # group_0: optional "the"
        # group_1: entity
        # group_2: property
        
        return {
            'entity': groups.get('group_1', '').lower(),
            'property': groups.get('group_2', '').lower()
        }


class DisjunctionPatternHandler(PatternHandlerBase):
    """Handles disjunction (either/or) patterns."""
    
    def handle(self, match: PatternMatch) -> Result[str, str]:
        """Handle disjunction pattern."""
        components = self.extract_components(match.matched_groups)
        
        first_option = components.get('first', '')
        second_option = components.get('second', '')
        
        if not first_option or not second_option:
            return Failure("Incomplete disjunction statement")
        
        # Build TCE format
        tce_format = f"{first_option} or {second_option}"
        return Success(tce_format)
    
    def extract_components(self, groups: Dict[str, str]) -> Dict[str, str]:
        """Extract disjunction options."""
        # group_0: first option
        # group_1: second option
        
        first = groups.get('group_0', '').strip()
        second = groups.get('group_1', '').strip()
        
        return {
            'first': self._normalize_option(first),
            'second': self._normalize_option(second)
        }
    
    def _normalize_option(self, option: str) -> str:
        """Normalize disjunction option."""
        # Remove trailing punctuation
        option = option.rstrip('.,;')
        return option


class PatternHandlerFactory:
    """Factory for creating pattern handlers."""
    
    _handlers = {
        PatternType.UNIVERSAL: UniversalPatternHandler,
        PatternType.EXISTENTIAL: ExistentialPatternHandler,
        PatternType.CONDITIONAL: ConditionalPatternHandler,
        PatternType.PREDICATE: PredicatePatternHandler,
        PatternType.RELATION: RelationPatternHandler,
        PatternType.ALWAYS_PROPERTY: AlwaysPropertyHandler,
        PatternType.DISJUNCTION: DisjunctionPatternHandler,
    }
    
    @classmethod
    def create_handler(cls, pattern_type: PatternType) -> Optional[PatternHandlerBase]:
        """Create handler for pattern type."""
        handler_class = cls._handlers.get(pattern_type)
        if handler_class:
            return handler_class()
        return None
    
    @classmethod
    def register_handler(cls, pattern_type: PatternType, handler_class: type):
        """Register custom handler for pattern type."""
        cls._handlers[pattern_type] = handler_class