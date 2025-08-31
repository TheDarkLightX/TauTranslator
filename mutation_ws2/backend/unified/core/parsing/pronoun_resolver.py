"""
Pronoun Resolver - Pure coreference resolution logic.
Resolves pronouns to their antecedents based on context.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Tuple, Dict
from backend.unified.core.domain.parser_types import (
    VariableName, EntityType, EntityInfo, ParseContext,
    PronounResolutionError
)


class PronounResolver:
    """
    Resolves pronouns to their antecedents - pure logic, no I/O.
    Follows IDP with explicit method names indicating consequences.
    """
    
    def __init__(self):
        """Initialize resolver with pronoun rules."""
        self._initialize_pronoun_rules()
    
    def _initialize_pronoun_rules(self) -> None:
        """Set up pronoun resolution rules."""
        self.singular_pronouns = {'it', 'its', 'itself'}
        self.plural_pronouns = {'they', 'them', 'their', 'theirs', 'themselves'}
        self.person_pronouns = {'he', 'him', 'his', 'she', 'her', 'hers'}
        
        # Entity types that can be referenced by specific pronouns
        self.person_entity_types = {'person', 'user', 'customer', 'employee', 
                                   'student', 'professor', 'manager'}
        self.singular_entity_types = {'car', 'system', 'transaction', 'process',
                                     'rule', 'constraint', 'function'}
    
    def resolve_pronoun_to_variable(
        self,
        pronoun: str,
        context: ParseContext,
        position_hint: Optional[int] = None
    ) -> VariableName:
        """
        Main entry point for pronoun resolution.
        Routes to specific resolver based on pronoun type.
        """
        pronoun_lower = pronoun.lower()
        
        if pronoun_lower in self.singular_pronouns:
            return self.resolve_it_pronoun_to_entity(context, position_hint)
        elif pronoun_lower in self.plural_pronouns:
            return self.resolve_they_pronoun_to_entity(context, position_hint)
        elif pronoun_lower in self.person_pronouns:
            return self.resolve_person_pronoun_to_entity(pronoun_lower, context, position_hint)
        else:
            # Try definite reference resolution
            return self.resolve_definite_reference_to_entity(pronoun, context)
    
    def resolve_it_pronoun_to_entity(
        self,
        context: ParseContext,
        position_hint: Optional[int] = None
    ) -> VariableName:
        """
        Resolves 'it' to nearest singular entity.
        Uses recency and type compatibility.
        """
        candidates = self._find_singular_entity_candidates(context)
        
        if not candidates:
            raise PronounResolutionError("No singular entities found for 'it' resolution")
        
        # Return most recent (last in list)
        return candidates[-1]
    
    def _find_singular_entity_candidates(
        self, 
        context: ParseContext
    ) -> List[VariableName]:
        """Find entities that can be referenced by 'it'."""
        candidates = []
        
        for var, entity_info in context.entities.items():
            if self._is_singular_compatible(entity_info):
                candidates.append(var)
        
        return candidates
    
    def _is_singular_compatible(self, entity_info: EntityInfo) -> bool:
        """Check if entity can be referenced by singular pronouns."""
        # Check if entity type suggests singular
        entity_type_str = str(entity_info.entity_type).lower()
        
        # Singular by type
        if entity_type_str in self.singular_entity_types:
            return True
        
        # Not a plural form
        if not entity_type_str.endswith('s'):
            return True
        
        # Explicit quantifier check
        if entity_info.quantifier:
            quantifier_str = str(entity_info.quantifier.value).lower()
            if quantifier_str in ['a', 'an', 'one', 'each']:
                return True
                
        return False
    
    def resolve_they_pronoun_to_entity(
        self,
        context: ParseContext,
        position_hint: Optional[int] = None
    ) -> VariableName:
        """
        Resolves 'they/them' to nearest plural entity or group.
        Returns the variable representing the group.
        """
        candidates = self._find_plural_entity_candidates(context)
        
        if not candidates:
            raise PronounResolutionError("No plural entities found for 'they' resolution")
        
        # Return most recent (last in list)
        return candidates[-1]
    
    def _find_plural_entity_candidates(
        self,
        context: ParseContext
    ) -> List[VariableName]:
        """Find entities that can be referenced by 'they'."""
        candidates = []
        
        for var, entity_info in context.entities.items():
            if self._is_plural_compatible(entity_info):
                candidates.append(var)
        
        return candidates
    
    def _is_plural_compatible(self, entity_info: EntityInfo) -> bool:
        """Check if entity can be referenced by plural pronouns."""
        entity_type_str = str(entity_info.entity_type).lower()
        
        # Plural by type (ends with 's' but not 'ss')
        if entity_type_str.endswith('s') and not entity_type_str.endswith('ss'):
            return True
        
        # Universal quantifiers suggest groups
        if entity_info.quantifier:
            quantifier_str = str(entity_info.quantifier.value).lower()
            if quantifier_str in ['all', 'every', 'many', 'several', 'some']:
                return True
                
        return False
    
    def resolve_person_pronoun_to_entity(
        self,
        pronoun: str,
        context: ParseContext,
        position_hint: Optional[int] = None
    ) -> VariableName:
        """Resolves he/she/him/her to nearest person entity."""
        candidates = self._find_person_entity_candidates(context)
        
        if not candidates:
            raise PronounResolutionError(f"No person entities found for '{pronoun}' resolution")
        
        # Return most recent (last in list)
        return candidates[-1]
    
    def _find_person_entity_candidates(
        self,
        context: ParseContext
    ) -> List[VariableName]:
        """Find entities that represent people."""
        candidates = []
        
        for var, entity_info in context.entities.items():
            entity_type_str = str(entity_info.entity_type).lower()
            if entity_type_str in self.person_entity_types:
                candidates.append(var)
        
        return candidates
    
    def resolve_definite_reference_to_entity(
        self,
        reference: str,
        context: ParseContext
    ) -> VariableName:
        """
        Resolves definite references like 'the car' to their variables.
        Checks coreference mappings first, then entity types.
        """
        # Check explicit coreferences
        if reference in context.coreferences:
            return context.coreferences[reference]
        
        # Try to extract the entity type from the reference
        # "the car" -> "car", "the red car" -> "car"
        words = reference.lower().split()
        if words and words[0] == 'the':
            # Find the noun (usually last word)
            potential_type = words[-1]
            
            # Look for entities of this type
            for var, entity_info in context.entities.items():
                if str(entity_info.entity_type).lower() == potential_type:
                    return var
        
        raise PronounResolutionError(f"Cannot resolve reference: {reference}")
    
    def add_coreference_mapping(
        self,
        reference: str,
        variable: VariableName,
        context: ParseContext
    ) -> None:
        """Add a coreference mapping to the context."""
        context.add_coreference(reference, variable)