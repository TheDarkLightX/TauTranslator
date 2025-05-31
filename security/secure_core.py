#!/usr/bin/env python3
"""
Secure Core - Real Security Implementation
==========================================

This module provides ACTUAL security, not just a secure-looking GUI.
"""

import os
import json
import secrets
import time
from pathlib import Path

# Try to import cryptography for real encryption
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    from cryptography.hazmat.primitives import hashes, constant_time
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

class SecureStorage:
    """Real secure storage with AES-256-GCM encryption."""
    
    def __init__(self):
        # Create secure directory
        self.config_dir = Path.home() / ".tau_translator_secure"
        self.config_dir.mkdir(mode=0o700, exist_ok=True)
        
        # Secure file paths
        self.keys_file = self.config_dir / "encrypted_keys.dat"
        self.salt_file = self.config_dir / "salt.bin"
        self.auth_file = self.config_dir / "auth.bin"
        
        # Set restrictive permissions
        os.chmod(self.config_dir, 0o700)
        
        # Security state
        self.aes_gcm = None
        self.authenticated = False
        self.api_keys = {}
    
    def _secure_random_bytes(self, length: int) -> bytes:
        """Generate cryptographically secure random bytes."""
        return secrets.token_bytes(length)
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key using Scrypt (memory-hard)."""
        if not CRYPTO_AVAILABLE:
            raise Exception("Cryptography library required")

        kdf = Scrypt(
            length=32,  # 256-bit key
            salt=salt,
            n=2**14,    # CPU cost (16384)
            r=8,        # Memory cost
            p=1,        # Parallelization
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))
    
    def _hash_password(self, password: str, salt: bytes) -> bytes:
        """Create secure password hash."""
        kdf = Scrypt(
            length=32,
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))
    
    def _secure_write_file(self, filepath: Path, data: bytes):
        """Atomic write with secure permissions."""
        temp_file = filepath.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            
            os.chmod(temp_file, 0o600)
            temp_file.replace(filepath)
            
        except Exception:
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    def setup_encryption(self, password: str) -> bool:
        """Set up encryption for first time."""
        try:
            # Generate secure salt
            salt = self._secure_random_bytes(32)
            
            # Derive key and hash password
            key = self._derive_key(password, salt)
            password_hash = self._hash_password(password, salt)
            
            # Initialize AES-GCM
            self.aes_gcm = AESGCM(key)
            
            # Save salt and password hash
            self._secure_write_file(self.salt_file, salt)
            self._secure_write_file(self.auth_file, password_hash)
            
            # Initialize empty storage
            self.api_keys = {}
            self._save_encrypted_data()
            
            self.authenticated = True
            return True
            
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def unlock_with_password(self, password: str) -> bool:
        """Unlock existing encrypted storage."""
        try:
            # Load salt and stored hash
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
            
            with open(self.auth_file, 'rb') as f:
                stored_hash = f.read()
            
            # Verify password
            computed_hash = self._hash_password(password, salt)
            
            if constant_time.bytes_eq(stored_hash, computed_hash):
                # Password correct
                key = self._derive_key(password, salt)
                self.aes_gcm = AESGCM(key)
                self._load_encrypted_data()
                self.authenticated = True
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Unlock failed: {e}")
            return False
    
    def _save_encrypted_data(self):
        """Save data with AES-GCM encryption."""
        if not self.aes_gcm or not self.authenticated:
            raise Exception("Not authenticated")
        
        data = {
            'api_keys': self.api_keys,
            'timestamp': time.time()
        }
        
        # Encrypt with AES-GCM
        plaintext = json.dumps(data).encode('utf-8')
        nonce = self._secure_random_bytes(12)
        ciphertext = self.aes_gcm.encrypt(nonce, plaintext, None)
        
        # Save nonce + ciphertext
        encrypted_data = nonce + ciphertext
        self._secure_write_file(self.keys_file, encrypted_data)
    
    def _load_encrypted_data(self):
        """Load and decrypt data."""
        if not self.aes_gcm:
            raise Exception("Not authenticated")
        
        if not self.keys_file.exists():
            self.api_keys = {}
            return
        
        with open(self.keys_file, 'rb') as f:
            encrypted_data = f.read()
        
        # Split nonce and ciphertext
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        # Decrypt
        plaintext = self.aes_gcm.decrypt(nonce, ciphertext, None)
        data = json.loads(plaintext.decode('utf-8'))
        
        self.api_keys = data.get('api_keys', {})
    
    def store_api_key(self, provider: str, api_key: str):
        """Store API key securely."""
        if not self.authenticated:
            raise Exception("Not authenticated")
        
        self.api_keys[provider] = api_key
        self._save_encrypted_data()
    
    def get_api_key(self, provider: str) -> str:
        """Get stored API key."""
        if not self.authenticated:
            raise Exception("Not authenticated")
        
        return self.api_keys.get(provider, "")
    
    def remove_api_key(self, provider: str):
        """Remove API key."""
        if not self.authenticated:
            raise Exception("Not authenticated")
        
        if provider in self.api_keys:
            del self.api_keys[provider]
            self._save_encrypted_data()
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key exists."""
        if not self.authenticated:
            return False
        return provider in self.api_keys
    
    def is_first_time(self) -> bool:
        """Check if this is first time setup."""
        return not self.auth_file.exists()
    
    def secure_shutdown(self):
        """Clear sensitive data from memory."""
        if hasattr(self, 'api_keys'):
            self.api_keys.clear()
        self.aes_gcm = None
        self.authenticated = False
    
    def get_storage_info(self) -> dict:
        """Get information about where data is stored."""
        return {
            'directory': str(self.config_dir),
            'encrypted_keys': str(self.keys_file),
            'salt_file': str(self.salt_file),
            'auth_file': str(self.auth_file),
            'permissions': '0o700 (owner only)',
            'encryption': 'AES-256-GCM',
            'key_derivation': 'Scrypt (memory-hard)'
        }

def test_secure_storage():
    """Test the secure storage."""
    if not CRYPTO_AVAILABLE:
        print("❌ Cryptography not available")
        return
    
    print("🔐 Testing Secure Storage")
    
    storage = SecureStorage()
    
    # Test setup
    if storage.setup_encryption("TestPassword123!"):
        print("✅ Setup successful")
        
        # Test storage
        storage.store_api_key("openrouter", "sk-or-v1-test123")
        print("✅ Key stored")
        
        # Test retrieval
        key = storage.get_api_key("openrouter")
        print(f"✅ Key retrieved: {key[:10]}...")
        
        # Test info
        info = storage.get_storage_info()
        print(f"✅ Storage location: {info['directory']}")
        
        storage.secure_shutdown()
        print("✅ Secure shutdown")
    else:
        print("❌ Setup failed")

if __name__ == "__main__":
    test_secure_storage()
