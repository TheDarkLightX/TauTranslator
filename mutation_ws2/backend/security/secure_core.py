# Copyright (c) DarkLightX / Dana Edwards

"""
Provides secure, encrypted storage for sensitive data like API keys.
Uses Fernet symmetric encryption from the cryptography library.
"""

import base64
import json
import logging
import os

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Fernet = object  # Dummy class to avoid runtime errors if crypto is not available

logger = logging.getLogger(__name__)

class SecureStorage:
    """Manages the encryption and decryption of API keys."""

    def __init__(self, master_password_hash: str, storage_path: str = 'secure_storage.enc'):
        if not master_password_hash:
            raise ValueError("Master password hash cannot be empty.")
        self.storage_path = storage_path
        self._key = self._derive_key(master_password_hash.encode('utf-8'))
        self._fernet = Fernet(self._key)
        self._store = self._load_store()

    def _derive_key(self, password: bytes) -> bytes:
        """Derives a secure encryption key from the master password hash."""
        # Using the hash itself as the salt is not ideal, but acceptable for this use case.
        salt = password[:16] 
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

    def _load_store(self) -> dict:
        """Loads and decrypts the key store from disk."""
        if not os.path.exists(self.storage_path):
            return {}
        try:
            with open(self.storage_path, 'rb') as f:
                encrypted_data = f.read()
            if not encrypted_data:
                return {}
            decrypted_data = self._fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to load or decrypt secure store: {e}. A new store will be created.")
            # If decryption fails (e.g., wrong password), start with a fresh store.
            return {}

    def _save_store(self):
        """Encrypts and saves the current key store to disk."""
        try:
            data_to_encrypt = json.dumps(self._store).encode('utf-8')
            encrypted_data = self._fernet.encrypt(data_to_encrypt)
            with open(self.storage_path, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.exception(f"Failed to save secure store: {e}")

    def save_api_key(self, provider_id: str, api_key: str):
        """Saves or updates an API key for a given provider."""
        self._store[provider_id] = api_key
        self._save_store()
        logger.info(f"API key for provider '{provider_id}' has been saved securely.")

    def get_api_key(self, provider_id: str) -> str | None:
        """Retrieves an API key for a given provider."""
        return self._store.get(provider_id)

    def remove_api_key(self, provider_id: str):
        """Removes an API key for a given provider."""
        if provider_id in self._store:
            del self._store[provider_id]
            self._save_store()
            logger.info(f"API key for provider '{provider_id}' has been removed.")

    def get_all_api_keys(self) -> dict:
        """Returns all stored provider IDs and their keys."""
        return self._store.copy()

    def has_api_key(self, provider_id: str) -> bool:
        """Checks if an API key for a given provider exists."""
        return provider_id in self._store
