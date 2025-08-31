import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# ======================================
# 3. Negated Identity Facts (Happy Path)
# ======================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Test case 1: Simple negation with determiner
    ("socrates is not a god.", "not(god(socrates))."),

    # Test case 2: Simple negation without determiner (property)
    ("plato is not a student.", "not(student(plato))."),

    # Test case 3: Multi-word subject
    ("the first man is not a god.", "not(god(the_first_man))."),

    # Test case 4: Multi-word entity class
    ("tau is not a simple language.", "not(simple_language(tau))."),
])
def test_negated_identity_facts_canonical(parser, sentence, expected_tau):
    """
    Tests that simple 'X is not a Y' sentences are correctly translated into canonical Tau predicates
    wrapped in a 'not()' operator.
    """
    # GIVEN a sentence representing a negated identity fact
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical negated Tau predicate
    assert result.strip() == expected_tau
