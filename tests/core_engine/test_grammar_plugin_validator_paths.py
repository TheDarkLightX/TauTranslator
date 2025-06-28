# tests/core_engine/test_grammar_plugin_validator_paths.py
"""
Tests for the GrammarPluginValidator focusing on file system and path validation.
"""

import unittest
from pathlib import Path
from .base_validator_test import BaseGrammarPluginValidatorTest

class TestGrammarPluginValidatorPaths(BaseGrammarPluginValidatorTest):
    """
    Test suite for path and file system validation in GrammarPluginValidator.
    """

    def test_grammar_file_does_not_exist(self):
        """Tests failure when the specified grammar_file does not exist on disk."""
        manifest = self._get_base_valid_manifest()
        # Intentionally *not* calling _prepare_plugin_files for the grammar file
        
        is_valid, _, errors = self.validator.validate_manifest(manifest, self.temp_plugin_dir)
        
        self.assertFalse(is_valid)
        grammar_file = manifest["grammar_details"]["grammar_file"]
        expected_path = self.temp_plugin_dir / grammar_file
        self.assertIn(f"Grammar file '{grammar_file}' (path '{expected_path}') does not exist", errors[0])

    def test_ilr_construct_mappings_schema_file_is_directory(self):
        """Tests failure when a path points to a directory instead of a file."""
        manifest = self._get_base_valid_manifest()
        self._prepare_plugin_files(manifest) # Prepare all files first
        
        # Overwrite one file with a directory
        mappings_path = self.temp_plugin_dir / manifest["grammar_details"]["ilr_construct_mappings_schema"]
        mappings_path.unlink()
        mappings_path.mkdir()

        is_valid, _, errors = self.validator.validate_manifest(manifest, self.temp_plugin_dir)
        
        self.assertFalse(is_valid)
        self.assertIn("does not exist or is not a file", errors[0])

    def test_path_resolution_is_correct(self):
        """Verifies that file paths are correctly resolved to absolute paths."""
        manifest = self._get_base_valid_manifest()
        self._prepare_plugin_files(manifest)
        
        is_valid, parsed_config, errors = self.validator.validate_manifest(manifest, self.temp_plugin_dir)
        
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
        
        # Check that paths in the parsed_config are absolute and correct
        grammar_file_path = parsed_config.get("resolved_grammar_file_path")
        self.assertIsNotNone(grammar_file_path)
        self.assertTrue(Path(grammar_file_path).is_absolute())
        self.assertEqual(Path(grammar_file_path).name, "main.lark")

        mappings_path = parsed_config.get("resolved_ilr_construct_mappings_schema_path")
        self.assertIsNotNone(mappings_path)
        self.assertTrue(Path(mappings_path).is_absolute())
        self.assertEqual(Path(mappings_path).name, "mappings.json")

if __name__ == '__main__':
    unittest.main()
