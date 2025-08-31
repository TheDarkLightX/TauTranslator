"""
Pure functions for neural network operations.

This module contains the core mathematical and logical operations for the
gradient descent parser's neural network, including weight initialization,
activation functions, forward/backward passes, and gradient calculations.

Copyright (c) DarkLightX / Dana Edwards
"""

import numpy as np
from typing import Tuple

from .neural_types import ParseNetworkState # Assuming neural_types.py is in the same directory

# === Weight and Bias Initialization ===

def initialize_network_weights(state: ParseNetworkState):
    """Initialize network weights randomly."""
    np.random.seed(42)  # Reproducible initialization
    
    state.weights_input_hidden = create_random_weights(state.input_layer, state.hidden_layer)
    state.weights_hidden_output = create_random_weights(state.hidden_layer, state.output_layer)
    state.bias_hidden = create_random_bias(state.hidden_layer)
    state.bias_output = create_random_bias(state.output_layer)
    
    # Initialize momentum terms
    state.momentum_ih = create_zero_weights(state.input_layer, state.hidden_layer)
    state.momentum_ho = create_zero_weights(state.hidden_layer, state.output_layer)
    state.momentum_bh = create_zero_bias(state.hidden_layer)
    state.momentum_bo = create_zero_bias(state.output_layer)

def create_random_weights(input_size: int, output_size: int) -> np.ndarray:
    """Create randomly initialized weights."""
    # Xavier initialization for better convergence
    scale = np.sqrt(2.0 / (input_size + output_size))
    return np.random.normal(0, scale, (input_size, output_size))

def create_random_bias(size: int) -> np.ndarray:
    """Create randomly initialized bias."""
    return np.random.normal(0, 0.01, size)

def create_zero_weights(input_size: int, output_size: int) -> np.ndarray:
    """Create zero-initialized weights."""
    return np.zeros((input_size, output_size))

def create_zero_bias(size: int) -> np.ndarray:
    """Create zero-initialized bias."""
    return np.zeros(size)

# === Activation Functions and Derivatives ===

def sigmoid_activation(x: np.ndarray) -> np.ndarray:
    """Sigmoid activation function."""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))  # Clip to prevent overflow

def sigmoid_derivative(x: np.ndarray) -> np.ndarray:
    """Derivative of sigmoid function."""
    sig = sigmoid_activation(x)
    return sig * (1.0 - sig)

def relu_activation(x: np.ndarray) -> np.ndarray:
    """ReLU activation function."""
    return np.maximum(0, x)

def relu_derivative(x: np.ndarray) -> np.ndarray:
    """Derivative of ReLU function."""
    return (np.asarray(x) > 0).astype(float)

def tanh_activation(x: np.ndarray) -> np.ndarray:
    """Hyperbolic tangent (tanh) activation function."""
    return np.tanh(x)

def tanh_derivative(x: np.ndarray) -> np.ndarray:
    """Derivative of the tanh function."""
    return 1.0 - np.tanh(x)**2

# === Forward and Backward Pass ===

def forward_pass(input_vector: np.ndarray, state: ParseNetworkState) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Perform forward pass through network.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: A tuple containing:
            - hidden_layer_activations (np.ndarray): Activations of the hidden layer.
            - output_layer_raw_sum (np.ndarray): Weighted sum at the output layer before activation.
            - output_layer_activations (np.ndarray): Final activations of the output layer.
    """
    # Input to hidden layer
    hidden_input = compute_layer_input(input_vector, state.weights_input_hidden, state.bias_hidden)
    hidden_output = relu_activation(hidden_input)
    
    # Hidden to output layer
    output_input = compute_layer_input(hidden_output, state.weights_hidden_output, state.bias_output)
    output = sigmoid_activation(output_input)
    
    return hidden_output, output_input, output

def compute_layer_input(input_vec: np.ndarray, weights: np.ndarray, bias: np.ndarray) -> np.ndarray:
    """Compute layer input with weights and bias."""
    return np.dot(input_vec, weights) + bias

def backward_pass(input_vector: np.ndarray, target: np.ndarray, hidden_output: np.ndarray, 
                 output_input: np.ndarray, actual_output: np.ndarray, state: ParseNetworkState):
    """Perform backward pass with gradient descent."""
    # Calculate output layer error
    output_error = calculate_output_error(actual_output, target)
    output_delta = calculate_output_delta(output_error, output_input)
    
    # Calculate hidden layer error
    hidden_error = calculate_hidden_error(output_delta, state.weights_hidden_output)
    hidden_delta = calculate_hidden_delta(hidden_error, hidden_output)
    
    # Update weights with momentum
    update_weights_with_momentum(input_vector, hidden_output, hidden_delta, output_delta, state)

# === Error and Delta Calculations ===

def calculate_output_error(actual: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Calculate output layer error."""
    return target - actual

