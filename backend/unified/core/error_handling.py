"""
Enhanced Error Handling System - Comprehensive error recovery and suggestions
Provides detailed error messages and parsing suggestions.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import logging

from backend.unified.core.semantic_validator import ValidationError, ValidationResult


class ErrorType(Enum):
    """Types of parsing errors."""
    SYNTAX_ERROR = "syntax_error"
    SYNTAX_WARNING = "syntax_warning"
    SEMANTIC_ERROR = "semantic_error"
    VALIDATION_ERROR = "validation_error"
    PATTERN_MISMATCH = "pattern_mismatch"
    TEMPORAL_ERROR = "temporal_error"
    MODAL_ERROR = "modal_error"
    QUANTIFIER_ERROR = "quantifier_error"
    UNKNOWN_ENTITY = "unknown_entity"


@dataclass
class ParseError:
    """Comprehensive parsing error with recovery suggestions."""
    error_type: ErrorType
    message: str
    position: int
    length: int
    original_text: str
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 0.7
    recoverable: bool = True


@dataclass
class ErrorContext:
    """Context information for error analysis."""
    sentence: str
    position: int
    parsed_so_far: Dict = field(default_factory=dict)
    attempted_patterns: List[str] = field(default_factory=list)
    validation_errors: List[ValidationError] = field(default_factory=list)


@dataclass
class AppError:
    """Represents a generic application error."""
    message: str


# === PURE ERROR HANDLING FUNCTIONS (CC=1 each) ===

def create_parse_error(error_type: ErrorType, message: str, position: int, text: str) -> ParseError:
    """Create parse error with basic information."""
    return ParseError(
        error_type=error_type,
        message=message,
        position=position,
        length=len(text),
        original_text=text
    )


def add_suggestions_to_error(error: ParseError, suggestions: List[str]) -> ParseError:
    """Add suggestions to existing error."""
    error.suggestions.extend(suggestions)
    return error


def analyze_syntax_error(text: str, position: int) -> List[str]:
    """Analyze syntax error and provide suggestions."""
    return generate_syntax_suggestions(text, position)


def generate_syntax_suggestions(text: str, position: int) -> List[str]:
    """Generate syntax correction suggestions."""
    suggestions = []
    
    # Check for common syntax issues
    suggestions.extend(check_missing_articles(text))
    suggestions.extend(check_verb_agreement(text))
    suggestions.extend(check_punctuation_issues(text))
    suggestions.extend(check_quantifier_placement(text))
    
    return suggestions


def check_missing_articles(text: str) -> List[str]:
    """Check for missing articles."""
    # Simple pattern: noun without article
    pattern = r'\b(person|car|house|system)\b'
    matches = re.finditer(pattern, text, re.IGNORECASE)
    
    suggestions = []
    for match in matches:
        word = match.group(1)
        if not has_preceding_article(text, match.start()):
            suggestions.append(f"Consider adding 'a' or 'the' before '{word}'")
    
    return suggestions


def has_preceding_article(text: str, position: int) -> bool:
    """Check if word has preceding article."""
    articles = {'a', 'an', 'the', 'every', 'all', 'some'}
    words_before = text[:position].split()
    return len(words_before) > 0 and words_before[-1].lower() in articles


def check_verb_agreement(text: str) -> List[str]:
    """Check for subject-verb agreement issues."""
    # Simple patterns for common issues
    patterns = [
        (r'\b(all|every)\s+\w+\s+are\b', "Use 'is' with 'every', 'are' with 'all'"),
        (r'\bpeople\s+is\b', "Use 'people are' not 'people is'"),
        (r'\bperson\s+are\b', "Use 'person is' not 'person are'")
    ]
    
    suggestions = []
    for pattern, suggestion in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            suggestions.append(suggestion)
    
    return suggestions


def check_punctuation_issues(text: str) -> List[str]:
    """Check for punctuation issues."""
    suggestions = []
    
    if check_missing_comma_in_complex_sentence(text):
        suggestions.append("Consider adding comma before dependent clause")
    
    if check_missing_period(text):
        suggestions.append("Consider ending statement with period")
    
    return suggestions


def check_missing_comma_in_complex_sentence(text: str) -> bool:
    """Check if complex sentence needs comma."""
    complex_indicators = ['if', 'when', 'while', 'although', 'because']
    return any(f' {indicator} ' in text.lower() and ',' not in text for indicator in complex_indicators)


def check_missing_period(text: str) -> bool:
    """Check if statement needs period."""
    return len(text) > 20 and not text.strip().endswith(('.', '!', '?'))


def check_quantifier_placement(text: str) -> List[str]:
    """Check quantifier placement issues."""
    suggestions = []
    
    # Check for misplaced quantifiers
    if re.search(r'\b\w+\s+(all|every|some)\s+', text, re.IGNORECASE):
        suggestions.append("Move quantifier to beginning of statement")
    
    return suggestions


def analyze_semantic_error(validation_errors: List[ValidationError]) -> List[str]:
    """Analyze semantic errors and generate suggestions."""
    return generate_semantic_suggestions(validation_errors)


def generate_semantic_suggestions(validation_errors: List[ValidationError]) -> List[str]:
    """Generate semantic correction suggestions."""
    suggestions = []
    
    for error in validation_errors:
        suggestion = create_semantic_suggestion(error)
        if suggestion:
            suggestions.append(suggestion)
    
    return suggestions


def create_semantic_suggestion(error: ValidationError) -> Optional[str]:
    """Create suggestion for semantic error."""
    if error.error_type == 'semantic_mismatch':
        return f"Semantic issue: {error.suggestion}"
    elif error.error_type == 'temporal_contradiction':
        return f"Temporal issue: {error.suggestion}"
    elif error.error_type == 'modal_subject_mismatch':
        return f"Modal logic issue: {error.suggestion}"
    else:
        return error.suggestion


def analyze_pattern_mismatch(text: str, attempted_patterns: List[str]) -> List[str]:
    """Analyze pattern matching failures."""
    return generate_pattern_suggestions(text, attempted_patterns)


def generate_pattern_suggestions(text: str, attempted_patterns: List[str]) -> List[str]:
    """Generate pattern matching suggestions."""
    suggestions = []
    
    # Suggest simpler patterns
    if 'complex_temporal' in attempted_patterns:
        suggestions.append("Try simpler temporal structure: 'When X happens, Y occurs'")
    
    if 'complex_quantified' in attempted_patterns:
        suggestions.append("Try standard quantifier: 'All X are Y' or 'Some X are Y'")
    
    if 'causal_relation' in attempted_patterns:
        suggestions.append("Try clear causal structure: 'X causes Y' or 'X leads to Y'")
    
    # Suggest breaking down complex sentences
    if len(text.split()) > 15:
        suggestions.append("Consider breaking into shorter sentences")
    
    return suggestions


def create_unknown_entity_suggestions(entity: str) -> List[str]:
    """Create suggestions for unknown entities."""
    suggestions = []
    
    # Suggest common entity alternatives
    common_entities = {
        'person': ['customer', 'user', 'employee', 'individual'],
        'thing': ['object', 'item', 'product', 'entity'],
        'place': ['location', 'site', 'area', 'region'],
        'time': ['moment', 'period', 'duration', 'interval']
    }
    
    entity_lower = entity.lower()
    for category, alternatives in common_entities.items():
        if entity_lower in category or any(alt in entity_lower for alt in alternatives):
            suggestions.extend([f"Did you mean '{alt}'?" for alt in alternatives[:3]])
            break
    
    if not suggestions:
        suggestions.append(f"Define '{entity}' or use a more common term")
    
    return suggestions


def detect_error_type(text: str, context: ErrorContext) -> ErrorType:
    """Detect the type of error based on context."""
    return classify_error_from_context(text, context)


def classify_error_from_context(text: str, context: ErrorContext) -> ErrorType:
    """Classify error based on available context."""
    if context.validation_errors:
        return ErrorType.SEMANTIC_ERROR
    
    if has_syntax_indicators(text):
        return ErrorType.SYNTAX_ERROR
    
    if has_temporal_indicators(text):
        return ErrorType.TEMPORAL_ERROR
    
    if has_modal_indicators(text):
        return ErrorType.MODAL_ERROR
    
    if has_quantifier_indicators(text):
        return ErrorType.QUANTIFIER_ERROR
    
    return ErrorType.PATTERN_MISMATCH


def has_syntax_indicators(text: str) -> bool:
    """Check if text has syntax error indicators."""
    syntax_issues = [
        r'\b\w+\s+\w+\s+\w+\s+\w+\s+\w+\s+\w+\s+\w+',  # Very long phrases
        r'\b(is|are)\s+(is|are)\b',  # Repeated verbs
        r'\b(a|an)\s+(a|an)\b',  # Repeated articles
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in syntax_issues)


def has_temporal_indicators(text: str) -> bool:
    """Check if text has temporal indicators."""
    temporal_words = ['when', 'while', 'before', 'after', 'during', 'until']
    return any(word in text.lower() for word in temporal_words)


def has_modal_indicators(text: str) -> bool:
    """Check if text has modal indicators."""
    modal_words = ['must', 'should', 'can', 'may', 'might', 'could', 'ought']
    return any(word in text.lower() for word in modal_words)


def has_quantifier_indicators(text: str) -> bool:
    """Check if text has quantifier indicators."""
    quantifier_words = ['all', 'every', 'some', 'many', 'few', 'most', 'several']
    return any(word in text.lower() for word in quantifier_words)


class ErrorRecoveryEngine:
    """
    Comprehensive error recovery and suggestion engine.
    Analyzes parsing failures and provides actionable suggestions.
    """
    
    def __init__(self):
        """Initialize error recovery engine."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_error(self, text: str, context: ErrorContext) -> ParseError:
        """Analyze parsing error and generate comprehensive suggestions."""
        return create_comprehensive_error_analysis(text, context)
    
    def suggest_corrections(self, error: ParseError) -> List[str]:
        """Generate specific correction suggestions."""
        return generate_error_corrections(error)
    
    def attempt_recovery(self, text: str, error: ParseError) -> Optional[str]:
        """Attempt to automatically recover from error."""
        return try_automatic_recovery(text, error)


