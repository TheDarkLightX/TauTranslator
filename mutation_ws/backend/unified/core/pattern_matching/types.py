"""
Shared data types for the pattern matching engine.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class MatchResult:
    """Represents a single, successful pattern match."""

    pattern_id: str
    start_pos: int
    end_pos: int
    matched_text: str
    replacement: Optional[str] = None
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
