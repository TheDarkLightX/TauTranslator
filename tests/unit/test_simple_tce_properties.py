import re
from hypothesis import given, strategies as st

from backend.unified.api.simple_tce import validate_tce_simple, translate_tce_to_tau_simple


@given(st.text(min_size=1, max_size=200))
def test_validate_tce_simple_handles_any_string(s: str):
    ok, errs = validate_tce_simple(s)
    # No exceptions; returns a boolean and list of errors
    assert isinstance(ok, bool)
    assert isinstance(errs, list)


@given(st.from_regex(r"always\s*\(.*\)", fullmatch=False))
def test_translate_tce_to_tau_simple_balance_and_tokens(s: str):
    ok, tau, errs = translate_tce_to_tau_simple(s)
    if ok:
        assert tau is not None and tau.lower().startswith("always (") and tau.endswith(")")
        # Check parentheses balance
        depth = 0
        for ch in tau:
            if ch == '(': depth += 1
            elif ch == ')': depth -= 1
        assert depth == 0
