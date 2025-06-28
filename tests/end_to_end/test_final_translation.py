import pytest
from backend.unified.tce_parser import TCEParser
from backend.unified.tce_transformer import TCETransformer


@pytest.fixture
def translator():
    """Provides a configured parser and transformer for translation."""
    parser = TCEParser()
    transformer = TCETransformer()

    def _translate(tce_sentence: str) -> str:
        tree = parser.parse(tce_sentence)
        tau_spec = transformer.transform(tree)
        return str(tau_spec)

    return _translate


@pytest.mark.parametrize(
    "tce_sentence, expected_tau",
    [
        # Identity and Relations
        ("Socrates is a man", "man(Socrates) := true."),
        ("Plato teaches Aristotle", "teaches(Plato, Aristotle) := true."),
        ("the house is not red", "not red(the_house) := true."),

        # Universal Quantifiers
        ("every car is a vehicle", "vehicle(X) := car(X)."),
        ("all men are mortal", "mortal(X) := man(X)."),

        # Existential Quantifiers
        ("some animal is a mammal", "exists X : (animal(X) and mammal(X))."),
        ("a dog is barking", "exists X : (dog(X) and barking(X))."),

        # Boolean Logic
        ("a person is a man and is a human", "exists X : (person(X) and (man(X) and human(X)))."),
        ("a person is a man or is a woman", "exists X : (person(X) and (man(X) or woman(X)))."),

        # Complex Statements
        ("every student who studies logic is a good student", "good_student(X) := (student(X) and studies(X, logic))."),
    ]
)
def test_end_to_end_translation(translator, tce_sentence, expected_tau):
    """Tests the full TCE to Tau translation pipeline for a variety of constructs."""
    # Act
    actual_tau = translator(tce_sentence)

    # Assert
    assert actual_tau == expected_tau
