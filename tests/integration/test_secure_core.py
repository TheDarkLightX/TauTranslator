#!/usr/bin/env python3
"""
Comprehensive Unit Tests for SecureStorage
==========================================

Micro unit tests following TDD principles with:
- Complete API surface coverage
- Security property validation
- Performance benchmarks
- Edge case testing
- Mock isolation
- Parameterized test scenarios
"""

import pytest
import os
import json
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from contextlib import contextmanager

# Import the module under test
try:
    from secure_core import SecureStorage, CRYPTO_AVAILABLE
    if CRYPTO_AVAILABLE:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives import constant_time
        from cryptography.exceptions import InvalidTag
except ImportError:
    pytest.skip("secure_core module not available", allow_module_level=True)

# Import security fixtures
from tests.fixtures.security_fixtures import SecureTestFixtures

# Skip all tests if cryptography not available
pytestmark = pytest.mark.skipif(
    not CRYPTO_AVAILABLE, 
    reason="cryptography library not available"
)

class TestSecureStorageFixtures:
    """Test fixtures and utilities for SecureStorage testing."""
    
    @pytest.fixture
    def temp_home(self, tmp_path):
        """Create temporary home directory for testing."""
        temp_home_dir = tmp_path / "test_home"
        temp_home_dir.mkdir()
        
        with patch('pathlib.Path.home', return_value=temp_home_dir):
            yield temp_home_dir
    
    @pytest.fixture
    def secure_storage(self, temp_home):
        """Create SecureStorage instance with temporary directory."""
        storage = SecureStorage()
        yield storage
        # Cleanup
        storage.secure_shutdown()
    
    @pytest.fixture
    def mock_secrets(self):
        """Mock secrets module for deterministic testing."""
        with patch('secure_core.secrets') as mock_secrets:
            # Return predictable "random" bytes for testing
            mock_secrets.token_bytes.side_effect = lambda n: b'A' * n
            yield mock_secrets
    
    @pytest.fixture
    def mock_time(self):
        """Mock time module for deterministic timestamps."""
        with patch('secure_core.time') as mock_time:
            mock_time.time.return_value = 1234567890.0
            yield mock_time
    
    @pytest.fixture
    def sample_password(self):
        """Sample strong password for testing."""
        return SecureTestFixtures.get_test_password()
    
    @pytest.fixture
    def sample_weak_passwords(self):
        """Sample weak passwords for edge case testing."""
        return [
            "",  # Empty
            "a",  # Too short
            "password",  # Common word
            "12345678",  # Only numbers
            "abcdefgh",  # Only letters
        ]
    
    @pytest.fixture
    def sample_api_keys(self):
        """Sample API keys for testing."""
        return {
            "openrouter": SecureTestFixtures.generate_test_api_key("or-v1"),
            "openai": SecureTestFixtures.generate_test_api_key("openai"),
            "anthropic": SecureTestFixtures.generate_test_api_key("ant")
        }

class TestSecureStorageInitialization(TestSecureStorageFixtures):
    """Test SecureStorage initialization and setup."""
    
    def test_init_creates_secure_directory(self, temp_home):
        """Test that initialization creates secure directory with correct permissions."""
        storage = SecureStorage()
        
        # Verify directory exists
        assert storage.config_dir.exists()
        assert storage.config_dir.is_dir()
        
        # Verify permissions (0o700 = owner only)
        stat_info = storage.config_dir.stat()
        assert oct(stat_info.st_mode)[-3:] == '700'
    
    def test_init_sets_correct_file_paths(self, secure_storage, temp_home):
        """Test that initialization sets correct file paths."""
        expected_dir = temp_home / ".tau_translator_secure"
        
        assert secure_storage.config_dir == expected_dir
        assert secure_storage.keys_file == expected_dir / "encrypted_keys.dat"
        assert secure_storage.salt_file == expected_dir / "salt.bin"
        assert secure_storage.auth_file == expected_dir / "auth.bin"
    
    def test_init_sets_default_state(self, secure_storage):
        """Test that initialization sets correct default state."""
        assert secure_storage.aes_gcm is None
        assert secure_storage.authenticated is False
        assert secure_storage.api_keys == {}
    
    @patch('os.chmod')
    def test_init_sets_directory_permissions(self, mock_chmod, temp_home):
        """Test that directory permissions are set correctly."""
        storage = SecureStorage()
        
        # Verify chmod was called with correct permissions
        mock_chmod.assert_called_with(storage.config_dir, 0o700)

