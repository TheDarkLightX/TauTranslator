from backend.unified.domain.normalization import gate_tokens


def test_gate_tokens_idempotent():
    inputs = [
        "always (x)",
        "x)",
        "always ( (x && y) ",
        "if a then b",
        "there exists x such that a(x)",
    ]
    for s in inputs:
        a, _ = gate_tokens(s)
        b, _ = gate_tokens(a)
        assert a == b


