# Copyright (c) DarkLightX / Dana Edwards

"""
Authentication service for TauTranslator.
Handles secure storage initialization, API key management, and user authentication.
"""

import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from returns.result import Result, Success, Failure

# Project-specific imports
try:
    from backend.security.secure_core import SecureStorage, CRYPTO_AVAILABLE
    from backend.api_models import ProviderInfo
    from backend.config.provider_config import provider_config
except ImportError as e:
    # This block allows the module to be imported but functionality will be limited.
    logging.warning(f"Could not import dependencies for AuthService: {e}. Functionality will be impaired.")
    SecureStorage = None
    CRYPTO_AVAILABLE = False
    ProviderConfig = None
    provider_config = None

logger = logging.getLogger(__name__)

# --- Custom Error Types ---

class AuthServiceError(Exception):
    """Base class for authentication service errors."""
    pass

class StorageInitializationError(AuthServiceError):
    """Represents an error during storage initialization."""
    pass

class EncryptionSetupError(StorageInitializationError):
    """Error during the first-time encryption setup."""
    pass

class StorageUnlockError(StorageInitializationError):
    """Error when attempting to unlock existing storage (e.g., wrong password)."""
    pass

class SessionError(AuthServiceError):
    """Base class for session-related errors."""
    pass

class InvalidSessionTokenError(SessionError):
    """Raised when a session token is invalid or expired."""
    pass

# --- Service Class ---

class AuthService:
    """
    Manages authentication, session tokens, and secure API key storage.
    Follows the Intentional Disclosure Principle for method naming and structure.
    """
    _SESSION_EXPIRATION_MINUTES = 60

    def __init__(self):
        self.storage: Optional[SecureStorage] = None
        self.authenticated_sessions: Dict[str, datetime] = {}

    # --- Orchestrator Method ---

    async def initialize_storage_with_password_and_create_session(self, password: str) -> Result[str, AuthServiceError]:
        """Orchestrator to initialize storage and create a new session."""
        storage_result = self._initialize_secure_storage_from_password(password)

        if isinstance(storage_result, Failure):
            return storage_result  # Propagate the failure

        self.storage = storage_result.unwrap()
        session_token = self._create_new_session_token()
        logger.info(f"New session created. Token will expire at {self.authenticated_sessions[session_token]}.")
        return Success(session_token)

    # --- Implementation Details ---

    def _initialize_secure_storage_from_password(self, password: str) -> Result[SecureStorage, StorageInitializationError]:
        """Initializes or unlocks the secure storage."""
        if SecureStorage is None:
            logger.error("SecureStorage class not found. Ensure 'secure_core.py' is correctly placed.")
            return Failure(StorageInitializationError("SecureStorage component is not available."))

        master_password_hash = os.environ.get("TAUTRANSLATOR_MASTER_PASSWORD_HASH")
        if not master_password_hash:
            logger.critical("TAUTRANSLATOR_MASTER_PASSWORD_HASH environment variable not set.")
            return Failure(StorageInitializationError("Server is not configured with a master password hash."))

        try:
            storage = SecureStorage(master_password_hash=master_password_hash)
            if storage.is_first_time():
                logger.info("Performing first-time setup for secure storage.")
                setup_success = storage.setup_encryption(password)
                if setup_success:
                    logger.info("Secure storage encryption setup successful.")
                    return Success(storage)
                else:
                    logger.error("Failed to setup encryption for secure storage.")
                    return Failure(EncryptionSetupError("Failed to setup encryption."))
            else:
                logger.info("Attempting to unlock existing secure storage.")
                unlock_success = storage.unlock_with_password(password)
                if unlock_success:
                    logger.info("Secure storage unlocked successfully.")
                    return Success(storage)
                else:
                    logger.warning("Failed to unlock secure storage. Incorrect password or corrupted storage.")
                    return Failure(StorageUnlockError("Failed to unlock storage. Incorrect password?"))
        except Exception as e:
            logger.exception(f"An unexpected error occurred during storage initialization: {e}")
            return Failure(StorageInitializationError(f"Unexpected error: {str(e)}"))

    def _create_new_session_token(self) -> str:
        """Generates and stores a new secure session token."""
        session_token = secrets.token_hex(32)
        expires_at = datetime.utcnow() + timedelta(minutes=self._SESSION_EXPIRATION_MINUTES)
        self.authenticated_sessions[session_token] = expires_at
        return session_token

    def validate_session(self, token: Optional[str]) -> Result[None, InvalidSessionTokenError]:
        """Validates a session token, checking for existence and expiration."""
        if not token or token not in self.authenticated_sessions:
            return Failure(InvalidSessionTokenError("Session token is invalid."))

        if datetime.utcnow() > self.authenticated_sessions[token]:
            del self.authenticated_sessions[token]
            return Failure(InvalidSessionTokenError("Session token has expired."))

        return Success(None)

    async def get_configured_providers(self) -> Result[List[ProviderInfo], AuthServiceError]:
        """Retrieves the configuration status of all providers."""
        if not self.storage or not provider_config:
            return Failure(AuthServiceError("Service or configuration not initialized."))
        
        provider_list = provider_config.get_all_providers()
        keys = self.storage.get_all_api_keys()
        
        response = [
            ProviderInfo(
                id=p_id,
                name=p_data['name'],
                is_configured=p_id in keys
            ) for p_id, p_data in provider_list.items()
        ]
        return Success(response)

    async def set_api_key_for_provider(self, provider_id: str, api_key: str) -> Result[None, AuthServiceError]:
        """Stores an API key for a given provider in secure storage."""
        if not self.storage:
            return Failure(AuthServiceError("Storage not initialized."))
        
        self.storage.set_api_key(provider_id, api_key)
        logger.info(f"API key for provider '{provider_id}' has been set.")
        return Success(None)

    async def remove_api_key_for_provider(self, provider_id: str) -> Result[None, AuthServiceError]:
        """Removes an API key for a given provider from secure storage."""
        if not self.storage:
            return Failure(AuthServiceError("Storage not initialized."))
        
        self.storage.remove_api_key(provider_id)
        logger.info(f"API key for provider '{provider_id}' has been removed.")
        return Success(None)
