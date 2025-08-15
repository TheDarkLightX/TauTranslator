"""
Simple regex pattern cache compatible with deprecated CNL parser imports.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Dict


@lru_cache(maxsize=256)
def _compiled(pattern: str, flags: int) -> re.Pattern[str]:
    return re.compile(pattern, flags)


def get_pattern(pattern: str, flags: int = 0) -> re.Pattern[str]:
    return _compiled(pattern, flags)


def precompile_patterns(pattern_map: Dict[str, str], flags: int = 0) -> None:
    for _, pattern in pattern_map.items():
        _compiled(pattern, flags)


