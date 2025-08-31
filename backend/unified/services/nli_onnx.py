from __future__ import annotations

import os
import re
from typing import List, Sequence, Tuple, Optional


def _tok(s: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9]+", (s or "").lower()))


class OnnxNliReranker:
    """ONNX-backed MNLI reranker with lexical fallback.

    Note: Without a tokenizer pipeline, this adapter currently loads the
    ONNX session (to validate availability) and then falls back to lexical
    Jaccard scoring to keep offline behavior robust. It caches the session.
    """

    _session: Optional[object] = None
    _loaded_path: Optional[str] = None

    def __init__(self, onnx_path: str):
        self._ensure_session(onnx_path)

    @classmethod
    def _ensure_session(cls, onnx_path: str) -> None:
        if cls._loaded_path == onnx_path and cls._session is not None:
            return
        cls._session = None
        cls._loaded_path = None
        try:
            import onnxruntime as ort  # type: ignore
            if os.path.exists(onnx_path):
                cls._session = ort.InferenceSession(onnx_path)
                cls._loaded_path = onnx_path
        except Exception:
            cls._session = None
            cls._loaded_path = None

    def rerank(self, premise: str, candidates: Sequence[str]) -> Tuple[str, List[str]]:
        if not candidates:
            return "", []
        # Lexical Jaccard fallback; mention ONNX status in reasons
        p = _tok(premise)
        best_idx = 0
        best = -1.0
        for i, h in enumerate(candidates):
            hset = _tok(h)
            inter = len(p & hset)
            union = max(1, len(p | hset))
            score = inter / union
            if score > best:
                best = score
                best_idx = i
        reasons = []
        if self._session is not None:
            reasons.append("NLI-onnx session loaded; lexical fallback used")
        else:
            reasons.append("NLI-lite rerank applied (lexical)")
        return candidates[best_idx], reasons


