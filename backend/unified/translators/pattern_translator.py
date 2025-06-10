"""
Pattern-based translation engine following Intentional Disclosure Principle.

Implements simple pattern-based translation as a fallback mechanism.
Consolidates pattern-based logic with explicit type annotations and clear I/O boundaries.

Copyright: DarkLightX/Dana Edwards
"""

import re
import time
from typing import List, Tuple, Pattern, Dict, Any, Optional
from dataclasses import dataclass

# Import domain types
from ..core.domain_types import (
    SourceText, TargetText,
    TranslationStatus, EngineType, Result, Success, Failure
)
from .base import TranslationEngine, TranslationDirection, TranslationResult


@dataclass
class PatternRule:
    """Represents a single translation pattern rule."""
    pattern: Pattern[str]
    replacement: str
    description: str


@dataclass 
class PatternSet:
    """Collection of pattern rules for a specific direction."""
    direction: TranslationDirection
    rules: List[PatternRule]


class PatternTranslationEngine(TranslationEngine):
    """Pattern-based translation engine with explicit disclosure of operations."""
    
    def __init__(self) -> None:
        """Initialize pattern translation engine with predefined rule sets."""
        super().__init__(
            name="pattern_based",
            description="Simple pattern-based translation with regex rules"
        )
        
        # Initialize pattern sets following Rule 2: Orchestrator pattern
        self._pattern_sets = self._initialize_pattern_sets()
    
    def can_translate(self, text: SourceText, direction: TranslationDirection) -> bool:
        """Determine if engine can handle the requested translation."""
        # Rule 2: High-level orchestration
        return (
            self._validate_input_text(text) and
            self._is_direction_supported(direction)
        )
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """Return list of supported translation directions."""
        return [TranslationDirection.TO_TAU, TranslationDirection.TO_TCE]
    
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """Implementation of abstract translate method from base class."""
        # Since translate_text_with_patterns_async is async, we need to run it synchronously
        import asyncio
        
        async def _translate():
            return await self.translate_text_with_patterns_async(
                SourceText(text), direction, **kwargs
            )
        
        # Run async method in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a task
                task = asyncio.create_task(_translate())
                result = asyncio.run_until_complete(task)
            else:
                result = loop.run_until_complete(_translate())
        except RuntimeError:
            # No event loop, create one
            result = asyncio.run(_translate())
        
        if isinstance(result, Success):
            return result.value
        else:
            # Return error result
            return self._create_result(
                success=False,
                translated_text="",
                original_text=text,
                direction=direction,
                error_message=f"{result.error_code}: {result.message}",
                start_time=time.time()
            )
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """Check if this engine can handle the given translation."""
        return (
            bool(text and text.strip()) and 
            direction in self.get_supported_directions()
        )
    
    async def translate_text_with_patterns_async(
        self, 
        text: SourceText, 
        direction: TranslationDirection, 
        **kwargs: Dict[str, Any]
    ) -> Result[BaseTranslationResult]:
        """
        Translate text using pattern matching rules.
        Rule 1: Name explicitly indicates pattern-based operation and async nature.
        Rule 2: Orchestrator pattern for high-level flow.
        """
        start_time = time.time()
        
        # Validate preconditions
        validation_result = self._validate_translation_request(text, direction)
        if isinstance(validation_result, Failure):
            return validation_result
            
        # Select appropriate pattern set
        pattern_set = self._select_pattern_set_for_direction(direction)
        if not pattern_set:
            return Failure(
                error_code="UNSUPPORTED_DIRECTION",
                message=f"Direction {direction.value} not supported"
            )
            
        # Apply translation patterns
        translation_result = self._apply_pattern_rules_to_text(text, pattern_set)
        if isinstance(translation_result, Failure):
            return translation_result
            
        # Post-process and calculate metrics
        cleaned_text = self._clean_translated_text(translation_result.value, direction)
        confidence = self._calculate_translation_confidence(text, cleaned_text)
        
        # Create final result
        return Success(self._create_translation_result(
            original_text=text,
            translated_text=cleaned_text,
            direction=direction,
            confidence=confidence,
            start_time=start_time
        ))
    
    # --- Private Implementation Methods (Rule 2) ---
    
    def _initialize_pattern_sets(self) -> Dict[TranslationDirection, PatternSet]:
        """Initialize pattern rule sets for each translation direction."""
        return {
            TranslationDirection.TO_TAU: self._create_tce_to_tau_patterns(),
            TranslationDirection.TO_TCE: self._create_tau_to_tce_patterns()
        }
    
    def _create_tce_to_tau_patterns(self) -> PatternSet:
        """Create pattern rules for TCE to Tau translation."""
        return PatternSet(
            direction=TranslationDirection.TO_TAU,
            rules=[
                PatternRule(re.compile(r'\band\b'), '&', 'Logical AND operator'),
                PatternRule(re.compile(r'\bor\b'), '|', 'Logical OR operator'),
                PatternRule(re.compile(r'\bnot\b'), '!', 'Logical NOT operator'),
                PatternRule(re.compile(r'\bequals\b'), '=', 'Equality operator'),
                PatternRule(re.compile(r'\bplus\b'), '+', 'Addition operator'),
                PatternRule(re.compile(r'\bminus\b'), '-', 'Subtraction operator'),
                PatternRule(re.compile(r'\btimes\b'), '*', 'Multiplication operator'),
                PatternRule(re.compile(r'\bdivided by\b'), '/', 'Division operator'),
                PatternRule(re.compile(r'\bthe\b'), '', 'Remove articles'),
                PatternRule(re.compile(r'\bat time (\w+)'), r'[\1]', 'Temporal indexing'),
                PatternRule(re.compile(r'\s+'), ' ', 'Normalize whitespace')
            ]
        )
    
    def _create_tau_to_tce_patterns(self) -> PatternSet:
        """Create pattern rules for Tau to TCE translation."""
        return PatternSet(
            direction=TranslationDirection.TO_TCE,
            rules=[
                PatternRule(re.compile(r'&'), ' and ', 'Logical AND operator'),
                PatternRule(re.compile(r'\|'), ' or ', 'Logical OR operator'),
                PatternRule(re.compile(r'!'), ' not ', 'Logical NOT operator'),
                PatternRule(re.compile(r'='), ' equals ', 'Equality operator'),
                PatternRule(re.compile(r'\+'), ' plus ', 'Addition operator'),
                PatternRule(re.compile(r'-'), ' minus ', 'Subtraction operator'),
                PatternRule(re.compile(r'\*'), ' times ', 'Multiplication operator'),
                PatternRule(re.compile(r'/'), ' divided by ', 'Division operator'),
                PatternRule(re.compile(r'\[(\w+)\]'), r' at time \1', 'Temporal indexing'),
                PatternRule(re.compile(r'\s+'), ' ', 'Normalize whitespace')
            ]
        )
    
    def _validate_input_text(self, text: SourceText) -> bool:
        """Validate that input text meets requirements."""
        return bool(text and len(text.strip()) > 0 and len(text) < 10000)
    
    def _is_direction_supported(self, direction: TranslationDirection) -> bool:
        """Check if translation direction is supported."""
        return direction in self._pattern_sets
    
    def _validate_translation_request(
        self, 
        text: SourceText, 
        direction: TranslationDirection
    ) -> Result[None]:
        """Validate the complete translation request."""
        if not self._validate_input_text(text):
            return Failure("INVALID_INPUT", "Input text is invalid or too long")
            
        if not self._is_direction_supported(direction):
            return Failure("UNSUPPORTED_DIRECTION", f"Direction {direction.value} not supported")
            
        return Success(None)
    
    def _select_pattern_set_for_direction(
        self, 
        direction: TranslationDirection
    ) -> Optional[PatternSet]:
        """Select the appropriate pattern set for the given direction."""
        return self._pattern_sets.get(direction)
    
    def _apply_pattern_rules_to_text(
        self, 
        text: SourceText, 
        pattern_set: PatternSet
    ) -> Result[TargetText]:
        """Apply pattern rules to transform the text."""
        try:
            result = text
            
            # Apply each rule in sequence
            for rule in pattern_set.rules:
                result = rule.pattern.sub(rule.replacement, result)
                
            return Success(TargetText(result))
            
        except Exception as e:
            return Failure("PATTERN_APPLICATION_ERROR", str(e))
    
    def _clean_translated_text(
        self, 
        text: TargetText, 
        direction: TranslationDirection
    ) -> TargetText:
        """Clean and normalize the translated text."""
        # Remove extra spaces
        cleaned = ' '.join(text.split())
        
        # Direction-specific cleaning
        if direction == TranslationDirection.TO_TAU:
            # Remove leading/trailing spaces around operators
            cleaned = re.sub(r'\s*([&|!=+\-*/])\s*', r'\1', cleaned)
            
        return TargetText(cleaned.strip())
    
    def _calculate_translation_confidence(
        self, 
        original: SourceText, 
        translated: TargetText
    ) -> float:
        """Calculate confidence score based on text transformation."""
        if not original or not translated:
            return 0.0
            
        # Simple heuristic: more changes = higher confidence it was translated
        similarity = self._calculate_text_similarity(original, translated)
        return max(0.0, min(1.0, 1.0 - similarity))
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0.0 to 1.0)."""
        if text1 == text2:
            return 1.0
            
        # Simple character-based similarity
        longer = max(len(text1), len(text2))
        if longer == 0:
            return 1.0
            
        distance = self._levenshtein_distance(text1, text2)
        return 1.0 - (distance / longer)
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
            
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
    
    def _create_translation_result(
        self,
        original_text: SourceText,
        translated_text: TargetText,
        direction: TranslationDirection,
        confidence: float,
        start_time: float
    ) -> BaseTranslationResult:
        """Create a complete translation result object."""
        return BaseTranslationResult(
            success=True,
            original_text=original_text,
            translated_text=translated_text,
            direction=direction,
            confidence=confidence,
            translation_method=self.name,
            processing_time=time.time() - start_time,
            metadata={
                "pattern_count": len(self._pattern_sets[direction].rules),
                "text_length": len(original_text),
                "result_length": len(translated_text)
            }
        )