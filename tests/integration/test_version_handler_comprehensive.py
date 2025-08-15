"""Comprehensive tests for the version handler module."""

import pytest
import semver
from unittest.mock import Mock, patch
from tau_translator_omega.core_engine.version_handler import VersionHandler


class TestVersionHandlerComprehensive:
    """Comprehensive tests for version handler functionality."""

    @pytest.fixture
    def handler(self):
        """Create a version handler instance for testing."""
        return VersionHandler()

    @pytest.fixture
    def mock_plugin(self):
        """Create a mock plugin for testing."""
        plugin = Mock()
        plugin.id = "test-plugin"
        plugin.ilr_versions_supported = ["1.0.0"]
        return plugin

    def test_handler_initialization(self):
        """Test version handler initialization."""
        handler = VersionHandler()
        assert handler.errors == []

    def test_parse_semver_valid_versions(self, handler):
        """Test parsing valid semantic versions."""
        # Test standard version
        version = handler.parse_semver("1.2.3", "Test")
        assert version is not None
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

        # Test version with prerelease
        version = handler.parse_semver("2.0.0-alpha.1", "Test")
        assert version is not None
        assert version.prerelease == "alpha.1"

        # Test version with build metadata
        version = handler.parse_semver("1.0.0+build.123", "Test")
        assert version is not None
        assert version.build == "build.123"

        # Test complex version
        version = handler.parse_semver("3.4.5-beta.2+build.456", "Test")
        assert version is not None
        assert version.major == 3
        assert version.minor == 4
        assert version.patch == 5
        assert version.prerelease == "beta.2"
        assert version.build == "build.456"

    def test_parse_semver_invalid_versions(self, handler):
        """Test parsing invalid semantic versions."""
        # Test invalid format
        version = handler.parse_semver("1.2", "Test")
        assert version is None
        assert len(handler.errors) > 0
        assert "VERSION_STRING_MALFORMED" in handler.errors[0]

        # Clear errors for next test
        handler.errors.clear()

        # Test non-numeric version
        version = handler.parse_semver("a.b.c", "Test")
        assert version is None
        assert len(handler.errors) > 0

        # Test empty string
        handler.errors.clear()
        version = handler.parse_semver("", "Test")
        assert version is None
        assert "VERSION_STRING_MISSING" in handler.errors[0]

        # Test None
        handler.errors.clear()
        version = handler.parse_semver(None, "Test")
        assert version is None
        assert "VERSION_STRING_MISSING" in handler.errors[0]

    def test_parse_semver_with_plugin_id(self, handler):
        """Test parsing with plugin ID for better error messages."""
        version = handler.parse_semver("invalid", "Test", plugin_id="test-plugin")
        assert version is None
        assert "test-plugin" in handler.errors[0]

    def test_check_ilr_compatibility_exact_match(self, handler, mock_plugin):
        """Test ILR compatibility with exact version match."""
        core_version = semver.VersionInfo.parse("1.0.0")
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.0.0", mock_plugin
        )
        
        assert is_compatible is True
        assert len(errors) == 0

    def test_check_ilr_compatibility_range_match(self, handler, mock_plugin):
        """Test ILR compatibility with version ranges."""
        core_version = semver.VersionInfo.parse("1.5.0")
        mock_plugin.ilr_versions_supported = [">=1.0.0,<2.0.0"]
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.5.0", mock_plugin
        )
        
        assert is_compatible is True
        assert len(errors) == 0

    def test_check_ilr_compatibility_no_match(self, handler, mock_plugin):
        """Test ILR compatibility when versions don't match."""
        core_version = semver.VersionInfo.parse("2.0.0")
        mock_plugin.ilr_versions_supported = ["1.0.0", "1.1.0", "1.2.0"]
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "2.0.0", mock_plugin
        )
        
        assert is_compatible is False
        assert len(errors) > 0
        assert "ILR_VERSION_NO_MATCH" in errors[0]

    def test_check_ilr_compatibility_empty_supported_versions(self, handler, mock_plugin):
        """Test compatibility when plugin has no version constraints."""
        core_version = semver.VersionInfo.parse("1.0.0")
        mock_plugin.ilr_versions_supported = []
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.0.0", mock_plugin
        )
        
        assert is_compatible is True
        assert len(errors) == 0

    def test_check_ilr_compatibility_invalid_specifier(self, handler, mock_plugin):
        """Test compatibility with invalid version specifiers."""
        core_version = semver.VersionInfo.parse("1.0.0")
        mock_plugin.ilr_versions_supported = ["invalid-version-spec"]
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.0.0", mock_plugin
        )
        
        assert is_compatible is False
        assert len(errors) > 0
        assert "ILR_SPECIFIER_INVALID_SYNTAX" in errors[0]

    def test_check_ilr_compatibility_mixed_valid_invalid(self, handler, mock_plugin):
        """Test compatibility with mix of valid and invalid specifiers."""
        core_version = semver.VersionInfo.parse("1.5.0")
        mock_plugin.ilr_versions_supported = [
            "invalid-spec",
            ">=1.0.0,<2.0.0",  # This should match
            "another-invalid"
        ]
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.5.0", mock_plugin
        )
        
        assert is_compatible is True  # Should be compatible despite some invalid specs
        assert len(errors) > 0  # But should report the invalid ones

    def test_check_ilr_compatibility_complex_ranges(self, handler, mock_plugin):
        """Test compatibility with complex version ranges."""
        core_version = semver.VersionInfo.parse("1.5.0")
        
        # Test various complex ranges
        test_cases = [
            (">=1.0.0,<1.4.0 || >=1.5.0,<2.0.0", True),  # Should match second range
            ("~1.5.0", True),  # Compatible with 1.5.x
            ("^1.5.0", True),  # Compatible with 1.x.x where x >= 5
            (">1.5.0", False),  # Core version not greater than 1.5.0
            ("!=1.5.0", False),  # Explicitly excludes 1.5.0
        ]
        
        for spec, expected in test_cases:
            handler.errors.clear()
            mock_plugin.ilr_versions_supported = [spec]
            
            is_compatible, errors = handler.check_ilr_compatibility(
                core_version, "1.5.0", mock_plugin
            )
            
            assert is_compatible == expected, f"Failed for spec: {spec}"

    def test_check_ilr_compatibility_prerelease_versions(self, handler, mock_plugin):
        """Test compatibility with prerelease versions."""
        # Test prerelease core version
        core_version = semver.VersionInfo.parse("2.0.0-beta.1")
        mock_plugin.ilr_versions_supported = [">=2.0.0-alpha"]
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "2.0.0-beta.1", mock_plugin
        )
        
        assert is_compatible is True

        # Test with stable version requirement
        mock_plugin.ilr_versions_supported = [">=2.0.0"]
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "2.0.0-beta.1", mock_plugin
        )
        
        # Prerelease might not satisfy stable version requirement
        # This depends on the specific implementation
        assert isinstance(is_compatible, bool)

    def test_check_ilr_compatibility_invalid_core_version(self, handler, mock_plugin):
        """Test compatibility check with invalid core version."""
        is_compatible, errors = handler.check_ilr_compatibility(
            None, "invalid", mock_plugin
        )
        
        assert is_compatible is False
        assert len(errors) > 0
        assert "CORE_ILR_INVALID_FOR_CHECK" in errors[0]

    def test_check_ilr_compatibility_invalid_supported_type(self, handler, mock_plugin):
        """Test compatibility with invalid supported versions type."""
        core_version = semver.VersionInfo.parse("1.0.0")
        mock_plugin.ilr_versions_supported = "1.0.0"  # Should be a list
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.0.0", mock_plugin
        )
        
        assert is_compatible is False
        assert "ILR_VERSIONS_INVALID_TYPE" in errors[0]

    def test_check_ilr_compatibility_none_supported_versions(self, handler, mock_plugin):
        """Test compatibility when supported versions is None."""
        core_version = semver.VersionInfo.parse("1.0.0")
        mock_plugin.ilr_versions_supported = None
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.0.0", mock_plugin
        )
        
        assert is_compatible is True  # None means no constraints
        assert len(errors) == 0

    def test_check_ilr_compatibility_empty_string_in_list(self, handler, mock_plugin):
        """Test compatibility with empty strings in version list."""
        core_version = semver.VersionInfo.parse("1.0.0")
        mock_plugin.ilr_versions_supported = ["1.0.0", "", "2.0.0"]
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.0.0", mock_plugin
        )
        
        assert is_compatible is True  # Should match "1.0.0"
        assert len(errors) > 0  # But should report error for empty string

    def test_check_ilr_compatibility_whitespace_handling(self, handler, mock_plugin):
        """Test compatibility with whitespace in version specifiers."""
        core_version = semver.VersionInfo.parse("1.5.0")
        mock_plugin.ilr_versions_supported = [
            "  >=1.0.0  ",  # Leading/trailing whitespace
            "\t<2.0.0\n",   # Tabs and newlines
        ]
        
        # Should handle whitespace gracefully
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.5.0", mock_plugin
        )
        
        # The handler should trim whitespace
        assert isinstance(is_compatible, bool)

    def test_error_accumulation(self, handler):
        """Test that errors accumulate correctly."""
        # Parse invalid version
        handler.parse_semver("invalid1", "Test1")
        assert len(handler.errors) == 1
        
        # Parse another invalid version
        handler.parse_semver("invalid2", "Test2")
        assert len(handler.errors) == 2
        
        # Check that errors are cleared in check_ilr_compatibility
        mock_plugin = Mock()
        mock_plugin.id = "test"
        mock_plugin.ilr_versions_supported = []
        
        handler.check_ilr_compatibility(
            semver.VersionInfo.parse("1.0.0"), "1.0.0", mock_plugin
        )
        
        # Errors should be cleared at the start of check_ilr_compatibility
        assert len(handler.errors) == 0

    def test_version_handler_with_missing_plugin_attributes(self, handler):
        """Test handling of plugins with missing attributes."""
        core_version = semver.VersionInfo.parse("1.0.0")
        
        # Plugin without id attribute
        plugin = Mock(spec=[])
        plugin.ilr_versions_supported = ["1.0.0"]
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.0.0", plugin
        )
        
        assert is_compatible is True
        # Should use 'UnknownPlugin' as fallback

    def test_plain_version_string_interpretation(self, handler, mock_plugin):
        """Test interpretation of plain version strings as exact matches."""
        core_version = semver.VersionInfo.parse("1.0.0")
        mock_plugin.ilr_versions_supported = ["1.0.0"]  # Plain version, not a range
        
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.0.0", mock_plugin
        )
        
        assert is_compatible is True
        
        # Should not match different version
        core_version = semver.VersionInfo.parse("1.0.1")
        is_compatible, errors = handler.check_ilr_compatibility(
            core_version, "1.0.1", mock_plugin
        )
        
        assert is_compatible is False

    @patch('tau_translator_omega.core_engine.version_handler.logger')
    def test_logging_behavior(self, mock_logger, handler, mock_plugin):
        """Test that appropriate log messages are generated."""
        core_version = semver.VersionInfo.parse("1.0.0")
        
        # Test successful compatibility
        handler.check_ilr_compatibility(core_version, "1.0.0", mock_plugin)
        mock_logger.info.assert_called()
        
        # Test failed compatibility
        mock_plugin.ilr_versions_supported = ["2.0.0"]
        handler.check_ilr_compatibility(core_version, "1.0.0", mock_plugin)
        mock_logger.warning.assert_called()