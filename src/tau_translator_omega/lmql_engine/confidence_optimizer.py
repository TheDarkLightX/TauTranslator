"""
Gradient Descent Optimizer for Pattern Confidence Tuning
======================================================

Implements gradient descent optimization to automatically tune
pattern recognition confidence scores based on translation accuracy.

Author: DarkLightX / Dana Edwards
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class TranslationExample:
    """A training example for confidence optimization."""
    source_text: str
    expected_translation: str
    pattern_type: str
    is_correct: bool
    current_confidence: float


@dataclass
class OptimizationResult:
    """Result of confidence optimization."""
    pattern_type: str
    original_confidence: float
    optimized_confidence: float
    improvement: float
    iterations: int
    final_loss: float


class ConfidenceOptimizer:
    """
    Gradient descent optimizer for pattern recognition confidence scores.
    
    Features:
    - Automatic confidence threshold tuning
    - Learning from translation feedback
    - Adaptive learning rates
    - Regularization to prevent overfitting
    """
    
    def __init__(self, learning_rate: float = 0.01, 
                 regularization: float = 0.001,
                 min_confidence: float = 0.5,
                 max_confidence: float = 0.99):
        """
        Initialize confidence optimizer.
        
        Args:
            learning_rate: Initial learning rate for gradient descent
            regularization: L2 regularization strength
            min_confidence: Minimum allowed confidence score
            max_confidence: Maximum allowed confidence score
        """
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.min_confidence = min_confidence
        self.max_confidence = max_confidence
        
        # Current confidence scores by pattern type
        self.confidence_scores: Dict[str, float] = defaultdict(lambda: 0.85)
        
        # Training history
        self.training_examples: List[TranslationExample] = []
        self.loss_history: List[float] = []
        
        # Optimization state
        self.momentum: Dict[str, float] = defaultdict(float)
        self.beta = 0.9  # Momentum coefficient
    
    def add_training_example(self, example: TranslationExample) -> None:
        """
        Add a training example for optimization.
        
        Args:
            example: Translation example with correctness feedback
        """
        self.training_examples.append(example)
    
    def sigmoid(self, x: float) -> float:
        """Sigmoid activation function."""
        return 1.0 / (1.0 + np.exp(-x))
    
    def sigmoid_derivative(self, x: float) -> float:
        """Derivative of sigmoid function."""
        s = self.sigmoid(x)
        return s * (1 - s)
    
    def compute_loss(self, confidences: Dict[str, float]) -> float:
        """
        Compute cross-entropy loss with L2 regularization.
        
        Args:
            confidences: Current confidence scores
            
        Returns:
            Total loss value
        """
        if not self.training_examples:
            return 0.0
        
        total_loss = 0.0
        
        for example in self.training_examples:
            confidence = confidences.get(example.pattern_type, 0.85)
            
            # Cross-entropy loss
            if example.is_correct:
                # Correct translation - want high confidence
                loss = -np.log(confidence + 1e-10)
            else:
                # Incorrect translation - want low confidence
                loss = -np.log(1 - confidence + 1e-10)
            
            total_loss += loss
        
        # L2 regularization to prevent extreme values
        reg_loss = self.regularization * sum(
            (c - 0.85) ** 2 for c in confidences.values()
        )
        
        return (total_loss / len(self.training_examples)) + reg_loss
    
    def compute_gradients(self, confidences: Dict[str, float]) -> Dict[str, float]:
        """
        Compute gradients for each pattern type.
        
        Args:
            confidences: Current confidence scores
            
        Returns:
            Gradients for each pattern type
        """
        gradients = defaultdict(float)
        counts = defaultdict(int)
        
        for example in self.training_examples:
            pattern_type = example.pattern_type
            confidence = confidences.get(pattern_type, 0.85)
            
            # Gradient of cross-entropy loss
            if example.is_correct:
                # Gradient when example is correct
                grad = -1.0 / (confidence + 1e-10)
            else:
                # Gradient when example is incorrect
                grad = 1.0 / (1 - confidence + 1e-10)
            
            gradients[pattern_type] += grad
            counts[pattern_type] += 1
        
        # Average gradients and add regularization
        for pattern_type in gradients:
            if counts[pattern_type] > 0:
                gradients[pattern_type] /= counts[pattern_type]
                
            # L2 regularization gradient
            gradients[pattern_type] += 2 * self.regularization * (
                confidences.get(pattern_type, 0.85) - 0.85
            )
        
        return dict(gradients)
    
    def optimize(self, max_iterations: int = 100, 
                tolerance: float = 1e-4,
                verbose: bool = False) -> Dict[str, OptimizationResult]:
        """
        Optimize confidence scores using gradient descent with momentum.
        
        Args:
            max_iterations: Maximum optimization iterations
            tolerance: Convergence tolerance
            verbose: Whether to print progress
            
        Returns:
            Optimization results for each pattern type
        """
        if not self.training_examples:
            logger.warning("No training examples available for optimization")
            return {}
        
        # Initialize confidences
        pattern_types = set(ex.pattern_type for ex in self.training_examples)
        current_confidences = {
            pt: self.confidence_scores.get(pt, 0.85) 
            for pt in pattern_types
        }
        original_confidences = current_confidences.copy()
        
        # Optimization loop
        prev_loss = float('inf')
        
        for iteration in range(max_iterations):
            # Compute loss and gradients
            loss = self.compute_loss(current_confidences)
            gradients = self.compute_gradients(current_confidences)
            
            self.loss_history.append(loss)
            
            # Check convergence
            if abs(prev_loss - loss) < tolerance:
                if verbose:
                    print(f"Converged at iteration {iteration}")
                break
            
            # Update with momentum
            for pattern_type in current_confidences:
                if pattern_type in gradients:
                    # Momentum update
                    self.momentum[pattern_type] = (
                        self.beta * self.momentum[pattern_type] - 
                        self.learning_rate * gradients[pattern_type]
                    )
                    
                    # Update confidence
                    new_confidence = current_confidences[pattern_type] + self.momentum[pattern_type]
                    
                    # Clip to valid range
                    new_confidence = np.clip(new_confidence, self.min_confidence, self.max_confidence)
                    
                    current_confidences[pattern_type] = new_confidence
            
            if verbose and iteration % 10 == 0:
                print(f"Iteration {iteration}: Loss = {loss:.4f}")
            
            prev_loss = loss
        
        # Update stored confidences
        self.confidence_scores.update(current_confidences)
        
        # Prepare results
        results = {}
        for pattern_type in pattern_types:
            original = original_confidences[pattern_type]
            optimized = current_confidences[pattern_type]
            
            results[pattern_type] = OptimizationResult(
                pattern_type=pattern_type,
                original_confidence=original,
                optimized_confidence=optimized,
                improvement=optimized - original,
                iterations=iteration + 1,
                final_loss=loss
            )
        
        return results
    
    def get_confidence(self, pattern_type: str) -> float:
        """
        Get optimized confidence for a pattern type.
        
        Args:
            pattern_type: Type of pattern
            
        Returns:
            Optimized confidence score
        """
        return self.confidence_scores.get(pattern_type, 0.85)
    
    def save_state(self, filepath: str) -> None:
        """
        Save optimizer state to file.
        
        Args:
            filepath: Path to save state
        """
        state = {
            'confidence_scores': dict(self.confidence_scores),
            'learning_rate': self.learning_rate,
            'regularization': self.regularization,
            'loss_history': self.loss_history,
            'training_examples': [
                {
                    'source_text': ex.source_text,
                    'expected_translation': ex.expected_translation,
                    'pattern_type': ex.pattern_type,
                    'is_correct': ex.is_correct,
                    'current_confidence': ex.current_confidence
                }
                for ex in self.training_examples[-1000:]  # Keep last 1000 examples
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str) -> None:
        """
        Load optimizer state from file.
        
        Args:
            filepath: Path to load state from
        """
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.confidence_scores = defaultdict(lambda: 0.85, state['confidence_scores'])
        self.learning_rate = state['learning_rate']
        self.regularization = state['regularization']
        self.loss_history = state.get('loss_history', [])
        
        # Reload training examples
        self.training_examples = []
        for ex_data in state.get('training_examples', []):
            self.training_examples.append(TranslationExample(**ex_data))
    
    def adaptive_learning_rate(self) -> None:
        """
        Adjust learning rate based on loss history.
        
        Implements learning rate decay when loss plateaus.
        """
        if len(self.loss_history) < 10:
            return
        
        # Check if loss is plateauing
        recent_losses = self.loss_history[-10:]
        loss_variance = np.var(recent_losses)
        
        if loss_variance < 1e-6:
            # Plateau detected - reduce learning rate
            self.learning_rate *= 0.9
            logger.info(f"Reduced learning rate to {self.learning_rate:.6f}")
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Get detailed optimization report.
        
        Returns:
            Dictionary with optimization statistics
        """
        pattern_stats = defaultdict(lambda: {'correct': 0, 'incorrect': 0})
        
        for example in self.training_examples:
            if example.is_correct:
                pattern_stats[example.pattern_type]['correct'] += 1
            else:
                pattern_stats[example.pattern_type]['incorrect'] += 1
        
        # Calculate accuracy for each pattern type
        accuracies = {}
        for pattern_type, stats in pattern_stats.items():
            total = stats['correct'] + stats['incorrect']
            if total > 0:
                accuracies[pattern_type] = stats['correct'] / total
        
        return {
            'total_examples': len(self.training_examples),
            'pattern_types': len(self.confidence_scores),
            'current_loss': self.loss_history[-1] if self.loss_history else None,
            'learning_rate': self.learning_rate,
            'pattern_accuracies': accuracies,
            'confidence_scores': dict(self.confidence_scores)
        }