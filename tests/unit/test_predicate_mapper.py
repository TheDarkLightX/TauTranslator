from __future__ import annotations

import os
from backend.unified.services.predicate_mapper import PredicateMapper


def test_predicate_mapper_exact_and_contains(tmp_path):
    yml = tmp_path / "preds.yaml"
    yml.write_text('"payment approved": payment_approved\n"sensor high": sensor_high\n', encoding="utf-8")
    os.environ["TAU_PREDICATE_MAP_PATH"] = str(yml)
    pm = PredicateMapper()
    assert pm.map_phrase("payment approved") == "payment_approved"
    assert pm.map_phrase("when sensor is high") == "sensor_high"


def test_predicate_mapper_fuzzy_and_empty(tmp_path):
    yml = tmp_path / "preds.yaml"
    yml.write_text('"send data over network": send_over_network\n', encoding="utf-8")
    os.environ["TAU_PREDICATE_MAP_PATH"] = str(yml)
    pm = PredicateMapper()
    assert pm.map_phrase("never send data over the network") == "send_over_network"
    assert pm.map_phrase("") == ""


