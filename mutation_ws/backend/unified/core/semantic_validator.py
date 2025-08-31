"""
Semantic Validator - Validates logical consistency of parsed statements
Prevents nonsensical combinations like "cars think about philosophy"

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, List, Set, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

from backend.unified.core.semantic_lexicon import SemanticLexicon, EntityCategory, RelationType
from .domain_types import Result, Success, Failure, AppError


@dataclass(frozen=True)
class ValidationError:
    """Semantic validation error with suggestion."""
    message: str
    error_type: str
    suggestion: str
    confidence: float = 0.8


@dataclass 
class ValidationResult:
    """Result of semantic validation."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


# === PURE VALIDATION FUNCTIONS (CC=1 each) ===

def validate_entity_relation_compatibility(subject_type: EntityCategory, relation: str, object_type: EntityCategory) -> bool:
    """Validate if entity types are compatible with relation."""
    return check_relation_compatibility(subject_type, relation, object_type)


def check_relation_compatibility(subject_type: EntityCategory, relation: str, object_type: EntityCategory) -> bool:
    """Check if relation makes semantic sense."""
    valid_combinations = get_valid_relation_combinations()
    return is_combination_valid(valid_combinations, subject_type, relation, object_type)


def get_valid_relation_combinations() -> Dict[str, List[Tuple[EntityCategory, EntityCategory]]]:
    """Get valid subject-object combinations for relations."""
    return {
        'owns': [
            (EntityCategory.PERSON, EntityCategory.OBJECT),
            (EntityCategory.PERSON, EntityCategory.DOCUMENT),
            (EntityCategory.ORGANIZATION, EntityCategory.OBJECT),
        ],
        'thinks': [
            (EntityCategory.PERSON, EntityCategory.ABSTRACT),
        ],
        'drives': [
            (EntityCategory.PERSON, EntityCategory.OBJECT),
        ],
        'located_at': [
            (EntityCategory.PERSON, EntityCategory.LOCATION),
            (EntityCategory.OBJECT, EntityCategory.LOCATION),
            (EntityCategory.ORGANIZATION, EntityCategory.LOCATION),
        ],
        'causes': [
            (EntityCategory.EVENT, EntityCategory.EVENT),
            (EntityCategory.ABSTRACT, EntityCategory.ABSTRACT),
            (EntityCategory.PERSON, EntityCategory.EVENT),
        ],
        'requires': [
            (EntityCategory.SYSTEM, EntityCategory.OBJECT),
            (EntityCategory.PERSON, EntityCategory.OBJECT),
            (EntityCategory.EVENT, EntityCategory.ABSTRACT),
        ]
    }


def is_combination_valid(valid_combinations: Dict, subject_type: EntityCategory, relation: str, object_type: EntityCategory) -> bool:
    """Check if specific combination is valid."""
    if relation not in valid_combinations:
        return True  # Unknown relations are allowed
    
    valid_pairs = valid_combinations[relation]
    return any(is_pair_match(pair, subject_type, object_type) for pair in valid_pairs)


def is_pair_match(pair: Tuple[EntityCategory, EntityCategory], subject_type: EntityCategory, object_type: EntityCategory) -> bool:
    """Check if pair matches subject and object types."""
    return pair[0] == subject_type and pair[1] == object_type


def create_validation_error(error_type: str, message: str, suggestion: str) -> ValidationError:
    """Create validation error with suggestion."""
    return ValidationError(
        message=message,
        error_type=error_type,
        suggestion=suggestion
    )


def validate_quantifier_logic(quantifier: str, entity: str, predicate: str) -> ValidationResult:
    """Validate quantifier logic consistency."""
    return check_quantifier_consistency(quantifier, entity, predicate)


def check_quantifier_consistency(quantifier: str, entity: str, predicate: str) -> ValidationResult:
    """Check if quantifier usage is logically consistent."""
    errors = []
    
    error = check_universal_quantifier_validity(quantifier, predicate)
    if error:
        errors.append(error)
    
    error = check_existential_quantifier_validity(quantifier, predicate)  
    if error:
        errors.append(error)
        
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def check_universal_quantifier_validity(quantifier: str, predicate: str) -> Optional[ValidationError]:
    """Check universal quantifier validity."""
    universal_quantifiers = {'all', 'every', 'each'}
    
    if quantifier.lower() in universal_quantifiers:
        return validate_universal_claim(predicate)
    return None


def validate_universal_claim(predicate: str) -> Optional[ValidationError]:
    """Validate universal claim reasonableness."""
    risky_predicates = {'perfect', 'never', 'always', 'impossible'}
    
    if any(risky in predicate.lower() for risky in risky_predicates):
        return create_validation_error(
            'universal_risk',
            f"Universal claim with '{predicate}' may be too strong",
            "Consider using 'most' or 'typically' instead"
        )
    return None


def check_existential_quantifier_validity(quantifier: str, predicate: str) -> Optional[ValidationError]:
    """Check existential quantifier validity."""
    existential_quantifiers = {'some', 'few', 'many'}
    
    if quantifier.lower() in existential_quantifiers:
        return validate_existential_claim(predicate)
    return None


def validate_existential_claim(predicate: str) -> Optional[ValidationError]:
    """Validate existential claim reasonableness."""
    # For now, existential claims are generally safe
    return None


def validate_temporal_logic(temporal_expr: str, main_clause: str) -> ValidationResult:
    """Validate temporal logic consistency."""
    return check_temporal_consistency(temporal_expr, main_clause)