class TestSecureStorageRandomGeneration(TestSecureStorageFixtures):
    """Test secure random byte generation."""
    
    def test_secure_random_bytes_returns_correct_length(self, secure_storage):
        """Test that _secure_random_bytes returns correct length."""
        for length in [1, 16, 32, 64, 128]:
            result = secure_storage._secure_random_bytes(length)
            assert len(result) == length
            assert isinstance(result, bytes)
    
    def test_secure_random_bytes_returns_different_values(self, secure_storage):
        """Test that _secure_random_bytes returns different values each call."""
        # Generate multiple random byte sequences
        results = [secure_storage._secure_random_bytes(32) for _ in range(10)]
        
        # Verify they're all different (extremely high probability)
        assert len(set(results)) == len(results)
    
    @patch('secure_core.secrets.token_bytes')
    def test_secure_random_bytes_uses_secrets_module(self, mock_token_bytes, secure_storage):
        """Test that _secure_random_bytes uses secrets module."""
        mock_token_bytes.return_value = b'test_bytes'
        
        result = secure_storage._secure_random_bytes(16)
        
        mock_token_bytes.assert_called_once_with(16)
        assert result == b'test_bytes'

class TestSecureStorageKeyDerivation(TestSecureStorageFixtures):
    """Test key derivation functionality."""
    
    def test_derive_key_returns_correct_length(self, secure_storage):
        """Test that _derive_key returns 32-byte key."""
        password = SecureTestFixtures.get_test_password()
        salt = b'A' * 32
        
        key = secure_storage._derive_key(password, salt)
        
        assert len(key) == 32
        assert isinstance(key, bytes)
    
    def test_derive_key_deterministic_with_same_inputs(self, secure_storage):
        """Test that _derive_key is deterministic with same inputs."""
        password = SecureTestFixtures.get_test_password()
        salt = b'A' * 32
        
        key1 = secure_storage._derive_key(password, salt)
        key2 = secure_storage._derive_key(password, salt)
        
        assert key1 == key2
    
    def test_derive_key_different_with_different_passwords(self, secure_storage):
        """Test that _derive_key produces different keys for different passwords."""
        salt = b'A' * 32
        
        key1 = secure_storage._derive_key("password1", salt)
        key2 = secure_storage._derive_key("password2", salt)
        
        assert key1 != key2
    
    def test_derive_key_different_with_different_salts(self, secure_storage):
        """Test that _derive_key produces different keys for different salts."""
        password = SecureTestFixtures.get_test_password()
        
        key1 = secure_storage._derive_key(password, b'A' * 32)
        key2 = secure_storage._derive_key(password, b'B' * 32)
        
        assert key1 != key2
    
    def test_hash_password_same_as_derive_key(self, secure_storage):
        """Test that _hash_password uses same algorithm as _derive_key."""
        password = SecureTestFixtures.get_test_password()
        salt = b'A' * 32
        
        key = secure_storage._derive_key(password, salt)
        hash_result = secure_storage._hash_password(password, salt)
        
        # Should be identical since they use same Scrypt parameters
        assert key == hash_result
    
    @patch('secure_core.CRYPTO_AVAILABLE', False)
    def test_derive_key_raises_when_crypto_unavailable(self, secure_storage):
        """Test that _derive_key raises exception when cryptography unavailable."""
        with pytest.raises(Exception, match="Cryptography library required"):
            secure_storage._derive_key("password", b'salt')

