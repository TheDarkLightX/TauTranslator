"""
Tests for neural network weight initialization and activation functions.
"""
import pytest
import numpy as np
from backend.unified.core import neural_network as nn

# === Test for Weight Initialization Helpers ===

def test_create_random_weights_and_biases():
    """Test create_random_weights and create_random_bias functions."""
    input_dim = 10
    output_dim = 5

    # Test create_random_weights
    weights = nn.create_random_weights(input_dim, output_dim)
    assert isinstance(weights, np.ndarray), "Weights should be a numpy array"
    assert weights.shape == (input_dim, output_dim), \
        f"Weights shape mismatch: expected ({input_dim}, {output_dim}), got {weights.shape}"
    assert np.any(weights != 0), "Weights should not all be zero after random initialization"

    # Test create_random_bias
    biases = nn.create_random_bias(output_dim)
    assert isinstance(biases, np.ndarray), "Biases should be a numpy array"
    assert biases.shape == (output_dim,), \
        f"Biases shape mismatch: expected ({output_dim},), got {biases.shape}"
    zero_biases = nn.create_zero_bias(output_dim)
    assert np.all(zero_biases == 0), "create_zero_bias should return all zeros"


# === Tests for Activation Functions ===

def test_sigmoid_and_derivative():
    """Test the sigmoid activation function and its derivative."""
    # Test sigmoid with scalars
    assert nn.sigmoid_activation(0) == pytest.approx(0.5)
    assert nn.sigmoid_activation(100) == pytest.approx(1.0) # Large positive input
    assert nn.sigmoid_activation(-100) == pytest.approx(0.0) # Large negative input
    assert nn.sigmoid_activation(0.88137358701) == pytest.approx(0.70710678118) # approx sigmoid(ln(1+sqrt(2)))

    # Test sigmoid with numpy array
    x_array = np.array([-1, 0, 1])
    expected_sigmoid_array = np.array([1 / (1 + np.exp(1)), 0.5, 1 / (1 + np.exp(-1))])
    assert np.allclose(nn.sigmoid_activation(x_array), expected_sigmoid_array)

    # Test sigmoid_derivative with scalars
    # sigmoid_derivative(x) = sigmoid(x) * (1 - sigmoid(x))
    assert nn.sigmoid_derivative(0) == pytest.approx(0.5 * (1 - 0.5)) # 0.25
    assert nn.sigmoid_derivative(100) == pytest.approx(1.0 * (1 - 1.0)) # approx 0
    assert nn.sigmoid_derivative(-100) == pytest.approx(0.0 * (1 - 0.0)) # approx 0

    # Test sigmoid_derivative with numpy array
    expected_derivative_array = expected_sigmoid_array * (1 - expected_sigmoid_array)
    assert np.allclose(nn.sigmoid_derivative(x_array), expected_derivative_array)

def test_relu_and_derivative():
    """Test the relu activation function and its derivative."""
    # Test relu with scalars
    assert nn.relu_activation(0) == pytest.approx(0.0)
    assert nn.relu_activation(5) == pytest.approx(5.0)
    assert nn.relu_activation(-5) == pytest.approx(0.0)

    # Test relu with numpy array
    x_array = np.array([-2, 0, 2, -0.5, 0.5])
    expected_relu_array = np.array([0, 0, 2, 0, 0.5])
    assert np.allclose(nn.relu_activation(x_array), expected_relu_array)

    # Test relu_derivative with scalars
    # relu_derivative(x) = 1 if x > 0 else 0
    assert nn.relu_derivative(0) == pytest.approx(0.0)
    assert nn.relu_derivative(5) == pytest.approx(1.0)
    assert nn.relu_derivative(-5) == pytest.approx(0.0)

    # Test relu_derivative with numpy array
    expected_derivative_array = np.array([0, 0, 1, 0, 1])
    assert np.allclose(nn.relu_derivative(x_array), expected_derivative_array)

def test_tanh_and_derivative():
    """Test the tanh activation function and its derivative."""
    # Test tanh with scalars
    assert nn.tanh_activation(0) == pytest.approx(0.0)
    assert nn.tanh_activation(100) == pytest.approx(1.0)  # Large positive input
    assert nn.tanh_activation(-100) == pytest.approx(-1.0) # Large negative input
    # tanh(0.5 * ln(3)) = 0.5
    assert nn.tanh_activation(0.5 * np.log(3)) == pytest.approx(0.5)

    # Test tanh with numpy array
    x_array = np.array([-1, 0, 1, 0.5 * np.log(3)])
    expected_tanh_array = np.tanh(x_array) # Use numpy's tanh for expected values
    assert np.allclose(nn.tanh_activation(x_array), expected_tanh_array)

    # Test tanh_derivative with scalars
    # tanh_derivative(x) = 1 - tanh(x)^2
    assert nn.tanh_derivative(0) == pytest.approx(1.0 - 0.0**2) # 1.0
    assert nn.tanh_derivative(100) == pytest.approx(1.0 - 1.0**2) # approx 0.0
    assert nn.tanh_derivative(-100) == pytest.approx(1.0 - (-1.0)**2) # approx 0.0
    assert nn.tanh_derivative(0.5 * np.log(3)) == pytest.approx(1.0 - 0.5**2) # 0.75

    # Test tanh_derivative with numpy array
    expected_derivative_array = 1 - expected_tanh_array**2
    assert np.allclose(nn.tanh_derivative(x_array), expected_derivative_array)
