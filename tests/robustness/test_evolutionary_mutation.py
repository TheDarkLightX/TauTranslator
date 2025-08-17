import os
import json
import re
import random
import subprocess


BASE = os.environ.get("TRANSLATOR_BASE", "https://tau-translator-api.fly.dev")
random.seed(1337)


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
    # Prefer backend analysis if available
    sig = {
        "causal": False,
        "negation": False,
        "has_all": False,
        "has_ex": False,
    }
    na = resp.get("nlp_analysis") or {}
    sig["causal"] = bool(na.get("causality") or na.get("implication"))
    sig["negation"] = bool(na.get("negation") or na.get("negate"))
    q = na.get("quantifiers") or []
    if isinstance(q, list):
        sig["has_all"] = any("all" in str(x) for x in q)
        sig["has_ex"] = any("ex" in str(x) for x in q)
    # Fallback from tau if needed
    tau = (resp.get("tau") or "")
    if tau:
        tl = tau.lower()
        sig["causal"] = sig["causal"] or ("->" in tl)
        sig["has_all"] = sig["has_all"] or ("all " in tl)
        sig["has_ex"] = sig["has_ex"] or ("ex " in tl)
        sig["negation"] = sig["negation"] or ("!" in tl or " not " in tl)
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

FILL = [
    "please",
    "now",
    "strictly",
    "ensure that",
    "make sure to",
]


def _mutate_one(prompt: str) -> str:
    ops = []
    if random.random() < 0.6:
        # synonym swap with word-boundary replacement to preserve spacing
        keys = [k for k in SYN.keys() if re.search(rf"\b{re.escape(k)}\b", prompt, flags=re.I)]
        if keys:
            k = random.choice(keys)
            repl = random.choice(SYN[k])
            prompt = re.sub(rf"\b{re.escape(k)}\b", repl, prompt, count=1, flags=re.I)
            ops.append("syn")
    if random.random() < 0.4:
        # insert filler at word boundary
        words = prompt.split()
        idx = random.randint(0, len(words))
        words = words[:idx] + [random.choice(FILL)] + words[idx:]
        prompt = " ".join(words)
        ops.append("fill")
    if random.random() < 0.4:
        prompt = prompt.strip().capitalize()
        ops.append("case")
    if random.random() < 0.3:
        prompt = "Always, " + prompt.rstrip(".")
        ops.append("adv")
    return " ".join(prompt.split())


def test_evolutionary_mutation_signatures_stable():
    # Base prompts and their extracted signatures define fitness target
    bases = [
        "Never send data over the network.",
        "Every user must have a profile.",
        "If a payment is approved then the order is shipped.",
    ]
    max_generations = 6
    pop_size = 12
    for base in bases:
        base_resp = _call_api(base)
        base_sig = _extract_signature(base_resp)
        # Initialize population with base
        population = [base]
        found_divergent = None
        for _ in range(max_generations):
            # mutate to create candidates
            while len(population) < pop_size:
                population.append(_mutate_one(random.choice(population)))
            # evaluate and select
            next_pop = []
            for p in population[:pop_size]:
                r = _call_api(p)
                sig = _extract_signature(r)
                # divergence if core intent flips (focus on causal vs invariant)
                if sig["causal"] != base_sig["causal"] or sig["negation"] != base_sig["negation"]:
                    found_divergent = (p, sig, base_sig)
                    break
                next_pop.append(p)
            if found_divergent:
                break
            # keep top unique
            uniq = list(dict.fromkeys(next_pop))
            population = uniq[: max(4, pop_size // 2)]
        assert not found_divergent, f"Signature diverged: {found_divergent} from base '{base}'"


