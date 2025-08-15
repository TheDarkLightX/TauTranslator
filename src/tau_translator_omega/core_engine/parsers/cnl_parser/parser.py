"""
Stable shim for CNL/TCE parser.

For CNL (Tau Controlled English), prefer the O(n) Pratt-based `CNLParser`
implementation as the canonical parser. This preserves compatibility for
`from ...cnl_parser.parser import CNLParser` imports.
"""

from ..deprecated.cnl_parser.cnl_parser import *  # noqa: F401,F403


