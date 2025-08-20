from backend.unified.domain.spec_strategy import get_spec_strategy


def test_rr_strategy_same_time_equality():
    strat = get_spec_strategy('rr')
    out = strat.normalize("output equals input each time step", "output equals input")
    assert out == "(o1[t] = i1[t])"


def test_rr_strategy_previous_time():
    strat = get_spec_strategy('rr')
    out = strat.normalize("output equals previous input at t-1", "output equals prev input")
    assert out == "(o1[t] = i1[t-1])"


def test_wff_strategy_fallback():
    strat = get_spec_strategy('wff')
    out = strat.normalize("if sensor is high then alarm on", "if sensor high then alarm on")
    assert "->" in out

