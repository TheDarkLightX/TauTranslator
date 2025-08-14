"""
Domain types for LLM-assisted Prompt→Spec and Spec→Prompt flows.
Follows ROP with unified Result type.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass(frozen=True)
class PromptToSpecRequest:
    prompt: str
    mode: str  # "assist" | "generate"
    grammar_id: Optional[str] = None
    grammar_version: Optional[str] = None


@dataclass(frozen=True)
class PromptToSpecResponse:
    success: bool
    tce: Optional[str]
    tau: Optional[str]
    reasons: List[str]
    provenance: Dict[str, Any]


@dataclass(frozen=True)
class SpecToPromptRequest:
    spec_text: str  # TCE or Tau
    spec_type: str  # "tce" | "tau"


@dataclass(frozen=True)
class SpecToPromptResponse:
    success: bool
    explanation: str
    provenance: Dict[str, Any]
    # Optional NL prompt paraphrase and structured analysis for UI chips
    prompt_candidate: Optional[str] = None
    analysis: Dict[str, Any] = None  # e.g., {"temporal": True, "implication": True, "quantifiers": ["all"], "time_indices": ["o1","i1"]}


