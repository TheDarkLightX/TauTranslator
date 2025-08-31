from dataclasses import dataclass, field
from typing import List


class AppError(Exception):
    """Base class for application-specific errors."""
    pass


@dataclass(frozen=True)
class TranslationError(AppError):
    """Base class for translation-related errors."""
    message: str


@dataclass(frozen=True)
class ParsingError(TranslationError):
    """Represents an error during parsing."""
    line: int | None = None
    column: int | None = None


@dataclass(frozen=True)
class SemanticError(TranslationError):
    """Represents an error during semantic analysis (e.g., type checking)."""
    pass


@dataclass(frozen=True)
class LLMError(TranslationError):
    """Represents an error from the LLM service."""
    pass


@dataclass(frozen=True)
class GrammarError(TranslationError):
    """Represents an error related to the grammar definition itself."""
    pass
