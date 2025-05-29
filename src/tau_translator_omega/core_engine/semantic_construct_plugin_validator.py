import json 
import os
from pathlib import Path
import logging
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import parse as parse_version, InvalidVersion
from typing import Dict, Any, List, Tuple 

from .plugin import BasePluginValidator 


class SemanticConstructPluginValidator(BasePluginValidator):
    SUPPORTED_ILR_VERSIONS = ["1.0.0"] 
    SUPPORTED_DPD_FORMATS = ["yaml", "json"]

    def __init__(self, core_ilr_version: str, logger_instance: logging.Logger):
        super().__init__(core_ilr_version, logger_instance)
        # self.logger is now set by BasePluginValidator
        # Any specific initialization for this validator can go here
        # For example, loading a specific schema if this validator used one like GrammarPluginValidator
        # self.construct_schema = self._load_construct_schema() # Example

    def validate_manifest(self, manifest_data: Dict[str, Any], plugin_dir: Path) -> Tuple[bool, Dict[str, Any], List[str]]:
        # core_ilr_version is now available as self.core_ilr_version
        # logger is now available as self.logger

        errors: List[str] = []
        # plugin_root_path (str) is now plugin_dir (Path)
        # plugin_root = Path(plugin_root_path) # No longer needed, plugin_dir is already a Path

        if not manifest_data.get("id"):
            errors.append("Manifest missing 'id'")
        
        # Updated plugin_type check
        expected_plugin_type = "semantic_construct"
        if manifest_data.get("plugin_type") != expected_plugin_type:
            errors.append(f"Invalid plugin_type: {manifest_data.get('plugin_type')}. Expected '{expected_plugin_type}'.")
        
        # Renamed from grammar_details to construct_details for clarity, assuming this validator handles general constructs
        construct_details = manifest_data.get("construct_details") 
        if not isinstance(construct_details, dict):
            errors.append("Manifest missing 'construct_details' or it's not a dictionary.")
        else:
            # Check fields within construct_details
            ilr_version_val = construct_details.get("ilr_version")
            if ilr_version_val is None:
                errors.append("Missing 'ilr_version' in 'construct_details'.")
            elif ilr_version_val not in self.SUPPORTED_ILR_VERSIONS: # This validator can have its own supported ILR versions
                errors.append(f"Unsupported 'ilr_version': {ilr_version_val}. Supported versions for this validator: {self.SUPPORTED_ILR_VERSIONS}.")

            ilr_constraint_str = construct_details.get("ilr_version_constraint")
            if ilr_constraint_str is not None:
                try:
                    core_v = parse_version(self.core_ilr_version) # Use self.core_ilr_version
                    specifiers = SpecifierSet(ilr_constraint_str)
                    if not specifiers.contains(core_v):
                        errors.append(f"Core ILR version '{self.core_ilr_version}' does not meet plugin's construct_details.ilr_version_constraint '{ilr_constraint_str}'.")
                except InvalidSpecifier:
                    errors.append(f"Invalid specifier string in construct_details.ilr_version_constraint: '{ilr_constraint_str}'.")
                except InvalidVersion:
                    # This error implies self.core_ilr_version was bad, which should be caught by BasePluginValidator or PluginManager init
                    self.logger.error(f"Invalid core ILR version format for comparison: '{self.core_ilr_version}'. This should have been caught earlier.")
                    errors.append(f"Internal Error: Invalid core ILR version format for comparison: '{self.core_ilr_version}'.")

            # Renamed from grammar_construct_schema_path to construct_schema_path
            schema_path_val = construct_details.get("construct_schema_path")
            if schema_path_val is None:
                errors.append("Missing 'construct_schema_path' in 'construct_details'.")
            else:
                self.logger.debug(f"SemanticConstructPluginValidator: Validating schema_path. plugin_dir: '{plugin_dir.resolve()}'")
                self.logger.debug(f"SemanticConstructPluginValidator: schema_path_val (from manifest): '{schema_path_val}'")
                self.logger.debug(f"SemanticConstructPluginValidator: Current CWD: '{os.getcwd()}'")
                
                abs_schema_path = plugin_dir / schema_path_val # Use plugin_dir
                self.logger.debug(f"SemanticConstructPluginValidator: Constructed abs_schema_path: '{abs_schema_path}' (is_absolute: {abs_schema_path.is_absolute()})")
                
                try:
                    if not abs_schema_path.exists():
                        errors.append(f"Path specified in 'construct_schema_path' does not exist: {schema_path_val} (abs: {abs_schema_path}) (plugin_dir: {plugin_dir})")
                    elif not abs_schema_path.is_file():
                        errors.append(f"Path specified in 'construct_schema_path' is not a file: {schema_path_val} (abs: {abs_schema_path}) (plugin_dir: {plugin_dir})")
                except Exception as e_schema_check: # General exception for path checks
                    self.logger.error(f"SemanticConstructPluginValidator: Error during schema_path check! Exception: {e_schema_check}, abs_schema_path: '{abs_schema_path}', CWD: '{os.getcwd()}'")
                    errors.append(f"Error checking path for 'construct_schema_path': {e_schema_check}")

            definition_provider_details = construct_details.get("definition_provider_details")
            if not isinstance(definition_provider_details, dict):
                errors.append("Manifest missing 'definition_provider_details' in 'construct_details' or it's not a dictionary.")
            else:
                dpd_format = definition_provider_details.get("format")
                if dpd_format is None:
                    errors.append("Missing 'format' in 'definition_provider_details'.")
                elif dpd_format not in self.SUPPORTED_DPD_FORMATS:
                    errors.append(f"Unsupported 'format': {dpd_format}. Supported formats: {self.SUPPORTED_DPD_FORMATS}.")

                root_dir_val = definition_provider_details.get("root_directory")
                if root_dir_val is None:
                    errors.append("Missing 'root_directory' in 'definition_provider_details'.")
                else:
                    self.logger.debug(f"SemanticConstructPluginValidator: Validating root_directory. plugin_dir: '{plugin_dir.resolve()}'")
                    self.logger.debug(f"SemanticConstructPluginValidator: root_dir_val (from manifest): '{root_dir_val}'")
                    self.logger.debug(f"SemanticConstructPluginValidator: Current CWD: '{os.getcwd()}'")
                    
                    abs_root_dir_path = plugin_dir / root_dir_val # Use plugin_dir
                    self.logger.debug(f"SemanticConstructPluginValidator: Constructed abs_root_dir_path: '{abs_root_dir_path}' (is_absolute: {abs_root_dir_path.is_absolute()})")
                    
                    try:
                        if not abs_root_dir_path.exists():
                            errors.append(f"Path specified in 'definition_provider_details.root_directory' does not exist: {root_dir_val} (abs: {abs_root_dir_path}) (plugin_dir: {plugin_dir})")
                        elif not abs_root_dir_path.is_dir():
                            errors.append(f"Path specified in 'definition_provider_details.root_directory' is not a directory: {root_dir_val} (abs: {abs_root_dir_path}) (plugin_dir: {plugin_dir})")
                    except Exception as e_dir_check: # General exception for path checks
                        self.logger.error(f"SemanticConstructPluginValidator: Error during root_directory check! Exception: {e_dir_check}, abs_root_dir_path: '{abs_root_dir_path}', CWD: '{os.getcwd()}'")
                        errors.append(f"Error checking path for 'definition_provider_details.root_directory': {e_dir_check}")

                file_mappings_val = definition_provider_details.get("file_mappings")
                if file_mappings_val is None:
                    errors.append("Missing 'file_mappings' in 'definition_provider_details'.")
                elif not isinstance(file_mappings_val, list):
                    errors.append("'file_mappings' in 'definition_provider_details' must be a list.")
                else:
                    for i, item in enumerate(file_mappings_val):
                        if not isinstance(item, dict):
                            errors.append(f"Item at index {i} in 'file_mappings' is not a dictionary.")
                            continue
                        
                        def_type = item.get("definition_type")
                        if def_type is None:
                            errors.append(f"Item at index {i} in 'file_mappings' is missing 'definition_type'.")
                        elif not isinstance(def_type, str):
                            errors.append(f"'{'definition_type'}' in item at index {i} of 'file_mappings' must be a string.")
                        
                        path_glob = item.get("path_glob")
                        if path_glob is None:
                            errors.append(f"Item at index {i} in 'file_mappings' is missing 'path_glob'.")
                        elif not isinstance(path_glob, str):
                            errors.append(f"'{'path_glob'}' in item at index {i} of 'file_mappings' must be a string.")

        if errors:
            return False, {}, errors # Return empty dict for parsed_info on failure

        # Ensure construct_details exists before trying to access its members
        # This check is technically redundant if the earlier isinstance check passed and no errors were added for it
        # but it's a safe guard.
        if not isinstance(manifest_data.get("construct_details"), dict):
             # This state should not be reached if errors were properly appended above.
             self.logger.error("Critical internal error: 'construct_details' is not a dict despite passing initial checks.")
             return False, {}, ["Critical internal error: 'construct_details' structure invalid."]

        c_details = manifest_data["construct_details"] 
        dp_details = c_details["definition_provider_details"]

        # Use plugin_dir for resolving paths
        abs_construct_schema_path = str(plugin_dir / c_details["construct_schema_path"])
        abs_dp_root_directory = str(plugin_dir / dp_details["root_directory"])

        parsed_info = {
            "ilr_version": c_details["ilr_version"],
            "construct_schema_path": abs_construct_schema_path,
            "definition_provider": {
                "format": dp_details["format"],
                "root_directory": abs_dp_root_directory,
                "file_mappings": dp_details["file_mappings"]
            }
        }
        return True, parsed_info, []
