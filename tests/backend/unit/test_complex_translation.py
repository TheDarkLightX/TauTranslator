import pytest
from lark import Lark
from tau_translator_omega.core_engine.translators.tce_tau_transformer import TCEToTauTransformer, TauToTCETransformer

@pytest.fixture(scope="module")
def tce_parser_complex():
    with open("~/TauTranslator/src/tau_translator_omega/core_engine/parsers/grammars/tau_controlled.lark", "r") as f:
        return Lark(f, parser='earley', lexer='dynamic', start='expression')

@pytest.fixture(scope="module")
def tau_parser_complex():
    # This grammar will need to be created and expanded
    grammar = """
    ?start: rr | rec_relation | wff

    rr: rec_relations main_wff "."
    rec_relations: (rec_relation ".")*
    rec_relation: ref ":=" (capture | ref | wff | bf)

    ref: CNAME [offsets] ref_args ["fallback" fp_fallback]
    fp_fallback: "first" | "last" | capture | ref | wff | bf
    ref_args: "(" [bf ("," bf)*] ")"

    wff: "(" wff ")"                                     -> wff_parenthesis
       | "ex" q_vars wff                                   -> wff_ex
       | ref                                               -> wff_ref
       | wff "&&" wff                                      -> wff_and
       | bf "=" bf                                         -> bf_eq
       | bf

    bf: "(" bf ")"                                       -> bf_parenthesis
      | variable
      | bf "|" bf                                         -> bf_or

    variable: CNAME
    capture: "$" CNAME
    q_vars: q_var ("," q_var)*
    q_var: capture | variable
    main_wff: wff
    offsets: "[" CNAME "]" 

    CNAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    %import common.WS
    %ignore WS
    """
    return Lark(grammar, parser='earley')

@pytest.fixture(scope="module")
def tce_to_tau_transformer_complex():
    return TCEToTauTransformer()

@pytest.fixture(scope="module")
def tau_to_tce_transformer_complex():
    return TauToTCETransformer()

def test_round_trip_full_adder(tce_parser_complex, tau_parser_complex, tce_to_tau_transformer_complex, tau_to_tce_transformer_complex):
    """Tests a round-trip translation of the full adder specification."""
    tce_input = "there exists x, y, z such that h(a, b, x, y) and h(x, i, s, z)"
    expected_tau = "ex x ex y ex z (h(a, b, x, y) && h(x, i, s, z))"

    # 1. Forward pass: TCE -> Tau
    tce_tree = tce_parser_complex.parse(tce_input)
    tau_output = tce_to_tau_transformer_complex.transform(tce_tree)
    assert tau_output.strip() == expected_tau