"""
NLP translation domain types following the Intentional Disclosure Principle.

These immutable domain types replace primitive obsession and provide clear
type boundaries for NLP translation operations.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, NewType, Pattern, Tuple
from enum import Enum
import re

# Domain Type Aliases
NaturalLanguageText = NewType("NaturalLanguageText", str)
TCEText = NewType("TCEText", str)
TAUText = NewType("TAUText", str)
EntityName = NewType("EntityName", str)
PredicateName = NewType("PredicateName", str)
RelationName = NewType("RelationName", str)
PatternTemplate = NewType("PatternTemplate", str)

class PatternType(Enum):
    """Types of language patterns."""
    UNIVERSAL = "universal"
    EXISTENTIAL = "existential"
    NEG_UNIVERSAL = "neg_universal"
    CONDITIONAL = "conditional"
    PREDICATE = "predicate"
    RELATION = "relation"
    ALWAYS_PROPERTY = "always_property"
    DISJUNCTION = "disjunction"
    CONJUNCTION = "conjunction"
    NEGATION = "negation"

class TranslationDirection(Enum):
    """Direction of translation."""
    NL_TO_TCE = "nl_to_tce"
    TCE_TO_NL = "tce_to_nl"
    NL_TO_TAU = "nl_to_tau"
    TAU_TO_NL = "tau_to_nl"

class NormalizationType(Enum):
    """Types of text normalization."""
    WHITESPACE = "whitespace"
    PUNCTUATION = "punctuation"
    CASE = "case"
    ARTICLES = "articles"
    CONTRACTIONS = "contractions"

@dataclass(frozen=True)
class LanguagePattern:
    """Represents a language pattern for matching."""
    pattern_type: PatternType
    regex: Pattern[str]
    template: PatternTemplate
    priority: int = 0
    
    def matches(self, text: str) -> Optional[re.Match]:
        """Check if pattern matches text."""
        return self.regex.match(text)
    
    def extract_groups(self, match: re.Match) -> Dict[str, str]:
        """Extract named groups from match."""
        return {
            f"group_{i}": group
            for i, group in enumerate(match.groups())
            if group is not None
        }

@dataclass(frozen=True)
class PatternMatch:
    """Result of pattern matching."""
    pattern_type: PatternType
    template: PatternTemplate
    matched_groups: Dict[str, str]
    original_text: str
    confidence: float = 1.0

@dataclass(frozen=True)
class TranslationContext:
    """Context for translation operations."""
    vocabulary: Dict[str, Any] = field(default_factory=dict)
    custom_patterns: List[LanguagePattern] = field(default_factory=list)
    normalization_rules: List[NormalizationType] = field(default_factory=list)
    
    def with_vocabulary(self, vocab: Dict[str, Any]) -> 'TranslationContext':
        """Create new context with updated vocabulary."""
        return TranslationContext(
            vocabulary=vocab,
            custom_patterns=self.custom_patterns,
            normalization_rules=self.normalization_rules
        )
    
    def with_pattern(self, pattern: LanguagePattern) -> 'TranslationContext':
        """Add custom pattern to context."""
        new_patterns = list(self.custom_patterns)
        new_patterns.append(pattern)
        return TranslationContext(
            vocabulary=self.vocabulary,
            custom_patterns=new_patterns,
            normalization_rules=self.normalization_rules
        )

@dataclass(frozen=True)
class Entity:
    """Represents an entity in the domain."""
    name: EntityName
    plural_form: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def singular(self) -> str:
        """Get singular form of entity name."""
        name_str = str(self.name)
        if name_str.endswith('s') and self.plural_form is None:
            return name_str[:-1]
        return name_str

@dataclass(frozen=True)
class Predicate:
    """Represents a predicate or property."""
    name: PredicateName
    entity: Optional[EntityName] = None
    modality: Optional[str] = None  # can, must, should, etc.
    negated: bool = False

@dataclass(frozen=True)
class Relation:
    """Represents a relation between entities."""
    name: RelationName
    subject: EntityName
    object: EntityName
    tense: str = "present"
    negated: bool = False

@dataclass(frozen=True)
class Condition:
    """Represents a conditional expression."""
    antecedent: str
    consequent: str
    condition_type: str = "if_then"
    
    def to_tce(self) -> str:
        """Convert to TCE format."""
        return f"if {self.antecedent} then {self.consequent}"
    
    def to_natural(self) -> str:
        """Convert to natural language."""
        return f"If {self.antecedent}, then {self.consequent}"

@dataclass(frozen=True)
class Quantifier:
    """Represents a quantified expression."""
    quantifier_type: PatternType
    variable: EntityName
    constraint: str
    
    def to_tce(self) -> str:
        """Convert to TCE format."""
        if self.quantifier_type == PatternType.UNIVERSAL:
            return f"for every {self.variable} such that {self.constraint}"
        elif self.quantifier_type == PatternType.EXISTENTIAL:
            return f"there exists {self.variable} such that {self.constraint}"
        else:
            return str(self.constraint)

@dataclass(frozen=True)
class TranslationResult:
    """Result of a translation operation."""
    success: bool
    output_text: Optional[str] = None
    pattern_used: Optional[PatternType] = None
    confidence: float = 1.0
    error_message: Optional[str] = None
    
    @classmethod
    def success_result(cls, text: str, pattern: Optional[PatternType] = None) -> 'TranslationResult':
        """Create successful translation result."""
        return cls(
            success=True,
            output_text=text,
            pattern_used=pattern,
            confidence=1.0
        )
    
    @classmethod
    def failure_result(cls, error: str) -> 'TranslationResult':
        """Create failed translation result."""
        return cls(
            success=False,
            error_message=error,
            confidence=0.0
        )

@dataclass(frozen=True)
class PhraseMapping:
    """Maps phrases between natural language and formal representations."""
    natural_phrase: str
    formal_phrase: str
    pattern_type: Optional[PatternType] = None
    priority: int = 0

@dataclass(frozen=True)
class NormalizationRule:
    """Rule for text normalization."""
    rule_type: NormalizationType
    pattern: Pattern[str]
    replacement: str
    
    def apply(self, text: str) -> str:
        """Apply normalization rule to text."""
        return self.pattern.sub(self.replacement, text)

@dataclass(frozen=True)
class TranslationPipeline:
    """Represents a translation pipeline configuration."""
    steps: List[str]
    direction: TranslationDirection
    context: TranslationContext = field(default_factory=TranslationContext)
    
    @property
    def step_count(self) -> int:
        """Number of steps in pipeline."""
        return len(self.steps)