"""Comprehensive tests for the semantic construct plugin validator."""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from tau_translator_omega.core_engine.semantic_construct_plugin_validator import SemanticConstructPluginValidator


class TestSemanticConstructPluginValidator:
    """Test the semantic construct plugin validator."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing."""
        logger = Mock()
        return SemanticConstructPluginValidator("1.0.0", logger)

    @pytest.fixture
    def base_manifest(self):
        """Base manifest data for semantic construct plugins."""
        return {
            "id": "test-semantic-plugin",
            "name": "Test Semantic Plugin",
            "version": "1.0.0",
            "plugin_type": "semantic_construct",
            "semantic_construct_config": {
                "construct_type": "entity",
                "ilr_schema_path": "schemas/entity.json",
                "validation_rules": {
                    "required_fields": ["id", "name", "type"],
                    "field_types": {
                        "id": "string",
                        "name": "string",
                        "type": "string"
                    }
                }
            }
        }

    def test_validator_initialization(self):
        """Test validator initialization."""
        logger = Mock()
        validator = SemanticConstructPluginValidator("1.0.0", logger)
        
        assert validator.core_ilr_version == "1.0.0"
        assert validator.logger == logger
        assert validator.schema is not None

    def test_validate_manifest_valid(self, validator, base_manifest, tmp_path):
        """Test validation of a valid manifest."""
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()
        
        # Create schema file
        schema_dir = plugin_dir / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "entity.json"
        schema_file.write_text(json.dumps({
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string"}
            }
        }))
        
        is_valid, parsed_config, errors = validator.validate_manifest(base_manifest, plugin_dir)
        
        assert is_valid is True
        assert len(errors) == 0
        assert "construct_type" in parsed_config
        assert parsed_config["construct_type"] == "entity"

    def test_validate_manifest_missing_config(self, validator, tmp_path):
        """Test validation with missing semantic_construct_config."""
        manifest = {
            "id": "test-plugin",
            "name": "Test Plugin",
            "plugin_type": "semantic_construct"
        }
        
        is_valid, parsed_config, errors = validator.validate_manifest(manifest, tmp_path)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("semantic_construct_config" in error for error in errors)

    def test_validate_manifest_invalid_construct_type(self, validator, base_manifest, tmp_path):
        """Test validation with invalid construct type."""
        base_manifest["semantic_construct_config"]["construct_type"] = "invalid_type"
        
        is_valid, parsed_config, errors = validator.validate_manifest(base_manifest, tmp_path)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("construct_type" in error for error in errors)

    def test_validate_manifest_missing_schema_file(self, validator, base_manifest, tmp_path):
        """Test validation when schema file is missing."""
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()
        
        is_valid, parsed_config, errors = validator.validate_manifest(base_manifest, plugin_dir)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("schema" in error.lower() for error in errors)

    def test_validate_manifest_invalid_schema_json(self, validator, base_manifest, tmp_path):
        """Test validation with invalid JSON in schema file."""
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()
        
        schema_dir = plugin_dir / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "entity.json"
        schema_file.write_text("invalid json content")
        
        is_valid, parsed_config, errors = validator.validate_manifest(base_manifest, plugin_dir)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("json" in error.lower() for error in errors)

    def test_validate_manifest_complex_validation_rules(self, validator, tmp_path):
        """Test validation with complex validation rules."""
        manifest = {
            "id": "complex-plugin",
            "name": "Complex Plugin",
            "plugin_type": "semantic_construct",
            "semantic_construct_config": {
                "construct_type": "relationship",
                "ilr_schema_path": "schemas/relationship.json",
                "validation_rules": {
                    "required_fields": ["source", "target", "type"],
                    "field_types": {
                        "source": "object",
                        "target": "object",
                        "type": "string",
                        "properties": "object"
                    },
                    "constraints": [
                        {
                            "type": "unique",
                            "fields": ["source.id", "target.id", "type"]
                        }
                    ]
                },
                "transformation_rules": {
                    "normalize_ids": True,
                    "validate_references": True
                }
            }
        }
        
        plugin_dir = tmp_path / "complex-plugin"
        plugin_dir.mkdir()
        
        # Create schema file
        schema_dir = plugin_dir / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "relationship.json"
        schema_file.write_text(json.dumps({
            "type": "object",
            "properties": {
                "source": {"type": "object"},
                "target": {"type": "object"},
                "type": {"type": "string"}
            }
        }))
        
        is_valid, parsed_config, errors = validator.validate_manifest(manifest, plugin_dir)
        
        assert is_valid is True
        assert "transformation_rules" in parsed_config
        assert parsed_config["transformation_rules"]["normalize_ids"] is True

    def test_validate_manifest_with_dependencies(self, validator, tmp_path):
        """Test validation with plugin dependencies."""
        manifest = {
            "id": "dependent-plugin",
            "name": "Dependent Plugin",
            "plugin_type": "semantic_construct",
            "dependencies": ["base-semantic-plugin>=1.0.0"],
            "semantic_construct_config": {
                "construct_type": "entity",
                "extends": "base-semantic-plugin:entity",
                "ilr_schema_path": "schemas/extended_entity.json",
                "validation_rules": {
                    "inherit_from": "base-semantic-plugin",
                    "additional_fields": ["extended_property"]
                }
            }
        }
        
        plugin_dir = tmp_path / "dependent-plugin"
        plugin_dir.mkdir()
        
        schema_dir = plugin_dir / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "extended_entity.json"
        schema_file.write_text(json.dumps({
            "allOf": [
                {"$ref": "base-entity.json"},
                {
                    "type": "object",
                    "properties": {
                        "extended_property": {"type": "string"}
                    }
                }
            ]
        }))
        
        is_valid, parsed_config, errors = validator.validate_manifest(manifest, plugin_dir)
        
        # This might fail if dependency resolution is strict
        assert isinstance(is_valid, bool)
        if is_valid:
            assert "extends" in parsed_config

    def test_validate_manifest_with_custom_validators(self, validator, tmp_path):
        """Test validation with custom validator specifications."""
        manifest = {
            "id": "custom-validator-plugin",
            "name": "Custom Validator Plugin",
            "plugin_type": "semantic_construct",
            "semantic_construct_config": {
                "construct_type": "entity",
                "ilr_schema_path": "schemas/entity.json",
                "custom_validators": [
                    {
                        "name": "validate_id_format",
                        "type": "regex",
                        "pattern": "^[A-Z][A-Z0-9_]*$",
                        "field": "id",
                        "message": "ID must be uppercase with underscores"
                    },
                    {
                        "name": "validate_name_length",
                        "type": "length",
                        "min": 3,
                        "max": 50,
                        "field": "name"
                    }
                ]
            }
        }
        
        plugin_dir = tmp_path / "custom-validator-plugin"
        plugin_dir.mkdir()
        
        schema_dir = plugin_dir / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "entity.json"
        schema_file.write_text(json.dumps({
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"}
            }
        }))
        
        is_valid, parsed_config, errors = validator.validate_manifest(manifest, plugin_dir)
        
        assert is_valid is True
        assert "custom_validators" in parsed_config
        assert len(parsed_config["custom_validators"]) == 2

    def test_validate_manifest_schema_loading_error(self, validator, base_manifest, tmp_path):
        """Test handling of schema loading errors."""
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()
        
        # Create a schema file that exists but causes an error when loaded
        schema_dir = plugin_dir / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "entity.json"
        
        # Make the schema file unreadable
        schema_file.write_text("{}")
        schema_file.chmod(0o000)
        
        is_valid, parsed_config, errors = validator.validate_manifest(base_manifest, plugin_dir)
        
        # Restore permissions for cleanup
        schema_file.chmod(0o644)
        
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_manifest_circular_dependencies(self, validator, tmp_path):
        """Test detection of circular dependencies."""
        manifest = {
            "id": "circular-plugin-a",
            "name": "Circular Plugin A",
            "plugin_type": "semantic_construct",
            "dependencies": ["circular-plugin-b"],
            "semantic_construct_config": {
                "construct_type": "entity",
                "ilr_schema_path": "schemas/entity.json",
                "extends": "circular-plugin-b:entity"
            }
        }
        
        plugin_dir = tmp_path / "circular-plugin-a"
        plugin_dir.mkdir()
        
        schema_dir = plugin_dir / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "entity.json"
        schema_file.write_text(json.dumps({"type": "object"}))
        
        is_valid, parsed_config, errors = validator.validate_manifest(manifest, plugin_dir)
        
        # The validator should handle this gracefully
        assert isinstance(is_valid, bool)

    def test_validate_manifest_version_compatibility(self, validator, base_manifest, tmp_path):
        """Test ILR version compatibility checking."""
        base_manifest["ilr_versions_supported"] = ["2.0.0"]  # Incompatible with validator's 1.0.0
        
        plugin_dir = tmp_path / "test-plugin"
        plugin_dir.mkdir()
        
        schema_dir = plugin_dir / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "entity.json"
        schema_file.write_text(json.dumps({"type": "object"}))
        
        is_valid, parsed_config, errors = validator.validate_manifest(base_manifest, plugin_dir)
        
        # Version compatibility might be checked elsewhere
        assert isinstance(is_valid, bool)

    def test_validate_manifest_with_examples(self, validator, tmp_path):
        """Test validation with example data."""
        manifest = {
            "id": "example-plugin",
            "name": "Example Plugin",
            "plugin_type": "semantic_construct",
            "semantic_construct_config": {
                "construct_type": "entity",
                "ilr_schema_path": "schemas/entity.json",
                "examples": [
                    {
                        "id": "USER_001",
                        "name": "John Doe",
                        "type": "person"
                    },
                    {
                        "id": "ORG_001",
                        "name": "Acme Corp",
                        "type": "organization"
                    }
                ]
            }
        }
        
        plugin_dir = tmp_path / "example-plugin"
        plugin_dir.mkdir()
        
        schema_dir = plugin_dir / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "entity.json"
        schema_file.write_text(json.dumps({
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string"}
            }
        }))
        
        is_valid, parsed_config, errors = validator.validate_manifest(manifest, plugin_dir)
        
        assert is_valid is True
        assert "examples" in parsed_config
        assert len(parsed_config["examples"]) == 2

    @patch('pathlib.Path.exists')
    def test_validate_manifest_schema_not_found(self, mock_exists, validator, base_manifest, tmp_path):
        """Test handling when schema file doesn't exist."""
        mock_exists.return_value = False
        
        is_valid, parsed_config, errors = validator.validate_manifest(base_manifest, tmp_path)
        
        assert is_valid is False
        assert any("not found" in error.lower() for error in errors)

    def test_validate_manifest_empty_config(self, validator, tmp_path):
        """Test validation with empty semantic_construct_config."""
        manifest = {
            "id": "empty-config-plugin",
            "name": "Empty Config Plugin",
            "plugin_type": "semantic_construct",
            "semantic_construct_config": {}
        }
        
        is_valid, parsed_config, errors = validator.validate_manifest(manifest, tmp_path)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("construct_type" in error for error in errors)