"""
Pattern-based translation engine - Refactored for minimal complexity.
Following clean code principles with enhanced Result types and guard clauses.
"""

import re
import time
from typing import List, Pattern, Dict, Any, Optional
from dataclasses import dataclass
from backend.unified.core.domain_types import (
    SourceText, TargetText, TranslationStatus, EngineType, AppError,
    Result, Success, Failure
)
from backend.unified.core.functional_utils import (
    AsyncSyncBridge, ValidationPipeline, Validators, guard, guard_not_none
)
from .base import TranslationEngine, TranslationDirection, TranslationResult


# Constants
class PatternTranslatorConstants:
    MAX_TEXT_LENGTH = 10_000
    MIN_TEXT_LENGTH = 1
    ENGINE_NAME = "pattern_based"
    ENGINE_DESCRIPTION = "Simple pattern-based translation with regex rules"


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


class TextValidator:
    """Validates text for translation."""
    
    @staticmethod
    def validate(text: SourceText) -> Result[SourceText, AppError]:
        """
        Note: This is a pure function (no side effects).
        Validate text meets all requirements."""
        return (ValidationPipeline()
                .add(lambda t: guard_not_none(t, "NULL_TEXT", "Text cannot be null"))
                .add(lambda t: Validators.not_empty(t, "text"))
                .add(lambda t: Validators.length_between(
                    PatternTranslatorConstants.MIN_TEXT_LENGTH,
                    PatternTranslatorConstants.MAX_TEXT_LENGTH,
                    "text"
                )(t))
                .validate(text))


class PatternRepository:
    """Manages pattern sets for different translation directions."""
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
    
    def get_pattern_set(self, direction: TranslationDirection) -> Result[PatternSet, AppError]:
        """
        Note: This is a pure function (no side effects).
        Get pattern set for a direction."""
        pattern_set = self._patterns.get(direction)
        if pattern_set is None:
            return Failure(AppError(
                code="UNSUPPORTED_DIRECTION",
                message=f"Direction {direction.value} not supported"
            ))
        return Success(pattern_set)
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """
        Note: This is a pure function (no side effects).
        Get list of supported directions."""
        return list(self._patterns.keys())
    
    def _initialize_patterns(self) -> Dict[TranslationDirection, PatternSet]:
        """
        Note: This is a pure function (no side effects).
        Initialize all pattern sets."""
        return {
            TranslationDirection.TO_TAU: self._create_tce_to_tau_patterns(),
            TranslationDirection.TO_TCE: self._create_tau_to_tce_patterns()
        }
    
    def _create_tce_to_tau_patterns(self) -> PatternSet:
        """
        Note: This is a pure function (no side effects).
        Create TCE to Tau patterns."""
        return PatternSet(
            direction=TranslationDirection.TO_TAU,
            rules=self._get_tce_to_tau_rules()
        )
    
    def _get_tce_to_tau_rules(self) -> List[PatternRule]:
        """
        Note: This is a pure function (no side effects).
        Get TCE to Tau pattern rules."""
        return [
            PatternRule(re.compile(r'\band\b'), '&', 'Logical AND'),
            PatternRule(re.compile(r'\bor\b'), '|', 'Logical OR'),
            PatternRule(re.compile(r'\bnot\b'), '!', 'Logical NOT'),
            PatternRule(re.compile(r'\bequals\b'), '=', 'Equality'),
            PatternRule(re.compile(r'\bplus\b'), '+', 'Addition'),
            PatternRule(re.compile(r'\bminus\b'), '-', 'Subtraction'),
            PatternRule(re.compile(r'\btimes\b'), '*', 'Multiplication'),
            PatternRule(re.compile(r'\bdivided by\b'), '/', 'Division'),
            PatternRule(re.compile(r'\bthe\b'), '', 'Remove articles'),
            PatternRule(re.compile(r'\bat time (\w+)'), r'[\1]', 'Temporal'),
            PatternRule(re.compile(r'\s+'), ' ', 'Normalize spaces')
        ]
    
    def _create_tau_to_tce_patterns(self) -> PatternSet:
        """
        Note: This is a pure function (no side effects).
        Create Tau to TCE patterns."""
        return PatternSet(
            direction=TranslationDirection.TO_TCE,
            rules=self._get_tau_to_tce_rules()
        )
    
    def _get_tau_to_tce_rules(self) -> List[PatternRule]:
        """
        Note: This is a pure function (no side effects).
        Get Tau to TCE pattern rules."""
        return [
            PatternRule(re.compile(r'&'), ' and ', 'Logical AND'),
            PatternRule(re.compile(r'\|'), ' or ', 'Logical OR'),
            PatternRule(re.compile(r'!'), ' not ', 'Logical NOT'),
            PatternRule(re.compile(r'='), ' equals ', 'Equality'),
            PatternRule(re.compile(r'\+'), ' plus ', 'Addition'),
            PatternRule(re.compile(r'-'), ' minus ', 'Subtraction'),
            PatternRule(re.compile(r'\*'), ' times ', 'Multiplication'),
            PatternRule(re.compile(r'/'), ' divided by ', 'Division'),
            PatternRule(re.compile(r'\[(\w+)\]'), r' at time \1', 'Temporal'),
            PatternRule(re.compile(r'\s+'), ' ', 'Normalize spaces')
        ]


