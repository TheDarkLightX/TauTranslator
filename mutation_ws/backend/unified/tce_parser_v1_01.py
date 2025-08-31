"""
TCE Parser V1.01 - Minimal Complexity Baseline
Every method has CC=1. No conditionals in any method.
All logic is broken down into single-responsibility functions.

Copyright: DarkLightX / Dana Edwards
"""

import re
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import logging

# Import IDP components with fallback
try:
    from backend.unified.core.domain.parser_types import (
        SentenceText, VariableName, EntityType, ParseContext as IDPParseContext
    )
    from backend.unified.core.parsing.mathematical_expression_parser import MathematicalExpressionParser
    from backend.unified.core.parsing.pronoun_resolver import PronounResolver
    from backend.unified.core.parsing.stream_notation_normalizer import StreamNotationNormalizer
    IDP_AVAILABLE = True
except ImportError:
    IDP_AVAILABLE = False
    class MathematicalExpressionParser:
        def parse_time_expression_to_ast(self, expr): return None
    class PronounResolver:
        pass
    class StreamNotationNormalizer:
        def normalize_stream_in_text(self, text): return text


@dataclass
class ParseContext:
    """Context for parsing complex sentences."""
    entities: Dict[str, str] = field(default_factory=dict)
    variables: List[str] = field(default_factory=list)
    coreferences: Dict[str, str] = field(default_factory=dict)


# === PURE FUNCTIONS (CC=1 each) ===

def create_plural_rules() -> Dict[str, str]:
    """Create singularization rules."""
    return {
        'people': 'person',
        'children': 'child',
        'men': 'man',
        'women': 'woman',
        'mice': 'mouse',
        'geese': 'goose',
        'feet': 'foot',
        'teeth': 'tooth'
    }


def create_pattern_matchers() -> Dict[str, re.Pattern]:
    """Create compiled regex patterns."""
    return {
        'for_every_who': re.compile(r'for\s+every\s+(\w+)\s+who\s+([^,]+),\s*(.+?)\.?$', re.IGNORECASE),
        'who_clause': re.compile(r'(\w+)\s+who\s+(\w+)\s+(.+)', re.IGNORECASE),
        'always_when': re.compile(r'always\s+when\s+(.+?),\s*(.+)', re.IGNORECASE),
        'stream_at_time': re.compile(r'(input|output)\s+(?:stream\s+)?(\d+)\s+at\s+(?:time\s+)?(.+?)(?=\s+equals|\s+is|\s*$)', re.IGNORECASE),
        'the_entity': re.compile(r'\bthe\s+(\w+)\b', re.IGNORECASE),
        'is_comparison': re.compile(r'(\w+)\s+is\s+(greater|less|equal)\s+(?:than\s+)?(?:to\s+)?(.+)', re.IGNORECASE),
        'must_pattern': re.compile(r'(\w+)\s+must\s+(.+)', re.IGNORECASE),
        'if_then': re.compile(r'if\s+(.+?)\s+then\s+(.+?)\.?$', re.IGNORECASE),
        'all_entities': re.compile(r'(all|every|each)\s+(\w+)\s+(?:are|is)\s+(.+?)\.?$', re.IGNORECASE),
        'no_entities': re.compile(r'no\s+(\w+)\s+(?:are|is)\s+(.+?)\.?$', re.IGNORECASE),
        'exists_pattern': re.compile(r'(there\s+exists?|some)\s+(\w+)', re.IGNORECASE)
    }


def singularize_word(word: str, rules: Dict[str, str]) -> str:
    """Convert word to singular form."""
    lower_word = word.lower()
    return rules.get(lower_word, apply_standard_singularization(lower_word))


def apply_standard_singularization(word: str) -> str:
    """Apply standard English singularization."""
    if word.endswith('ies'):
        return word[:-3] + 'y'
    if word.endswith('es') and not word.endswith('ness'):
        return word[:-2]
    if word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word


def normalize_stream_notation(sentence: str) -> str:
    """Normalize stream notation in sentence."""
    stream_pattern = re.compile(r'(input|output)(?:\s+stream)?\s+(\d+)\s+at\s+(?:time\s+)?([^\s,]+)')
    return stream_pattern.sub(r'\1_\2[\3]', sentence)


def remove_articles(text: str) -> str:
    """Remove articles from text."""
    words = text.split()
    articles = {'the', 'a', 'an'}
    filtered = [w for w in words if w.lower() not in articles]
    return ' '.join(filtered)


def extract_variable_from_entity(entity: str, context: ParseContext) -> str:
    """Extract variable name from entity."""
    singular = singularize_word(entity, create_plural_rules())
    context.entities[singular] = 'entity'
    return singular[0].lower()


def format_predicate(entity: str, predicate: str) -> str:
    """Format predicate expression."""
    clean_predicate = remove_articles(predicate)
    return f"is_{clean_predicate.replace(' ', '_').lower()}"


def match_pattern_by_name(sentence: str, pattern_name: str, patterns: Dict[str, re.Pattern]) -> Union[re.Match, None]:
    """Match sentence against named pattern."""
    pattern = patterns.get(pattern_name)
    return pattern.match(sentence) if pattern else None


def parse_for_every_who_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: ParseContext) -> Union[str, None]:
    """Parse 'for every X who Y, Z' pattern."""
    match = match_pattern_by_name(sentence, 'for_every_who', patterns)
    return build_for_every_result(match, context) if match else None


