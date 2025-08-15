"""
Infrastructure layer for Tau Translator core engine.

Currently provides a minimal `GrammarRepository` implementation expected by
the grammar-driven parser and grammar processing services. This is a thin
I/O shell around reading `.lark` and `.tgf` files and a JSON config, keeping
functional core pure.
"""

from .grammar_io import GrammarRepository  # noqa: F401