class TestSecureStorageFileOperations(TestSecureStorageFixtures):
    """Test secure file operations."""
    
    def test_secure_write_file_creates_file_with_correct_permissions(self, secure_storage, tmp_path):
        """Test that _secure_write_file creates file with correct permissions."""
        test_file = tmp_path / "test_file.dat"
        test_data = b"test data"
        
        secure_storage._secure_write_file(test_file, test_data)
        
        # Verify file exists and has correct content
        assert test_file.exists()
        assert test_file.read_bytes() == test_data
        
        # Verify permissions (0o600 = owner read/write only)
        stat_info = test_file.stat()
        assert oct(stat_info.st_mode)[-3:] == '600'
    
    def test_secure_write_file_atomic_operation(self, secure_storage, tmp_path):
        """Test that _secure_write_file performs atomic write operation."""
        test_file = tmp_path / "test_file.dat"
        temp_file = test_file.with_suffix('.tmp')
        test_data = b"test data"
        
        with patch('pathlib.Path.replace') as mock_replace:
            secure_storage._secure_write_file(test_file, test_data)
            
            # Verify atomic rename was called
            mock_replace.assert_called_once_with(test_file)
    
    def test_secure_write_file_cleans_up_on_error(self, secure_storage, tmp_path):
        """Test that _secure_write_file cleans up temp file on error."""
        test_file = tmp_path / "test_file.dat"
        temp_file = test_file.with_suffix('.tmp')
        
        with patch('builtins.open', side_effect=IOError("Write failed")):
            with pytest.raises(IOError):
                secure_storage._secure_write_file(test_file, b"data")
            
            # Verify temp file doesn't exist
            assert not temp_file.exists()
    
    @patch('os.fsync')
    def test_secure_write_file_forces_disk_sync(self, mock_fsync, secure_storage, tmp_path):
        """Test that _secure_write_file forces data to disk."""
        test_file = tmp_path / "test_file.dat"
        
        secure_storage._secure_write_file(test_file, b"test data")
        
        # Verify fsync was called
        mock_fsync.assert_called_once()

class TestSecureStorageEncryptionSetup(TestSecureStorageFixtures):
    """Test encryption setup functionality."""
    
    def test_setup_encryption_success(self, secure_storage, sample_password, mock_secrets, mock_time):
        """Test successful encryption setup."""
        result = secure_storage.setup_encryption(sample_password)
        
        assert result is True
        assert secure_storage.authenticated is True
        assert secure_storage.aes_gcm is not None
        assert isinstance(secure_storage.aes_gcm, AESGCM)
    
    def test_setup_encryption_creates_required_files(self, secure_storage, sample_password, mock_secrets):
        """Test that setup_encryption creates all required files."""
        secure_storage.setup_encryption(sample_password)
        
        assert secure_storage.salt_file.exists()
        assert secure_storage.auth_file.exists()
        assert secure_storage.keys_file.exists()
    
    def test_setup_encryption_saves_correct_salt(self, secure_storage, sample_password, mock_secrets):
        """Test that setup_encryption saves correct salt."""
        # Mock secrets to return predictable salt
        expected_salt = b'A' * 32
        mock_secrets.token_bytes.return_value = expected_salt
        
        secure_storage.setup_encryption(sample_password)
        
        saved_salt = secure_storage.salt_file.read_bytes()
        assert saved_salt == expected_salt
    
    def test_setup_encryption_initializes_empty_api_keys(self, secure_storage, sample_password, mock_secrets):
        """Test that setup_encryption initializes empty API keys."""
        secure_storage.setup_encryption(sample_password)
        
        assert secure_storage.api_keys == {}
    
    def test_setup_encryption_handles_crypto_error(self, secure_storage, sample_password):
        """Test that setup_encryption handles cryptography errors gracefully."""
        with patch('secure_core.AESGCM', side_effect=Exception("Crypto error")):
            result = secure_storage.setup_encryption(sample_password)
            
            assert result is False
            assert secure_storage.authenticated is False

