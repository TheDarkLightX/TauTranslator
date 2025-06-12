"""
NLP infrastructure layer following the Intentional Disclosure Principle.

Isolates all pattern matching, text processing, and I/O operations
from business logic according to IDP Rule 4.

Copyright: DarkLightX / Dana Edwards
"""

import re
import logging
from typing import List, Dict, Optional, Any
from returns.result import Result, Success, Failure

from ..domain.nlp_types import (
    LanguagePattern, PatternType, PatternTemplate, NormalizationType,
    NormalizationRule
)

logger = logging.getLogger(__name__)


class PatternRegistry:
    """Registry of language patterns for NLP translation."""
    
    @staticmethod
    def get_default_patterns() -> List[LanguagePattern]:
        """Get default language patterns."""
        return [
            # Universal quantifiers
            LanguagePattern(
                pattern_type=PatternType.UNIVERSAL,
                regex=re.compile(r'\b(all|every|each)\s+(\w+)s?\s+(.*)', re.I),
                template=PatternTemplate('for every {1} such that {2}'),
                priority=10
            ),
            
            # Existential quantifiers
            LanguagePattern(
                pattern_type=PatternType.EXISTENTIAL,
                regex=re.compile(r'\b(some|a|an)\s+(\w+)\s+(.*)', re.I),
                template=PatternTemplate('there exists {1} such that {2}'),
                priority=10
            ),
            
            # Negated universal
            LanguagePattern(
                pattern_type=PatternType.NEG_UNIVERSAL,
                regex=re.compile(r'\b(no|none|nobody)\s+(.*)', re.I),
                template=PatternTemplate('for every x such that not {1}'),
                priority=9
            ),
            
            # Conditionals
            LanguagePattern(
                pattern_type=PatternType.CONDITIONAL,
                regex=re.compile(r'^if\s+(.*?)[,;]\s*then\s+(.*)', re.I),
                template=PatternTemplate('if {0} then {1}'),
                priority=8
            ),
            
            # Simple predicates
            LanguagePattern(
                pattern_type=PatternType.PREDICATE,
                regex=re.compile(r'^(\w+)\s+is\s+(\w+)$', re.I),
                template=PatternTemplate('{0} is {1}'),
                priority=5
            ),
            
            # Relations
            LanguagePattern(
                pattern_type=PatternType.RELATION,
                regex=re.compile(r'^(\w+)\s+(loves?|has|knows?|sees?)\s+(\w+)$', re.I),
                template=PatternTemplate('{1}({0}, {2})'),
                priority=6
            ),
            
            # Properties with "always"
            LanguagePattern(
                pattern_type=PatternType.ALWAYS_PROPERTY,
                regex=re.compile(r'^(the\s+)?(\w+)\s+is\s+always\s+(\w+)$', re.I),
                template=PatternTemplate('always {1} is {2}'),
                priority=7
            ),
            
            # Either/or
            LanguagePattern(
                pattern_type=PatternType.DISJUNCTION,
                regex=re.compile(r'^either\s+(.*?)\s+or\s+(.*)', re.I),
                template=PatternTemplate('{0} or {1}'),
                priority=6
            )
        ]
    
    @staticmethod
    def load_custom_patterns(pattern_file: str) -> Result[List[LanguagePattern], str]:
        """Load custom patterns from file."""
        try:
            # This would load patterns from a configuration file
            # For now, return empty list
            logger.info(f"Loading custom patterns from {pattern_file}")
            return Success([])
        except Exception as e:
            return Failure(f"Failed to load patterns: {e}")


class TextNormalizer:
    """Handles text normalization operations."""
    
    @staticmethod
    def get_default_rules() -> List[NormalizationRule]:
        """Get default normalization rules."""
        return [
            # Whitespace normalization
            NormalizationRule(
                rule_type=NormalizationType.WHITESPACE,
                pattern=re.compile(r'\s+'),
                replacement=' '
            ),
            
            # Remove trailing punctuation except period
            NormalizationRule(
                rule_type=NormalizationType.PUNCTUATION,
                pattern=re.compile(r'[,;:!?]+$'),
                replacement=''
            ),
            
            # Remove articles in specific contexts
            NormalizationRule(
                rule_type=NormalizationType.ARTICLES,
                pattern=re.compile(r'\b(the|a|an)\s+', re.I),
                replacement=''
            ),
            
            # Expand contractions
            NormalizationRule(
                rule_type=NormalizationType.CONTRACTIONS,
                pattern=re.compile(r"can't", re.I),
                replacement='cannot'
            ),
            NormalizationRule(
                rule_type=NormalizationType.CONTRACTIONS,
                pattern=re.compile(r"won't", re.I),
                replacement='will not'
            ),
            NormalizationRule(
                rule_type=NormalizationType.CONTRACTIONS,
                pattern=re.compile(r"n't", re.I),
                replacement=' not'
            ),
            NormalizationRule(
                rule_type=NormalizationType.CONTRACTIONS,
                pattern=re.compile(r"'re", re.I),
                replacement=' are'
            ),
            NormalizationRule(
                rule_type=NormalizationType.CONTRACTIONS,
                pattern=re.compile(r"'ve", re.I),
                replacement=' have'
            ),
            NormalizationRule(
                rule_type=NormalizationType.CONTRACTIONS,
                pattern=re.compile(r"'ll", re.I),
                replacement=' will'
            ),
            NormalizationRule(
                rule_type=NormalizationType.CONTRACTIONS,
                pattern=re.compile(r"'d", re.I),
                replacement=' would'
            )
        ]
    
    @staticmethod
    def normalize_text(text: str, rules: List[NormalizationRule]) -> str:
        """Apply normalization rules to text."""
        normalized = text.strip()
        
        for rule in rules:
            normalized = rule.apply(normalized)
        
        # Final cleanup
        normalized = normalized.strip()
        
        # Ensure ends with period for TCE format
        if normalized and not normalized.endswith('.'):
            normalized += '.'
        
        return normalized
    
    @staticmethod
    def clean_input(text: str) -> str:
        """Basic input cleaning."""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned


