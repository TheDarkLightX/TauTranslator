from __future__ import annotations

from backend.unified.domain.normalization_fast import (
    ensure_always_wrapper,
    balance_parentheses_stream,
    whitelist_and_canonicalize,
    gate_tokens_fast,
)


def test_ensure_always_wrapper_wraps():
    out, msgs = ensure_always_wrapper("A -> B")
    assert out.lower().startswith("always (")
    assert any("Wrapped in always" in m for m in msgs)


def test_balance_parentheses_adds_missing():
    out, msgs = balance_parentheses_stream("((A -> B)")
    assert out.endswith(")")
    assert any("Balanced missing" in m for m in msgs)


def test_balance_parentheses_drops_excess_closing():
    out, msgs = balance_parentheses_stream(")A -> B)")
    assert out.startswith("A") and out.endswith(")")
    assert any("Removed unmatched" in m for m in msgs)


def test_whitelist_and_canonicalize_strips_disallowed():
    dirty = "A → B :  C\t\n &&  D💥"
    clean, msgs = whitelist_and_canonicalize(dirty)
    assert "💥" not in clean
    assert any("Removed unsupported" in m for m in msgs)


def test_gate_tokens_fast_end_to_end_cleans_and_wraps():
    raw = "(A -> B"
    out, reasons = gate_tokens_fast(raw)
    assert out.lower().startswith("always (")
    assert out.endswith(")")
    assert reasons  # should include at least one reason


