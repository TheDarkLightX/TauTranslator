"""
BDD-style unit tests for refactored plugin manager.

These tests follow Given-When-Then structure and focus on behavior rather than implementation.
Tests are designed to be mutation-resistant and cover edge cases comprehensively.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime
import tempfile
import os

# Import components under test
from .manager import (
    PluginManager, PluginError, ErrorCode, ErrorMessage, PluginId,
    ManifestPath, PluginDirectory, ValidationResult,
    ManifestFileRepository, PluginValidator, PluginRegistry
)
from src.tau_translator_omega.core_engine.plugin import Plugin
from returns.result import Success, Failure


class TestPluginDiscoveryBehavior:
    """BDD tests for plugin discovery behavior."""
    
    def test_given_empty_directory_when_discovering_plugins_then_returns_empty_dict(self, tmp_path):
        """Given an empty directory, when discovering plugins, then returns empty dict."""
        # Given: An empty plugin directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        manager = PluginManager(plugin_dirs=str(empty_dir))
        
        # When: Discovering plugins
        discovered_plugins = manager.discover_plugins()
        
        # Then: No plugins are found
        assert discovered_plugins == {}
        assert len(manager.get_errors()) == 0
    
    def test_given_multiple_valid_plugins_when_discovering_then_all_are_loaded(self, tmp_path):
        """Given multiple valid plugins, when discovering, then all are loaded."""
        # Given: Multiple plugin directories with valid manifests
        plugin_configs = [
            {"id": "plugin-alpha", "name": "Alpha Plugin", "version": "1.0.0", "plugin_type": "generic"},
            {"id": "plugin-beta", "name": "Beta Plugin", "version": "2.0.0", "plugin_type": "generic"},
            {"id": "plugin-gamma", "name": "Gamma Plugin", "version": "3.0.0", "plugin_type": "generic"}
        ]
        
        for config in plugin_configs:
            plugin_dir = tmp_path / config["id"]
            plugin_dir.mkdir()
            manifest_path = plugin_dir / "manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(config, f)
        
        # Mock validator to accept all plugins
        with patch.object(PluginValidator, 'validate_plugin') as mock_validate:
            mock_validate.return_value = ValidationResult(success=True, config={})
            
            manager = PluginManager(plugin_dirs=str(tmp_path))
            
            # When: Discovering plugins
            discovered_plugins = manager.discover_plugins()
            
            # Then: All plugins are discovered
            assert len(discovered_plugins) == 3
            assert all(config["id"] in discovered_plugins for config in plugin_configs)
    
    def test_given_invalid_json_manifest_when_discovering_then_error_is_logged(self, tmp_path):
        """Given invalid JSON in manifest, when discovering, then error is logged."""
        # Given: A plugin with malformed JSON manifest
        plugin_dir = tmp_path / "broken-plugin"
        plugin_dir.mkdir()
        manifest_path = plugin_dir / "manifest.json"
        
        with open(manifest_path, 'w') as f:
            f.write("{ invalid json content")
        
        manager = PluginManager(plugin_dirs=str(tmp_path))
        
        # When: Discovering plugins
        discovered_plugins = manager.discover_plugins()
        
        # Then: No plugins are loaded and error is recorded
        assert len(discovered_plugins) == 0
        errors = manager.get_errors()
        assert len(errors) == 1
        assert errors[0].code == "MANIFEST_MALFORMED"
    
    def test_given_nested_plugin_structure_when_discovering_then_finds_all_manifests(self, tmp_path):
        """Given nested plugin structure, when discovering, then finds all manifests."""
        # Given: Nested directory structure with plugins at different levels
        structures = [
            "plugins/core/auth-plugin",
            "plugins/extensions/data-plugin",
            "plugins/community/viz-plugin"
        ]
        
        for structure in structures:
            plugin_path = tmp_path / structure
            plugin_path.mkdir(parents=True)
            manifest_path = plugin_path / "manifest.json"
            
            plugin_id = structure.split('/')[-1]
            manifest_data = {
                "id": plugin_id,
                "name": f"{plugin_id} Plugin",
                "version": "1.0.0",
                "plugin_type": "generic"
            }
            
            with open(manifest_path, 'w') as f:
                json.dump(manifest_data, f)
        
        with patch.object(PluginValidator, 'validate_plugin') as mock_validate:
            mock_validate.return_value = ValidationResult(success=True, config={})
            
            manager = PluginManager(plugin_dirs=str(tmp_path))
            
            # When: Discovering plugins
            discovered_plugins = manager.discover_plugins()
            
            # Then: All nested plugins are found
            assert len(discovered_plugins) == 3
            assert "auth-plugin" in discovered_plugins
            assert "data-plugin" in discovered_plugins
            assert "viz-plugin" in discovered_plugins


class TestPluginValidationBehavior:
    """BDD tests for plugin validation behavior."""
    
    def test_given_plugin_without_type_when_validating_then_validation_fails(self):
        """Given plugin without type, when validating, then validation fails."""
        # Given: A manifest without plugin_type
        manifest_data = {
            "id": "typeless-plugin",
            "name": "Typeless Plugin",
            "version": "1.0.0"
            # Missing plugin_type
        }
        
        plugin = Mock(spec=Plugin)
        validator = PluginValidator({})
        
        # When: Validating the plugin
        result = validator.validate_plugin(
            plugin,
            manifest_data,
            PluginDirectory(Path("/tmp"))
        )
        
        # Then: Validation fails with appropriate error
        assert result.success is False
        assert len(result.errors) == 1
        assert "Missing plugin_type" in result.errors[0]
    
    def test_given_plugin_with_unknown_type_when_generic_validator_exists_then_uses_generic(self):
        """Given plugin with unknown type, when generic validator exists, then uses generic."""
        # Given: A plugin with unknown type and a generic validator
        manifest_data = {
            "id": "custom-plugin",
            "plugin_type": "custom-unknown-type"
        }
        
        plugin = Mock(spec=Plugin)
        mock_generic_validator = Mock()
        mock_generic_validator.validate_manifest.return_value = (True, {"validated": True}, [])
        
        validator = PluginValidator({"generic": mock_generic_validator})
        
        # When: Validating the plugin
        result = validator.validate_plugin(
            plugin,
            manifest_data,
            PluginDirectory(Path("/tmp"))
        )
        
        # Then: Generic validator is used and validation succeeds
        assert result.success is True
        assert result.config == {"validated": True}
        mock_generic_validator.validate_manifest.assert_called_once()
    
    def test_given_validator_throws_exception_when_validating_then_returns_failure(self):
        """Given validator throws exception, when validating, then returns failure."""
        # Given: A validator that throws an exception
        manifest_data = {"plugin_type": "faulty"}
        plugin = Mock(spec=Plugin)
        
        mock_validator = Mock()
        mock_validator.validate_manifest.side_effect = RuntimeError("Validator crashed")
        
        validator = PluginValidator({"faulty": mock_validator})
        
        # When: Validating the plugin
        result = validator.validate_plugin(
            plugin,
            manifest_data,
            PluginDirectory(Path("/tmp"))
        )
        
        # Then: Validation fails gracefully
        assert result.success is False
        assert len(result.errors) == 1
        assert "Validation exception" in result.errors[0]
        assert "Validator crashed" in result.errors[0]


class TestPluginLoadingBehavior:
    """BDD tests for plugin loading behavior."""
    
    def test_given_plugin_with_valid_module_when_loading_then_instance_is_created(self):
        """Given plugin with valid module, when loading, then instance is created."""
        # Given: A plugin with valid entry point and module
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir) / "test-plugin"
            plugin_dir.mkdir()
            
            # Create plugin module
            module_path = plugin_dir / "plugin_module.py"
            with open(module_path, 'w') as f:
                f.write("""
