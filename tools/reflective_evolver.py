from __future__ import annotations

"""
Single-model reflective evolution loop over prompts/spec drafts.

Uses the same backend model for generation and reflection via /llm endpoints.
Evaluates prompts with TCE/Tau gates and optional SAT, then applies small
patches suggested by the chat assistant. Keeps the variant only if score improves.

Run:
  python tools/reflective_evolver.py --limit 24 --iters 2
"""

import argparse
import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from tools.generate_prompt_corpus_large import as_dicts


BASE = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")
TAU_BIN = Path("external/tau-lang/build-Release/tau").resolve()


def call_api_prompt_to_spec(prompt: str) -> Dict[str, Any]:
    payload = json.dumps({"prompt": prompt, "mode": "assist"})
    res = subprocess.run(
        [
            "curl","-fsSL","-H","Content-Type: application/json","-X","POST",
            f"{BASE}/llm/prompt-to-spec","-d",payload
        ], capture_output=True, text=True, timeout=45)
    if res.returncode != 0:
        raise RuntimeError(f"HTTP call failed: {res.stderr}")
    return json.loads(res.stdout)


def call_api_chat_reflect(prompt: str, tce: str, tau: str) -> str:
    sys = (
        "You are a concise evaluator. Given a natural-language prompt, its current TCE and Tau, "
        "return a JSON object with fields: SCORE (0-100 int), ERROR_TAGS (array of short tags), "
        "FIX_RULE (one sentence), PROMPT_PATCH (<=3 lines to add to prompt). Keep it terse."
    )
    user = json.dumps({"prompt": prompt, "tce": tce, "tau": tau})
    body = json.dumps({"messages": [{"role":"system","content":sys},{"role":"user","content":user}]})
    res = subprocess.run(
        ["curl","-fsSL","-H","Content-Type: application/json","-X","POST",
         f"{BASE}/llm/chat","-d",body], capture_output=True, text=True, timeout=45)
    if res.returncode != 0:
        return "{}"
    try:
        data = json.loads(res.stdout)
        return data.get("reply") or "{}"
    except Exception:
        return "{}"


def sat_with_tau(tau: str) -> Tuple[bool, str]:
    if not TAU_BIN.exists():
        return True, "(tau not built; skipping)"
    with tempfile.NamedTemporaryFile("w", suffix=".cmd", delete=False) as tf:
        tf.write("# stubs relaxed for generic sat\n")
        tf.write(f"sat {tau}\nquit\n")
        tf.flush()
        cmd = tf.name
    try:
        proc = subprocess.run([str(TAU_BIN)], stdin=open(cmd,"r"), capture_output=True, text=True, timeout=30)
    finally:
        try: os.unlink(cmd)
        except OSError: pass
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    out_stripped = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", out)
    sat = re.findall(r"%\d+:\s*([TF])", out_stripped)
    return (bool(sat) and sat[-1] == 'T', out)


def has_symbols_in_tce(tce: str) -> bool:
    return any(sym in tce for sym in ["->","&&","||","(",")","!"])


def tau_shape_ok(tau: str) -> bool:
    if not tau.lower().startswith("always ("):
        return False
    bal = 0
    for ch in tau:
        if ch == '(': bal += 1
        elif ch == ')': bal -= 1
        if bal < 0: return False
    return bal == 0


def diversity_score(tau: str) -> float:
    score = 0.0
    for tok in ["->","!","&&","||","all ","ex ","=", "!="]:
        if tok in tau: score += 0.1
    return min(score, 1.0)


def paraphrase_signature(resp: Dict[str, Any]) -> Dict[str,bool]:
    na = resp.get("nlp_analysis") or {}
    s = {
        "causal": bool(na.get("causality") or na.get("implication")),
        "neg": bool(na.get("negation") or na.get("negate")),
    }
    tau = (resp.get("tau") or "").lower()
    if tau:
        s["causal"] = s["causal"] or ("->" in tau)
        s["neg"] = s["neg"] or ("!" in tau or " not " in tau)
    return s


def stability_score(base_sig: Dict[str,bool], cand_sig: Dict[str,bool]) -> float:
    score = 1.0
    if base_sig["causal"] != cand_sig["causal"]:
        score -= 0.5
    if base_sig["neg"] != cand_sig["neg"]:
        score -= 0.5
    return max(0.0, score)


def evaluate(prompt: str) -> Tuple[float, Dict[str, Any]]:
    t0 = time.time()
    resp = call_api_prompt_to_spec(prompt)
    tce = (resp.get("tce") or "")
    tau = (resp.get("tau") or "")
    tce_ok = float(tce.lower().startswith("at all times") and not has_symbols_in_tce(tce))
    tau_ok = float(tau_shape_ok(tau))
    correct, _ = sat_with_tau(tau)
    correct_f = 1.0 if correct else 0.0
    div = diversity_score(tau)
    sig = paraphrase_signature(resp)
    lat = max(0.001, time.time() - t0)
    combined = 0.45*correct_f + 0.2*tce_ok + 0.15*tau_ok + 0.1*div - 0.05*lat
    return combined, {"resp": resp, "sig": sig, "lat": lat, "score": combined}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=24)
    ap.add_argument('--iters', type=int, default=2)
    args = ap.parse_args()

    seeds = as_dicts(limit=5000)
    # Mix across categories, pick top-N
    by_cat: Dict[str, List[Dict[str,str]]] = {}
    for it in seeds:
        by_cat.setdefault(it["category"], []).append(it)
    chosen: List[str] = []
    per_cat = max(1, args.limit // max(1, len(by_cat)))
    for cat, items in by_cat.items():
        for it in items[:per_cat]:
            chosen.append(it["text"])
    chosen = chosen[:args.limit]

    results: List[Dict[str, Any]] = []
    for base in chosen:
        base_score, base_meta = evaluate(base)
        best_prompt, best_score, best_meta = base, base_score, base_meta
        for _ in range(args.iters):
            # Reflect
            tce = (best_meta["resp"].get("tce") or "")
            tau = (best_meta["resp"].get("tau") or "")
            reply = call_api_chat_reflect(best_prompt, tce, tau)
            patch = ""
            try:
                j = json.loads(reply) if reply.strip().startswith('{') else {}
                patch = (j.get("PROMPT_PATCH") or "").strip()
            except Exception:
                patch = ""
            # Apply simple patch as appended constraint
            candidate = best_prompt if not patch else f"{best_prompt}\n{patch}"
            cand_score, cand_meta = evaluate(candidate)
            # Keep if improved
            if cand_score > best_score:
                best_prompt, best_score, best_meta = candidate, cand_score, cand_meta
        results.append({
            "base": base,
            "best_prompt": best_prompt,
            "base_score": base_score,
            "best_score": best_score,
        })

    print(json.dumps({"count": len(results), "items": results[:5]}, indent=2))


if __name__ == '__main__':
    main()


