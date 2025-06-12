"""
Gradient Descent Parser - Neural parsing with backpropagation learning
Lightweight implementation optimized for MacBook Pro M2 with 128GB RAM.

Copyright: DarkLightX / Dana Edwards
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import logging

from backend.unified.core.result_enhanced import Result, Success, Failure
from backend.unified.core.plugin_system import LearningPlugin, PluginMetadata, PluginType, ParseContext
from backend.unified.core.error_handling import ParseError, ErrorType


@dataclass
class ParseFeatures:
    """Feature vector for parsing input."""
    word_count: int
    has_quantifier: bool
    has_temporal: bool
    has_modal: bool
    has_causal: bool
    avg_word_length: float
    sentence_complexity: float
    pattern_confidence: float
    semantic_consistency: float


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


# === PURE NEURAL FUNCTIONS (CC=1 each) ===

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


def extract_parsing_features(text: str) -> ParseFeatures:
    """Extract features from input text."""
    words = text.split()
    
    return ParseFeatures(
        word_count=len(words),
        has_quantifier=has_quantifier_words(text),
        has_temporal=has_temporal_words(text),
        has_modal=has_modal_words(text),
        has_causal=has_causal_words(text),
        avg_word_length=calculate_avg_word_length(words),
        sentence_complexity=calculate_sentence_complexity(text),
        pattern_confidence=calculate_pattern_confidence(text),
        semantic_consistency=calculate_semantic_consistency(text)
    )


def has_quantifier_words(text: str) -> bool:
    """Check if text has quantifier words."""
    quantifiers = {'all', 'every', 'some', 'many', 'few', 'most', 'several', 'each'}
    return any(word in text.lower() for word in quantifiers)


def has_temporal_words(text: str) -> bool:
    """Check if text has temporal words."""
    temporal = {'when', 'while', 'before', 'after', 'during', 'until', 'since'}
    return any(word in text.lower() for word in temporal)


def has_modal_words(text: str) -> bool:
    """Check if text has modal words."""
    modals = {'must', 'should', 'can', 'may', 'might', 'could', 'ought', 'will', 'would'}
    return any(word in text.lower() for word in modals)


def has_causal_words(text: str) -> bool:
    """Check if text has causal words."""
    causal = {'causes', 'leads to', 'results in', 'because', 'since', 'therefore', 'thus'}
    return any(phrase in text.lower() for phrase in causal)


def calculate_avg_word_length(words: List[str]) -> float:
    """Calculate average word length."""
    if not words:
        return 0.0
    return sum(len(word) for word in words) / len(words)


def calculate_sentence_complexity(text: str) -> float:
    """Calculate sentence complexity score."""
    complexity_indicators = [
        len(text.split()),  # Word count
        text.count(','),    # Comma count
        text.count('('),    # Parentheses
        text.count('and') + text.count('or'),  # Conjunctions
    ]
    return sum(complexity_indicators) / 100.0  # Normalize


def calculate_pattern_confidence(text: str) -> float:
    """Calculate pattern matching confidence."""
    # Simple heuristic based on structure
    has_subject_verb = bool(re.search(r'\w+\s+(is|are|was|were|has|have)\s+\w+', text))
    has_clear_structure = bool(re.search(r'^(all|every|some|if|when)\s+', text, re.IGNORECASE))
    
    confidence = 0.5  # Base confidence
    if has_subject_verb:
        confidence += 0.2
    if has_clear_structure:
        confidence += 0.3
    
    return min(confidence, 1.0)


def calculate_semantic_consistency(text: str) -> float:
    """Calculate semantic consistency score."""
    # Simple consistency checks
    inconsistency_patterns = [
        r'car.*thinks',
        r'house.*runs',
        r'book.*drives',
        r'system.*sleeps'
    ]
    
    inconsistencies = sum(1 for pattern in inconsistency_patterns 
                         if re.search(pattern, text, re.IGNORECASE))
    
    return max(0.0, 1.0 - (inconsistencies * 0.3))


def features_to_vector(features: ParseFeatures) -> np.ndarray:
    """Convert features to numpy vector."""
    return np.array([
        features.word_count / 20.0,  # Normalize
        float(features.has_quantifier),
        float(features.has_temporal),
        float(features.has_modal),
        float(features.has_causal),
        features.avg_word_length / 10.0,
        features.sentence_complexity,
        features.pattern_confidence,
        features.semantic_consistency
    ])


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
    return (x > 0).astype(float)


def forward_pass(input_vector: np.ndarray, state: ParseNetworkState) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Perform forward pass through network."""
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


