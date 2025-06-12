"""
NLP translation service following the Intentional Disclosure Principle.

Handles natural language translation with all methods ≤10 lines following IDP Rule 2.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional
from returns.result import Result, Success, Failure

from .nlp_types import (
    NaturalLanguageText, TCEText, TAUText, PatternMatch,
    TranslationResult, TranslationContext, LanguagePattern,
    TranslationDirection, NormalizationType
)
from .nlp_pattern_handlers import PatternHandlerFactory
from ..infrastructure.nlp_infrastructure import (
    PatternRegistry, TextNormalizer, PhraseMapper,
    TCEPatternMatcher, TemplateProcessor
)


class NLPTranslationService:
    """Pure business logic for NLP translation operations."""
    
    def __init__(self, context: Optional[TranslationContext] = None):
        self._context = context or TranslationContext()
        self._patterns = self._initialize_patterns()
        self._normalizer = TextNormalizer()
    
    def translate_nl_to_tce(self, text: NaturalLanguageText) -> TranslationResult:
        """Translate natural language to TCE."""
        # Clean and validate input
        cleaned_text = self._prepare_input(text)
        if not cleaned_text:
            return TranslationResult.failure_result("Empty input text")
        
        # Try pattern matching
        pattern_result = self._match_patterns(cleaned_text)
        if pattern_result:
            return self._apply_pattern_handler(pattern_result)
        
        # Fallback to rule-based translation
        return self._apply_rule_based_translation(cleaned_text)
    
    def translate_tce_to_nl(self, text: TCEText) -> TranslationResult:
        """Translate TCE to natural language."""
        # Clean input
        cleaned_text = str(text).strip()
        if not cleaned_text:
            return TranslationResult.failure_result("Empty input text")
        
        # Remove trailing period for processing
        if cleaned_text.endswith('.'):
            cleaned_text = cleaned_text[:-1]
        
        # Try pattern matching
        match_result = TCEPatternMatcher.match_tce_pattern(cleaned_text)
        if match_result:
            return self._apply_tce_pattern(match_result)
        
        # Fallback - return as is
        return TranslationResult.success_result(cleaned_text)
    
    def _initialize_patterns(self) -> List[LanguagePattern]:
        """Initialize language patterns."""
        # Get default patterns
        patterns = PatternRegistry.get_default_patterns()
        
        # Add any custom patterns from context
        patterns.extend(self._context.custom_patterns)
        
        # Sort by priority
        patterns.sort(key=lambda p: p.priority, reverse=True)
        
        return patterns
    
    def _prepare_input(self, text: NaturalLanguageText) -> str:
        """Prepare input text for processing."""
        # Basic cleaning
        cleaned = TextNormalizer.clean_input(str(text))
        
        if not cleaned:
            return ""
        
        # Apply normalization rules
        rules = TextNormalizer.get_default_rules()
        normalized = TextNormalizer.normalize_text(cleaned, rules)
        
        # Remove trailing period for pattern matching
        if normalized.endswith('.'):
            normalized = normalized[:-1]
        
        return normalized
    
    def _match_patterns(self, text: str) -> Optional[PatternMatch]:
        """Match text against patterns."""
        for pattern in self._patterns:
            match = pattern.matches(text)
            if match:
                groups = pattern.extract_groups(match)
                return PatternMatch(
                    pattern_type=pattern.pattern_type,
                    template=pattern.template,
                    matched_groups=groups,
                    original_text=text
                )
        return None
    
    def _apply_pattern_handler(self, match: PatternMatch) -> TranslationResult:
        """Apply pattern handler to generate TCE."""
        handler = PatternHandlerFactory.create_handler(match.pattern_type)
        
        if not handler:
            return TranslationResult.failure_result(
                f"No handler for pattern type: {match.pattern_type}"
            )
        
        result = handler.handle(match)
        
        if isinstance(result, Success):
            # Add period for TCE format
            tce_text = result.unwrap()
            if not tce_text.endswith('.'):
                tce_text += '.'
            return TranslationResult.success_result(tce_text, match.pattern_type)
        else:
            return TranslationResult.failure_result(result.failure())
    
    def _apply_rule_based_translation(self, text: str) -> TranslationResult:
        """Apply rule-based translation as fallback."""
        # Try phrase mapping
        mapped_text = self._apply_phrase_mappings(text)
        
        # Add period if needed
        if mapped_text and not mapped_text.endswith('.'):
            mapped_text += '.'
        
        return TranslationResult.success_result(mapped_text)
    
    def _apply_phrase_mappings(self, text: str) -> str:
        """Apply phrase mappings to text."""
        result = text
        
        # Common phrase replacements
        replacements = [
            ("it is not the case that", "not"),
            ("it is the case that", ""),
            ("is not", "is not"),
            ("are not", "are not"),
            ("at least one", "exists"),
            ("there is", "exists"),
        ]
        
        for old_phrase, new_phrase in replacements:
            result = result.replace(old_phrase, new_phrase)
        
        return result.strip()
    
    def _apply_tce_pattern(self, match_result: tuple) -> TranslationResult:
        """Apply TCE pattern for reverse translation."""
        pattern_type, template, match = match_result
        
        # Extract groups from match
        groups = [match.group(i) for i in range(len(match.groups()) + 1)]
        
        # Apply template
        nl_text = template
        for i, group in enumerate(groups[1:]):  # Skip full match
            nl_text = nl_text.replace(f"{{{i}}}", group)
        
        # Post-process for natural language
        nl_text = self._post_process_natural_language(nl_text)
        
        return TranslationResult.success_result(nl_text)
    
    def _post_process_natural_language(self, text: str) -> str:
        """Post-process text for natural language output."""
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        # Ensure ends with period
        if text and not text.endswith('.'):
            text += '.'
        
        # Fix spacing
        text = ' '.join(text.split())
        
        return text


class RuleBasedTranslationService:
    """Service for rule-based translation fallbacks."""
    
    def __init__(self):
        self._phrase_mapper = PhraseMapper()
    
    def translate_with_rules(self, text: str) -> str:
        """Translate using rule-based approach."""
        # Handle special cases
        if self._is_negation(text):
            return self._translate_negation(text)
        
        if self._is_implication(text):
            return self._translate_implication(text)
        
        # Default - clean up and return
        return self._clean_for_tce(text)
    
    def _is_negation(self, text: str) -> bool:
        """Check if text is a negation."""
        negation_starts = [
            "it is not", "not", "no", "none", "nobody", "nothing"
        ]
        return any(text.lower().startswith(neg) for neg in negation_starts)
    
    def _translate_negation(self, text: str) -> str:
        """Translate negation patterns."""
        if text.lower().startswith("it is not the case that"):
            inner = text[24:].strip()
            return f"not ({inner})"
        
        if text.lower().startswith("not "):
            return text
        
        return f"not ({text})"
    
    def _is_implication(self, text: str) -> bool:
        """Check if text contains implication."""
        return " implies " in text.lower() or " entails " in text.lower()
    
    def _translate_implication(self, text: str) -> str:
        """Translate implication patterns."""
        for word in ["implies", "entails"]:
            if f" {word} " in text.lower():
                parts = text.split(f" {word} ", 1)
                if len(parts) == 2:
                    return f"if {parts[0].strip()} then {parts[1].strip()}"
        return text
    
    def _clean_for_tce(self, text: str) -> str:
        """Clean text for TCE format."""
        # Remove unnecessary words
        remove_words = ["the", "a", "an"]
        words = text.split()
        cleaned = [w for w in words if w.lower() not in remove_words or words.index(w) > 0]
        
        return " ".join(cleaned)