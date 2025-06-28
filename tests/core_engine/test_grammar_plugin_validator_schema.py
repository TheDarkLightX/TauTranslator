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
from typing import Dict, Any

from tau_translator_omega.core_engine.plugins.grammar_plugin_validator import GrammarPluginValidator, SCHEMA_FILE_PATH
from .base_validator_test import BaseGrammarPluginValidatorTest

# Configure logging for tests
log = logging.getLogger(__name__)

class TestGrammarPluginValidatorSchema(BaseGrammarPluginValidatorTest):
    """
    Test suite for schema-related validation in GrammarPluginValidator.
    """

    def test_validator_loads_schema_successfully(self):
        """Ensures the validator loads its schema upon instantiation."""
        self.assertIsNotNone(self.validator.schema)
        self.assertEqual(self.validator.schema.get('title'), "TauTranslatorOmega Plugin Manifest")

    def test_full_valid_manifest(self):
        """Tests a manifest with all required and optional fields correctly filled."""
        manifest = self._get_base_valid_manifest()
        self._prepare_plugin_files(manifest)
        
        is_valid, _, errors = self.validator.validate_manifest(manifest, self.temp_plugin_dir)
        
        self.assertTrue(is_valid, f"Validation failed unexpectedly: {errors}")
        self.assertEqual(errors, [])

    def test_manifest_missing_required_field_id(self):
        """Tests validation failure when a top-level required field ('id') is missing."""
        manifest = self._get_base_valid_manifest()
        del manifest["id"]
        self._prepare_plugin_files(manifest)

        is_valid, _, errors = self.validator.validate_manifest(manifest, self.temp_plugin_dir)

        self.assertFalse(is_valid)
        self.assertIn("'id' is a required property", errors[0])

    def test_manifest_with_invalid_version_format(self):
        """Tests validation failure for a non-SemVer version string."""
        manifest = self._get_base_valid_manifest()
        manifest["version"] = "not-a-version"
        self._prepare_plugin_files(manifest)

        is_valid, _, errors = self.validator.validate_manifest(manifest, self.temp_plugin_dir)

        self.assertFalse(is_valid)
        self.assertIn("'not-a-version' does not match", errors[0])
        self.assertIn("path: ['version']", errors[0])

    def test_grammar_details_missing_required_field_formalism(self):
        """Tests failure when a nested required field ('formalism') is missing."""
        manifest = self._get_base_valid_manifest()
        del manifest["grammar_details"]["formalism"]
        self._prepare_plugin_files(manifest)
        
        is_valid, _, errors = self.validator.validate_manifest(manifest, self.temp_plugin_dir)
        
        self.assertFalse(is_valid)
        self.assertIn("'formalism' is a required property", errors[0])
        self.assertIn("path: ['grammar_details']", errors[0])

    def test_transformer_class_invalid_fqn_format(self):
        """Tests failure when transformer_class is not a valid Python FQN."""
        manifest = self._get_base_valid_manifest()
        manifest["grammar_details"]["transformer_class"] = "invalid-fqn"
        self._prepare_plugin_files(manifest)

        is_valid, _, errors = self.validator.validate_manifest(manifest, self.temp_plugin_dir)

        self.assertFalse(is_valid)
        self.assertIn("'invalid-fqn' does not match", errors[0])
        self.assertIn("path: ['grammar_details', 'transformer_class']", errors[0])

    def test_antlr_manifest_with_no_transformer_is_valid(self):
        """Ensures ANTLR manifests are valid without a transformer_class, as it's optional."""
        manifest = self._get_base_valid_manifest()
        manifest["grammar_details"]["formalism"] = "antlr"
        del manifest["grammar_details"]["transformer_class"] # It's optional
        self._prepare_plugin_files(manifest)

        is_valid, _, errors = self.validator.validate_manifest(manifest, self.temp_plugin_dir)

        self.assertTrue(is_valid, f"Validation failed unexpectedly for ANTLR manifest: {errors}")
        self.assertEqual(errors, [])

if __name__ == '__main__':
    unittest.main()
