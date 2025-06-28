"""
Tests for neural network backward pass components, gradients, and updates.
"""
import pytest
import numpy as np
from backend.unified.core import neural_network as nn
from backend.unified.core.neural_types import ParseNetworkState

# === Tests for Backward Pass Components, Gradients, and Updates ===

def test_calculate_output_error():
    """Test the calculate_output_error function."""
    actual_output = np.array([0.7, 0.2, 0.9])
    target_output = np.array([1.0, 0.0, 1.0])
    expected_error = np.array([0.3, -0.2, 0.1])
    
    calculated_error = nn.calculate_output_error(actual_output, target_output)
    
    assert isinstance(calculated_error, np.ndarray)
    np.testing.assert_array_almost_equal(calculated_error, expected_error, decimal=4)

def test_calculate_output_delta():
    """Test the calculate_output_delta function."""
    output_error = np.array([0.3, -0.2, 0.1])
    # Raw output sum (before sigmoid) that would lead to some sigmoid derivative values
    # Let's pick values for raw_output_sum such that sigmoid_derivative is easy to calculate
    # If raw_output_sum = 0, sigmoid_derivative = 0.5 * (1-0.5) = 0.25
    # If raw_output_sum is large positive (e.g., 10), sigmoid_derivative approx 0
    # If raw_output_sum is large negative (e.g., -10), sigmoid_derivative approx 0
    # For simplicity, let's use raw_output_sum values that produce known derivatives
    # Example: if output_sum = [0, 0, 0], then sigmoid_derivative(output_sum) = [0.25, 0.25, 0.25]
    raw_output_sum = np.array([0.0, 0.0, 0.0]) 
    # This implies actual_output was [0.5, 0.5, 0.5] before error calc.
    # This test is independent of actual_output, only depends on error and derivative of sum.

    # sigmoid_derivative(0) = 0.5 * (1 - 0.5) = 0.25
    # expected_delta = output_error * sigmoid_derivative(raw_output_sum)
    #                = [0.3, -0.2, 0.1] * [0.25, 0.25, 0.25]
    #                = [0.075, -0.05, 0.025]
    expected_delta = output_error * nn.sigmoid_derivative(raw_output_sum)
    
    calculated_delta = nn.calculate_output_delta(output_error, raw_output_sum)
    
    assert isinstance(calculated_delta, np.ndarray)
    np.testing.assert_array_almost_equal(calculated_delta, expected_delta, decimal=4)

def test_calculate_hidden_error(simple_network_state: ParseNetworkState):
    """Test the calculate_hidden_error function."""
    state = simple_network_state # weights_hidden_output = [[0.5], [0.6]]
    output_delta = np.array([0.075]) # Example output delta (scalar for single output neuron)

    # expected_hidden_error = output_delta @ state.weights_hidden_output.T
    #                       = [0.075] @ [[0.5, 0.6]]
    #                       = [0.075 * 0.5, 0.075 * 0.6]
    #                       = [0.0375, 0.045]
    expected_hidden_error = np.dot(output_delta, state.weights_hidden_output.T)
    
    calculated_hidden_error = nn.calculate_hidden_error(output_delta, state.weights_hidden_output)
    
    assert isinstance(calculated_hidden_error, np.ndarray)
    # If output_delta is 1D (e.g. (1,)), and weights_hidden_output.T is 2D (e.g. (1,2)),
    # dot product results in 1D array (e.g. (2,)).
    assert calculated_hidden_error.shape == (state.weights_hidden_output.shape[0],) 
    np.testing.assert_array_almost_equal(calculated_hidden_error, expected_hidden_error, decimal=4)

def test_calculate_hidden_delta():
    """Test the calculate_hidden_delta function."""
    hidden_error = np.array([0.0375, 0.045])
    # Hidden output (after ReLU) that would lead to some ReLU derivative values
    # If hidden_output = [0.55, 0.85] (from forward_pass test, both > 0), then relu_derivative = [1, 1]
    hidden_output = np.array([0.55, 0.85]) # Values > 0, so derivative is 1
    # If hidden_output = [-0.1, 0.85], then relu_derivative = [0, 1]

    # relu_derivative for [0.55, 0.85] is [1.0, 1.0]
    # expected_hidden_delta = hidden_error * relu_derivative(hidden_output)
    #                       = [0.0375, 0.045] * [1.0, 1.0]
    #                       = [0.0375, 0.045]
    expected_hidden_delta = hidden_error * nn.relu_derivative(hidden_output)
    
    calculated_hidden_delta = nn.calculate_hidden_delta(hidden_error, hidden_output)
    
    assert isinstance(calculated_hidden_delta, np.ndarray)
    np.testing.assert_array_almost_equal(calculated_hidden_delta, expected_hidden_delta, decimal=4)

