from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass(frozen=True)
class ILGOBasis:
    """Join-irreducible basis for ILGO lattice as bit positions."""
    intent_bits: Dict[str, int]
    guard_bits: Dict[str, int]
    quant_bits: Dict[str, int]
    time_bits: Dict[str, int]


def build_default_basis(guards: List[str], quants: List[str], times: List[str]) -> ILGOBasis:
    bit = 0
    intent_bits: Dict[str, int] = {}
    for k in ["invariant", "causal", "equivalence", "temporal"]:
        intent_bits[k] = bit; bit += 1
    guard_bits: Dict[str, int] = {g: (i+bit) for i, g in enumerate(sorted(set(guards)))}
    bit += len(guard_bits)
    quant_bits: Dict[str, int] = {q: (i+bit) for i, q in enumerate(sorted(set(quants)))}
    bit += len(quant_bits)
    time_bits: Dict[str, int] = {t: (i+bit) for i, t in enumerate(sorted(set(times), key=lambda s: (len(s), s)))}
    return ILGOBasis(intent_bits=intent_bits, guard_bits=guard_bits, quant_bits=quant_bits, time_bits=time_bits)


def encode_bitset(basis: ILGOBasis, feats: Dict[str, Any]) -> int:
    mask = 0
    intent = feats.get("intent")
    if intent and intent in basis.intent_bits:
        mask |= 1 << basis.intent_bits[intent]
    for g in feats.get("guards") or []:
        if g in basis.guard_bits:
            mask |= 1 << basis.guard_bits[g]
    for q in feats.get("quantifiers") or []:
        if q in basis.quant_bits:
            mask |= 1 << basis.quant_bits[q]
    for t in feats.get("temporal") or []:
        if t in basis.time_bits:
            mask |= 1 << basis.time_bits[t]
    return mask


def glb_with_constraints(bitset: int, constraint_mask: int) -> int:
    """Greatest lower bound (meet) under constraints: intersection (AND)."""
    return bitset & constraint_mask


def lub(bitset_a: int, bitset_b: int) -> int:
    """Least upper bound (join): union (OR)."""
    return bitset_a | bitset_b


def decode_bitset(basis: ILGOBasis, bits: int) -> Dict[str, Any]:
    inv_intent = {v: k for k, v in basis.intent_bits.items()}
    inv_guard = {v: k for k, v in basis.guard_bits.items()}
    inv_quant = {v: k for k, v in basis.quant_bits.items()}
    inv_time = {v: k for k, v in basis.time_bits.items()}
    feats: Dict[str, Any] = {
        "intent": None,
        "guards": [],
        "quantifiers": [],
        "temporal": [],
    }
    for i in sorted(inv_intent.keys()):
        if bits & (1 << i):
            feats["intent"] = inv_intent[i]
            break
    feats["guards"] = [inv_guard[i] for i in sorted(inv_guard.keys()) if bits & (1 << i)]
    feats["quantifiers"] = [inv_quant[i] for i in sorted(inv_quant.keys()) if bits & (1 << i)]
    feats["temporal"] = [inv_time[i] for i in sorted(inv_time.keys()) if bits & (1 << i)]
    return feats


