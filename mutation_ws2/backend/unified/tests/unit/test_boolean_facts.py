import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# ======================================
# 7. Boolean Facts (Happy Path)
# ======================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Test case 1: Conjunction (and)
    ("(socrates is a man) and (plato is a man).", "(is_a(socrates, man)) & (is_a(plato, man))."),
    
    # Test case 2: Disjunction (or)
    ("(socrates is a man) or (socrates is a god).", "(is_a(socrates, man)) | (is_a(socrates, god))."),
    
    # Test case 3: Negation (it is not the case that)
    ("it is not the case that (socrates is mortal).", "(is_a(socrates, mortal))'."),

    # Test case 4: Nested boolean expressions
    ("((socrates is a man) and (plato is a man)) or (aristotle is a philosopher).", "((is_a(socrates, man)) & (is_a(plato, man))) | (is_a(aristotle, philosopher))."),
])
def test_boolean_facts(parser, sentence, expected_tau):
    """
    Tests that boolean connectives (and, or, not) are correctly
    translated into their canonical Tau representations.
    """
    # GIVEN a sentence with boolean connectives
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical boolean expression
    assert result.strip() == expected_tau
