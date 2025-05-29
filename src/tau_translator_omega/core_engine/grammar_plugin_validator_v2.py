"""
Refactored Grammar Plugin Validator using validation pipeline pattern.

This is a demonstration of how the validation pipeline can reduce complexity
and improve maintainability of the validation logic.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import logging

from .plugin import BasePluginValidator
from .validation_pipeline import (
    ValidationPipeline, 
    SchemaValidationStage, 
    FileExistenceStage,
    ValidationStage,
    ValidationContext,
    StageResult
)
from .logging_config import get_component_logger


class GrammarDetailsStage(ValidationStage):
    """Validates and extracts grammar-specific details."""
    
    def __init__(self):
        super().__init__('grammar_details')
    
    def validate(self, context: ValidationContext) -> StageResult:
        """Validate grammar details and extract configuration."""
        grammar_details = context.manifest_data.get("grammar_details", {})
        config_updates = {}
        
        # Extract formalism (required by schema)
        formalism = grammar_details.get("formalism")
        if formalism:
            config_updates["formalism"] = formalism
        
        # Extract optional entry rule
        entry_rule = grammar_details.get("entry_rule")
        if entry_rule:
            config_updates["entry_rule"] = entry_rule
        
        # Handle ANTLR-specific configuration
        if formalism == "antlr4":
            antlr_version = grammar_details.get("antlr_version")
            if antlr_version:
                config_updates["antlr_version"] = antlr_version
        
        self.logger.debug(f"Extracted grammar details for plugin {context.plugin_id}: {list(config_updates.keys())}")
        return StageResult.success_with_data(config_updates)


class ILRMappingsStage(ValidationStage):
    """Validates ILR construct mappings schema if present."""
    
    def __init__(self):
        super().__init__('ilr_mappings')
    
    def validate(self, context: ValidationContext) -> StageResult:
        """Validate ILR mappings schema file if specified."""
        grammar_details = context.manifest_data.get("grammar_details", {})
        mappings_schema_relative = grammar_details.get("ilr_construct_mappings_schema")
        
        if not mappings_schema_relative:
            # Optional field, no error
            return StageResult.success_with_data({})
        
        mappings_schema_path = context.plugin_dir / str(mappings_schema_relative)
        
        if not mappings_schema_path.exists():
            error_msg = f"ILR construct mappings schema file '{mappings_schema_relative}' does not exist at {mappings_schema_path}"
            return StageResult.failure_with_errors([error_msg])
        
        if not mappings_schema_path.is_file():
            error_msg = f"ILR construct mappings schema path '{mappings_schema_relative}' is not a file: {mappings_schema_path}"
            return StageResult.failure_with_errors([error_msg])
        
        resolved_path = str(mappings_schema_path.resolve())
        config_updates = {"resolved_ilr_construct_mappings_schema_path": resolved_path}
        
        self.logger.debug(f"Validated ILR mappings schema for plugin {context.plugin_id}: {resolved_path}")
        return StageResult.success_with_data(config_updates)


class GrammarPluginValidatorV2(BasePluginValidator):
    """
    Refactored Grammar Plugin Validator using validation pipeline pattern.
    
    This demonstrates how complex validation logic can be broken down into
    focused, testable stages with clear separation of concerns.
    """
    
    def __init__(self, core_ilr_version: str, logger: logging.Logger):
        super().__init__(core_ilr_version, logger)
        self.schema: Optional[Dict[str, Any]] = None
        self.pipeline: Optional[ValidationPipeline] = None
        self._load_schema()
        self._setup_pipeline()
    
    def _load_schema(self) -> None:
        """Load the grammar plugin manifest schema."""
        try:
            # Use the same schema loading logic as the original validator
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            schema_file_path = project_root / "docs" / "schemas" / "grammar_plugin_manifest_schema.json"
            
            if schema_file_path.exists():
                with open(schema_file_path, 'r') as schema_f:
                    self.schema = json.load(schema_f)
                self.logger.info(f"Loaded grammar plugin schema from {schema_file_path}")
            else:
                self.logger.warning(f"Grammar plugin schema not found at {schema_file_path}")
        except Exception as e:
            self.logger.error(f"Error loading grammar plugin schema: {e}", exc_info=True)
    
    def _setup_pipeline(self) -> None:
        """Setup the validation pipeline with appropriate stages."""
        stages = [
            SchemaValidationStage(self.schema),
            FileExistenceStage(['grammar_details.grammar_file']),
            GrammarDetailsStage(),
            ILRMappingsStage()
        ]
        
        self.pipeline = ValidationPipeline(stages)
        self.logger.debug(f"Setup validation pipeline with {len(stages)} stages")
    
    def validate_manifest(self, manifest_data: Dict[str, Any], plugin_dir: Path) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validate a grammar plugin manifest using the validation pipeline.
        
        Returns:
            Tuple of (is_valid, parsed_config, errors_list)
        """
        if not self.pipeline:
            error_msg = "Validation pipeline not initialized"
            self.logger.error(error_msg)
            return False, {}, [error_msg]
        
        plugin_id = manifest_data.get('id', 'unknown')
        self.logger.debug(f"Starting validation for grammar plugin {plugin_id}")
        
        # Run validation pipeline
        context = self.pipeline.validate(manifest_data, plugin_dir)
        
        # Return results
        is_valid = len(context.errors) == 0
        
        if is_valid:
            self.logger.info(f"Grammar plugin validation successful for {plugin_id}")
        else:
            self.logger.warning(f"Grammar plugin validation failed for {plugin_id}: {context.errors}")
        
        return is_valid, context.config, context.errors


# Factory function for backward compatibility
def create_grammar_validator(core_ilr_version: str, logger: logging.Logger) -> GrammarPluginValidatorV2:
    """Create a new grammar plugin validator instance."""
    return GrammarPluginValidatorV2(core_ilr_version, logger)
