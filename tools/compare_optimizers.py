from __future__ import annotations

import json
import os
import re
import statistics
import time
from typing import Any, Dict, List

from fastapi.testclient import TestClient
from backend.api.server import app


def balanced_parens(text: str) -> bool:
    c = 0
    for ch in text:
        if ch == '(': c += 1
        elif ch == ')': c -= 1
        if c < 0: return False
    return c == 0


PROMPTS = [
    "if payment approved then order shipped",
    "always keep lock engaged when system armed",
    "for all users, if request authenticated then access granted",
    "ship unless maintenance",
    "respond within 5 seconds",
    "never leak data",
    "ensure price implies buy_signal or sell_signal",
    "invalid : punctuation : should be removed",
]


def run_mode(use_fdl: bool) -> Dict[str, Any]:
    # Toggle env flag per batch (optimizer checks env at call time)
    os.environ["TAU_OPTIMIZER_USE_FDL"] = "1" if use_fdl else "0"
    client = TestClient(app)
    results: List[Dict[str, Any]] = []
    for p in PROMPTS:
        t0 = time.perf_counter()
        r = client.post("/llm/prompt-to-spec", json={"prompt": p, "mode": "assist", "constraints": {"forbid_colon": True, "require_prefix": "always (", "require_closing_paren": True, "allowed_connectives": ["and","or","->","!"]}})
        dt = (time.perf_counter() - t0) * 1000.0
        if r.status_code != 200:
            results.append({"prompt": p, "error": r.text, "ms": dt})
            continue
        data = r.json()
        tce = data.get("tce") or ""
        sugg = data.get("prompt_suggestions") or []
        clar = [s for s in sugg if isinstance(s, str) and s.lower().startswith("clarify:")]
        rec = {
            "prompt": p,
            "ms": round(dt, 2),
            "tce_ok": bool(tce) and tce.lower().startswith("always ("),
            "parens_ok": balanced_parens(tce),
            "tau_present": bool(data.get("tau") or ""),
            "reasons": len(data.get("reasons") or []),
            "clarifications": len(clar),
            "tce": tce,
        }
        results.append(rec)
    # Aggregate
    lat = [x["ms"] for x in results if "ms" in x]
    tce_ok = sum(1 for x in results if x.get("tce_ok"))
    par_ok = sum(1 for x in results if x.get("parens_ok"))
    clar = [x["clarifications"] for x in results]
    agg = {
        "use_fdl": use_fdl,
        "count": len(results),
        "latency_ms_avg": round(statistics.mean(lat), 2) if lat else None,
        "latency_ms_p95": round(statistics.quantiles(lat, n=20)[-1], 2) if len(lat) >= 20 else (round(sorted(lat)[int(0.95*len(lat))-1], 2) if lat else None),
        "tce_ok": tce_ok,
        "parens_ok": par_ok,
        "avg_clarifications": round(statistics.mean(clar), 2) if clar else 0.0,
    }
    return {"aggregate": agg, "cases": results}


def main():
    legacy = run_mode(False)
    fdl = run_mode(True)
    report = {"legacy": legacy["aggregate"], "fdl": fdl["aggregate"]}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()