class PatternApplicator:
    """Applies pattern rules to text."""
    
    @staticmethod
    def apply_patterns(text: str, pattern_set: PatternSet) -> Result[str, AppError]:
        """
        Note: This is a pure function (no side effects).
        Apply all patterns in sequence."""
        try:
            for rule in pattern_set.rules:
                text = rule.pattern.sub(rule.replacement, text)
            return Success(text)
        except Exception as e:
            return Failure(AppError(
                code="PATTERN_APPLICATION_FAILED",
                message=f"Failed to apply patterns: {e}"
            ))


class TextCleaner:
    """Cleans translated text based on direction."""
    
    @staticmethod
    def clean(text: str, direction: TranslationDirection) -> str:
        """
        Note: This is a pure function (no side effects).
        Clean and normalize translated text."""
        # Remove extra spaces
        cleaned = ' '.join(text.split())
        
        # Direction-specific cleaning
        if direction == TranslationDirection.TO_TAU:
            # Remove spaces around operators
            cleaned = re.sub(r'\s*([&|!=+\-*/])\s*', r'\1', cleaned)
        
        return cleaned.strip()


class ConfidenceCalculator:
    """Calculates translation confidence scores."""
    
    @staticmethod
    def calculate(original: str, translated: str) -> float:
        """
        Note: This is a pure function (no side effects).
        Calculate confidence based on text changes."""
        if not original or not translated:
            return 0.0
        
        if original == translated:
            return 0.1  # Low confidence if no changes
        
        # Simple heuristic: more changes = higher confidence
        similarity = ConfidenceCalculator._similarity(original, translated)
        return max(0.0, min(1.0, 1.0 - similarity))
    
    @staticmethod
    def _similarity(text1: str, text2: str) -> float:
        """
        Note: This is a pure function (no side effects).
        Calculate simple similarity ratio."""
        if text1 == text2:
            return 1.0
        
        # Simple character-based similarity
        longer = max(len(text1), len(text2))
        if longer == 0:
            return 1.0
        
        # Simplified - just check length difference
        distance = abs(len(text1) - len(text2))
        return 1.0 - (distance / longer)


