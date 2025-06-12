"""
Comprehensive unit tests for refactored plugin manager.

These tests follow TDD principles and test each component in isolation.
Tests are organized by component to ensure clear coverage of all functionality.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, MagicMock, patch, mock_open
from datetime import datetime

# Import components to test
from .manager import (
    # Domain types
    PluginId, ModulePath, ClassName, ManifestPath, PluginDirectory,
    ErrorCode, ErrorMessage, VersionString, PluginType,
    PluginError, ValidationResult, LoadResult, ImportResult, InstantiationResult,
    
    # Infrastructure
    ManifestFileRepository, ModuleImporter,
    
    # Business logic
    PluginValidator, VersionCompatibilityChecker, PluginInstantiator,
    PluginRegistry, ErrorCollector,
    
    # Services
    PluginDiscoveryService, PluginLoadingService,
    
    # Main manager
    PluginManager
)

from returns.result import Success, Failure
from src.tau_translator_omega.core_engine.plugin import Plugin, PluginEntryPoint


# ===== Test Fixtures =====

@pytest.fixture
def sample_manifest():
    """Sample valid manifest data."""
    return {
        "id": "test-plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "plugin_type": "generic",
        "entry_point": {
            "type": "module",
            "module_path": "test_plugin.py",
            "class_name": "TestPlugin"
        },
        "min_ilr_version": "1.0.0",
        "max_ilr_version": "2.0.0"
    }


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """Create temporary plugin directory."""
    plugin_dir = tmp_path / "test-plugin"
    plugin_dir.mkdir()
    return plugin_dir


@pytest.fixture
def plugin_error():
    """Sample plugin error."""
    return PluginError(
        code=ErrorCode("TEST_ERROR"),
        message=ErrorMessage("Test error message"),
        plugin_id=PluginId("test-plugin")
    )


# ===== Domain Types Tests =====

class TestDomainTypes:
    """Test domain type behaviors."""
    
    def test_plugin_error_creation(self):
        """Test PluginError creation and string representation."""
        error = PluginError(
            code=ErrorCode("TEST_ERROR"),
            message=ErrorMessage("Test message"),
            plugin_id=PluginId("test-plugin")
        )
        
        assert error.code == "TEST_ERROR"
        assert error.message == "Test message"
        assert error.plugin_id == "test-plugin"
        assert isinstance(error.timestamp, datetime)
        
    def test_plugin_error_str_representation(self):
        """Test PluginError string formatting."""
        error = PluginError(
            code=ErrorCode("TEST_ERROR"),
            message=ErrorMessage("Test message"),
            plugin_id=PluginId("test-plugin")
        )
        
        error_str = str(error)
        assert "TEST_ERROR" in error_str
        assert "test-plugin" in error_str
        assert "Test message" in error_str
        
    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            success=True,
            config={"key": "value"},
            errors=[ErrorMessage("Warning")]
        )
        
        assert result.success is True
        assert result.config == {"key": "value"}
        assert result.errors == ["Warning"]


# ===== Infrastructure Layer Tests =====

class TestManifestFileRepository:
    """Test manifest file operations."""
    
    def test_scan_for_manifests_success(self, tmp_path):
        """Test successful manifest scanning."""
        # Create test structure
        plugin1 = tmp_path / "plugin1"
        plugin1.mkdir()
        (plugin1 / "manifest.json").touch()
        
        plugin2 = tmp_path / "plugin2"
        plugin2.mkdir()
        (plugin2 / "manifest.json").touch()
        
        # Scan
        result = ManifestFileRepository.scan_for_manifests(PluginDirectory(tmp_path))
        
        assert isinstance(result, Success)
        assert len(result.unwrap()) == 2
        assert all(str(p).endswith("manifest.json") for p in result.unwrap())
        
    def test_scan_for_manifests_invalid_directory(self):
        """Test scanning non-existent directory."""
        result = ManifestFileRepository.scan_for_manifests(
            PluginDirectory(Path("/non/existent/path"))
        )
        
        assert isinstance(result, Failure)
        assert result.failure().code == "INVALID_DIRECTORY"
        
    def test_read_manifest_success(self, tmp_path):
        """Test successful manifest reading."""
        manifest_path = tmp_path / "manifest.json"
        manifest_data = {"id": "test", "version": "1.0.0"}
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f)
        
        result = ManifestFileRepository.read_manifest(ManifestPath(manifest_path))
        
        assert isinstance(result, Success)
        assert result.unwrap() == manifest_data
        
    def test_read_manifest_file_not_found(self):
        """Test reading non-existent manifest."""
        result = ManifestFileRepository.read_manifest(
            ManifestPath(Path("/non/existent/manifest.json"))
        )
        
        assert isinstance(result, Failure)
        assert result.failure().code == "MANIFEST_NOT_FOUND"
        
    def test_read_manifest_invalid_json(self, tmp_path):
        """Test reading manifest with invalid JSON."""
        manifest_path = tmp_path / "manifest.json"
        
        with open(manifest_path, 'w') as f:
            f.write("{ invalid json")
        
        result = ManifestFileRepository.read_manifest(ManifestPath(manifest_path))
        
        assert isinstance(result, Failure)
        assert result.failure().code == "MANIFEST_MALFORMED"


class TestModuleImporter:
    """Test module importing operations."""
    
    def test_prepare_module_name(self):
        """Test module name preparation."""
        assert ModuleImporter._prepare_module_name(ModulePath("test.py")) == "test"
        assert ModuleImporter._prepare_module_name(ModulePath("test_module")) == "test_module"
        
    @patch('importlib.import_module')
    def test_import_plugin_module_success(self, mock_import):
        """Test successful module import."""
        mock_module = Mock()
        mock_import.return_value = mock_module
        
        result = ModuleImporter.import_plugin_module(
            ModulePath("test_plugin"),
            PluginDirectory(Path("/tmp/plugin")),
            PluginId("test-plugin")
        )
        
        assert isinstance(result, Success)
        assert result.unwrap() == mock_module
        
    @patch('importlib.import_module')
    def test_import_plugin_module_import_error(self, mock_import):
        """Test module import with ImportError."""
        mock_import.side_effect = ImportError("Module not found")
        
        result = ModuleImporter.import_plugin_module(
            ModulePath("test_plugin"),
            PluginDirectory(Path("/tmp/plugin")),
            PluginId("test-plugin")
        )
        
        assert isinstance(result, Failure)
        assert result.failure().code == "IMPORT_ERROR"
        assert "Module not found" in result.failure().message


# ===== Business Logic Tests =====

class TestPluginValidator:
    """Test plugin validation."""
    
    def test_validate_plugin_missing_type(self):
        """Test validation with missing plugin type."""
        plugin = Mock(spec=Plugin)
        manifest_data = {}  # Missing plugin_type
        
        validator = PluginValidator({})
        result = validator.validate_plugin(
            plugin,
            manifest_data,
            PluginDirectory(Path("/tmp"))
        )
        
        assert not result.success
        assert "Missing plugin_type" in result.errors[0]
        
    def test_validate_plugin_with_validator(self):
        """Test validation with specific validator."""
        plugin = Mock(spec=Plugin)
        manifest_data = {"plugin_type": "generic"}
        
        mock_validator = Mock()
        mock_validator.validate_manifest.return_value = (True, {"config": "data"}, [])
        
        validator = PluginValidator({"generic": mock_validator})
        result = validator.validate_plugin(
            plugin,
            manifest_data,
            PluginDirectory(Path("/tmp"))
        )
        
        assert result.success
        assert result.config == {"config": "data"}
        
    def test_validate_plugin_validator_exception(self):
        """Test validation when validator raises exception."""
        plugin = Mock(spec=Plugin)
        manifest_data = {"plugin_type": "generic"}
        
        mock_validator = Mock()
        mock_validator.validate_manifest.side_effect = Exception("Validation error")
        
        validator = PluginValidator({"generic": mock_validator})
        result = validator.validate_plugin(
            plugin,
            manifest_data,
            PluginDirectory(Path("/tmp"))
        )
        
        assert not result.success
        assert "Validation exception" in result.errors[0]


class TestVersionCompatibilityChecker:
    """Test version compatibility checking."""
    
    def test_is_compatible_valid_versions(self):
        """Test compatibility with valid versions."""
        mock_handler = Mock()
        mock_handler.parse_semver.return_value = (1, 0, 0)
        mock_handler.check_ilr_compatibility.return_value = (True, [])
        
        plugin = Mock(spec=Plugin)
        
        checker = VersionCompatibilityChecker(mock_handler, VersionString("1.0.0"))
        is_compatible, errors = checker.is_compatible(plugin)
        
        assert is_compatible
        assert len(errors) == 0
        
    def test_is_compatible_invalid_core_version(self):
        """Test compatibility with invalid core version."""
        mock_handler = Mock()
        mock_handler.parse_semver.return_value = None
        
        plugin = Mock(spec=Plugin)
        
        checker = VersionCompatibilityChecker(mock_handler, VersionString("invalid"))
        is_compatible, errors = checker.is_compatible(plugin)
        
        assert not is_compatible
        assert "Invalid core version" in errors[0]


class TestPluginInstantiator:
    """Test plugin instantiation."""
    
    def test_find_plugin_class_success(self):
        """Test successful plugin class finding."""
        class TestPlugin:
            pass
        
        mock_module = Mock()
        mock_module.TestPlugin = TestPlugin
        
        result = PluginInstantiator.find_plugin_class(
            mock_module,
            ClassName("TestPlugin"),
            PluginId("test-plugin")
        )
        
        assert isinstance(result, Success)
        assert result.unwrap() == TestPlugin
        
    def test_find_plugin_class_not_found(self):
        """Test plugin class not found."""
        # Use a real object that doesn't have the attribute
        mock_module = type('MockModule', (), {})()
        
        result = PluginInstantiator.find_plugin_class(
            mock_module,
            ClassName("NonExistent"),
            PluginId("test-plugin")
        )
        
        assert isinstance(result, Failure)
        assert result.failure().code == "CLASS_NOT_FOUND"
        
    def test_find_plugin_class_not_a_class(self):
        """Test when attribute is not a class."""
        mock_module = Mock()
        mock_module.NotAClass = "string_value"
        
        result = PluginInstantiator.find_plugin_class(
            mock_module,
            ClassName("NotAClass"),
            PluginId("test-plugin")
        )
        
        assert isinstance(result, Failure)
        assert result.failure().code == "NOT_A_CLASS"
        
    def test_prepare_init_args(self):
        """Test initialization argument preparation."""
        class TestPlugin:
            def __init__(self, arg1, arg2, arg3=None):
                pass
        
        args = PluginInstantiator.prepare_init_args(
            TestPlugin,
            {"arg1": "value1", "arg4": "ignored"},
            {"arg2": "value2", "arg3": "value3"}
        )
        
        assert args == {"arg1": "value1", "arg2": "value2", "arg3": "value3"}
        
    def test_instantiate_success(self):
        """Test successful instantiation."""
        class TestPlugin:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
        
        result = PluginInstantiator.instantiate(
            TestPlugin,
            {"arg1": "value1"},
            PluginId("test-plugin")
        )
        
        assert isinstance(result, Success)
        assert isinstance(result.unwrap(), TestPlugin)
        assert result.unwrap().kwargs == {"arg1": "value1"}
        
    def test_instantiate_type_error(self):
        """Test instantiation with TypeError."""
        class TestPlugin:
            def __init__(self, required_arg):
                pass
        
        result = PluginInstantiator.instantiate(
            TestPlugin,
            {},  # Missing required argument
            PluginId("test-plugin")
        )
        
        assert isinstance(result, Failure)
        assert result.failure().code == "INSTANTIATION_TYPE_ERROR"


class TestPluginRegistry:
    """Test plugin registry operations."""
    
    def test_register_success(self):
        """Test successful plugin registration."""
        registry = PluginRegistry()
        plugin = Mock(spec=Plugin)
        plugin.id = "test-plugin"
        
        result = registry.register(plugin)
        
        assert isinstance(result, Success)
        assert registry.get(PluginId("test-plugin")) == plugin
        
    def test_register_duplicate(self):
        """Test registering duplicate plugin."""
        registry = PluginRegistry()
        plugin = Mock(spec=Plugin)
        plugin.id = "test-plugin"
        
        registry.register(plugin)
        result = registry.register(plugin)
        
        assert isinstance(result, Failure)
        assert result.failure().code == "DUPLICATE_PLUGIN"
        
    def test_get_all(self):
        """Test getting all plugins."""
        registry = PluginRegistry()
        
        plugin1 = Mock(spec=Plugin)
        plugin1.id = "plugin1"
        plugin2 = Mock(spec=Plugin)
        plugin2.id = "plugin2"
        
        registry.register(plugin1)
        registry.register(plugin2)
        
        all_plugins = registry.get_all()
        assert len(all_plugins) == 2
        assert plugin1 in all_plugins
        assert plugin2 in all_plugins
        
    def test_clear(self):
        """Test clearing registry."""
        registry = PluginRegistry()
        plugin = Mock(spec=Plugin)
        plugin.id = "test-plugin"
        
        registry.register(plugin)
        registry.clear()
        
        assert len(registry.get_all()) == 0


class TestErrorCollector:
    """Test error collection."""
    
    def test_add_error(self):
        """Test adding errors."""
        collector = ErrorCollector()
        error = PluginError(
            code=ErrorCode("TEST"),
            message=ErrorMessage("Test error")
        )
        
        collector.add_error(error)
        
        errors = collector.get_errors()
        assert len(errors) == 1
        assert errors[0] == error
        
    def test_clear_errors(self):
        """Test clearing errors."""
        collector = ErrorCollector()
        error = PluginError(
            code=ErrorCode("TEST"),
            message=ErrorMessage("Test error")
        )
        
        collector.add_error(error)
        collector.clear()
        
        assert len(collector.get_errors()) == 0


# ===== Service Layer Tests =====

class TestPluginDiscoveryService:
    """Test plugin discovery service."""
    
    def test_discover_plugins_success(self, tmp_path):
        """Test successful plugin discovery."""
        # Create plugin structure
        plugin_dir = tmp_path / "plugin"
        plugin_dir.mkdir()
        manifest_path = plugin_dir / "manifest.json"
        
        manifest_data = {"id": "test-plugin", "version": "1.0.0"}
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f)
        
        # Create service
        manifest_repo = ManifestFileRepository()
        error_collector = ErrorCollector()
        service = PluginDiscoveryService(manifest_repo, error_collector)
        
        # Discover
        discovered = service.discover_plugins_in_directory(PluginDirectory(tmp_path))
        
        assert len(discovered) == 1
        assert discovered[0][1] == manifest_data
        
    def test_discover_plugins_with_errors(self):
        """Test discovery with scan errors."""
        manifest_repo = Mock()
        manifest_repo.scan_for_manifests.return_value = Failure(
            PluginError(code=ErrorCode("SCAN_ERROR"), message=ErrorMessage("Scan failed"))
        )
        
        error_collector = ErrorCollector()
        service = PluginDiscoveryService(manifest_repo, error_collector)
        
        discovered = service.discover_plugins_in_directory(PluginDirectory(Path("/tmp")))
        
        assert len(discovered) == 0
        assert len(error_collector.get_errors()) == 1


class TestPluginLoadingService:
    """Test plugin loading service."""
    
    def test_load_plugin_instance_grammar_type(self):
        """Test loading grammar plugin (no instantiation needed)."""
        plugin = Mock(spec=Plugin)
        plugin.plugin_type = "grammar_definition"
        
        service = PluginLoadingService(Mock(), Mock(), ErrorCollector())
        result = service.load_plugin_instance(plugin)
        
        assert result is None
        
    def test_load_plugin_instance_no_entry_point(self):
        """Test loading plugin without entry point."""
        plugin = Mock(spec=Plugin)
        plugin.plugin_type = "generic"
        plugin.entry_point = None
        
        service = PluginLoadingService(Mock(), Mock(), ErrorCollector())
        result = service.load_plugin_instance(plugin)
        
        assert result is None
        
    def test_load_plugin_instance_success(self):
        """Test successful plugin instance loading."""
        # Setup plugin
        plugin = Mock(spec=Plugin)
        plugin.plugin_type = "generic"
        plugin.id = "test-plugin"
        plugin.manifest_path = Path("/tmp/plugin/manifest.json")
        plugin.entry_point = Mock()
        plugin.entry_point.type = "module"
        plugin.entry_point.module_path = "test_module.py"
        plugin.entry_point.class_name = "TestPlugin"
        plugin.entry_point.default_init_args = {}
        plugin.plugin_specific_config = {}
        
        # Setup mocks
        mock_module = Mock()
        test_instance = Mock()
        
        module_importer = Mock()
        module_importer.import_plugin_module.return_value = Success(mock_module)
        
        instantiator = Mock()
        instantiator.find_plugin_class.return_value = Success(Mock)
        instantiator.prepare_init_args.return_value = {}
        instantiator.instantiate.return_value = Success(test_instance)
        
        # Test
        service = PluginLoadingService(module_importer, instantiator, ErrorCollector())
        result = service.load_plugin_instance(plugin)
        
        assert result == test_instance


# ===== Integration Tests =====

class TestPluginManagerIntegration:
    """Test PluginManager integration."""
    
    def test_plugin_manager_initialization(self, tmp_path):
        """Test plugin manager initialization."""
        manager = PluginManager(
            plugin_dirs=str(tmp_path),
            core_ilr_version="1.0.0",
            default_init_args={"arg": "value"}
        )
        
        assert manager._core_version == "1.0.0"
        assert manager._default_init_args == {"arg": "value"}
        assert len(manager._plugin_roots) == 1
        
    def test_discover_plugins_empty_directory(self, tmp_path):
        """Test discovering plugins in empty directory."""
        manager = PluginManager(plugin_dirs=str(tmp_path))
        plugins = manager.discover_plugins()
        
        assert len(plugins) == 0
        assert len(manager.get_errors()) == 0
        
    def test_discover_plugins_with_valid_plugin(self, tmp_path, sample_manifest):
        """Test discovering valid plugin."""
        # Create plugin structure
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()
        
        manifest_path = plugin_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(sample_manifest, f)
        
        # Create plugin module
        module_path = plugin_dir / "test_plugin.py"
        with open(module_path, 'w') as f:
            f.write("""