class TestPlugin:
    def __init__(self, config_value=None):
        self.config_value = config_value
        self.initialized = True
    
    def translate_to_ilr(self, source):
        return {"source": source, "translated": True}
""")
            
            # Create manifest
            manifest_data = {
                "id": "test-plugin",
                "name": "Test Plugin",
                "version": "1.0.0",
                "plugin_type": "generic",
                "entry_point": {
                    "type": "module",
                    "module_path": "plugin_module.py",
                    "class_name": "TestPlugin"
                }
            }
            
            manifest_path = plugin_dir / "manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest_data, f)
            
            # Mock validator
            with patch.object(PluginValidator, 'validate_plugin') as mock_validate:
                mock_validate.return_value = ValidationResult(
                    success=True,
                    config={"config_value": "test"}
                )
                
                manager = PluginManager(plugin_dirs=str(temp_dir))
                
                # When: Discovering and loading plugins
                discovered = manager.discover_plugins()
                
                # Then: Plugin is loaded with instance
                assert len(discovered) == 1
                plugin = discovered["test-plugin"]
                assert plugin.instance is not None
                assert hasattr(plugin.instance, 'initialized')
                assert plugin.instance.initialized is True
                assert plugin.instance.config_value == "test"
    
    def test_given_plugin_missing_required_class_when_loading_then_error_is_logged(self):
        """Given plugin missing required class, when loading, then error is logged."""
        # Given: A plugin module without the specified class
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir) / "incomplete-plugin"
            plugin_dir.mkdir()
            
            # Create module without required class
            module_path = plugin_dir / "incomplete.py"
            with open(module_path, 'w') as f:
                f.write("""
