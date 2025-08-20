import re
from hypothesis import given, strategies as st, settings

from backend.unified.domain.normalization import gate_tokens, normalize_inner_from_prompt


def _balanced_parens(s: str) -> bool:
    bal = 0
    for ch in s:
        if ch == '(': bal += 1
        elif ch == ')': bal -= 1
        if bal < 0:
            return False
    return bal == 0


@settings(max_examples=100)
@given(st.text(min_size=0, max_size=200))
def test_gate_tokens_properties(random_text: str):
    out, _ = gate_tokens(random_text)
    assert out.lower().startswith("always ("), out
    assert out.endswith(")"), out
    assert _balanced_parens(out), out
    # Allowed token whitelist
    assert re.fullmatch(r"[A-Za-z0-9_,\s\(\)\-\>\|\&'\[\]<!=>]+", out) is not None, out
    # Idempotence
    out2, _ = gate_tokens(out)
    assert out == out2


def test_normalize_inner_causality():
    prompt = "If user logs in then session is active"
    inner = normalize_inner_from_prompt(prompt.lower(), "if login then active")
    assert "->" in inner


@settings(max_examples=50)
@given(
    st.text(alphabet=st.characters(whitelist_categories=["Ll", "Lu"]).map(lambda s: s or "x"), min_size=1, max_size=10),
    st.text(alphabet=st.characters(whitelist_categories=["Ll", "Lu"]).map(lambda s: s or "y"), min_size=1, max_size=10),
)
def test_normalize_inner_random_if_then(lhs: str, rhs: str):
    prompt = f"if {lhs} then {rhs}"
    out = normalize_inner_from_prompt(prompt.lower(), prompt)
    assert "->" in out


