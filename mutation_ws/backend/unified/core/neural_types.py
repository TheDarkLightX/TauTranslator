"""
Data types for the neural parsing components.

Copyright (c) DarkLightX / Dana Edwards
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class ParseFeatures:
    """Feature vector for parsing input."""
    word_count: int = 0
    has_quantifier: bool = False
    has_temporal: bool = False
    has_modal: bool = False
    has_causal: bool = False
    avg_word_length: float = 0.0
    sentence_complexity: float = 0.0
    pattern_confidence: float = 0.5  # Base confidence if no structure matched
    semantic_consistency: float = 1.0 # Assumes consistent if no inconsistencies found


@dataclass
class ParsingNeuron:
    """Simple neuron for parsing decisions."""
    weights: np.ndarray
    bias: float = 0.0
    activation_type: str = "sigmoid"


@dataclass
class ParseNetworkState:
    """State of the parsing neural network."""
    input_layer: int = 9  # Feature count
    hidden_layer: int = 16
    output_layer: int = 8  # Parse pattern types
    learning_rate: float = 0.01
    momentum: float = 0.9
    
    # Network weights
    weights_input_hidden: np.ndarray = None
    weights_hidden_output: np.ndarray = None
    bias_hidden: np.ndarray = None
    bias_output: np.ndarray = None
    
    # Momentum terms
    momentum_ih: np.ndarray = None
    momentum_ho: np.ndarray = None
    momentum_bh: np.ndarray = None
    momentum_bo: np.ndarray = None
