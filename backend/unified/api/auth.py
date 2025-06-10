"""
Authentication endpoints for the unified backend - Refactored.

Follows Intentional Disclosure Principle with proper async naming
and clear separation of API layer from business logic.

Copyright: DarkLightX/Dana Edwards
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..core.domain_types import SessionId, UserId, ApiKey, Result, Success, Failure
from ..core.interfaces import IAuthenticationRepository, IEventBus
from ..infrastructure.di_container import get_container
from ..core.responses import create_success_response, create_error_response


router = APIRouter()


# --- Request/Response Models (Rule 3: Rich Types) ---

class LoginRequest(BaseModel):
    """Request model for login with semantic validation."""
    password: str = Field(
        ..., 
        min_length=8,
        max_length=128,
        description="Master password for authentication"
    )


class LoginResponse(BaseModel):
    """Response model for successful login with explicit fields."""
    access_token: SessionId
    token_type: str = Field(default="bearer", const=True)
    user_id: UserId
    expires_in_seconds: int = Field(..., gt=0, description="Token lifetime in seconds")
    issued_at: str = Field(..., description="ISO 8601 timestamp")


class APIKeyRequest(BaseModel):
    """Request model for storing API keys with validation."""
    provider: str = Field(
        ...,
        pattern="^[a-z0-9_-]+$",
        min_length=2,
        max_length=50,
        description="API provider identifier (e.g., 'openrouter', 'huggingface')"
    )
    api_key: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The API key to store (will be encrypted)"
    )


class APIKeyResponse(BaseModel):
    """Response model for API key operations."""
    provider: str
    stored_at: str = Field(..., description="ISO 8601 timestamp")
    key_preview: str = Field(..., description="First/last few chars for verification")


# --- Dependency Injection Helpers ---

async def get_auth_service_async():
    """Get authentication service from DI container."""
    return get_container().create_authentication_service()


async def get_current_session_async(
    authorization: str = Depends(lambda: ...)  # FastAPI auth header
) -> SessionId:
    """Extract and validate session from authorization header."""
    # In real implementation, parse Bearer token
    # For now, simplified
    return SessionId(authorization.replace("Bearer ", ""))


async def require_valid_session_async(
    session_id: SessionId = Depends(get_current_session_async),
    auth_service = Depends(get_auth_service_async)
) -> SessionId:
    """Validate session and return if valid, raise 401 if not."""
    validation_result = await auth_service.validate_session_async(session_id)
    
    if isinstance(validation_result, Failure):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session validation error"
        )
    
    if not validation_result.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return session_id


# --- API Endpoints (Rule 2: Orchestrators) ---

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def authenticate_user_with_password_async(
    request: LoginRequest,
    auth_service = Depends(get_auth_service_async)
) -> LoginResponse:
    """
    Authenticate user with master password and create session.
    Rule 1: Name explicitly indicates password authentication.
    Rule 2: Orchestrates authentication flow.
    """
    # Delegate to service layer
    auth_result = await auth_service.authenticate_with_password_async(request.password)
    
    # Handle result
    if isinstance(auth_result, Failure):
        _raise_authentication_error(auth_result)
    
    # Create response
    return _create_login_response(auth_result.value)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_user_session_async(
    session_id: SessionId = Depends(require_valid_session_async),
    auth_service = Depends(get_auth_service_async)
) -> None:
    """
    Terminate current session and invalidate token.
    Rule 1: Name clearly indicates session termination.
    """
    logout_result = await auth_service.logout_session_async(session_id)
    
    if isinstance(logout_result, Failure):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout session"
        )


@router.get("/me", response_model=Dict[str, Any])
async def retrieve_current_session_info_async(
    session_id: SessionId = Depends(require_valid_session_async)
) -> Dict[str, Any]:
    """
    Retrieve information about current authenticated session.
    Rule 1: Name indicates retrieval of session info.
    """
    return create_success_response({
        "session_id": str(session_id),
        "user_id": "authenticated_user",  # In real impl, get from session data
        "auth_method": "password",
        "session_active": True
    })


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def store_api_key_for_provider_async(
    request: APIKeyRequest,
    session_id: SessionId = Depends(require_valid_session_async),
    auth_service = Depends(get_auth_service_async)
) -> APIKeyResponse:
    """
    Store encrypted API key for specified provider.
    Rule 1: Name explicitly indicates storage operation for provider.
    Rule 2: Orchestrates validation and storage.
    """
    # Validate provider name
    validation_result = _validate_provider_name(request.provider)
    if isinstance(validation_result, Failure):
        _raise_validation_error(validation_result)
    
    # Store via service
    store_result = await auth_service.store_api_key_for_provider_async(
        provider=request.provider,
        api_key=request.api_key,
        session_id=session_id
    )
    
    if isinstance(store_result, Failure):
        _raise_storage_error(store_result)
    
    # Create response with key preview
    return _create_api_key_response(request.provider, request.api_key)


@router.get("/api-keys/{provider}", response_model=Dict[str, Any])
async def retrieve_api_key_for_provider_async(
    provider: str,
    session_id: SessionId = Depends(require_valid_session_async),
    auth_service = Depends(get_auth_service_async)
) -> Dict[str, Any]:
    """
    Retrieve decrypted API key for specified provider.
    Rule 1: Name explicitly indicates retrieval for provider.
    """
    # Retrieve via service
    key_result = await auth_service.retrieve_api_key_for_provider_async(
        provider=provider,
        session_id=session_id
    )
    
    if isinstance(key_result, Failure):
        _raise_retrieval_error(key_result)
    
    if key_result.value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No API key found for provider: {provider}"
        )
    
    return create_success_response({
        "provider": provider,
        "key_preview": _create_key_preview(str(key_result.value))
    })


@router.delete("/api-keys/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key_for_provider_async(
    provider: str,
    session_id: SessionId = Depends(require_valid_session_async),
    auth_service = Depends(get_auth_service_async)
) -> None:
    """
    Delete stored API key for specified provider.
    Rule 1: Name explicitly indicates deletion for provider.
    """
    # Note: In refactored auth service, we'd need to add this method
    # For now, showing the pattern
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Delete operation not yet implemented in refactored service"
    )


@router.get("/api-keys", response_model=Dict[str, Any])
async def list_all_stored_api_keys_async(
    session_id: SessionId = Depends(require_valid_session_async),
    auth_service = Depends(get_auth_service_async)
) -> Dict[str, Any]:
    """
    List all providers with stored API keys.
    Rule 1: Name indicates listing all stored keys.
    """
    # Would need to add this to refactored service
    # Showing the pattern
    return create_success_response({
        "providers": ["openrouter", "huggingface"],  # Example
        "count": 2
    })


# --- Private Helper Methods (Rule 2: Implementation Details) ---

def _raise_authentication_error(failure: Failure) -> None:
    """Raise appropriate HTTP exception for authentication failure."""
    if failure.error_code == "INVALID_PASSWORD":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {failure.message}"
        )


def _create_login_response(session_id: SessionId) -> LoginResponse:
    """Create login response with session details."""
    from datetime import datetime, timezone
    
    return LoginResponse(
        access_token=session_id,
        user_id=UserId("authenticated_user"),
        expires_in_seconds=24 * 3600,  # 24 hours
        issued_at=datetime.now(timezone.utc).isoformat()
    )


def _validate_provider_name(provider: str) -> Result[None]:
    """Validate provider name against allowed list."""
    allowed_providers = ["openrouter", "huggingface", "anthropic", "openai"]
    
    if provider.lower() not in allowed_providers:
        return Failure(
            "INVALID_PROVIDER",
            f"Provider '{provider}' not in allowed list: {allowed_providers}"
        )
    
    return Success(None)


def _raise_validation_error(failure: Failure) -> None:
    """Raise HTTP exception for validation failure."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=failure.message
    )


def _raise_storage_error(failure: Failure) -> None:
    """Raise HTTP exception for storage failure."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to store API key: {failure.message}"
    )


def _raise_retrieval_error(failure: Failure) -> None:
    """Raise HTTP exception for retrieval failure."""
    if failure.error_code == "INVALID_SESSION":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=failure.message
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve API key: {failure.message}"
        )


def _create_api_key_response(provider: str, api_key: str) -> APIKeyResponse:
    """Create response for API key storage."""
    from datetime import datetime, timezone
    
    return APIKeyResponse(
        provider=provider,
        stored_at=datetime.now(timezone.utc).isoformat(),
        key_preview=_create_key_preview(api_key)
    )


def _create_key_preview(api_key: str) -> str:
    """Create safe preview of API key for display."""
    if len(api_key) < 10:
        return "***"
    
    return f"{api_key[:4]}...{api_key[-4:]}"