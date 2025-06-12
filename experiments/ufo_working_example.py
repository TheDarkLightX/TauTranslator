#!/usr/bin/env python3
"""
UFO Tools Working Example
Testing the actual UFO API
"""

from ufo.containers import Simple, Maybe, Result as UFOResult, ListType
from ufo.wrappers import mutation_free
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.unified.core.domain_types import Result, Success, Failure

print("=== TESTING UFO CONTAINERS ===\n")

# Test Simple container with >> operator
def double(x):
    return x * 2

def add_ten(x):
    return x + 10

print("Simple container with >> operator:")
result = Simple(5) >> double >> add_ten
print(f"Simple(5) >> double >> add_ten = {result.unwrap()}")

# Test with string transformations
def make_upper(s):
    return Simple(s.upper())

def add_prefix(s):
    return Simple(f"PREFIX: {s}")

print("\nString transformations:")
text_result = Simple("hello") >> make_upper >> add_prefix
print(f"Result: {text_result.unwrap()}")

# Test Maybe container
print("\n=== MAYBE CONTAINER ===")

def safe_divide(x, y):
    if y == 0:
        return Maybe(None)
    return Maybe(x / y)

maybe1 = Maybe(10) >> (lambda x: safe_divide(x, 2)) >> double
maybe2 = Maybe(10) >> (lambda x: safe_divide(x, 0)) >> double

print(f"Maybe(10) / 2 * 2 = {maybe1.unwrap()}")
print(f"Maybe(10) / 0 * 2 = {maybe2.unwrap()}")

# Test mutation_free decorator
print("\n=== MUTATION FREE DECORATOR ===")

@mutation_free
def process_list(items, new_item):
    items.append(new_item)
    return sorted(items)

original = [3, 1, 4]
print(f"Original list: {original}")
result = process_list(original, 2)
print(f"Result: {result}")
print(f"Original after call: {original}")

# Test UFOResult
print("\n=== UFO RESULT TYPE ===")

def divide_with_result(x, y):
    if y == 0:
        return UFOResult.failure("Division by zero")
    return UFOResult.success(x / y)

# Check how UFOResult works
res1 = divide_with_result(10, 2)
res2 = divide_with_result(10, 0)

print(f"10 / 2 = {res1}")
print(f"10 / 0 = {res2}")

# Try chaining with Result
if hasattr(res1, 'bind'):
    chained = res1.bind(lambda x: UFOResult.success(x * 2))
    print(f"Chained result: {chained}")

print("\n=== PRACTICAL REFACTORING EXAMPLE ===")

# Original method (simplified from our codebase)
def translate_text_original(text: str) -> Result[str]:
    # Validate
    if len(text) < 1:
        return Failure("EMPTY_TEXT", "Text cannot be empty")
    
    # Clean
    cleaned = text.strip().lower()
    
    # Apply patterns
    patterns = {"hello": "hola", "world": "mundo"}
    result = cleaned
    for k, v in patterns.items():
        result = result.replace(k, v)
    
    return Success(result)

# Using UFO Simple for the pipeline
@mutation_free
def translate_text_ufo(text: str) -> str:
    def clean(t):
        return Simple(t.strip().lower())
    
    def apply_patterns(t):
        patterns = {"hello": "hola", "world": "mundo"}
        result = t
        for k, v in patterns.items():
            result = result.replace(k, v)
        return Simple(result)
    
    return (Simple(text) >> clean >> apply_patterns).unwrap()

# Test both approaches
test_text = "  Hello World  "
print(f"Original approach: {translate_text_original(test_text)}")
print(f"UFO approach: {translate_text_ufo(test_text)}")

print("\n=== KEY FINDINGS ===")
print("1. UFO uses >> operator for chaining, not .then()")
print("2. Each function in chain must return a container")
print("3. @mutation_free works great for immutability")
print("4. Maybe handles None elegantly")
print("5. UFOResult exists but has different API than ours")