class PhraseMapper:
    """Maps phrases between natural language and formal representations."""
    
    COMMON_PHRASES = {
        # Modal mappings
        "can": "can",
        "must": "must",
        "should": "should",
        "might": "might",
        "could": "can",
        
        # Logical connectives
        "and": "and",
        "or": "or",
        "but": "and",
        "however": "and",
        
        # Quantifier phrases
        "at least one": "exists",
        "there is": "exists",
        "for each": "for every",
        "for all": "for every",
        
        # Temporal phrases
        "always": "always",
        "never": "never",
        "sometimes": "sometimes",
        
        # Conditional phrases
        "implies": "implies",
        "if and only if": "iff",
        "when": "if",
        "whenever": "if"
    }
    
    @staticmethod
    def map_phrase(phrase: str) -> str:
        """Map common phrase to formal representation."""
        phrase_lower = phrase.lower().strip()
        return PhraseMapper.COMMON_PHRASES.get(phrase_lower, phrase)
    
    @staticmethod
    def reverse_map_phrase(formal_phrase: str) -> str:
        """Map formal representation back to natural language."""
        # Create reverse mapping
        reverse_map = {v: k for k, v in PhraseMapper.COMMON_PHRASES.items()}
        
        # Special cases for reverse mapping
        reverse_map.update({
            "for every": "every",
            "exists": "some",
            "and": "and",
            "or": "or",
            "iff": "if and only if"
        })
        
        return reverse_map.get(formal_phrase.lower(), formal_phrase)


class EntityExtractor:
    """Extracts entities and their properties from text."""
    
    @staticmethod
    def extract_entity_from_phrase(phrase: str) -> Result[Dict[str, str], str]:
        """Extract entity information from a phrase."""
        words = phrase.strip().split()
        
        if not words:
            return Failure("Empty phrase")
        
        # Simple extraction - last noun-like word
        entity = None
        modifiers = []
        
        for word in reversed(words):
            if word.isalpha() and len(word) > 1:
                if entity is None:
                    entity = word
                else:
                    modifiers.append(word)
        
        if entity is None:
            return Failure("No entity found in phrase")
        
        return Success({
            "entity": entity.lower(),
            "modifiers": list(reversed(modifiers)),
            "original": phrase
        })
    
    @staticmethod
    def singularize(word: str) -> str:
        """Simple singularization of plural nouns."""
        if word.endswith('ies'):
            return word[:-3] + 'y'
        elif word.endswith('es'):
            return word[:-2]
        elif word.endswith('s') and not word.endswith('ss'):
            return word[:-1]
        return word
    
    @staticmethod
    def pluralize(word: str) -> str:
        """Simple pluralization of singular nouns."""
        if word.endswith('y') and len(word) > 2 and word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
        elif word.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return word + 'es'
        else:
            return word + 's'


class TemplateProcessor:
    """Processes template strings with variable substitution."""
    
    @staticmethod
    def apply_template(template: str, groups: Dict[str, str]) -> str:
        """Apply template with group substitutions."""
        result = template
        
        # Replace {0}, {1}, etc. with corresponding groups
        for i in range(10):  # Support up to 10 groups
            key = f"group_{i}"
            if key in groups:
                placeholder = f"{{{i}}}"
                result = result.replace(placeholder, groups[key])
        
        return result
    
    @staticmethod
    def extract_variables_from_template(template: str) -> List[int]:
        """Extract variable indices from template."""
        import re
        pattern = r'\{(\d+)\}'
        matches = re.findall(pattern, template)
        return [int(m) for m in matches]


class TCEPatternMatcher:
    """Matches TCE patterns for reverse translation."""
    
    TCE_PATTERNS = [
        # Universal quantifier
        (re.compile(r'^for\s+every\s+(\w+)\s+such\s+that\s+(.+)$', re.I),
         'universal', 'Every {0} {1}'),
        
        # Existential quantifier
        (re.compile(r'^there\s+exists\s+(\w+)\s+such\s+that\s+(.+)$', re.I),
         'existential', 'Some {0} {1}'),
        
        # Conditional
        (re.compile(r'^if\s+(.+?)\s+then\s+(.+)$', re.I),
         'conditional', 'If {0}, then {1}'),
        
        # Always property
        (re.compile(r'^always\s+(\w+)\s+is\s+(\w+)$', re.I),
         'always', 'The {0} is always {1}'),
        
        # Simple predicate
        (re.compile(r'^(\w+)\s+is\s+(\w+)$', re.I),
         'predicate', '{0} is {1}'),
        
        # Relation
        (re.compile(r'^(\w+)\((.*?),\s*(.*?)\)$', re.I),
         'relation', '{1} {0} {2}')
    ]
    
    @staticmethod
    def match_tce_pattern(text: str) -> Optional[tuple]:
        """Match TCE text against patterns."""
        for pattern, pattern_type, template in TCEPatternMatcher.TCE_PATTERNS:
            match = pattern.match(text.strip())
            if match:
                return pattern_type, template, match
        return None