class TestSecureStoragePasswordUnlock(TestSecureStorageFixtures):
    """Test password unlock functionality."""
    
    def test_unlock_with_correct_password(self, secure_storage, sample_password, mock_secrets):
        """Test unlocking with correct password."""
        # Setup first
        secure_storage.setup_encryption(sample_password)
        secure_storage.secure_shutdown()
        
        # Now test unlock
        result = secure_storage.unlock_with_password(sample_password)
        
        assert result is True
        assert secure_storage.authenticated is True
        assert secure_storage.aes_gcm is not None
    
    def test_unlock_with_incorrect_password(self, secure_storage, sample_password, mock_secrets):
        """Test unlocking with incorrect password."""
        # Setup first
        secure_storage.setup_encryption(sample_password)
        secure_storage.secure_shutdown()
        
        # Try unlock with wrong password
        result = secure_storage.unlock_with_password("wrong_password")
        
        assert result is False
        assert secure_storage.authenticated is False
        assert secure_storage.aes_gcm is None
    
    def test_unlock_uses_constant_time_comparison(self, secure_storage, sample_password, mock_secrets):
        """Test that unlock uses constant-time comparison."""
        # Setup first
        secure_storage.setup_encryption(sample_password)
        secure_storage.secure_shutdown()
        
        with patch('secure_core.constant_time.bytes_eq') as mock_bytes_eq:
            mock_bytes_eq.return_value = True
            
            secure_storage.unlock_with_password(sample_password)
            
            # Verify constant_time.bytes_eq was called
            mock_bytes_eq.assert_called_once()
    
    def test_unlock_handles_missing_files(self, secure_storage, sample_password):
        """Test that unlock handles missing salt/auth files gracefully."""
        result = secure_storage.unlock_with_password(sample_password)
        
        assert result is False
        assert secure_storage.authenticated is False
    
    def test_unlock_handles_corrupted_files(self, secure_storage, sample_password, mock_secrets):
        """Test that unlock handles corrupted files gracefully."""
        # Setup first
        secure_storage.setup_encryption(sample_password)
        
        # Corrupt the auth file
        secure_storage.auth_file.write_bytes(b"corrupted_data")
        secure_storage.secure_shutdown()
        
        result = secure_storage.unlock_with_password(sample_password)

        assert result is False
        assert secure_storage.authenticated is False

class TestSecureStorageDataOperations(TestSecureStorageFixtures):
    """Test encrypted data save/load operations."""

    def test_save_encrypted_data_requires_authentication(self, secure_storage):
        """Test that _save_encrypted_data requires authentication."""
        with pytest.raises(Exception, match="Not authenticated"):
            secure_storage._save_encrypted_data()

    def test_save_encrypted_data_creates_encrypted_file(self, secure_storage, sample_password, mock_secrets, mock_time):
        """Test that _save_encrypted_data creates properly encrypted file."""
        secure_storage.setup_encryption(sample_password)
        secure_storage.api_keys = {"test": "key"}

        secure_storage._save_encrypted_data()

        assert secure_storage.keys_file.exists()

        # Verify file contains encrypted data (not plaintext)
        encrypted_data = secure_storage.keys_file.read_bytes()
        assert b"test" not in encrypted_data  # Plaintext should not be visible
        assert b"key" not in encrypted_data

    def test_save_encrypted_data_includes_timestamp(self, secure_storage, sample_password, mock_secrets, mock_time):
        """Test that _save_encrypted_data includes timestamp."""
        secure_storage.setup_encryption(sample_password)

        # Decrypt and verify timestamp is included
        secure_storage._save_encrypted_data()
        encrypted_data = secure_storage.keys_file.read_bytes()

        # Decrypt to verify structure
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        plaintext = secure_storage.aes_gcm.decrypt(nonce, ciphertext, None)
        data = json.loads(plaintext.decode('utf-8'))

        assert 'timestamp' in data
        assert data['timestamp'] == 1234567890.0  # From mock_time

    def test_load_encrypted_data_requires_authentication(self, secure_storage):
        """Test that _load_encrypted_data requires authentication."""
        with pytest.raises(Exception, match="Not authenticated"):
            secure_storage._load_encrypted_data()

    def test_load_encrypted_data_handles_missing_file(self, secure_storage, sample_password, mock_secrets):
        """Test that _load_encrypted_data handles missing file gracefully."""
        secure_storage.setup_encryption(sample_password)
        secure_storage.keys_file.unlink()  # Remove the file

        secure_storage._load_encrypted_data()

        assert secure_storage.api_keys == {}

    def test_load_encrypted_data_decrypts_correctly(self, secure_storage, sample_password, mock_secrets, sample_api_keys):
        """Test that _load_encrypted_data decrypts data correctly."""
        secure_storage.setup_encryption(sample_password)
        secure_storage.api_keys = sample_api_keys
        secure_storage._save_encrypted_data()

        # Clear and reload
        secure_storage.api_keys = {}
        secure_storage._load_encrypted_data()

        assert secure_storage.api_keys == sample_api_keys

    def test_load_encrypted_data_handles_corrupted_file(self, secure_storage, sample_password, mock_secrets):
        """Test that _load_encrypted_data handles corrupted file."""
        secure_storage.setup_encryption(sample_password)

        # Corrupt the encrypted file
        secure_storage.keys_file.write_bytes(b"corrupted_data")

        with pytest.raises(Exception):
            secure_storage._load_encrypted_data()

    def test_encryption_roundtrip_preserves_data(self, secure_storage, sample_password, mock_secrets, sample_api_keys):
        """Test that encryption/decryption roundtrip preserves data exactly."""
        secure_storage.setup_encryption(sample_password)

        # Test with various data types
        test_data = {
            "string_key": "test_value",
            "unicode_key": "test_ünïcödé_value",
            "empty_key": "",
            "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?"
        }

        secure_storage.api_keys = test_data
        secure_storage._save_encrypted_data()

        # Clear and reload
        secure_storage.api_keys = {}
        secure_storage._load_encrypted_data()

        assert secure_storage.api_keys == test_data

