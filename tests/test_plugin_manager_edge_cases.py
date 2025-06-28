import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock
from tau_translator_omega.core_engine.plugins.plugin_manager import PluginManager
from tau_translator_omega.core_engine.plugin import Plugin, PluginEntryPoint


class TestPluginManagerEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_plugin_dirs_list(self):
        """Test initialization with empty plugin dirs list"""
        manager = PluginManager(plugin_dirs=[])
        
        assert len(manager.plugin_roots) == 0
        manager.discover_plugins()
        assert len(manager.plugins) == 0

    def test_mixed_valid_invalid_directories(self, tmp_path):
        """Test with mix of valid and invalid directories"""
        valid_dir = tmp_path / "valid"
        valid_dir.mkdir()
        invalid_dir = tmp_path / "invalid"
        
        manager = PluginManager(plugin_dirs=[valid_dir, invalid_dir])
        manager.discover_plugins()
        
        assert any("PLUGIN_DIR_INVALID" in str(error) for error in manager.errors)

    def test_unicode_in_paths(self, tmp_path):
        """Test plugin discovery with unicode characters in paths and names"""
        plugin_dir_name = "plugin-你好世界"
        plugin_id = "unicode-plugin"
        plugin_name = "Unicode Test Plugin 世界"

        plugin_path = tmp_path / plugin_dir_name
        plugin_path.mkdir()

        manifest_data = {
            "id": plugin_id,
            "name": plugin_name,
            "version": "1.0.0",
            "manifest_version": "1.0",
            "description": "Test unicode plugin",
            "author": "Test Author",
            "license": "MIT",
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"},
            "entry_point": {"type": "cli", "command": "echo hello"}
        }
        
        with open(plugin_path / "manifest.json", 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f)
        
        manager = PluginManager(plugin_dirs=tmp_path)
        manager.discover_plugins()
        
        assert "unicode-plugin" in manager.plugins

    def test_very_deep_nesting(self, tmp_path):
        """Test discovery with very deep directory nesting"""
        # Create deeply nested structure
        deep_path = tmp_path
        for i in range(10):
            deep_path = deep_path / f"level{i}"
        
        deep_path.mkdir(parents=True)

        manifest_data = {
            "id": "deep-plugin",
            "name": "Deep Plugin",
            "version": "1.0.0",
            "manifest_version": "1.0",
            "description": "Test deep nesting plugin",
            "author": "Test Author",
            "license": "MIT",
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"},
            "entry_point": {"type": "cli", "command": "deep"}
        }
        
        with open(deep_path / "manifest.json", 'w') as f:
            json.dump(manifest_data, f)
        
        manager = PluginManager(plugin_dirs=tmp_path)
        manager.discover_plugins()
        
        assert "deep-plugin" in manager.plugins

    def test_concurrent_error_handling(self, tmp_path):
        """Test that errors are properly accumulated"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        # Add multiple errors
        manager._add_error("ERROR1", "First error")
        manager._add_error("ERROR2", "Second error")
        manager._add_error("ERROR3", "Third error")
        
        errors = manager.get_errors()
        assert len(errors) == 3
        assert all(f"ERROR{i+1}" in str(errors[i]) for i in range(3))

    def test_plugin_with_special_characters_in_id(self, tmp_path):
        """Test plugin with special characters in ID"""
        plugin_dir = tmp_path / "special-plugin"
        plugin_dir.mkdir()
        
        manifest_data = {
            "id": "plugin-with-special-chars-123",
            "name": "Special Plugin",
            "version": "1.0.0",
            "manifest_version": "1.0",
            "description": "Test special chars plugin",
            "author": "Test Author",
            "license": "MIT",
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"},
            "entry_point": {"type": "cli", "command": "special"}
        }
        
        with open(plugin_dir / "manifest.json", 'w') as f:
            json.dump(manifest_data, f)
        
        manager = PluginManager(plugin_dirs=tmp_path)
        manager.discover_plugins()
        
        assert "plugin-with-special-chars-123" in manager.plugins

    def test_large_manifest_file(self, tmp_path):
        """Test handling of large manifest file"""
        plugin_dir = tmp_path / "large-plugin"
        plugin_dir.mkdir()
        
        # Create a large manifest with many fields
        manifest_data = {
            "id": "large-plugin",
            "name": "Large Plugin",
            "version": "1.0.0",
            "manifest_version": "1.0",
            "entry_point": {"type": "cli", "command": "large"},
            "description": "x" * 10000,  # Long description
            "author": "Test Author for Large Plugin",
            "license": "MIT",
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"},
            "tags": [f"tag{i}" for i in range(100)],  # Many tags
            "configuration_schema": {
                "type": "object",
                "properties": {
                    f"prop{i}": {"type": "string"} for i in range(100)
                }
            }
        }
        
        with open(plugin_dir / "manifest.json", 'w') as f:
            json.dump(manifest_data, f)
        
        manager = PluginManager(plugin_dirs=tmp_path)
        manager.discover_plugins()
        
        assert "large-plugin" in manager.plugins
        assert len(manager.plugins["large-plugin"].tags) == 100
