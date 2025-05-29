# tests/core_engine/test_grammar_plugin_validator.py
"""
Tests for the new GrammarPluginValidator (schema-based).
"""

import unittest
import os
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Tuple
from unittest.mock import patch, MagicMock
from tau_translator_omega.core_engine.grammar_plugin_validator import GrammarPluginValidator, SCHEMA_FILE_PATH

# Configure logging for tests (optional, but can be helpful)
# logging.basicConfig(level=logging.DEBUG)

class TestGrammarPluginValidatorSchema(unittest.TestCase):
    validator: GrammarPluginValidator
    schema_for_test_construction: Dict[str, Any]
    temp_dir_obj: tempfile.TemporaryDirectory
    temp_plugin_dir: Path

    @classmethod
    def setUpClass(cls):
        """Load the schema once for all tests and instantiate validator."""
        # Ensure the schema path used by the validator itself is valid
        cls.assertTrue(os.path.exists(SCHEMA_FILE_PATH),
                       f"Schema file must exist at the path used by the validator: {SCHEMA_FILE_PATH}")

        # For tests, we can also load the schema directly to help construct test cases
        # but the validator should use its own SCHEMA_FILE_PATH
        try:
            with open(SCHEMA_FILE_PATH, 'r', encoding='utf-8') as f:
                cls.schema_for_test_construction = json.load(f)
        except Exception as e:
            raise AssertionError(f"Failed to load schema for test construction: {e}")

        cls.validator = GrammarPluginValidator(core_ilr_version="1.0.0", logger_instance=logging.getLogger("test_gpv_logger"))

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources if any (none here after changes)."""
        pass

    def setUp(self):
        """Reset validator errors and set up a fresh temporary directory before each test."""
        self.validator.errors = [] # Ensure errors are cleared from previous tests
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_plugin_dir = Path(self.temp_dir_obj.name)

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.temp_dir_obj.cleanup()

    def test_validator_loads_schema_on_init(self):
        """Test that the validator loads its schema upon instantiation."""
        self.assertIsNotNone(self.validator.schema, "Validator should have loaded the schema.")
        self.assertEqual(self.validator.schema.get('title'), "Plugin Manifest for Grammar Definition")

    def test_valid_lark_manifest_basic(self):
        """Test a minimal valid Lark manifest."""
        manifest = {
            "id": "dev.larky.simple",
            "name": "Simple Lark",
            "version": "1.0.0-alpha",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        grammar_file_path = manifest.get("grammar_details", {}).get("grammar_file")
        if grammar_file_path:
            (self.temp_plugin_dir / grammar_file_path).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_plugin_dir / grammar_file_path).touch()

        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(errors, [])
        self.assertEqual(parsed_config.get("formalism"), "lark")
        self.assertTrue(Path(parsed_config.get("resolved_grammar_file_path")).name == "grammar.lark")

    def test_valid_antlr_manifest_basic(self):
        """Test a minimal valid ANTLR manifest."""
        manifest = {
            "id": "com.example.antlr_min",
            "name": "Minimal ANTLR",
            "version": "0.0.1",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "antlr4",
                "grammar_file": "g/MyGrammar.g4",
                "antlr_version": "4.9",
                "ilr_version": "1.0.0"
            }
        }
        grammar_file_path = manifest.get("grammar_details", {}).get("grammar_file")
        if grammar_file_path:
            (self.temp_plugin_dir / grammar_file_path).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_plugin_dir / grammar_file_path).touch()

        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(errors, [])
        self.assertEqual(parsed_config.get("formalism"), "antlr4")
        self.assertEqual(parsed_config.get("antlr_version"), "4.9")
        self.assertTrue(Path(parsed_config.get("resolved_grammar_file_path")).name == "MyGrammar.g4")

    def test_valid_manifest_with_all_optional_fields(self):
        """Test a valid manifest that includes optional fields."""
        manifest = {
            "id": "org.tau.comprehensive",
            "name": "Comprehensive Grammar Plugin",
            "version": "2.1.3-beta+build.123",
            "description": "A detailed grammar plugin with all bells and whistles.",
            "author": "Tau Translator Team",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "src/tau_lang.lark",
                "entry_rule": "tau_compilation_unit",
                "transformer_class": "tau_translator_omega.grammars.common.GenericLarkTransformer",
                "ilr_version": "1.0.0"
            }
        }
        grammar_file_path = manifest.get("grammar_details", {}).get("grammar_file")
        if grammar_file_path:
            (self.temp_plugin_dir / grammar_file_path).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_plugin_dir / grammar_file_path).touch()

        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(errors, [])
        # parsed_config from GrammarPluginValidator is specialized and doesn't contain all original manifest fields like 'author'.
        # It contains resolved paths and critical grammar details.
        # Example check for a field that *is* expected in this specialized parsed_config:
        self.assertIn("resolved_grammar_file_path", parsed_config)
        self.assertEqual(parsed_config.get("formalism"), "lark")

    def test_missing_required_id(self):
        """Test manifest missing 'id'."""
        manifest = {
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'id' is a required property (path: [])", errors)

    def test_missing_required_name(self):
        """Test manifest missing 'name'."""
        manifest = {
            "id": "com.example.test",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'name' is a required property (path: [])", errors)

    def test_missing_required_version(self):
        """Test manifest missing 'version'."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'version' is a required property (path: [])", errors)

    def test_missing_required_plugin_type(self):
        """Test manifest missing 'plugin_type'."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'plugin_type' is a required property (path: [])", errors)

    def test_missing_required_ilr_versions_supported(self):
        """Test manifest missing 'ilr_versions_supported'."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'ilr_versions_supported' is a required property (path: [])", errors)

    def test_missing_required_grammar_details(self):
        """Test manifest missing 'grammar_details'."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"]
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'grammar_details' is a required property (path: [])", errors)

    def test_missing_required_formalism_in_grammar_details(self):
        """Test manifest missing 'formalism' in 'grammar_details'."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        # Expecting error about antlr_version due to schema structure when formalism is missing
        self.assertIn("Manifest schema validation error: 'antlr_version' is a required property (path: ['grammar_details'])", errors)

    def test_missing_required_grammar_file_in_grammar_details(self):
        """Test manifest missing 'grammar_file' in 'grammar_details'."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'grammar_file' is a required property (path: ['grammar_details'])", errors)

    def test_invalid_version_format(self):
        """Test manifest with 'version' not matching SemVer pattern."""
        manifest = {
            "id": "com.example.test.version_invalid",
            "name": "Version Invalid Format Test",
            "version": "1.0", # Invalid format
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        # Pattern for SemVer, aiming to match jsonschema error messages which seem to use \\d
        semver_pattern_str = r"^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$"
        expected_error = f"Manifest schema validation error: '1.0' does not match '{semver_pattern_str}' (path: ['version'])"
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], expected_error)

    def test_invalid_plugin_type_value(self):
        """Test manifest with invalid 'plugin_type' value."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "not_grammar",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        expected_error_msg = "Manifest schema validation error: 'grammar_definition' was expected (path: ['plugin_type'])"
        self.assertIn(expected_error_msg, errors)

    def test_ilr_versions_supported_not_array(self):
        """Test 'ilr_versions_supported' is not an array."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": "0.1.0",
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: '0.1.0' is not of type 'array' (path: ['ilr_versions_supported'])", errors)

    def test_ilr_versions_supported_array_not_of_strings(self):
        """Test 'ilr_versions_supported' array contains non-string."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0", 123],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 123 is not of type 'string' (path: ['ilr_versions_supported', 1])", errors)

    def test_invalid_formalism_value(self):
        """Test manifest with invalid 'formalism' value."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "cobol",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'cobol' is not one of ['antlr4', 'lark'] (path: ['grammar_details', 'formalism'])", errors)

    def test_antlr_version_missing_for_antlr4_formalism(self):
        """Test 'antlr_version' is missing when 'formalism' is 'antlr4'."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "antlr4",
                "grammar_file": "grammar.g4",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'antlr_version' is a required property (path: ['grammar_details'])", errors)

    def test_antlr_version_present_for_lark_formalism_is_valid(self):
        """Test 'antlr_version' present for 'lark' formalism (should be ignored and valid)."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "antlr_version": "4.10", # extraneous
                "ilr_version": "1.0.0"
            }
        }
        grammar_file_path = manifest.get("grammar_details", {}).get("grammar_file")
        if grammar_file_path:
            (self.temp_plugin_dir / grammar_file_path).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_plugin_dir / grammar_file_path).touch()

        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(errors, [])

    def test_entry_rule_invalid_type(self):
        """Test 'entry_rule' in 'grammar_details' is not a string."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "entry_rule": 12345,
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 12345 is not of type 'string' (path: ['grammar_details', 'entry_rule'])", errors)

    def test_valid_lark_manifest_with_transformer_class(self):
        """Test a valid Lark manifest including 'transformer_class'."""
        manifest = {
            "id": "dev.larky.transformer",
            "name": "Lark With Transformer",
            "version": "1.1.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar/my_lang.lark",
                "transformer_class": "my_plugin.transformers.SpecificTransformer",
                "ilr_version": "1.0.0"
            }
        }
        grammar_file_path = manifest.get("grammar_details", {}).get("grammar_file")
        if grammar_file_path:
            (self.temp_plugin_dir / grammar_file_path).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_plugin_dir / grammar_file_path).touch()

        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(errors, [])

    def test_invalid_transformer_class_format(self):
        """Test 'transformer_class' with a format not matching FQN pattern."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "transformer_class": "invalid-class-name",
                "ilr_version": "1.0.0"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'invalid-class-name' does not match '^[a-zA-Z_][a-zA-Z0-9_]*(\\\\.[a-zA-Z_][a-zA-Z0-9_]*)+$' (path: ['grammar_details', 'transformer_class'])", errors)

    def test_valid_antlr_manifest_with_transformer_class(self):
        """Test ANTLR manifest with 'transformer_class' (should be allowed by schema)."""
        manifest = {
            "id": "com.example.antlr_with_transformer",
            "name": "ANTLR With Optional Transformer",
            "version": "0.2.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "antlr4",
                "grammar_file": "grammars/my_antlr.g4",
                "antlr_version": "4.13",
                "transformer_class": "some.optional.Transformer",
                "ilr_version": "1.0.0"
            }
        }
        grammar_file_path = manifest.get("grammar_details", {}).get("grammar_file")
        if grammar_file_path:
            (self.temp_plugin_dir / grammar_file_path).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_plugin_dir / grammar_file_path).touch()

        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(errors, [])

    # Test for grammar file not existing - this is beyond schema validation
    def test_grammar_file_not_exists(self):
        """Test grammar file does not exist."""
        manifest = {
            "id": "dev.larky.no_file",
            "name": "Lark No File",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0.0"
            }
        }
        # Do NOT create the dummy grammar file here
        grammar_file_relative = manifest["grammar_details"]["grammar_file"]
        grammar_file_path_in_test = self.temp_plugin_dir / grammar_file_relative

        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        expected_error_msg = f"Grammar file '{grammar_file_relative}' (path '{grammar_file_path_in_test}') does not exist for plugin {manifest['id']}."
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], expected_error_msg)

    def test_grammar_file_is_directory(self):
        """Test grammar file is a directory."""
        manifest = {
            "id": "dev.larky.dir_as_file",
            "name": "Lark Dir As File",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "a_directory_named_grammar.lark", # Unique name for this test
                "ilr_version": "1.0.0"
            }
        }
        # Create a directory instead of a file
        grammar_file_relative = manifest["grammar_details"]["grammar_file"]
        grammar_file_path_in_test_dir = self.temp_plugin_dir / grammar_file_relative
        grammar_file_path_in_test_dir.mkdir(parents=True, exist_ok=True)

        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        # This test expects the error from the os.path.isfile check block in the validator
        expected_error_msg = f"Grammar file '{grammar_file_relative}' (resolved to '{grammar_file_path_in_test_dir.resolve()}') does not exist or is not a file for plugin {manifest['id']}."
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], expected_error_msg)

    def test_grammar_details_missing_ilr_version(self):
        """Test manifest missing 'ilr_version' in 'grammar_details'."""
        manifest = {
            "id": "com.example.test",
            "name": "Test Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark"
            }
        }
        # Schema validation, plugin_dir content doesn't matter for this failure
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        self.assertIn("Manifest schema validation error: 'ilr_version' is a required property (path: ['grammar_details'])", errors)

    def test_grammar_details_ilr_version_invalid_format(self):
        """Test 'grammar_details.ilr_version' with an invalid format."""
        manifest = {
            "id": "com.example.test.ilr_version_invalid",
            "name": "ILR Version Invalid Format Test",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_version": "1.0" # Invalid format
            }
        }
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        # Pattern for SemVer, aiming to match jsonschema error messages which seem to use \\d
        semver_pattern_str = r"^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$"
        expected_error = f"Manifest schema validation error: '1.0' does not match '{semver_pattern_str}' (path: ['grammar_details', 'ilr_version'])"
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], expected_error)

    def test_ilr_construct_mappings_schema_valid_path(self):
        """Test valid 'ilr_construct_mappings_schema' path."""
        manifest = {
            "id": "dev.larky.mappings",
            "name": "Lark With Mappings",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_construct_mappings_schema": "mappings/constructs.json",
                "ilr_version": "1.0.0"
            }
        }
        grammar_file_path = manifest.get("grammar_details", {}).get("grammar_file")
        if grammar_file_path:
            (self.temp_plugin_dir / grammar_file_path).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_plugin_dir / grammar_file_path).touch()
        
        mappings_schema_path = manifest.get("grammar_details", {}).get("ilr_construct_mappings_schema")
        if mappings_schema_path:
            (self.temp_plugin_dir / mappings_schema_path).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_plugin_dir / mappings_schema_path).touch()

        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertTrue(is_valid, f"Validation failed with errors: {errors}")
        self.assertEqual(errors, [])
        self.assertIn("resolved_ilr_construct_mappings_schema_path", parsed_config)
        self.assertTrue(Path(parsed_config["resolved_ilr_construct_mappings_schema_path"]).name == "constructs.json")

    def test_ilr_construct_mappings_schema_file_not_exists(self):
        """Test 'ilr_construct_mappings_schema' file does not exist."""
        manifest = {
            "id": "dev.larky.mappings_no_file",
            "name": "Lark Mappings No File",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar.lark",
                "ilr_construct_mappings_schema": "mappings/nonexistent.json", # This file won't be created
                "ilr_version": "1.0.0"
            }
        }
        grammar_file_path = manifest.get("grammar_details", {}).get("grammar_file")
        if grammar_file_path:
            (self.temp_plugin_dir / grammar_file_path).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_plugin_dir / grammar_file_path).touch()
        
        # Do NOT create the dummy ilr_construct_mappings_schema file here
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, plugin_dir=self.temp_plugin_dir)
        self.assertFalse(is_valid)
        # The error comes from the initial Path.exists() check for the unresolved path
        expected_error_msg = f"ILR construct mappings schema file 'mappings/nonexistent.json' (path '{self.temp_plugin_dir / 'mappings/nonexistent.json'}') does not exist for plugin {manifest.get('id')}."
        self.assertIn(expected_error_msg, errors)

if __name__ == '__main__':
    unittest.main()
