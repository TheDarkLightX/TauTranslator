#!/usr/bin/env python3
"""
Compatibility shim for health.py

This module has been refactored into a modular structure following the 
Intentional Disclosure Principle. Please update your imports to use 
health_router instead.

This shim provides backward compatibility during the migration period.

Copyright: DarkLightX / Dana Edwards
"""

import warnings
from .health_router import router

warnings.warn(
    "health module has been refactored into a modular structure. "
    "Please update your imports to use health_router.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export router for backward compatibility
__all__ = ['router']
