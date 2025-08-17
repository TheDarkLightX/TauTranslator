from __future__ import annotations

import json
import os
import re
from threading import RLock
from typing import Dict, Optional, List


def _normalize_phrase(text: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", text.lower())
    stop = {
        "the","a","an","to","and","or","of","for","in","on","over","under",
        "with","without","if","then","when","whenever","through","by","at","no",
        "time","circumstances","any","each","every","all","must","should","shall",
        "do","not","never","cannot","can","please","now","strictly","ensure","make",
        "sure","that"
    }
    kept = [t for t in tokens if t not in stop]
    return "_".join(kept)[:64]


class AlignmentCache:
    """Lightweight phrase→predicate alignment cache.

    - suggest_predicate(phrase): returns a predicate name if known
    - update_from_translation(prompt, tau): learns alignments heuristically

    Storage is best-effort: saves to data/alignment_cache.json if writable; otherwise stays in-memory.
    """

    def __init__(self, path: Optional[str] = None) -> None:
        self._lock = RLock()
        self._path = path or os.path.abspath(os.path.join("data", "alignment_cache.json"))
        self._map: Dict[str, str] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        with self._lock:
            if self._loaded:
                return
            try:
                if os.path.exists(self._path):
                    with open(self._path, "r", encoding="utf-8") as f:
                        self._map = json.load(f)
            except Exception:
                self._map = {}
            finally:
                self._loaded = True

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._map, f, ensure_ascii=False, indent=2)
        except Exception:
            # ignore persistence errors
            pass

    def suggest_predicate(self, phrase: str) -> Optional[str]:
        self._load()
        key = _normalize_phrase(phrase)
        if not key:
            return None
        with self._lock:
            # exact
            if key in self._map:
                return self._map[key]
            # prefix/backoff search
            for k, v in self._map.items():
                if key.startswith(k) or k.startswith(key):
                    return v
        return None

    def update_from_translation(self, prompt: str, tau: str) -> None:
        """Heuristically learn alignments from prompt and accepted Tau.

        Extracts predicate names from Tau and tries to align with informative n-grams from the prompt.
        """
        self._load()
        preds: List[str] = []
        for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\[0\]\(", tau):
            preds.append(m.group(1))
        if not preds:
            return
        words = re.findall(r"[A-Za-z0-9]+", prompt.lower())
        # form n-grams up to length 4
        ngrams: List[str] = []
        for n in (1, 2, 3, 4):
            for i in range(0, max(0, len(words) - n + 1)):
                ngrams.append(" ".join(words[i:i+n]))
        candidates = [(_normalize_phrase(g), g) for g in ngrams]
        updates: Dict[str, str] = {}
        for pred in preds:
            p_norm = pred
            # choose first ngram whose normalized key is contained in pred or vice versa
            for key, raw in candidates:
                if not key:
                    continue
                if p_norm.startswith(key) or key.startswith(p_norm):
                    updates.setdefault(key, pred)
                    break
        if not updates:
            return
        with self._lock:
            changed = False
            for k, v in updates.items():
                if k not in self._map:
                    self._map[k] = v
                    changed = True
            if changed:
                self._save()


# Singleton instance
alignment_cache = AlignmentCache()