class WrongClassName:
    pass
""")
            
            manifest_data = {
                "id": "incomplete-plugin",
                "name": "Incomplete Plugin",
                "version": "1.0.0",
                "plugin_type": "generic",
                "entry_point": {
                    "type": "module",
                    "module_path": "incomplete.py",
                    "class_name": "MissingClass"  # This class doesn't exist
                }
            }
            
            manifest_path = plugin_dir / "manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest_data, f)
            
            with patch.object(PluginValidator, 'validate_plugin') as mock_validate:
                mock_validate.return_value = ValidationResult(success=True)
                
                manager = PluginManager(plugin_dirs=str(temp_dir))
                
                # When: Discovering plugins
                discovered = manager.discover_plugins()
                
                # Then: Plugin is not loaded and error is recorded
                assert len(discovered) == 1  # Plugin is discovered
                plugin = discovered["incomplete-plugin"]
                assert plugin.instance is None  # But instance is not created
                
                errors = manager.get_errors()
                assert any(e.code == "CLASS_NOT_FOUND" for e in errors)
    
    def test_given_cyclic_imports_when_loading_plugins_then_handles_gracefully(self):
        """Given cyclic imports, when loading plugins, then handles gracefully."""
        # Given: Two plugins with cyclic imports
        with tempfile.TemporaryDirectory() as temp_dir:
            # Plugin A imports Plugin B
            plugin_a_dir = Path(temp_dir) / "plugin-a"
            plugin_a_dir.mkdir()
            
            with open(plugin_a_dir / "module_a.py", 'w') as f:
                f.write("""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'plugin-b'))
from module_b import PluginB

class PluginA:
    def __init__(self):
        self.dependency = PluginB()
""")
            
            with open(plugin_a_dir / "manifest.json", 'w') as f:
                json.dump({
                    "id": "plugin-a",
                    "plugin_type": "generic",
                    "entry_point": {
                        "type": "module",
                        "module_path": "module_a.py",
                        "class_name": "PluginA"
                    }
                }, f)
            
            # Plugin B imports Plugin A
            plugin_b_dir = Path(temp_dir) / "plugin-b"
            plugin_b_dir.mkdir()
            
            with open(plugin_b_dir / "module_b.py", 'w') as f:
                f.write("""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'plugin-a'))
from module_a import PluginA

class PluginB:
    def __init__(self):
        self.dependency = PluginA()
