"""
Functional utilities to reduce code complexity and enable cleaner patterns.
"""

from typing import Callable, TypeVar, Any, Optional, List
from functools import reduce, wraps
import asyncio
from .result_enhanced import Result, Success, Failure

T = TypeVar('T')
U = TypeVar('U')


# Guard clause helpers
def guard(condition: bool, error_code: str, message: str) -> Result[None]:
    """Create a guard clause that returns Result."""
    if not condition:
        return Failure(error_code, message)
    return Success(None)


def guard_not_none(value: Optional[T], error_code: str, message: str) -> Result[T]:
    """Guard against None values."""
    if value is None:
        return Failure(error_code, message)
    return Success(value)


# Async/Sync bridge utility
class AsyncSyncBridge:
    """Utility for running async code in sync context."""
    
    @staticmethod
    def run(coro):
        """Run async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a task
                task = asyncio.create_task(coro)
                return asyncio.run_until_complete(task)
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(coro)


# Validation pipeline
class ValidationPipeline:
    """Composable validation pipeline."""
    
    def __init__(self):
        self.validators: List[Callable[[Any], Result[Any]]] = []
    
    def add(self, validator: Callable[[Any], Result[Any]]) -> 'ValidationPipeline':
        """Add a validator to the pipeline."""
        self.validators.append(validator)
        return self
    
    def validate(self, value: Any) -> Result[Any]:
        """Run all validators in sequence."""
        result = Success(value)
        for validator in self.validators:
            result = result.flat_map(validator)
        return result


# Common validators
class Validators:
    """Common validation functions returning Results."""
    
    @staticmethod
    def not_empty(value: str, field_name: str = "value") -> Result[str]:
        """Validate string is not empty."""
        if not value or not value.strip():
            return Failure("EMPTY_VALUE", f"{field_name} cannot be empty")
        return Success(value)
    
    @staticmethod
    def length_between(min_len: int, max_len: int, field_name: str = "value"):
        """Create a length validator."""
        def validator(value: str) -> Result[str]:
            length = len(value)
            if length < min_len:
                return Failure("TOO_SHORT", f"{field_name} must be at least {min_len} characters")
            if length > max_len:
                return Failure("TOO_LONG", f"{field_name} must be at most {max_len} characters")
            return Success(value)
        return validator
    
    @staticmethod
    def matches_pattern(pattern: str, error_code: str, error_message: str):
        """Create a regex pattern validator."""
        import re
        compiled = re.compile(pattern)
        
        def validator(value: str) -> Result[str]:
            if not compiled.match(value):
                return Failure(error_code, error_message)
            return Success(value)
        return validator


# Retry utility
async def retry_async(
    operation: Callable[[], Result[T]],
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0
) -> Result[T]:
    """Retry an operation with exponential backoff."""
    last_failure = None
    delay = delay_seconds
    
    for attempt in range(max_attempts):
        result = await operation() if asyncio.iscoroutinefunction(operation) else operation()
        
        if isinstance(result, Success):
            return result
        
        last_failure = result
        if attempt < max_attempts - 1:
            await asyncio.sleep(delay)
            delay *= backoff_factor
    
    return Failure(
        "MAX_RETRIES_EXCEEDED",
        f"Operation failed after {max_attempts} attempts",
        {"last_error": last_failure}
    )


# Method size enforcement decorator
def max_lines(limit: int = 10):
    """Decorator to enforce maximum method size (for development)."""
    def decorator(func):
        import inspect
        lines = len(inspect.getsource(func).split('\n'))
        if lines > limit:
            import warnings
            warnings.warn(
                f"Method {func.__name__} has {lines} lines, exceeds limit of {limit}",
                UserWarning
            )
        return func
    return decorator


# Null object implementations
class NullObject:
    """Base null object that does nothing."""
    def __getattr__(self, name):
        return lambda *args, **kwargs: None