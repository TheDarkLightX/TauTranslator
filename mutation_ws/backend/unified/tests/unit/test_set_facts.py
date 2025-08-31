import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# ======================================
# 6. Set Facts (Happy Path)
# ======================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Test case 1: Set Definition
    ("the apostles are {peter, james, john}.", "the_apostles :: {peter, james, john}."),
    
    # Test case 2: Set Definition with single element
    ("the founder is {socrates}.", "the_founder :: {socrates}."),
])
def test_set_definition_facts(parser, sentence, expected_tau):
    """
    Tests that set definitions ('X are {a, b, c}') are correctly
    translated into canonical Tau `::` expressions.
    """
    # GIVEN a sentence representing a set definition
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical set definition expression
    assert result.strip() == expected_tau

@pytest.mark.parametrize("sentence, expected_tau", [
    # Test case 1: Set Membership
    ("peter is a member of the apostles.", "peter in the_apostles."),
    
    # Test case 2: Another membership test
    ("socrates is a member of the philosophers.", "socrates in the_philosophers."),
])
def test_set_membership_facts(parser, sentence, expected_tau):
    """
    Tests that set membership sentences ('X is a member of Y') are correctly
    translated into canonical Tau `in` expressions.
    """
    # GIVEN a sentence representing set membership
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical set membership expression
    assert result.strip() == expected_tau
