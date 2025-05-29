import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from tau_translator_omega.core_engine.plugin_manager import PluginManager
from tau_translator_omega.core_engine.plugin import Plugin, PluginEntryPoint


class TestPluginManagerManifestProcessing:
    """Test manifest file processing"""

    def test_process_manifest_file_not_found(self, tmp_path):
        """Test processing when manifest file doesn't exist"""
        manager = PluginManager(plugin_dirs=tmp_path)
        manifest_path = tmp_path / "missing" / "manifest.json"
        plugin_dir = tmp_path / "missing"
        
        result = manager._process_manifest(manifest_path, plugin_dir)
        
        assert result is None
        assert any(e.code == "MANIFEST_NOT_FOUND" for e in manager.errors)

    def test_process_manifest_json_decode_error(self, tmp_path):
        """Test processing manifest with invalid JSON"""
        manager = PluginManager(plugin_dirs=tmp_path)
        manifest_path = tmp_path / "manifest.json"
        
        with open(manifest_path, 'w') as f:
            f.write("{ invalid json")
        
        result = manager._process_manifest(manifest_path, tmp_path)
        
        assert result is None
        assert any(e.code == "MANIFEST_JSON_MALFORMED" for e in manager.errors)

    @patch('tau_translator_omega.core_engine.plugin_manager.PluginManager._load_and_instantiate_plugin')
    def test_process_manifest_valid_no_schema(self, mock_load_instantiate, tmp_path):
        """Test processing valid manifest when manager.manifest_schema is None"""
        mock_load_instantiate.return_value = Mock() # Simulate successful instantiation
        manager = PluginManager(plugin_dirs=tmp_path)
        manager.manifest_schema = None  # Simulate no schema validation

        # Create a dummy grammar file for the validator to find
        dummy_grammar_file = tmp_path / "dummy.lark"
        dummy_grammar_file.touch()

        manifest_data = {
            "id": "test-plugin", # Changed from plugin_id for consistency with Plugin.from_manifest
            "name": "Test Plugin", # Changed from plugin_name
            "version": "1.0.0",    # Changed from plugin_version
            "plugin_type": "grammar_definition", 
            "ilr_versions_supported": ["1.0.0"], 
            "entry_point": {
                "type": "module",
                "module_path": "dummy.test_plugin",
                "class_name": "TestPlugin"
            }, 
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "dummy.lark",
                "ilr_version": "1.0.0" # Added as schema expects it
            }
        }
        
        manifest_path = tmp_path / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f)
        
        result = manager._process_manifest(manifest_path, tmp_path)
        
        assert result is not None
        assert result.id == "test-plugin"
        assert manager.errors == [] # Expect no errors for a valid manifest

    def test_process_manifest_schema_validation_error(self, tmp_path):
        """Test processing manifest that fails schema validation (e.g., in grammar_details)"""
        manager = PluginManager(plugin_dirs=tmp_path)
        
        # Create a dummy grammar file because its existence is checked
        dummy_grammar_file = tmp_path / "test_grammar.lark"
        dummy_grammar_file.touch()

        manifest_data = {
            "id": "test-plugin",
            "name": "Schema Test Plugin", # Added
            "version": "1.0.0",          # Added
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"], # Added
            "entry_point": {
                "type": "module",
                "module_path": "dummy.schema_test_plugin",
                "class_name": "SchemaTestPlugin"
            }, 
            "grammar_details": {
                "formalism": "lark",
                # 'grammar_file' is deliberately missing to test schema validation for this field
                # or an invalid value for another field like ilr_version can be used.
                # Let's test for missing 'grammar_file' as per schema's required list for grammar_details
                "ilr_version": "1.0.0" # Keep this valid for now to isolate grammar_file issue
            }
        }
        
        manifest_path = tmp_path / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f)
        
        result = manager._process_manifest(manifest_path, tmp_path)
        
        assert result is None
        assert any(
            e.plugin_id == "test-plugin" and
            e.code == "GRAMMAR_DEFINITION_VALIDATION_ERROR" and 
            ("'grammar_file' is a required property" in e.message) # Specific check
            # ('invalid-ilr-version-format' does not match" in e.message) 
            for e in manager.errors
        )

    @patch('tau_translator_omega.core_engine.plugin_manager.PluginManager._load_and_instantiate_plugin')
    def test_process_manifest_pattern_validation_error(self, mock_load_instantiate, tmp_path):
        """Test processing manifest with pattern validation error in grammar_details"""
        mock_load_instantiate.return_value = Mock() # Simulate successful instantiation
        manager = PluginManager(plugin_dirs=tmp_path)
        
        dummy_grammar_file = tmp_path / "grammar.lark"
        dummy_grammar_file.touch()

        manifest_data = {
            "id": "pattern-test", 
            "name": "Pattern Test Plugin", # Added
            "version": "1.0.0",           # Added
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"], # Added
            "entry_point": {
                "type": "module",
                "module_path": "dummy.pattern_test_plugin",
                "class_name": "PatternTestPlugin"
            }, 
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark", 
                "ilr_version": "1.0", # Invalid: schema expects X.Y.Z pattern for ilr_version
            }
        }
        
        manifest_path = tmp_path / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f)
        
        result = manager._process_manifest(manifest_path, tmp_path)
        
        assert result is None
        assert any(
            e.plugin_id == "pattern-test" and
            e.code == "GRAMMAR_DEFINITION_VALIDATION_ERROR" and 
            ("'1.0' does not match" in e.message and
             "(path: ['grammar_details', 'ilr_version'])" in e.message and
             "Manifest schema validation error:" in e.message)
            for e in manager.errors
        )

    @patch('tau_translator_omega.core_engine.plugin_manager.PluginManager._load_and_instantiate_plugin')
    def test_process_manifest_grammar_plugin_valid(self, mock_load_instantiate, tmp_path):
        """Test processing valid grammar definition plugin"""
        mock_load_instantiate.return_value = Mock() # Simulate successful instantiation
        manager = PluginManager(plugin_dirs=tmp_path)
        # manager.manifest_schema = None # Let Plugin.from_manifest use its default schema logic
        
        # Create required files for grammar plugin
        grammar_file = tmp_path / "my_grammar.g4"
        grammar_file.touch() # Create dummy grammar file
        
        manifest_data = {
            "id": "grammar-plugin",
            "name": "Grammar Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "entry_point": {
                "type": "module",
                "module_path": "dummy.grammar_plugin",
                "class_name": "GrammarPlugin"
            },
            "ilr_versions_supported": ["1.0.0"], # For ILR compatibility check
            "grammar_details": {
                "formalism": "antlr4",
                "grammar_file": "my_grammar.g4",
                "ilr_version": "1.0.0",
                "antlr_version": "4.9"
            }
        }
        
        manifest_path = tmp_path / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f)
        
        # No need to mock GrammarPluginValidator.validate_manifest anymore if we want to test its actual logic
        # If we were to mock it:
        # with patch('tau_translator_omega.core_engine.grammar_plugin_validator.GrammarPluginValidator.validate_manifest') as mock_validate:
        #     mock_validate.return_value = (True, {"resolved_grammar_file_path": str(grammar_file)}, []) 
            
        result = manager._process_manifest(manifest_path, tmp_path)

        assert result is not None
        assert result.id == "grammar-plugin"
        assert result.plugin_specific_config.get("resolved_grammar_file_path") == str(grammar_file.resolve())
        assert manager.errors == []
        # assert manager.errors_by_plugin == {} # This attribute doesn't exist