import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import json
from tau_translator_omega.core_engine.plugin_manager import PluginManager
from tau_translator_omega.core_engine.version_handler import VersionHandler
import builtins
import logging


class TestPluginManagerInit:
    """Test PluginManager initialization"""

    def test_init_with_single_string_path(self, tmp_path):
        """Test initialization with a single string path"""
        plugin_dir = str(tmp_path)
        manager = PluginManager(plugin_dirs=plugin_dir)
        
        assert len(manager.plugin_roots) == 1
        assert manager.plugin_roots[0] == Path(plugin_dir)
        assert manager.core_ilr_version_str == "1.0.0"
        assert manager.default_init_args == {}
        assert manager.plugins == {}

    def test_init_with_single_path_object(self, tmp_path):
        """Test initialization with a single Path object"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        assert len(manager.plugin_roots) == 1
        assert manager.plugin_roots[0] == tmp_path
        assert isinstance(manager.version_handler, VersionHandler)

    def test_init_with_list_of_strings(self, tmp_path):
        """Test initialization with a list of string paths"""
        dir1 = tmp_path / "plugins1"
        dir2 = tmp_path / "plugins2"
        dir1.mkdir()
        dir2.mkdir()
        
        manager = PluginManager(plugin_dirs=[str(dir1), str(dir2)])
        
        assert len(manager.plugin_roots) == 2
        assert manager.plugin_roots[0] == dir1
        assert manager.plugin_roots[1] == dir2

    def test_init_with_list_of_paths(self, tmp_path):
        """Test initialization with a list of Path objects"""
        dir1 = tmp_path / "plugins1"
        dir2 = tmp_path / "plugins2"
        dir1.mkdir()
        dir2.mkdir()
        
        manager = PluginManager(plugin_dirs=[dir1, dir2])
        
        assert len(manager.plugin_roots) == 2
        assert manager.plugin_roots[0] == dir1
        assert manager.plugin_roots[1] == dir2

    def test_init_with_custom_ilr_version(self, tmp_path):
        """Test initialization with custom core ILR version"""
        manager = PluginManager(
            plugin_dirs=tmp_path,
            core_ilr_version="2.1.0"
        )
        
        assert manager.core_ilr_version_str == "2.1.0"
        assert manager.core_ilr_semver is not None

    def test_init_with_invalid_ilr_version(self, tmp_path):
        """Test initialization with invalid core ILR version"""
        manager = PluginManager(
            plugin_dirs=tmp_path,
            core_ilr_version="invalid.version"
        )
        
        assert manager.core_ilr_semver is None
        assert len(manager.errors) > 0
        assert any("CORE_ILR_INVALID_INIT" in str(error) for error in manager.errors)

    def test_init_with_default_init_args(self, tmp_path):
        """Test initialization with default init args"""
        init_args = {"param1": "value1", "param2": 42}
        manager = PluginManager(
            plugin_dirs=tmp_path,
            default_init_args=init_args
        )
        
        assert manager.default_init_args == init_args
        # Check that no schema-related errors were added
        assert manager.manifest_schema is not None
        assert not any("SCHEMA_" in str(error) for error in manager.errors)

    def test_init_with_invalid_plugin_dirs_type(self):
        """Test initialization with invalid plugin_dirs type"""
        with pytest.raises(TypeError) as exc_info:
            PluginManager(plugin_dirs=123)
        
        assert "plugin_dirs must be a string, Path, or list" in str(exc_info.value)

    def test_init_loads_schema_successfully(self, tmp_path, monkeypatch):
        """Test successful schema loading during initialization"""
        schema_content = {"type": "object", "properties": {"id": {"type": "string"}}}
        
        # Mock the schema file location
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path.open = mock_open(read_data=json.dumps(schema_content))
        
        with patch('pathlib.Path.resolve') as mock_resolve:
            mock_resolve.return_value.parent.parent.parent.parent = tmp_path
            with patch('builtins.open', mock_open(read_data=json.dumps(schema_content))):
                with patch('pathlib.Path.exists', return_value=True):
                    manager = PluginManager(plugin_dirs=tmp_path)
        
        assert manager.manifest_schema == schema_content
        assert not any("SCHEMA_" in str(error) for error in manager.errors)

    def test_init_schema_file_not_found(self, tmp_path, monkeypatch):
        """Test schema loading when file doesn't exist"""
        with patch('pathlib.Path.exists', return_value=False):
            manager = PluginManager(plugin_dirs=tmp_path)
        
        assert manager.manifest_schema is None
        # Check that a schema load error was added
        assert any("SCHEMA_LOAD_ERROR" in str(error) for error in manager.errors)


