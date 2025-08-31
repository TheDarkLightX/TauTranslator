from __future__ import annotations

import os
import re
import yaml
from typing import Dict, Optional


class PredicateMapper:
    """Config-driven phrase→predicate resolver with fuzzy fallback.

    - Loads a small YAML map at startup or first use.
    - Exact, case-insensitive keys win; otherwise uses contains/fuzzy.
    - Returns empty string when no mapping is found to keep callers pure.
    """

    def __init__(self, yaml_path: Optional[str] = None):
        self._yaml_path = yaml_path or os.getenv(
            "TAU_PREDICATE_MAP_PATH",
            os.path.join(os.path.dirname(__file__), "..", "config", "predicate_map.yaml"),
        )
        self._map: Dict[str, str] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        try:
            with open(self._yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                self._map = {str(k).strip().lower(): str(v).strip() for k, v in dict(data).items()}
        except Exception:
            self._map = {}
        finally:
            self._loaded = True

    def map_phrase(self, phrase: str) -> str:
        self._load()
        s = (phrase or "").strip().lower()
        if not s:
            return ""
        # Exact key match
        if s in self._map:
            return self._map[s]
        # Contains any key as subsequence (simple heuristic)
        for k, v in self._map.items():
            if k in s:
                return v
        # Fuzzy: compare top-3 alphanum tokens
        toks = re.findall(r"[A-Za-z0-9]+", s)
        if toks:
            top = " ".join(toks[:3])
            tokset = set(toks)
            for k, v in self._map.items():
                k_toks = set(re.findall(r"[A-Za-z0-9]+", k))
                if k_toks and k_toks.issubset(tokset):
                    return v
                if all(t in k for t in toks[:2]):
                    return v
                if k.startswith(top):
                    return v
        return ""


