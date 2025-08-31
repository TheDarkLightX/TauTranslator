from __future__ import annotations

import json
import os
import random
import re
import yaml
from dataclasses import dataclass
from typing import Iterable, List, Tuple, Optional

from ..api.simple_tce import translate_tce_to_tau_simple
from ..domain.normalization_fast import gate_tokens_fast


@dataclass
class DataItem:
    nl: str
    tce_en: Optional[str] = None   # Controlled English TCE (plain language)
    tce_sym: Optional[str] = None  # Internal symbolic TCE (always (...)->...)


def load_seed_yaml(path: str) -> List[DataItem]:
    data = yaml.safe_load(open(path, "r", encoding="utf-8"))
    out: List[DataItem] = []
    for item in data or []:
        nl = str(item.get("nl", "")).strip()
        # accept either "tce_en" (preferred) or legacy "tce" as english
        tce_en = (item.get("tce_en") or item.get("tce") or "")
        tce_en = str(tce_en).strip() or None
        tce_sym = str(item.get("tce_sym", "")).strip() or None
        if nl and (tce_en or tce_sym):
            out.append(DataItem(nl=nl, tce_en=tce_en, tce_sym=tce_sym))
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


def validate_tce_sym_deterministic(tce_sym: str) -> Tuple[bool, List[str]]:
    """Validate symbolic TCE: gate tokens and attempt simple tce→tau.

    Note: Controlled English TCE (tce_en) is not validated here; symbolic is
    required for deterministic gating/translation.
    """
    gated, reasons = gate_tokens_fast(tce_sym)
    ok, tau, errs = translate_tce_to_tau_simple(gated)
    if not ok:
        reasons.extend(errs or [])
    return bool(ok), reasons


def save_pairs_jsonl(pairs: Iterable[DataItem], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        for p in pairs:
            obj = {"nl": p.nl}
            if p.tce_en:
                obj["tce_en"] = p.tce_en
            if p.tce_sym:
                obj["tce_sym"] = p.tce_sym
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


