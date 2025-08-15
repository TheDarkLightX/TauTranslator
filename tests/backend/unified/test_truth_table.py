from backend.unified.utils.truth_table import build_truth_table, Success


def test_simple_and_table():
    expr = "a & b"
    res = build_truth_table(expr)
    assert isinstance(res, Success)
    table = res.value
    # Expect 4 rows
    assert len(table) == 4
    # Row where both 1 => value 1
    row_true = next(r for r in table if r["vars"] == {"a": True, "b": True})
    assert row_true["value"] == 1
    # Row where a=1,b=0 -> 0
    row_false = next(r for r in table if r["vars"] == {"a": True, "b": False})
    assert row_false["value"] == 0 