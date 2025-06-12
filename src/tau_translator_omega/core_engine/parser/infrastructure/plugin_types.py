"""
Plugin type definitions for infrastructure layer.

Minimal interface to avoid circular imports.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Plugin:
    """Minimal plugin interface for parser infrastructure."""
    plugin_type: str
    grammar_config: Optional[Dict[str, Any]] = None
    manifest: Optional[Dict[str, Any]] = None