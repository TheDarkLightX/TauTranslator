from __future__ import annotations

import random
from typing import List

import pytest

from backend.unified.domain.lattice import (
    build_default_basis,
    encode_bitset,
    decode_bitset,
    glb_with_constraints,
    lub,
)


def random_subset(pool: List[str]) -> List[str]:
    return [x for x in pool if random.choice([True, False])]


@pytest.mark.parametrize("guards,quants,times", [
    ([], [], []),
    (["admin_only"], ["all"], []),
    (["no_pii","rate_limit"], ["ex"], ["t","t-1"]),
])
def test_encode_decode_roundtrip_partial(guards: List[str], quants: List[str], times: List[str]):
    basis = build_default_basis(guards=guards, quants=quants, times=times)
    feats = {
        "intent": random.choice(["invariant","causal","fact"]),
        "guards": random_subset(guards),
        "quantifiers": random_subset(quants),
        "temporal": random_subset(times),
    }
    bits = encode_bitset(basis, feats)
    decoded = decode_bitset(basis, bits)
    # Decoded values must be subsets of basis features and include selected ones
    assert set(decoded.get("guards", [])) <= set(guards)
    assert set(feats.get("guards", [])) <= set(decoded.get("guards", []))
    assert set(decoded.get("quantifiers", [])) <= set(quants)
    assert set(feats.get("quantifiers", [])) <= set(decoded.get("quantifiers", []))
    assert set(decoded.get("temporal", [])) <= set(times)
    assert set(feats.get("temporal", [])) <= set(decoded.get("temporal", []))


def test_meet_and_join_idempotence_and_absorption():
    basis = build_default_basis(guards=["g1","g2"], quants=["all","ex"], times=["t","t-1"])
    a = encode_bitset(basis, {"guards":["g1"], "quantifiers":["all"], "temporal":["t"]})
    b = encode_bitset(basis, {"guards":["g2"], "quantifiers":["ex"], "temporal":["t-1"]})
    # glb with allow_mask = all bits allowed -> a ^ fullmask == a (idempotence with full allow)
    fullmask = (1 << (max(basis.intent_bits.values() or [0], default=0)
                      or 0) ) - 1
    # To be safe, construct a mask that allows all derived bit positions
    allow_mask = 0
    for d in (basis.intent_bits|basis.guard_bits|basis.quant_bits|basis.time_bits).values():
        allow_mask |= (1 << d)
    assert glb_with_constraints(a, allow_mask) == a
    # lub absorption: a v (a ^ b) == a when meet implemented as mask
    meet = a & b
    assert lub(a, meet) == a
    # Commutativity
    assert lub(a, b) == lub(b, a)