class TestSecureStorageAPIKeyManagement(TestSecureStorageFixtures):
    """Test API key management operations."""

    def test_store_api_key_requires_authentication(self, secure_storage):
        """Test that store_api_key requires authentication."""
        with pytest.raises(Exception, match="Not authenticated"):
            secure_storage.store_api_key("provider", "key")

    def test_store_api_key_saves_key(self, secure_storage, sample_password, mock_secrets):
        """Test that store_api_key saves key correctly."""
        secure_storage.setup_encryption(sample_password)
        test_key = SecureTestFixtures.generate_test_api_key("or-v1")

        secure_storage.store_api_key("openrouter", test_key)

        assert secure_storage.api_keys["openrouter"] == test_key

    def test_store_api_key_persists_to_disk(self, secure_storage, sample_password, mock_secrets, temp_home):
        """Test that store_api_key persists to disk."""
        secure_storage.setup_encryption(sample_password)

        test_key = SecureTestFixtures.generate_test_api_key("or-v1")
        secure_storage.store_api_key("openrouter", test_key)

        # Verify file was updated
        assert secure_storage.keys_file.exists()

        # Create new instance and verify key persists
        with patch('pathlib.Path.home', return_value=temp_home):
            new_storage = SecureStorage()
            new_storage.unlock_with_password(sample_password)
            assert new_storage.get_api_key("openrouter") == test_key

    def test_get_api_key_requires_authentication(self, secure_storage):
        """Test that get_api_key requires authentication."""
        with pytest.raises(Exception, match="Not authenticated"):
            secure_storage.get_api_key("provider")

    def test_get_api_key_returns_stored_key(self, secure_storage, sample_password, mock_secrets):
        """Test that get_api_key returns stored key."""
        secure_storage.setup_encryption(sample_password)
        test_key = SecureTestFixtures.generate_test_api_key("or-v1")
        secure_storage.store_api_key("openrouter", test_key)

        result = secure_storage.get_api_key("openrouter")

        assert result == test_key

    def test_get_api_key_returns_empty_for_missing_key(self, secure_storage, sample_password, mock_secrets):
        """Test that get_api_key returns empty string for missing key."""
        secure_storage.setup_encryption(sample_password)

        result = secure_storage.get_api_key("nonexistent")

        assert result == ""

    def test_remove_api_key_requires_authentication(self, secure_storage):
        """Test that remove_api_key requires authentication."""
        with pytest.raises(Exception, match="Not authenticated"):
            secure_storage.remove_api_key("provider")

    def test_remove_api_key_removes_existing_key(self, secure_storage, sample_password, mock_secrets):
        """Test that remove_api_key removes existing key."""
        secure_storage.setup_encryption(sample_password)
        test_key = SecureTestFixtures.generate_test_api_key("or-v1")
        secure_storage.store_api_key("openrouter", test_key)

        secure_storage.remove_api_key("openrouter")

        assert "openrouter" not in secure_storage.api_keys
        assert secure_storage.get_api_key("openrouter") == ""

    def test_remove_api_key_handles_missing_key(self, secure_storage, sample_password, mock_secrets):
        """Test that remove_api_key handles missing key gracefully."""
        secure_storage.setup_encryption(sample_password)

        # Should not raise exception
        secure_storage.remove_api_key("nonexistent")

    def test_has_api_key_requires_authentication(self, secure_storage):
        """Test that has_api_key returns False when not authenticated."""
        result = secure_storage.has_api_key("provider")
        assert result is False

    def test_has_api_key_returns_correct_status(self, secure_storage, sample_password, mock_secrets):
        """Test that has_api_key returns correct status."""
        secure_storage.setup_encryption(sample_password)

        assert secure_storage.has_api_key("openrouter") is False

        test_key = SecureTestFixtures.generate_test_api_key("or-v1")
        secure_storage.store_api_key("openrouter", test_key)
        assert secure_storage.has_api_key("openrouter") is True

        secure_storage.remove_api_key("openrouter")
        assert secure_storage.has_api_key("openrouter") is False

