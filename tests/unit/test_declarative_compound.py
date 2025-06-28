import pytest
from backend.unified.declarative_tce_parser import DeclarativeTCEParser

@pytest.fixture
def parser():
    return DeclarativeTCEParser()

def test_compound_fact_with_and(parser):
    """Test a compound fact linked by 'and'."""
    sentence = "a user has a name and a user has an email."
    expected_tau = "has(a_user, a_name) and has(a_user, an_email)"
    result = parser.parse(sentence)
    assert result == expected_tau