class GradientDescentParser(LearningPlugin):
    """
    Neural parser using gradient descent learning.
    Optimized for MacBook Pro M2 with lightweight architecture.
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        """Initialize gradient descent parser."""
        metadata = PluginMetadata(
            name="gradient_descent_parser",
            version="1.0.0",
            plugin_type=PluginType.LEARNING,
            priority=60,
            description="Neural parser with gradient descent learning",
            config={
                'max_memory_mb': 256,  # Conservative for M2
                'batch_size': 32,
                'max_epochs': 100,
                'early_stopping_patience': 10
            }
        )
        super().__init__(metadata)
        
        self.model_path = model_path or Path("models/gradient_parser.json")
        self.network_state = ParseNetworkState()
        self.training_history = []
        self.initialize_network()
        self.load_model()
    
    def can_handle(self, text: str, context: ParseContext) -> bool:
        """Neural parser can handle any text."""
        return True
    
    def process(self, text: str, context: ParseContext) -> Result[str]:
        """Process text using neural network."""
        return neural_parse_text(text, self.network_state)
    
    def learn_from_correction(self, original: str, corrected: str, feedback: str):
        """Learn from correction using backpropagation."""
        neural_learn_from_correction(original, corrected, feedback, self.network_state)
        self.save_model()
    
    def predict_corrections(self, text: str) -> List[str]:
        """Predict corrections using neural network."""
        return neural_predict_corrections(text, self.network_state)
    
    def get_adaptation_suggestions(self, text: str) -> List[str]:
        """Get neural adaptation suggestions."""
        return neural_adaptation_suggestions(text, self.network_state)
    
    def train_on_batch(self, examples: List[Tuple[str, str]]):
        """Train on batch of examples."""
        neural_train_batch(examples, self.network_state)
        self.save_model()
    
    def initialize_network(self):
        """Initialize neural network."""
        initialize_network_weights(self.network_state)
    
    def load_model(self):
        """Load neural model from disk."""
        load_neural_model(self.model_path, self.network_state)
    
    def save_model(self):
        """Save neural model to disk."""
        save_neural_model(self.model_path, self.network_state)


# === NEURAL PROCESSING FUNCTIONS ===

def neural_parse_text(text: str, state: ParseNetworkState) -> Result[str]:
    """Parse text using neural network."""
    features = extract_parsing_features(text)
    input_vector = features_to_vector(features)
    
    _, _, output = forward_pass(input_vector, state)
    parse_type = predict_parse_type(output)
    confidence = float(np.max(output))
    
    if confidence > 0.7:
        return Success(f"neural_{parse_type}({text})")
    else:
        from backend.unified.core.error_handling import create_parse_error
        error = create_parse_error(
            ErrorType.PATTERN_MISMATCH,
            f"Low confidence neural parse: {confidence:.2f}",
            0,
            text
        )
        return Failure(error)


def neural_learn_from_correction(original: str, corrected: str, feedback: str, state: ParseNetworkState):
    """Learn from correction using neural network."""
    # Extract features and create training example
    features = extract_parsing_features(original)
    input_vector = features_to_vector(features)
    
    # Determine target parse type from correction
    target_type = infer_parse_type_from_correction(corrected, feedback)
    target_vector = create_target_vector(target_type)
    
    # Perform forward and backward pass
    hidden_output, output_input, actual_output = forward_pass(input_vector, state)
    backward_pass(input_vector, target_vector, hidden_output, output_input, actual_output, state)


def infer_parse_type_from_correction(corrected: str, feedback: str) -> str:
    """Infer parse type from correction."""
    if 'quantified' in feedback.lower() or any(q in corrected.lower() for q in ['all', 'every', 'some']):
        return 'quantified'
    elif 'temporal' in feedback.lower() or any(t in corrected.lower() for t in ['when', 'while', 'before']):
        return 'temporal'
    elif 'modal' in feedback.lower() or any(m in corrected.lower() for m in ['must', 'should', 'can']):
        return 'modal'
    elif 'causal' in feedback.lower() or 'causes' in corrected.lower():
        return 'causal'
    else:
        return 'simple'


def neural_predict_corrections(text: str, state: ParseNetworkState) -> List[str]:
    """Predict corrections using neural network."""
    features = extract_parsing_features(text)
    input_vector = features_to_vector(features)
    
    _, _, output = forward_pass(input_vector, state)
    
    # Get top 3 predicted parse types
    top_indices = np.argsort(output)[-3:][::-1]
    parse_types = ['quantified', 'temporal', 'modal', 'causal', 'comparative', 'conditional', 'simple', 'complex']
    
    predictions = []
    for idx in top_indices:
        confidence = output[idx]
        if confidence > 0.3:
            parse_type = parse_types[idx]
            predictions.append(f"Try {parse_type} structure (confidence: {confidence:.2f})")
    
    return predictions


def neural_adaptation_suggestions(text: str, state: ParseNetworkState) -> List[str]:
    """Generate neural adaptation suggestions."""
    features = extract_parsing_features(text)
    
    suggestions = []
    
    if features.sentence_complexity > 0.8:
        suggestions.append("Neural network suggests breaking into simpler sentences")
    
    if features.semantic_consistency < 0.5:
        suggestions.append("Neural network detects semantic inconsistency")
    
    if features.pattern_confidence < 0.6:
        suggestions.append("Neural network suggests using clearer sentence structure")
    
    return suggestions


def neural_train_batch(examples: List[Tuple[str, str]], state: ParseNetworkState):
    """Train neural network on batch of examples."""
    for original, target_type in examples:
        features = extract_parsing_features(original)
        input_vector = features_to_vector(features)
        target_vector = create_target_vector(target_type)
        
        hidden_output, output_input, actual_output = forward_pass(input_vector, state)
        backward_pass(input_vector, target_vector, hidden_output, output_input, actual_output, state)


def load_neural_model(model_path: Path, state: ParseNetworkState):
    """Load neural model from disk."""
    if not model_path.exists():
        return
    
    try:
        with open(model_path, 'r') as f:
            data = json.load(f)
            
        # Load weights and biases
        state.weights_input_hidden = np.array(data.get('weights_ih', []))
        state.weights_hidden_output = np.array(data.get('weights_ho', []))
        state.bias_hidden = np.array(data.get('bias_h', []))
        state.bias_output = np.array(data.get('bias_o', []))
        
        # Reshape if needed
        if state.weights_input_hidden.size > 0:
            state.weights_input_hidden = state.weights_input_hidden.reshape(state.input_layer, state.hidden_layer)
        if state.weights_hidden_output.size > 0:
            state.weights_hidden_output = state.weights_hidden_output.reshape(state.hidden_layer, state.output_layer)
            
    except (json.JSONDecodeError, IOError, ValueError):
        # Reinitialize on load failure
        initialize_network_weights(state)


def save_neural_model(model_path: Path, state: ParseNetworkState):
    """Save neural model to disk."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        'weights_ih': state.weights_input_hidden.tolist(),
        'weights_ho': state.weights_hidden_output.tolist(),
        'bias_h': state.bias_hidden.tolist(),
        'bias_o': state.bias_output.tolist(),
        'learning_rate': state.learning_rate,
        'momentum': state.momentum
    }
    
    try:
        with open(model_path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass  # Fail silently if can't save


def create_gradient_descent_parser(model_path: Optional[Path] = None) -> GradientDescentParser:
    """Create gradient descent parser instance."""
    return GradientDescentParser(model_path)