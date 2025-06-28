"""
Enhanced Result type with monadic operations for functional composition.
Enables railway-oriented programming and eliminates nested conditionals.
"""

from typing import TypeVar, Generic, Callable, Union, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')


class Result(ABC, Generic[T]):
    """Base Result type supporting monadic operations."""
    
    @abstractmethod
    def is_success(self) -> bool:
        """Check if this is a success result."""
        pass
    
    @abstractmethod
    def is_failure(self) -> bool:
        """Check if this is a failure result."""
        pass
    
    @abstractmethod
    def map(self, func: Callable[[T], U]) -> 'Result[U]':
        """Transform success value, propagate failure."""
        pass
    
    @abstractmethod
    def flat_map(self, func: Callable[[T], 'Result[U]']) -> 'Result[U]':
        """Chain operations that return Results."""
        pass
    
    @abstractmethod
    def or_else(self, default: Union[T, Callable[[], T]]) -> T:
        """Provide default value for failure cases."""
        pass
    
    @abstractmethod
    def fold(self, on_success: Callable[[T], U], on_failure: Callable[['Failure'], U]) -> U:
        """Handle both success and failure cases with single expression."""
        pass
    
    @abstractmethod
    def filter(self, predicate: Callable[[T], bool], error_code: str = "FILTER_FAILED") -> 'Result[T]':
        """Filter success values, converting false predicates to failures."""
        pass
    
    @abstractmethod
    def recover(self, recovery: Callable[['Failure'], T]) -> 'Result[T]':
        """Attempt to recover from failure."""
        pass
    
    @abstractmethod
    def to_optional(self) -> Optional[T]:
        """Convert to Optional, losing error information."""
        pass


@dataclass(frozen=True)
class Success(Result[T], Generic[T]):
    """Represents a successful operation result."""
    value: T
    
    def is_success(self) -> bool:
        return True
    
    def is_failure(self) -> bool:
        return False
    
    def map(self, func: Callable[[T], U]) -> Result[U]:
        """Transform the success value."""
        try:
            return Success(func(self.value))
        except Exception as e:
            return Failure("MAP_ERROR", f"Error in map operation: {str(e)}")
    
    def flat_map(self, func: Callable[[T], Result[U]]) -> Result[U]:
        """Chain operations that return Results."""
        try:
            return func(self.value)
        except Exception as e:
            return Failure("FLATMAP_ERROR", f"Error in flatMap operation: {str(e)}")
    
    def or_else(self, default: Union[T, Callable[[], T]]) -> T:
        """Return the success value."""
        return self.value
    
    def fold(self, on_success: Callable[[T], U], on_failure: Callable[['Failure'], U]) -> U:
        """Apply success function to value."""
        return on_success(self.value)
    
    def filter(self, predicate: Callable[[T], bool], error_code: str = "FILTER_FAILED") -> Result[T]:
        """Filter success value."""
        try:
            if predicate(self.value):
                return self
            return Failure(error_code, f"Value {self.value} did not match predicate")
        except Exception as e:
            return Failure("FILTER_ERROR", f"Error in filter operation: {str(e)}")
    
    def recover(self, recovery: Callable[['Failure'], T]) -> Result[T]:
        """No recovery needed for success."""
        return self
    
    def to_optional(self) -> Optional[T]:
        """Convert to Some."""
        return self.value


@dataclass(frozen=True)
class Failure(Result[Any]):
    """Represents a failed operation result."""
    error_code: str
    message: str
    details: Optional[dict] = None
    
    def is_success(self) -> bool:
        return False
    
    def is_failure(self) -> bool:
        return True
    
    def map(self, func: Callable[[Any], Any]) -> 'Failure':
        """Propagate failure unchanged."""
        return self
    
    def flat_map(self, func: Callable[[Any], Result[Any]]) -> 'Failure':
        """Propagate failure unchanged."""
        return self
    
    def or_else(self, default: Union[T, Callable[[], T]]) -> T:
        """Return the default value."""
        if callable(default):
            return default()
        return default
    
    def fold(self, on_success: Callable[[Any], U], on_failure: Callable[['Failure'], U]) -> U:
        """Apply failure function to self."""
        return on_failure(self)
    
    def filter(self, predicate: Callable[[Any], bool], error_code: str = "FILTER_FAILED") -> 'Failure':
        """Propagate failure unchanged."""
        return self
    
    def recover(self, recovery: Callable[['Failure'], T]) -> Result[T]:
        """Attempt to recover from failure."""
        try:
            return Success(recovery(self))
        except Exception as e:
            return Failure("RECOVERY_ERROR", f"Recovery failed: {str(e)}")
    
    def to_optional(self) -> None:
        """Convert to None."""
        return None


# Utility functions for Result creation
def success(value: T) -> Success[T]:
    """Create a success result."""
    return Success(value)


def failure(error_code: str, message: str, details: Optional[dict] = None) -> Failure:
    """Create a failure result."""
    return Failure(error_code, message, details)


# Utility functions for working with Results
def sequence(results: list[Result[T]]) -> Result[list[T]]:
    """Convert list of Results to Result of list, failing on first failure."""
    values = []
    for result in results:
        if isinstance(result, Failure):
            return result
        values.append(result.value)
    return Success(values)


def traverse(items: list[T], func: Callable[[T], Result[U]]) -> Result[list[U]]:
    """Apply function returning Result to each item, collecting results."""
    results = []
    for item in items:
        result = func(item)
        if isinstance(result, Failure):
            return result
        results.append(result.value)
    return Success(results)


def try_catch(func: Callable[[], T], error_code: str = "EXCEPTION") -> Result[T]:
    """Convert exception-throwing function to Result."""
    try:
        return Success(func())
    except Exception as e:
        return Failure(error_code, str(e))


# Function composition utilities
def compose(*functions):
    """Compose functions from right to left."""
    def inner(arg):
        result = arg
        for func in reversed(functions):
            result = func(result)
        return result
    return inner


def pipe(*functions):
    """Pipe functions from left to right."""
    def inner(arg):
        result = arg
        for func in functions:
            result = func(result)
        return result
    return inner
