from __future__ import annotations

import json
import statistics
import time
from typing import Dict, List

from fastapi.testclient import TestClient
from backend.api.server import app


def load_jsonl(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def eval_prompt_to_spec(items: List[Dict]) -> Dict[str, float]:
    client = TestClient(app)
    latencies: List[float] = []
    quant_ok = 0
    temporal_ok = 0
    total = 0
    for it in items:
        nl = (it.get("nl") or "").strip()
        gold_en = (it.get("tce_en") or "").strip()
        gold_sym = (it.get("tce_sym") or "").strip()
        if not nl:
            continue
        body = {"prompt": nl, "mode": "assist", "constraints": {"forbid_colon": True}}
        t0 = time.perf_counter()
        r = client.post("/llm/prompt-to-spec", json=body)
        dt = (time.perf_counter() - t0) * 1000.0
        latencies.append(dt)
        if r.status_code != 200:
            continue
        data = r.json()
        out_en = (data.get("tce") or "").strip()
        out_tau = (data.get("tau") or "").strip()
        # crude checks: quantifier/temporal correctness compared to gold_sym
        gold_has_always = gold_sym.lower().startswith("always (")
        out_has_always = out_tau.lower().startswith("always (") if out_tau else out_en.lower().startswith("at all times,")
        if gold_has_always == out_has_always:
            temporal_ok += 1
        gold_has_all = " all " in (gold_sym.lower() + " ")
        gold_has_ex = " ex " in (gold_sym.lower() + " ")
        out_has_all = " all " in (out_en.lower() + " ") or " all " in (out_tau.lower() + " ")
        out_has_ex = " there exists " in (out_en.lower() + " ") or " ex " in (out_tau.lower() + " ")
        if (gold_has_all and out_has_all) or (gold_has_ex and out_has_ex) or (not gold_has_all and not gold_has_ex and not out_has_all and not out_has_ex):
            quant_ok += 1
        total += 1
    return {
        "count": float(total),
        "latency_p50_ms": statistics.median(latencies) if latencies else 0.0,
        "latency_p90_ms": (statistics.quantiles(latencies, n=10)[8] if len(latencies) >= 10 else (max(latencies) if latencies else 0.0)),
        "temporal_acc": (temporal_ok / total) if total else 0.0,
        "quantifier_acc": (quant_ok / total) if total else 0.0,
    }


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "backend/unified/dataset/gold/dev.jsonl"
    items = load_jsonl(path)
    metrics = eval_prompt_to_spec(items)
    print(json.dumps(metrics, indent=2))


