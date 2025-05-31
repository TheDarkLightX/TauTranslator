#!/usr/bin/env python3
"""
Refactored LLM Translator with Reduced Complexity
================================================

Following SOLID principles, reduced cyclomatic complexity,
and optimized algorithms for production use.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol, Any
from enum import Enum
import re

logger = logging.getLogger(__name__)


# Strategy Pattern for Framework Handlers
class TranslationStrategy(Protocol):
    """Protocol for translation strategies."""
    async def translate(self, text: str) -> str:
        """Translate text to Tau specification."""
        ...


@dataclass
class ValidationResult:
    """Result of Tau syntax validation."""
    valid: bool
    confidence: float = 0.0
    errors: List[str] = field(default_factory=list)
    patterns_found: List[str] = field(default_factory=list)


@dataclass
class TranslationRequest:
    """Encapsulates a translation request."""
    text: str
    max_iterations: int = 3
    interactive: bool = False
    language: str = "en"


@dataclass 
class TranslationResponse:
    """Response from translation."""
    tau_code: str
    confidence: float
    iterations_used: int
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)


# Simplified pattern validator using composition
class TauPatternValidator:
    """Validates Tau syntax patterns efficiently."""
    
    # Compiled patterns for better performance
    PATTERNS = {
        'stream': re.compile(r'sbf\s+\w+\s*=\s*(ifile|ofile|console)'),
        'rule': re.compile(r'r\s+\w+\[.*?\]\s*='),
        'function': re.compile(r'\w+\s*\([^)]*\)\s*:='),
        'temporal': re.compile(r'(always|sometimes|never)\s+'),
        'constraint': re.compile(r'\w+\[t\]\s*(>|<|>=|<=|=)\s*\d+')
    }
    
    def validate(self, tau_code: str) -> ValidationResult:
        """Validate Tau code syntax with O(n) complexity."""
        if not tau_code.strip():
            return ValidationResult(valid=False, errors=["Empty specification"])
        
        result = ValidationResult(valid=True)
        lines = tau_code.strip().split('\n')
        
        # Single pass validation
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check parentheses balance
            if not self._check_balanced(line, '(', ')'):
                result.errors.append(f"Line {i}: Unmatched parentheses")
                result.valid = False
            
            if not self._check_balanced(line, '[', ']'):
                result.errors.append(f"Line {i}: Unmatched brackets")
                result.valid = False
        
        # Pattern detection
        for name, pattern in self.PATTERNS.items():
            if pattern.search(tau_code):
                result.patterns_found.append(name)
        
        # Calculate confidence
        result.confidence = len(result.patterns_found) / len(self.PATTERNS) if self.PATTERNS else 0
        
        return result
    
    @staticmethod
    def _check_balanced(text: str, open_char: str, close_char: str) -> bool:
        """Check if brackets are balanced - O(n) algorithm."""
        count = 0
        for char in text:
            if char == open_char:
                count += 1
            elif char == close_char:
                count -= 1
                if count < 0:
                    return False
        return count == 0


# Base translation strategy
class BaseTranslationStrategy(TranslationStrategy):
    """Base class for translation strategies."""
    
    def __init__(self, validator: TauPatternValidator):
        self.validator = validator
    
    @abstractmethod
    async def translate(self, text: str) -> str:
        """Must be implemented by subclasses."""
        pass


# Pattern-based translation (always available)
class PatternTranslationStrategy(BaseTranslationStrategy):
    """Efficient pattern-based translation."""
    
    # Precompiled translation patterns
    TRANSLATIONS = [
        (re.compile(r'\balways\s+(.+)', re.I), 'always {0}'),
        (re.compile(r'\bsometimes\s+(.+)', re.I), 'sometimes {0}'),
        (re.compile(r'\b(\w+)\s+must\s+(?:be\s+)?between\s+(\d+)\s+and\s+(\d+)', re.I), 
         'always {0}[t] >= {1} & {0}[t] <= {2}'),
        (re.compile(r'\bmonitor\s+(\w+)(?:\s+sensor)?', re.I), 'r {0}_status[t] = {0}[t]'),
        (re.compile(r'\bread\s+from\s+["\']([^"\']+)["\']', re.I), 'sbf input = ifile("{0}")'),
        (re.compile(r'\bwrite\s+to\s+["\']([^"\']+)["\']', re.I), 'sbf output = ofile("{0}")'),
    ]
    
    async def translate(self, text: str) -> str:
        """Translate using efficient pattern matching."""
        result_lines = []
        
        # Process each sentence
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            translated = False
            for pattern, template in self.TRANSLATIONS:
                match = pattern.search(sentence)
                if match:
                    tau_line = template.format(*match.groups())
                    result_lines.append(tau_line)
                    translated = True
                    break
            
            if not translated and sentence:
                # Default handling for unmatched patterns
                if 'must' in sentence.lower() or 'always' in sentence.lower():
                    result_lines.append(f"# TODO: {sentence}")
        
        return '\n'.join(result_lines)


# LLM-based strategies can be added as plugins
class LMQLTranslationStrategy(BaseTranslationStrategy):
    """LMQL-based translation strategy."""
    
    def __init__(self, validator: TauPatternValidator):
        super().__init__(validator)
        self._check_availability()
    
    def _check_availability(self):
        """Check if LMQL is available."""
        try:
            import lmql
            self.lmql = lmql
            self.available = True
        except ImportError:
            self.available = False
    
    async def translate(self, text: str) -> str:
        """Translate using LMQL if available."""
        if not self.available:
            # Fallback to pattern strategy
            return await PatternTranslationStrategy(self.validator).translate(text)
        
        try:
            query = '''
            argmax
                """Requirements: {text}
                
                Tau Specification:
                [TAU]"""
            from "openai/gpt-3.5-turbo"
            where len(TAU) < 1000
            '''
            result = await self.lmql.run(query, text=text)
            return result.variables['TAU']
        except Exception as e:
            logger.error(f"LMQL translation failed: {e}")
            return await PatternTranslationStrategy(self.validator).translate(text)


# Feedback generator with single responsibility
class FeedbackGenerator:
    """Generates feedback for translation improvement."""
    
    @staticmethod
    def generate(validation: ValidationResult, tau_code: str) -> str:
        """Generate concise feedback."""
        feedback_parts = []
        
        if validation.errors:
            feedback_parts.append("Syntax errors: " + "; ".join(validation.errors))
        
        missing_patterns = {'stream', 'temporal', 'rule'} - set(validation.patterns_found)
        if missing_patterns:
            suggestions = {
                'stream': "Add stream declarations (sbf name = ifile/ofile)",
                'temporal': "Add temporal properties (always/sometimes)",
                'rule': "Add rules (r name[t] = expression)"
            }
            feedback_parts.extend(suggestions.get(p, "") for p in missing_patterns if p in suggestions)
        
        return " | ".join(filter(None, feedback_parts)) or "Looks good"


# Main translator with dependency injection
class RefactoredLLMTranslator:
    """Main translator with reduced complexity and better separation of concerns."""
    
    def __init__(self, 
                 strategy: Optional[TranslationStrategy] = None,
                 validator: Optional[TauPatternValidator] = None,
                 feedback_generator: Optional[FeedbackGenerator] = None):
        """Initialize with injected dependencies."""
        self.validator = validator or TauPatternValidator()
        self.feedback_generator = feedback_generator or FeedbackGenerator()
        self.strategy = strategy or self._select_default_strategy()
    
    def _select_default_strategy(self) -> TranslationStrategy:
        """Select the best available strategy."""
        # Try strategies in order of preference
        strategies = [
            LMQLTranslationStrategy,
            PatternTranslationStrategy
        ]
        
        for strategy_class in strategies:
            try:
                strategy = strategy_class(self.validator)
                if hasattr(strategy, 'available') and not strategy.available:
                    continue
                return strategy
            except Exception:
                continue
        
        # Fallback
        return PatternTranslationStrategy(self.validator)
    
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Main translation method with clean separation."""
        response = TranslationResponse(
            tau_code="",
            confidence=0.0,
            iterations_used=0
        )
        
        # Initial translation
        response.tau_code = await self.strategy.translate(request.text)
        response.iterations_used = 1
        
        # Iterative refinement
        for iteration in range(1, request.max_iterations):
            validation = self.validator.validate(response.tau_code)
            response.confidence = validation.confidence
            
            if validation.valid and validation.confidence > 0.8:
                break
            
            # Get feedback
            feedback = await self._get_feedback(
                response.tau_code, 
                validation, 
                request.interactive
            )
            
            response.feedback_history.append({
                'iteration': iteration,
                'feedback': feedback,
                'validation': validation
            })
            
            # Refine
            response.tau_code = await self._refine(
                request.text,
                response.tau_code,
                feedback
            )
            response.iterations_used = iteration + 1
        
        return response
    
    async def _get_feedback(self, 
                           tau_code: str, 
                           validation: ValidationResult,
                           interactive: bool) -> str:
        """Get feedback (user or automatic)."""
        if interactive:
            return await self._get_user_feedback(tau_code, validation)
        return self.feedback_generator.generate(validation, tau_code)
    
    async def _get_user_feedback(self, tau_code: str, validation: ValidationResult) -> str:
        """Get interactive user feedback."""
        print(f"\nCurrent Translation:\n{tau_code}")
        print(f"\nValid: {validation.valid}, Confidence: {validation.confidence:.2f}")
        return input("Feedback (Enter to accept): ").strip() or "Accepted"
    
    async def _refine(self, original: str, current: str, feedback: str) -> str:
        """Refine translation based on feedback."""
        # Simple refinement - add missing components
        refined = current
        
        if "stream declarations" in feedback and "sbf" not in refined:
            refined = f"sbf input = ifile(\"data.txt\")\n\n{refined}"
        
        if "temporal properties" in feedback and "always" not in refined:
            refined = f"{refined}\n\nalways system_valid[t]"
        
        return refined


