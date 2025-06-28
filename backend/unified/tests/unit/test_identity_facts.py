import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# ======================================
# 1. Identity Facts (Happy Path)
# ======================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Test case 1: Simple identity with determiner
    ("socrates is a man.", "man(socrates)."),

    # Test case 2: Simple identity without determiner (property)
    ("socrates is mortal.", "mortal(socrates)."),

    # Test case 3: Multi-word subject
    ("the philosopher socrates is a man.", "man(the_philosopher_socrates)."),

    # Test case 4: Multi-word entity class
    ("tau is a powerful language.", "powerful_language(tau)."),
])
def test_identity_facts_canonical(parser, sentence, expected_tau):
    """
    Tests that simple 'X is a Y' sentences are correctly translated into canonical Tau predicates.
    This follows the data-driven `Y(subject)` Tau syntax.
    """
    # GIVEN a sentence representing an identity fact
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical Tau predicate
    assert result.strip() == expected_tau