class PatternTranslationEngine(TranslationEngine):
    """Pattern-based translation engine with minimal complexity."""
    
    def __init__(self) -> None:
        """
        Note: This is a pure function (no side effects).
        Initialize engine."""
        super().__init__(
            name=PatternTranslatorConstants.ENGINE_NAME,
            description=PatternTranslatorConstants.ENGINE_DESCRIPTION
        )
        self._repository = PatternRepository()
        self._validator = TextValidator()
        self._applicator = PatternApplicator()
        self._cleaner = TextCleaner()
        self._confidence = ConfidenceCalculator()
    
    def can_translate(self, text: str, direction: TranslationDirection) -> bool:
        """
        Note: This is a pure function (no side effects).
        Check if engine can handle translation."""
        # Simple checks without complex conditions
        if not text:
            return False
        if direction not in self.get_supported_directions():
            return False
        return True
    
    def get_supported_directions(self) -> List[TranslationDirection]:
        """
        Note: This is a pure function (no side effects).
        Get supported translation directions."""
        return self._repository.get_supported_directions()
    
    def translate(self, text: str, direction: TranslationDirection, **kwargs) -> TranslationResult:
        """
        Note: This is a pure function (no side effects).
        Translate text synchronously."""
        async def _translate():
            return await self.translate_async(
                SourceText(text), direction, **kwargs
            )
        
        result = AsyncSyncBridge.run(_translate())
        
        return result.fold(
            on_success=lambda res: res,
            on_failure=lambda err: self._create_error_result(text, direction, err)
        )
    
    async def translate_async(
        self,
        text: SourceText,
        direction: TranslationDirection,
        **kwargs: Dict[str, Any]
    ) -> Result[TranslationResult, AppError]:
        """Translate text using patterns."""
        start_time = time.time()
        
        # Validation pipeline
        result = await self._validate_and_translate(text, direction)
        
        # Process result
        return result.map(
            lambda translated: self._create_success_result(
                text, translated, direction, start_time
            )
        )
    
    async def _validate_and_translate(
        self,
        text: SourceText,
        direction: TranslationDirection
    ) -> Result[TargetText, AppError]:
        """Validate input and perform translation."""
        validation_result = self._validator.validate(text)
        if isinstance(validation_result, Failure):
            return validation_result

        pattern_set_result = self._repository.get_pattern_set(direction)
        if isinstance(pattern_set_result, Failure):
            return pattern_set_result

        validated_text = validation_result.unwrap()
        pattern_set = pattern_set_result.unwrap()

        # Handle the Result from apply_patterns
        applied_text_result = self._applicator.apply_patterns(validated_text, pattern_set)
        if isinstance(applied_text_result, Failure):
            return applied_text_result

        applied_text = applied_text_result.unwrap()
        cleaned_text = self._cleaner.clean(applied_text, direction)
        target_text = TargetText(cleaned_text)
        return Success(target_text)
    
    def _create_success_result(
        self,
        original: SourceText,
        translated: TargetText,
        direction: TranslationDirection,
        start_time: float
    ) -> TranslationResult:
        """Create successful translation result."""
        return TranslationResult(
            success=True,
            original_text=original,
            translated_text=translated,
            direction=direction,
            confidence=self._confidence.calculate(original, translated),
            translation_method=self.name,
            processing_time=time.time() - start_time,
            metadata=self._create_metadata(original, translated, direction)
        )
    
    def _create_metadata(self, original: str, translated: str, direction: TranslationDirection) -> dict:
        """
        Note: This is a pure function (no side effects).
        Create metadata for result."""
        return {
            "pattern_count": self._get_pattern_count(direction),
            "text_length": len(original),
            "result_length": len(translated)
        }
    
    def _get_pattern_count(self, direction: TranslationDirection) -> int:
        """
        Note: This is a pure function (no side effects).
        Get pattern count for a direction."""
        result = self._repository.get_pattern_set(direction)
        if isinstance(result, Success):
            return len(result.unwrap().rules)
        return 0
    
    def _create_error_result(self, text: str, direction: TranslationDirection, error: Failure) -> TranslationResult:
        """
        Note: This is a pure function (no side effects).
        Create error translation result."""
        app_error = error.failure()
        return TranslationResult(
            success=False,
            original_text=text,
            translated_text="",
            direction=direction,
            confidence=0.0,
            translation_method=self.name,
            processing_time=0.0,
            error_message=f"{app_error.code}: {app_error.message}",
            metadata={}
        )