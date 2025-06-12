"""
Error handling and resilience for gamification system.

Provides comprehensive error handling, recovery strategies, and logging.
Follows defensive programming principles.

Copyright: DarkLightX / Dana Edwards
"""

import logging
import traceback
from typing import Optional, Callable, Any, TypeVar, Union
from functools import wraps
from datetime import datetime

from ..core.result_enhanced import Result, Success, Failure

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

class GamificationError(Exception):
    """Base exception for gamification system errors."""
    
    def __init__(self, message: str, error_code: str, details: Optional[dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()

class ProfileError(GamificationError):
    """Errors related to user profiles."""
    pass

class PersistenceError(GamificationError):
    """Errors related to data persistence."""
    pass

class AchievementError(GamificationError):
    """Errors related to achievements."""
    pass

class AutocompleteError(GamificationError):
    """Errors related to autocomplete functionality."""
    pass

def safe_execute(
    operation: Callable[[], T],
    error_code: str,
    error_message: str,
    default_value: Optional[T] = None,
    log_error: bool = True
) -> Result[T]:
    """
    Safely execute an operation with error handling.
    
    Returns Result[T] with either the operation result or an error.
    """
    try:
        result = operation()
        return Success(result)
    except Exception as e:
        if log_error:
            logger.error(
                f"{error_message}: {str(e)}",
                extra={
                    "error_code": error_code,
                    "traceback": traceback.format_exc()
                }
            )
        
        if default_value is not None:
            logger.info(f"Using default value for {error_code}")
            return Success(default_value)
        
        return Failure(error_code, f"{error_message}: {str(e)}")

def retry_on_failure(
    max_attempts: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry operations on failure.
    
    Implements exponential backoff for retries.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}, "
                            f"retrying in {wait_time}s: {str(e)}"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator

def handle_ui_error(func: Callable) -> Callable:
    """
    Decorator to handle UI-related errors gracefully.
    
    Shows user-friendly error messages and logs details.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.error(
                f"UI error in {func.__name__}: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            
            # Show error dialog if Qt is available
            try:
                from PyQt6.QtWidgets import QMessageBox
                if hasattr(self, 'parent') or hasattr(self, 'window'):
                    parent = getattr(self, 'parent', None) or getattr(self, 'window', None)
                    if callable(parent):
                        parent = parent()
                    
                    msg = QMessageBox(parent)
                    msg.setIcon(QMessageBox.Icon.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText("An error occurred")
                    msg.setDetailedText(str(e))
                    msg.exec()
            except ImportError:
                pass  # Qt not available
            
            # Return safe default if possible
            return_type = func.__annotations__.get('return')
            if return_type == bool:
                return False
            elif return_type == str:
                return ""
            elif return_type == int:
                return 0
            elif return_type == list:
                return []
            elif return_type == dict:
                return {}
            
            return None
    
    return wrapper

class ErrorRecoveryStrategy:
    """
    Strategies for recovering from different types of errors.
    """
    
    @staticmethod
    def recover_profile_corruption(user_id: str) -> Result[dict]:
        """Recover from corrupted profile data."""
        logger.warning(f"Attempting to recover corrupted profile for user {user_id}")
        
        # Create minimal valid profile
        recovery_profile = {
            "user_id": user_id,
            "username": f"User_{user_id}",
            "total_xp": 0,
            "current_level": 1,
            "completed_achievements": [],
            "earned_badges": [],
            "active_challenges": [],
            "skill_progress": {},
            "daily_streak": 0,
            "last_active": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        return Success(recovery_profile)
    
    @staticmethod
    def recover_database_connection() -> Result[None]:
        """Recover from database connection errors."""
        logger.info("Attempting to recover database connection")
        
        # In a real implementation, might:
        # - Reset connection pool
        # - Switch to backup database
        # - Use in-memory fallback
        
        return Success(None)
    
    @staticmethod
    def recover_autocomplete_failure(context: dict) -> Result[list]:
        """Provide fallback suggestions on autocomplete failure."""
        logger.warning("Using fallback suggestions due to autocomplete failure")
        
        # Provide basic suggestions based on context
        fallback_suggestions = [
            {
                "text": "forall",
                "display": "forall - Universal quantifier",
                "category": "quantifier",
                "description": "Express properties for all values",
                "example": "forall x : x > 0",
                "difficulty": "beginner"
            },
            {
                "text": "exists",
                "display": "exists - Existential quantifier",
                "category": "quantifier",
                "description": "Express properties for at least one value",
                "example": "exists y : y < 0",
                "difficulty": "beginner"
            }
        ]
        
        return Success(fallback_suggestions)

class CircuitBreaker:
    """
    Circuit breaker pattern for preventing cascading failures.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func: Callable[[], T]) -> Result[T]:
        """Execute function with circuit breaker protection."""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                return Failure(
                    "CIRCUIT_OPEN",
                    "Service temporarily unavailable due to repeated failures"
                )
        
        try:
            result = func()
            self._on_success()
            return Success(result)
        except self.expected_exception as e:
            self._on_failure()
            return Failure("SERVICE_ERROR", str(e))
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again."""
        if not self.last_failure_time:
            return True
        
        time_since_failure = (datetime.now() - self.last_failure_time).seconds
        return time_since_failure >= self.recovery_timeout
    
    def _on_success(self):
        """Reset circuit breaker on successful call."""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None
    
    def _on_failure(self):
        """Record failure and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

class ValidationHelper:
    """
    Helper methods for input validation and sanitization.
    """
    
    @staticmethod
    def validate_user_id(user_id: Any) -> Result[str]:
        """Validate and sanitize user ID."""
        if not user_id:
            return Failure("INVALID_USER_ID", "User ID is required")
        
        user_id_str = str(user_id).strip()
        
        # Sanitize: alphanumeric and underscore only
        if not user_id_str.replace('_', '').isalnum():
            return Failure("INVALID_USER_ID", "User ID contains invalid characters")
        
        # Length check
        if len(user_id_str) > 50:
            return Failure("INVALID_USER_ID", "User ID too long")
        
        return Success(user_id_str)
    
    @staticmethod
    def validate_xp_amount(amount: Any) -> Result[int]:
        """Validate XP amount."""
        try:
            xp = int(amount)
            if xp < 0:
                return Failure("INVALID_XP", "XP cannot be negative")
            if xp > 10000:
                return Failure("INVALID_XP", "XP amount too large")
            return Success(xp)
        except (TypeError, ValueError):
            return Failure("INVALID_XP", "Invalid XP amount")
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """Sanitize user input text."""
        if not text:
            return ""
        
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text

# Global error handler for uncaught exceptions
def setup_global_error_handler():
    """Set up global error handling for the application."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    import sys
    sys.excepthook = handle_exception