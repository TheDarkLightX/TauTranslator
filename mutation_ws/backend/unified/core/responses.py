"""
Standardized response utilities for the unified backend.

Provides consistent JSON response formats and error handling.

Author: DarkLightX / Dana Edwards
"""

from typing import Any, Optional, Dict, List, Union
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import traceback
import logging

logger = logging.getLogger(__name__)


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    success: bool
    timestamp: datetime = datetime.utcnow()
    message: Optional[str] = None


class SuccessResponse(BaseResponse):
    """Standard success response."""
    success: bool = True
    data: Optional[Any] = None


class ErrorResponse(BaseResponse):
    """Standard error response."""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class TranslationResponse(BaseResponse):
    """Response for translation requests."""
    success: bool = True
    source_text: str
    translated_text: str
    translation_method: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ValidationResponse(BaseResponse):
    """Response for validation requests."""
    success: bool = True
    is_valid: bool
    issues: List[Dict[str, Any]] = []
    suggestions: List[str] = []


class HealthResponse(BaseResponse):
    """Health check response."""
    success: bool = True
    status: str = "healthy"
    services: Dict[str, str] = {}
    uptime: Optional[float] = None


def create_success_response(
    data: Any = None, 
    message: str = "Success",
    status_code: int = 200
) -> JSONResponse:
    """Create a standardized success response."""
    response = SuccessResponse(data=data, message=message)
    return JSONResponse(
        content=response.dict(),
        status_code=status_code
    )


def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> JSONResponse:
    """Create a standardized error response."""
    response = ErrorResponse(
        message=message,
        error_code=error_code,
        details=details
    )
    return JSONResponse(
        content=response.dict(),
        status_code=status_code
    )


def create_translation_response(
    source_text: str,
    translated_text: str,
    translation_method: str,
    confidence: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    message: str = "Translation completed successfully"
) -> JSONResponse:
    """Create a translation response."""
    response = TranslationResponse(
        message=message,
        source_text=source_text,
        translated_text=translated_text,
        translation_method=translation_method,
        confidence=confidence,
        metadata=metadata
    )
    return JSONResponse(content=response.dict())


def create_validation_response(
    is_valid: bool,
    issues: List[Dict[str, Any]] = None,
    suggestions: List[str] = None,
    message: str = "Validation completed"
) -> JSONResponse:
    """Create a validation response."""
    response = ValidationResponse(
        message=message,
        is_valid=is_valid,
        issues=issues or [],
        suggestions=suggestions or []
    )
    return JSONResponse(content=response.dict())


class TauTranslatorException(Exception):
    """Base exception for TauTranslator backend."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.details = details
        self.status_code = status_code
        super().__init__(message)


class TranslationError(TauTranslatorException):
    """Translation-specific error."""
    
    def __init__(self, message: str, translation_method: str = None, **kwargs):
        super().__init__(message, error_code="TRANSLATION_ERROR", **kwargs)
        if translation_method:
            self.details = self.details or {}
            self.details["translation_method"] = translation_method


class AuthenticationError(TauTranslatorException):
    """Authentication-related error."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message, 
            error_code="AUTH_ERROR", 
            status_code=401,
            **kwargs
        )


class ValidationError(TauTranslatorException):
    """Validation-related error."""
    
    def __init__(self, message: str, validation_issues: List[str] = None, **kwargs):
        super().__init__(
            message, 
            error_code="VALIDATION_ERROR", 
            status_code=422,
            **kwargs
        )
        if validation_issues:
            self.details = self.details or {}
            self.details["validation_issues"] = validation_issues


class ConfigurationError(TauTranslatorException):
    """Configuration-related error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message, 
            error_code="CONFIG_ERROR", 
            status_code=500,
            **kwargs
        )


def handle_exception(exc: Exception) -> JSONResponse:
    """Handle exceptions and return appropriate error responses."""
    if isinstance(exc, TauTranslatorException):
        return create_error_response(
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details,
            status_code=exc.status_code
        )
    elif isinstance(exc, HTTPException):
        return create_error_response(
            message=exc.detail,
            error_code="HTTP_ERROR",
            status_code=exc.status_code
        )
    else:
        # Log unexpected errors
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        
        # In debug mode, include traceback
        details = None
        try:
            from .config import settings
            if settings.debug:
                details = {"traceback": traceback.format_exc()}
        except:
            pass
        
        return create_error_response(
            message="An unexpected error occurred",
            error_code="INTERNAL_ERROR",
            details=details,
            status_code=500
        )


# User-friendly error messages
FRIENDLY_ERROR_MESSAGES = {
    "TRANSLATION_ERROR": "We couldn't translate your text. Please check the input and try again.",
    "AUTH_ERROR": "Please check your authentication credentials and try again.",
    "VALIDATION_ERROR": "The input doesn't look quite right. Please check and try again.",
    "CONFIG_ERROR": "There's a configuration issue. Please contact support.",
    "INTERNAL_ERROR": "Something went wrong on our end. Please try again later.",
    "HTTP_ERROR": "There was a problem with your request. Please check and try again."
}


def get_friendly_message(error_code: str, original_message: str) -> str:
    """Get a user-friendly error message."""
    return FRIENDLY_ERROR_MESSAGES.get(error_code, original_message)