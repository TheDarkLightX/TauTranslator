import pytest

from backend.unified.api.simple_tce import translate_tce_to_tau_simple


@pytest.mark.parametrize(
    "tce,expected_sub",
    [
        ("always (all x (user[0](x) -> has_profile[0](x)))", "all x"),
        ("always ((sensor_high[0]() && manual_override[0]()) -> alarm_on[0]())", "->"),
        ("always (o1[t] = i1[t-1])", "o1[t] = i1[t-1]"),
    ],
)
def test_golden_simple_translation_contains(tce: str, expected_sub: str):
    ok, tau, errs = translate_tce_to_tau_simple(tce)
    assert ok, errs
    assert tau and expected_sub in tau


