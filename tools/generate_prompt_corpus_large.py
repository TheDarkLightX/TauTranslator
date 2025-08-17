"""
Large prompt corpus generator for E2E testing.

Generates thousands of plain-English prompts spanning categories:
- invariants (negation), causal (implication), quantifiers (all/ex),
  temporal phrases, guards/unless, coordination, comparisons,
  nested quantifiers, equivalence/iff, stream relations, robotics, and
  multi-sentence spec drafts.

This module is deterministic given a seed and does not depend on external data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Iterable
import random


@dataclass(frozen=True)
class PromptItem:
    id: str
    category: str
    text: str


def _cartesian(*lists: List[str]) -> Iterable[List[str]]:
    if not lists:
        yield []
        return
    first, *rest = lists
    for v in first:
        for tail in _cartesian(*rest):
            yield [v, *tail]


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set(); out: List[str] = []
    for s in items:
        if s not in seen:
            out.append(s); seen.add(s)
    return out


def _make_invariants() -> List[str]:
    never_syn = [
        "Never", "Do not", "Must not", "Cannot", "Should not",
        "At no time", "Under no circumstances",
    ]
    actions = [
        "send data over the network",
        "process contraband bits",
        "accept expired tokens",
        "access the restricted area",
        "escalate privileges",
    ]
    prompts = [f"{ns} {a}." for ns, a in _cartesian(never_syn, actions)]
    return _dedupe_keep_order(prompts)


def _make_causal() -> List[str]:
    conds = [
        "a payment is approved",
        "sensor is high",
        "manual override is on",
        "the door is locked and a valid code is entered",
        "input is not 1",
    ]
    cons = [
        "the order is shipped",
        "the alarm turns on",
        "the door unlocks",
        "output is not 0",
    ]
    templates = [
        "If {c} then {k}.",
        "When {c}, {k}.",
        "Whenever {c}, {k}.",
        "After {c}, {k}.",
    ]
    out: List[str] = []
    for c in conds:
        for k in cons:
            for t in templates:
                out.append(t.format(c=c, k=k))
    return _dedupe_keep_order(out)


def _make_quantifiers() -> List[str]:
    return _dedupe_keep_order([
        "Every user must have a profile.",
        "Each order has a customer.",
        "For all devices, no device transmits secrets.",
        "There exists a session for each login.",
        "There exists a supervisor for every team.",
        "For every x, if p(x) then there exists y such that q(x,y).",
    ])


def _make_temporal() -> List[str]:
    return _dedupe_keep_order([
        "After a failure, retry immediately.",
        "Before midnight, do not payout.",
        "Output always equals input at each time step.",
        "Output equals input one step earlier.",
    ])


def _make_guards() -> List[str]:
    return _dedupe_keep_order([
        "If the system is live then process orders unless maintenance.",
        "If checkout is open then accept payments unless risk detected.",
    ])


def _make_coordination() -> List[str]:
    return _dedupe_keep_order([
        "If sensor is high or manual override is on then the alarm turns on, always.",
        "If a and b then c, always.",
        "If a or b then c, always.",
    ])


def _make_comparisons() -> List[str]:
    return _dedupe_keep_order([
        "If counter is greater than 10 then raise alert.",
        "If temperature is at least 100 then shutdown.",
        "If latency exceeds 200 ms then throttle.",
    ])


def _make_equivalence() -> List[str]:
    return _dedupe_keep_order([
        "x if and only if y.",
        "x iff y.",
        "x is equivalent to y.",
    ])


def _make_streams() -> List[str]:
    return _dedupe_keep_order([
        "o1 at time t equals i1 at time t always.",
        "o1[t] equals i1[t-1] always.",
        "o2 equals i2 delayed by one step, always.",
    ])


def _make_robotics() -> List[str]:
    return _dedupe_keep_order([
        "A robot may not injure a human or, through inaction, allow a human to come to harm.",
        "A robot must obey human orders unless doing so would cause harm to a human.",
        "A robot must protect its own existence unless this conflicts with higher-priority laws.",
    ])


def _make_spec_drafts() -> List[str]:
    drafts = [
        "Spec: Inputs i1,i2; Outputs o1. At all times, if i1 then o1. Also, o1 equals i1 delayed by one step.",
        "Spec: Users and sessions. For every user, there exists a session after login. Never transmit secrets over the network.",
        "Spec: Payments system. If payment is approved then ship order; do not accept expired tokens; if risk then do not payout.",
    ]
    return drafts


def _make_long_spec_drafts() -> List[str]:
    return [
        (
            """
            Spec: Streamed IO and gating
            Inputs: i1, i2
            Outputs: o1, o2
            Rules:
              - At all times, if i1 then o1.
              - At all times, o1 equals i1 delayed by one step.
              - At all times, if i2 then o2 unless maintenance.
              - Never transmit secrets over the network.
            """.strip()
        ),
        (
            """
            Spec: Users, sessions, and safety
            Entities: user, session
            Requirements:
              - For every user, there exists a session after login.
              - If risk is detected, do not payout.
              - If payment is approved then ship order.
              - Under no circumstances escalate privileges.
            """.strip()
        ),
        (
            """
            Spec: Robotics compliance
            Assumptions: robots r, humans h
            Constraints:
              - A robot may not injure a human or, through inaction, allow a human to come to harm.
              - A robot must obey human orders unless doing so would cause harm to a human.
              - A robot must protect its own existence unless this conflicts with higher-priority laws.
            """.strip()
        ),
    ]


def generate_prompts(total: int = 5000, seed: int = 1337) -> List[PromptItem]:
    rnd = random.Random(seed)
    buckets: Dict[str, List[str]] = {
        "invariant": _make_invariants(),
        "causal": _make_causal(),
        "quantifiers": _make_quantifiers(),
        "temporal": _make_temporal(),
        "guards": _make_guards(),
        "coordination": _make_coordination(),
        "comparisons": _make_comparisons(),
        "equivalence": _make_equivalence(),
        "streams": _make_streams(),
        "robotics": _make_robotics(),
        "spec_drafts": _make_spec_drafts(),
    }
    # Flatten and repeat with light variations to reach target
    pool: List[PromptItem] = []
    for cat, lst in buckets.items():
        for i, txt in enumerate(lst):
            pool.append(PromptItem(id=f"{cat}_{i}", category=cat, text=txt))
    # If not enough, augment by adding simple adverbials and punctuation variants
    adverbs = ["", " Strictly.", " Now.", " Please."]
    base_pool = list(pool)
    idx = 0
    while len(pool) < total:
        item = base_pool[idx % len(base_pool)]
        adv = adverbs[idx % len(adverbs)]
        pool.append(PromptItem(id=f"{item.id}_v{idx}", category=item.category, text=item.text.rstrip('.') + adv))
        idx += 1
    # Shuffle for variety
    rnd.shuffle(pool)
    return pool[:total]


def as_dicts(limit: int | None = None, seed: int = 1337) -> List[Dict]:
    items = generate_prompts(5000, seed=seed)
    if limit is not None:
        items = items[:limit]
    return [{"id": it.id, "category": it.category, "text": it.text} for it in items]


if __name__ == "__main__":
    import json
    data = as_dicts()
    print(json.dumps({"count": len(data), "sample": data[:5]}, indent=2))


