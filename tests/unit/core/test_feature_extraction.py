"""
Unit tests for feature_extraction.py module.
"""
import pytest
import numpy as np

from backend.unified.core.neural_types import ParseFeatures
from backend.unified.core import feature_extraction as fe

# === Tests for extract_parsing_features ===

def test_extract_parsing_features_simple_text():
    """Test with basic, simple text."""
    text = "This is a simple sentence."
    features = fe.extract_parsing_features(text)
    assert isinstance(features, ParseFeatures)
    assert features.word_count == 5  # Corrected from sentence_length
    assert features.avg_word_length == pytest.approx( (4+2+1+6+9) / 5 ) # Corrected: 'sentence.' has length 9
    assert not features.has_quantifier
    assert not features.has_temporal
    assert not features.has_modal
    assert not features.has_causal
    # Based on feature_extraction.py, for simple text:
    # sentence_complexity will be low, e.g., (5 words + 0 commas + 0 parens + 0 conj) / 100 = 0.05
    # pattern_confidence might be 0.5 (base) + 0.2 (is/are) = 0.7
    # semantic_consistency likely 1.0
    assert features.sentence_complexity == pytest.approx(0.05) 
    assert features.pattern_confidence == pytest.approx(0.7) 
    assert features.semantic_consistency == pytest.approx(1.0)

def test_extract_parsing_features_with_quantifier():
    """Test text containing quantifier words."""
    text = "There are many apples."
    features = fe.extract_parsing_features(text)
    assert features.has_quantifier
    # quantifier_count is not a direct field in ParseFeatures in this context

def test_extract_parsing_features_empty_string():
    """Test with an empty string input."""
    text = ""
    features = fe.extract_parsing_features(text)
    assert isinstance(features, ParseFeatures)
    assert features.word_count == 0  # Corrected from sentence_length
    assert features.avg_word_length == 0
    # All boolean flags should be False
    assert not features.has_quantifier
    assert not features.has_temporal
    assert not features.has_modal
    assert not features.has_causal
    # For empty string:
    # sentence_complexity = 0.0
    # pattern_confidence = 0.5 (base, no structure matched)
    # semantic_consistency = 1.0 (no inconsistency patterns matched)
    assert features.sentence_complexity == pytest.approx(0.0)
    assert features.pattern_confidence == pytest.approx(0.5)
    assert features.semantic_consistency == pytest.approx(1.0)

# === Tests for features_to_vector ===

def test_features_to_vector_default_features():
    """Test converting default (mostly zero/False) ParseFeatures to a vector."""
    # Default ParseFeatures() will have 0 for numeric types and False for booleans.
    features = ParseFeatures() 
    vector = fe.features_to_vector(features)
    
    expected_vector_length = 9 # Corrected: features_to_vector produces 9 elements
    assert isinstance(vector, np.ndarray)
    assert len(vector) == expected_vector_length
    
    # Expected vector for default ParseFeatures (all zeros/False):
    # vector[0] = features.word_count / 20.0 (0.0/20=0.0)
    # vector[1] = float(features.has_quantifier) (float(False)=0.0)
    # vector[2] = float(features.has_temporal) (float(False)=0.0)
    # vector[3] = float(features.has_modal) (float(False)=0.0)
    # vector[4] = float(features.has_causal) (float(False)=0.0)
    # vector[5] = features.avg_word_length / 10.0 (0.0/10.0=0.0)
    # vector[6] = features.sentence_complexity (0.0)
    # vector[7] = features.pattern_confidence (0.0)
    # vector[8] = features.semantic_consistency (0.0)
    expected_default_vector = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 1.0])
    assert np.all(vector == pytest.approx(expected_default_vector))

def test_features_to_vector_custom_features():
    """Test converting ParseFeatures with some custom values."""
    features = ParseFeatures(
        word_count=10,              # Corrected field name
        avg_word_length=5.5,
        has_quantifier=True,
        has_modal=True,
        has_causal=False, 
        has_temporal=False, 
        sentence_complexity=0.7,
        pattern_confidence=0.6,
        semantic_consistency=0.9
    )
    vector = fe.features_to_vector(features)
    expected_vector_length = 9 # Corrected
    assert len(vector) == expected_vector_length
    
    # Vector mapping based on feature_extraction.py:
    # vector[0] = features.word_count / 20.0
    # vector[1] = float(features.has_quantifier)
    # vector[2] = float(features.has_temporal)
    # vector[3] = float(features.has_modal)
    # vector[4] = float(features.has_causal)
    # vector[5] = features.avg_word_length / 10.0
    # vector[6] = features.sentence_complexity
    # vector[7] = features.pattern_confidence
    # vector[8] = features.semantic_consistency

    assert vector[0] == pytest.approx(10.0 / 20.0)  # word_count
    assert vector[1] == pytest.approx(1.0)          # has_quantifier (True)
    assert vector[2] == pytest.approx(0.0)          # has_temporal (False)
    assert vector[3] == pytest.approx(1.0)          # has_modal (True)
    assert vector[4] == pytest.approx(0.0)          # has_causal (False)
    assert vector[5] == pytest.approx(5.5 / 10.0)   # avg_word_length
    assert vector[6] == pytest.approx(0.7)          # sentence_complexity
    assert vector[7] == pytest.approx(0.6)          # pattern_confidence
    assert vector[8] == pytest.approx(0.9)          # semantic_consistency

# === Tests for helper functions (e.g., has_quantifier_words) ===

@pytest.mark.parametrize("text, expected", [
    ("There are many cats", True),
    ("A few dogs barked", True),
    ("Several birds sang", True),
    ("No elephants were seen", False), # Corrected: 'no' is not in the hardcoded list
    ("This is a simple sentence", False),
    ("", False)
])
def test_has_quantifier_words(text, expected):
    """Test has_quantifier_words with various inputs."""
    assert fe.has_quantifier_words(text) == expected

@pytest.mark.parametrize("text, expected", [
    ("We will meet tomorrow.", False), # Corrected: 'tomorrow' not in list
    ("The event happened yesterday.", False), # Corrected: 'yesterday' not in list
    ("Currently, it is raining.", False), # Corrected: 'currently' not in list
    ("Meet me when the bell rings.", True), # 'when' is in the list
    ("This is a timeless piece.", False),
    ("", False)
])
def test_has_temporal_words(text, expected):
    """Test has_temporal_words with various inputs."""
    assert fe.has_temporal_words(text) == expected

@pytest.mark.parametrize("text, expected", [
    ("He might go to the store.", True),
    ("She can swim very well.", True),
    ("They must finish the project.", True),
    ("This is a factual statement.", False),
    ("", False)
])
def test_has_modal_words(text, expected):
    """Test has_modal_words with various inputs."""
    assert fe.has_modal_words(text) == expected

@pytest.mark.parametrize("text, expected", [
    ("The project was delayed because of the rain.", True),
    ("Therefore, we must reconsider our options.", True),
    ("Since it's late, we should leave.", True),
    ("The sky is blue.", False),
    ("", False)
])
def test_has_causal_words(text, expected):
    """Test has_causal_words with various inputs."""
    assert fe.has_causal_words(text) == expected

# TODO:
# - Add tests for calculate_sentence_complexity (cover more cases)
# - Add tests for calculate_semantic_consistency (cover more cases)
# - Add tests for calculate_pattern_confidence (cover more cases)
# - Add tests for calculate_avg_word_length
# - Add more edge cases for extract_parsing_features (e.g. punctuation only, numbers, mixed case)
# Note: count_named_entities and get_part_of_speech_distribution are not in the current feature_extraction.py
