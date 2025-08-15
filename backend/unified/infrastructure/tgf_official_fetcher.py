"""
Fetch the official Tau TGF grammar from IDNI repositories without embedding it.

Respects licensing by downloading at runtime into the configured grammar dir.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path
from typing import Optional

from ..core.result_enhanced import Result, Success, Failure


DEFAULT_TGF_URL = (
    "https://raw.githubusercontent.com/IDNI/tau-lang/main/grammar/rr.tgf"
)


def download_official_tgf(destination_dir: str, filename: str = "official_rr.tgf", url: Optional[str] = None) -> Result[str]:
    try:
        dest = Path(destination_dir)
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / filename
        remote = url or DEFAULT_TGF_URL
        with urllib.request.urlopen(remote, timeout=20) as response:  # nosec - controlled URL
            content = response.read()
        target.write_bytes(content)
        return Success(str(target))
    except Exception as e:
        return Failure("DOWNLOAD_ERROR", str(e))


