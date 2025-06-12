#!/usr/bin/env python3
"""
UFO Integration Example
Showing how to add @mutation_free to our refactored pattern_translator.py
"""

from ufo.wrappers import mutation_free
from typing import Dict, List, Set, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.unified.core.domain_types import Result, Success, Failure, SourceText, TargetText
from backend.unified.translators.base import TranslationDirection

# Example: Enhancing our refactored PatternTranslator with @mutation_free

class PatternApplicator:
    """Applies translation patterns - enhanced with @mutation_free."""
    
    @mutation_free
    def apply_patterns(
        self, 
        text: str, 
        patterns: Set[tuple]
    ) -> Result[str]:
        """Apply all patterns to text - guaranteed immutable."""
        if not patterns:
            return Success(text)
        
        result = text
        for pattern, replacement in patterns:
            result = self._apply_single_pattern(result, pattern, replacement)
        
        return Success(result)
    
    @mutation_free
    def _apply_single_pattern(
        self, 
        text: str, 
        pattern: str, 
        replacement: str
    ) -> str:
        """Apply a single pattern - immutable."""
        return text.replace(pattern, replacement)


class TextCleaner:
    """Cleans translated text - enhanced with @mutation_free."""
    
    @mutation_free
    def clean(self, text: str, direction: TranslationDirection) -> str:
        """Clean text based on direction - immutable."""
        cleaners = {
            TranslationDirection.TO_TAU: self._clean_tau_output,
            TranslationDirection.TO_ENGLISH: self._clean_requirements_output
        }
        
        cleaner = cleaners.get(direction, self._default_clean)
        return cleaner(text)
    
    @mutation_free
    def _clean_tau_output(self, text: str) -> str:
        """Clean TAU output - immutable."""
        # Multiple cleaning steps, all immutable
        text = self._normalize_whitespace(text)
        text = self._fix_tau_operators(text)
        text = self._ensure_tau_format(text)
        return text
    
    @mutation_free
    def _clean_requirements_output(self, text: str) -> str:
        """Clean requirements output - immutable."""
        text = self._normalize_whitespace(text)
        text = self._capitalize_sentences(text)
        text = self._fix_grammar(text)
        return text
    
    @mutation_free
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace - immutable."""
        return " ".join(text.split())
    
    @mutation_free
    def _fix_tau_operators(self, text: str) -> str:
        """Fix TAU operator spacing - immutable."""
        operators = ["->", "&&", "||", "!", "==", "!=", "<=", ">="]
        result = text
        for op in operators:
            result = result.replace(f" {op} ", op)
            result = result.replace(f"{op}", f" {op} ")
        return self._normalize_whitespace(result)
    
    @mutation_free
    def _ensure_tau_format(self, text: str) -> str:
        """Ensure proper TAU format - immutable."""
        return text.strip()
    
    @mutation_free
    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize sentences - immutable."""
        sentences = text.split(". ")
        capitalized = [s.strip().capitalize() for s in sentences if s]
        return ". ".join(capitalized) + ("." if text.rstrip().endswith(".") else "")
    
    @mutation_free
    def _fix_grammar(self, text: str) -> str:
        """Basic grammar fixes - immutable."""
        # Simple grammar rules
        text = text.replace(" i ", " I ")
        text = text.replace(". i ", ". I ")
        if text.startswith("i "):
            text = "I " + text[2:]
        return text
    
    @mutation_free
    def _default_clean(self, text: str) -> str:
        """Default cleaning - immutable."""
        return self._normalize_whitespace(text)


# Demonstration
print("=== PATTERN TRANSLATOR WITH @mutation_free ===\n")

# Test immutability
applicator = PatternApplicator()
patterns = {("hello", "hola"), ("world", "mundo")}
text = "hello world, hello friend"

print(f"Original patterns: {patterns}")
result = applicator.apply_patterns(text, patterns)
print(f"Patterns after apply: {patterns}")  # Unchanged!
print(f"Result: {result}")

# Test cleaner
cleaner = TextCleaner()
tau_text = "always   x>5  ->  y==10"
req_text = "the system shall process. it must be fast. i think it works."

print(f"\nTAU cleaning:")
print(f"Before: '{tau_text}'")
cleaned_tau = cleaner.clean(tau_text, TranslationDirection.TO_TAU)
print(f"After: '{cleaned_tau}'")

print(f"\nRequirements cleaning:")
print(f"Before: '{req_text}'")
cleaned_req = cleaner.clean(req_text, TranslationDirection.TO_ENGLISH)
print(f"After: '{cleaned_req}'")

# Benefits demonstration
print("\n=== BENEFITS OF @mutation_free ===")

class ConfigProcessor:
    """Example showing mutation protection."""
    
    @mutation_free
    def process_config(self, config: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Process configuration with defaults - immutable."""
        # Merge defaults with config
        result = defaults.copy()
        result.update(config)
        
        # Normalize values
        if "timeout" in result:
            result["timeout"] = max(1, min(300, result["timeout"]))
        
        # Add computed values
        result["processed"] = True
        result["version"] = "2.0"
        
        return result

processor = ConfigProcessor()
user_config = {"timeout": 500, "debug": True}
defaults = {"timeout": 30, "retry": 3, "debug": False}

print(f"User config before: {user_config}")
print(f"Defaults before: {defaults}")

processed = processor.process_config(user_config, defaults)

print(f"User config after: {user_config}")  # Unchanged!
print(f"Defaults after: {defaults}")  # Unchanged!
print(f"Processed config: {processed}")

print("\n=== RECOMMENDATION ===")
print("Add @mutation_free to:")
print("1. All methods in TextValidator")
print("2. All methods in PatternApplicator")
print("3. All methods in TextCleaner")
print("4. All methods in ConfidenceCalculator")
print("5. Any pure transformation functions")
print("\nThis ensures immutability and prevents bugs!")