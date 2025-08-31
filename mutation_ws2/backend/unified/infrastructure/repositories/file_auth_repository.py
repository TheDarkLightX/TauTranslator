"""
File-based implementation of IAuthenticationRepository.
Isolates all authentication-related file I/O operations.

Copyright: DarkLightX/Dana Edwards
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import os

from ...core.domain_types import (
    SessionId, ApiKey, Result, Success, Failure,
    FileSystemOperation
)
from ...core.interfaces import IAuthenticationRepository


class FileAuthenticationRepository(IAuthenticationRepository, FileSystemOperation):
    """
    File-based authentication repository.
    Marked as FileSystemOperation to make I/O operations explicit (Rule 4).
    """
    
    def __init__(self, base_dir: Path):
        """Initialize with base directory for auth data."""
        self.base_dir = base_dir
        self.sessions_file = base_dir / "sessions.json"
        self.api_keys_file = base_dir / "api_keys.enc"
        self.key_file = base_dir / ".encryption_key"
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_sessions_async(self) -> Result[Dict[SessionId, Dict[str, Any]]]:
        """Load all active sessions from file storage."""
        try:
            if not self.sessions_file.exists():
                return Success({})
            
            content = await asyncio.to_thread(
                self.sessions_file.read_text, encoding='utf-8'
            )
            
            if not content.strip():
                return Success({})
            
            data = await asyncio.to_thread(json.loads, content)
            
            # Convert string keys to SessionId
            sessions = {
                SessionId(sid): session_data 
                for sid, session_data in data.items()
            }
            
            return Success(sessions)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in sessions file: {e}")
            return Failure("INVALID_SESSION_DATA", "Session file contains invalid JSON")
        except Exception as e:
            self.logger.error(f"Error loading sessions: {e}")
            return Failure("LOAD_ERROR", str(e))
    
    async def save_session_async(self, session_id: SessionId, session_data: Dict[str, Any]) -> Result[None]:
        """Save a single session to file storage."""
        try:
            # Load existing sessions
            sessions_result = await self.load_sessions_async()
            if isinstance(sessions_result, Failure):
                sessions = {}
            else:
                sessions = sessions_result.value
            
            # Update session
            sessions[session_id] = session_data
            
            # Save all sessions
            return await self._save_all_sessions_async(sessions)
            
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")
            return Failure("SAVE_ERROR", str(e))
    
    async def delete_session_async(self, session_id: SessionId) -> Result[None]:
        """Delete a session from file storage."""
        try:
            sessions_result = await self.load_sessions_async()
            if isinstance(sessions_result, Failure):
                return sessions_result
            
            sessions = sessions_result.value
            
            if session_id in sessions:
                del sessions[session_id]
                return await self._save_all_sessions_async(sessions)
            
            return Success(None)
            
        except Exception as e:
            self.logger.error(f"Error deleting session: {e}")
            return Failure("DELETE_ERROR", str(e))
    
    async def load_api_keys_async(self) -> Result[Dict[str, ApiKey]]:
        """Load encrypted API keys from file storage."""
        try:
            if not self.api_keys_file.exists():
                return Success({})
            
            # Load encryption key
            key_result = await self.load_encryption_key_async()
            if isinstance(key_result, Failure):
                return key_result
            
            fernet = Fernet(key_result.value)
            
            # Read encrypted content
            encrypted_content = await asyncio.to_thread(
                self.api_keys_file.read_bytes
            )
            
            if not encrypted_content:
                return Success({})
            
            # Decrypt
            decrypted_content = await asyncio.to_thread(
                fernet.decrypt, encrypted_content
            )
            
            # Parse JSON
            data = await asyncio.to_thread(
                json.loads, decrypted_content.decode('utf-8')
            )
            
            # Convert to ApiKey type
            api_keys = {
                provider: ApiKey(key) 
                for provider, key in data.items()
            }
            
            return Success(api_keys)
            
        except Exception as e:
            self.logger.error(f"Error loading API keys: {e}")
            return Failure("LOAD_ERROR", str(e))
    
    async def save_api_key_async(self, provider: str, key: ApiKey) -> Result[None]:
        """Save an encrypted API key to file storage."""
        try:
            # Load existing keys
            keys_result = await self.load_api_keys_async()
            if isinstance(keys_result, Failure):
                keys = {}
            else:
                keys = keys_result.value
            
            # Update key
            keys[provider] = key
            
            # Save all keys
            return await self._save_all_api_keys_async(keys)
            
        except Exception as e:
            self.logger.error(f"Error saving API key: {e}")
            return Failure("SAVE_ERROR", str(e))
    
    async def delete_api_key_async(self, provider: str) -> Result[None]:
        """Delete an API key from file storage."""
        try:
            keys_result = await self.load_api_keys_async()
            if isinstance(keys_result, Failure):
                return keys_result
            
            keys = keys_result.value
            
            if provider in keys:
                del keys[provider]
                return await self._save_all_api_keys_async(keys)
            
            return Success(None)
            
        except Exception as e:
            self.logger.error(f"Error deleting API key: {e}")
            return Failure("DELETE_ERROR", str(e))
    
    async def load_encryption_key_async(self) -> Result[bytes]:
        """Load or generate encryption key for API keys."""
        try:
            if self.key_file.exists():
                key = await asyncio.to_thread(self.key_file.read_bytes)
                return Success(key)
            else:
                # Generate new key
                key = Fernet.generate_key()
                await self.save_encryption_key_async(key)
                return Success(key)
                
        except Exception as e:
            self.logger.error(f"Error loading encryption key: {e}")
            return Failure("KEY_ERROR", str(e))
    
    async def save_encryption_key_async(self, key: bytes) -> Result[None]:
        """Save encryption key to file."""
        try:
            await asyncio.to_thread(self.key_file.write_bytes, key)
            
            # Set restrictive permissions (Unix-like systems)
            if os.name != 'nt':  # Not Windows
                await asyncio.to_thread(os.chmod, self.key_file, 0o600)
            
            return Success(None)
            
        except Exception as e:
            self.logger.error(f"Error saving encryption key: {e}")
            return Failure("SAVE_ERROR", str(e))
    
    # --- Private Helper Methods ---
    
    async def _save_all_sessions_async(self, sessions: Dict[SessionId, Dict[str, Any]]) -> Result[None]:
        """Save all sessions to file."""
        try:
            # Convert SessionId to string for JSON serialization
            data = {str(sid): session_data for sid, session_data in sessions.items()}
            
            content = await asyncio.to_thread(
                json.dumps, data, indent=2, default=str
            )
            
            await asyncio.to_thread(
                self.sessions_file.write_text, content, encoding='utf-8'
            )
            
            return Success(None)
            
        except Exception as e:
            self.logger.error(f"Error saving sessions: {e}")
            return Failure("SAVE_ERROR", str(e))
    
    async def _save_all_api_keys_async(self, api_keys: Dict[str, ApiKey]) -> Result[None]:
        """Save all API keys encrypted to file."""
        try:
            # Load encryption key
            key_result = await self.load_encryption_key_async()
            if isinstance(key_result, Failure):
                return key_result
            
            fernet = Fernet(key_result.value)
            
            # Convert to JSON
            data = {provider: str(key) for provider, key in api_keys.items()}
            json_content = await asyncio.to_thread(json.dumps, data)
            
            # Encrypt
            encrypted_content = await asyncio.to_thread(
                fernet.encrypt, json_content.encode('utf-8')
            )
            
            # Save to file
            await asyncio.to_thread(
                self.api_keys_file.write_bytes, encrypted_content
            )
            
            return Success(None)
            
        except Exception as e:
            self.logger.error(f"Error saving API keys: {e}")
            return Failure("SAVE_ERROR", str(e))