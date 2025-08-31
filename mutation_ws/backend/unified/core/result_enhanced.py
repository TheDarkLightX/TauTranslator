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
    # Support both Result[T] and Result[T, E] annotations at runtime
    # to maintain backward compatibility with existing type hints.
    def __class_getitem__(cls, params):  # type: ignore[override]
        # Allow 1- or 2-parameter forms without raising typing errors
        # e.g., Result[T] or Result[T, E]. We ignore type params at runtime.
        if isinstance(params, tuple):
            if len(params) in (1, 2):
                return cls
        else:
            return cls
        return cls

    # Compatibility helpers inspired by `returns` API
    @abstractmethod
    def unwrap(self) -> T:
        """Return the inner value or raise for Failure."""
        raise NotImplementedError

    @abstractmethod
    def failure(self) -> Any:
        """Return underlying error payload for Failure, or raise for Success."""
        raise NotImplementedError
    
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

    # Compatibility helpers
    def unwrap(self) -> T:
        return self.value

    def failure(self) -> Any:  # pragma: no cover - not expected for Success
        raise ValueError("Called failure() on Success")


@dataclass(frozen=True, init=False)
class Failure(Result[Any]):
    """Represents a failed operation result."""
    error_code: str
    message: str
    details: Optional[dict] = None
    
    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        """
        Backward-compatible constructor:
        - Failure(code, message, details=None)
        - Failure(message_str)
        - Failure(domain_error_obj) → will stringify
        """
        # Structured form via kwargs
        if 'error_code' in kwargs or 'message' in kwargs:
            error_code = kwargs.get('error_code', 'ERROR')
            message = kwargs.get('message', '')
            details = kwargs.get('details')
        else:
            # Positional handling
            if len(args) == 1:
                # Single string or object → treat as message
                error_code = 'ERROR'
                message = str(args[0])
                details = None
            elif len(args) >= 2:
                error_code = str(args[0])
                message = str(args[1])
                details = args[2] if len(args) >= 3 else None
            else:
                error_code = 'ERROR'
                message = ''
                details = None

        object.__setattr__(self, 'error_code', error_code)
        object.__setattr__(self, 'message', message)
        object.__setattr__(self, 'details', details)
    
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

    # Compatibility helpers
    def unwrap(self) -> Any:  # pragma: no cover - will raise
        raise ValueError(f"Tried to unwrap Failure[{self.error_code}]: {self.message}")

    def failure(self) -> Any:
        """Return a structured error payload when possible."""
        # Prefer details when it looks like a domain error; otherwise return message
        return self.details or {"code": self.error_code, "message": self.message}


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

# Backward-compatibility typing alias used by some tests as Result[T, E]
TypingResult = Result


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