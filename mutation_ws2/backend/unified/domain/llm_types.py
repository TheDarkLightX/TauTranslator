"""
Domain types for LLM-assisted Prompt→Spec and Spec→Prompt flows.
Follows ROP with unified Result type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    # Optional high-level intent and better prompt suggestions
    intent: Optional[str] = None
    prompt_suggestions: List[str] = field(default_factory=list)
    # Optional extended NLP analysis and refinements
    nlp_analysis: Dict[str, Any] = field(default_factory=dict)
    refined_prompt: Optional[str] = None
    refined_options: List[str] = field(default_factory=list)
    # New: ambiguity/clarification metadata
    ambiguity_score: Optional[float] = None
    ambiguity_facets: List[str] = field(default_factory=list)
    clarifying_questions: List[Dict[str, Any]] = field(default_factory=list)  # [{"question": str, "options": [str]}]
    chosen_cut: Optional[Dict[str, Any]] = None  # lattice cut or decisions applied


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
    # Optional verification metadata for faithful explanations
    verification: Optional[Dict[str, Any]] = None  # e.g., {"equations":19, "helpers_present":{"full3":true}}


