from __future__ import annotations

import os
import pytest

from backend.unified.services.disambiguation_services import (
    infer_temporal_mode,
    choose_quantifier,
    sanitize_to_tce,
    get_nli_reranker,
    Constraints,
)


def test_infer_temporal_mode_default_atemporal():
    assert infer_temporal_mode("Blue elephants exist.", None) == "atemporal"


def test_infer_temporal_mode_invariant_on_keywords():
    assert infer_temporal_mode("Always keep doors locked.", None) == "invariant"
    assert infer_temporal_mode("whenever X then Y", None) == "invariant"


def test_choose_quantifier_heuristics_and_preference():
    # none present -> universal cue
    q, reason = choose_quantifier("For all users, if A then B", "A -> B", Constraints())
    assert q == "all" and "universal" in (reason or "").lower()
    # existential cue
    q2, reason2 = choose_quantifier("There exists a session for each login", "login(x) -> session(x)", Constraints())
    assert q2 == "ex" and "existential" in (reason2 or "").lower()
    # explicit preference wins
    q3, reason3 = choose_quantifier("some text", "p(x)", Constraints(prefer_quantifier="all"))
    assert q3 == "all" and "preference" in (reason3 or "").lower()
    # already quantified -> no change
    q4, _ = choose_quantifier("irrelevant", "all x (p(x))", Constraints())
    assert q4 is None


def test_sanitize_to_tce_respects_temporal_mode():
    # If LLM outputs a bare atom, invariant wraps, atemporal does not
    out_inv = sanitize_to_tce("User: p(x)", "p(x)", "invariant")
    assert out_inv.lower().startswith("always (")
    out_at = sanitize_to_tce("User: p(x)", "p(x)", "atemporal")
    assert not out_at.lower().startswith("always (")


def test_nli_reranker_lexical_enabled_when_flag_set(monkeypatch):
    monkeypatch.setenv("TAU_ENABLE_NLI", "1")
    rr = get_nli_reranker()
    assert rr is not None
    best, reasons = rr.rerank("blue elephants exist", ["There exists x such that elephant(x) and blue(x).", "Unrelated text"])  # type: ignore[arg-type]
    assert isinstance(best, str) and reasons


def test_nli_reranker_disabled_by_default(monkeypatch):
    monkeypatch.delenv("TAU_ENABLE_NLI", raising=False)
    assert get_nli_reranker() is None
