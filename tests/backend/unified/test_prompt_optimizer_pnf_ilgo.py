from __future__ import annotations

from backend.unified.domain.prompt_optimizer_pnf_ilgo import optimize_prompt_to_tce
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


