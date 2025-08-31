import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# ======================================
# 5. Existential Facts (Happy Path)
# ======================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Test case 1: Existential Quantification ('some')
    ("some man is a philosopher.", "exists x : (man(x) and philosopher(x))."),

    # Test case 2: Existential Quantification with a different noun
    ("some politician is honest.", "exists x : (politician(x) and honest(x))."),
])
def test_existential_quantification_facts_canonical(parser, sentence, expected_tau):
    """
    Tests that existentially quantified sentences ('some X is Y') are correctly
    translated into canonical Tau `exists` expressions.
    """
    # GIVEN a sentence representing an existentially quantified fact
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical `exists` expression
    assert result.strip() == expected_tau
