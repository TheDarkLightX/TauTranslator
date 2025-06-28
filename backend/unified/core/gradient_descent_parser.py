"""
Gradient Descent Parser - Neural parsing with backpropagation learning
Lightweight implementation optimized for MacBook Pro M2 with 128GB RAM.

Copyright: DarkLightX / Dana Edwards
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import json
from pathlib import Path
import re
import logging

from backend.unified.core.domain_types import AppError, Result, Success, Failure
from backend.unified.core.plugin_system import LearningPlugin, PluginMetadata, PluginType, ParseContext
from backend.unified.core.error_handling import ParseError, ErrorType

# New imports for refactored modules
from .neural_types import ParseFeatures, ParseNetworkState # ParsingNeuron not used by the shell
from . import feature_extraction as fe
from . import neural_network as nn

logger = logging.getLogger(__name__)

# === Gradient Descent Parser Class ===

class GradientDescentParser(LearningPlugin):
    # --- Plugin System Compliance: metadata is set by super().__init__ ---
    # --- Implementation of ParsingPlugin abstract methods ---
    def can_handle(self, text: str, context: ParseContext) -> bool:
        """Determines if this parser can handle the given text."""
        # For now, assume it can handle any non-empty text for semantic type prediction.
        # More sophisticated logic can be added later (e.g., based on context or pre-checks).
        return bool(text.strip())

    def process(self, text: str, context: ParseContext) -> Result[str, AppError]:
        """Processes the text to predict its semantic type. Wraps the existing parse method."""
        # The ParseContext from plugin_system might be richer than Optional[ParseContext]
        # currently in self.parse. For now, we pass it directly.
        return self.parse(text, context) # type: ignore

    # --- Implementation of LearningPlugin abstract methods ---
    def learn_from_correction(self, original: str, corrected: str, feedback: str) -> None:
        """Learns from a correction. Wraps the existing learn method."""
        # The abstract method expects no return, while self.learn returns Result[None].
        # We'll call self.learn and discard the result for now.
        # Context is also handled differently; passing None for now.
        _ = self.learn(original_text=original, corrected_text=corrected, feedback=feedback, context=None)
        return

    def predict_corrections(self, text: str) -> List[str]:
        """Predicts corrections for the given text. Wraps get_corrections."""
        # Context is handled differently; passing None for now.
        return self.get_corrections(text, context=None)

    def get_adaptation_suggestions(self, text: str) -> List[str]:
        """Gets adaptation suggestions. Wraps get_suggestions."""
        # Context is handled differently; passing None for now.
        return self.get_suggestions(text, context=None)

    # --- Original GradientDescentParser methods ---

    def __init__(self, metadata: PluginMetadata, model_path: Optional[Path] = None):
        """
        Initialize the parser.
        Loads an existing model if model_path is provided, otherwise uses default from metadata config.
        """
        super().__init__(metadata) # Initialize base plugin with metadata
        
        # Determine the model path: use provided, then config, then a hardcoded default
        default_model_filename = "models/gdp_model.json" # A fallback default
        config_model_path = self.metadata.config.get("default_model_path", default_model_filename)
        
        # Ensure config_model_path is treated as relative to project root if not absolute
        # Assuming project root is where 'models/' directory would be if relative path is used.
        # For simplicity, we'll assume Path handles this correctly or it's an absolute path.
        # A more robust solution might involve passing a base_path or using a global config for paths.
        
        self.model_path = model_path if model_path is not None else Path(config_model_path)
        """
        Initialize the parser.
        Loads an existing model if model_path is provided, otherwise initializes a new model.
        """
        self.state = ParseNetworkState()
        # self.model_path is now set above using metadata and argument

        if self.model_path.exists():
            logger.info(f"Loading model from {self.model_path}")
            self._load_model(self.model_path)
        else:
            logger.info("Initializing new model.")
            self._initialize_model()
            if self.model_path: # Save initial model if path was given but file didn't exist
                self._save_model(self.model_path)


    def _initialize_model(self):
        """Initializes a new neural network model with random weights."""
        nn.initialize_network_weights(self.state)
        logger.debug("New model initialized with random weights.")

    def parse(self, text: str, context: Optional[ParseContext] = None) -> Result[str, AppError]:
        """
        Parse the input text and predict its semantic type.
        """
        if not text:
            return Failure(AppError(error_code=ErrorType.VALIDATION_ERROR.value, message="Input text cannot be empty."))
        
        try:
            features = fe.extract_parsing_features(text)
            input_vector = fe.features_to_vector(features)
            
            _, _, output = nn.forward_pass(input_vector, self.state)
            predicted_type = nn.predict_parse_type(output)
            
            logger.debug(f"Parsed text: '{text}', Predicted type: {predicted_type}")
            return Success(predicted_type)
        except Exception as e:
            logger.error(f"Error during parsing: {e}", exc_info=True)
            return Failure(AppError(error_code="PROCESSING_ERROR", message=f"Parsing failed: {e}"))

    def learn(self, original_text: str, corrected_text: str, 
              feedback: Optional[str] = None, context: Optional[ParseContext] = None) -> Result[None, AppError]:
        """
        Train the neural network based on corrected text or feedback.
        """
        if not original_text or not corrected_text:
             return Failure(AppError(error_code=ErrorType.VALIDATION_ERROR.value, message="Original and corrected text cannot be empty for learning."))

        try:
            target_type = identify_parse_type_from_feedback(corrected_text, feedback)
            features = fe.extract_parsing_features(original_text)
            input_vector = fe.features_to_vector(features)
            target_vector = nn.create_target_vector(target_type)
            
            hidden_output, output_input, actual_output = nn.forward_pass(input_vector, self.state)
            nn.backward_pass(input_vector, target_vector, hidden_output, output_input, actual_output, self.state)
            
            logger.debug(f"Learned from: Original='{original_text}', Corrected='{corrected_text}', TargetType='{target_type}'")
            
            if self.model_path:
                self._save_model(self.model_path)
            return Success(None)
        except Exception as e:
            logger.error(f"Error during learning: {e}", exc_info=True)
            return Failure(AppError(message=f"Learning failed: {e}", error_code=ErrorType.PROCESSING.value))

    def get_suggestions(self, text: str, context: Optional[ParseContext] = None) -> List[str]:
        """
        Provide suggestions for improving the input text based on neural analysis.
        """
        return neural_adaptation_suggestions(text, self.state) # Pass state for signature consistency

    def get_corrections(self, text: str, context: Optional[ParseContext] = None) -> List[str]:
        """
        Provide potential corrections for the input text.
        """
        return neural_predict_corrections(text, self.state)

    def get_state(self) -> Dict:
        """Get current model state (weights, biases)."""
        return {
            'weights_input_hidden': self.state.weights_input_hidden.tolist() if self.state.weights_input_hidden is not None else [],
            'weights_hidden_output': self.state.weights_hidden_output.tolist() if self.state.weights_hidden_output is not None else [],
            'bias_hidden': self.state.bias_hidden.tolist() if self.state.bias_hidden is not None else [],
            'bias_output': self.state.bias_output.tolist() if self.state.bias_output is not None else [],
            'learning_rate': self.state.learning_rate,
            'momentum': self.state.momentum
        }

    def set_state(self, state_dict: Dict):
        """Set model state from a dictionary."""
        self.state.weights_input_hidden = np.array(state_dict.get('weights_input_hidden', []))
        self.state.weights_hidden_output = np.array(state_dict.get('weights_hidden_output', []))
        self.state.bias_hidden = np.array(state_dict.get('bias_hidden', []))
        self.state.bias_output = np.array(state_dict.get('bias_output', []))
        
        # Reshape if needed, ensure correct dimensions
        if self.state.weights_input_hidden.size > 0:
            self.state.weights_input_hidden = self.state.weights_input_hidden.reshape(self.state.input_layer, self.state.hidden_layer)
        if self.state.weights_hidden_output.size > 0:
            self.state.weights_hidden_output = self.state.weights_hidden_output.reshape(self.state.hidden_layer, self.state.output_layer)
            
        self.state.learning_rate = state_dict.get('learning_rate', self.state.learning_rate)
        self.state.momentum = state_dict.get('momentum', self.state.momentum)
        logger.debug("Model state updated.")

    def _save_model(self, model_path: Path):
        """Saves the current neural network model to a file."""
        save_neural_model_file(model_path, self.state)
        logger.info(f"Model saved to {model_path}")

    def _load_model(self, model_path: Path):
        """Loads a neural network model from a file."""
        load_neural_model_file(model_path, self.state)
        logger.info(f"Model loaded from {model_path}")

# === Plugin Metadata and Helper Functions ===

def get_plugin_metadata() -> PluginMetadata:
    """Return metadata for the Gradient Descent Parser plugin."""
    return PluginMetadata(
        name="gradient_descent_parser",
        version="0.2.1", # Incremented version for this fix
        plugin_type=PluginType.LEARNING,
        priority=60,
        description="Neural network parser with gradient descent learning capabilities, refactored for clarity.",
        dependencies=["numpy"],
        config={"default_model_path": "models/gdp_model.json"}
    )

def identify_parse_type_from_feedback(corrected: str, feedback: Optional[str]) -> str:
    """Identify parse type from corrected text or feedback."""
    if feedback:
        # Prioritize explicit feedback
        f_lower = feedback.lower()
        if 'quantif' in f_lower: return 'quantified'
        if 'temporal' in f_lower: return 'temporal'
        if 'modal' in f_lower: return 'modal'
        if 'causal' in f_lower: return 'causal'
        if 'comparative' in f_lower: return 'comparative'
        if 'conditional' in f_lower: return 'conditional'
        if 'complex' in f_lower: return 'complex'
        # If feedback doesn't match known types, proceed to text analysis
    
    # Analyze corrected text using feature extraction helpers
    if fe.has_quantifier_words(corrected): return 'quantified'
    if fe.has_temporal_words(corrected): return 'temporal'
    if fe.has_modal_words(corrected): return 'modal'
    if fe.has_causal_words(corrected): return 'causal'
    
    # Fallback to structural heuristics for less clear types
    # Ensure 'when' for conditional isn't primarily temporal
    if ('if' in corrected.lower() or \
        ('when' in corrected.lower() and not fe.has_temporal_words(corrected))):
        return 'conditional'
    if 'than' in corrected.lower() or 'as much as' in corrected.lower():
        return 'comparative'
    
    # Simplified complexity check for 'complex' vs 'simple'
    # Consider using fe.calculate_sentence_complexity if more nuance is needed
    if len(corrected.split()) > 10 or ',' in corrected or len(re.findall(r'(and|or|but)', corrected.lower())) > 1:
        return 'complex'
        
    return 'simple'


def neural_predict_corrections(text: str, state: ParseNetworkState) -> List[str]:
    """Predict corrections using neural network."""
    features = fe.extract_parsing_features(text)
    input_vector = fe.features_to_vector(features)
    
    _, _, output = nn.forward_pass(input_vector, state)
    
    # Get top 3 predicted parse types
    # Note: parse_types list is duplicated here and in nn module. Consider centralizing.
    parse_types = ['quantified', 'temporal', 'modal', 'causal', 'comparative', 'conditional', 'simple', 'complex']
    top_indices = np.argsort(output)[-3:][::-1] 
    
    predictions = []
    for idx in top_indices:
        confidence = output[idx]
        if confidence > 0.3: # Confidence threshold
            parse_type = parse_types[idx]
            predictions.append(f"Try {parse_type} structure (confidence: {confidence:.2f})")
    
    return predictions


def neural_adaptation_suggestions(text: str, state: ParseNetworkState) -> List[str]:
    """Generate neural adaptation suggestions. `state` is kept for signature consistency."""
    features = fe.extract_parsing_features(text) # Only needs features
    
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
        features = fe.extract_parsing_features(original)
        input_vector = fe.features_to_vector(features)
        target_vector = nn.create_target_vector(target_type)
        
        hidden_output, output_input, actual_output = nn.forward_pass(input_vector, state)
        nn.backward_pass(input_vector, target_vector, hidden_output, output_input, actual_output, state)
    logger.debug(f"Trained batch of {len(examples)} examples.")


def load_neural_model_file(model_path: Path, state: ParseNetworkState):
    """Load neural model from disk. Initializes a new model if loading fails or file not found."""
    if not model_path.exists():
        logger.warning(f"Model file not found: {model_path}. Initializing new model.")
        nn.initialize_network_weights(state)
        return
    
    try:
        with open(model_path, 'r') as f:
            data = json.load(f)
            
        # Helper to safely get and reshape arrays
        def _get_and_reshape(key, shape_dims, default_create_func):
            arr_data = data.get(key, [])
            arr = np.array(arr_data)
            if arr.size > 0:
                expected_size = np.prod(shape_dims)
                if arr.size != expected_size:
                    logger.error(f"Mismatched {key} size. Expected {expected_size}, got {arr.size}. Using default.")
                    return default_create_func(*shape_dims)
                return arr.reshape(shape_dims)
            return default_create_func(*shape_dims)

        state.weights_input_hidden = _get_and_reshape('weights_ih', (state.input_layer, state.hidden_layer), nn.create_zero_weights)
        state.weights_hidden_output = _get_and_reshape('weights_ho', (state.hidden_layer, state.output_layer), nn.create_zero_weights)
        state.bias_hidden = _get_and_reshape('bias_h', (state.hidden_layer,), nn.create_zero_bias) # Bias shape is 1D
        state.bias_output = _get_and_reshape('bias_o', (state.output_layer,), nn.create_zero_bias) # Bias shape is 1D

        state.learning_rate = data.get('learning_rate', state.learning_rate)
        state.momentum = data.get('momentum', state.momentum)
        logger.info(f"Model successfully loaded from {model_path}.")
            
    except (json.JSONDecodeError, IOError, ValueError) as e:
        logger.error(f"Error loading model from {model_path}: {e}. Reinitializing.", exc_info=True)
        nn.initialize_network_weights(state)


def save_neural_model_file(model_path: Path, state: ParseNetworkState):
    """Save neural model to disk."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        'weights_ih': state.weights_input_hidden.tolist() if state.weights_input_hidden is not None else [],
        'weights_ho': state.weights_hidden_output.tolist() if state.weights_hidden_output is not None else [],
        'bias_h': state.bias_hidden.tolist() if state.bias_hidden is not None else [],
        'bias_o': state.bias_output.tolist() if state.bias_output is not None else [],
        'learning_rate': state.learning_rate,
        'momentum': state.momentum
    }
    
    try:
        with open(model_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Model data saved to {model_path}")
    except IOError as e:
        logger.error(f"Could not save model to {model_path}: {e}", exc_info=True)


def create_gradient_descent_parser(model_path: Optional[Path] = None) -> GradientDescentParser:
    """Create gradient descent parser instance."""
    metadata = get_plugin_metadata()
    return GradientDescentParser(metadata=metadata, model_path=model_path)
