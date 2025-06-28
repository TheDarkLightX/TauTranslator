"""
Tests for the neural network forward pass.
"""
import pytest
import numpy as np
from backend.unified.core import neural_network as nn
from backend.unified.core.neural_types import ParseNetworkState

# === Tests for Forward Pass ===

def test_forward_pass(simple_network_state: ParseNetworkState):
    """Test the forward_pass function with a simple network and input."""
    state = simple_network_state
    input_vector = np.array([0.5, 1.5]) # Example input

    # Manual calculation based on simple_network_state values:
    # Hidden layer input:
    # hidden_input_sum = input_vector @ state.weights_input_hidden + state.bias_hidden
    #                  = [0.5, 1.5] @ [[0.1, 0.2], [0.3, 0.4]] + [0.05, 0.15]
    #                  = [0.5*0.1 + 1.5*0.3, 0.5*0.2 + 1.5*0.4] + [0.05, 0.15]
    #                  = [0.05 + 0.45, 0.1 + 0.6] + [0.05, 0.15]
    #                  = [0.5, 0.7] + [0.05, 0.15]
    #                  = [0.55, 0.85]
    expected_hidden_input_sum = np.dot(input_vector, state.weights_input_hidden) + state.bias_hidden

    # Hidden layer output (ReLU activation):
    # expected_hidden_outputs = relu([0.55, 0.85]) = [0.55, 0.85]
    expected_hidden_outputs = nn.relu_activation(expected_hidden_input_sum)

    # Output layer input:
    # output_input_sum = expected_hidden_outputs @ state.weights_hidden_output + state.bias_output
    #                  = [0.55, 0.85] @ [[0.5], [0.6]] + [0.25]
    #                  = [0.55*0.5 + 0.85*0.6] + [0.25]
    #                  = [0.275 + 0.51] + [0.25]
    #                  = [0.785] + [0.25]
    #                  = [1.035]
    expected_raw_output_sum = np.dot(expected_hidden_outputs, state.weights_hidden_output) + state.bias_output

    # Final output (Sigmoid activation):
    # expected_final_outputs = sigmoid([1.035])
    # sigmoid(1.035) approx 0.7378
    expected_final_outputs = nn.sigmoid_activation(expected_raw_output_sum)

    # Call the forward_pass function
    hidden_outputs_actual, raw_output_sum_actual, final_outputs_actual = nn.forward_pass(input_vector, state)

    # Assertions
    assert isinstance(hidden_outputs_actual, np.ndarray)
    assert isinstance(raw_output_sum_actual, np.ndarray)
    assert isinstance(final_outputs_actual, np.ndarray)

    np.testing.assert_array_almost_equal(hidden_outputs_actual, expected_hidden_outputs, decimal=4)
    np.testing.assert_array_almost_equal(raw_output_sum_actual, expected_raw_output_sum, decimal=4)
    np.testing.assert_array_almost_equal(final_outputs_actual, expected_final_outputs, decimal=4)
