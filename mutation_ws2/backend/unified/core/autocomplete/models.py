"""
Domain models for educational autocomplete system following the Intentional Disclosure Principle.

All types are immutable and maximize disclosure through the type system.
No primitive obsession - every domain concept has its own type.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass, field
from typing import Optional, List, NewType, Literal
from enum import Enum

# =======================
# Domain Type Aliases (Rule 3: Maximize Disclosure via Type System)
# =======================

SuggestionText = NewType("SuggestionText", str)
DisplayText = NewType("DisplayText", str)
HintText = NewType("HintText", str)
ExampleCode = NewType("ExampleCode", str)
TemplatePattern = NewType("TemplatePattern", str)
TauCode = NewType("TauCode", str)
TcePattern = NewType("TcePattern", str)
CursorPosition = NewType("CursorPosition", int)
ConfidenceScore = NewType("ConfidenceScore", float)

class SuggestionCategory(Enum):
    """Categories of suggestions for clear classification."""
    KEYWORD = "keyword"
    OPERATOR = "operator"
    TEMPORAL = "temporal"
    QUANTIFIER = "quantifier"
    DEFINITION = "definition"
    PATTERN = "pattern"
    TEMPLATE = "template"
    STREAM = "stream"
    SOLVER = "solver"

class DifficultyLevel(Enum):
    """Learning difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class LanguageMode(Enum):
    """Language being edited."""
    TAU = "TAU"
    TCE = "TCE"

class ContextType(Enum):
    """Type of specification context."""
    FUNCTION_DEFINITION = "function_definition"
    TEMPORAL_CONSTRAINT = "temporal_constraint"
    STREAM_RULE = "stream_rule"
    LOGICAL_ASSERTION = "logical_assertion"
    SOLVER_COMMAND = "solver_command"
    QUANTIFIER_EXPRESSION = "quantifier_expression"
    BOOLEAN_EXPRESSION = "boolean_expression"
    ARITHMETIC_EXPRESSION = "arithmetic_expression"

# =======================
# Core Domain Models
# =======================

@dataclass(frozen=True)
class EducationalSuggestion:
    """
    Immutable suggestion with educational metadata.
    Follows Rule 3: Rich type disclosure.
    """
    text: SuggestionText
    display: DisplayText
    category: SuggestionCategory
    description: HintText
    example: ExampleCode
    difficulty: DifficultyLevel
    template: Optional[TemplatePattern] = None
    tau_equivalent: Optional[TauCode] = None  # For TCE suggestions
    related_concepts: List[str] = field(default_factory=list)
    confidence: ConfidenceScore = ConfidenceScore(1.0)
    
    def is_high_confidence(self) -> bool:
        """Check if this is a high-confidence suggestion."""
        return self.confidence >= 0.8

@dataclass(frozen=True)
class SpecificationContext:
    """
    Immutable context for analyzing current specification state.
    Provides complete disclosure of editing context.
    """
    full_text: str
    cursor_position: CursorPosition
    language_mode: LanguageMode
    context_type: ContextType
    parent_constructs: List[str] = field(default_factory=list)
    variables_in_scope: List[str] = field(default_factory=list)
    learning_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    
    def get_text_before_cursor(self) -> str:
        """Get text before cursor position."""
        return self.full_text[:self.cursor_position]
    
    def get_current_line(self) -> str:
        """Get the current line being edited."""
        lines = self.full_text[:self.cursor_position].split('\n')
        return lines[-1] if lines else ""

@dataclass(frozen=True)
class SuggestionRequest:
    """Request for autocomplete suggestions."""
    context: SpecificationContext
    max_suggestions: int = 10
    include_templates: bool = True
    include_examples: bool = True

@dataclass(frozen=True)
class SuggestionResponse:
    """Response containing educational suggestions."""
    suggestions: List[EducationalSuggestion]
    context_hint: Optional[HintText] = None
    learning_tip: Optional[HintText] = None

# =======================
# Pattern Definitions
# =======================

@dataclass(frozen=True)
class TauPattern:
    """TAU language pattern definition."""
    pattern: str
    category: SuggestionCategory
    description: str
    example: str
    difficulty: DifficultyLevel
    keywords: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class TcePattern:
    """TCE (Controlled English) pattern definition."""
    english_pattern: TcePattern
    tau_equivalent: TauCode
    description: str
    example: str
    difficulty: DifficultyLevel

# =======================
# Learning Models
# =======================

@dataclass(frozen=True)
class LearningHint:
    """Educational hint for a concept."""
    concept: str
    explanation: str
    examples: List[ExampleCode]
    related_concepts: List[str]
    difficulty: DifficultyLevel

@dataclass(frozen=True)
class ProgressionPath:
    """Learning progression from beginner to advanced."""
    concept: str
    beginner_version: str
    intermediate_version: str
    advanced_version: str
    explanation: str