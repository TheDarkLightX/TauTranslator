"""
Authentication Service - Refactored with Clean Architecture.
Pure business logic with no I/O operations (Rule 4).

Copyright: DarkLightX/Dana Edwards
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

from .domain_types import (
    UserId, SessionId, ApiKey, Result, Success, Failure
)
from .interfaces import IAuthenticationRepository, IEventBus


class AuthenticationService:
    """
    Core authentication service with pure business logic.
    All I/O operations delegated to repositories following Rule 4.
    """
    
    def __init__(
        self,
        auth_repository: IAuthenticationRepository,
        event_bus: IEventBus,
        master_password: Optional[str] = None,
        session_expire_hours: int = 24
    ):
        """Initialize with injected dependencies."""
        self._auth_repo = auth_repository
        self._event_bus = event_bus
        self._master_password = master_password
        self._session_expire_hours = session_expire_hours
        self.logger = logging.getLogger(__name__)
    
    async def authenticate_with_password_async(self, password: str) -> Result[SessionId]:
        """
        Authenticate user with master password.
        Rule 1: Name explicitly indicates async authentication operation.
        Rule 2: Orchestrator pattern delegating to private methods.
        """
        # Validate password
        validation_result = self._validate_master_password(password)
        if isinstance(validation_result, Failure):
            await self._publish_auth_event("authentication_failed", {"reason": "invalid_password"})
            return validation_result
        
        # Create new session
        session_id = self._generate_session_id()
        session_data = self._create_session_data()
        
        # Store session via repository
        save_result = await self._auth_repo.save_session_async(session_id, session_data)
        if isinstance(save_result, Failure):
            return save_result
        
        # Publish success event
        await self._publish_auth_event(
            "authentication_success",
            {"session_id": str(session_id), "expires_at": session_data["expires_at"]}
        )
        
        return Success(session_id)
    
    async def validate_session_async(self, session_id: SessionId) -> Result[bool]:
        """
        Validate if a session is active and not expired.
        Returns Success(True) if valid, Success(False) if invalid/expired.
        """
        # Load all sessions from repository
        sessions_result = await self._auth_repo.load_sessions_async()
        if isinstance(sessions_result, Failure):
            return sessions_result
        
        sessions = sessions_result.value
        
        # Check if session exists
        if session_id not in sessions:
            return Success(False)
        
        # Check expiration
        session_data = sessions[session_id]
        is_valid = self._is_session_valid(session_data)
        
        if not is_valid:
            # Clean up expired session
            await self._auth_repo.delete_session_async(session_id)
            await self._publish_auth_event("session_expired", {"session_id": str(session_id)})
        
        return Success(is_valid)
    
    async def logout_session_async(self, session_id: SessionId) -> Result[None]:
        """
        Logout and invalidate a session.
        Rule 1: Explicit async operation naming.
        """
        delete_result = await self._auth_repo.delete_session_async(session_id)
        
        if isinstance(delete_result, Success):
            await self._publish_auth_event("session_logout", {"session_id": str(session_id)})
        
        return delete_result
    
    async def store_api_key_for_provider_async(
        self,
        provider: str,
        api_key: str,
        session_id: SessionId
    ) -> Result[None]:
        """
        Store an API key for a provider after session validation.
        Rule 1: Name clearly indicates storage operation for provider.
        """
        # Validate session first
        validation_result = await self.validate_session_async(session_id)
        if isinstance(validation_result, Failure):
            return validation_result
        
        if not validation_result.value:
            return Failure("INVALID_SESSION", "Session is invalid or expired")
        
        # Store API key
        store_result = await self._auth_repo.save_api_key_async(provider, ApiKey(api_key))
        
        if isinstance(store_result, Success):
            await self._publish_auth_event(
                "api_key_stored",
                {"provider": provider, "session_id": str(session_id)}
            )
        
        return store_result
    
    async def retrieve_api_key_for_provider_async(
        self,
        provider: str,
        session_id: SessionId
    ) -> Result[Optional[ApiKey]]:
        """
        Retrieve an API key for a provider after session validation.
        Rule 1: Name clearly indicates retrieval operation for provider.
        """
        # Validate session first
        validation_result = await self.validate_session_async(session_id)
        if isinstance(validation_result, Failure):
            return validation_result
        
        if not validation_result.value:
            return Failure("INVALID_SESSION", "Session is invalid or expired")
        
        # Load API keys
        keys_result = await self._auth_repo.load_api_keys_async()
        if isinstance(keys_result, Failure):
            return keys_result
        
        api_keys = keys_result.value
        api_key = api_keys.get(provider)
        
        return Success(api_key)
    
    async def clean_expired_sessions_async(self) -> Result[int]:
        """
        Clean up all expired sessions.
        Returns number of sessions cleaned.
        """
        sessions_result = await self._auth_repo.load_sessions_async()
        if isinstance(sessions_result, Failure):
            return sessions_result
        
        sessions = sessions_result.value
        expired_count = 0
        
        for session_id, session_data in list(sessions.items()):
            if not self._is_session_valid(session_data):
                await self._auth_repo.delete_session_async(session_id)
                expired_count += 1
        
        if expired_count > 0:
            await self._publish_auth_event(
                "sessions_cleaned",
                {"count": expired_count}
            )
        
        return Success(expired_count)
    
    # --- Private Implementation Methods (Rule 2) ---
    
    def _validate_master_password(self, password: str) -> Result[None]:
        """Validate the provided password against master password."""
        if not self._master_password:
            return Failure("NO_MASTER_PASSWORD", "No master password configured")
        
        if not self._is_password_match(password, self._master_password):
            return Failure("INVALID_PASSWORD", "Invalid password")
        
        return Success(None)
    
    def _is_password_match(self, provided: str, stored: str) -> bool:
        """Securely compare passwords using constant-time comparison."""
        provided_hash = hashlib.sha256(provided.encode()).hexdigest()
        stored_hash = hashlib.sha256(stored.encode()).hexdigest()
        return secrets.compare_digest(provided_hash, stored_hash)
    
    def _generate_session_id(self) -> SessionId:
        """Generate a secure random session ID."""
        return SessionId(secrets.token_urlsafe(32))
    
    def _create_session_data(self) -> Dict[str, Any]:
        """Create session data with expiration."""
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self._session_expire_hours)
        
        return {
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_accessed": now.isoformat()
        }
    
    def _is_session_valid(self, session_data: Dict[str, Any]) -> bool:
        """Check if session data indicates a valid, non-expired session."""
        try:
            expires_at_str = session_data.get("expires_at")
            if not expires_at_str:
                return False
            
            expires_at = datetime.fromisoformat(expires_at_str)
            return datetime.utcnow() < expires_at
            
        except (ValueError, TypeError):
            return False
    
    async def _publish_auth_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish authentication-related events."""
        await self._event_bus.publish_event_async(f"auth.{event_type}", data)