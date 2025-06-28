import pytest
import numpy as np
from backend.unified.core import neural_network as nn
from backend.unified.core.neural_types import ParseNetworkState

@pytest.fixture
def simple_network_state() -> ParseNetworkState:
    """Provides a simple ParseNetworkState for testing forward/backward pass."""
    state = ParseNetworkState(
        input_layer=2,
        hidden_layer=2,
        output_layer=1,
        learning_rate=0.1,
        momentum=0.9
    )
    # Initialize weights and biases with deterministic values for consistent tests
    state.weights_input_hidden = np.array([[0.1, 0.2], [0.3, 0.4]])
    state.weights_hidden_output = np.array([[0.5], [0.6]])
    state.bias_hidden = np.array([0.05, 0.15])
    state.bias_output = np.array([0.25])

    # Initialize momentum terms to zeros (as done by initialize_network_weights)
    state.momentum_ih = nn.create_zero_weights(state.input_layer, state.hidden_layer)
    state.momentum_ho = nn.create_zero_weights(state.hidden_layer, state.output_layer)
    state.momentum_bh = nn.create_zero_bias(state.hidden_layer)
    state.momentum_bo = nn.create_zero_bias(state.output_layer)
    return state
