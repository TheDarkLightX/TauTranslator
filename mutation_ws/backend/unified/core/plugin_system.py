"""
Plugin System Architecture - Extensible parsing with domain-specific plugins
Includes ML plugin for adaptive parsing on MacBook Pro M2.

Copyright: DarkLightX / Dana Edwards
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from pathlib import Path

from .domain_types import Result, Success, Failure, AppError
from backend.unified.core.error_handling import ParseError, ErrorContext
from backend.unified.core.semantic_validator import ValidationResult


class PluginType(Enum):
    """Types of parsing plugins."""
    DOMAIN_SPECIFIC = "domain_specific"
    PREPROCESSING = "preprocessing"
    POSTPROCESSING = "postprocessing"
    VALIDATION = "validation"
    LEARNING = "learning"
    RECOVERY = "recovery"


@dataclass
class PluginMetadata:
    """Plugin metadata and configuration."""
    name: str
    version: str
    plugin_type: PluginType
    priority: int = 50  # 0-100, higher = earlier execution
    enabled: bool = True
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseContext:
    """Enhanced context for plugin parsing."""
    original_text: str
    preprocessed_text: str
    attempted_patterns: List[str] = field(default_factory=list)
    plugin_results: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


# === PLUGIN INTERFACES ===

class ParsingPlugin(ABC):
    """Base interface for all parsing plugins."""
    
    def __init__(self, metadata: PluginMetadata):
        """Initialize plugin with metadata."""
        self.metadata = metadata
        self.logger = logging.getLogger(f"plugin.{metadata.name}")
        self.enabled = metadata.enabled
    
    @abstractmethod
    def can_handle(self, text: str, context: ParseContext) -> bool:
        """Check if plugin can handle the given text."""
        pass
    
    @abstractmethod
    def process(self, text: str, context: ParseContext) -> Result[str, AppError]:
        """Process text and return result or error."""
        pass
    
    def get_confidence(self, text: str, context: ParseContext) -> float:
        """Get confidence score for handling this text."""
        return 0.5  # Default neutral confidence


class DomainSpecificPlugin(ParsingPlugin):
    """Plugin for domain-specific parsing patterns."""
    
    @abstractmethod
    def get_domain_patterns(self) -> Dict[str, str]:
        """Get domain-specific regex patterns."""
        pass
    
    @abstractmethod
    def get_domain_vocabulary(self) -> Dict[str, str]:
        """Get domain-specific vocabulary mappings."""
        pass


class LearningPlugin(ParsingPlugin):
    """Plugin for machine learning-based adaptive parsing."""
    
    @abstractmethod
    def learn_from_correction(self, original: str, corrected: str, feedback: str):
        """Learn from user corrections."""
        pass
    
    @abstractmethod
    def predict_corrections(self, text: str) -> List[str]:
        """Predict potential corrections."""
        pass
    
    @abstractmethod
    def get_adaptation_suggestions(self, text: str) -> List[str]:
        """Get suggestions based on learned patterns."""
        pass


# === CONCRETE PLUGIN IMPLEMENTATIONS ===

class BusinessDomainPlugin(DomainSpecificPlugin):
    """Plugin for business domain parsing."""
    
    def __init__(self):
        metadata = PluginMetadata(
            name="business_domain",
            version="1.0.0",
            plugin_type=PluginType.DOMAIN_SPECIFIC,
            priority=70,
            description="Handles business domain terms and patterns"
        )
        super().__init__(metadata)
    
    def can_handle(self, text: str, context: ParseContext) -> bool:
        """Check if text contains business terms."""
        return has_business_indicators(text)
    
    def process(self, text: str, context: ParseContext) -> Result[str, AppError]:
        """Process business domain text."""
        return process_business_text(text, self.get_domain_patterns())
    
    def get_domain_patterns(self) -> Dict[str, str]:
        """Get business domain patterns."""
        return {
            'customer_transaction': r'customer\s+(\w+)\s+(?:purchases|buys|orders)\s+(.+)',
            'service_requirement': r'(?:service|system)\s+(?:must|should)\s+(.+)',
            'business_rule': r'(?:if|when)\s+(.+?),?\s+then\s+(.+)',
            'compliance_rule': r'all\s+(.+?)\s+must\s+comply\s+with\s+(.+)'
        }
    
    def get_domain_vocabulary(self) -> Dict[str, str]:
        """Get business vocabulary mappings."""
        return {
            'purchase': 'buy',
            'acquire': 'buy',
            'client': 'customer',
            'regulation': 'rule',
            'mandate': 'requirement'
        }


class SimpleLearningPlugin(LearningPlugin):
    """Lightweight ML plugin optimized for MacBook Pro M2."""
    
    def __init__(self, model_path: Optional[Path] = None):
        metadata = PluginMetadata(
            name="simple_learning",
            version="1.0.0", 
            plugin_type=PluginType.LEARNING,
            priority=30,
            description="Lightweight adaptive learning for parsing improvements",
            config={
                'max_memory_mb': 512,  # Limit for M2 efficiency
                'learning_rate': 0.01,
                'pattern_cache_size': 1000
            }
        )
        super().__init__(metadata)
        self.model_path = model_path or Path("models/simple_learning.json")
        self.corrections_cache = {}
        self.pattern_frequency = {}
        self.load_model()
    
    def can_handle(self, text: str, context: ParseContext) -> bool:
        """Simple learning can handle any text."""
        return True
    
    def process(self, text: str, context: ParseContext) -> Result[str, AppError]:
        """Process text with learned adaptations."""
        return apply_learned_adaptations(text, self.corrections_cache)
    
    def learn_from_correction(self, original: str, corrected: str, feedback: str):
        """Learn from user correction (lightweight approach)."""
        learn_simple_correction(self.corrections_cache, original, corrected, feedback)
        self.save_model()
    
    def predict_corrections(self, text: str) -> List[str]:
        """Predict corrections using simple pattern matching."""
        return predict_simple_corrections(text, self.corrections_cache)
    
    def get_adaptation_suggestions(self, text: str) -> List[str]:
        """Get adaptation suggestions."""
        return generate_adaptation_suggestions(text, self.pattern_frequency)
    
    def load_model(self):
        """Load lightweight model from disk."""
        load_simple_model(self.model_path, self.corrections_cache, self.pattern_frequency)
    
    def save_model(self):
        """Save lightweight model to disk."""
        save_simple_model(self.model_path, self.corrections_cache, self.pattern_frequency)


class ValidationPlugin(ParsingPlugin):
    """Plugin for enhanced validation checks."""
    
    def __init__(self):
        metadata = PluginMetadata(
            name="enhanced_validation",
            version="1.0.0",
            plugin_type=PluginType.VALIDATION,
            priority=80,
            description="Enhanced semantic and logical validation"
        )
        super().__init__(metadata)
    
    def can_handle(self, text: str, context: ParseContext) -> bool:
        """Validation can handle any parsed text."""
        return True
    
    def process(self, text: str, context: ParseContext) -> Result[str, AppError]:
        """Validate text for logical consistency."""
        return validate_enhanced_semantics(text, context)


# === PURE FUNCTIONS FOR PLUGINS (CC=1 each) ===

def has_business_indicators(text: str) -> bool:
    """Check if text has business domain indicators."""
    business_terms = {'customer', 'purchase', 'order', 'service', 'compliance', 'regulation', 'business'}
    return any(term in text.lower() for term in business_terms)


def process_business_text(text: str, patterns: Dict[str, str]) -> Result[str, AppError]:
    """Process text using business domain patterns."""
    import re
    
    for pattern_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return Success(f"business_{pattern_name}({', '.join(match.groups())})")
    
    return Success(text)  # No transformation needed


def apply_learned_adaptations(text: str, corrections_cache: Dict) -> Result[str, AppError]:
    """Apply learned adaptations to text."""
    adapted_text = text
    
    # Apply cached corrections
    for original_pattern, correction in corrections_cache.items():
        adapted_text = adapted_text.replace(original_pattern, correction)
    
    return Success(adapted_text)


def learn_simple_correction(corrections_cache: Dict, original: str, corrected: str, feedback: str):
    """Learn simple correction patterns."""
    # Extract simple substitution patterns
    if len(original.split()) <= 3:  # Only learn from short phrases
        corrections_cache[original.lower()] = corrected.lower()


def predict_simple_corrections(text: str, corrections_cache: Dict) -> List[str]:
    """Predict corrections using cached patterns."""
    predictions = []
    
    words = text.lower().split()
    for phrase_len in [1, 2, 3]:
        for i in range(len(words) - phrase_len + 1):
            phrase = ' '.join(words[i:i+phrase_len])
            if phrase in corrections_cache:
                correction = corrections_cache[phrase]
                corrected_text = text.lower().replace(phrase, correction)
                predictions.append(corrected_text)
    
    return predictions[:3]  # Return top 3 predictions


def generate_adaptation_suggestions(text: str, pattern_frequency: Dict) -> List[str]:
    """Generate adaptation suggestions based on frequency."""
    suggestions = []
    
    # Suggest more common patterns
    for pattern, frequency in sorted(pattern_frequency.items(), key=lambda x: x[1], reverse=True)[:3]:
        if pattern not in text.lower():
            suggestions.append(f"Consider using common pattern: '{pattern}'")
    
    return suggestions


def load_simple_model(model_path: Path, corrections_cache: Dict, pattern_frequency: Dict):
    """Load simple model from JSON."""
    if model_path.exists():
        try:
            with open(model_path, 'r') as f:
                data = json.load(f)
                corrections_cache.update(data.get('corrections', {}))
                pattern_frequency.update(data.get('patterns', {}))
        except (json.JSONDecodeError, IOError):
            pass  # Start with empty model if loading fails


def save_simple_model(model_path: Path, corrections_cache: Dict, pattern_frequency: Dict):
    """Save simple model to JSON."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        'corrections': corrections_cache,
        'patterns': pattern_frequency
    }
    
    try:
        with open(model_path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass  # Fail silently if can't save


def validate_enhanced_semantics(text: str, context: ParseContext) -> Result[str, AppError]:
    """Validate text with enhanced semantic checks."""
    # Simple validation - could be enhanced
    if len(text.split()) > 50:
        from backend.unified.core.error_handling import create_parse_error, ErrorType
        error = create_parse_error(
            ErrorType.VALIDATION_ERROR,
            "Sentence too complex for reliable parsing",
            0,
            text
        )
        return Failure(error_code=error.error_type.value, message=error.message)
    
    return Success(text)


class PluginManager:
    """
    Manages and orchestrates parsing plugins.
    Provides extensible architecture for domain-specific parsing.
    """
    
    def __init__(self):
        """Initialize plugin manager."""
        self.plugins: Dict[str, ParsingPlugin] = {}
        self.plugin_order: List[str] = []
        self.logger = logging.getLogger(__name__)
        self._register_default_plugins()
    
    def register_plugin(self, plugin: ParsingPlugin):
        """Register a new plugin."""
        register_plugin_with_manager(self, plugin)
    
    def unregister_plugin(self, plugin_name: str):
        """Unregister a plugin."""
        unregister_plugin_from_manager(self, plugin_name)
    
    def parse_with_plugins(self, text: str) -> Result[str, AppError]:
        """Parse text using appropriate plugins."""
        return execute_plugin_pipeline(self, text)
    
    def get_plugin_suggestions(self, text: str) -> List[str]:
        """Get suggestions from learning plugins."""
        return collect_plugin_suggestions(self, text)
    
    def learn_from_feedback(self, original: str, corrected: str, feedback: str):
        """Pass learning feedback to appropriate plugins."""
        distribute_learning_feedback(self, original, corrected, feedback)
    
    def _register_default_plugins(self):
        """Register default plugins."""
        self.register_plugin(BusinessDomainPlugin())
        self.register_plugin(SimpleLearningPlugin())
        self.register_plugin(ValidationPlugin())


# === PLUGIN MANAGER HELPER FUNCTIONS ===

def register_plugin_with_manager(manager: PluginManager, plugin: ParsingPlugin):
    """Register plugin with manager."""
    manager.plugins[plugin.metadata.name] = plugin
    update_plugin_order(manager)


def unregister_plugin_from_manager(manager: PluginManager, plugin_name: str):
    """Unregister plugin from manager."""
    if plugin_name in manager.plugins:
        del manager.plugins[plugin_name]
        update_plugin_order(manager)


def update_plugin_order(manager: PluginManager):
    """Update plugin execution order by priority."""
    manager.plugin_order = sorted(
        manager.plugins.keys(),
        key=lambda name: manager.plugins[name].metadata.priority,
        reverse=True
    )


def execute_plugin_pipeline(manager: PluginManager, text: str) -> Result[str, AppError]:
    """Execute plugin pipeline in priority order."""
    context = ParseContext(original_text=text, preprocessed_text=text)
    
    for plugin_name in manager.plugin_order:
        plugin = manager.plugins[plugin_name]
        
        if not plugin.enabled:
            continue
            
        if plugin.can_handle(text, context):
            result = plugin.process(text, context)
            
            if isinstance(result, Success):
                context.plugin_results[plugin_name] = result.value
                context.confidence_scores[plugin_name] = plugin.get_confidence(text, context)
                
                # Use first successful result
                return result
    
    # No plugin could handle the text
    from backend.unified.core.error_handling import create_parse_error, ErrorType
    error = create_parse_error(
        ErrorType.PATTERN_MISMATCH,
        "No plugin could parse the text",
        0,
        text
    )
    return Failure(error_code=error.error_type.value, message=error.message)


def collect_plugin_suggestions(manager: PluginManager, text: str) -> List[str]:
    """Collect suggestions from all learning plugins."""
    suggestions = []
    
    for plugin in manager.plugins.values():
        if isinstance(plugin, LearningPlugin) and plugin.enabled:
            plugin_suggestions = plugin.get_adaptation_suggestions(text)
            suggestions.extend(plugin_suggestions)
    
    return suggestions


def distribute_learning_feedback(manager: PluginManager, original: str, corrected: str, feedback: str):
    """Distribute learning feedback to appropriate plugins."""
    for plugin in manager.plugins.values():
        if isinstance(plugin, LearningPlugin) and plugin.enabled:
            plugin.learn_from_correction(original, corrected, feedback)


def create_plugin_manager() -> PluginManager:
    """Create plugin manager instance."""
    return PluginManager()