"""
TCE (Tau Controlled English) Domain Types
Copyright: DarkLightX/Dana Edwards

Defines types for TCE representation following craftsmanship principles.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class TCEPattern(str, Enum):
    """Standard TCE patterns."""
    DEFINITION = "definition"
    FACT = "fact"
    RULE = "rule"
    FUNCTION = "function"
    PREDICATE = "predicate"
    CONSTRAINT = "constraint"
    ASSERTION = "assertion"
    QUANTIFICATION = "quantification"


@dataclass(frozen=True)
class TCEBinding:
    """Binding of variables in TCE patterns."""
    variable: str
    value: str
    type_hint: Optional[str] = None


@dataclass(frozen=True)
class TCEStatement:
    """A single TCE statement."""
    pattern: str
    bindings: Dict[str, str]
    constraints: List[str] = None
    metadata: Dict[str, str] = None


@dataclass(frozen=True)
class TCEDocument:
    """A collection of TCE statements forming a document."""
    statements: List[TCEStatement]
    title: Optional[str] = None
    metadata: Dict[str, str] = None