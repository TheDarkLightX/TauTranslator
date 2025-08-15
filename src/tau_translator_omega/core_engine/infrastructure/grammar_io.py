"""
Filesystem-backed GrammarRepository for loading Tau grammar files.

This is an imperative shell that reads from two locations:
- A directory containing `.lark` grammars used directly by Lark
- A JSON config file listing available grammars, with optional metadata

All methods return `returns.result.Result` values to support ROP.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any

from returns.result import Result, Success, Failure


class GrammarRepository:
    """
    Reads grammar configuration and files from disk.

    Parameters
    - grammar_dir: Directory containing `.lark` grammars
    - config_file: JSON file listing grammars and which is active
    """

    def __init__(self, grammar_dir: Path, config_file: Path):
        self._grammar_dir = Path(grammar_dir)
        self._config_file = Path(config_file)

    def read_grammar_config(self) -> Result[List[Dict[str, Any]], str]:
        """Load grammar configuration JSON.

        Returns Success[list] or Failure[str].
        """
        try:
            if not self._config_file.exists():
                return Failure(f"Config file not found: {self._config_file}")
            data = json.loads(self._config_file.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return Failure("Grammar config must be a JSON array of definitions")
            return Success(data)
        except Exception as exc:
            return Failure(f"Failed to read grammar config: {exc}")

    def write_grammar_config(self, configs: List[Dict[str, Any]]) -> Result[None, str]:
        """Persist updated grammar configuration JSON."""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            self._config_file.write_text(json.dumps(configs, indent=2), encoding="utf-8")
            return Success(None)
        except Exception as exc:
            return Failure(f"Failed to write grammar config: {exc}")

    def read_grammar_file(self, filename: str) -> Result[str, str]:
        """Read a grammar file from the grammar directory."""
        try:
            path = (self._grammar_dir / filename).resolve()
            if not path.exists():
                return Failure(f"Grammar file not found: {path}")
            content = path.read_text(encoding="utf-8")
            return Success(content)
        except Exception as exc:
            return Failure(f"Failed to read grammar file '{filename}': {exc}")


