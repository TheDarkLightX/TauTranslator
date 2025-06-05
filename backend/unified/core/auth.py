"""
Unified authentication system for the TauTranslator backend.

Consolidates authentication from all backend variants into a single system.

Author: DarkLightX / Dana Edwards
"""

import os
import json
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from .config import settings
from .responses import AuthenticationError, ConfigurationError

logger = logging.getLogger(__name__)

# Security for bearer tokens
security = HTTPBearer()


class SessionManager:
    """Manages user sessions and authentication tokens."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.sessions_file = settings.sessions_dir / "sessions.json"
        self._load_sessions()
    
    def _load_sessions(self):
        """Load sessions from file."""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    data = json.load(f)
                    # Filter out expired sessions
                    now = datetime.utcnow()
                    self.sessions = {
                        sid: session for sid, session in data.items()
                        if datetime.fromisoformat(session['expires_at']) > now
                    }
        except Exception as e:
            logger.warning(f"Could not load sessions: {e}")
            self.sessions = {}
    
    def _save_sessions(self):
        """Save sessions to file."""
        try:
            settings.ensure_directories()
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, default=str)
        except Exception as e:
            logger.error(f"Could not save sessions: {e}")
    
    def create_session(self, user_id: str = "default_user", metadata: Dict[str, Any] = None) -> str:
        """Create a new session and return session token."""
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=settings.session_expire_hours)
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires_at.isoformat(),
            'metadata': metadata or {}
        }
        
        self._save_sessions()
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate a session and return session data if valid."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if expires_at <= datetime.utcnow():
            # Session expired
            del self.sessions[session_id]
            self._save_sessions()
            return None
        
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
            logger.info(f"Deleted session {session_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if datetime.fromisoformat(session['expires_at']) <= now
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
        
        if expired_sessions:
            self._save_sessions()
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")


class APIKeyManager:
    """Manages API keys with encryption (from backend_server.py)."""
    
    def __init__(self):
        self.keys_file = settings.sessions_dir / "api_keys.json"
        self.fernet = self._get_or_create_encryption_key()
    
    def _get_or_create_encryption_key(self) -> Fernet:
        """Get or create encryption key for API keys."""
        key_file = settings.sessions_dir / "encryption.key"
        
        try:
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                settings.ensure_directories()
                with open(key_file, 'wb') as f:
                    f.write(key)
                logger.info("Created new encryption key")
            
            return Fernet(key)
        except Exception as e:
            logger.error(f"Could not initialize encryption: {e}")
            raise ConfigurationError("Failed to initialize API key encryption")
    
    def store_api_key(self, provider: str, api_key: str, user_id: str = "default") -> bool:
        """Store an encrypted API key."""
        try:
            # Load existing keys
            keys_data = {}
            if self.keys_file.exists():
                with open(self.keys_file, 'r') as f:
                    keys_data = json.load(f)
            
            # Encrypt the API key
            encrypted_key = self.fernet.encrypt(api_key.encode()).decode()
            
            # Store with metadata
            if user_id not in keys_data:
                keys_data[user_id] = {}
            
            keys_data[user_id][provider] = {
                'encrypted_key': encrypted_key,
                'created_at': datetime.utcnow().isoformat(),
                'last_used': None
            }
            
            # Save to file
            settings.ensure_directories()
            with open(self.keys_file, 'w') as f:
                json.dump(keys_data, f)
            
            logger.info(f"Stored API key for {provider} (user: {user_id})")
            return True
            
        except Exception as e:
            logger.error(f"Could not store API key: {e}")
            return False
    
    def get_api_key(self, provider: str, user_id: str = "default") -> Optional[str]:
        """Retrieve and decrypt an API key."""
        try:
            if not self.keys_file.exists():
                return None
            
            with open(self.keys_file, 'r') as f:
                keys_data = json.load(f)
            
            if user_id not in keys_data or provider not in keys_data[user_id]:
                return None
            
            encrypted_key = keys_data[user_id][provider]['encrypted_key']
            decrypted_key = self.fernet.decrypt(encrypted_key.encode()).decode()
            
            # Update last used
            keys_data[user_id][provider]['last_used'] = datetime.utcnow().isoformat()
            with open(self.keys_file, 'w') as f:
                json.dump(keys_data, f)
            
            return decrypted_key
            
        except Exception as e:
            logger.error(f"Could not retrieve API key for {provider}: {e}")
            return None
    
    def delete_api_key(self, provider: str, user_id: str = "default") -> bool:
        """Delete an API key."""
        try:
            if not self.keys_file.exists():
                return False
            
            with open(self.keys_file, 'r') as f:
                keys_data = json.load(f)
            
            if user_id in keys_data and provider in keys_data[user_id]:
                del keys_data[user_id][provider]
                
                # Clean up empty user entries
                if not keys_data[user_id]:
                    del keys_data[user_id]
                
                with open(self.keys_file, 'w') as f:
                    json.dump(keys_data, f)
                
                logger.info(f"Deleted API key for {provider} (user: {user_id})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Could not delete API key: {e}")
            return False


class AuthenticationService:
    """Main authentication service combining all auth methods."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.api_key_manager = APIKeyManager()
    
    def authenticate_with_password(self, password: str) -> str:
        """Authenticate with master password and return session token."""
        if not settings.master_password:
            raise AuthenticationError("Master password not configured")
        
        if password != settings.master_password:
            raise AuthenticationError("Invalid master password")
        
        # Create session
        session_token = self.session_manager.create_session(
            user_id="authenticated_user",
            metadata={"auth_method": "master_password"}
        )
        
        return session_token
    
    def authenticate_with_token(self, token: str) -> Dict[str, Any]:
        """Authenticate with session token and return user info."""
        session = self.session_manager.validate_session(token)
        if not session:
            raise AuthenticationError("Invalid or expired session token")
        
        return session
    
    def logout(self, token: str) -> bool:
        """Logout by deleting session."""
        return self.session_manager.delete_session(token)
    
    def cleanup_sessions(self):
        """Clean up expired sessions."""
        self.session_manager.cleanup_expired_sessions()


# Global instances
auth_service = AuthenticationService()


# FastAPI dependency functions
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user."""
    try:
        session = auth_service.authenticate_with_token(credentials.credentials)
        return session
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """FastAPI dependency to get user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        return auth_service.authenticate_with_token(credentials.credentials)
    except AuthenticationError:
        return None


def require_master_password():
    """FastAPI dependency that requires master password to be set."""
    if not settings.master_password:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Master password authentication not configured"
        )


# Password hashing utilities
def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash a password with salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against hash."""
    new_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(new_hash, hashed)