# Factory for creating translators
class TranslatorFactory:
    """Factory for creating configured translators."""
    
    @staticmethod
    def create(framework: str = "auto") -> RefactoredLLMTranslator:
        """Create a translator with specified framework."""
        validator = TauPatternValidator()
        
        strategies = {
            'pattern': PatternTranslationStrategy,
            'lmql': LMQLTranslationStrategy,
        }
        
        strategy_class = strategies.get(framework, PatternTranslationStrategy)
        strategy = strategy_class(validator)
        
        return RefactoredLLMTranslator(
            strategy=strategy,
            validator=validator,
            feedback_generator=FeedbackGenerator()
        )


# Example usage with clean API
async def main():
    """Example usage of refactored translator."""
    # Create translator
    translator = TranslatorFactory.create("auto")
    
    # Create request
    request = TranslationRequest(
        text="""
        Create a temperature monitoring system.
        Temperature must always stay between 20 and 80 degrees.
        Read sensor data from sensors.txt.
        Log warnings when temperature exceeds 70 degrees.
        """,
        max_iterations=3,
        interactive=False
    )
    
    # Translate
    response = await translator.translate(request)
    
    # Display results
    print("Tau Specification:")
    print("=" * 60)
    print(response.tau_code)
    print("=" * 60)
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Iterations: {response.iterations_used}")


if __name__ == "__main__":
    asyncio.run(main())