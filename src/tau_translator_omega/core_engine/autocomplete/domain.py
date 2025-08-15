"""
Defines the core data contracts for the NLP-powered autocomplete service.

This module establishes a rich, statically-typed domain model that serves as the
foundation for the railway-oriented processing pipeline. It uses Enums for
categorical data and dataclasses for structured data, ensuring that all inputs,
outputs, and potential errors are explicit and type-safe.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeAlias

from returns.result import Result


class AutocompleteError(Enum):
    """Enumerates the possible failures in the autocomplete pipeline."""
    PARSING_ERROR = auto()  # Input text could not be parsed into an AST.
    INSUFFICIENT_CONTEXT = auto()  # Not enough information to provide suggestions.
    NLP_PROCESSING_FAILED = auto()  # The NLP model failed to process the text.
    SUGGESTION_GENERATION_FAILED = auto()  # The core suggestion logic failed.


class SuggestionType(Enum):
    """Categorizes the type of an autocomplete suggestion."""
    KEYWORD = auto()  # A language keyword (e.g., 'always', 'let').
    CONSTANT = auto()  # A defined constant.
    FUNCTION = auto()  # A defined function.
    TEMPLATE = auto()  # A boilerplate snippet (e.g., a full expression).


@dataclass(frozen=True)
class AutocompleteRequest:
    """Represents the input for an autocomplete request."""
    text: str
    cursor_position: int


@dataclass(frozen=True)
class Suggestion:
    """Represents a single, rich autocomplete suggestion."""
    text: str
    type: SuggestionType
    score: float  # A value from 0.0 to 1.0 indicating relevance.
    description: str | None = None  # An educational hint or description.
    example: str | None = None  # An example of usage.


# The primary type for the entire autocomplete pipeline.
# It will either succeed with a list of suggestions or fail with a specific error.
AutocompleteResult: TypeAlias = Result[list[Suggestion], AutocompleteError]
