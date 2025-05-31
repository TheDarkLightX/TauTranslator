# src/tau_translator_omega/core_engine/grammar_plugin_validator.py
"""
Validates 'grammar_definition' type plugin manifests for TauTranslatorOmega
using a JSON schema.
"""

import json
import os
import logging
from jsonschema import validate, ValidationError
from typing import List, Dict, Any, Tuple
from pathlib import Path

from .plugin import BasePluginValidator

# Determine the schema file path relative to this file's location
# This assumes the 'schemas' directory is at the project root,
# and this file is 'src/tau_translator_omega/core_engine/grammar_plugin_validator.py'
# Project Root -> schemas/plugin_manifest_grammar_v1.json
# This file   -> src/tau_translator_omega/core_engine/grammar_plugin_validator.py
# Path from this file to project root: ../../../
SCHEMA_FILE_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "..", # up to project root (src/tau_translator_omega/ -> src/ -> ./ )
    "schemas", 
    "plugin_manifest_grammar_v1.json"
))

class GrammarPluginValidator(BasePluginValidator):
    """
    Validates the manifest of a 'grammar_definition' plugin against a JSON schema.
    """

    def __init__(self, core_ilr_version: str, logger_instance):
        """
        Initializes the validator, loading the JSON schema.
        Args:
            core_ilr_version: The core ILR version string.
            logger_instance: The logger instance to use.
        """
        super().__init__(core_ilr_version, logger_instance) 
        self.schema: Dict[str, Any] | None = self._load_schema()
        self.errors: List[str] = [] 

    def _load_schema(self) -> Dict[str, Any] | None:
        """
        Loads the grammar plugin manifest JSON schema.
        Returns the schema as a dictionary, or None if loading fails.
        """
        try:
            if not os.path.exists(SCHEMA_FILE_PATH):
                self.logger.error(f"Schema file not found: {SCHEMA_FILE_PATH}")
                # This is a critical error for the validator's function
                raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE_PATH}")
            with open(SCHEMA_FILE_PATH, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
                self.logger.info(f"Successfully loaded grammar plugin manifest schema from: {SCHEMA_FILE_PATH}")
                return schema_data
        except FileNotFoundError:
            # Already logged, re-raise to indicate critical failure
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON schema from {SCHEMA_FILE_PATH}: {e}")
            raise # Critical failure
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while loading schema from {SCHEMA_FILE_PATH}: {e}")
            raise # Critical failure


    def validate_manifest(self, manifest_data: Dict[str, Any], plugin_dir: Path) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validates the provided manifest data against the loaded JSON schema and checks for grammar file existence.

        Args:
            manifest_data: The plugin manifest data as a dictionary.
            plugin_dir: The Path object representing the plugin's base directory.

        Returns:
            A tuple: (is_valid: bool, parsed_config: Dict[str, Any], errors: List[str])
        """
        self.errors = [] 
        parsed_config: Dict[str, Any] = {}

        if not self.schema:
            self.errors.append("Grammar plugin manifest schema not loaded. Validator cannot proceed.")
            self.logger.critical("Attempted to validate manifest, but schema is not loaded.")
            return False, parsed_config, self.errors

        try:
            validate(instance=manifest_data, schema=self.schema)
            self.logger.info(f"Manifest schema validation successful for plugin_id: {manifest_data.get('id', 'N/A')} in dir {plugin_dir}")
        except ValidationError as e:
            error_message = f"Manifest schema validation error: {e.message} (path: {list(e.path)})"
            self.errors.append(error_message)
            self.logger.warning(f"Manifest validation failed for plugin_id {manifest_data.get('id', 'N/A')} in dir {plugin_dir}: {error_message}")
            return False, parsed_config, self.errors
        except Exception as e:
            error_message = f"An unexpected error occurred during manifest schema validation: {e}"
            self.errors.append(error_message)
            self.logger.error(f"Unexpected schema validation error for plugin_id {manifest_data.get('id', 'N/A')} in dir {plugin_dir}: {e}", exc_info=True)
            return False, parsed_config, self.errors

        # Schema validation passed, now check grammar_file existence and populate parsed_config
        grammar_details = manifest_data.get("grammar_details", {})
        grammar_file_relative = grammar_details.get("grammar_file")

        if not grammar_file_relative:
            # This should ideally be caught by the JSON schema's 'required' fields for grammar_details.grammar_file
            # Adding a defensive check here.
            err_msg = f"'grammar_file' is missing in 'grammar_details' for plugin {manifest_data.get('id', 'N/A')}."
            self.errors.append(err_msg)
            self.logger.warning(err_msg)
            return False, parsed_config, self.errors

        try:
            grammar_file_path_unresolved = plugin_dir / str(grammar_file_relative)
            self.logger.info(f"Validating grammar file existence: {grammar_file_path_unresolved}")
            if not grammar_file_path_unresolved.exists():
                err_msg = f"Grammar file '{grammar_file_relative}' (path '{grammar_file_path_unresolved}') does not exist for plugin {manifest_data.get('id', 'N/A')}."
                self.errors.append(err_msg)
                self.logger.warning(err_msg)
                return False, parsed_config, self.errors

            resolved_grammar_file = grammar_file_path_unresolved.resolve()
            self.logger.info(f"Validating grammar file type: {resolved_grammar_file}")
            if not os.path.isfile(resolved_grammar_file):
                err_msg = f"Grammar file '{grammar_file_relative}' (resolved to '{resolved_grammar_file}') does not exist or is not a file for plugin {manifest_data.get('id', 'N/A')}."
                self.errors.append(err_msg)
                self.logger.warning(err_msg)
                return False, parsed_config, self.errors
            
            # Populate parsed_config with essential details
            parsed_config["resolved_grammar_file_path"] = str(resolved_grammar_file)
            parsed_config["formalism"] = grammar_details.get("formalism") # Schema ensures this exists
            if grammar_details.get("entry_rule"):
                parsed_config["entry_rule"] = grammar_details.get("entry_rule")
            if grammar_details.get("formalism") == "antlr4" and grammar_details.get("antlr_version"):
                parsed_config["antlr_version"] = grammar_details.get("antlr_version")
            if grammar_details.get("ilr_construct_mappings_schema"):
                 mappings_schema_relative = grammar_details.get("ilr_construct_mappings_schema")
                 mappings_schema_path_unresolved = plugin_dir / str(mappings_schema_relative)
                 self.logger.info(f"Validating ILR mappings schema existence: {mappings_schema_path_unresolved}")
                 if not mappings_schema_path_unresolved.exists():
                    err_msg = f"ILR construct mappings schema file '{mappings_schema_relative}' (path '{mappings_schema_path_unresolved}') does not exist for plugin {manifest_data.get('id', 'N/A')}."
                    self.errors.append(err_msg)
                    self.logger.warning(err_msg)
                    return False, parsed_config, self.errors

                 resolved_mappings_schema = mappings_schema_path_unresolved.resolve()
                 self.logger.info(f"Validating ILR mappings schema file type: {resolved_mappings_schema}")
                 if not os.path.isfile(resolved_mappings_schema):
                    err_msg = f"ILR construct mappings schema file '{mappings_schema_relative}' (resolved to '{resolved_mappings_schema}') does not exist or is not a file for plugin {manifest_data.get('id', 'N/A')}."
                    self.errors.append(err_msg)
                    self.logger.warning(err_msg)
                    return False, parsed_config, self.errors
                 parsed_config["resolved_ilr_construct_mappings_schema_path"] = str(resolved_mappings_schema)

            # Safeguard: If any errors were recorded but not explicitly returned as False, ensure validity is False.
            if self.errors:
                self.logger.error(
                    f"Internal logic error or unexpected state: self.errors is populated but validate_manifest was about to return True. "
                    f"Errors: {self.errors}. Plugin ID: {manifest_data.get('id', 'N/A')}"
                )
                # Ensure parsed_config is the initial empty one if we are forcing a False return here
                # However, if an error occurred after some parsing, it might contain partial data.
                # For now, let's return the current parsed_config, as it might give clues if this branch is hit.
                return False, parsed_config, self.errors

            self.logger.info(f"Grammar file and details validated for plugin {manifest_data.get('id', 'N/A')}. Config: {parsed_config}")
            return True, parsed_config, self.errors # self.errors should be empty here

        except FileNotFoundError: # Should be caught by is_file() check, but as a fallback
            attempted_path = plugin_dir / str(grammar_file_relative) # .resolve() might fail here
            err_msg = f"Grammar file '{grammar_file_relative}' not found at or near path '{attempted_path}' for plugin {manifest_data.get('id', 'N/A')}. Underlying FileNotFoundError."
            self.errors.append(err_msg)
            self.logger.warning(err_msg)
            return False, parsed_config, self.errors
        except Exception as e:
            err_msg = f"Error resolving or processing grammar file path for '{grammar_file_relative}' in plugin {manifest_data.get('id', 'N/A')}: {e}"
            self.errors.append(err_msg)
            self.logger.error(f"Error processing grammar file path for {manifest_data.get('id', 'N/A')}: {e}", exc_info=True)
            return False, parsed_config, self.errors

    # Future methods might include:
    # - validate_grammar_file_exists(self, plugin_root_path: str, grammar_file_relative_path: str) -> bool
    # - (Potentially) light_parse_grammar_file(self, ...) -> bool
