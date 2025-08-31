import random

from backend.unified.domain.prompt_optimizer_pnf_ilgo import (
    ILGOBasis,
    build_default_basis,
    encode_bitset,
    decode_bitset,
    glb_with_constraints,
    lub,
)


def _sample_basis() -> ILGOBasis:
    # Provide a small but non-trivial basis
    guards = ["g1", "g2", "g3"]
    quants = ["all x", "ex x"]
    times = ["[t-1]", "[t+1]"]
    return build_default_basis(guards=guards, quants=quants, times=times)


def _rand_mask(bits: int) -> int:
    return random.getrandbits(bits)


def _max_bit_index(basis: ILGOBasis) -> int:
    xs = list(basis.intent_bits.values()) + list(basis.guard_bits.values()) + list(basis.quant_bits.values()) + list(basis.time_bits.values())
    return max(xs) if xs else 0


def test_encode_decode_roundtrip_subset():
    basis = _sample_basis()
    # construct a features dict that includes a single intent and some facets
    feats = {
        "intent": "invariant",
        "guards": ["g1", "g3"],
        "quantifiers": ["all x"],
        "temporal": ["[t-1]"],
    }
    bits = encode_bitset(basis, feats)
    decoded = decode_bitset(basis, bits)
    bits_re = encode_bitset(basis, decoded)
    # Decoding chooses one intent; ensure re-encoded set is contained in original bitset
    assert (bits_re & bits) == bits_re


def test_lattice_absorption_comm_assoc_dist():
    random.seed(7)
    basis = _sample_basis()
    nbits = _max_bit_index(basis) + 1
    for _ in range(200):
        a = _rand_mask(nbits)
        b = _rand_mask(nbits)
        c = _rand_mask(nbits)
        # commutativity
        assert lub(a, b) == lub(b, a)
        assert glb_with_constraints(a, b) == glb_with_constraints(b, a)
        # associativity
        assert lub(lub(a, b), c) == lub(a, lub(b, c))
        assert glb_with_constraints(glb_with_constraints(a, b), c) == glb_with_constraints(a, glb_with_constraints(b, c))
        # idempotence
        assert lub(a, a) == a
        assert glb_with_constraints(a, a) == a
        # absorption
        assert lub(a, glb_with_constraints(a, b)) == a
        assert glb_with_constraints(a, lub(a, b)) == a
        # distributivity
        left = glb_with_constraints(a, lub(b, c))
        right = lub(glb_with_constraints(a, b), glb_with_constraints(a, c))
        assert left == right
        left2 = lub(a, glb_with_constraints(b, c))
        right2 = glb_with_constraints(lub(a, b), lub(a, c))
        assert left2 == right2


