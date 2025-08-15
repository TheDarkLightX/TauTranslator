"""
Adapts the Lark parsing library for use in the railway-oriented pipeline.

This module provides a safe, isolated interface to the parsing engine. Its primary
responsibility is to take raw text and attempt to parse it into an Abstract
Syntax Tree (AST). The outcome is wrapped in a `Result` container, which allows
the orchestrating service to handle parsing failures as a predictable data path
rather than as an unexpected exception.

Copyright: DarkLightX / Dana Edwards
"""

from returns.result import Result, Success, Failure
from tau_translator_omega.core_engine.autocomplete.domain import AutocompleteError

# Route to canonical Pratt-based CNL parser for tests until Lark grammar is harmonized.
try:
    from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser
except Exception:  # pragma: no cover
    from src.tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser


def parse_text_to_ast(text: str) -> Result[object, AutocompleteError]:
    """Parse text to an AST using the canonical CNL parser and wrap in Result."""
    try:
        parser = CNLParser()
        ast = parser.parse(text)
        return Success(ast)
    except Exception:
        return Failure(AutocompleteError.PARSING_ERROR)
