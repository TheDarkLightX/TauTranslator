import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import importlib
from tau_translator_omega.core_engine.plugin_manager import PluginManager
from tau_translator_omega.core_engine.plugin import Plugin, PluginEntryPoint


class TestPluginManagerLoading:
    """Test plugin loading and instantiation"""

    def test_load_grammar_definition_plugin_skip(self, tmp_path):
        """Test that grammar definition plugins skip instantiation"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="grammar-plugin",
            name="Grammar Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={},
            plugin_type="grammar_definition"
        )
        
        result = manager._load_and_instantiate_plugin(plugin)
        
        assert result is None
        assert plugin.instance is None

    def test_load_non_module_type_skip(self, tmp_path):
        """Test that non-module type plugins skip instantiation"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="cli-plugin",
            name="CLI Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="cli", command="test-command"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        result = manager._load_and_instantiate_plugin(plugin)
        
        assert result is None
        assert plugin.instance is None
        assert not manager.errors  # No errors should be logged for a clean skip

    def test_load_missing_module_path(self, tmp_path):
        """Test loading plugin with missing module path"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module", class_name="TestClass"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        result = manager._load_and_instantiate_plugin(plugin)
        
        assert plugin.instance is None
        assert any("MODULE_PATH_OR_CLASS_NAME_MISSING" in str(error) for error in manager.errors)

    def test_load_missing_class_name(self, tmp_path):
        """Test loading plugin with missing class name"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module", module_path="test.py"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        result = manager._load_and_instantiate_plugin(plugin)
        
        assert plugin.instance is None
        assert any("MODULE_PATH_OR_CLASS_NAME_MISSING" in str(error) for error in manager.errors)

    def test_load_successful_instantiation(self, tmp_path):
        """Test successful plugin instantiation"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        # Create a test module
        test_module_content = '''
class TestPlugin:
    def __init__(self):
        self.initialized = True
'''
        module_path = tmp_path / "test_plugin.py"
        with open(module_path, 'w') as f:
            f.write(test_module_content)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(
                type="module",
                module_path="test_plugin.py",
                class_name="TestPlugin"
            ),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        result = manager._load_and_instantiate_plugin(plugin)
        
        assert result is not None
        assert hasattr(result, 'initialized')
        assert result.initialized is True

    def test_load_with_init_args(self, tmp_path):
        """Test plugin instantiation with init arguments"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        # Create a test module
        test_module_content = '''
class TestPlugin:
    def __init__(self, arg1, arg2="default"):
        self.arg1 = arg1
        self.arg2 = arg2
        self.initialized_with_arg = True
'''
        module_path = tmp_path / "test_plugin_with_args.py"
        with open(module_path, 'w') as f:
            f.write(test_module_content)
        
        plugin = Plugin(
            id="test-plugin-init-args",
            name="Test Plugin Init Args",
            version="1.0.0",
            description="Test with init args",
            entry_point=PluginEntryPoint(
                type="module",
                module_path="test_plugin_with_args.py",
                class_name="TestPlugin"
            ),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        # Directly set default_init_args on the plugin's entry_point for this test
        if plugin.entry_point: 
            plugin.entry_point.default_init_args = {"arg1": "custom_value"}

        instance = manager._load_and_instantiate_plugin(plugin)

        assert instance is not None
        assert instance.initialized_with_arg
        assert instance.arg1 == "custom_value"
        assert instance.arg2 == "default" # Test default value from signature

    def test_load_missing_required_init_args(self, tmp_path):
        """Test plugin instantiation with missing required arguments"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        # Create a test module
        test_module_content = '''
class TestPlugin:
    def __init__(self, required_arg, optional_arg=None):
        self.required_arg = required_arg
'''
        module_path = tmp_path / "test_plugin.py"
        with open(module_path, 'w') as f:
            f.write(test_module_content)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(
                type="module",
                module_path="test_plugin.py",
                class_name="TestPlugin",
                default_init_args={}  # Ensure this is explicitly set for the test
            ),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        manager._load_and_instantiate_plugin(plugin)
        
        assert plugin.instance is None
        assert any("PLUGIN_INSTANTIATION_TYPE_ERROR" in str(error) for error in manager.errors)
        assert any("required_arg" in str(error) for error in manager.errors)

    def test_load_module_not_found(self, tmp_path):
        """Test loading when module is not found"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(
                type="module",
                module_path="nonexistent.py",
                class_name="TestPlugin"
            ),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        manager._load_and_instantiate_plugin(plugin)
        
        assert plugin.instance is None
        assert any("PLUGIN_IMPORT_ERROR" in str(error) for error in manager.errors)

    def test_load_class_not_found(self, tmp_path):
        """Test loading when class is not found in module"""
        manager = PluginManager(plugin_dirs=tmp_path)

        # Define an empty module or one with unrelated content
        test_module_content = """# This module is intentionally sparse
class AnotherClassAltogether:
    pass
"""
        module_path = tmp_path / "test_plugin_for_class_not_found.py" # Use a unique module name to avoid cache hits
        with open(module_path, 'w') as f:
            f.write(test_module_content)

        plugin = Plugin(
            id="test-plugin-cnF",
            name="Test CNF Plugin",
            version="1.0.0",
            description="Test Class Not Found",
            entry_point=PluginEntryPoint(
                type="module",
                module_path="test_plugin_for_class_not_found.py", # Match new module name
                class_name="TrulyNonExistentPlugin"
            ),
            manifest_path=tmp_path / "manifest.json", # This manifest isn't strictly used by _load_and_instantiate_plugin directly
            plugin_dir=tmp_path,
            manifest_data={}, # No default_init_args needed as class won't be found
            default_init_args=None # Explicitly None
        )

        # Ensure the unique module name isn't lingering from a previous failed run (though pytest tmp_path helps)
        if plugin.entry_point.module_path.removesuffix('.py') in sys.modules:
            del sys.modules[plugin.entry_point.module_path.removesuffix('.py')]

        manager._load_and_instantiate_plugin(plugin)

        assert plugin.instance is None
        assert any("PLUGIN_CLASS_NOT_FOUND" in str(error) for error in manager.errors), \
            f"Expected 'PLUGIN_CLASS_NOT_FOUND' but errors were: {manager.errors}"

    def test_load_instantiation_error(self, tmp_path):
        """Test handling of errors during instantiation"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        # Create a test module that raises an error during instantiation
        test_module_content = '''
class TestPlugin:
    def __init__(self):
        raise ValueError("Instantiation error")
'''
        module_path = tmp_path / "test_plugin.py"
        with open(module_path, 'w') as f:
            f.write(test_module_content)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(
                type="module",
                module_path="test_plugin.py",
                class_name="TestPlugin"
            ),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        manager._load_and_instantiate_plugin(plugin)
        
        assert plugin.instance is None
        assert any("PLUGIN_INSTANTIATION_ERROR" in str(error) for error in manager.errors)
        assert any("Instantiation error" in str(error) for error in manager.errors)

    def test_load_sys_path_management(self, tmp_path):
        """Test that sys.path is properly managed during loading"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        # Create a test module
        test_module_content = '''
class TestPlugin:
    pass
'''
        module_path = tmp_path / "test_plugin.py"
        with open(module_path, 'w') as f:
            f.write(test_module_content)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(
                type="module",
                module_path="test_plugin.py",
                class_name="TestPlugin"
            ),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        original_sys_path = list(sys.path)
        
        result = manager._load_and_instantiate_plugin(plugin)
        
        # sys.path should be restored
        assert sys.path == original_sys_path
        assert result is not None

    def test_load_module_with_py_extension(self, tmp_path):
        """Test loading module with .py extension in path"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        # Create a test module
        test_module_content = '''
class TestPlugin:
    def __init__(self): # Added explicit __init__
        pass
'''
        module_path = tmp_path / "my_plugin.py"
        with open(module_path, 'w') as f:
            f.write(test_module_content)
        
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(
                type="module",
                module_path="my_plugin.py",  # With .py extension
                class_name="TestPlugin"
            ),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={}
        )
        
        instance = manager._load_and_instantiate_plugin(plugin)
        
        assert instance is not None

    def test_load_grammar_definition_plugin_no_instantiation(self, tmp_path):
        """Test that grammar definition plugins skip instantiation"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        plugin = Plugin(
            id="grammar-plugin",
            name="Grammar Plugin",
            version="1.0.0",
            description="Test",
            entry_point=PluginEntryPoint(type="module"),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={},
            plugin_type="grammar_definition"
        )
        
        result = manager._load_and_instantiate_plugin(plugin)
        
        assert result is None
        assert plugin.instance is None

    def test_load_attribute_error(self, tmp_path):
        """Test handling of AttributeError during loading"""
        manager = PluginManager(plugin_dirs=tmp_path)

        # Define a dummy module content. It won't actually be used due to mocking import_module,
        # but helps if sys.path logic in loader needs a file to exist.
        dummy_module_path = tmp_path / "test_plugin_for_attr_err.py"
        with open(dummy_module_path, 'w') as f:
            f.write("# Dummy module for attribute error test")

        plugin = Plugin(
            id="test-plugin-attrErr",
            name="Test AttrErr Plugin",
            version="1.0.0",
            description="Test Attribute Error",
            entry_point=PluginEntryPoint(
                type="module",
                module_path="test_plugin_for_attr_err.py", # Use a unique module name
                class_name="TestPlugin"
            ),
            manifest_path=tmp_path / "manifest.json",
            plugin_dir=tmp_path,
            manifest_data={},
            default_init_args=None # No init args needed as getattr will fail first
        )

        module_name_to_clear = plugin.entry_point.module_path.removesuffix('.py')
        if module_name_to_clear in sys.modules:
            del sys.modules[module_name_to_clear]

        with patch('importlib.import_module') as mock_import_module, \
             patch('importlib.reload') as mock_reload_module: # Also mock reload
            
            mock_module_instance = MagicMock(__name__=module_name_to_clear)
            class_name_str = plugin.entry_point.class_name

            if not isinstance(class_name_str, str) or not class_name_str.isidentifier():
                class_name_str = "TestPlugin" 

            setattr(mock_module_instance, class_name_str, PropertyMock(side_effect=AttributeError("Test attribute error")))
            
            mock_import_module.return_value = mock_module_instance
            # If reload were to be called, make it return the same mock_module_instance
            # This handles the case where the module_name_to_clear might have been re-added by another part of the code
            # before _load_and_instantiate_plugin checks sys.modules again.
            mock_reload_module.return_value = mock_module_instance 

            manager._load_and_instantiate_plugin(plugin)
            
            assert plugin.instance is None 
            expected_error_code = "PLUGIN_ENTRY_NOT_CLASS"
            expected_error_fragment = f"Entry point '{class_name_str}' in module '{module_name_to_clear}' for plugin '{plugin.id}' is not a class."
            
            found_error = False
            for error in manager.errors:
                if error.code == expected_error_code and expected_error_fragment in error.message:
                    found_error = True
                    break
            assert found_error, \
                f"Expected error code '{expected_error_code}' with fragment '{expected_error_fragment}' but errors were: {manager.errors}"

    def test_load_type_error_in_init(self, tmp_path):
        """Test handling of TypeError during plugin __init__ (e.g. wrong arg types)."""
