from __future__ import annotations

from backend.unified.domain.gs_ir import var, Not, Always, build_from_features, to_tce, to_nnf, Imply, conj


def test_build_from_features_causal_guard_quant():
    ast = build_from_features(
        intent="causal",
        condition="payment_approved",
        action="order_shipped",
        guards=["maintenance"],
        quantifiers=["all x"],
        temporal=[],
    )
    txt = to_tce(ast)
    assert txt.lower().startswith("always (")
    # Arrow may be eliminated by NNF under quantifier; accept implication or its NNF form
    assert ("->" in txt) or ("not payment_approved" in txt and ("or order_shipped" in txt))
    assert "all x" in txt
    assert "not maintenance" in txt


def test_nnf_imply_elimination():
    a = var("a")
    b = var("b")
    nnf = to_nnf(Imply(a, b))
    # a -> b becomes (not a) or b (after pretty-print, parentheses may differ)
    txt = to_tce(Always(nnf))
    assert "not a" in txt and "or b" in txt


