# src/tau_translator_omega/core_engine/semantic_layer_validator.py
import json
import yaml
import glob
import os
from pathlib import Path
from jsonschema import Draft7Validator, RefResolver, ValidationError

class SemanticLayerValidator:
    def __init__(self, project_root_path: str):
        self.project_root_path = Path(project_root_path)
        self.system_schemas_store = {} 
        self.schema_base_uri = self.project_root_path.joinpath("docs", "schemas").as_uri() + "/"
        self._load_system_schemas()

    def _load_system_schemas(self):
        """Loads all known system JSON schemas into memory, keyed by their URI."""
        schema_dir = self.project_root_path / "docs" / "schemas"
        schemas_to_load = {
            "concept": "concept_definition_v1.json",
            "relationship": "relationship_definition_v1.json"
        }

        for schema_key, schema_filename in schemas_to_load.items():
            schema_path = schema_dir / schema_filename
            schema_uri = self.schema_base_uri + schema_filename 
            try:
                with open(schema_path, 'r') as f:
                    schema_content = json.load(f)
                    self.system_schemas_store[schema_uri] = schema_content
            except FileNotFoundError as e:
                print(f"ERROR: System schema file not found: {schema_path}. Validator cannot operate effectively.")
            except json.JSONDecodeError as e:
                print(f"ERROR: System schema file {schema_path} is not valid JSON: {e}. Validator cannot operate effectively.")

    def get_schema_by_key(self, key: str):
        """Helper to get a schema by its short key (e.g., 'concept') if needed."""
        schema_filename_map = {
            "concept": "concept_definition_v1.json",
            "relationship": "relationship_definition_v1.json"
        }
        if key in schema_filename_map:
            return self.system_schemas_store.get(self.schema_base_uri + schema_filename_map[key])
        return None

    def validate_plugin_semantic_layer(self, plugin_manifest: dict, plugin_root_path: str) -> tuple[bool, dict, list[str]]:
        errors = []
        parsed_definitions = {"concepts": {}, "relationships": {}}
        plugin_root = Path(plugin_root_path)

        if not self.get_schema_by_key("concept") or not self.get_schema_by_key("relationship"):
            errors.append("Critical: Essential system schemas (concept/relationship) not loaded. Cannot validate.")
            return False, {}, errors

        plugin_type = plugin_manifest.get("plugin_type")
        if plugin_type != "semantic_layer_definition":
            errors.append(f"Plugin is not of type 'semantic_layer_definition', found '{plugin_type}'.")
            return False, {}, errors

        details = plugin_manifest.get("definition_provider_details")
        if not details:
            errors.append("Manifest missing 'definition_provider_details'.")
            return False, {}, errors

        file_format = details.get("format", "yaml").lower()
        root_def_dir_name = details.get("root_directory")
        if not root_def_dir_name:
            errors.append("'definition_provider_details' missing 'root_directory'.")
            return False, {}, errors
        
        root_def_path = plugin_root / root_def_dir_name

        file_mappings = details.get("file_mappings")
        if not file_mappings or not isinstance(file_mappings, list):
            errors.append("'definition_provider_details' missing or has invalid 'file_mappings'.")
            return False, {}, errors

        resolver = RefResolver(base_uri=self.schema_base_uri, referrer=None, store=self.system_schemas_store)

        for mapping in file_mappings:
            def_type = mapping.get("definition_type") 
            path_glob_pattern = mapping.get("path_glob")

            current_schema_content = self.get_schema_by_key(def_type)
            if not current_schema_content:
                errors.append(f"Invalid or unsupported 'definition_type': {def_type} in file_mappings or schema not loaded.")
                continue
            
            if not path_glob_pattern: 
                errors.append(f"Mapping for definition_type '{def_type}' is missing 'path_glob'.")
                continue

            full_glob = str(root_def_path / path_glob_pattern)
            definition_files = glob.glob(full_glob, recursive=True)

            for file_path_str in definition_files:
                file_path = Path(file_path_str)
                try:
                    with open(file_path, 'r') as f:
                        if file_format == "yaml":
                            data = yaml.safe_load(f)
                        elif file_format == "json":
                            data = json.load(f)
                        else:
                            errors.append(f"Unsupported file format '{file_format}' specified in manifest for file {str(file_path.relative_to(root_def_path))}.")
                            continue
                    
                    validator = Draft7Validator(current_schema_content, resolver=resolver)
                    
                    validation_errors_for_file = []
                    for error in sorted(validator.iter_errors(data), key=str):
                        error_path = " -> ".join(map(str, error.path)) if error.path else "root"
                        validation_errors_for_file.append(f"Schema validation failed for {file_path.name} (type: {def_type}) at '{error_path}': {error.message}")
                    
                    if validation_errors_for_file:
                        errors.extend(validation_errors_for_file)
                        continue 

                    item_name = data.get("name")
                    if not item_name:
                        errors.append(f"Definition in {file_path.name} (type: {def_type}) is missing a 'name'.")
                        continue

                    if def_type == "concept":
                        if item_name in parsed_definitions["concepts"]:
                            errors.append(f"Duplicate concept name '{item_name}' found in {file_path.name}. Previous was {parsed_definitions['concepts'][item_name].get('_source_file')}")
                        else:
                            data['_source_file'] = str(file_path.relative_to(plugin_root))
                            parsed_definitions["concepts"][item_name] = data
                    elif def_type == "relationship":
                        if item_name in parsed_definitions["relationships"]:
                            errors.append(f"Duplicate relationship name '{item_name}' found in {file_path.name}. Previous was {parsed_definitions['relationships'][item_name].get('_source_file')}")
                        else:
                            data['_source_file'] = str(file_path.relative_to(plugin_root))
                            parsed_definitions["relationships"][item_name] = data

                except FileNotFoundError:
                    errors.append(f"File not found during processing: {file_path_str}")
                except (yaml.YAMLError, json.JSONDecodeError) as e:
                    errors.append(f"Error parsing {file_format.upper()} file {file_path.name}: {e}")
                except Exception as e: 
                    errors.append(f"Unexpected error processing file {file_path.name}: {e}")

        if errors:
            # If there were any errors during file processing or schema validation, overall success is False
            return False, {}, errors # Return empty parsed_definitions on any error
        
        # --- Begin Cross-Validation --- 
        cross_validation_errors = []
        # 1. Check if source and target concepts for relationships exist
        for rel_name, rel_def in parsed_definitions.get("relationships", {}).items():
            source_concept_name = rel_def.get("source_concept")
            target_concept_name = rel_def.get("target_concept")

            if source_concept_name and source_concept_name not in parsed_definitions.get("concepts", {}):
                cross_validation_errors.append(
                    f"Cross-validation error in relationship '{rel_name}': Source concept '{source_concept_name}' not found."
                )
            
            if target_concept_name and target_concept_name not in parsed_definitions.get("concepts", {}):
                cross_validation_errors.append(
                    f"Cross-validation error in relationship '{rel_name}': Target concept '{target_concept_name}' not found."
                )
        
        # TODO: Add other cross-validation checks here as needed (e.g., attribute types, FKs)

        if cross_validation_errors:
            errors.extend(cross_validation_errors)
            return False, {}, errors # Return empty parsed_definitions on any cross-validation error
        # --- End Cross-Validation ---

        return True, parsed_definitions, [] # No errors at all, return success
