import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
from tau_translator_omega.core_engine.plugin_manager import PluginManager


class TestPluginManagerDiscovery:
    """Test plugin discovery functionality"""

    def test_discover_plugins_clears_existing(self, tmp_path):
        """Test that discover_plugins clears existing plugins and errors"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        # Add some existing data
        manager.plugins["existing"] = Mock()
        manager.errors.append("Existing error")
        
        manager.discover_plugins()
        
        assert "existing" not in manager.plugins
        assert "Existing error" not in manager.errors

    def test_discover_plugins_invalid_directory(self, tmp_path):
        """Test discovery with non-existent directory"""
        invalid_dir = tmp_path / "nonexistent"
        manager = PluginManager(plugin_dirs=invalid_dir)
        
        manager.discover_plugins()
        
        assert len(manager.plugins) == 0
        assert any("PLUGIN_DIR_INVALID" in str(error) for error in manager.errors)
        assert any(str(invalid_dir) in str(e) for e in manager.errors)

    def test_discover_plugins_file_instead_of_directory(self, tmp_path):
        """Test discovery when path is a file instead of directory"""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("content")
        
        manager = PluginManager(plugin_dirs=file_path)
        
        manager.discover_plugins()
        
        assert len(manager.plugins) == 0
        assert any("PLUGIN_DIR_INVALID" in str(error) for error in manager.errors)

    def test_discover_plugins_empty_directory(self, tmp_path):
        """Test discovery in empty directory"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        manager.discover_plugins()
        
        assert len(manager.plugins) == 0
        assert len(manager.errors) == 0

    def test_discover_plugins_single_valid_plugin(self, tmp_path):
        """Test discovery of single valid plugin"""
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()
        
        manifest_data = {
            "id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "manifest_version": "1.0",
            "description": "A test plugin.",
            "author": "Test Author",
            "license": "MIT",
            "entry_point": {
                "type": "cli",
                "command": "test"
            },
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"}
        }
        
        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f)
        
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0")
        manager.discover_plugins()
        
        assert len(manager.plugins) == 1
        assert "test-plugin" in manager.plugins
        assert manager.plugins["test-plugin"].name == "Test Plugin"

    def test_discover_plugins_multiple_plugins(self, tmp_path):
        """Test discovery of multiple plugins"""
        # Create first plugin
        plugin1_dir = tmp_path / "plugin1"
        plugin1_dir.mkdir()
        manifest1 = {
            "id": "plugin-1",
            "name": "Plugin 1",
            "version": "1.0.0",
            "manifest_version": "1.0",
            "description": "Plugin one.",
            "author": "Test Author",
            "license": "MIT",
            "entry_point": {"type": "cli", "command": "cmd1"},
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"}
        }
        with open(plugin1_dir / "manifest.json", 'w') as f:
            json.dump(manifest1, f)
        
        # Create second plugin
        plugin2_dir = tmp_path / "plugin2"
        plugin2_dir.mkdir()
        manifest2 = {
            "id": "plugin-2",
            "name": "Plugin 2",
            "version": "1.0.0",
            "manifest_version": "1.0",
            "description": "Plugin two.",
            "author": "Test Author",
            "license": "MIT",
            "entry_point": {"type": "cli", "command": "cmd2"},
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"}
        }
        with open(plugin2_dir / "manifest.json", 'w') as f:
            json.dump(manifest2, f)
        
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0")
        manager.discover_plugins()
        
        assert len(manager.plugins) == 2
        assert "plugin-1" in manager.plugins
        assert "plugin-2" in manager.plugins

    def test_discover_plugins_nested_directories(self, tmp_path):
        """Test discovery in nested directory structure"""
        # Create nested plugin structure
        nested_dir = tmp_path / "category" / "subcategory" / "plugin"
        nested_dir.mkdir(parents=True)
        
        manifest_data = {
            "id": "nested-plugin",
            "name": "Nested Plugin",
            "version": "1.0.0",
            "manifest_version": "1.0",
            "description": "A nested plugin.",
            "author": "Test Author",
            "license": "MIT",
            "entry_point": {"type": "cli", "command": "nested"},
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"}
        }
        
        with open(nested_dir / "manifest.json", 'w') as f:
            json.dump(manifest_data, f)
        
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0")
        manager.discover_plugins()
        
        assert len(manager.plugins) == 1
        assert "nested-plugin" in manager.plugins

    def test_discover_plugins_duplicate_ids(self, tmp_path):
        """Test handling of duplicate plugin IDs"""
        # Create first plugin
        plugin1_dir = tmp_path / "plugin1"
        plugin1_dir.mkdir()
        manifest = {
            "id": "duplicate-id",
            "name": "Plugin 1",
            "version": "1.0.0",
            "manifest_version": "1.0",
            "description": "First plugin with duplicate ID.",
            "author": "Test Author",
            "license": "MIT",
            "entry_point": {"type": "cli", "command": "cmd1"},
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"}
        }
        with open(plugin1_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f)
        
        # Create second plugin with same ID
        plugin2_dir = tmp_path / "plugin2"
        plugin2_dir.mkdir()
        manifest_plugin2 = {
            "id": "duplicate-id", # Same ID
            "name": "Plugin 2",    # Different name
            "version": "1.0.0",
            "manifest_version": "1.0",
            "description": "Second plugin with duplicate ID.",
            "author": "Test Author",
            "license": "MIT",
            "entry_point": {"type": "cli", "command": "cmd2"}, # Different command
            "target_grammar": {"grammar_name": "generic"},
            "ilr_versions_supported": ["1.0.0"],
            "plugin_type": "generic",
            "output_details": {"format_mime_type": "text/plain"}
        }
        with open(plugin2_dir / "manifest.json", 'w') as f:
            json.dump(manifest_plugin2, f)
        
        manager = PluginManager(plugin_dirs=tmp_path, core_ilr_version="1.0.0")
        manager.discover_plugins()
        
        # Only first plugin should be loaded (duplicate IDs are skipped)
        assert len(manager.plugins) == 1
        assert manager.plugins["duplicate-id"].name == "Plugin 1"