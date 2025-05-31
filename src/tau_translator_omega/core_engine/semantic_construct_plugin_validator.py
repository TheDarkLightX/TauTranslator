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
        """Validate semantic construct plugin manifest using modular validation approach."""
        errors: List[str] = []
        
        # Basic manifest validation
        errors.extend(self._validate_basic_fields(manifest_data))
        
        # Construct details validation
        construct_details = manifest_data.get("construct_details")
        if not isinstance(construct_details, dict):
            errors.append("Manifest missing 'construct_details' or it's not a dictionary.")
            return False, {}, errors
        
        errors.extend(self._validate_construct_details(construct_details, plugin_dir))
        
        if errors:
            return False, {}, errors
        
        # Build parsed info if validation passed
        parsed_info = self._build_parsed_info(construct_details, plugin_dir)
        return True, parsed_info, []
    
    def _validate_basic_fields(self, manifest_data: Dict[str, Any]) -> List[str]:
        """Validate basic manifest fields."""
        errors = []
        
        if not manifest_data.get("id"):
            errors.append("Manifest missing 'id'")
        
        expected_plugin_type = "semantic_construct"
        if manifest_data.get("plugin_type") != expected_plugin_type:
            errors.append(f"Invalid plugin_type: {manifest_data.get('plugin_type')}. Expected '{expected_plugin_type}'.")
        
        return errors
    
    def _validate_construct_details(self, construct_details: Dict[str, Any], plugin_dir: Path) -> List[str]:
        """Validate construct_details section."""
        errors = []
        
        errors.extend(self._validate_ilr_version(construct_details))
        errors.extend(self._validate_schema_path(construct_details, plugin_dir))
        errors.extend(self._validate_definition_provider(construct_details, plugin_dir))
        
        return errors
    
    def _validate_ilr_version(self, construct_details: Dict[str, Any]) -> List[str]:
        """Validate ILR version and constraints."""
        errors = []
        
        ilr_version_val = construct_details.get("ilr_version")
        if ilr_version_val is None:
            errors.append("Missing 'ilr_version' in 'construct_details'.")
        elif ilr_version_val not in self.SUPPORTED_ILR_VERSIONS:
            errors.append(f"Unsupported 'ilr_version': {ilr_version_val}. Supported versions: {self.SUPPORTED_ILR_VERSIONS}.")
        
        ilr_constraint_str = construct_details.get("ilr_version_constraint")
        if ilr_constraint_str is not None:
            errors.extend(self._validate_version_constraint(ilr_constraint_str))
        
        return errors
    
    def _validate_version_constraint(self, constraint_str: str) -> List[str]:
        """Validate version constraint specification."""
        errors = []
        
        try:
            core_v = parse_version(self.core_ilr_version)
            specifiers = SpecifierSet(constraint_str)
            if not specifiers.contains(core_v):
                errors.append(f"Core ILR version '{self.core_ilr_version}' does not meet constraint '{constraint_str}'.")
        except InvalidSpecifier:
            errors.append(f"Invalid specifier string: '{constraint_str}'.")
        except InvalidVersion:
            self.logger.error(f"Invalid core ILR version format: '{self.core_ilr_version}'.")
            errors.append(f"Internal Error: Invalid core ILR version format: '{self.core_ilr_version}'.")
        
        return errors

    def _validate_schema_path(self, construct_details: Dict[str, Any], plugin_dir: Path) -> List[str]:
        """Validate construct schema path."""
        errors = []
        
        schema_path_val = construct_details.get("construct_schema_path")
        if schema_path_val is None:
            errors.append("Missing 'construct_schema_path' in 'construct_details'.")
            return errors
        
        abs_schema_path = plugin_dir / schema_path_val
        self.logger.info(f"Validating schema path: {abs_schema_path}")
        
        try:
            if not abs_schema_path.exists():
                errors.append(f"Schema path does not exist: {schema_path_val}")
            elif not abs_schema_path.is_file():
                errors.append(f"Schema path is not a file: {schema_path_val}")
        except Exception as e:
            self.logger.error(f"Error validating schema path: {e}")
            errors.append(f"Error checking schema path: {e}")
        
        return errors

    def _validate_definition_provider(self, construct_details: Dict[str, Any], plugin_dir: Path) -> List[str]:
        """Validate definition provider details."""
        errors = []
        
        dp_details = construct_details.get("definition_provider_details")
        if not isinstance(dp_details, dict):
            errors.append("Missing or invalid 'definition_provider_details'.")
            return errors
        
        errors.extend(self._validate_dp_format(dp_details))
        errors.extend(self._validate_dp_root_directory(dp_details, plugin_dir))
        errors.extend(self._validate_dp_file_mappings(dp_details))
        
        return errors
    
    def _validate_dp_format(self, dp_details: Dict[str, Any]) -> List[str]:
        """Validate definition provider format."""
        errors = []
        
        dpd_format = dp_details.get("format")
        if dpd_format is None:
            errors.append("Missing 'format' in 'definition_provider_details'.")
        elif dpd_format not in self.SUPPORTED_DPD_FORMATS:
            errors.append(f"Unsupported format: {dpd_format}. Supported: {self.SUPPORTED_DPD_FORMATS}.")
        
        return errors
    
    def _validate_dp_root_directory(self, dp_details: Dict[str, Any], plugin_dir: Path) -> List[str]:
        """Validate definition provider root directory."""
        errors = []
        
        root_dir_val = dp_details.get("root_directory")
        if root_dir_val is None:
            errors.append("Missing 'root_directory' in 'definition_provider_details'.")
            return errors
        
        abs_root_dir_path = plugin_dir / root_dir_val
        self.logger.info(f"Validating root directory: {abs_root_dir_path}")
        
        try:
            if not abs_root_dir_path.exists():
                errors.append(f"Root directory does not exist: {root_dir_val}")
            elif not abs_root_dir_path.is_dir():
                errors.append(f"Root directory is not a directory: {root_dir_val}")
        except Exception as e:
            self.logger.error(f"Error validating root directory: {e}")
            errors.append(f"Error checking root directory: {e}")
        
        return errors
    
    def _validate_dp_file_mappings(self, dp_details: Dict[str, Any]) -> List[str]:
        """Validate definition provider file mappings."""
        errors = []
        
        file_mappings = dp_details.get("file_mappings")
        if file_mappings is None:
            errors.append("Missing 'file_mappings'.")
        elif not isinstance(file_mappings, list):
            errors.append("'file_mappings' must be a list.")
        else:
            errors.extend(self._validate_file_mapping_items(file_mappings))
        
        return errors
    
    def _validate_file_mapping_items(self, file_mappings: List[Any]) -> List[str]:
        """Validate individual file mapping items."""
        errors = []
        
        for i, item in enumerate(file_mappings):
            if not isinstance(item, dict):
                errors.append(f"File mapping item {i} is not a dictionary.")
                continue
            
            if not item.get("definition_type"):
                errors.append(f"File mapping item {i} missing 'definition_type'.")
            elif not isinstance(item.get("definition_type"), str):
                errors.append(f"File mapping item {i} 'definition_type' must be a string.")
            
            if not item.get("path_glob"):
                errors.append(f"File mapping item {i} missing 'path_glob'.")
            elif not isinstance(item.get("path_glob"), str):
                errors.append(f"File mapping item {i} 'path_glob' must be a string.")
        
        return errors

    def _build_parsed_info(self, construct_details: Dict[str, Any], plugin_dir: Path) -> Dict[str, Any]:
        """Build parsed info from validated construct details."""
        dp_details = construct_details["definition_provider_details"]
        
        abs_construct_schema_path = str(plugin_dir / construct_details["construct_schema_path"])
        abs_dp_root_directory = str(plugin_dir / dp_details["root_directory"])
        
        return {
            "ilr_version": construct_details["ilr_version"],
            "construct_schema_path": abs_construct_schema_path,
            "definition_provider": {
                "format": dp_details["format"],
                "root_directory": abs_dp_root_directory,
                "file_mappings": dp_details["file_mappings"]
            }
        }