class TestSecureStorageUtilityMethods(TestSecureStorageFixtures):
    """Test utility and information methods."""

    def test_is_first_time_returns_true_initially(self, secure_storage):
        """Test that is_first_time returns True initially."""
        assert secure_storage.is_first_time() is True

    def test_is_first_time_returns_false_after_setup(self, secure_storage, sample_password, mock_secrets):
        """Test that is_first_time returns False after setup."""
        secure_storage.setup_encryption(sample_password)

        assert secure_storage.is_first_time() is False

    def test_secure_shutdown_clears_sensitive_data(self, secure_storage, sample_password, mock_secrets):
        """Test that secure_shutdown clears sensitive data."""
        secure_storage.setup_encryption(sample_password)
        test_key = SecureTestFixtures.generate_test_api_key("or-v1")
        secure_storage.store_api_key("openrouter", test_key)

        secure_storage.secure_shutdown()

        assert secure_storage.api_keys == {}
        assert secure_storage.aes_gcm is None
        assert secure_storage.authenticated is False

    def test_get_storage_info_returns_correct_information(self, secure_storage, temp_home):
        """Test that get_storage_info returns correct information."""
        info = secure_storage.get_storage_info()

        expected_dir = str(temp_home / ".tau_translator_secure")

        assert info['directory'] == expected_dir
        assert info['encrypted_keys'] == f"{expected_dir}/encrypted_keys.dat"
        assert info['salt_file'] == f"{expected_dir}/salt.bin"
        assert info['auth_file'] == f"{expected_dir}/auth.bin"
        assert info['permissions'] == '0o700 (owner only)'
        assert info['encryption'] == 'AES-256-GCM'
        assert info['key_derivation'] == 'Scrypt (memory-hard)'

