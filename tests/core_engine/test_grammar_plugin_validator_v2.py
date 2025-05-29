"""
Tests for the refactored Grammar Plugin Validator V2.

This demonstrates that the refactored validator maintains the same functionality
while having better structure and lower complexity.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock

from src.tau_translator_omega.core_engine.grammar_plugin_validator_v2 import GrammarPluginValidatorV2


class TestGrammarPluginValidatorV2:
    """Test the refactored grammar plugin validator."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        return Mock()
    
    @pytest.fixture
    def validator(self, mock_logger):
        """Create a validator instance for testing."""
        return GrammarPluginValidatorV2("1.0.0", mock_logger)
    
    @pytest.fixture
    def temp_plugin_dir(self):
        """Create a temporary directory for plugin testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = Path(temp_dir)
            
            # Create a sample grammar file
            grammar_file = plugin_dir / "test_grammar.lark"
            grammar_file.write_text("start: expression\nexpression: NUMBER")
            
            yield plugin_dir
    
    @pytest.fixture
    def valid_manifest_data(self):
        """Create valid manifest data for testing."""
        return {
            "id": "test-grammar-plugin",
            "name": "Test Grammar Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "lark",
                "grammar_file": "test_grammar.lark",
                "entry_rule": "start"
            }
        }
    
    def test_validator_initialization(self, validator):
        """Test that the validator initializes correctly."""
        assert validator is not None
        assert validator.pipeline is not None
        assert len(validator.pipeline.stages) == 4  # Schema, File, Grammar, ILR stages
    
    def test_validate_manifest_valid(self, validator, valid_manifest_data, temp_plugin_dir):
        """Test validation of a valid manifest."""
        is_valid, config, errors = validator.validate_manifest(valid_manifest_data, temp_plugin_dir)
        
        # Should be valid
        assert is_valid is True
        assert len(errors) == 0
        
        # Should have extracted configuration
        assert "formalism" in config
        assert config["formalism"] == "lark"
        assert "entry_rule" in config
        assert config["entry_rule"] == "start"
        assert "resolved_grammar_details_grammar_file_path" in config
    
    def test_validate_manifest_missing_grammar_file(self, validator, valid_manifest_data, temp_plugin_dir):
        """Test validation when grammar file is missing."""
        # Remove the grammar file
        (temp_plugin_dir / "test_grammar.lark").unlink()
        
        is_valid, config, errors = validator.validate_manifest(valid_manifest_data, temp_plugin_dir)
        
        # Should fail validation
        assert is_valid is False
        assert len(errors) > 0
        assert any("does not exist" in error for error in errors)
    
    def test_validate_manifest_with_ilr_mappings(self, validator, valid_manifest_data, temp_plugin_dir):
        """Test validation with ILR construct mappings schema."""
        # Add ILR mappings schema file
        mappings_file = temp_plugin_dir / "ilr_mappings.json"
        mappings_file.write_text('{"type": "object"}')
        
        # Update manifest to include mappings
        valid_manifest_data["grammar_details"]["ilr_construct_mappings_schema"] = "ilr_mappings.json"
        
        is_valid, config, errors = validator.validate_manifest(valid_manifest_data, temp_plugin_dir)
        
        # Should be valid
        assert is_valid is True
        assert len(errors) == 0
        
        # Should have mappings path in config
        assert "resolved_ilr_construct_mappings_schema_path" in config
    
    def test_validate_manifest_missing_ilr_mappings(self, validator, valid_manifest_data, temp_plugin_dir):
        """Test validation when ILR mappings file is specified but missing."""
        # Update manifest to include non-existent mappings
        valid_manifest_data["grammar_details"]["ilr_construct_mappings_schema"] = "missing_mappings.json"
        
        is_valid, config, errors = validator.validate_manifest(valid_manifest_data, temp_plugin_dir)
        
        # Should fail validation
        assert is_valid is False
        assert len(errors) > 0
        assert any("mappings schema" in error for error in errors)
    
    def test_validate_manifest_antlr_formalism(self, validator, temp_plugin_dir):
        """Test validation with ANTLR formalism."""
        antlr_manifest = {
            "id": "test-antlr-plugin",
            "name": "Test ANTLR Plugin",
            "version": "1.0.0",
            "plugin_type": "grammar_definition",
            "ilr_versions_supported": ["1.0.0"],
            "grammar_details": {
                "formalism": "antlr4",
                "grammar_file": "test_grammar.lark",  # Using same file for simplicity
                "antlr_version": "4.9.2"
            }
        }
        
        is_valid, config, errors = validator.validate_manifest(antlr_manifest, temp_plugin_dir)
        
        # Should be valid
        assert is_valid is True
        assert len(errors) == 0
        
        # Should have ANTLR-specific configuration
        assert config["formalism"] == "antlr4"
        assert config["antlr_version"] == "4.9.2"


class TestValidationPipelineIntegration:
    """Test the validation pipeline integration."""
    
    def test_pipeline_stage_order(self):
        """Test that pipeline stages run in the correct order."""
        from src.tau_translator_omega.core_engine.validation_pipeline import ValidationPipeline
        from src.tau_translator_omega.core_engine.grammar_plugin_validator_v2 import (
            GrammarDetailsStage, 
            ILRMappingsStage
        )
        
        # Create a simple pipeline
        stages = [GrammarDetailsStage(), ILRMappingsStage()]
        pipeline = ValidationPipeline(stages)
        
        assert len(pipeline.stages) == 2
        assert pipeline.stages[0].name == "grammar_details"
        assert pipeline.stages[1].name == "ilr_mappings"
    
    def test_validation_context_error_handling(self):
        """Test that validation context properly handles errors."""
        from src.tau_translator_omega.core_engine.validation_pipeline import ValidationContext
        
        context = ValidationContext({"id": "test"}, Path("/tmp"))
        
        # Initially no errors
        assert len(context.errors) == 0
        
        # Add error
        context.add_error("Test error")
        assert len(context.errors) == 1
        assert "Test error" in context.errors
        
        # Plugin ID should be extracted
        assert context.plugin_id == "test"
