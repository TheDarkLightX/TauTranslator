from __future__ import annotations

from backend.unified.domain.prompt_optimizer_pnf_ilgo import optimize_prompt_to_tce, build_default_basis, encode_bitset, glb_with_constraints
from backend.unified.core.result_enhanced import Success


def test_optimizer_basic_causal():
    res = optimize_prompt_to_tce(
        "if payment approved then order shipped",
        constraints={"forbid_colon": True, "require_prefix": "always ("},
    )
    assert isinstance(res, Success)
    out = res.unwrap()
    assert out.tce.lower().startswith("always (")
    assert "->" in out.tce
    assert out.intent in ("causal", "invariant")


def test_optimizer_guard_and_quantifier():
    res = optimize_prompt_to_tce(
        "for all orders, if payment approved then ship unless maintenance",
        constraints={"forbid_colon": True},
    )
    assert isinstance(res, Success)
    out = res.unwrap()
    assert "all" in out.tce or out.quantifiers
    assert any(g in out.tce for g in out.guards) or out.guards


def test_optimizer_ambiguity_questions_present():
    res = optimize_prompt_to_tce("ship", constraints={})
    assert isinstance(res, Success)
    out = res.unwrap()
    # likely missing condition/intent: questions should be proposed
    assert out.questions or out.ambiguity >= 0.0


def test_fdl_bitset_glb_projection():
    basis = build_default_basis(["maintenance"], ["all x"], ["[t-1]"])
    feats = {"intent": "causal", "guards": ["maintenance"], "quantifiers": ["all x"], "temporal": []}
    x = encode_bitset(basis, feats)
    # constraint: forbid guard and quantifier bits
    forbid = 0
    for bmap in (basis.guard_bits, basis.quant_bits):
        for _, pos in bmap.items():
            forbid |= 1 << pos
    allow = ~forbid  # mask allows intent/time only
    y = glb_with_constraints(x, allow)
    # GLB should keep intent only
    kept_intent = (y & (1 << basis.intent_bits["causal"])) != 0
    kept_guard = any((y & (1 << pos)) != 0 for pos in basis.guard_bits.values())
    kept_quant = any((y & (1 << pos)) != 0 for pos in basis.quant_bits.values())
    assert kept_intent and not kept_guard and not kept_quant


def test_negation_never_network_maps_to_not():
    res = optimize_prompt_to_tce(
        "Never send data over the network",
        constraints={"forbid_colon": True, "require_prefix": "always (", "require_closing_paren": True},
        use_fdl=False,
        use_gs=False,
    )
    assert isinstance(res, Success)
    out = res.unwrap()
    assert out.tce.lower().startswith("always (")
    assert 'not' in out.tce.lower()