""")
            
            with open(plugin_b_dir / "manifest.json", 'w') as f:
                json.dump({
                    "id": "plugin-b",
                    "plugin_type": "generic",
                    "entry_point": {
                        "type": "module",
                        "module_path": "module_b.py",
                        "class_name": "PluginB"
                    }
                }, f)
            
            with patch.object(PluginValidator, 'validate_plugin') as mock_validate:
                mock_validate.return_value = ValidationResult(success=True)
                
                manager = PluginManager(plugin_dirs=str(temp_dir))
                
                # When: Discovering plugins (should handle cyclic imports)
                discovered = manager.discover_plugins()
                
                # Then: Manager handles the situation without crashing
                # At least one plugin should fail to load due to import error
                errors = manager.get_errors()
                assert len(errors) > 0
                assert any("IMPORT" in e.code or "INSTANTIATION" in e.code for e in errors)


class TestPluginInvocationBehavior:
    """BDD tests for plugin invocation behavior."""
    
    def test_given_registered_plugin_with_translate_method_when_invoking_then_returns_result(self):
        """Given registered plugin with translate method, when invoking, then returns result."""
        # Given: A plugin with a working translate_to_ilr method
        plugin = Mock(spec=Plugin)
        plugin.id = "translator-plugin"
        
        instance = Mock()
        instance.translate_to_ilr.return_value = {
            "ilr": {"type": "program", "statements": []},
            "metadata": {"version": "1.0"}
        }
        plugin.instance = instance
        
        manager = PluginManager(plugin_dirs=[])
        manager._registry.register(plugin)
        
        # When: Invoking translation
        tau_source = "DEFINE concept AS true"
        result = manager.invoke_translation("translator-plugin", tau_source)
        
        # Then: Translation result is returned
        assert result is not None
        assert "ilr" in result
        assert result["ilr"]["type"] == "program"
        instance.translate_to_ilr.assert_called_once_with(tau_source)
    
    def test_given_plugin_without_translate_method_when_invoking_then_returns_none_and_logs_error(self):
        """Given plugin without translate method, when invoking, then returns None and logs error."""
        # Given: A plugin instance without translate_to_ilr method
        plugin = Mock(spec=Plugin)
        plugin.id = "incomplete-plugin"
        
        instance = Mock()
        # Remove translate_to_ilr method
        del instance.translate_to_ilr
        plugin.instance = instance
        
        manager = PluginManager(plugin_dirs=[])
        manager._registry.register(plugin)
        
        # When: Invoking translation
        result = manager.invoke_translation("incomplete-plugin", "source")
        
        # Then: Returns None and logs error
        assert result is None
        errors = manager.get_errors()
        assert len(errors) == 1
        assert errors[0].code == "NO_TRANSLATE_METHOD"
    
    def test_given_translate_method_throws_exception_when_invoking_then_returns_none_and_logs_error(self):
        """Given translate method throws exception, when invoking, then returns None and logs error."""
        # Given: A plugin that throws during translation
        plugin = Mock(spec=Plugin)
        plugin.id = "faulty-plugin"
        
        instance = Mock()
        instance.translate_to_ilr.side_effect = ValueError("Invalid TAU syntax")
        plugin.instance = instance
        
        manager = PluginManager(plugin_dirs=[])
        manager._registry.register(plugin)
        
        # When: Invoking translation
        result = manager.invoke_translation("faulty-plugin", "invalid source")
        
        # Then: Returns None and logs the exception
        assert result is None
        errors = manager.get_errors()
        assert len(errors) == 1
        assert errors[0].code == "TRANSLATION_ERROR"
        assert "Invalid TAU syntax" in errors[0].message


class TestEdgeCasesAndBoundaryConditions:
    """Tests for edge cases and boundary conditions."""
    
    def test_given_empty_manifest_when_parsing_then_handles_gracefully(self, tmp_path):
        """Given empty manifest file, when parsing, then handles gracefully."""
        # Given: An empty manifest file
        plugin_dir = tmp_path / "empty-manifest"
        plugin_dir.mkdir()
        manifest_path = plugin_dir / "manifest.json"
        
        with open(manifest_path, 'w') as f:
            f.write("{}")  # Empty JSON object
        
        manager = PluginManager(plugin_dirs=str(tmp_path))
        
        # When: Discovering plugins
        discovered = manager.discover_plugins()
        
        # Then: No crash, appropriate errors logged
        assert len(discovered) == 0
        # Should have errors about missing required fields
        errors = manager.get_errors()
        assert len(errors) > 0
    
    def test_given_unicode_in_plugin_metadata_when_loading_then_handles_correctly(self, tmp_path):
        """Given unicode in plugin metadata, when loading, then handles correctly."""
        # Given: Plugin with unicode characters in metadata
        plugin_dir = tmp_path / "unicode-plugin"
        plugin_dir.mkdir()
        
        manifest_data = {
            "id": "unicode-test",
            "name": "测试插件 🔌",
            "description": "Plugin for testing émojis and 中文",
            "author": "محمد أحمد",
            "version": "1.0.0",
            "plugin_type": "generic"
        }
        
        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, ensure_ascii=False)
        
        with patch.object(PluginValidator, 'validate_plugin') as mock_validate:
            mock_validate.return_value = ValidationResult(success=True)
            
            manager = PluginManager(plugin_dirs=str(tmp_path))
            
            # When: Discovering plugins
            discovered = manager.discover_plugins()
            
            # Then: Unicode is preserved correctly
            assert len(discovered) == 1
            plugin = discovered["unicode-test"]
            assert plugin.name == "测试插件 🔌"
            assert "émojis" in plugin.description
            assert "中文" in plugin.description
    
    def test_given_very_long_plugin_id_when_registering_then_handles_appropriately(self):
        """Given very long plugin ID, when registering, then handles appropriately."""
        # Given: A plugin with extremely long ID
        very_long_id = "x" * 1000  # 1000 character ID
        
        plugin = Mock(spec=Plugin)
        plugin.id = very_long_id
        
        registry = PluginRegistry()
        
        # When: Registering plugin
        result = registry.register(plugin)
        
        # Then: Registration succeeds (no arbitrary length limits)
        assert isinstance(result, Success)
        assert registry.get(PluginId(very_long_id)) == plugin
    
    def test_given_plugin_with_null_values_when_loading_then_handles_defaults(self, tmp_path):
        """Given plugin with null values, when loading, then handles defaults."""
        # Given: Manifest with null/None values
        plugin_dir = tmp_path / "null-plugin"
        plugin_dir.mkdir()
        
        manifest_data = {
            "id": "null-test",
            "name": "Null Test Plugin",
            "version": "1.0.0",
            "plugin_type": "generic",
            "description": None,  # Explicit null
            "author": None,
            "config": {}
        }
        
        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f)
        
        with patch.object(PluginValidator, 'validate_plugin') as mock_validate:
            mock_validate.return_value = ValidationResult(success=True)
            
            # Need to also patch Plugin.from_manifest to handle this case
            with patch('src.tau_translator_omega.core_engine.plugin.Plugin.from_manifest') as mock_from_manifest:
                mock_plugin = Mock(spec=Plugin)
                mock_plugin.id = "null-test"
                mock_plugin.plugin_type = "generic"
                mock_plugin.manifest_path = manifest_path
                mock_plugin.entry_point = None
                mock_from_manifest.return_value = mock_plugin
                
                manager = PluginManager(plugin_dirs=str(tmp_path))
                
                # When: Discovering plugins
                discovered = manager.discover_plugins()
                
                # Then: Plugin loads with appropriate defaults
                assert len(discovered) == 1
                assert "null-test" in discovered


class TestPerformanceCharacteristics:
    """Tests to ensure performance characteristics are maintained."""
    
    def test_given_many_plugins_when_discovering_then_completes_in_reasonable_time(self, tmp_path):
        """Given many plugins, when discovering, then completes in reasonable time."""
        import time
        
        # Given: 50 plugins to discover
        for i in range(50):
            plugin_dir = tmp_path / f"plugin-{i}"
            plugin_dir.mkdir()
            
            manifest_data = {
                "id": f"plugin-{i}",
                "name": f"Plugin {i}",
                "version": "1.0.0",
                "plugin_type": "generic"
            }
            
            with open(plugin_dir / "manifest.json", 'w') as f:
                json.dump(manifest_data, f)
        
        with patch.object(PluginValidator, 'validate_plugin') as mock_validate:
            mock_validate.return_value = ValidationResult(success=True)
            
            manager = PluginManager(plugin_dirs=str(tmp_path))
            
            # When: Timing plugin discovery
            start_time = time.time()
            discovered = manager.discover_plugins()
            elapsed_time = time.time() - start_time
            
            # Then: Discovery completes quickly
            assert len(discovered) == 50
            assert elapsed_time < 2.0  # Should complete within 2 seconds
    
    def test_given_concurrent_plugin_operations_when_accessing_registry_then_thread_safe(self):
        """Given concurrent plugin operations, when accessing registry, then thread safe."""
        import threading
        import random
        
        manager = PluginManager(plugin_dirs=[])
        errors = []
        
        def register_plugins():
            try:
                for i in range(10):
                    plugin = Mock(spec=Plugin)
                    plugin.id = f"thread-{threading.get_ident()}-{i}"
                    manager._registry.register(plugin)
                    # Random sleep to increase chance of race conditions
                    time.sleep(random.uniform(0.0001, 0.001))
            except Exception as e:
                errors.append(e)
        
        def read_plugins():
            try:
                for _ in range(20):
                    all_plugins = manager.get_all_plugins()
                    # Verify data integrity
                    assert isinstance(all_plugins, list)
                    time.sleep(random.uniform(0.0001, 0.001))
            except Exception as e:
                errors.append(e)
        
        # When: Running concurrent operations
        threads = []
        
        # Create writer threads
        for _ in range(3):
            t = threading.Thread(target=register_plugins)
            threads.append(t)
            t.start()
        
        # Create reader threads
        for _ in range(2):
            t = threading.Thread(target=read_plugins)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Then: No errors occurred
        assert len(errors) == 0
        
        # Verify final state
        all_plugins = manager.get_all_plugins()
        assert len(all_plugins) == 30  # 3 threads * 10 plugins each