# === HELPER FUNCTIONS ===

def create_comprehensive_error_analysis(text: str, context: ErrorContext) -> ParseError:
    """Create comprehensive error analysis."""
    error_type = detect_error_type(text, context)
    
    error = create_parse_error(
        error_type=error_type,
        message=create_error_message(error_type, text),
        position=context.position,
        text=text
    )
    
    suggestions = generate_comprehensive_suggestions(error_type, text, context)
    return add_suggestions_to_error(error, suggestions)


def create_error_message(error_type: ErrorType, text: str) -> str:
    """Create appropriate error message for type."""
    messages = {
        ErrorType.SYNTAX_ERROR: f"Syntax error in: '{text}'",
        ErrorType.SEMANTIC_ERROR: f"Semantic inconsistency in: '{text}'",
        ErrorType.PATTERN_MISMATCH: f"No matching pattern for: '{text}'",
        ErrorType.TEMPORAL_ERROR: f"Temporal logic error in: '{text}'",
        ErrorType.MODAL_ERROR: f"Modal logic error in: '{text}'",
        ErrorType.QUANTIFIER_ERROR: f"Quantifier usage error in: '{text}'",
        ErrorType.UNKNOWN_ENTITY: f"Unknown entity in: '{text}'"
    }
    return messages.get(error_type, f"Parsing error in: '{text}'")


