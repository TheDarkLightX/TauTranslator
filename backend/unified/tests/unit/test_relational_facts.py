import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# ======================================
# 2. Relational Facts (Happy Path)
# ======================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Test case 1: Simple ownership
    ("john owns a house.", "owns(john, a_house)."),

    # Test case 2: Multi-word subject
    ("the big john owns a house.", "owns(the_big_john, a_house)."),

    # Test case 3: Multi-word object
    ("john owns a big house.", "owns(john, a_big_house)."),

    # Test case 4: Multi-word subject and object
    ("the big john owns a big house.", "owns(the_big_john, a_big_house)."),
])
def test_relational_owns_facts_canonical(parser, sentence, expected_tau):
    """
    Tests that simple 'X owns a Y' sentences are correctly translated into canonical Tau predicates.
    This follows the data-driven `predicate(subject, object)` Tau syntax.
    """
    # GIVEN a sentence representing a relational fact
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical Tau predicate
    assert result.strip() == expected_tau