def calculate_output_delta(error: np.ndarray, output_input: np.ndarray) -> np.ndarray:
    """Calculate output layer delta."""
    return error * sigmoid_derivative(output_input)

def calculate_hidden_error(output_delta: np.ndarray, weights_ho: np.ndarray) -> np.ndarray:
    """Calculate hidden layer error."""
    return np.dot(output_delta, weights_ho.T)

def calculate_hidden_delta(error: np.ndarray, hidden_output: np.ndarray) -> np.ndarray:
    """Calculate hidden layer delta."""
    return error * relu_derivative(hidden_output)

# === Weight Updates and Momentum ===

def update_weights_with_momentum(input_vector: np.ndarray, hidden_output: np.ndarray,
                                hidden_delta: np.ndarray, output_delta: np.ndarray, 
                                state: ParseNetworkState):
    """Update weights using momentum-based gradient descent."""
    # Calculate gradients
    grad_ho = calculate_weight_gradient(hidden_output, output_delta)
    grad_ih = calculate_weight_gradient(input_vector, hidden_delta)
    grad_bo = output_delta
    grad_bh = hidden_delta
    
    # Update momentum terms
    update_momentum_terms(state, grad_ih, grad_ho, grad_bh, grad_bo)
    
    # Update weights
    apply_weight_updates(state)

def calculate_weight_gradient(input_vec: np.ndarray, delta: np.ndarray) -> np.ndarray:
    """Calculate weight gradient."""
    return np.outer(input_vec, delta)

def update_momentum_terms(state: ParseNetworkState, grad_ih: np.ndarray, grad_ho: np.ndarray,
                         grad_bh: np.ndarray, grad_bo: np.ndarray):
    """Update momentum terms."""
    state.momentum_ih = apply_momentum_update(state.momentum_ih, grad_ih, state.momentum, state.learning_rate)
    state.momentum_ho = apply_momentum_update(state.momentum_ho, grad_ho, state.momentum, state.learning_rate)
    state.momentum_bh = apply_momentum_update(state.momentum_bh, grad_bh, state.momentum, state.learning_rate)
    state.momentum_bo = apply_momentum_update(state.momentum_bo, grad_bo, state.momentum, state.learning_rate)

def apply_momentum_update(momentum: np.ndarray, gradient: np.ndarray, momentum_factor: float, learning_rate: float) -> np.ndarray:
    """Apply momentum update rule."""
    return momentum_factor * momentum + learning_rate * gradient

def apply_weight_updates(state: ParseNetworkState):
    """Apply weight updates from momentum."""
    state.weights_input_hidden += state.momentum_ih
    state.weights_hidden_output += state.momentum_ho
    state.bias_hidden += state.momentum_bh
    state.bias_output += state.momentum_bo

# === Utility Functions ===

def create_target_vector(parse_type: str) -> np.ndarray:
    """Create target vector for parse type."""
    parse_types = {
        'quantified': 0,
        'temporal': 1,
        'modal': 2,
        'causal': 3,
        'comparative': 4,
        'conditional': 5,
        'simple': 6,
        'complex': 7
    }
    
    target = np.zeros(8)
    if parse_type in parse_types:
        target[parse_types[parse_type]] = 1.0
    else:
        target[6] = 1.0  # Default to simple
    
    return target

def predict_parse_type(output: np.ndarray) -> str:
    """Predict parse type from network output."""
    parse_types = ['quantified', 'temporal', 'modal', 'causal', 'comparative', 'conditional', 'simple', 'complex']
    predicted_index = np.argmax(output)
    return parse_types[predicted_index]