def generate_comprehensive_suggestions(error_type: ErrorType, text: str, context: ErrorContext) -> List[str]:
    """Generate comprehensive suggestions based on error type."""
    if error_type == ErrorType.SYNTAX_ERROR:
        return analyze_syntax_error(text, context.position)
    elif error_type == ErrorType.SEMANTIC_ERROR:
        return analyze_semantic_error(context.validation_errors)
    elif error_type == ErrorType.PATTERN_MISMATCH:
        return analyze_pattern_mismatch(text, context.attempted_patterns)
    else:
        return ["Try rephrasing the statement more simply"]


def generate_error_corrections(error: ParseError) -> List[str]:
    """Generate specific corrections for error."""
    corrections = []
    
    # Add type-specific corrections
    if error.error_type == ErrorType.SYNTAX_ERROR:
        corrections.extend(error.suggestions)
    
    # Add general corrections
    corrections.append("Try breaking into simpler sentences")
    corrections.append("Use standard subject-verb-object structure")
    
    return corrections


def try_automatic_recovery(text: str, error: ParseError) -> Optional[str]:
    """Attempt automatic error recovery."""
    if error.error_type == ErrorType.SYNTAX_ERROR:
        return attempt_syntax_recovery(text)
    elif error.error_type == ErrorType.PATTERN_MISMATCH:
        return attempt_pattern_recovery(text)
    else:
        return None


def attempt_syntax_recovery(text: str) -> Optional[str]:
    """Attempt to recover from syntax errors."""
    # Simple recovery attempts
    recovered = text
    
    # Add missing articles
    recovered = re.sub(r'\b(person|car|house)\b', r'a \1', recovered)
    
    # Fix verb agreement
    recovered = re.sub(r'\bevery\s+\w+\s+are\b', lambda m: m.group(0).replace('are', 'is'), recovered)
    
    return recovered if recovered != text else None


def attempt_pattern_recovery(text: str) -> Optional[str]:
    """Attempt to recover from pattern matching failures."""
    # Simplify complex structures
    recovered = text
    
    # Simplify temporal expressions
    recovered = re.sub(r'\bwhenever\b', 'when', recovered, flags=re.IGNORECASE)
    recovered = re.sub(r'\bprovided that\b', 'if', recovered, flags=re.IGNORECASE)
    
    return recovered if recovered != text else None


def create_error_recovery_engine() -> ErrorRecoveryEngine:
    """Create error recovery engine instance."""
    return ErrorRecoveryEngine()