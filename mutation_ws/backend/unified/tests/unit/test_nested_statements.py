import pytest
from backend.unified.tce_parser import TCEParser

@pytest.fixture
def parser():
    """Returns a configured instance of the TCE parser."""
    return TCEParser()

# =================================================
# 10. Complex Nested Statements (Happy Path)
# =================================================

@pytest.mark.parametrize("sentence, expected_tau", [
    # Relational expression with nested boolean logic on both sides
    (
        "(a and b) is equal to (c or d).",
        "(a & b) = (c | d)."
    ),
    # A negated relational expression
    (
        "it is not the case that (a is equal to b).",
        "not(a = b)."
    ),
])
def test_nested_statements(parser, sentence, expected_tau):
    """
    Tests that complex nested statements, such as relational expressions
    containing boolean logic, are correctly translated.
    """
    # GIVEN a sentence with nested logic
    
    # WHEN the sentence is parsed
    result = parser.parse(sentence)
    
    # THEN the output should be a canonical nested expression
    assert result.strip() == expected_tau
