import pytest
import json
from pathlib import Path
from typing import Dict, Any

# Common dummy plugin code, can be shared across tests via this conftest
DUMMY_PLUGIN_MODULE_CONTENT = """
class DummyPlugin:
    def __init__(self, **kwargs):
        # Allow any kwargs for simplicity in tests not focused on __init__ args
        pass
    def execute(self):
        return 'dummy executed'
"""

@pytest.fixture
def create_plugin_env_func(tmp_path: Path):
    """
    Pytest fixture that provides a helper function to create a standard 
    plugin directory structure for testing.
    The returned function uses the 'tmp_path' fixture for its root.
    """
    def _create_plugin_environment(
        plugin_id: str, 
        manifest_content: Dict[str, Any], 
        module_file_name: str = "dummy_module.py", 
        module_content: str = DUMMY_PLUGIN_MODULE_CONTENT
    ) -> Path:
        """Helper to create a standard plugin directory structure for testing."""
        plugins_root_dir = tmp_path / "plugins"
        plugins_root_dir.mkdir(exist_ok=True)
        
        plugin_dir = plugins_root_dir / plugin_id
        plugin_dir.mkdir(exist_ok=True) # Allow re-creation for multiple tests using same tmp_path
        
        manifest_file_path = plugin_dir / "manifest.json"
        with open(manifest_file_path, 'w') as f:
            json.dump(manifest_content, f)
            
        if module_file_name and module_content:
            module_file_path = plugin_dir / module_file_name
            with open(module_file_path, 'w') as f:
                f.write(module_content)
                
        return plugins_root_dir
    
    return _create_plugin_environment
