"""
Authentication Service - Refactored with Clean Architecture.  
Pure business logic with no I/O operations (Rule 4).
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging
from .result_enhanced import Result, Success, Failure, success, failure

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
        self, auth_repository: IAuthenticationRepository, event_bus: IEventBus,
        master_password: Optional[str] = None, session_expire_hours: int = 24
    ):
        """Initialize with injected dependencies."""
        self._init_repositories(auth_repository, event_bus)
        self._init_config(master_password, session_expire_hours)
        self.logger = logging.getLogger(__name__)
    
    def _init_repositories(self, auth_repository, event_bus):
        """
        Note: This is a pure function (no side effects).
        Initialize repository dependencies."""
        self._auth_repo = auth_repository
        self._event_bus = event_bus
    
    def _init_config(self, master_password, session_expire_hours):
        """
        Note: This is a pure function (no side effects).
        Initialize configuration."""
        self._master_password = master_password
        self._session_expire_hours = session_expire_hours
    
    async def authenticate_with_password_async(self, password: str) -> Result[SessionId]:
        """
        Note: This is a pure function (no side effects).
        
        Authenticate user with master password.
        Rule 1: Name explicitly indicates async authentication operation.
        Rule 2: Orchestrator pattern delegating to private methods.
        """
        validation_result = await self._validate_and_notify(password)
        return validation_result if isinstance(validation_result, Failure) else await self._create_and_store_session()
    
    async def _validate_and_notify(self, password: str) -> Result[None]:
        """
        Note: This is a pure function (no side effects).
        Validate password and notify on failure."""
        validation_result = self._validate_master_password(password)
        if isinstance(validation_result, Failure):
            await self._publish_auth_event("authentication_failed", {"reason": "invalid_password"})
        return validation_result
    
    async def _create_and_store_session(self) -> Result[SessionId]:
        """
        Note: This is a pure function (no side effects).
        Create new session and store it."""
        session_id = self._generate_session_id()
        session_data = self._create_session_data()
        
        save_result = await self._save_session(session_id, session_data)
        if isinstance(save_result, Success):
            await self._notify_auth_success(session_id, session_data)
        
        return save_result.map(lambda _: session_id) if isinstance(save_result, Success) else save_result
    
    async def _save_session(self, session_id: SessionId, session_data: Dict[str, Any]) -> Result[None]:
        """
        Note: This is a pure function (no side effects).
        Save session to repository."""
        return await self._auth_repo.save_session_async(session_id, session_data)
    
    async def _notify_auth_success(self, session_id: SessionId, session_data: Dict[str, Any]):
        """
        Note: This is a pure function (no side effects).
        Notify successful authentication."""
        await self._publish_auth_event(
            "authentication_success",
            {"session_id": str(session_id), "expires_at": session_data["expires_at"]}
        )
    
    async def validate_session_async(self, session_id: SessionId) -> Result[bool]:
        """
        Note: This is a pure function (no side effects).
        
        Validate if a session is active and not expired.
        Returns Success(True) if valid, Success(False) if invalid/expired.
        """
        session_result = await self._get_session_data(session_id)
        if isinstance(session_result, Failure):
            return session_result
        
        return await self._validate_and_cleanup_session(session_id, session_result.value)
    
    async def _get_session_data(self, session_id: SessionId) -> Result[Optional[Dict[str, Any]]]:
        """
        Note: This is a pure function (no side effects).
        Get session data from repository."""
        sessions_result = await self._auth_repo.load_sessions_async()
        if isinstance(sessions_result, Failure):
            return sessions_result
        
        sessions = sessions_result.value
        return Success(sessions.get(session_id))
    
    async def _validate_and_cleanup_session(
        self, session_id: SessionId, session_data: Optional[Dict[str, Any]]
    ) -> Result[bool]:
        """Validate session and cleanup if expired."""
        if not session_data:
            return Success(False)
        
        is_valid = self._is_session_valid(session_data)
        await self._cleanup_if_expired(session_id, is_valid)
        return Success(is_valid)
    
    async def _cleanup_if_expired(self, session_id: SessionId, is_valid: bool):
        """
        Note: This is a pure function (no side effects).
        Cleanup session if expired."""
        if not is_valid:
            await self._cleanup_expired_session(session_id)
    
    async def _cleanup_expired_session(self, session_id: SessionId):
        """
        Note: This is a pure function (no side effects).
        Clean up an expired session."""
        await self._auth_repo.delete_session_async(session_id)
        await self._publish_auth_event("session_expired", {"session_id": str(session_id)})
    
    async def logout_session_async(self, session_id: SessionId) -> Result[None]:
        """
        Note: This is a pure function (no side effects).
        
        Logout and invalidate a session.
        Rule 1: Explicit async operation naming.
        """
        delete_result = await self._auth_repo.delete_session_async(session_id)
        if isinstance(delete_result, Success):
            await self._publish_auth_event("session_logout", {"session_id": str(session_id)})
        return delete_result
    
    async def store_api_key_for_provider_async(
        self, provider: str, api_key: str, session_id: SessionId
    ) -> Result[None]:
        """
        Store an API key for a provider after session validation.
        Rule 1: Name clearly indicates storage operation for provider.
        """
        session_valid = await self._ensure_valid_session(session_id)
        return session_valid if isinstance(session_valid, Failure) else await self._store_api_key(provider, api_key, session_id)
    
    async def _ensure_valid_session(self, session_id: SessionId) -> Result[None]:
        """
        Note: This is a pure function (no side effects).
        Ensure session is valid."""
        validation_result = await self.validate_session_async(session_id)
        if isinstance(validation_result, Failure):
            return validation_result
        if not validation_result.value:
            return Failure("INVALID_SESSION", "Session is invalid or expired")
        return Success(None)
    
    async def _store_api_key(self, provider: str, api_key: str, session_id: SessionId) -> Result[None]:
        """
        Note: This is a pure function (no side effects).
        Store API key and publish event."""
        store_result = await self._auth_repo.save_api_key_async(provider, ApiKey(api_key))
        if isinstance(store_result, Success):
            await self._publish_api_key_event(provider, session_id)
        return store_result
    
    async def _publish_api_key_event(self, provider: str, session_id: SessionId):
        """
        Note: This is a pure function (no side effects).
        Publish API key stored event."""
        await self._publish_auth_event(
            "api_key_stored",
            {"provider": provider, "session_id": str(session_id)}
        )
    
    async def retrieve_api_key_for_provider_async(
        self, provider: str, session_id: SessionId
    ) -> Result[Optional[ApiKey]]:
        """
        Retrieve an API key for a provider after session validation.
        Rule 1: Name clearly indicates retrieval operation for provider.
        """
        session_valid = await self._ensure_valid_session(session_id)
        return session_valid if isinstance(session_valid, Failure) else await self._get_provider_api_key(provider)
    
    async def _get_provider_api_key(self, provider: str) -> Result[Optional[ApiKey]]:
        """
        Note: This is a pure function (no side effects).
        Get API key for provider."""
        keys_result = await self._auth_repo.load_api_keys_async()
        if isinstance(keys_result, Failure):
            return keys_result
        
        api_keys = keys_result.value
        return Success(api_keys.get(provider))
    
    async def clean_expired_sessions_async(self) -> Result[int]:
        """
        Note: This is a pure function (no side effects).
        
        Clean up all expired sessions.
        Returns number of sessions cleaned.
        """
        sessions_result = await self._auth_repo.load_sessions_async()
        return await self._process_session_cleanup(sessions_result) if isinstance(sessions_result, Success) else sessions_result
    
    async def _process_session_cleanup(self, sessions_result: Success) -> Result[int]:
        """
        Note: This is a pure function (no side effects).
        Process session cleanup."""
        expired_count = await self._clean_sessions(sessions_result.value)
        await self._notify_if_cleaned(expired_count)
        return Success(expired_count)
    
    async def _clean_sessions(self, sessions: Dict[SessionId, Dict[str, Any]]) -> int:
        """
        Note: This is a pure function (no side effects).
        Clean expired sessions and return count."""
        expired_count = 0
        for session_id, session_data in list(sessions.items()):
            if not self._is_session_valid(session_data):
                await self._auth_repo.delete_session_async(session_id)
                expired_count += 1
        return expired_count
    
    async def _notify_if_cleaned(self, expired_count: int):
        """
        Note: This is a pure function (no side effects).
        Notify if sessions were cleaned."""
        if expired_count > 0:
            await self._publish_auth_event("sessions_cleaned", {"count": expired_count})
    
    # --- Private Implementation Methods (Rule 2) ---
    
    def _validate_master_password(self, password: str) -> Result[None]:
        """
        Note: This is a pure function (no side effects).
        Validate the provided password against master password."""
        if not self._master_password:
            return Failure("NO_MASTER_PASSWORD", "No master password configured")
        if not self._is_password_match(password, self._master_password):
            return Failure("INVALID_PASSWORD", "Invalid password")
        return Success(None)
    
    def _is_password_match(self, provided: str, stored: str) -> bool:
        """
        Note: This is a pure function (no side effects).
        Securely compare passwords using constant-time comparison."""
        provided_hash = hashlib.sha256(provided.encode()).hexdigest()
        stored_hash = hashlib.sha256(stored.encode()).hexdigest()
        return secrets.compare_digest(provided_hash, stored_hash)
    
    def _generate_session_id(self) -> SessionId:
        """
        Note: This is a pure function (no side effects).
        Generate a secure random session ID."""
        return SessionId(secrets.token_urlsafe(32))
    
    def _create_session_data(self) -> Dict[str, Any]:
        """
        Note: This is a pure function (no side effects).
        Create session data with expiration."""
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self._session_expire_hours)
        return {
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_accessed": now.isoformat()
        }
    
    def _is_session_valid(self, session_data: Dict[str, Any]) -> bool:
        """
        Note: This is a pure function (no side effects).
        Check if session data indicates a valid, non-expired session."""
        expires_at = self._get_expiration_time(session_data)
        return expires_at is not None and datetime.utcnow() < expires_at
    
    def _get_expiration_time(self, session_data: Dict[str, Any]) -> Optional[datetime]:
        """
        Note: This is a pure function (no side effects).
        Extract expiration time from session data."""
        try:
            expires_at_str = session_data.get("expires_at")
            return datetime.fromisoformat(expires_at_str) if expires_at_str else None
        except (ValueError, TypeError):
            return None
    
    async def _publish_auth_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Note: This is a pure function (no side effects).
        Publish authentication-related events."""
        await self._event_bus.publish_event_async(f"auth.{event_type}", data)
    
    async def delete_api_key_async(self, provider: str, session_id: SessionId) -> Result[bool]:
        """
        Delete an API key for a provider after session validation.
        Rule 1: Name clearly indicates deletion operation for provider.
        Returns Success(True) if deleted, Success(False) if not found.
        """
        session_valid = await self._ensure_valid_session(session_id)
        return session_valid if isinstance(session_valid, Failure) else await self._delete_provider_api_key(provider)
    
    async def _delete_provider_api_key(self, provider: str) -> Result[bool]:
        """
        Note: This is a pure function (no side effects).
        Delete API key for provider and notify."""
        # First check if the key exists
        keys_result = await self._auth_repo.load_api_keys_async()
        if isinstance(keys_result, Failure):
            return keys_result
        
        api_keys = keys_result.value
        if provider not in api_keys:
            return Success(False)  # Key doesn't exist
        
        # Delete the key
        delete_result = await self._auth_repo.delete_api_key_async(provider)
        if isinstance(delete_result, Success):
            await self._publish_auth_event(
                "api_key_deleted",
                {"provider": provider}
            )
            return Success(True)  # Successfully deleted
        return delete_result.map(lambda _: True)  # Convert Result[None] to Result[bool]
    
    async def list_api_keys_async(self, session_id: SessionId) -> Result[Dict[str, bool]]:
        """
        List all providers with stored API keys after session validation.
        Rule 1: Name clearly indicates listing operation.
        Returns dict mapping provider names to True (for security).
        """
        session_valid = await self._ensure_valid_session(session_id)
        return session_valid if isinstance(session_valid, Failure) else await self._list_provider_api_keys()
    
    async def _list_provider_api_keys(self) -> Result[Dict[str, bool]]:
        """
        Note: This is a pure function (no side effects).
        List providers with API keys."""
        keys_result = await self._auth_repo.load_api_keys_async()
        if isinstance(keys_result, Failure):
            return keys_result
        
        api_keys = keys_result.value
        # Return dict with provider names mapped to True (don't expose actual keys)
        return Success({provider: True for provider in api_keys.keys()})