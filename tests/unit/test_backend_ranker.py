from __future__ import annotations

from backend.unified.services.ranker import rank_candidates_by_rules_and_overlap


def test_ranker_prefers_existential_for_exist_prompts():
    prompt = "there exists a blue elephant"
    cands = [
        "always (all x ( ... ))",
        "there exists x such that elephant(x) and blue(x)",
        "if A then B",
    ]
    order = rank_candidates_by_rules_and_overlap(prompt, cands)
    assert order[0] == 1


def test_ranker_prefers_universal_for_forall_prompts():
    prompt = "for all users if login then has profile"
    cands = [
        "there exists x such that user(x)",
        "for every u, if login(u) then has_profile(u)",
        "always ( ... )",
    ]
    order = rank_candidates_by_rules_and_overlap(prompt, cands)
    assert order[0] == 1


