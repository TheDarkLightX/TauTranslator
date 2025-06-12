#!/usr/bin/env python3
"""
UFO Tools Comparison with Current Patterns
Evaluating UFO tools for potential adoption in TauTranslator
"""

from typing import Optional, List, Dict, Any
from ufo.containers import Simple, Maybe, Result as UFOResult
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

print("\n=== CONTAINER PATTERN COMPARISON ===\n")

# Our current Result monad pattern
def validate_text(text: str) -> Result[str]:
    if len(text) < 3:
        return Failure("TOO_SHORT", "Text must be at least 3 characters")
    return Success(text)

def make_uppercase(text: str) -> str:
    return text.upper()

def add_prefix(text: str) -> str:
    return f"TRANSLATED: {text}"

# Using our Result pattern
print("Our Result Pattern:")
result = (validate_text("hello")
    .map(make_uppercase)
    .map(add_prefix))

if isinstance(result, Success):
    print(f"Success: {result.value}")
else:
    print(f"Failure: {result.error}")

# Using UFO Container
print("\nUFO Container Pattern:")
ufo_result = (Container("hello")
    .then(make_uppercase)
    .then(add_prefix)
    .unwrap())
print(f"Result: {ufo_result}")

print("\n=== ARRAY PATTERN COMPARISON ===\n")

# Traditional list comprehension
names = ["alice", "bob", "charlie"]
traditional = [add_prefix(make_uppercase(name)) for name in names]
print(f"Traditional: {traditional}")

# Using UFO Array
ufo_array = (Array(*names)
    .then(make_uppercase)
    .then(add_prefix)
    .unwrap())
print(f"UFO Array: {ufo_array}")

print("\n=== COMPLEX PIPELINE EXAMPLE ===\n")

# Simulating our pattern translator pipeline
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

# UFO Pipeline
input_text = "  Hello world  my   friend  "
ufo_pipeline = (Container(input_text)
    .then(clean_text)
    .then(apply_patterns)
    .then(capitalize_sentences)
    .unwrap())

print(f"Input: '{input_text}'")
print(f"Output: '{ufo_pipeline}'")

print("\n=== ERROR HANDLING COMPARISON ===\n")

# UFO doesn't have built-in error handling like our Result type
# Let's see how we might combine them

def safe_divide(x: float, y: float) -> Result[float]:
    if y == 0:
        return Failure("DIVISION_BY_ZERO", "Cannot divide by zero")
    return Success(x / y)

# Our Result pattern handles errors explicitly
result1 = safe_divide(10, 2).map(lambda x: x * 2)
result2 = safe_divide(10, 0).map(lambda x: x * 2)

print(f"10 / 2 * 2 = {result1}")
print(f"10 / 0 * 2 = {result2}")

# UFO Container would need error handling wrapper
def divide_with_container(x: float, y: float) -> float:
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

try:
    ufo_divide = Container(10).then(lambda x: divide_with_container(x, 2)).unwrap()
    print(f"UFO divide success: {ufo_divide}")
except ValueError as e:
    print(f"UFO divide error: {e}")

print("\n=== CONCLUSION ===")
print("1. UFO's @mutation_free is excellent for ensuring immutability")
print("2. Container provides cleaner syntax for transformations")
print("3. Our Result type provides better error handling")
print("4. Could combine both: Result for errors, Container for transformations")
print("5. Array simplifies list transformations")