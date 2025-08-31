from __future__ import annotations

import json
import os
import random
import re
import yaml
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from ..api.simple_tce import translate_tce_to_tau_simple
from ..domain.normalization_fast import gate_tokens_fast


@dataclass
class NLPair:
    nl: str
    tce: str


def load_seed_yaml(path: str) -> List[NLPair]:
    data = yaml.safe_load(open(path, "r", encoding="utf-8"))
    out: List[NLPair] = []
    for item in data or []:
        nl = str(item.get("nl", "")).strip()
        tce = str(item.get("tce", "")).strip()
        if nl and tce:
            out.append(NLPair(nl=nl, tce=tce))
    return out


def paraphrase_offline(nl: str, k: int = 3) -> List[str]:
    """Very lightweight paraphraser using rule-based rewrites.

    Not a true LLM paraphraser; serves as an offline placeholder to generate
    minor lexical variations for robustness testing.
    """
    variants = set()
    base = nl.strip()
    swaps = [
        (r"whenever", "when"),
        (r"if", "when"),
        (r"\bthen\b", ""),
        (r"must\s+", ""),
        (r"there exists", "some"),
        (r"for all", "every"),
    ]
    for pat, rep in swaps:
        variants.add(re.sub(pat, rep, base, flags=re.IGNORECASE))
    # Shuffle slight punctuation/spacing
    variants.add(base.replace(",", ";"))
    variants.add(base.replace(".", ""))
    out = [v for v in variants if v and v != base]
    random.shuffle(out)
    return out[:k]


def validate_tce_deterministic(tce: str) -> Tuple[bool, List[str]]:
    """Gate tokens and attempt simple translation to Tau; return (ok, reasons)."""
    gated, reasons = gate_tokens_fast(tce)
    ok, tau, errs = translate_tce_to_tau_simple(gated)
    if not ok:
        reasons.extend(errs or [])
    return bool(ok), reasons


def save_pairs_jsonl(pairs: Iterable[NLPair], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps({"nl": p.nl, "tce": p.tce}, ensure_ascii=False) + "\n")


