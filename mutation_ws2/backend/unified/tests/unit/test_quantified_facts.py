import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# ======================================
# 4. Quantified Facts (Happy Path)
# ======================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Test case 1: Universal Quantification ('every')
    ("every man is mortal.", "forall x : (man(x) -> mortal(x))."),

    # Test case 2: Universal Quantification ('all') - singular noun
    ("all men are mortal.", "forall x : (man(x) -> mortal(x))."),
])
def test_universal_quantification_facts_canonical(parser, sentence, expected_tau):
    """
    Tests that universally quantified sentences ('every X is Y', 'all X are Y') are correctly
    translated into canonical Tau `forall` expressions.
    """
    # GIVEN a sentence representing a universally quantified fact
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical `forall` expression
    assert result.strip() == expected_tau
