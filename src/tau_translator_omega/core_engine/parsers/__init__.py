"""
Public parser package for Tau Translator core engine.

This module provides stable import paths that forward to the currently
maintained implementations. Several legacy modules live under
`parsers.deprecated` and are re-exported here to preserve compatibility
with existing tests and integrations while we complete the refactor.

Do not import from `parsers.deprecated` directly in application code.
Use the stable paths exposed from this package instead, e.g.:

    from tau_translator_omega.core_engine.parsers.cnl_parser import parser

"""

# Expose grammar-driven parser under a stable path
from .grammar_driven_parser import GrammarDrivenParser  # noqa: F401

# Expose CNL/TCE parser package under a stable path
from .cnl_parser import parser as cnl_parser  # noqa: F401


