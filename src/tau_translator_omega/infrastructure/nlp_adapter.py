"""
Adapts the spaCy NLP library for use in the railway-oriented pipeline.

This module handles the impure operations of loading a spaCy model from disk and
processing raw text to extract linguistic features (e.g., POS tags, dependency
parses). It wraps these potentially fallible operations in `Result` containers,
ensuring that failures are handled as predictable data rather than exceptions.

Copyright: DarkLightX / Dana Edwards
"""

import spacy
from spacy.language import Language
from spacy.tokens import Doc
from returns.result import Result, Success, Failure, safe

from tau_translator_omega.core_engine.autocomplete.domain import AutocompleteError

# A simple cache for the loaded NLP model to avoid reloading it on every call.
_nlp_model: Language | None = None


@safe
def _load_model() -> Language:
    """Loads the spaCy model. Decorated with @safe to catch exceptions."""
    global _nlp_model
    if _nlp_model is None:
        _nlp_model = spacy.load("en_core_web_sm")
    return _nlp_model


def get_nlp_model() -> Result[Language, AutocompleteError]:
    """Safely gets the singleton instance of the spaCy language model.

    Returns:
        A `Success` containing the spaCy `Language` object.
        A `Failure` if the model cannot be loaded.
    """
    return _load_model().alt(lambda _: Failure(AutocompleteError.NLP_PROCESSING_FAILED))


def extract_linguistic_features(text: str, nlp: Language) -> Result[Doc, AutocompleteError]:
    """Processes text to extract linguistic features using spaCy.

    Args:
        text: The raw input string to process.
        nlp: The loaded spaCy language model.

    Returns:
        A `Success` containing the processed `Doc` object.
        A `Failure` if NLP processing fails.
    """
    try:
        doc = nlp(text)
        return Success(doc)
    except Exception:
        return Failure(AutocompleteError.NLP_PROCESSING_FAILED)
