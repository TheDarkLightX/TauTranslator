from backend.unified.domain.spec_to_prompt_ast import parse_wff, to_english, build_spec_to_prompt


def _ex(s: str) -> str:
    return build_spec_to_prompt(s, "tau").get("explanation", "")


def test_implication_structure_preserved_in_english():
    ast = parse_wff("(a && b) -> (c || !d)")
    eng = to_english(ast).lower()
    assert "if" in eng and "then" in eng
    assert "and" in eng or "or" in eng or "do not" in eng


def test_quantifiers_and_negation_emit_cleanly():
    ast = parse_wff("all x (!p(x) || ex y (q(x,y)))")
    eng = to_english(ast).lower()
    assert "for every x" in eng or "for every" in eng
    assert "there exists" in eng or "such that" in eng
    assert "do not" in eng


def test_implication_and_negation():
    s = "always (!a || (b -> c))"
    e = _ex(s)
    assert e.lower().startswith("at all times,")
    assert "or" in e.lower() or "if" in e.lower()


def test_bare_always_without_parens():
    s = "always o1[t] = 0"
    e = _ex(s)
    assert e and e.strip().lower().startswith("at all times,")


def test_trailing_punctuation_single_line():
    s = "always o1[t] = 0."
    e = _ex(s)
    assert e and e.strip().lower().startswith("at all times,")


def test_prime_next_notation_normalization():
    s = "always o1[t]' = 0"
    e = _ex(s)
    # We don't assert exact phrasing, only that an explanation exists and refers to o1
    assert e and ("o1" in e or "time" in e.lower())


def test_relations_without_spaces():
    s = "always(o1[t]=0)"
    e = _ex(s)
    assert e and e.strip().lower().startswith("at all times,")