def test_calculate_weight_gradient():
    """Test the calculate_weight_gradient function."""
    input_vec = np.array([1.0, 0.5]) # Shape (2,)
    delta = np.array([0.03, 0.04, 0.02]) # Shape (3,)
    expected_gradient = np.outer(input_vec, delta)
    
    calculated_gradient = nn.calculate_weight_gradient(input_vec, delta)
    
    assert isinstance(calculated_gradient, np.ndarray)
    assert calculated_gradient.shape == (input_vec.shape[0], delta.shape[0])
    np.testing.assert_array_almost_equal(calculated_gradient, expected_gradient, decimal=4)

def test_apply_momentum_update():
    """Test the apply_momentum_update function."""
    initial_momentum = np.array([[0.01, 0.02], [0.03, 0.04]])
    gradient = np.array([[0.1, 0.2], [0.3, 0.4]])
    momentum_factor = 0.9
    learning_rate = 0.1
    expected_new_momentum = momentum_factor * initial_momentum + learning_rate * gradient
    
    calculated_new_momentum = nn.apply_momentum_update(initial_momentum, gradient, momentum_factor, learning_rate)
    
    assert isinstance(calculated_new_momentum, np.ndarray)
    np.testing.assert_array_almost_equal(calculated_new_momentum, expected_new_momentum, decimal=5)

def test_update_momentum_terms(simple_network_state: ParseNetworkState):
    """Test the update_momentum_terms function."""
    state = simple_network_state
    grad_ih = np.array([[0.1, 0.2], [0.3, 0.4]])
    grad_ho = np.array([[0.5], [0.6]])
    grad_bh = np.array([0.05, 0.15])
    grad_bo = np.array([0.25])

    learning_rate = state.learning_rate
    expected_momentum_ih = learning_rate * grad_ih
    expected_momentum_ho = learning_rate * grad_ho
    expected_momentum_bh = learning_rate * grad_bh
    expected_momentum_bo = learning_rate * grad_bo

    nn.update_momentum_terms(state, grad_ih, grad_ho, grad_bh, grad_bo)

    np.testing.assert_array_almost_equal(state.momentum_ih, expected_momentum_ih, decimal=5)
    np.testing.assert_array_almost_equal(state.momentum_ho, expected_momentum_ho, decimal=5)
    np.testing.assert_array_almost_equal(state.momentum_bh, expected_momentum_bh, decimal=5)
    np.testing.assert_array_almost_equal(state.momentum_bo, expected_momentum_bo, decimal=5)


def test_apply_weight_updates(simple_network_state: ParseNetworkState):
    """Test the apply_weight_updates function."""
    state = simple_network_state

    # Store initial weights and biases for comparison
    initial_weights_ih = state.weights_input_hidden.copy()
    initial_weights_ho = state.weights_hidden_output.copy()
    initial_bias_h = state.bias_hidden.copy()
    initial_bias_o = state.bias_output.copy()

    # Manually set some momentum terms (fixture initializes them to zero)
    # Shapes must match the network dimensions (input=2, hidden=2, output=1)
    momentum_ih_update = np.array([[0.01, 0.02], [0.03, 0.04]])
    momentum_ho_update = np.array([[0.05], [0.06]])
    momentum_bh_update = np.array([0.005, 0.015])
    momentum_bo_update = np.array([0.025])

    state.momentum_ih = momentum_ih_update
    state.momentum_ho = momentum_ho_update
    state.momentum_bh = momentum_bh_update
    state.momentum_bo = momentum_bo_update

    # Calculate expected new weights and biases
    expected_weights_ih = initial_weights_ih + momentum_ih_update
    expected_weights_ho = initial_weights_ho + momentum_ho_update
    expected_bias_h = initial_bias_h + momentum_bh_update
    expected_bias_o = initial_bias_o + momentum_bo_update

    # Call the function to apply weight updates
    nn.apply_weight_updates(state)

    # Assert that the weights and biases in the state are updated correctly
    np.testing.assert_array_almost_equal(state.weights_input_hidden, expected_weights_ih, decimal=5)
    np.testing.assert_array_almost_equal(state.weights_hidden_output, expected_weights_ho, decimal=5)
    np.testing.assert_array_almost_equal(state.bias_hidden, expected_bias_h, decimal=5)
    np.testing.assert_array_almost_equal(state.bias_output, expected_bias_o, decimal=5)
