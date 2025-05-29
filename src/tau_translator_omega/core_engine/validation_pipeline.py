"""
Validation pipeline for plugin manifest processing.

This module implements a pipeline pattern for validating plugin manifests,
breaking down complex validation logic into focused, testable stages.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging

from .logging_config import get_component_logger


logger = get_component_logger('validation_pipeline')


@dataclass
class ValidationContext:
    """Context object passed through validation pipeline stages."""
    manifest_data: Dict[str, Any]
    plugin_dir: Path
    config: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    plugin_id: Optional[str] = None
    
    def __post_init__(self):
        """Extract plugin ID for easier access."""
        self.plugin_id = self.manifest_data.get('id', 'unknown')
    
    def add_error(self, error: str) -> None:
        """Add an error to the context."""
        self.errors.append(error)
        logger.warning(f"Validation error for plugin {self.plugin_id}: {error}")
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update the configuration with new values."""
        self.config.update(updates)
        logger.debug(f"Updated config for plugin {self.plugin_id}: {list(updates.keys())}")


@dataclass
class StageResult:
    """Result of a validation stage."""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    @classmethod
    def success_with_data(cls, data: Dict[str, Any]) -> 'StageResult':
        """Create a successful result with data."""
        return cls(success=True, data=data)
    
    @classmethod
    def failure_with_errors(cls, errors: List[str]) -> 'StageResult':
        """Create a failed result with errors."""
        return cls(success=False, errors=errors)


class ValidationStage(ABC):
    """Abstract base class for validation pipeline stages."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_component_logger(f'validation_stage.{name}')
    
    @abstractmethod
    def validate(self, context: ValidationContext) -> StageResult:
        """Validate the context and return a result."""
        pass
    
    def __str__(self) -> str:
        return f"ValidationStage({self.name})"


class SchemaValidationStage(ValidationStage):
    """Validates manifest against JSON schema."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        super().__init__('schema_validation')
        self.schema = schema
    
    def validate(self, context: ValidationContext) -> StageResult:
        """Validate manifest against JSON schema."""
        if not self.schema:
            self.logger.warning(f"No schema available for plugin {context.plugin_id}")
            return StageResult.failure_with_errors(["Schema not available for validation"])
        
        try:
            from jsonschema import validate, ValidationError
            validate(instance=context.manifest_data, schema=self.schema)
            self.logger.debug(f"Schema validation passed for plugin {context.plugin_id}")
            return StageResult.success_with_data({})
        except ValidationError as e:
            error_msg = f"Schema validation failed: {e.message} (path: {list(e.path)})"
            self.logger.warning(f"Schema validation failed for plugin {context.plugin_id}: {error_msg}")
            return StageResult.failure_with_errors([error_msg])
        except Exception as e:
            error_msg = f"Unexpected error during schema validation: {e}"
            self.logger.error(f"Unexpected schema validation error for plugin {context.plugin_id}: {e}", exc_info=True)
            return StageResult.failure_with_errors([error_msg])


class FileExistenceStage(ValidationStage):
    """Validates that required files exist."""
    
    def __init__(self, file_fields: List[str]):
        super().__init__('file_existence')
        self.file_fields = file_fields
    
    def validate(self, context: ValidationContext) -> StageResult:
        """Validate that required files exist."""
        config_updates = {}
        
        for field_path in self.file_fields:
            file_path = self._extract_file_path(context.manifest_data, field_path)
            if not file_path:
                continue
                
            full_path = context.plugin_dir / file_path
            if not full_path.exists():
                error_msg = f"Required file '{file_path}' does not exist at {full_path}"
                return StageResult.failure_with_errors([error_msg])
            
            if not full_path.is_file():
                error_msg = f"Path '{file_path}' exists but is not a file: {full_path}"
                return StageResult.failure_with_errors([error_msg])
            
            # Store resolved path
            resolved_key = f"resolved_{field_path.replace('.', '_')}_path"
            config_updates[resolved_key] = str(full_path.resolve())
            self.logger.debug(f"Validated file existence: {full_path}")
        
        return StageResult.success_with_data(config_updates)
    
    def _extract_file_path(self, manifest_data: Dict[str, Any], field_path: str) -> Optional[str]:
        """Extract file path from nested manifest data."""
        keys = field_path.split('.')
        current = manifest_data
        
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        
        return str(current) if current else None


class ValidationPipeline:
    """Pipeline for running validation stages in sequence."""
    
    def __init__(self, stages: List[ValidationStage]):
        self.stages = stages
        self.logger = get_component_logger('validation_pipeline')
    
    def validate(self, manifest_data: Dict[str, Any], plugin_dir: Path) -> ValidationContext:
        """Run all validation stages and return the final context."""
        context = ValidationContext(manifest_data, plugin_dir)
        
        self.logger.debug(f"Starting validation pipeline for plugin {context.plugin_id} with {len(self.stages)} stages")
        
        for stage in self.stages:
            self.logger.debug(f"Running stage: {stage.name}")
            result = stage.validate(context)
            
            if not result.success:
                context.errors.extend(result.errors)
                self.logger.warning(f"Stage {stage.name} failed for plugin {context.plugin_id}")
                break
            
            # Update context with stage results
            context.update_config(result.data)
            self.logger.debug(f"Stage {stage.name} completed successfully for plugin {context.plugin_id}")
        
        success = len(context.errors) == 0
        self.logger.info(f"Validation pipeline {'succeeded' if success else 'failed'} for plugin {context.plugin_id}")
        
        return context
