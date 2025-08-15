"""
Legacy import shim: expose CNLParser and related symbols under
`parsers.cnl_parser.cnl_parser` for backward compatibility.
"""

from ..deprecated.cnl_parser.cnl_parser import *  # noqa: F401,F403


