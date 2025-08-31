import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# =================================================
# 8. Relational Expression Facts (Happy Path)
# =================================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Equality
    ("x is equal to y.", "x = y."),
    # Inequality
    ("x is not equal to y.", "x != y."),
    # Less than
    ("x is less than y.", "x < y."),
    # Greater than
    ("x is greater than y.", "x > y."),
    # Less than or equal to
    ("x is less than or equal to y.", "x <= y."),
    # Greater than or equal to
    ("x is greater than or equal to y.", "x >= y."),
])
def test_relational_expression_facts(parser, sentence, expected_tau):
    """
    Tests that relational expressions (comparisons) are correctly
    translated into their canonical Tau representations.
    """
    # GIVEN a sentence with a relational expression
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical relational expression
    assert result.strip() == expected_tau
