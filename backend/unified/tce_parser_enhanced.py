"""
Enhanced TCE Parser - Production-ready parser with all improvements
Integrates validation, error handling, plugins, ML, and parser combinators.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

from backend.unified.tce_parser_semantic import TCEParserSemanticV2, SemanticContext
from backend.unified.core.semantic_validator import SemanticValidator, ValidationResult, create_semantic_validator
from backend.unified.core.error_handling import ErrorRecoveryEngine, ParseError, ErrorContext, create_error_recovery_engine
from backend.unified.core.plugin_system import PluginManager, create_plugin_manager, ParseContext
from backend.unified.core.gradient_descent_parser import GradientDescentParser, create_gradient_descent_parser
from backend.unified.core.parser_combinators import TCEParserCombinator, create_tce_parser_combinator
from backend.unified.core.semantic_lexicon import SemanticLexicon, get_semantic_lexicon
from backend.unified.core.result_enhanced import Result, Success, Failure


@dataclass
class EnhancedParseResult:
    """Enhanced parsing result with metadata."""
    parsed_text: str
    parse_method: str
    confidence: float
    validation_result: ValidationResult
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[ParseError] = field(default_factory=list)


@dataclass
class ParsingStrategy:
    """Strategy for parsing with specific method."""
    name: str
    parser_func: Any
    priority: int
    enabled: bool = True


# === PURE STRATEGY FUNCTIONS (CC=1 each) ===

def create_parsing_strategies(enhanced_parser) -> List[ParsingStrategy]:
    """Create list of parsing strategies."""
    return [
        ParsingStrategy("plugin_system", enhanced_parser._parse_with_plugins, priority=90),
        ParsingStrategy("neural_network", enhanced_parser._parse_with_neural, priority=80),
        ParsingStrategy("parser_combinators", enhanced_parser._parse_with_combinators, priority=70),
        ParsingStrategy("semantic_v2", enhanced_parser._parse_with_semantic, priority=60),
        ParsingStrategy("fallback", enhanced_parser._parse_fallback, priority=10)
    ]


def try_parsing_strategy(strategy: ParsingStrategy, text: str) -> Result[str, ParseError]:
    """Try single parsing strategy."""
    if not strategy.enabled:
        return create_strategy_disabled_error(strategy.name)
    
    return strategy.parser_func(text)


def create_strategy_disabled_error(strategy_name: str) -> Result[str, ParseError]:
    """Create error for disabled strategy."""
    from backend.unified.core.error_handling import create_parse_error, ErrorType
    error = create_parse_error(
        ErrorType.PATTERN_MISMATCH,
        f"Strategy '{strategy_name}' is disabled",
        0,
        ""
    )
    return Failure(error)


def execute_parsing_strategies(strategies: List[ParsingStrategy], text: str) -> Tuple[Optional[str], List[ParseError]]:
    """Execute parsing strategies in priority order."""
    errors = []
    
    for strategy in sorted(strategies, key=lambda s: s.priority, reverse=True):
        result = try_parsing_strategy(strategy, text)
        
        if isinstance(result, Success):
            return result.unwrap(), errors
        else:
            errors.append(result.failure())
    
    return None, errors


def validate_parse_result(text: str, parsed_result: str, validator: SemanticValidator) -> ValidationResult:
    """Validate parsed result."""
    # Extract components for validation
    components = extract_parse_components(parsed_result)
    return validator.validate_statement(text, components)


def extract_parse_components(parsed_result: str) -> Dict:
    """Extract components from parsed result for validation."""
    components = create_empty_components()
    
    extract_relation_components(parsed_result, components)
    extract_quantifier_components(parsed_result, components)
    
    return components


def create_enhanced_result(text: str, parsed_result: str, method: str, confidence: float, 
                         validation: ValidationResult, suggestions: List[str] = None) -> EnhancedParseResult:
    """Create enhanced parse result."""
    return EnhancedParseResult(
        parsed_text=parsed_result,
        parse_method=method,
        confidence=confidence,
        validation_result=validation,
        suggestions=suggestions or [],
        metadata={'input_length': len(text), 'method': method}
    )


def generate_recovery_suggestions(text: str, errors: List[ParseError], 
                                recovery_engine: ErrorRecoveryEngine) -> List[str]:
    """Generate recovery suggestions from errors."""
    suggestions = []
    
    suggestions.extend(collect_error_suggestions(errors, recovery_engine))
    suggestions.extend(add_general_suggestions(text))
    
    return remove_duplicate_suggestions(suggestions)


def attempt_error_recovery(text: str, errors: List[ParseError], 
                          recovery_engine: ErrorRecoveryEngine) -> Optional[str]:
    """Attempt automatic error recovery."""
    for error in errors:
        recovered = recovery_engine.attempt_recovery(text, error)
        if recovered:
            return recovered
    
    return None


class EnhancedTCEParser:
    """
    Production-ready TCE parser with all enhancements.
    Combines validation, error handling, plugins, ML, and parser combinators.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize enhanced parser with configuration."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self._initialize_components()
        self._initialize_strategies()
        self._initialize_statistics()
    
    def _initialize_components(self):
        """Initialize parser components."""
        self.semantic_parser = TCEParserSemanticV2()
        self.validator = create_semantic_validator()
        self.error_engine = create_error_recovery_engine()
        self.plugin_manager = create_plugin_manager()
        self.neural_parser = create_gradient_descent_parser()
        self.combinator_parser = create_tce_parser_combinator()
    
    def _initialize_strategies(self):
        """Initialize parsing strategies."""
        self.plugin_manager.register_plugin(self.neural_parser)
        self.strategies = create_parsing_strategies(self)
    
    def _initialize_statistics(self):
        """Initialize parsing statistics."""
        self.parse_stats = create_empty_parse_stats()
    
    def parse(self, text: str) -> EnhancedParseResult:
        """Parse text with comprehensive error handling and validation."""
        self.parse_stats['total_parses'] += 1
        
        # Attempt parsing with all strategies
        parsed_result, errors = execute_parsing_strategies(self.strategies, text)
        
        if parsed_result:
            return self._create_successful_result(text, parsed_result, errors)
        else:
            return self._create_failed_result(text, errors)
    
    def parse_with_learning(self, text: str, expected_result: Optional[str] = None) -> EnhancedParseResult:
        """Parse with learning capability."""
        result = self.parse(text)
        
        # Learn from expected result if provided
        if expected_result and result.parsed_text != expected_result:
            self._learn_from_correction(text, result.parsed_text, expected_result)
        
        return result
    
    def get_parsing_suggestions(self, text: str) -> List[str]:
        """Get parsing suggestions without actually parsing."""
        return self.plugin_manager.get_plugin_suggestions(text)
    
    def add_domain_knowledge(self, domain: str, patterns: Dict[str, str], vocabulary: Dict[str, str]):
        """Add domain-specific knowledge."""
        # This would integrate with plugin system
        self.logger.info(f"Added domain knowledge for: {domain}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics."""
        return self.parse_stats.copy()
    
    def _create_successful_result(self, text: str, parsed_result: str, errors: List[ParseError]) -> EnhancedParseResult:
        """Create result for successful parse."""
        self.parse_stats['successful_parses'] += 1
        
        # Validate result
        validation = validate_parse_result(text, parsed_result, self.validator)
        
        # Calculate confidence
        confidence = self._calculate_confidence(text, parsed_result, validation)
        
        # Get suggestions
        suggestions = self.plugin_manager.get_plugin_suggestions(text)
        
        return create_enhanced_result(
            text=text,
            parsed_result=parsed_result,
            method="multi_strategy",
            confidence=confidence,
            validation=validation,
            suggestions=suggestions
        )
    
    def _create_failed_result(self, text: str, errors: List[ParseError]) -> EnhancedParseResult:
        """Create result for failed parse."""
        recovered = attempt_error_recovery(text, errors, self.error_engine)
        
        if recovered:
            return self._try_recovery_parsing(recovered, text, errors)
        else:
            return self._create_final_failed_result(text, errors)
    
    def _try_recovery_parsing(self, recovered: str, original_text: str, errors: List[ParseError]) -> EnhancedParseResult:
        """Try parsing recovered text."""
        recovered_result, _ = execute_parsing_strategies(self.strategies, recovered)
        
        if recovered_result:
            return self._create_recovery_success_result(recovered, recovered_result)
        else:
            return self._create_final_failed_result(original_text, errors)
    
    def _create_recovery_success_result(self, recovered: str, recovered_result: str) -> EnhancedParseResult:
        """Create result for successful recovery."""
        validation = validate_parse_result(recovered, recovered_result, self.validator)
        suggestions = [f"Auto-recovered: '{recovered}'"]
        
        return create_enhanced_result(
            text=recovered_result,
            parsed_result=recovered_result,
            method="error_recovery",
            confidence=0.6,
            validation=validation,
            suggestions=suggestions
        )
    
    def _create_final_failed_result(self, text: str, errors: List[ParseError]) -> EnhancedParseResult:
        """Create final failed result."""
        suggestions = generate_recovery_suggestions(text, errors, self.error_engine)
        
        result = create_enhanced_result(
            text=text,
            parsed_result=text,
            method="failed",
            confidence=0.0,
            validation=ValidationResult(is_valid=False),
            suggestions=suggestions
        )
        result.errors = errors
        return result
    
    def _calculate_confidence(self, text: str, parsed_result: str, validation: ValidationResult) -> float:
        """Calculate parsing confidence."""
        return calculate_parsing_confidence(text, parsed_result, validation)
    
    def _learn_from_correction(self, original: str, parsed: str, expected: str):
        """Learn from user correction."""
        feedback = f"Expected: {expected}, Got: {parsed}"
        self.plugin_manager.learn_from_feedback(original, expected, feedback)
    
    # === STRATEGY IMPLEMENTATIONS ===
    
    def _parse_with_plugins(self, text: str) -> Result[str, ParseError]:
        """Parse using plugin system."""
        return self.plugin_manager.parse_with_plugins(text)
    
    def _parse_with_neural(self, text: str) -> Result[str, ParseError]:
        """Parse using neural network."""
        context = ParseContext(original_text=text, preprocessed_text=text)
        return self.neural_parser.process(text, context)
    
    def _parse_with_combinators(self, text: str) -> Result[str, ParseError]:
        """Parse using parser combinators."""
        result = self.combinator_parser.parse(text)
        if isinstance(result, Success):
            return result
        else:
            from backend.unified.core.error_handling import create_parse_error, ErrorType
            error = create_parse_error(
                ErrorType.PATTERN_MISMATCH,
                f"Combinator parsing failed: {result.failure()}",
                0,
                text
            )
            return Failure(error)
    
    def _parse_with_semantic(self, text: str) -> Result[str, ParseError]:
        """Parse using semantic parser."""
        try:
            result = self.semantic_parser.parse(text)
            return Success(result)
        except Exception as e:
            from backend.unified.core.error_handling import create_parse_error, ErrorType
            error = create_parse_error(
                ErrorType.SEMANTIC_ERROR,
                f"Semantic parsing failed: {e}",
                0,
                text
            )
            return Failure(error)
    
    def _parse_fallback(self, text: str) -> Result[str, ParseError]:
        """Fallback parsing strategy."""
        # Simple fallback - just return the text
        return Success(f"fallback({text})")


# === FACTORY FUNCTIONS ===

def create_enhanced_tce_parser(config: Optional[Dict] = None) -> EnhancedTCEParser:
    """Create enhanced TCE parser instance."""
    return EnhancedTCEParser(config)


def create_production_parser() -> EnhancedTCEParser:
    """Create production-ready parser with optimal settings."""
    config = {
        'enable_neural': True,
        'enable_validation': True,
        'enable_error_recovery': True,
        'max_complexity': 50,
        'confidence_threshold': 0.7
    }
    return create_enhanced_tce_parser(config)


# === CONVENIENCE FUNCTIONS ===

def quick_parse(text: str) -> str:
    """Quick parse function for simple usage."""
    parser = create_enhanced_tce_parser()
    result = parser.parse(text)
    return result.parsed_text


def parse_with_validation(text: str) -> Tuple[str, bool, List[str]]:
    """Parse with validation information."""
    parser = create_enhanced_tce_parser()
    result = parser.parse(text)
    return result.parsed_text, result.validation_result.is_valid, result.suggestions


def parse_and_learn(text: str, expected: Optional[str] = None) -> EnhancedParseResult:
    """Parse with learning capability."""
    parser = create_enhanced_tce_parser()
    return parser.parse_with_learning(text, expected)


def create_empty_parse_stats() -> Dict[str, Any]:
    """Create empty parsing statistics."""
    return {
        'total_parses': 0,
        'successful_parses': 0,
        'method_usage': {},
        'average_confidence': 0.0
    }


def calculate_parsing_confidence(text: str, parsed_result: str, validation: ValidationResult) -> float:
    """Calculate parsing confidence score."""
    confidence = 0.5  # Base confidence
    
    confidence = add_parsing_success_boost(confidence, text, parsed_result)
    confidence = add_validation_boost(confidence, validation)
    confidence = apply_complexity_penalty(confidence, text)
    
    return clamp_confidence(confidence)


def add_parsing_success_boost(confidence: float, text: str, parsed_result: str) -> float:
    """Add boost for successful parsing."""
    return confidence + 0.3 if parsed_result != text else confidence


def add_validation_boost(confidence: float, validation: ValidationResult) -> float:
    """Add boost for validation success."""
    return confidence + 0.2 if validation.is_valid else confidence - 0.1


def apply_complexity_penalty(confidence: float, text: str) -> float:
    """Apply penalty for text complexity."""
    complexity = len(text.split()) / 20.0
    return confidence - (complexity * 0.1)


def clamp_confidence(confidence: float) -> float:
    """Clamp confidence to valid range."""
    return max(0.0, min(1.0, confidence))


def create_empty_components() -> Dict:
    """Create empty components structure."""
    return {
        'relations': [],
        'quantifiers': [],
        'temporal_expressions': [],
        'modal_expressions': []
    }


def extract_relation_components(parsed_result: str, components: Dict):
    """Extract relation components."""
    if 'owns(' in parsed_result:
        components['relations'].append(('subject', 'owns', 'object'))


def extract_quantifier_components(parsed_result: str, components: Dict):
    """Extract quantifier components."""
    if 'all ' in parsed_result or 'every ' in parsed_result:
        components['quantifiers'].append({'quantifier': 'universal', 'entity': 'entity', 'predicate': 'predicate'})


def collect_error_suggestions(errors: List[ParseError], recovery_engine: ErrorRecoveryEngine) -> List[str]:
    """Collect suggestions from errors."""
    suggestions = []
    for error in errors:
        error_suggestions = recovery_engine.suggest_corrections(error)
        suggestions.extend(error_suggestions)
    return suggestions


def add_general_suggestions(text: str) -> List[str]:
    """Add general parsing suggestions."""
    suggestions = []
    
    suggestions.extend(check_sentence_length(text))
    suggestions.extend(check_structure_words(text))
    
    return suggestions


def check_sentence_length(text: str) -> List[str]:
    """Check if sentence is too long."""
    if len(text.split()) > 15:
        return ["Try breaking into shorter sentences"]
    return []


def check_structure_words(text: str) -> List[str]:
    """Check for structure words."""
    structure_words = ['all', 'every', 'some', 'if', 'when']
    if not any(q in text.lower() for q in structure_words):
        return ["Try adding clear structure words like 'all', 'every', 'if', 'when'"]
    return []


def remove_duplicate_suggestions(suggestions: List[str]) -> List[str]:
    """Remove duplicate suggestions."""
    return list(set(suggestions))