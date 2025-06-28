import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# =================================================
# 9. Recursive Relation Facts (Happy Path)
# =================================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Base case definition
    (
        "the definition of rotate at 0 with x, y, z is (x and y) or z.",
        "rotate[0](x, y, z) := (x & y) | z."
    ),
    # Recursive step definition
    (
        "the definition of rotate at n with x, y, z is rotate at n-1 with y, z, x.",
        "rotate[n](x, y, z) := rotate[n-1](y, z, x)."
    ),
    # More complex boolean expression in body
    (
        "the definition of complex_rule at 1 with a, b is (a and (b or a)).",
        "complex_rule[1](a, b) := (a & (b | a))."
    ),
    # Single parameter
    (
        "the definition of countdown at k with x is countdown at k-1 with x.",
        "countdown[k](x) := countdown[k-1](x)."
    ),
])
def test_recursive_relation_facts(parser, sentence, expected_tau):
    """
    Tests that recursive relations (predicates/functions) are correctly
    translated into their canonical Tau representations.
    """
    # GIVEN a sentence defining a recursive relation
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical recursive relation definition
    assert result.strip() == expected_tau
