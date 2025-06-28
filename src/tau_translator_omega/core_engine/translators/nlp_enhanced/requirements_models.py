"""
Data Models for the Requirements Analyzer
=========================================

This module defines the core data structures used by the RequirementsAnalyzer
to represent extracted information from natural language requirements.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List

class RequirementType(Enum):
    """Types of requirements that can be extracted"""
    CONSTRAINT = auto()      # Must/shall constraints
    BEHAVIOR = auto()        # System behavior descriptions
    PERFORMANCE = auto()     # Timing, throughput requirements
    VALIDATION = auto()      # Input validation rules
    OUTPUT = auto()          # Output format requirements
    SECURITY = auto()        # Security and access control
    EXCEPTION = auto()       # Exception handling rules


class RequirementCategory(Enum):
    """Defines the category of a requirement section."""

    FUNCTIONAL = auto()
    NON_FUNCTIONAL = auto()
    UI_UX = auto()
    UNCATEGORIZED = auto()


@dataclass
class LogicalStructure:
    """Represents the logical structure of a requirement"""

    quantifiers: List[str]
    conditionals: List[str]
    logical_operators: List[str]
    temporal_operators: List[str]
    has_quantification: bool = False
    has_conditionals: bool = False
    has_temporal: bool = False


@dataclass
class FormalConstraint:
    """Represents a formal constraint extracted from requirements"""

    constraint_type: str
    variables: List[str]
    predicates: List[str]
    logical_form: str
    confidence: float


@dataclass
class RequirementItem:
    """Represents a single extracted requirement"""

    raw_text: str
    type: RequirementType
    category: RequirementCategory
    entities: List[str]
    predicates: List[str]
    logical_structure: LogicalStructure
    formal_constraints: List[FormalConstraint]
    confidence: float
    has_quantification: bool = False
