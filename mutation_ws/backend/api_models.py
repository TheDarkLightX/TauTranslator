# Copyright (c) DarkLightX / Dana Edwards

"""
Defines the Pydantic models used for API request and response validation.
These models serve as the data contracts for the FastAPI application.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

# --- Authentication Models ---

class AuthRequest(BaseModel):
    """Request model for user authentication."""
    master_password: str = Field(..., description="The master password for the backend.")

class AuthResponse(BaseModel):
    """Response model for successful authentication, providing a session token."""
    access_token: str = Field(..., description="The JWT session token.")
    token_type: str = Field(default="bearer", description="The type of the token.")

# --- Translation Models ---

class TranslationRequest(BaseModel):
    """Request model for a translation task."""
    text: str = Field(..., description="The source text to be translated.")
    source_lang: str = Field(..., alias="sourceLangKey", description="The key for the source language (e.g., 'PLAIN_ENGLISH').")
    target_lang: str = Field(..., alias="targetLangKey", description="The key for the target language (e.g., 'TAU').")
    provider: Optional[str] = Field(default="default", description="The specific translation provider to use (e.g., 'openai', 'anthropic'). 'default' uses internal engines.")

class TranslationResponse(BaseModel):
    """Response model for a completed translation task."""
    translated_text: str = Field(..., alias="translatedText", description="The resulting translated text.")
    provider: str = Field(..., description="The provider that performed the translation.")
    model: Optional[str] = Field(None, description="The specific model used for the translation, if applicable.")
    processing_time: Optional[float] = Field(None, alias="processingTime", description="The time taken for the translation in seconds.")

# --- Provider and API Key Models ---

class ProviderInfo(BaseModel):
    """Model representing information about a configured translation provider."""
    id: str
    name: str
    is_configured: bool = Field(..., description="True if the API key for this provider is configured.")

class APIKeyRequest(BaseModel):
    """Request model for adding or updating an API key."""
    provider_id: str = Field(..., description="The unique identifier for the provider (e.g., 'openai').")
    api_key: str = Field(..., alias="apiKey", description="The API key to be stored securely.")

class APIKeyResponse(BaseModel):
    """Standard response for API key operations."""
    message: str
    success: bool

# --- Health Check Models ---

class EngineStatus(BaseModel):
    """Represents the status of a single translation engine."""
    name: str
    available: bool
    details: Optional[str] = None

class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""
    status: str
    secure_storage_available: bool
    crypto_available: bool
    configured_providers: List[str]
    engine_statuses: List[EngineStatus]