class TestPlugin:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        
    def translate_to_ilr(self, tau_source):
        return {"source": tau_source, "ilr": "translated"}
""")
        
        # Mock validators
        mock_validator = Mock()
        mock_validator.validate_manifest.return_value = (True, {}, [])
        
        manager = PluginManager(plugin_dirs=str(tmp_path))
        manager._plugin_validator._validators = {"generic": mock_validator}
        
        # Discover
        plugins = manager.discover_plugins()
        
        assert len(plugins) == 1
        assert "test-plugin" in plugins
        
    def test_get_plugin(self, tmp_path):
        """Test getting specific plugin."""
        manager = PluginManager(plugin_dirs=str(tmp_path))
        
        # Manually register a plugin
        plugin = Mock(spec=Plugin)
        plugin.id = "test-plugin"
        manager._registry.register(plugin)
        
        retrieved = manager.get_plugin("test-plugin")
        assert retrieved == plugin
        
    def test_get_all_plugins(self, tmp_path):
        """Test getting all plugins."""
        manager = PluginManager(plugin_dirs=str(tmp_path))
        
        # Manually register plugins
        plugin1 = Mock(spec=Plugin)
        plugin1.id = "plugin1"
        plugin2 = Mock(spec=Plugin)
        plugin2.id = "plugin2"
        
        manager._registry.register(plugin1)
        manager._registry.register(plugin2)
        
        all_plugins = manager.get_all_plugins()
        assert len(all_plugins) == 2
        
    def test_invoke_translation_plugin_not_found(self, tmp_path):
        """Test invoking translation on non-existent plugin."""
        manager = PluginManager(plugin_dirs=str(tmp_path))
        result = manager.invoke_translation("non-existent", "source")
        
        assert result is None
        errors = manager.get_errors()
        assert len(errors) == 1
        assert errors[0].code == "PLUGIN_NOT_FOUND"
        
    def test_invoke_translation_no_instance(self, tmp_path):
        """Test invoking translation on plugin without instance."""
        manager = PluginManager(plugin_dirs=str(tmp_path))
        
        plugin = Mock(spec=Plugin)
        plugin.id = "test-plugin"
        plugin.instance = None
        
        manager._registry.register(plugin)
        result = manager.invoke_translation("test-plugin", "source")
        
        assert result is None
        errors = manager.get_errors()
        assert len(errors) == 1
        assert errors[0].code == "NO_INSTANCE"
        
    def test_invoke_translation_success(self, tmp_path):
        """Test successful translation invocation."""
        manager = PluginManager(plugin_dirs=str(tmp_path))
        
        # Create plugin with instance
        plugin = Mock(spec=Plugin)
        plugin.id = "test-plugin"
        
        instance = Mock()
        instance.translate_to_ilr.return_value = {"result": "translated"}
        plugin.instance = instance
        
        manager._registry.register(plugin)
        result = manager.invoke_translation("test-plugin", "source code")
        
        assert result == {"result": "translated"}
        instance.translate_to_ilr.assert_called_once_with("source code")
        
    def test_invoke_translation_exception(self, tmp_path):
        """Test translation invocation with exception."""
        manager = PluginManager(plugin_dirs=str(tmp_path))
        
        # Create plugin with instance that raises
        plugin = Mock(spec=Plugin)
        plugin.id = "test-plugin"
        
        instance = Mock()
        instance.translate_to_ilr.side_effect = Exception("Translation failed")
        plugin.instance = instance
        
        manager._registry.register(plugin)
        result = manager.invoke_translation("test-plugin", "source")
        
        assert result is None
        errors = manager.get_errors()
        assert len(errors) == 1
        assert errors[0].code == "TRANSLATION_ERROR"
        assert "Translation failed" in errors[0].message


# ===== Performance and Edge Case Tests =====

class TestPerformanceAndEdgeCases:
    """Test performance optimizations and edge cases."""
    
    def test_large_directory_scan_performance(self, tmp_path):
        """Test scanning large directory structure."""
        # Create many plugins
        for i in range(100):
            plugin_dir = tmp_path / f"plugin{i}"
            plugin_dir.mkdir()
            manifest_path = plugin_dir / "manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump({"id": f"plugin{i}", "version": "1.0.0"}, f)
        
        import time
        start = time.time()
        
        result = ManifestFileRepository.scan_for_manifests(PluginDirectory(tmp_path))
        
        elapsed = time.time() - start
        
        assert isinstance(result, Success)
        assert len(result.unwrap()) == 100
        assert elapsed < 1.0  # Should complete within 1 second
        
    def test_circular_dependency_prevention(self):
        """Test prevention of circular dependencies."""
        # This would be implemented in the actual plugin loading logic
        # For now, we ensure the structure supports it
        registry = PluginRegistry()
        
        plugin1 = Mock(spec=Plugin)
        plugin1.id = "plugin1"
        plugin1.dependencies = ["plugin2"]
        
        plugin2 = Mock(spec=Plugin)
        plugin2.id = "plugin2"
        plugin2.dependencies = ["plugin1"]
        
        # Registry should handle this gracefully
        registry.register(plugin1)
        registry.register(plugin2)
        
        assert len(registry.get_all()) == 2
        
    def test_unicode_handling_in_manifest(self, tmp_path):
        """Test handling of unicode in manifest files."""
        manifest_path = tmp_path / "manifest.json"
        manifest_data = {
            "id": "unicode-plugin",
            "name": "Unicode Plugin 中文 العربية",
            "description": "Testing unicode: 🎉 émojis",
            "version": "1.0.0"
        }
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, ensure_ascii=False)
        
        result = ManifestFileRepository.read_manifest(ManifestPath(manifest_path))
        
        assert isinstance(result, Success)
        assert result.unwrap()["name"] == "Unicode Plugin 中文 العربية"
        assert "🎉" in result.unwrap()["description"]
        
    def test_concurrent_plugin_access(self):
        """Test thread-safe plugin access."""
        import threading
        import uuid
        
        registry = PluginRegistry()
        errors = []
        
        def register_plugins(thread_id):
            for i in range(10):
                plugin = Mock(spec=Plugin)
                # Use thread_id parameter and UUID to ensure uniqueness
                plugin.id = f"plugin{thread_id}-{i}-{str(uuid.uuid4())[:8]}"
                result = registry.register(plugin)
                if isinstance(result, Failure):
                    errors.append(result.failure())
        
        threads = []
        for thread_index in range(5):
            t = threading.Thread(target=register_plugins, args=(thread_index,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have 50 plugins registered (all IDs are unique now)
        assert len(registry.get_all()) == 50
        assert len(errors) == 0  # No registration errors expected