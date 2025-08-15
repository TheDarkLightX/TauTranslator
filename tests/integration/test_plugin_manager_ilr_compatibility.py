import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from tau_translator_omega.core_engine.plugins.plugin_manager import PluginManager
from tau_translator_omega.core_engine.plugin import Plugin, PluginEntryPoint
import semver


class TestPluginManagerILRCompatibility:
    """Test ILR version compatibility checking"""

    base_manifest_data = {
        "manifest_version": "1.0",
        "author": "Test Author",
        "license": "MIT",
        "target_grammar": {"grammar_name": "generic"},
        "plugin_type": "generic",
        "output_details": {"format_mime_type": "text/plain"}
    }

    def test_ilr_compatibility_with_invalid_core_version(self, tmp_path):
        """Test compatibility check when core ILR version is invalid"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="invalid")
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data=self.base_manifest_data.copy(),
            ilr_versions_supported=["1.0.0"]
        )
        
        result = manager._is_ilr_version_compatible(plugin)
        
        assert result is False
        assert any("ILR_CORE_VERSION_INVALID_SKIP_CHECK" in str(error) for error in manager.errors)

    def test_ilr_compatibility_exact_match(self, tmp_path):
        """Test compatibility with exact version match"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0")
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data=self.base_manifest_data.copy(),
            ilr_versions_supported=["1.0.0"]
        )
        
        result = manager._is_ilr_version_compatible(plugin)
        
        assert result is True

    def test_ilr_compatibility_with_range(self, tmp_path):
        """Test compatibility with version range"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.5.0")
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data=self.base_manifest_data.copy(),
            ilr_versions_supported=[">=1.0.0,<2.0.0"]
        )
        
        result = manager._is_ilr_version_compatible(plugin)
        
        assert result is True

    def test_ilr_compatibility_no_match(self, tmp_path):
        """Test compatibility when no version matches"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="2.0.0")
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data=self.base_manifest_data.copy(),
            ilr_versions_supported=["1.0.0", "1.1.0", "1.2.0"]
        )
        
        result = manager._is_ilr_version_compatible(plugin)
        
        assert result is False
        assert any("ILR Incompatibility" in str(error) for error in manager.errors)

    def test_ilr_compatibility_empty_supported_versions(self, tmp_path):
        """Test compatibility when plugin has no supported versions"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0")
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data=self.base_manifest_data.copy(),
            ilr_versions_supported=[]
        )
        
        result = manager._is_ilr_version_compatible(plugin)
        
        assert result is True  # Empty list means no constraints

    def test_ilr_compatibility_with_malformed_specifier(self, tmp_path):
        """Test compatibility with malformed version specifier results in error and incompatibility"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0")
    
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data=self.base_manifest_data.copy(),
            ilr_versions_supported=["invalid-specifier"]
        )
    
        result = manager._is_ilr_version_compatible(plugin)
    
        assert result is False
        # Check that an error about invalid specifier was added
        assert any("ILR Incompatibility" in str(error) and "invalid-specifier" in str(error) for error in manager.errors)

    def test_ilr_compatibility_multiple_valid_specifiers(self, tmp_path):
        """Test compatibility with multiple valid specifiers"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.5.0")
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data=self.base_manifest_data.copy(),
            ilr_versions_supported=[">=1.0.0,<1.5.0", "==1.2.3"]
        )
        
        result = manager._is_ilr_version_compatible(plugin)
        
        assert result is False

    def test_ilr_compatibility_with_prerelease_version(self, tmp_path):
        """Test compatibility with prerelease versions"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0-alpha.1")
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data=self.base_manifest_data.copy(),
            ilr_versions_supported=[">=1.0.0-alpha"]
        )
        
        result = manager._is_ilr_version_compatible(plugin)
        
        assert result is True

    def test_ilr_compatibility_with_grammar_plugin(self, tmp_path):
        """Test compatibility check for grammar definition plugin"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0")

        grammar_manifest_data = self.base_manifest_data.copy()
        grammar_manifest_data["plugin_type"] = "grammar_definition"
        # Example: A grammar plugin might target a specific grammar it defines or extends
        grammar_manifest_data["grammar_config"] = {
            "ilr_version": "1.0.0",
            "construct_schema_path": "/path/to/schema",
            "definition_provider": {
                "format": "yaml",
                "root_directory": "/path/to/defs",
                "file_mappings": []
            }
        }

        # Create a mock Plugin object for testing _is_ilr_version_compatible
        plugin = Plugin(
            id="grammar-plugin",
            name="Grammar Plugin",
            version="0.1.0",
            description="A test grammar plugin.",
            entry_point=PluginEntryPoint(type="grammar_definition"), # Simplified for test
            manifest_path=Path(tmp_path / "grammar-plugin/manifest.json"),
            plugin_dir=Path(tmp_path / "grammar-plugin"),
            manifest_data=grammar_manifest_data,
            plugin_type="grammar_definition",
            ilr_versions_supported=["1.0.0"]
        )
        
        # Set the plugin_specific_config after creation
        plugin.plugin_specific_config = {
            "ilr_version": "1.0.0",
            "construct_schema_path": "/path/to/schema",
            "definition_provider": {
                "format": "yaml",
                "root_directory": "/path/to/defs",
                "file_mappings": []
            }
        }
        
        result = manager._is_ilr_version_compatible(plugin)
        
        assert result is True

    def test_ilr_compatibility_transfers_version_handler_errors(self, tmp_path):
        """Test that errors from version_handler are properly transferred"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0")
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data=self.base_manifest_data.copy(),
            ilr_versions_supported=["not-a-valid-version"]
        )
        
        # Mock version_handler to return specific errors
        with patch.object(manager.version_handler, 'check_ilr_compatibility') as mock_check:
            mock_check.return_value = (False, ["Test error from version handler"])
            
            result = manager._is_ilr_version_compatible(plugin)
            
            assert result is False
            assert any("ILR Incompatibility" in str(error) and "Test error from version handler" in str(error) for error in manager.errors)


class TestPluginManagerCoreVersionParsing:
    """Test core ILR version parsing during initialization"""

    def test_core_version_valid_semver(self, tmp_path):
        """Test parsing valid semantic version"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.2.3")
        
        assert manager.core_ilr_semver is not None
        assert manager.core_ilr_semver.major == 1
        assert manager.core_ilr_semver.minor == 2
        assert manager.core_ilr_semver.patch == 3

    def test_core_version_with_prerelease(self, tmp_path):
        """Test parsing version with prerelease"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="2.0.0-beta.1")
        
        assert manager.core_ilr_semver is not None
        assert manager.core_ilr_semver.major == 2
        assert manager.core_ilr_semver.minor == 0
        assert manager.core_ilr_semver.patch == 0
        assert manager.core_ilr_semver.prerelease == "beta.1"

    def test_core_version_with_build_metadata(self, tmp_path):
        """Test parsing version with build metadata"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0+build.123")
        
        assert manager.core_ilr_semver is not None
        assert manager.core_ilr_semver.build == "build.123"

    def test_core_version_invalid_format(self, tmp_path):
        """Test parsing invalid version format"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.2")
        
        assert manager.core_ilr_semver is None
        assert len(manager.errors) > 0

    def test_core_version_empty_string(self, tmp_path):
        """Test parsing empty version string"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="")
        
        assert manager.core_ilr_semver is None
        assert len(manager.errors) > 0

    def test_core_version_non_numeric(self, tmp_path):
        """Test parsing non-numeric version"""
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="abc.def.ghi")
        
        assert manager.core_ilr_semver is None
        assert len(manager.errors) > 0
