#!/usr/bin/env python3
"""
UFO Tools Comparison with Current Patterns
Evaluating UFO tools for potential adoption in TauTranslator
"""

from typing import Optional, List, Dict, Any
from ufo.containers import Simple, Maybe, Result as UFOResult, ListType
from ufo.wrappers import mutation_free
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.unified.core.domain_types import Result, Success, Failure, SourceText, TargetText

# Example 1: Mutation-Free Decorator
print("=== MUTATION-FREE DECORATOR EXAMPLE ===\n")

# Without decorator - can mutate input
def add_exclamation_unsafe(text: str, items: list) -> str:
    items.append("!")  # This mutates the input list
    return text + "!"

# With decorator - prevents mutation
@mutation_free
def add_exclamation_safe(text: str, items: list) -> str:
    items.append("!")  # This won't affect the original list
    return text + "!"

# Test mutation safety
original_list = ["hello", "world"]
print(f"Original list: {original_list}")

result1 = add_exclamation_unsafe("test", original_list)
print(f"After unsafe function: {original_list}")  # List is mutated

original_list2 = ["hello", "world"]
result2 = add_exclamation_safe("test", original_list2)
print(f"After safe function: {original_list2}")  # List is unchanged

print("\n=== SIMPLE CONTAINER PATTERN ===\n")

# UFO Simple container for transformations
def make_uppercase(text: str) -> str:
    return text.upper()

def add_prefix(text: str) -> str:
    return f"TRANSLATED: {text}"

# Using UFO Simple container
print("UFO Simple Container:")
ufo_simple = (Simple("hello")
    .then(make_uppercase)
    .then(add_prefix)
    .unwrap())
print(f"Result: {ufo_simple}")

# Check if Simple supports chaining with multiple values
print("\n=== LISTTYPE PATTERN ===\n")

names = ["alice", "bob", "charlie"]

# Using UFO ListType for list transformations
ufo_list = (ListType(names)
    .then(make_uppercase)
    .then(add_prefix)
    .unwrap())
print(f"UFO ListType: {ufo_list}")

print("\n=== MAYBE PATTERN FOR OPTIONAL VALUES ===\n")

# UFO Maybe for handling optional values
def safe_get_length(text: Optional[str]) -> Optional[int]:
    return len(text) if text else None

# Using Maybe
maybe_result1 = (Maybe("hello")
    .then(safe_get_length)
    .then(lambda x: x * 2)
    .unwrap())
print(f"Maybe with value: {maybe_result1}")

maybe_result2 = (Maybe(None)
    .then(safe_get_length)
    .then(lambda x: x * 2)
    .unwrap())
print(f"Maybe with None: {maybe_result2}")

print("\n=== UFO RESULT VS OUR RESULT ===\n")

# UFO Result pattern
def divide_ufo(x: float, y: float) -> UFOResult[float, str]:
    if y == 0:
        return UFOResult.failure("Cannot divide by zero")
    return UFOResult.success(x / y)

# Test UFO Result
ufo_res1 = divide_ufo(10, 2).then(lambda x: x * 2)
ufo_res2 = divide_ufo(10, 0).then(lambda x: x * 2)

print(f"UFO Result 10/2*2: {ufo_res1}")
print(f"UFO Result 10/0*2: {ufo_res2}")

# Our Result pattern
def divide_ours(x: float, y: float) -> Result[float]:
    if y == 0:
        return Failure("DIVISION_BY_ZERO", "Cannot divide by zero")
    return Success(x / y)

our_res1 = divide_ours(10, 2).map(lambda x: x * 2)
our_res2 = divide_ours(10, 0).map(lambda x: x * 2)

print(f"Our Result 10/2*2: {our_res1}")
print(f"Our Result 10/0*2: {our_res2}")

print("\n=== COMPLEX PIPELINE WITH MUTATION_FREE ===\n")

@mutation_free
def clean_text(text: str) -> str:
    """Remove extra spaces."""
    return " ".join(text.split())

@mutation_free
def apply_patterns(text: str) -> str:
    """Apply translation patterns."""
    replacements = {
        "hello": "hola",
        "world": "mundo",
        "friend": "amigo"
    }
    result = text.lower()
    for eng, esp in replacements.items():
        result = result.replace(eng, esp)
    return result

@mutation_free
def capitalize_sentences(text: str) -> str:
    """Capitalize first letter of sentences."""
    sentences = text.split(". ")
    capitalized = [s.capitalize() for s in sentences]
    return ". ".join(capitalized)

# UFO Pipeline with Simple
input_text = "  Hello world  my   friend  "
ufo_pipeline = (Simple(input_text)
    .then(clean_text)
    .then(apply_patterns)
    .then(capitalize_sentences)
    .unwrap())

print(f"Input: '{input_text}'")
print(f"Output: '{ufo_pipeline}'")

# Same with our approach (without Result since these are pure transformations)
our_pipeline = capitalize_sentences(apply_patterns(clean_text(input_text)))
print(f"Our approach: '{our_pipeline}'")

print("\n=== PRACTICAL EXAMPLE: REFACTORING A METHOD ===\n")

# Simulating a method from our pattern_translator
class PatternTranslatorComparison:
    @mutation_free
    def apply_translation_patterns_ufo(self, text: str, patterns: List[tuple]) -> str:
        """Apply patterns using UFO style."""
        return (Simple(text)
            .then(lambda t: t.lower())
            .then(lambda t: self._apply_patterns(t, patterns))
            .then(lambda t: t.strip())
            .unwrap())
    
    @mutation_free
    def _apply_patterns(self, text: str, patterns: List[tuple]) -> str:
        result = text
        for pattern, replacement in patterns:
            result = result.replace(pattern, replacement)
        return result

translator = PatternTranslatorComparison()
patterns = [("hello", "hola"), ("world", "mundo")]
result = translator.apply_translation_patterns_ufo("Hello World!", patterns)
print(f"Pattern translation result: '{result}'")

print("\n=== CONCLUSIONS ===")
print("1. UFO uses 'Simple' not 'Container' (documentation mismatch)")
print("2. @mutation_free works excellently for immutability")
print("3. UFO has Result type that's similar to ours")
print("4. Maybe is useful for optional value handling")
print("5. ListType provides functional list operations")
print("6. The .then() chaining is clean and readable")