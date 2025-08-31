import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# ====================================
# 1. Atomic Facts (Happy Path)
# ====================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Test case 1: Simple, one-word entity and one-word class
    ("socrates is a man.", "man(socrates)."),

    # Test case 2: One-word entity, multi-word class
    ("socrates is a mortal man.", "mortal_man(socrates)."),

    # Test case 3: Multi-word entity, one-word class
    ("the big socrates is a man.", "man(the_big_socrates)."),

    # Test case 4: Multi-word entity, multi-word class
    ("the big socrates is a mortal man.", "mortal_man(the_big_socrates)."),

    # Test case 5: No determiner
    ("socrates is mortal.", "mortal(socrates)."),
])
def test_atomic_is_a_facts_canonical(parser, sentence, expected_tau):
    """
    Tests that simple 'X is a Y' sentences are correctly translated into canonical Tau predicates.
    This is data-driven based on the common Tau syntax `predicate(subject)`.
    """
    # GIVEN a sentence representing a simple fact
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical Tau predicate
    assert result.strip() == expected_tau
