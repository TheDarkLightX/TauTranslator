from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple


@dataclass
class PluginEntryPoint:
    """Defines the entry point for a plugin."""
    type: str
    module_path: Optional[str] = None
    class_name: Optional[str] = None
    command: Optional[str] = None
    url: Optional[str] = None
    default_init_args: Optional[Dict[str, Any]] = None

@dataclass
class PluginTargetGrammar:
    """Defines the target grammar details for a plugin."""
    grammar_name: str
    version_constraint: Optional[str] = None

@dataclass
class PluginOutputDetails:
    """Defines the output details for a plugin."""
    format_mime_type: str
    file_extension_suggestion: Optional[str] = None

@dataclass
class Plugin:
    """Represents a discovered plugin and its metadata."""
    # Non-default fields first
    id: str
    name: str
    version: str
    description: str
    entry_point: PluginEntryPoint
    manifest_path: Path
    plugin_dir: Path
    manifest_data: Dict[str, Any]

    # Fields with defaults
    plugin_type: str = "generic"
    ilr_versions_supported: List[str] = field(default_factory=list)
    manifest_version: str = "1.0"
    author: Optional[str] = None
    license: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    target_grammar: Optional[PluginTargetGrammar] = None
    output_details: Optional[PluginOutputDetails] = None
    configuration_schema: Optional[Dict[str, Any]] = None
    default_init_args: Optional[Dict[str, Any]] = None
    instance: Optional[Any] = None # Field to store the instantiated plugin class
    ilr_versions_parse_error: Optional[str] = None
    plugin_specific_config: Dict[str, Any] = field(default_factory=dict) # Corrected definition

    @staticmethod
    def _parse_ilr_versions(manifest_data: Dict[str, Any]) -> Tuple[List[str], Optional[str]]:
        """
        Parses and validates the structure of 'ilr_versions_supported'.
        Returns a list of valid version strings and an error code string if issues are found.
        Error codes: "MISSING", "INVALID_OVERALL_TYPE", "EMPTY_LIST", 
                     "LIST_CONTAINS_NON_STRING", "INVALID_CONTENT_EMPTY_STRING",
                     "INVALID_CONTENT_EMPTY_STRING_IN_LIST", "UNKNOWN_EMPTY_AFTER_PARSE".
        """
        ilr_support_data = manifest_data.get("ilr_versions_supported")

        if ilr_support_data is None:
            return [], "MISSING"

        if isinstance(ilr_support_data, str):
            stripped_version = ilr_support_data.strip()
            if not stripped_version:
                return [], "INVALID_CONTENT_EMPTY_STRING"
            return [stripped_version], None

        if isinstance(ilr_support_data, list):
            if not ilr_support_data:  # Empty list
                return [], "EMPTY_LIST"
            
            parsed_versions = []
            for item in ilr_support_data:
                if not isinstance(item, str):
                    return [], "LIST_CONTAINS_NON_STRING"
                stripped_item = item.strip()
                if not stripped_item:
                    return [], "INVALID_CONTENT_EMPTY_STRING_IN_LIST"
                parsed_versions.append(stripped_item)
            
            if not parsed_versions:
                 return [], "UNKNOWN_EMPTY_AFTER_PARSE"

            return parsed_versions, None

        return [], "INVALID_OVERALL_TYPE"

    @staticmethod
    def _parse_entry_point(manifest_data: Dict[str, Any], manifest_path: Path, plugin_id: str) -> PluginEntryPoint:
        """Parses and validates the entry_point dictionary from the manifest."""
        entry_point_data = manifest_data.get("entry_point")
        if not isinstance(entry_point_data, dict):
            raise ValueError(f"Manifest {manifest_path} for plugin '{plugin_id}': 'entry_point' must be a dictionary.")

        ep_type = entry_point_data.get("type")
        if not isinstance(ep_type, str):
            raise ValueError(f"Manifest {manifest_path} for plugin '{plugin_id}': 'entry_point' dictionary must contain a 'type' string.")

        ep_module_path: Optional[str] = None
        ep_class_name: Optional[str] = None
        ep_command: Optional[str] = None
        ep_url: Optional[str] = None

        if ep_type == "module":
            ep_module_path = entry_point_data.get("module_path")
            ep_class_name = entry_point_data.get("class_name")
            if not ep_module_path or not ep_class_name:
                raise ValueError(
                    f"Manifest {manifest_path} for plugin '{plugin_id}': Entry point of type 'module' must define 'module_path' and 'class_name' within the 'entry_point' dictionary."
                )
        elif ep_type == "cli":
            ep_command = entry_point_data.get("command")
            if not ep_command:
                raise ValueError(
                    f"Manifest {manifest_path} for plugin '{plugin_id}': Entry point of type 'cli' must define 'command' within the 'entry_point' dictionary."
                )
        elif ep_type == "url":
            ep_url = entry_point_data.get("url")
            if not ep_url:
                raise ValueError(
                    f"Manifest {manifest_path} for plugin '{plugin_id}': Entry point of type 'url' must define 'url' within the 'entry_point' dictionary."
                )
        else:
            raise ValueError(
                f"Manifest {manifest_path} for plugin '{plugin_id}': Unsupported 'entry_point' type: '{ep_type}'. Supported types are 'module', 'cli', 'url'."
            )
        
        return PluginEntryPoint(
            type=ep_type, 
            module_path=ep_module_path, 
            class_name=ep_class_name, 
            command=ep_command, 
            url=ep_url
        )

    @classmethod
    def from_manifest(cls, manifest_data: Dict[str, Any], manifest_path: Path, plugin_dir: Path) -> "Plugin":
        """Creates a Plugin instance from manifest data."""
        plugin_id = manifest_data.get("id", plugin_dir.name)
        name = manifest_data.get("name", plugin_id)
        version = manifest_data.get("version", "0.0.0")
        description = manifest_data.get("description", "")
        author = manifest_data.get("author")
        license_type = manifest_data.get("license") # Field in dataclass is 'license'
        tags = manifest_data.get("tags", [])
        dependencies = manifest_data.get("dependencies", [])
        plugin_type = manifest_data.get("plugin_type", "generic")
        
        ilr_versions_supported, ilr_versions_parse_error = cls._parse_ilr_versions(manifest_data)

        entry_point_obj = cls._parse_entry_point(manifest_data, manifest_path, plugin_id)
        
        raw_entry_point_data = manifest_data.get("entry_point", {})
        ep_default_init_args = raw_entry_point_data.get("default_init_args") if isinstance(raw_entry_point_data, dict) else None

        target_grammar_data = manifest_data.get("target_grammar")
        target_grammar = PluginTargetGrammar(**target_grammar_data) if isinstance(target_grammar_data, dict) else None

        output_details_data = manifest_data.get("output_details")
        output_details = PluginOutputDetails(**output_details_data) if isinstance(output_details_data, dict) else None
        
        configuration_schema = manifest_data.get("configuration_schema")
        if configuration_schema is not None and not isinstance(configuration_schema, dict):
            raise ValueError(f"Manifest {manifest_path} for plugin '{plugin_id}': 'configuration_schema' must be a dictionary if present.")

        return cls(
            id=plugin_id,
            name=name,
            version=version,
            description=description,
            author=author,
            license=license_type,
            tags=tags,
            dependencies=dependencies,
            plugin_type=plugin_type,
            ilr_versions_supported=ilr_versions_supported,
            entry_point=entry_point_obj,
            manifest_path=manifest_path,
            plugin_dir=plugin_dir,
            manifest_data=manifest_data, 
            manifest_version=manifest_data.get("manifest_version", "1.0"),
            target_grammar=target_grammar,
            output_details=output_details,
            configuration_schema=configuration_schema,
            default_init_args=ep_default_init_args,
            ilr_versions_parse_error=ilr_versions_parse_error
        )


class BasePluginValidator:
    """Base class for plugin manifest validators."""
    def __init__(self, core_ilr_version: str, logger):
        """Initializes the base validator.

        Args:
            core_ilr_version: The core ILR version string.
            logger: The logger instance.
        """
        self.core_ilr_version = core_ilr_version
        self.logger = logger

    def validate_manifest(self, manifest_data: Dict[str, Any], plugin_dir: Path) -> Tuple[bool, List[str]]:
        """Validates a plugin manifest.

        This method should be implemented by subclasses for specific plugin types.

        Args:
            manifest_data: The plugin manifest data as a dictionary.
            plugin_dir: The Path object representing the plugin's base directory.

        Returns:
            A tuple (is_valid, errors_list).
        """
        raise NotImplementedError("Subclasses must implement validate_manifest")
