"""
Lightweight shim to expose the grammar-driven parser under a stable path.

The implementation currently lives in `parsers.deprecated.grammar_driven_parser`
while refactoring is in progress. This module forwards imports to avoid
breaking external integrations and tests.
"""

from .deprecated.grammar_driven_parser import *  # noqa: F401,F403


