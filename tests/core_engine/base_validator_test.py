# tests/core_engine/base_validator_test.py
"""
Base test class for GrammarPluginValidator tests.
Provides common setup, teardown, and helper methods.
"""

import unittest
import os
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any

from tau_translator_omega.core_engine.plugins.grammar_plugin_validator import GrammarPluginValidator, SCHEMA_FILE_PATH

# Configure logging for tests
log = logging.getLogger(__name__)

class BaseGrammarPluginValidatorTest(unittest.TestCase):
    """
    Base class for validator tests, providing shared setup and helpers.
    """
    validator: GrammarPluginValidator
    temp_dir_obj: tempfile.TemporaryDirectory
    temp_plugin_dir: Path

    @classmethod
    def setUpClass(cls):
        """Load the schema once and instantiate the validator."""
        if not os.path.exists(SCHEMA_FILE_PATH):
            raise FileNotFoundError(f"Critical: Schema file not found at {SCHEMA_FILE_PATH}")
        cls.validator = GrammarPluginValidator(
            core_ilr_version="1.0.0", 
            logger_instance=log
        )

    def setUp(self):
        """Set up a fresh temporary directory and validator instance for each test."""
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_plugin_dir = Path(self.temp_dir_obj.name)
        # Reset validator state before each test
        self.validator.errors = []

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.temp_dir_obj.cleanup()

    def _get_base_valid_manifest(self) -> Dict[str, Any]:
        """
        Returns a dictionary representing a complete and valid plugin manifest.
        Tests can modify this baseline to test specific invalid cases.
        """
        return {
            "manifest_version": "1.0",
            "id": "dev.test.valid-plugin",
            "name": "Valid Test Plugin",
            "version": "1.0.0",
            "description": "A baseline valid plugin for testing.",
            "author": "Test Suite",
            "license": "MIT",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "target_grammar": {"grammar_name": "TauCore"},
            "output_details": {"format_mime_type": "application/tau+text"},
            "entry_point": {"type": "module", "module_path": "my_plugin.translator", "function_name": "translate"},
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "grammar/main.lark",
                "ilr_version": "1.0.0",
                "grammar_construct_schema_path": "schemas/constructs.json",
                "ilr_construct_mappings_schema": "mappings/mappings.json",
                "transformer_class": "my_plugin.transformer.MyTransformer",
                "definition_provider_details": {"type": "local_files", "root_directory": "."}
            }
        }

    def _prepare_plugin_files(self, manifest: Dict[str, Any]):
        """
        Create dummy files and directories required by the manifest for validation to pass.
        """
        details = manifest.get("grammar_details", {})
        for key in ["grammar_file", "grammar_construct_schema_path", "ilr_construct_mappings_schema"]:
            if path_str := details.get(key):
                full_path = self.temp_plugin_dir / path_str
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.touch()