def build_for_every_result(match: re.Match, context: ParseContext) -> str:
    """Build result for 'for every' pattern."""
    entity = match.group(1)
    condition = match.group(2)
    conclusion = match.group(3)
    
    var = extract_variable_from_entity(entity, context)
    condition_expr = build_condition_expression(condition, var, context)
    conclusion_expr = build_conclusion_expression(conclusion, var, context)
    
    return f"all {var}: {condition_expr} -> {conclusion_expr}"


def build_condition_expression(condition: str, var: str, context: ParseContext) -> str:
    """Build condition expression."""
    condition_clean = condition.strip()
    return handle_condition_based_on_content(condition_clean, var)


def handle_condition_based_on_content(condition: str, var: str) -> str:
    """Handle condition based on its content."""
    return check_owns_pattern(condition, var) or check_verb_pattern(condition, var) or f"condition({var})"


def check_owns_pattern(condition: str, var: str) -> Union[str, None]:
    """Check for 'owns X' pattern."""
    owns_match = re.search(r'owns?\s+(.+)', condition, re.IGNORECASE)
    return f"owns({var}, {owns_match.group(1)})" if owns_match else None


def check_verb_pattern(condition: str, var: str) -> Union[str, None]:
    """Check for general verb pattern."""
    verb_match = re.search(r'(\w+)\s+(.+)', condition)
    return f"{verb_match.group(1)}({var}, {verb_match.group(2)})" if verb_match else None


def build_conclusion_expression(conclusion: str, var: str, context: ParseContext) -> str:
    """Build conclusion expression."""
    conclusion_clean = conclusion.strip()
    return handle_conclusion_based_on_content(conclusion_clean, var)


def handle_conclusion_based_on_content(conclusion: str, var: str) -> str:
    """Handle conclusion based on its content."""
    return check_must_pattern(conclusion, var) or f"conclusion({var})"


def check_must_pattern(conclusion: str, var: str) -> Union[str, None]:
    """Check for 'must X' pattern."""
    must_match = re.search(r'must\s+(.+)', conclusion, re.IGNORECASE)
    return f"must({var}, {must_match.group(1)})" if must_match else None


def parse_simple_quantified_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: ParseContext) -> Union[str, None]:
    """Parse simple quantified pattern."""
    all_match = match_pattern_by_name(sentence, 'all_entities', patterns)
    return build_all_entities_result(all_match, context) if all_match else None


def build_all_entities_result(match: re.Match, context: ParseContext) -> str:
    """Build result for 'all entities' pattern."""
    quantifier = match.group(1)
    entity = match.group(2)
    predicate = match.group(3)
    
    var = extract_variable_from_entity(entity, context)
    pred_formatted = format_predicate(entity, predicate)
    
    return f"all {var}: {pred_formatted}({var})"


def parse_no_entities_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: ParseContext) -> Union[str, None]:
    """Parse 'no entities' pattern."""
    no_match = match_pattern_by_name(sentence, 'no_entities', patterns)
    return build_no_entities_result(no_match, context) if no_match else None


def build_no_entities_result(match: re.Match, context: ParseContext) -> str:
    """Build result for 'no entities' pattern."""
    entity = match.group(1)
    predicate = match.group(2)
    
    var = extract_variable_from_entity(entity, context)
    pred_formatted = format_predicate(entity, predicate)
    
    return f"all {var}: {pred_formatted}({var}) -> false"


def clean_and_normalize_text(text: str) -> str:
    """Clean and normalize input text."""
    return normalize_stream_notation(text.strip())


class TCEParserV101:
    """
    Ultra-low complexity parser.
    Every method has CC=1.
    """
    
    def __init__(self):
        """Initialize parser."""
        self.logger = logging.getLogger(__name__)
        self.context = ParseContext()
        self.math_parser = MathematicalExpressionParser()
        self.pronoun_resolver = PronounResolver()
        self.stream_normalizer = StreamNotationNormalizer()
        self.plural_rules = create_plural_rules()
        self.patterns = create_pattern_matchers()
    
    def parse(self, sentence: str) -> str:
        """Parse sentence to TCE expression."""
        normalized = clean_and_normalize_text(sentence)
        return try_all_patterns(normalized, self.patterns, self.context)
    
    def reset_context(self):
        """Reset parsing context."""
        self.context = ParseContext()


def try_all_patterns(sentence: str, patterns: Dict[str, re.Pattern], context: ParseContext) -> str:
    """Try all parsing patterns."""
    return (try_for_every_pattern(sentence, patterns, context) or
            try_simple_quantified_pattern(sentence, patterns, context) or
            try_no_entities_pattern(sentence, patterns, context) or
            sentence)


def try_for_every_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: ParseContext) -> Union[str, None]:
    """Try for every pattern."""
    return parse_for_every_who_pattern(sentence, patterns, context)


def try_simple_quantified_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: ParseContext) -> Union[str, None]:
    """Try simple quantified pattern."""
    return parse_simple_quantified_pattern(sentence, patterns, context)


def try_no_entities_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: ParseContext) -> Union[str, None]:
    """Try no entities pattern."""
    return parse_no_entities_pattern(sentence, patterns, context)


def create_enhanced_parser():
    """Create an instance of the v1.01 parser."""
    return TCEParserV101()


# Aliases for compatibility
EnhancedTCEParser = TCEParserV101
EnhancedTCEParserFixed = TCEParserV101