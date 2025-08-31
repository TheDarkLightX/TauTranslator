from __future__ import annotations

import json
from backend.unified.dataset.builder import load_seed_yaml, paraphrase_offline, validate_tce_deterministic, NLPair


def test_load_seed_yaml_and_paraphrase(tmp_path):
    seeds = tmp_path / "seeds.yaml"
    seeds.write_text("- nl: If A then B\n  tce: always (A -> B)\n", encoding="utf-8")
    pairs = load_seed_yaml(str(seeds))
    assert pairs and pairs[0].nl.lower().startswith("if ")
    paras = paraphrase_offline(pairs[0].nl, k=3)
    assert 0 < len(paras) <= 3


def test_validate_tce_deterministic_accepts_simple_implication():
    ok, reasons = validate_tce_deterministic("always (A -> B)")
    assert ok is True
    assert isinstance(reasons, list)


def test_save_pairs_jsonl(tmp_path):
    out = tmp_path / "pairs.jsonl"
    data = [NLPair(nl="A.", tce="always (A)")]
    from backend.unified.dataset.builder import save_pairs_jsonl
    save_pairs_jsonl(data, str(out))
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(lines[0])["tce"].startswith("always (")


