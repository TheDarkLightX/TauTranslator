"""
Stable import surface for the CNL (Tau Controlled English) parser.

Historically this lived under `parsers.deprecated.cnl_parser`. We retain
back-compatibility by re-exporting the public modules here.
"""

from ..deprecated.cnl_parser.ast_nodes import *  # noqa: F401,F403
from ..deprecated.cnl_parser.parser import *  # noqa: F401,F403
from ..deprecated.cnl_parser.optimized_parser import *  # noqa: F401,F403


