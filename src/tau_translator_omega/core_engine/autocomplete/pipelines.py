"""
Defines the pure, declarative pipelines for the autocomplete service.

This module contains the core business logic for generating suggestions. It is
composed of small, testable, pure functions that form a railway-oriented pipeline
for transforming context into a list of scored suggestions.

Copyright: DarkLightX / Dana Edwards
"""

from spacy.tokens import Doc
from lark import Tree
from returns.result import Success
from toolz import compose, pipe

from tau_translator_omega.core_engine.autocomplete.domain import (
    AutocompleteResult,
    Suggestion,
    SuggestionType,
)

# A simple, static list of keywords. In a more advanced implementation,
# this could be dynamically generated from the grammar or other sources.
ALL_KEYWORDS = [
    "always", "sometimes", "let", "define", "the", "expression", "for all",
    "there exists", "->", "&&", "||", "!",
]


def _find_prefix(doc: Doc) -> str:
    """Identifies the token or token fragment the user is currently typing."""
    # This logic assumes the cursor is at the end of the text.
    # A more robust implementation would use the cursor position from the request.
    last_token = doc[-1].text_with_ws.rstrip()
    return last_token


def _find_keyword_suggestions(prefix: str) -> list[Suggestion]:
    """Filters the global keyword list based on the prefix."""
    if not prefix:
        return []
    
    return [
        Suggestion(
            text=keyword,
            type=SuggestionType.KEYWORD,
            score=0.9,  # Base score for a keyword match
            description=f"A core language keyword."
        )
        for keyword in ALL_KEYWORDS if keyword.startswith(prefix)
    ]


def _score_suggestions(suggestions: list[Suggestion]) -> list[Suggestion]:
    """Applies scoring logic to a list of suggestions. (Placeholder)"""
    # Future logic could adjust scores based on AST context, etc.
    return sorted(suggestions, key=lambda s: s.score, reverse=True)


def generate_suggestions_from_context(
    context: tuple[Tree, Doc]
) -> AutocompleteResult:
    """Generates autocomplete suggestions from the given AST and NLP doc.

    This is the primary entry point into the pure core logic. It uses a
    declarative pipeline to transform the input context into a final, scored
    list of suggestions, wrapped in a `Success` container.

    Args:
        context: A tuple containing the parsed AST and the spaCy Doc.

    Returns:
        An `AutocompleteResult` containing the list of suggestions.
    """
    _, doc = context

    # This is a declarative pipeline using toolz.pipe
    result: list[Suggestion] = pipe(
        doc,
        _find_prefix,
        _find_keyword_suggestions,
        _score_suggestions,
    )

    return Success(result)