def check_temporal_consistency(temporal_expr: str, main_clause: str) -> ValidationResult:
    """Check temporal expression consistency."""
    errors = []
    
    error = check_temporal_contradiction(temporal_expr, main_clause)
    if error:
        errors.append(error)
        
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def check_temporal_contradiction(temporal_expr: str, main_clause: str) -> Optional[ValidationError]:
    """Check for temporal contradictions."""
    # Simple contradiction detection
    past_indicators = {'was', 'were', 'had', 'did'}
    future_indicators = {'will', 'shall', 'going to'}
    
    expr_has_past = any(indicator in temporal_expr.lower() for indicator in past_indicators)
    clause_has_future = any(indicator in main_clause.lower() for indicator in future_indicators)
    
    if expr_has_past and clause_has_future:
        return create_validation_error(
            'temporal_contradiction',
            "Past temporal condition with future consequence may be inconsistent",
            "Check if temporal relationship is logically coherent"
        )
    return None


def validate_modal_logic(subject: str, modal: str, action: str) -> ValidationResult:
    """Validate modal logic consistency."""
    return check_modal_consistency(subject, modal, action)


def check_modal_consistency(subject: str, modal: str, action: str) -> ValidationResult:
    """Check modal expression consistency."""
    errors = []
    
    error = check_modal_subject_compatibility(subject, modal, action)
    if error:
        errors.append(error)
        
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def check_modal_subject_compatibility(subject: str, modal: str, action: str) -> Optional[ValidationError]:
    """Check if subject can perform modal action."""
    necessity_modals = {'must', 'should', 'ought to'}
    possibility_modals = {'may', 'might', 'could', 'can'}
    
    # Check if inanimate objects have obligations
    inanimate_indicators = {'car', 'house', 'book', 'system', 'application'}
    
    if (modal.lower() in necessity_modals and 
        any(indicator in subject.lower() for indicator in inanimate_indicators)):
        return create_validation_error(
            'modal_subject_mismatch',
            f"Inanimate subject '{subject}' assigned obligation '{modal} {action}'",
            "Consider if this entity can actually have obligations"
        )
    return None


class SemanticValidator:
    """
    Validates semantic consistency of parsed statements.
    Prevents nonsensical combinations and provides suggestions.
    """
    
    def __init__(self, lexicon: SemanticLexicon):
        """Initialize with semantic lexicon."""
        self.lexicon = lexicon
        self.logger = logging.getLogger(__name__)
    
    def validate_statement(self, statement: str, parsed_components: Dict) -> ValidationResult:
        """Validate complete statement for semantic consistency."""
        return validate_statement_components(self.lexicon, parsed_components)
    
    def validate_relation(self, subject: str, relation: str, object_: str) -> Result[bool, ValidationError]:
        """Validate subject-relation-object triplet."""
        return validate_triplet(self.lexicon, subject, relation, object_)
    
    def validate_quantified_statement(self, quantifier: str, entity: str, predicate: str) -> ValidationResult:
        """Validate quantified statement logic."""
        return validate_quantifier_logic(quantifier, entity, predicate)
    
    def validate_temporal_statement(self, temporal_expr: str, main_clause: str) -> ValidationResult:
        """Validate temporal statement consistency."""
        return validate_temporal_logic(temporal_expr, main_clause)
    
    def validate_modal_statement(self, subject: str, modal: str, action: str) -> ValidationResult:
        """Validate modal statement consistency."""
        return validate_modal_logic(subject, modal, action)


# === HELPER FUNCTIONS ===

def validate_statement_components(lexicon: SemanticLexicon, components: Dict) -> ValidationResult:
    """Validate all components of a statement."""
    errors = []
    warnings = []
    
    # Validate each component type
    if 'relations' in components:
        relation_errors = validate_all_relations(lexicon, components['relations'])
        errors.extend(relation_errors)
    
    if 'quantifiers' in components:
        quantifier_errors = validate_all_quantifiers(components['quantifiers'])
        errors.extend(quantifier_errors)
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_all_relations(lexicon: SemanticLexicon, relations: List[Tuple[str, str, str]]) -> List[ValidationError]:
    """Validate all relations in statement."""
    errors = []
    for subject, relation, object_ in relations:
        result = validate_triplet(lexicon, subject, relation, object_)
        if isinstance(result, Failure):
            errors.append(result.failure())
    return errors


def validate_all_quantifiers(quantifiers: List[Dict]) -> List[ValidationError]:
    """Validate all quantifiers in statement."""
    errors = []
    for quant_info in quantifiers:
        result = validate_quantifier_logic(
            quant_info.get('quantifier', ''),
            quant_info.get('entity', ''),
            quant_info.get('predicate', '')
        )
        errors.extend(result.errors)
    return errors


def validate_triplet(lexicon: SemanticLexicon, subject: str, relation: str, object_: str) -> Result[bool, ValidationError]:
    """Validate subject-relation-object triplet."""
    subject_type = lexicon.classify_entity(subject)
    object_type = lexicon.classify_entity(object_)
    
    if validate_entity_relation_compatibility(subject_type, relation, object_type):
        return Success(True)
    else:
        error = create_semantic_mismatch_error(subject, subject_type, relation, object_, object_type)
        return Failure(error)


def create_semantic_mismatch_error(subject: str, subject_type: EntityCategory, relation: str, object_: str, object_type: EntityCategory) -> ValidationError:
    """Create error for semantic mismatch."""
    return create_validation_error(
        'semantic_mismatch',
        f"Semantic mismatch: {subject_type.value} '{subject}' cannot '{relation}' {object_type.value} '{object_}'",
        f"Consider if this relationship makes logical sense"
    )


def create_semantic_validator(lexicon: Optional[SemanticLexicon] = None) -> SemanticValidator:
    """Create semantic validator instance."""
    if lexicon is None:
        from backend.unified.core.semantic_lexicon import get_semantic_lexicon
        lexicon = get_semantic_lexicon()
    
    return SemanticValidator(lexicon)