import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock
from tau_translator_omega.core_engine.plugins.plugin_manager import PluginManager
from tau_translator_omega.core_engine.plugins.plugin import Plugin, PluginEntryPoint


class TestPluginManagerInvokeTranslation:
    """Test translation invocation functionality"""

    def test_invoke_translation_plugin_not_found(self, tmp_path):
        """Test invoking translation for non-existent plugin"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        result = manager.invoke_translation("non-existent", "source code")
        
        assert result is None
        assert any("Plugin 'non-existent' not found" in str(error) for error in manager.errors)

    def test_invoke_translation_no_instance(self, tmp_path):
        """Test invoking translation when plugin has no instance"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={
                "id": "test-plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "manifest_version": "1.0",
                "description": "Test",
                "author": "Test Author",
                "license": "MIT",
                "target_grammar": {"grammar_name": "generic"},
                "ilr_versions_supported": ["1.0.0"],
                "plugin_type": "generic",
                "output_details": {"format_mime_type": "text/plain"},
                "entry_point": {"type": "cli", "command": "echo 'No instance created'"},
            }
        )
        plugin.instance = None
        manager.plugins["test-plugin"] = plugin
        
        result = manager.invoke_translation("test-plugin", "source code")
        
        assert result is None
        assert any("has no active instance; cannot invoke translation" in str(error) for error in manager.errors)

    def test_invoke_translation_no_translate_method(self, tmp_path):
        """Test invoking translation when plugin has no translate_to_ilr method"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={
                "id": "test-plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "manifest_version": "1.0.0",
                "description": "Test",
                "author": "Test Author",
                "license": "MIT",
                "target_grammar": {"grammar_name": "generic"},
                "ilr_versions_supported": ["1.0.0"],
                "plugin_type": "generic",
                "output_details": {"format_mime_type": "text/plain"},
                "entry_point": {"type": "cli", "command": "echo hello"},
            }
        )
        
        # Create instance without translate_to_ilr method
        plugin.instance = Mock(spec=[])  # No methods
        manager.plugins["test-plugin"] = plugin
        
        result = manager.invoke_translation("test-plugin", "source code")
        
        assert result is None
        assert any("Missing callable 'translate_to_ilr' method" in str(error) for error in manager.errors)

    def test_invoke_translation_non_callable_translate_method(self, tmp_path):
        """Test invoking translation when translate_to_ilr is not callable"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={
                "id": "test-plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "manifest_version": "1.0.0",
                "description": "Test",
                "author": "Test Author",
                "license": "MIT",
                "target_grammar": {"grammar_name": "generic"},
                "ilr_versions_supported": ["1.0.0"],
                "plugin_type": "generic",
                "output_details": {"format_mime_type": "text/plain"},
                "entry_point": {"type": "cli", "command": "echo hello"},
            }
        )
        
        # Create instance with non-callable translate_to_ilr
        plugin.instance = Mock()
        plugin.instance.translate_to_ilr = "not callable"
        manager.plugins["test-plugin"] = plugin
        
        result = manager.invoke_translation("test-plugin", "source code")
        
        assert result is None
        assert any("Missing callable 'translate_to_ilr' method" in str(error) for error in manager.errors)

    def test_invoke_translation_successful(self, tmp_path):
        """Test successful translation invocation"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={
                "id": "test-plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "manifest_version": "1.0.0",
                "description": "Test",
                "author": "Test Author",
                "license": "MIT",
                "target_grammar": {"grammar_name": "generic"},
                "ilr_versions_supported": ["1.0.0"],
                "plugin_type": "generic",
                "entry_point": {"type": "cli", "command": "echo hello"},
            }
        )
        
        # Create instance with working translate_to_ilr method
        plugin.instance = Mock()
        expected_result = {"translated": "data"}
        plugin.instance.translate_to_ilr.return_value = expected_result
        manager.plugins["test-plugin"] = plugin
        
        result = manager.invoke_translation("test-plugin", "source code")
        
        assert result == expected_result
        plugin.instance.translate_to_ilr.assert_called_once_with("source code")

    def test_invoke_translation_method_exception(self, tmp_path):
        """Test handling of exception during translation"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={
                "id": "test-plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "manifest_version": "1.0.0",
                "description": "Test",
                "author": "Test Author",
                "license": "MIT",
                "target_grammar": {"grammar_name": "generic"},
                "ilr_versions_supported": ["1.0.0"],
                "plugin_type": "generic",
                "entry_point": {"type": "cli", "command": "echo hello"},
            }
        )
        
        # Create instance that raises exception
        plugin.instance = Mock()
        plugin.instance.translate_to_ilr.side_effect = ValueError("Translation error")
        manager.plugins["test-plugin"] = plugin
        
        result = manager.invoke_translation("test-plugin", "source code")
        
        assert result is None
        assert any("Runtime error in plugin 'test-plugin'" in str(error) for error in manager.errors)
        assert any("Translation error" in str(error) for error in manager.errors)

    def test_invoke_translation_with_complex_input(self, tmp_path):
        """Test translation with complex input data"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={
                "id": "test-plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "manifest_version": "1.0.0",
                "description": "Test",
                "author": "Test Author",
                "license": "MIT",
                "target_grammar": {"grammar_name": "generic"},
                "ilr_versions_supported": ["1.0.0"],
                "plugin_type": "generic",
                "entry_point": {"type": "cli", "command": "echo hello"},
            }
        )
        
        plugin.instance = Mock()
        plugin.instance.translate_to_ilr.return_value = {"success": True}
        manager.plugins["test-plugin"] = plugin
        
        complex_source = """
        def complex_function(x, y):
            return x + y
        """
        
        result = manager.invoke_translation("test-plugin", complex_source)
        
        assert result == {"success": True}
        plugin.instance.translate_to_ilr.assert_called_once_with(complex_source)

    def test_invoke_translation_none_return(self, tmp_path):
        """Test translation when method returns None"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={
                "id": "test-plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "manifest_version": "1.0.0",
                "description": "Test",
                "author": "Test Author",
                "license": "MIT",
                "target_grammar": {"grammar_name": "generic"},
                "ilr_versions_supported": ["1.0.0"],
                "plugin_type": "generic",
                "entry_point": {"type": "cli", "command": "echo hello"},
            }
        )
        
        plugin.instance = Mock()
        plugin.instance.translate_to_ilr.return_value = None
        manager.plugins["test-plugin"] = plugin
        
        result = manager.invoke_translation("test-plugin", "source code")
        
        assert result is None
        # Should not add error for None return value
        assert not any("Runtime error" in str(error) for error in manager.errors)
