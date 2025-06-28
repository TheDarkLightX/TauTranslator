"""
Tests for neural network utility functions.
"""
import pytest
import numpy as np
from backend.unified.core import neural_network as nn
from typing import List

# === Tests for Utility Functions ===

def test_create_target_vector():
    """Test the create_target_vector function."""
    defined_parse_types = {
        'quantified': 0,
        'temporal': 1,
        'modal': 2,
        'causal': 3,
        'comparative': 4,
        'conditional': 5,
        'simple': 6,
        'complex': 7
    }
    vector_size = 8 # Based on the implementation of create_target_vector

    for parse_type_str, expected_index in defined_parse_types.items():
        expected_vector = np.zeros(vector_size)
        expected_vector[expected_index] = 1.0
        
        calculated_vector = nn.create_target_vector(parse_type_str)
        
        assert isinstance(calculated_vector, np.ndarray), f"Vector for '{parse_type_str}' is not ndarray"
        assert calculated_vector.shape == (vector_size,), f"Vector shape for '{parse_type_str}' is incorrect"
        np.testing.assert_array_equal(calculated_vector, expected_vector,
                                      err_msg=f"Vector for '{parse_type_str}' is incorrect")

    # Test default behavior for an unknown parse_type
    unknown_parse_type = "unknown_type"
    expected_simple_index = defined_parse_types['simple']
    expected_vector_unknown = np.zeros(vector_size)
    expected_vector_unknown[expected_simple_index] = 1.0
    calculated_vector_unknown = nn.create_target_vector(unknown_parse_type)
    np.testing.assert_array_equal(calculated_vector_unknown, expected_vector_unknown,
                                  err_msg=f"Vector for unknown type '{unknown_parse_type}' did not default to 'simple'")

    # Test behavior for an empty string parse_type (should also default to 'simple')
    empty_parse_type = ""
    calculated_vector_empty = nn.create_target_vector(empty_parse_type)
    np.testing.assert_array_equal(calculated_vector_empty, expected_vector_unknown, # Compares to 'simple' vector
                                  err_msg=f"Vector for empty string type did not default to 'simple'")


def test_predict_parse_type():
    """Test the predict_parse_type function."""
    # Corresponds to the internal list in neural_network.predict_parse_type
    internal_parse_types = ['quantified', 'temporal', 'modal', 'causal', 'comparative', 'conditional', 'simple', 'complex']

    # Standard case: clear maximum
    output_vector_1 = np.array([0.1, 0.2, 0.8, 0.3, 0.1, 0.0, 0.4, 0.1]) # Max at index 2 ('modal')
    expected_prediction_1 = internal_parse_types[2]
    assert nn.predict_parse_type(output_vector_1) == expected_prediction_1

    # Edge case: first element is max
    output_vector_2 = np.array([0.9, 0.1, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0]) # Max at index 0 ('quantified')
    expected_prediction_2 = internal_parse_types[0]
    assert nn.predict_parse_type(output_vector_2) == expected_prediction_2

    # Edge case: last element is max (index 7 for an 8-element array)
    output_vector_3 = np.array([0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.7]) # Max at index 7 ('complex')
    expected_prediction_3 = internal_parse_types[7]
    assert nn.predict_parse_type(output_vector_3) == expected_prediction_3

    # Tie-breaking: np.argmax returns the index of the first occurrence of the maximum value
    output_vector_4 = np.array([0.1, 0.8, 0.3, 0.8, 0.1, 0.1, 0.1, 0.1]) # Max 0.8 at index 1 and 3. Expect index 1 ('temporal')
    expected_prediction_4 = internal_parse_types[1]
    assert nn.predict_parse_type(output_vector_4) == expected_prediction_4

    # Input vector shorter than internal_parse_types (should still work if argmax is within bounds)
    output_vector_5 = np.array([0.1, 0.9, 0.2]) # Max at index 1 ('temporal')
    expected_prediction_5 = internal_parse_types[1]
    assert nn.predict_parse_type(output_vector_5) == expected_prediction_5

    # Error handling: Input vector longer than internal_parse_types, and argmax result is out of bounds
    output_vector_error_1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]) # Max at index 8
    with pytest.raises(IndexError):
        nn.predict_parse_type(output_vector_error_1)

    # Error handling: Empty input vector
    output_vector_error_2 = np.array([])
    with pytest.raises(ValueError): # np.argmax raises ValueError for empty array
        nn.predict_parse_type(output_vector_error_2)
