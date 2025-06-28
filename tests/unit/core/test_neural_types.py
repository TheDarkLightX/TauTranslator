"""
Unit tests for neural_types.py module.

Verifies the instantiation and default values of dataclasses:
- ParseFeatures
- ParsingNeuron
- ParseNetworkState
"""
import pytest
import numpy as np
from backend.unified.core.neural_types import (
    ParseFeatures,
    ParsingNeuron,
    ParseNetworkState
)


# === Tests for ParseFeatures ===

def test_parse_features_defaults():
    """Test ParseFeatures instantiation with default values."""
    features = ParseFeatures()
    assert features.word_count == 0
    assert features.has_quantifier is False
    assert features.has_temporal is False
    assert features.has_modal is False
    assert features.has_causal is False
    assert features.avg_word_length == 0.0
    assert features.sentence_complexity == 0.0
    assert features.pattern_confidence == 0.5  # Default base confidence
    assert features.semantic_consistency == 1.0 # Default assumes consistent

def test_parse_features_custom_values():
    """Test ParseFeatures instantiation with custom values."""
    features = ParseFeatures(
        word_count=10,
        has_quantifier=True,
        has_temporal=True,
        has_modal=False,
        has_causal=True,
        avg_word_length=5.5,
        sentence_complexity=0.75,
        pattern_confidence=0.9,
        semantic_consistency=0.2
    )
    assert features.word_count == 10
    assert features.has_quantifier is True
    assert features.has_temporal is True
    assert features.has_modal is False
    assert features.has_causal is True
    assert features.avg_word_length == 5.5
    assert features.sentence_complexity == 0.75
    assert features.pattern_confidence == 0.9
    assert features.semantic_consistency == 0.2


# === Tests for ParsingNeuron ===

def test_parsing_neuron_defaults():
    """Test ParsingNeuron instantiation with default bias and activation_type."""
    mock_weights = np.array([0.1, 0.2])
    neuron = ParsingNeuron(weights=mock_weights)
    assert np.array_equal(neuron.weights, mock_weights)
    assert neuron.bias == 0.0
    assert neuron.activation_type == "sigmoid"

def test_parsing_neuron_custom_values():
    """Test ParsingNeuron instantiation with custom bias and activation_type."""
    mock_weights = np.array([0.3, 0.4, 0.5])
    neuron = ParsingNeuron(
        weights=mock_weights,
        bias=0.5,
        activation_type="relu"
    )
    assert np.array_equal(neuron.weights, mock_weights)
    assert neuron.bias == 0.5
    assert neuron.activation_type == "relu"


# === Tests for ParseNetworkState ===

def test_parse_network_state_defaults():
    """Test ParseNetworkState instantiation with default values."""
    state = ParseNetworkState()
    assert state.input_layer == 9
    assert state.hidden_layer == 16
    assert state.output_layer == 8
    assert state.learning_rate == 0.01
    assert state.momentum == 0.9
    assert state.weights_input_hidden is None
    assert state.weights_hidden_output is None
    assert state.bias_hidden is None
    assert state.bias_output is None
    assert state.momentum_ih is None
    assert state.momentum_ho is None
    assert state.momentum_bh is None
    assert state.momentum_bo is None

def test_parse_network_state_custom_values():
    """Test ParseNetworkState instantiation with custom values."""
    custom_w_ih = np.random.rand(9, 16)
    custom_w_ho = np.random.rand(16, 8)
    custom_b_h = np.random.rand(16)
    custom_b_o = np.random.rand(8)
    custom_m_ih = np.zeros((9,16))
    custom_m_ho = np.zeros((16,8))
    custom_m_bh = np.zeros(16)
    custom_m_bo = np.zeros(8)

    state = ParseNetworkState(
        input_layer=10,
        hidden_layer=20,
        output_layer=5,
        learning_rate=0.05,
        momentum=0.8,
        weights_input_hidden=custom_w_ih,
        weights_hidden_output=custom_w_ho,
        bias_hidden=custom_b_h,
        bias_output=custom_b_o,
        momentum_ih=custom_m_ih,
        momentum_ho=custom_m_ho,
        momentum_bh=custom_m_bh,
        momentum_bo=custom_m_bo
    )
    assert state.input_layer == 10
    assert state.hidden_layer == 20
    assert state.output_layer == 5
    assert state.learning_rate == 0.05
    assert state.momentum == 0.8
    assert np.array_equal(state.weights_input_hidden, custom_w_ih)
    assert np.array_equal(state.weights_hidden_output, custom_w_ho)
    assert np.array_equal(state.bias_hidden, custom_b_h)
    assert np.array_equal(state.bias_output, custom_b_o)
    assert np.array_equal(state.momentum_ih, custom_m_ih)
    assert np.array_equal(state.momentum_ho, custom_m_ho)
    assert np.array_equal(state.momentum_bh, custom_m_bh)
    assert np.array_equal(state.momentum_bo, custom_m_bo)
