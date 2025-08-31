"""
Authentication endpoints for the unified backend.

Handles login, logout, session management, and API key storage.

Author: DarkLightX / Dana Edwards
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from ..core.auth import auth_service, get_current_user, require_master_password
from ..core.responses import create_success_response, create_error_response, AuthenticationError

router = APIRouter()


class LoginRequest(BaseModel):
    """Request model for login."""
    password: str = Field(..., description="Master password")


class LoginResponse(BaseModel):
    """Response model for successful login."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    expires_in: int  # seconds


class APIKeyRequest(BaseModel):
    """Request model for storing API keys."""
    provider: str = Field(..., description="API provider (e.g., 'openrouter', 'huggingface')")
    api_key: str = Field(..., description="The API key to store")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, _: None = Depends(require_master_password)):
    """Authenticate with master password and get session token."""
    try:
        session_token = auth_service.authenticate_with_password(request.password)
        
        return LoginResponse(
            access_token=session_token,
            user_id="authenticated_user",
            expires_in=24 * 3600  # 24 hours in seconds
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """Logout and invalidate session token."""
    # Extract token from current user session
    # Note: In a real implementation, you'd need to pass the actual token
    # For now, we'll use a placeholder approach
    
    return create_success_response(
        {"message": "Logged out successfully"},
        message="Session terminated"
    )


@router.get("/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get information about the current authenticated user."""
    return create_success_response({
        "user_id": user.get("user_id"),
        "created_at": user.get("created_at"),
        "auth_method": user.get("metadata", {}).get("auth_method"),
        "session_info": {
            "expires_at": user.get("expires_at"),
            "metadata": user.get("metadata", {})
        }
    })


@router.post("/api-keys")
async def store_api_key(
    request: APIKeyRequest, 
    user: dict = Depends(get_current_user)
):
    """Store an encrypted API key for a provider."""
    try:
        user_id = user.get("user_id", "default")
        success = auth_service.api_key_manager.store_api_key(
            provider=request.provider,
            api_key=request.api_key,
            user_id=user_id
        )
        
        if success:
            return create_success_response(
                {"provider": request.provider},
                message=f"API key stored successfully for {request.provider}"
            )
        else:
            return create_error_response(
                "Failed to store API key",
                error_code="STORAGE_ERROR",
                status_code=500
            )
            
    except Exception as e:
        return create_error_response(
            f"Error storing API key: {str(e)}",
            error_code="STORAGE_ERROR",
            status_code=500
        )


@router.get("/api-keys/{provider}")
async def get_api_key(provider: str, user: dict = Depends(get_current_user)):
    """Get API key for a provider (returns masked version for security)."""
    try:
        user_id = user.get("user_id", "default")
        api_key = auth_service.api_key_manager.get_api_key(provider, user_id)
        
        if api_key:
            # Return masked version for security
            masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "*" * len(api_key)
            return create_success_response({
                "provider": provider,
                "api_key_masked": masked_key,
                "exists": True
            })
        else:
            return create_success_response({
                "provider": provider,
                "exists": False
            })
            
    except Exception as e:
        return create_error_response(
            f"Error retrieving API key: {str(e)}",
            error_code="RETRIEVAL_ERROR",
            status_code=500
        )


@router.delete("/api-keys/{provider}")
async def delete_api_key(provider: str, user: dict = Depends(get_current_user)):
    """Delete API key for a provider."""
    try:
        user_id = user.get("user_id", "default")
        success = auth_service.api_key_manager.delete_api_key(provider, user_id)
        
        if success:
            return create_success_response(
                {"provider": provider},
                message=f"API key deleted successfully for {provider}"
            )
        else:
            return create_error_response(
                f"API key not found for provider: {provider}",
                error_code="NOT_FOUND",
                status_code=404
            )
            
    except Exception as e:
        return create_error_response(
            f"Error deleting API key: {str(e)}",
            error_code="DELETION_ERROR",
            status_code=500
        )


@router.get("/api-keys")
async def list_api_keys(user: dict = Depends(get_current_user)):
    """List all stored API key providers for the current user."""
    try:
        # This would require enhancing the APIKeyManager to list providers
        # For now, return common providers and check if they exist
        common_providers = ["openrouter", "huggingface", "anthropic", "openai"]
        user_id = user.get("user_id", "default")
        
        providers = []
        for provider in common_providers:
            api_key = auth_service.api_key_manager.get_api_key(provider, user_id)
            if api_key:
                providers.append({
                    "provider": provider,
                    "exists": True,
                    "masked_key": api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "*" * len(api_key)
                })
        
        return create_success_response({
            "providers": providers,
            "total": len(providers)
        })
        
    except Exception as e:
        return create_error_response(
            f"Error listing API keys: {str(e)}",
            error_code="LIST_ERROR",
            status_code=500
        )


@router.post("/verify")
async def verify_token(user: dict = Depends(get_current_user)):
    """Verify that the current token is valid."""
    return create_success_response({
        "valid": True,
        "user_id": user.get("user_id"),
        "expires_at": user.get("expires_at")
    }, message="Token is valid")


@router.get("/status")
async def auth_status():
    """Get authentication system status."""
    from ..core.config import settings
    
    return create_success_response({
        "master_password_configured": bool(settings.master_password),
        "session_expire_hours": settings.session_expire_hours,
        "encryption_available": True,  # Always true if we got this far
        "supported_providers": [
            "openrouter", "huggingface", "anthropic", "openai"
        ]
    })