class TestPluginManagerSchemaLoadingErrors:
    # Define these paths once for the class if they are constant or derive them carefully
    # For simplicity in this example, we'll use a string check for the filename.
    # A more robust solution might involve mocking Path(__file__) in PluginManager
    # or getting the expected path from a fixture.
    MAIN_SCHEMA_FILENAME = "plugin_manifest_schema.json"

    def test_init_schema_json_decode_error(self, tmp_path):
        """Test schema loading with malformed JSON"""
        original_open = builtins.open

        def mock_open_for_json_error(file, *args, **kwargs):
            if self.MAIN_SCHEMA_FILENAME in str(file):
                # Return a mock file object that provides invalid JSON data
                return mock_open(read_data="invalid json")(file, *args, **kwargs)
            return original_open(file, *args, **kwargs)

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', side_effect=mock_open_for_json_error):
                manager = PluginManager(plugin_dirs=tmp_path)
        
        assert manager.manifest_schema is None
        # Check that a schema decode error was added
        # The error code is SCHEMA_LOAD_UNEXPECTED_ERROR, message contains details of JSONDecodeError
        assert any(
            error.code == "SCHEMA_LOAD_UNEXPECTED_ERROR" and 
            "Expecting value" in error.message and 
            self.MAIN_SCHEMA_FILENAME in error.message
            for error in manager.errors
        )

    def test_init_schema_unexpected_error(self, tmp_path):
        """Test schema loading with unexpected error"""
        original_open = builtins.open

        def mock_open_for_unexpected_exception(file, *args, **kwargs):
            if self.MAIN_SCHEMA_FILENAME in str(file):
                raise Exception("Custom Unexpected error for test")
            return original_open(file, *args, **kwargs)

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', side_effect=mock_open_for_unexpected_exception):
                manager = PluginManager(plugin_dirs=tmp_path)
        
        assert manager.manifest_schema is None
        # Check that an unexpected schema error was added
        assert any(
            error.code == "SCHEMA_LOAD_UNEXPECTED_ERROR" and 
            "Custom Unexpected error for test" in error.message and
            self.MAIN_SCHEMA_FILENAME in error.message
            for error in manager.errors
        )


class TestPluginManagerErrorHandling:
    """Test error handling methods"""

    def test_add_error_without_plugin(self, tmp_path):
        """Test adding error without plugin context"""
        manager = PluginManager(plugin_dirs=tmp_path)
        manager._add_error("TEST_ERROR", "Test error message")
        
        assert len(manager.errors) == 1
        error_str = str(manager.errors[0])
        assert "TEST_ERROR" in error_str
        assert "Test error message" in error_str

    def test_add_error_with_plugin(self, tmp_path):
        """Test adding error with plugin context"""
        from tau_translator_omega.core_engine.plugin import Plugin, PluginEntryPoint
        
        manager = PluginManager(plugin_dirs=tmp_path)
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        manager._add_error("TEST_ERROR", "Test error message", plugin)
        
        assert len(manager.errors) == 1
        error_str = str(manager.errors[0])
        assert "TEST_ERROR" in error_str
        assert "test-plugin" in error_str
        assert "Test error message" in error_str

    def test_add_error_critical_level(self, tmp_path, caplog):
        """Test critical error logging"""
        import logging
        caplog.set_level(logging.ERROR)
        
        manager = PluginManager(plugin_dirs=tmp_path)
        manager._add_error("CRITICAL_ERROR", "Critical error")
        
        assert "ERROR" in caplog.text
        assert "CRITICAL_ERROR" in caplog.text

    def test_add_error_deprecated_level(self, tmp_path, caplog):
        """Test deprecated warning logging"""
        import logging
        caplog.set_level(logging.ERROR)
        
        manager = PluginManager(plugin_dirs=tmp_path)
        manager._add_error("DEPRECATED_FEATURE", "Deprecated feature")
        
        assert "ERROR" in caplog.text
        assert "DEPRECATED_FEATURE" in caplog.text


class TestPluginManagerGetters:
    """Test getter methods"""

    def test_get_plugin_existing(self, tmp_path):
        """Test getting an existing plugin"""
        from tau_translator_omega.core_engine.plugin import Plugin, PluginEntryPoint
        
        manager = PluginManager(plugin_dirs=tmp_path)
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        manager.plugins["test-plugin"] = plugin
        
        result = manager.get_plugin("test-plugin")
        assert result == plugin

    def test_get_plugin_non_existing(self, tmp_path):
        """Test getting a non-existing plugin"""
        manager = PluginManager(plugin_dirs=tmp_path)
        result = manager.get_plugin("non-existing")
        assert result is None

    def test_get_all_plugins_empty(self, tmp_path):
        """Test getting all plugins when empty"""
        manager = PluginManager(plugin_dirs=tmp_path)
        result = manager.get_all_plugins()
        assert result == []

    def test_get_all_plugins_multiple(self, tmp_path):
        """Test getting all plugins with multiple plugins"""
        from tau_translator_omega.core_engine.plugin import Plugin, PluginEntryPoint
        
        manager = PluginManager(plugin_dirs=tmp_path)
        plugin1 = Plugin(
            id="plugin1",
            name="Plugin 1",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest1.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        plugin2 = Plugin(
            id="plugin2",
            name="Plugin 2",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest2.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        manager.plugins["plugin1"] = plugin1
        manager.plugins["plugin2"] = plugin2
        
        result = manager.get_all_plugins()
        assert len(result) == 2
        assert plugin1 in result
        assert plugin2 in result

    def test_get_errors_empty(self, tmp_path):
        """Test getting errors when empty"""
        manager = PluginManager(plugin_dirs=tmp_path)
        result = manager.get_errors()
        assert result == []

    def test_get_errors_multiple(self, tmp_path):
        """Test getting errors with multiple errors"""
        manager = PluginManager(plugin_dirs=tmp_path)
        manager._add_error("ERROR1", "First error")
        manager._add_error("ERROR2", "Second error")
        
        result = manager.get_errors()
        assert len(result) == 2
        assert any("ERROR1" in str(error) for error in result)
        assert any("ERROR2" in str(error) for error in result)
