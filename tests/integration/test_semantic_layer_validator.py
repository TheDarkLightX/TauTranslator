# tests/test_semantic_layer_validator.py
import pytest
import json
from pathlib import Path
from tau_translator_omega.core_engine.semantic_layer_validator import SemanticLayerValidator
import yaml

# Define schema content for testing
CONCEPT_SCHEMA_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ConceptDefinitionV1",
    "description": "Schema for defining a concept in the semantic layer, version 1.",
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Unique name of the concept."},
        "description": {"type": "string", "description": "Detailed description of the concept."}
    },
    "required": ["name"]
}

RELATIONSHIP_SCHEMA_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "RelationshipDefinitionV1",
    "description": "Schema for defining a relationship in the semantic layer, version 1.",
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Unique name of the relationship."},
        "source_concept": {"type": "string", "description": "Name of the source concept."},
        "target_concept": {"type": "string", "description": "Name of the target concept."}
    },
    "required": ["name", "source_concept", "target_concept"]
}

@pytest.fixture
def project_root_with_schemas(tmp_path):
    """Creates a temporary project root with valid schema files."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    schemas_dir = project_dir / "docs" / "schemas"
    schemas_dir.mkdir(parents=True)

    with open(schemas_dir / "concept_definition_v1.json", "w") as f:
        json.dump(CONCEPT_SCHEMA_V1, f)
    with open(schemas_dir / "relationship_definition_v1.json", "w") as f:
        json.dump(RELATIONSHIP_SCHEMA_V1, f)
    return project_dir

@pytest.fixture
def project_root_missing_concept_schema(tmp_path):
    """Creates a temporary project root with relationship schema but missing concept schema."""
    project_dir = tmp_path / "project_missing"
    project_dir.mkdir()
    schemas_dir = project_dir / "docs" / "schemas"
    schemas_dir.mkdir(parents=True)

    # Only relationship schema is created
    with open(schemas_dir / "relationship_definition_v1.json", "w") as f:
        json.dump(RELATIONSHIP_SCHEMA_V1, f)
    return project_dir

@pytest.fixture
def project_root_invalid_concept_schema(tmp_path):
    """Creates a temporary project root with an invalid (malformed JSON) concept schema."""
    project_dir = tmp_path / "project_invalid"
    project_dir.mkdir()
    schemas_dir = project_dir / "docs" / "schemas"
    schemas_dir.mkdir(parents=True)

    with open(schemas_dir / "concept_definition_v1.json", "w") as f:
        f.write("this is not valid json") # Malformed JSON
    with open(schemas_dir / "relationship_definition_v1.json", "w") as f:
        json.dump(RELATIONSHIP_SCHEMA_V1, f)
    return project_dir

class TestSemanticLayerValidatorInitAndLoad:
    def test_init_successful_schema_loading(self, project_root_with_schemas):
        """Test SemanticLayerValidator initialization with valid schemas."""
        validator = SemanticLayerValidator(str(project_root_with_schemas))
        
        assert validator.project_root_path == project_root_with_schemas
        assert validator.schema_base_uri == project_root_with_schemas.joinpath("docs", "schemas").as_uri() + "/"
        
        concept_schema_uri = validator.schema_base_uri + "concept_definition_v1.json"
        relationship_schema_uri = validator.schema_base_uri + "relationship_definition_v1.json"
        
        assert concept_schema_uri in validator.system_schemas_store
        assert validator.system_schemas_store[concept_schema_uri] == CONCEPT_SCHEMA_V1
        assert relationship_schema_uri in validator.system_schemas_store
        assert validator.system_schemas_store[relationship_schema_uri] == RELATIONSHIP_SCHEMA_V1
        
        # Check get_schema_by_key
        assert validator.get_schema_by_key("concept") == CONCEPT_SCHEMA_V1
        assert validator.get_schema_by_key("relationship") == RELATIONSHIP_SCHEMA_V1
        assert validator.get_schema_by_key("non_existent_key") is None


    def test_load_system_schemas_file_not_found(self, project_root_missing_concept_schema, capsys):
        """Test schema loading when a schema file is missing."""
        validator = SemanticLayerValidator(str(project_root_missing_concept_schema))
        captured = capsys.readouterr()
        
        concept_schema_path = project_root_missing_concept_schema / "docs" / "schemas" / "concept_definition_v1.json"
        expected_error_msg = f"ERROR: System schema file not found: {concept_schema_path}"
        assert expected_error_msg in captured.out

        concept_schema_uri = validator.schema_base_uri + "concept_definition_v1.json"
        assert concept_schema_uri not in validator.system_schemas_store
        assert validator.get_schema_by_key("concept") is None # Should not be loaded

        # Relationship schema should still be loaded
        relationship_schema_uri = validator.schema_base_uri + "relationship_definition_v1.json"
        assert relationship_schema_uri in validator.system_schemas_store
        assert validator.get_schema_by_key("relationship") == RELATIONSHIP_SCHEMA_V1


    def test_load_system_schemas_json_decode_error(self, project_root_invalid_concept_schema, capsys):
        """Test schema loading when a schema file contains invalid JSON."""
        validator = SemanticLayerValidator(str(project_root_invalid_concept_schema))
        captured = capsys.readouterr()

        concept_schema_path = project_root_invalid_concept_schema / "docs" / "schemas" / "concept_definition_v1.json"
        expected_error_msg_part = f"ERROR: System schema file {concept_schema_path} is not valid JSON"
        assert expected_error_msg_part in captured.out
        
        concept_schema_uri = validator.schema_base_uri + "concept_definition_v1.json"
        assert concept_schema_uri not in validator.system_schemas_store
        assert validator.get_schema_by_key("concept") is None # Should not be loaded

        # Relationship schema should still be loaded
        relationship_schema_uri = validator.schema_base_uri + "relationship_definition_v1.json"
        assert relationship_schema_uri in validator.system_schemas_store
        assert validator.get_schema_by_key("relationship") == RELATIONSHIP_SCHEMA_V1

    def test_get_schema_by_key_invalid_key(self, project_root_with_schemas):
        """Test get_schema_by_key with an invalid/unknown key."""
        validator = SemanticLayerValidator(str(project_root_with_schemas))
        assert validator.get_schema_by_key("unknown_schema_type") is None


class TestValidatePluginSemanticLayer:
    @pytest.fixture
    def validator(self, project_root_with_schemas):
        """Provides a SemanticLayerValidator instance with loaded schemas."""
        return SemanticLayerValidator(str(project_root_with_schemas))

    @pytest.fixture
    def minimal_plugin_manifest(self):
        """Provides a base minimal valid plugin manifest structure."""
        return {
            "plugin_type": "semantic_layer_definition",
            "definition_provider_details": {
                "format": "yaml",
                "root_directory": "semantic_defs",
                "file_mappings": [
                    {"definition_type": "concept", "path_glob": "concepts/**/*.yaml"},
                    {"definition_type": "relationship", "path_glob": "relationships/**/*.yaml"}
                ]
            }
        }

    @pytest.fixture
    def plugin_root(self, tmp_path):
        """Provides a temporary plugin root path."""
        plugin_dir = tmp_path / "my_plugin"
        plugin_dir.mkdir()
        # Create the semantic_defs directory referenced in minimal_plugin_manifest
        (plugin_dir / "semantic_defs").mkdir()
        return str(plugin_dir)

    def test_validate_critical_schemas_not_loaded(self, project_root_missing_concept_schema, minimal_plugin_manifest, plugin_root):
        """Test validation when essential system schemas (e.g., concept) are not loaded."""
        # Validator initialized with a project root where concept schema is missing
        validator_no_concept = SemanticLayerValidator(str(project_root_missing_concept_schema))
        
        is_valid, parsed_defs, errors = validator_no_concept.validate_plugin_semantic_layer(
            minimal_plugin_manifest, plugin_root
        )
        
        assert not is_valid
        assert parsed_defs == {}
        assert any("Critical: Essential system schemas (concept/relationship) not loaded." in e for e in errors)

    def test_validate_incorrect_plugin_type(self, validator, minimal_plugin_manifest, plugin_root):
        """Test validation when plugin_type is not 'semantic_layer_definition'."""
        manifest = minimal_plugin_manifest.copy()
        manifest["plugin_type"] = "not_semantic_layer"
        
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        
        assert not is_valid
        assert parsed_defs == {}
        assert any("Plugin is not of type 'semantic_layer_definition'" in e for e in errors)

    def test_validate_missing_definition_provider_details(self, validator, plugin_root):
        """Test validation when 'definition_provider_details' is missing from manifest."""
        manifest = {"plugin_type": "semantic_layer_definition"} # Missing details
        
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        
        assert not is_valid
        assert parsed_defs == {}
        assert any("Manifest missing 'definition_provider_details'." in e for e in errors)

    def test_validate_details_missing_root_directory(self, validator, plugin_root):
        """Test validation when 'root_directory' is missing from definition_provider_details."""
        manifest = {
            "plugin_type": "semantic_layer_definition",
            "definition_provider_details": {
                "format": "yaml",
                # root_directory is missing
                "file_mappings": [] 
            }
        }
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        
        assert not is_valid
        assert parsed_defs == {}
        assert any("'definition_provider_details' missing 'root_directory'." in e for e in errors)

    def test_validate_details_missing_file_mappings(self, validator, plugin_root):
        """Test validation when 'file_mappings' is missing from definition_provider_details."""
        manifest = {
            "plugin_type": "semantic_layer_definition",
            "definition_provider_details": {
                "format": "yaml",
                "root_directory": "semantic_defs"
                # file_mappings is missing
            }
        }
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        
        assert not is_valid
        assert parsed_defs == {}
        assert any("'definition_provider_details' missing or has invalid 'file_mappings'." in e for e in errors)

    def test_validate_details_invalid_file_mappings_type(self, validator, plugin_root):
        """Test validation when 'file_mappings' is not a list."""
        manifest = {
            "plugin_type": "semantic_layer_definition",
            "definition_provider_details": {
                "format": "yaml",
                "root_directory": "semantic_defs",
                "file_mappings": "this_should_be_a_list" # Invalid type
            }
        }
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        
        assert not is_valid
        assert parsed_defs == {}
        assert any("'definition_provider_details' missing or has invalid 'file_mappings'." in e for e in errors)

    def test_validate_file_mappings_invalid_definition_type(self, validator, minimal_plugin_manifest, plugin_root):
        """Test validation when a file_mapping has an invalid 'definition_type'."""
        manifest = minimal_plugin_manifest.copy()
        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "unknown_type", "path_glob": "*.yaml"}
        ]
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        assert not is_valid
        assert parsed_defs == {}
        assert any("Invalid or unsupported 'definition_type': unknown_type" in e for e in errors)

    def test_validate_file_mappings_missing_path_glob(self, validator, minimal_plugin_manifest, plugin_root):
        """Test validation when a file_mapping is missing 'path_glob'."""
        manifest = minimal_plugin_manifest.copy()
        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "concept"} # Missing path_glob
        ]
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        assert not is_valid
        assert parsed_defs == {}
        assert any(f"Mapping for definition_type 'concept' is missing 'path_glob'." in e for e in errors)

    def test_validate_path_glob_no_matches(self, validator, minimal_plugin_manifest, plugin_root):
        """Test validation when a path_glob matches no files. Should be valid with no definitions."""
        manifest = minimal_plugin_manifest.copy()
        # Ensure the semantic_defs dir exists but is empty for this glob
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        for item in defs_dir.iterdir(): # Clear out any pre-existing files from other fixtures
            if item.is_file(): item.unlink()
            elif item.is_dir(): pytest.fail("Subdirectory found, fixture not clean")

        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "concept", "path_glob": "non_existent_concepts/**/*.yaml"}
        ]
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        assert is_valid # No files found is not an error itself, just means no definitions of that type
        assert parsed_defs == {"concepts": {}, "relationships": {}}
        assert not errors

    def test_validate_single_valid_concept_yaml(self, validator, minimal_plugin_manifest, plugin_root):
        """Test successful validation of a single valid concept YAML file."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        
        concept_data = {"name": "TestConcept1", "description": "A test concept"}
        with open(concepts_dir / "concept1.yaml", "w") as f:
            yaml.dump(concept_data, f)

        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "concept", "path_glob": "concepts/**/*.yaml"}
        ]

        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        
        assert is_valid
        assert not errors
        assert "TestConcept1" in parsed_defs["concepts"]
        assert parsed_defs["concepts"]["TestConcept1"]["description"] == "A test concept"
        assert parsed_defs["concepts"]["TestConcept1"]['_source_file'] == str(Path("semantic_defs") / "concepts" / "concept1.yaml")

    def test_validate_single_valid_relationship_yaml(self, validator, minimal_plugin_manifest, plugin_root):
        """Test successful validation of a single valid relationship YAML file."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        relationships_dir = defs_dir / "relationships"
        relationships_dir.mkdir(parents=True, exist_ok=True)
        
        # Need dummy concepts for relationship validation to pass cross-validation later
        parsed_concept_data = {"name": "SourceConcept", "description": "-"}
        parsed_concept_data2 = {"name": "TargetConcept", "description": "-"}
        # Simulate these concepts are already parsed by placing them in validator's internal store for this test
        # This is a bit of a hack for unit testing this part in isolation before full cross-val tests
        # A better way might be to have a fixture that pre-populates concepts for relationship tests.
        # For now, we'll rely on the cross-validation step to be tested separately or ensure no cross-val errors.
        # To avoid cross-val error, we will make this test only parse relationships and not concepts.
        
        relationship_data = {"name": "Rel1", "source_concept": "SourceConcept", "target_concept": "TargetConcept"}
        with open(relationships_dir / "rel1.yaml", "w") as f:
            yaml.dump(relationship_data, f)

        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "relationship", "path_glob": "relationships/**/*.yaml"}
        ]
        # To pass cross-validation, we need to ensure the concepts exist. We'll add them manually to the parsed_defs
        # that the validator would have built if concepts were also processed.
        # This is a simplification for this specific unit test.
        # We are testing the relationship file parsing and schema validation here.
        # A more robust way would be to use a fixture that sets up a plugin with valid concepts first.
        # For this test, we'll assume concepts are validated elsewhere or not part of this specific glob.

        # Simulate that concepts are already processed and valid for cross-validation to pass
        # This is a way to unit test relationship processing without full integration test complexity here.
        # We'll create a validator instance and manually inject pre-parsed concepts.
        # This is not ideal, but helps focus the test.
        # A better approach: test cross-validation separately.
        # For now, let's ensure the test setup for relationship includes its dependent concepts.
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        with open(concepts_dir / "source.yaml", "w") as f:
            yaml.dump(parsed_concept_data, f)
        with open(concepts_dir / "target.yaml", "w") as f:
            yaml.dump(parsed_concept_data2, f)
        
        # Update manifest to include concept processing for cross-validation to pass
        manifest["definition_provider_details"]["file_mappings"].append(
            {"definition_type": "concept", "path_glob": "concepts/**/*.yaml"}
        )

        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        
        assert is_valid
        assert not errors
        assert "Rel1" in parsed_defs["relationships"]
        assert parsed_defs["relationships"]["Rel1"]["source_concept"] == "SourceConcept"
        assert parsed_defs["relationships"]["Rel1"]['_source_file'] == str(Path("semantic_defs") / "relationships" / "rel1.yaml")

    def test_validate_invalid_yaml_syntax(self, validator, minimal_plugin_manifest, plugin_root):
        """Test validation with a YAML file containing syntax errors."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        
        with open(concepts_dir / "invalid_concept.yaml", "w") as f:
            f.write("name: TestConcept\n  description: Bad Indent") # Invalid YAML

        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "concept", "path_glob": "concepts/**/*.yaml"}
        ]
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)

        assert not is_valid
        assert parsed_defs == {}
        assert any("Error parsing YAML file invalid_concept.yaml" in e for e in errors)

    def test_validate_concept_schema_validation_failure(self, validator, minimal_plugin_manifest, plugin_root):
        """Test validation when a concept file fails schema validation (e.g., missing 'name')."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        
        concept_data_missing_name = {"description": "This concept is missing its name."}
        with open(concepts_dir / "concept_no_name.yaml", "w") as f:
            yaml.dump(concept_data_missing_name, f)

        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "concept", "path_glob": "concepts/**/*.yaml"}
        ]
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)
        
        assert not is_valid
        assert parsed_defs == {}
        assert any("Schema validation failed for concept_no_name.yaml" in e and "'name' is a required property" in e for e in errors)

    def test_validate_duplicate_concept_name(self, validator, minimal_plugin_manifest, plugin_root):
        """Test validation when duplicate concept names are found."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        
        concept_data1 = {"name": "DuplicateConcept", "description": "First instance"}
        concept_data2 = {"name": "DuplicateConcept", "description": "Second instance"}
        with open(concepts_dir / "concept_dup1.yaml", "w") as f:
            yaml.dump(concept_data1, f)
        with open(concepts_dir / "concept_dup2.yaml", "w") as f:
            yaml.dump(concept_data2, f)

        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "concept", "path_glob": "concepts/**/*.yaml"}
        ]
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)

        assert not is_valid
        assert parsed_defs == {} # Should be empty on error
        assert any("Duplicate concept name 'DuplicateConcept' found in concept_dup2.yaml" in e for e in errors) or \
               any("Duplicate concept name 'DuplicateConcept' found in concept_dup1.yaml" in e for e in errors) # Order might vary

    def test_validate_definition_file_not_found_during_open(self, validator, minimal_plugin_manifest, plugin_root, mocker):
        """Test handling FileNotFoundError if a file disappears after glob returns it."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
    
        # Create a file that glob will find
        concepts_subdir = defs_dir / "concepts"
        concepts_subdir.mkdir(parents=True, exist_ok=True) # Ensure concepts subdir exists
        temp_file_path = concepts_subdir / "temp_concept.yaml"
        with open(temp_file_path, "w") as f:
            yaml.dump({"name": "Temp", "description": "Temporary"}, f)

        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "concept", "path_glob": "concepts/**/*.yaml"}
        ]

        # Mock os.path.exists to simulate file disappearing after glob but before open
        # More direct way: mock open to raise FileNotFoundError for that specific path
        def mock_open_wrapper(original_open):
            def mocked_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
                if Path(file).name == 'temp_concept.yaml':
                    raise FileNotFoundError(f"Simulated FileNotFoundError for {file}")
                return original_open(file, mode, buffering, encoding, errors, newline, closefd, opener)
            return mocked_open

        mocker.patch('builtins.open', mock_open_wrapper(open))

        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)

        assert not is_valid
        assert parsed_defs == {}
        assert any(f"File not found during processing: {temp_file_path}" in e for e in errors)

    def test_validate_unsupported_file_format(self, validator, minimal_plugin_manifest, plugin_root):
        """Test validation with an unsupported file format (e.g., 'xml')."""
        manifest = minimal_plugin_manifest.copy()
        manifest["definition_provider_details"]["format"] = "xml"
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        
        with open(concepts_dir / "concept.xml", "w") as f:
            f.write("<concept><name>MyConcept</name></concept>") # Dummy XML content

        manifest["definition_provider_details"]["file_mappings"] = [
            {"definition_type": "concept", "path_glob": "concepts/**/*.xml"}
        ]
        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)

        assert not is_valid
        assert parsed_defs == {}
        assert any("Unsupported file format 'xml' specified in manifest for file concepts/concept.xml" in e for e in errors)

    # --- Tests for Cross-Validation Logic ---

    def test_validate_cross_validation_missing_source_concept(self, validator, minimal_plugin_manifest, plugin_root):
        """Test cross-validation failure when a relationship's source_concept is missing."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        
        # Valid target concept
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        with open(concepts_dir / "target_c.yaml", "w") as f:
            yaml.dump({"name": "TargetConcept", "description": "Target"}, f)

        # Relationship with missing source
        relationships_dir = defs_dir / "relationships"
        relationships_dir.mkdir(parents=True, exist_ok=True)
        with open(relationships_dir / "rel_missing_source.yaml", "w") as f:
            yaml.dump({"name": "Rel1", "source_concept": "MissingSource", "target_concept": "TargetConcept"}, f)

        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)

        assert not is_valid
        assert parsed_defs == {}
        assert any("Cross-validation error in relationship 'Rel1': Source concept 'MissingSource' not found." in e for e in errors)

    def test_validate_cross_validation_missing_target_concept(self, validator, minimal_plugin_manifest, plugin_root):
        """Test cross-validation failure when a relationship's target_concept is missing."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        
        # Valid source concept
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        with open(concepts_dir / "source_c.yaml", "w") as f:
            yaml.dump({"name": "SourceConcept", "description": "Source"}, f)

        # Relationship with missing target
        relationships_dir = defs_dir / "relationships"
        relationships_dir.mkdir(parents=True, exist_ok=True)
        with open(relationships_dir / "rel_missing_target.yaml", "w") as f:
            yaml.dump({"name": "Rel2", "source_concept": "SourceConcept", "target_concept": "MissingTarget"}, f)

        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)

        assert not is_valid
        assert parsed_defs == {}
        assert any("Cross-validation error in relationship 'Rel2': Target concept 'MissingTarget' not found." in e for e in errors)

    def test_validate_cross_validation_valid_relationship(self, validator, minimal_plugin_manifest, plugin_root):
        """Test successful cross-validation for a valid relationship with existing concepts."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        with open(concepts_dir / "source_c.yaml", "w") as f:
            yaml.dump({"name": "SourceConcept", "description": "Source"}, f)
        with open(concepts_dir / "target_c.yaml", "w") as f:
            yaml.dump({"name": "TargetConcept", "description": "Target"}, f)

        relationships_dir = defs_dir / "relationships"
        relationships_dir.mkdir(parents=True, exist_ok=True)
        with open(relationships_dir / "rel_valid.yaml", "w") as f:
            yaml.dump({"name": "ValidRel", "source_concept": "SourceConcept", "target_concept": "TargetConcept"}, f)

        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)

        assert is_valid
        assert not errors
        assert "ValidRel" in parsed_defs["relationships"]
        assert "SourceConcept" in parsed_defs["concepts"]
        assert "TargetConcept" in parsed_defs["concepts"]

    def test_validate_cross_validation_multiple_relationships_mixed_validity(self, validator, minimal_plugin_manifest, plugin_root):
        """Test cross-validation with multiple relationships, some valid, some invalid."""
        manifest = minimal_plugin_manifest.copy()
        defs_dir = Path(plugin_root) / manifest["definition_provider_details"]["root_directory"]
        
        concepts_dir = defs_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        with open(concepts_dir / "c1.yaml", "w") as f: yaml.dump({"name": "C1", "description": "-"}, f)
        with open(concepts_dir / "c2.yaml", "w") as f: yaml.dump({"name": "C2", "description": "-"}, f)

        relationships_dir = defs_dir / "relationships"
        relationships_dir.mkdir(parents=True, exist_ok=True)
        # Valid relationship
        with open(relationships_dir / "rel_valid.yaml", "w") as f:
            yaml.dump({"name": "RelValid", "source_concept": "C1", "target_concept": "C2"}, f)
        # Invalid relationship (missing source)
        with open(relationships_dir / "rel_invalid_source.yaml", "w") as f:
            yaml.dump({"name": "RelInvalidSource", "source_concept": "MissingC", "target_concept": "C1"}, f)
        # Invalid relationship (missing target)
        with open(relationships_dir / "rel_invalid_target.yaml", "w") as f:
            yaml.dump({"name": "RelInvalidTarget", "source_concept": "C2", "target_concept": "MissingC"}, f)

        is_valid, parsed_defs, errors = validator.validate_plugin_semantic_layer(manifest, plugin_root)

        assert not is_valid
        assert parsed_defs == {}
        assert len(errors) == 2
        assert any("Cross-validation error in relationship 'RelInvalidSource': Source concept 'MissingC' not found." in e for e in errors)
        assert any("Cross-validation error in relationship 'RelInvalidTarget': Target concept 'MissingC' not found." in e for e in errors)
