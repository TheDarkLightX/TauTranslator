import os
import json
import re
import random
import subprocess
from collections import defaultdict

from tools.generate_prompt_corpus_large import as_dicts


BASE = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")
random.seed(1338)


def _call_api(prompt: str) -> dict:
    payload = json.dumps({"prompt": prompt, "mode": "assist"})
    res = subprocess.run(
        [
            "curl",
            "-fsSL",
            "-H",
            "Content-Type: application/json",
            "-X",
            "POST",
            f"{BASE}/llm/prompt-to-spec",
            "-d",
            payload,
        ],
        capture_output=True,
        text=True,
        timeout=45,
    )
    if res.returncode != 0:
        raise RuntimeError(f"HTTP call failed: rc={res.returncode} err={res.stderr}")
    return json.loads(res.stdout)


def _extract_signature(resp: dict) -> dict:
    sig = {"causal": False, "negation": False, "has_all": False, "has_ex": False, "equiv": False}
    na = resp.get("nlp_analysis") or {}
    sig["causal"] = bool(na.get("causality") or na.get("implication"))
    sig["negation"] = bool(na.get("negation") or na.get("negate"))
    q = na.get("quantifiers") or []
    if isinstance(q, list):
        sig["has_all"] = any("all" in str(x) for x in q)
        sig["has_ex"] = any("ex" in str(x) for x in q)
    tau = (resp.get("tau") or "").lower()
    if tau:
        sig["causal"] = sig["causal"] or ("->" in tau)
        sig["has_all"] = sig["has_all"] or ("all " in tau)
        sig["has_ex"] = sig["has_ex"] or ("ex " in tau)
        sig["negation"] = sig["negation"] or ("!" in tau or " not " in tau)
        sig["equiv"] = sig["equiv"] or ("<->" in tau or ("->" in tau and " and " in tau))
    return sig


SYN = {
    "never": ["at no time", "under no circumstances"],
    "send": ["transmit", "forward"],
    "data": ["information"],
    "network": ["the network"],
    "every": ["each", "all"],
    "user": ["user"],
    "profile": ["account profile"],
    "payment": ["payment"],
    "approved": ["authorized"],
    "order": ["order"],
    "shipped": ["dispatched"],
}

FILL = ["please", "now", "strictly", "ensure that", "make sure to"]


def _mutate_one(prompt: str) -> str:
    if random.random() < 0.6:
        keys = [k for k in SYN.keys() if re.search(rf"\b{re.escape(k)}\b", prompt, flags=re.I)]
        if keys:
            k = random.choice(keys)
            repl = random.choice(SYN[k])
            prompt = re.sub(rf"\b{re.escape(k)}\b", repl, prompt, count=1, flags=re.I)
    if random.random() < 0.4:
        words = prompt.split()
        idx = random.randint(0, len(words))
        words = words[:idx] + [random.choice(FILL)] + words[idx:]
        prompt = " ".join(words)
    if random.random() < 0.3:
        prompt = prompt.strip().capitalize()
    if random.random() < 0.3 and not prompt.lower().startswith("always"):
        prompt = "Always, " + prompt.rstrip(".")
    return " ".join(prompt.split())


def test_evolutionary_mutation_expanded_sampled():
    # Sample multiple bases per category from the large corpus
    corpus = as_dicts(limit=5000)
    by_cat = defaultdict(list)
    for it in corpus:
        by_cat[it["category"]].append(it["text"])
    # Keep runtime reasonable: sample N bases per category
    PER_CAT = 3
    bases = []
    for cat, items in by_cat.items():
        random.shuffle(items)
        bases.extend(items[:PER_CAT])

    # Lightweight evolution settings
    max_generations = 2
    pop_size = 8

    for base in bases:
        base_resp = _call_api(base)
        base_sig = _extract_signature(base_resp)
        base_equiv = (" iff " in base.lower()) or (" equivalent " in base.lower()) or bool(base_sig.get("equiv"))
        population = [base]
        found_divergent = None
        for _ in range(max_generations):
            while len(population) < pop_size:
                population.append(_mutate_one(random.choice(population)))
            next_pop = []
            for p in population[:pop_size]:
                r = _call_api(p)
                sig = _extract_signature(r)
                # core stability: if base is equivalence, require candidate to indicate equivalence (via prompt or tau);
                # otherwise require causal vs invariant match; always require negation match.
                cand_equiv = (" iff " in p.lower()) or (" equivalent " in p.lower()) or bool(sig.get("equiv"))
                diverge = False
                if base_equiv:
                    if not cand_equiv:
                        diverge = True
                else:
                    if sig["causal"] != base_sig["causal"]:
                        diverge = True
                if sig["negation"] != base_sig["negation"]:
                    diverge = True
                if diverge:
                    found_divergent = (p, sig, base_sig, base)
                    break
                next_pop.append(p)
            if found_divergent:
                break
            population = list(dict.fromkeys(next_pop))[: max(3, pop_size // 2)]
        assert not found_divergent, f"Divergence: {found_divergent}"


