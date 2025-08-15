import pytest
from lark import Lark
from pathlib import Path
from tau_translator_omega.core_engine.translators.tce_tau_transformer import TCEToTauTransformer, TauToTCETransformer

# Get the project root path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

@pytest.fixture(scope="module")
def tce_parser():
    grammar_path = PROJECT_ROOT / "src" / "tau_translator_omega" / "core_engine" / "parsers" / "grammars" / "tau_controlled.lark"
    with open(grammar_path, "r") as f:
        return Lark(f.read(), start='start')

@pytest.fixture(scope="module")
def tau_parser():
    # NOTE: This grammar is for development and is not part of the repository
    grammar_path = PROJECT_ROOT / ".tau_assets" / "tau.lark"
    if not grammar_path.exists():
        pytest.skip("Formal Tau grammar file not found in .tau_assets/tau.lark")
    with open(grammar_path, "r") as f:
        return Lark(f.read(), start='start')

@pytest.fixture(scope="module")
def tce_to_tau_transformer():
    return TCEToTauTransformer()

@pytest.fixture(scope="module")
def tau_to_tce_transformer():
    return TauToTCETransformer()


def test_round_trip_simple_definition(tce_parser, tau_parser, tce_to_tau_transformer, tau_to_tce_transformer):
    """Tests a round-trip translation of a simple definition."""
    tce_input = "let the function x be defined as y"

    # 1. Forward pass: TCE -> Tau
    tce_tree = tce_parser.parse(tce_input)
    tau_output = tce_to_tau_transformer.transform(tce_tree)

    # Expected Tau output for this simple case
    # Based on TCEToTauTransformer logic for 'definition' and 'predicate_def'
    expected_tau = 'x() := y'
    assert tau_output.strip() == expected_tau

    # 2. Reverse pass: Tau -> TCE
    tau_tree = tau_parser.parse(tau_output)
    tce_round_trip_output = tau_to_tce_transformer.transform(tau_tree)

    # This will fail because TauToTCETransformer is not implemented
    assert tce_round_trip_output.strip().lower() == tce_input.lower()