class TestSecureStorageSecurityProperties(TestSecureStorageFixtures):
    """Test security properties and edge cases."""

    @pytest.mark.parametrize("password", [
        "short",  # Too short
        "password123",  # Common pattern
        "12345678",  # Only numbers
        "abcdefgh",  # Only letters
        "",  # Empty
    ])
    def test_weak_passwords_still_work_but_not_recommended(self, secure_storage, password, mock_secrets):
        """Test that weak passwords still work (user responsibility)."""
        # The system doesn't enforce password strength - that's UI responsibility
        result = secure_storage.setup_encryption(password)
        assert result is True

    def test_constant_time_comparison_prevents_timing_attacks(self, secure_storage, sample_password, mock_secrets):
        """Test that password verification uses constant-time comparison."""
        secure_storage.setup_encryption(sample_password)
        secure_storage.secure_shutdown()

        with patch('secure_core.constant_time.bytes_eq') as mock_bytes_eq:
            mock_bytes_eq.return_value = False

            # Try with wrong password
            result = secure_storage.unlock_with_password("wrong_password")

            # Verify constant_time.bytes_eq was called (not regular ==)
            mock_bytes_eq.assert_called_once()
            assert result is False

    def test_nonce_uniqueness_for_encryption(self, secure_storage, sample_password, mock_secrets):
        """Test that each encryption uses a unique nonce."""
        secure_storage.setup_encryption(sample_password)

        # Save data multiple times
        secure_storage.api_keys = {"test": "key1"}
        secure_storage._save_encrypted_data()
        data1 = secure_storage.keys_file.read_bytes()

        secure_storage.api_keys = {"test": "key2"}
        secure_storage._save_encrypted_data()
        data2 = secure_storage.keys_file.read_bytes()

        # Nonces (first 12 bytes) should be different
        nonce1 = data1[:12]
        nonce2 = data2[:12]
        assert nonce1 != nonce2

    def test_encryption_produces_different_ciphertext_for_same_data(self, secure_storage, sample_password, mock_secrets):
        """Test that encrypting same data twice produces different ciphertext."""
        secure_storage.setup_encryption(sample_password)

        # Encrypt same data twice
        test_data = {"test": "same_data"}

        secure_storage.api_keys = test_data
        secure_storage._save_encrypted_data()
        ciphertext1 = secure_storage.keys_file.read_bytes()

        secure_storage.api_keys = test_data
        secure_storage._save_encrypted_data()
        ciphertext2 = secure_storage.keys_file.read_bytes()

        # Ciphertexts should be different (due to different nonces)
        assert ciphertext1 != ciphertext2

        # But both should decrypt to same data
        secure_storage.keys_file.write_bytes(ciphertext1)
        secure_storage._load_encrypted_data()
        assert secure_storage.api_keys == test_data

        secure_storage.keys_file.write_bytes(ciphertext2)
        secure_storage._load_encrypted_data()
        assert secure_storage.api_keys == test_data

    def test_memory_clearing_on_shutdown(self, secure_storage, sample_password, mock_secrets):
        """Test that sensitive data is cleared from memory on shutdown."""
        secure_storage.setup_encryption(sample_password)
        test_key = SecureTestFixtures.generate_test_api_key("or-v1-sensitive")
        secure_storage.store_api_key("openrouter", test_key)

        # Verify data is in memory
        assert secure_storage.api_keys["openrouter"] == test_key
        assert secure_storage.aes_gcm is not None
        assert secure_storage.authenticated is True

        # Shutdown and verify clearing
        secure_storage.secure_shutdown()

        assert secure_storage.api_keys == {}
        assert secure_storage.aes_gcm is None
        assert secure_storage.authenticated is False

    def test_file_permissions_are_restrictive(self, secure_storage, sample_password, mock_secrets):
        """Test that created files have restrictive permissions."""
        secure_storage.setup_encryption(sample_password)

        # Check directory permissions
        dir_stat = secure_storage.config_dir.stat()
        assert oct(dir_stat.st_mode)[-3:] == '700'  # Owner only

        # Check file permissions
        for file_path in [secure_storage.salt_file, secure_storage.auth_file, secure_storage.keys_file]:
            if file_path.exists():
                file_stat = file_path.stat()
                assert oct(file_stat.st_mode)[-3:] == '600'  # Owner read/write only

class TestSecureStorageEdgeCases(TestSecureStorageFixtures):
    """Test edge cases and error conditions."""

    def test_unicode_passwords_work_correctly(self, secure_storage, mock_secrets):
        """Test that Unicode passwords work correctly."""
        unicode_password = SecureTestFixtures.get_test_credentials()['unicode_password']

        result = secure_storage.setup_encryption(unicode_password)
        assert result is True

        secure_storage.secure_shutdown()

        result = secure_storage.unlock_with_password(unicode_password)
        assert result is True

    def test_unicode_api_keys_work_correctly(self, secure_storage, sample_password, mock_secrets):
        """Test that Unicode API keys work correctly."""
        secure_storage.setup_encryption(sample_password)

        unicode_key = "sk-ünïcödé-key-123!@#"
        secure_storage.store_api_key("unicode_provider", unicode_key)

        retrieved_key = secure_storage.get_api_key("unicode_provider")
        assert retrieved_key == unicode_key

    def test_large_api_key_data_works(self, secure_storage, sample_password, mock_secrets):
        """Test that large amounts of API key data work correctly."""
        secure_storage.setup_encryption(sample_password)

        # Create large dataset
        large_data = {}
        for i in range(100):
            large_data[f"provider_{i}"] = f"sk-very-long-api-key-{i}-" + "x" * 100

        secure_storage.api_keys = large_data
        secure_storage._save_encrypted_data()

        # Clear and reload
        secure_storage.api_keys = {}
        secure_storage._load_encrypted_data()

        assert secure_storage.api_keys == large_data

    def test_empty_api_keys_dict_works(self, secure_storage, sample_password, mock_secrets):
        """Test that empty API keys dict works correctly."""
        secure_storage.setup_encryption(sample_password)

        # Explicitly set empty dict
        secure_storage.api_keys = {}
        secure_storage._save_encrypted_data()

        # Reload
        secure_storage._load_encrypted_data()

        assert secure_storage.api_keys == {}

    def test_special_characters_in_provider_names(self, secure_storage, sample_password, mock_secrets):
        """Test that special characters in provider names work."""
        secure_storage.setup_encryption(sample_password)

        special_providers = {
            "provider-with-dashes": "key1",
            "provider_with_underscores": "key2",
            "provider.with.dots": "key3",
            "provider with spaces": "key4",
            "provider!@#$%": "key5"
        }

        for provider, key in special_providers.items():
            secure_storage.store_api_key(provider, key)

        for provider, expected_key in special_providers.items():
            assert secure_storage.get_api_key(provider) == expected_key

