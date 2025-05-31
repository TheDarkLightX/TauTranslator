"""
Security Test Fixtures
======================

Secure test data generation for security-related tests.
Replaces hardcoded secrets with generated test data.
"""

import os
import secrets
import string
from typing import Dict, Any


class SecureTestFixtures:
    """Generate secure test data for security tests."""
    
    @staticmethod
    def generate_test_password(length: int = 16) -> str:
        """Generate a secure test password."""
        chars = string.ascii_letters + string.digits + "!@#$%&*"
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_test_api_key(provider: str = "test") -> str:
        """Generate a test API key for the specified provider."""
        key_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        return f"sk-{provider}-{key_part}"
    
    @staticmethod
    def generate_test_salt(length: int = 32) -> bytes:
        """Generate a test salt for cryptographic operations."""
        return secrets.token_bytes(length)
    
    @staticmethod
    def get_test_password() -> str:
        """Get test password from environment or generate one."""
        return os.getenv('TEST_PASSWORD', SecureTestFixtures.generate_test_password())
    
    @staticmethod
    def get_test_credentials() -> Dict[str, Any]:
        """Get complete set of test credentials."""
        return {
            'password': SecureTestFixtures.get_test_password(),
            'api_key': SecureTestFixtures.generate_test_api_key(),
            'salt': SecureTestFixtures.generate_test_salt(),
            'unicode_password': SecureTestFixtures.generate_test_password() + "ünïcödé",
            'unicode_key': SecureTestFixtures.generate_test_api_key("unicode"),
        }


# Constants for tests (not secrets)
TEST_CONSTANTS = {
    'default_iteration_count': 100000,
    'key_length': 32,
    'salt_length': 32,
    'provider_names': ['openrouter', 'anthropic', 'openai'],
    'test_data_sizes': [100, 1000, 10000],
}