"""
Domain types and data classes for requirements analysis.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, NewType
from dataclasses import dataclass, field
from enum import Enum, auto

# Domain Types (Rule 3: Maximize Disclosure via Type System)
RequirementText = NewType("RequirementText", str)
SentenceText = NewType("SentenceText", str)
SectionTitle = NewType("SectionTitle", str)
SectionContent = NewType("SectionContent", str)
EntityName = NewType("EntityName", str)
PredicateName = NewType("PredicateName", str)
ConfidenceScore = NewType("ConfidenceScore", float)
LogicalFormula = NewType("LogicalFormula", str)
PatternType = NewType("PatternType", str)


class RequirementType(Enum):
    """Types of requirements that can be extracted."""
    CONSTRAINT = auto()
    BEHAVIOR = auto()
    PERFORMANCE = auto()
    VALIDATION = auto()
    OUTPUT = auto()
    SECURITY = auto()
    EXCEPTION = auto()


@dataclass(frozen=True)
class LogicalStructure:
    """Represents the logical structure of a requirement."""
    quantifiers: List[str] = field(default_factory=list)
    conditionals: List[str] = field(default_factory=list)
    logical_operators: List[str] = field(default_factory=list)
    temporal_operators: List[str] = field(default_factory=list)
    
    @property
    def has_quantification(self) -> bool:
        """Check if structure has quantification."""
        return len(self.quantifiers) > 0
    
    @property
    def has_conditionals(self) -> bool:
        """Check if structure has conditionals."""
        return len(self.conditionals) > 0
    
    @property
    def has_temporal(self) -> bool:
        """Check if structure has temporal operators."""
        return len(self.temporal_operators) > 0


@dataclass(frozen=True)
class FormalConstraint:
    """Represents a formal constraint extracted from requirements."""
    constraint_type: str
    variables: List[str]
    predicates: List[str]
    logical_form: LogicalFormula
    confidence: ConfidenceScore


@dataclass(frozen=True)
class RequirementItem:
    """Represents a single extracted requirement."""
    raw_text: RequirementText
    type: RequirementType
    category: str
    entities: List[EntityName]
    predicates: List[PredicateName]
    logical_structure: LogicalStructure
    formal_constraints: List[FormalConstraint]
    confidence: ConfidenceScore
    
    @property
    def has_quantification(self) -> bool:
        """Check if requirement has quantification."""
        return self.logical_structure.has_quantification