class TestSecureStoragePerformanceBenchmarks(TestSecureStorageFixtures):
    """Performance benchmarks for cryptographic operations."""

    def test_key_derivation_performance(self, secure_storage, benchmark):
        """Benchmark key derivation performance."""
        password = SecureTestFixtures.generate_test_password(length=24)
        salt = b'A' * 32

        def derive_key():
            return secure_storage._derive_key(password, salt)

        # Benchmark should complete in reasonable time
        result = benchmark(derive_key)
        assert len(result) == 32

    def test_encryption_performance(self, secure_storage, sample_password, mock_secrets, benchmark):
        """Benchmark encryption performance."""
        secure_storage.setup_encryption(sample_password)

        # Large dataset for benchmarking
        large_data = {}
        for i in range(50):
            large_data[f"provider_{i}"] = f"sk-api-key-{i}-" + "x" * 50

        def encrypt_data():
            secure_storage.api_keys = large_data
            secure_storage._save_encrypted_data()

        benchmark(encrypt_data)

    def test_decryption_performance(self, secure_storage, sample_password, mock_secrets, benchmark):
        """Benchmark decryption performance."""
        secure_storage.setup_encryption(sample_password)

        # Prepare encrypted data
        large_data = {}
        for i in range(50):
            large_data[f"provider_{i}"] = f"sk-api-key-{i}-" + "x" * 50

        secure_storage.api_keys = large_data
        secure_storage._save_encrypted_data()

        def decrypt_data():
            secure_storage.api_keys = {}
            secure_storage._load_encrypted_data()

        benchmark(decrypt_data)

    def test_setup_performance(self, temp_home, benchmark):
        """Benchmark setup performance."""
        def setup_encryption():
            with patch('pathlib.Path.home', return_value=temp_home):
                storage = SecureStorage()
                storage.setup_encryption("benchmark_password")
                storage.secure_shutdown()

        benchmark(setup_encryption)

# Parameterized tests for comprehensive coverage
class TestSecureStorageParameterized(TestSecureStorageFixtures):
    """Parameterized tests for comprehensive coverage."""

    @pytest.mark.parametrize("provider", [
        "openrouter",
        "openai", 
        "anthropic",
        "google",
        "custom_provider",
    ])
    def test_store_and_retrieve_various_providers(self, secure_storage, sample_password, mock_secrets, provider):
        """Test storing and retrieving various provider API keys."""
        secure_storage.setup_encryption(sample_password)
        
        # Generate secure API key for this provider
        api_key = SecureTestFixtures.generate_test_api_key(provider)

        secure_storage.store_api_key(provider, api_key)
        retrieved_key = secure_storage.get_api_key(provider)

        assert retrieved_key == api_key
        assert secure_storage.has_api_key(provider) is True

    @pytest.mark.parametrize("password_length", [8, 16, 32, 64, 128])
    def test_various_password_lengths(self, secure_storage, mock_secrets, password_length):
        """Test various password lengths."""
        password = SecureTestFixtures.generate_test_password(length=password_length)

        result = secure_storage.setup_encryption(password)
        assert result is True

        secure_storage.secure_shutdown()

        result = secure_storage.unlock_with_password(password)
        assert result is True

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=secure_core",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--benchmark-only",
        "--benchmark-sort=mean"
    ])
