"""Common utilities for plugin manager tests"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List


def create_valid_manifest(
    plugin_id: str = "test-plugin",
    plugin_name: str = "Test Plugin",
    version: str = "1.0.0",
    plugin_type: str = "generic",
    entry_point: Optional[Dict[str, Any]] = None,
    ilr_versions_supported: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create a valid manifest dictionary with sensible defaults"""
    if entry_point is None:
        entry_point = {
            "type": "cli",
            "command": "test-command"
        }
    
    if ilr_versions_supported is None:
        ilr_versions_supported = ["1.0.0"]
    
    manifest = {
        "manifest_version": "1.0",
        "id": plugin_id,
        "name": plugin_name,
        "version": version,
        "description": f"Description for {plugin_name}",
        "author": "Test Author",
        "license": "MIT",
        "tags": ["test"],
        "plugin_type": plugin_type,
        "ilr_versions_supported": ilr_versions_supported,
        "entry_point": entry_point
    }
    
    # Add any additional fields
    manifest.update(kwargs)
    
    return manifest


def create_plugin_directory(
    base_path: Path,
    plugin_id: str,
    manifest_data: Optional[Dict[str, Any]] = None,
    additional_files: Optional[Dict[str, str]] = None
) -> Path:
    """Create a plugin directory with manifest and optional additional files"""
    plugin_dir = base_path / plugin_id
    plugin_dir.mkdir(parents=True, exist_ok=True)
    
    # Create manifest
    if manifest_data is None:
        manifest_data = create_valid_manifest(plugin_id=plugin_id)
    
    manifest_path = plugin_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest_data, f, indent=2)
    
    # Create additional files
    if additional_files:
        for filename, content in additional_files.items():
            file_path = plugin_dir / filename
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
    
    return plugin_dir


def create_module_plugin(
    base_path: Path,
    plugin_id: str,
    module_name: str = "plugin",
    class_name: str = "TestPlugin",
    class_content: Optional[str] = None,
    init_args: Optional[Dict[str, Any]] = None
) -> Path:
    """Create a module-type plugin with Python code"""
    if class_content is None:
        class_content = f'''
class {class_name}:
    def __init__(self):
        self.initialized = True
    
    def translate_to_ilr(self, source):
        return {{"translated": source}}
'''
    
    entry_point = {
        "type": "module",
        "module_path": f"{module_name}.py",
        "class_name": class_name
    }
    
    if init_args:
        entry_point["default_init_args"] = init_args
    
    manifest_data = create_valid_manifest(
        plugin_id=plugin_id,
        entry_point=entry_point
    )
    
    additional_files = {
        f"{module_name}.py": class_content
    }
    
    return create_plugin_directory(
        base_path,
        plugin_id,
        manifest_data,
        additional_files
    )


def create_grammar_plugin(
    base_path: Path,
    plugin_id: str,
    ilr_version: str = "1.0.0",
    schema_content: Optional[str] = None,
    definition_files: Optional[Dict[str, str]] = None
) -> Path:
    """Create a grammar definition plugin"""
    if schema_content is None:
        schema_content = '{"type": "object", "properties": {}}'
    
    manifest_data = create_valid_manifest(
        plugin_id=plugin_id,
        plugin_type="grammar_definition",
        entry_point={"type": "module"},
        grammar_details={
            "ilr_version": ilr_version,
            "grammar_construct_schema_path": "schema.json",
            "definition_provider_details": {
                "format": "yaml",
                "root_directory": "definitions",
                "file_mappings": [
                    {
                        "definition_type": "construct",
                        "path_glob": "*.yaml"
                    }
                ]
            }
        }
    )
    
    additional_files = {
        "schema.json": schema_content,
        "definitions/.gitkeep": ""  # Ensure directory exists
    }
    
    if definition_files:
        for filename, content in definition_files.items():
            additional_files[f"definitions/{filename}"] = content
    
    return create_plugin_directory(
        base_path,
        plugin_id,
        manifest_data,
        additional_files
    )


def assert_plugin_loaded(manager, plugin_id: str, expected_name: Optional[str] = None):
    """Assert that a plugin was successfully loaded"""
    assert plugin_id in manager.plugins, f"Plugin '{plugin_id}' not found in loaded plugins"
    
    plugin = manager.plugins[plugin_id]
    if expected_name:
        assert plugin.name == expected_name
    
    return plugin


def assert_error_contains(manager, error_code: str, additional_text: Optional[str] = None):
    """Assert that an error with the given code exists"""
    errors = manager.get_errors()
    assert any(error_code in error for error in errors), \
        f"No error containing '{error_code}' found. Errors: {errors}"
    
    if additional_text:
        assert any(error_code in error and additional_text in error for error in errors), \
            f"No error containing both '{error_code}' and '{additional_text}' found. Errors: {errors}"


def get_error_by_code(manager, error_code: str) -> Optional[str]:
    """Get the first error containing the given error code"""
    for error in manager.get_errors():
        if error_code in error:
            return error
    return None


def count_errors_with_code(manager, error_code: str) -> int:
    """Count how many errors contain the given error code"""
    return sum(1 for error in manager.get_errors() if error_code in error)


class MockPluginClass:
    """A mock plugin class for testing"""
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.initialized = True
        self.translate_called = False
        self.translate_input = None
        self.translate_output = {"translated": True}
    
    def translate_to_ilr(self, source):
        self.translate_called = True
        self.translate_input = source
        return self.translate_output
