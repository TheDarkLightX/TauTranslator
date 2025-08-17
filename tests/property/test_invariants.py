import re


def is_balanced(text: str) -> bool:
    bal = 0
    for ch in text:
        if ch == '(': bal += 1
        elif ch == ')': bal -= 1
        if bal < 0: return False
    return bal == 0


def has_only_allowed_tokens(tau: str) -> bool:
    # Allow letters/digits/underscore/space/(),[] and logic tokens ! = < > - > | &
    cleaned = re.sub(r"[^A-Za-z0-9_\s\(\)\[\]<!=>\-\|&]", "", tau)
    return cleaned == tau


def test_balanced_parens_and_tokens():
    samples = [
        "always (all x (!p[0](x)))",
        "always ((a[0]() && b[0]()) -> c[0]())",
        "always ((i1[t] != 1) -> (o1[t] != 0))",
    ]
    for s in samples:
        assert s.lower().startswith("always ("), s
        assert is_balanced(s), s
        assert has_only_allowed_tokens(s), s


