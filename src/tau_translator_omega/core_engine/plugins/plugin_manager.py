import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any, Type, Union
import importlib
import sys
import inspect
from datetime import datetime

from .grammar_plugin_validator import GrammarPluginValidator

from .generic_plugin_validator import GenericPluginValidator
from ..plugin import Plugin, PluginEntryPoint, BasePluginValidator
from ..version_handler import VersionHandler

logger = logging.getLogger(__name__)

# Ensure a basic configuration for the logger if no other configuration is present.
# This is helpful for standalone testing or direct script use.
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@dataclass
class PluginError:
    """Represents a structured error encountered by the PluginManager."""
    code: str
    message: str
    plugin_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __str__(self):
        return f"[{self.timestamp}] {self.code} (Plugin ID: {self.plugin_id or 'N/A'}): {self.message}"


@dataclass
class ValidationResult:
    """Result of plugin validation with success status and configuration."""
    success: bool
    config: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class PluginManager:
    """Manages discovery, loading, and interaction with plugins."""
    CORE_ILR_VERSION = "1.0.0" # Default, can be overridden in __init__

    def __init__(
        self,
        plugin_dirs: Union[str, List[str], Path, List[Path]],
        core_ilr_version: str = "1.0.0",
        default_init_args: Optional[Dict[str, Any]] = None
    ):
        """Initialize PluginManager with plugin directories and configuration."""
        self.errors: List[PluginError] = []
        self.version_handler = VersionHandler()
        self.plugins: Dict[str, Plugin] = {}

        self._initialize_plugin_directories(plugin_dirs)
        self._initialize_core_version(core_ilr_version)
        self._initialize_default_args(default_init_args)
        self._load_manifest_schema()
        self._initialize_validators()

    def _initialize_plugin_directories(self, plugin_dirs: Union[str, List[str], Path, List[Path]]) -> None:
        """Initialize and validate plugin directory paths."""
        self.plugin_roots: List[Path] = []

        if isinstance(plugin_dirs, (str, Path)):
            self.plugin_roots.append(Path(plugin_dirs))
        elif isinstance(plugin_dirs, list):
            self.plugin_roots = [Path(p) for p in plugin_dirs]
        else:
            raise TypeError("plugin_dirs must be a string, Path, or list of strings/Paths")

    def _initialize_core_version(self, core_ilr_version: str) -> None:
        """Initialize and validate core ILR version."""
        self.core_ilr_version_str = core_ilr_version
        self.core_ilr_semver = self.version_handler.parse_semver(core_ilr_version, "Core ILR")

        if self.core_ilr_semver is None:
            self.errors.extend([
                PluginError(code="ILR_CORE_VERSION_INVALID", message=err)
                for err in self.version_handler.errors
            ])
            self._add_error(
                "CORE_ILR_INVALID_INIT",
                f"Core ILR version string '{core_ilr_version}' is invalid. See previous errors for details."
            )

    def _initialize_default_args(self, default_init_args: Optional[Dict[str, Any]]) -> None:
        """Initialize default initialization arguments."""
        self.default_init_args = default_init_args or {}

    def _load_manifest_schema(self) -> None:
        """Load and validate the plugin manifest schema."""
        self.manifest_schema: Optional[Dict[str, Any]] = None

        try:
            schema_path = self._get_schema_file_path()
            if not schema_path.exists():
                self._add_error("SCHEMA_LOAD_ERROR", f"Plugin manifest schema file not found at {schema_path}.")
                return

            with open(schema_path, 'r') as schema_f:
                self.manifest_schema = json.load(schema_f)
            logger.info(f"Successfully loaded plugin manifest schema from {schema_path}")

        except FileNotFoundError:
            self._add_error("SCHEMA_LOAD_ERROR", f"Plugin manifest schema file not found (FileNotFoundError).")
        except json.JSONDecodeError as e:
            schema_path = self._get_schema_file_path()
            self._add_error("SCHEMA_LOAD_UNEXPECTED_ERROR", f"Unexpected error loading schema from {schema_path}: {e}.")
        except Exception as e:
            schema_path = self._get_schema_file_path()
            self._add_error("SCHEMA_LOAD_UNEXPECTED_ERROR", f"Unexpected error loading schema from {schema_path}: {e}.")

        if not self.manifest_schema and not any("SCHEMA_" in err.code for err in self.errors):
            logger.error("CRITICAL: Plugin manifest schema could not be loaded. Manifest validation will be skipped.")

    def _get_schema_file_path(self) -> Path:
        """Get the path to the plugin manifest schema file."""
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        return project_root / "docs" / "schemas" / "plugin_manifest_schema.json"

    def _initialize_validators(self) -> None:
        """Initialize plugin validators for different plugin types."""
        self.plugin_validators: Dict[str, BasePluginValidator] = {
            "grammar_definition": GrammarPluginValidator(self.core_ilr_version_str, logger),
            "semantic_construct": GenericPluginValidator(self.core_ilr_version_str, logger),
            "generic": GenericPluginValidator(self.core_ilr_version_str, logger)
        }

    # _parse_semver method is removed, functionality moved to VersionHandler

    def _add_error(self, code: str, message: str, plugin_obj: Optional[Plugin] = None):
        """Adds a structured error to the internal list."""
        current_plugin_id = plugin_obj.id if plugin_obj else None
        error_entry = PluginError(code=code, message=message, plugin_id=current_plugin_id)
        self.errors.append(error_entry)
        logger.error(str(error_entry)) # Log the string representation for immediate visibility

    def _is_ilr_version_compatible(self, plugin: Plugin) -> bool:
        """Checks if the plugin's ILR version requirements are compatible with the core version using VersionHandler."""
        if self.core_ilr_semver is None:
            # If core ILR version is invalid, cannot perform compatibility check.
            # This state should ideally prevent plugin loading attempts or be handled earlier.
            # An error for invalid core ILR would have been added during __init__.
            self._add_error(
                "ILR_CORE_VERSION_INVALID_SKIP_CHECK", 
                f"Core ILR version '{self.core_ilr_version_str}' is invalid. Skipping ILR compatibility check for plugin '{plugin.id}'.",
                plugin
            )
            return False # Cannot be compatible if core version is broken

        is_compatible, version_errors = self.version_handler.check_ilr_compatibility(
            core_ilr_semver=self.core_ilr_semver,
            core_ilr_version_str=self.core_ilr_version_str,
            plugin=plugin
        )

        if not is_compatible:
            # Transfer errors from version_handler to PluginManager's errors
            # Prefix them to indicate they are from version compatibility check
            for err in version_errors:
                # The errors from version_handler are already formatted with codes and plugin IDs
                self._add_error("ILR Incompatibility", f"{err}", plugin)
            # No need to call self._add_error again as version_handler already logged them.
        return is_compatible

    def _import_plugin_module(self, entry_point: PluginEntryPoint, plugin_root_dir: Path, plugin_id_for_logging: str) -> Optional[Any]:
        """Imports the plugin module, managing sys.path."""
        if not entry_point.module_path:
            self._add_error(
                "PLUGIN_MODULE_PATH_MISSING", 
                f"Plugin '{plugin_id_for_logging}' entry_point is missing 'module_path'.",
                self.get_plugin(plugin_id_for_logging) # Pass the plugin object if available
            )
            return None

        module_name_to_import = entry_point.module_path
        if module_name_to_import.endswith(".py"):
            module_name_to_import = module_name_to_import[:-3]

        original_sys_path = list(sys.path)
        sys.path.insert(0, str(plugin_root_dir.resolve()))

        try:
            expected_module_file_path = (plugin_root_dir / entry_point.module_path).resolve()

            if module_name_to_import in sys.modules:
                existing_module = sys.modules[module_name_to_import]
                existing_module_file = getattr(existing_module, '__file__', None)
                if existing_module_file:
                    if Path(existing_module_file).resolve() != expected_module_file_path:
                        logger.info(
                            f"Module '{module_name_to_import}' (ID: {plugin_id_for_logging}) already in sys.modules "
                            f"but from a different path ('{existing_module_file}' vs '{expected_module_file_path}'). "
                            f"Removing from cache for fresh import."
                        )
                        del sys.modules[module_name_to_import]
                    else:
                        logger.info(
                            f"Module '{module_name_to_import}' (ID: {plugin_id_for_logging}) already in sys.modules "
                            f"and path matches. Using existing."
                        )
                # If no __file__ or other edge cases, let import_module handle it, possibly re-importing or using cache.

            module = importlib.import_module(module_name_to_import)
            return module
        except ImportError as e:
            self._add_error("PLUGIN_IMPORT_ERROR", f"Failed to import module '{entry_point.module_path}' (as '{module_name_to_import}') for plugin '{plugin_id_for_logging}': {e}", None)
            logger.error(f"PLUGIN_IMPORT_ERROR: Failed to import module '{entry_point.module_path}' (as '{module_name_to_import}') for plugin '{plugin_id_for_logging}': {e}")
        except Exception as e:
            self._add_error("PLUGIN_MODULE_LOAD_UNEXPECTED_ERROR", f"Unexpected error loading module '{entry_point.module_path}' (as '{module_name_to_import}') for plugin '{plugin_id_for_logging}': {e}", None)
            logger.exception(f"PLUGIN_MODULE_LOAD_UNEXPECTED_ERROR: Unexpected error loading module '{entry_point.module_path}' (as '{module_name_to_import}') for plugin '{plugin_id_for_logging}'.")
        finally:
            sys.path = original_sys_path # Restore sys.path
        return None

    def _find_plugin_class(self, module: Any, class_name: str, plugin_id_for_logging: str) -> Optional[Type[Any]]: # Changed Type hint
        """Finds and validates the plugin class within the module."""
        try:
            plugin_class = getattr(module, class_name)
            if not inspect.isclass(plugin_class):
                self._add_error("PLUGIN_ENTRY_NOT_CLASS", f"Entry point '{class_name}' in module '{module.__name__}' for plugin '{plugin_id_for_logging}' is not a class.", None) # Pass None for plugin_obj
                return None
            # Removed issubclass check against BasePlugin as it's not defined for plugin instances
            logger.info(f"Successfully found class '{class_name}' for plugin '{plugin_id_for_logging}'.")
            return plugin_class
        except AttributeError:
            self._add_error("PLUGIN_CLASS_NOT_FOUND", f"Class '{class_name}' not found in module '{module.__name__}' for plugin '{plugin_id_for_logging}'.", None) # Pass None for plugin_obj
        except Exception as e: # Broad catch for unexpected inspection issues
            self._add_error("PLUGIN_CLASS_FIND_UNEXPECTED_ERROR", f"Unexpected error finding class '{class_name}' for plugin '{plugin_id_for_logging}': {e}", None) # Pass None for plugin_obj
            logger.exception(f"PLUGIN_CLASS_FIND_UNEXPECTED_ERROR: Unexpected error finding class '{class_name}' for plugin '{plugin_id_for_logging}'.")
        return None

    def _prepare_plugin_init_args(self, plugin_class: Type[Any], plugin_obj: Plugin) -> Dict[str, Any]:
        """Prepares arguments for plugin class instantiation."""
        init_args = {}
        try:
            sig = inspect.signature(plugin_class.__init__)
            available_params = set(sig.parameters.keys())
            
            # Start with manager-level defaults
            combined_args = self.default_init_args.copy()

            # Overlay with plugin-specific defaults from entry_point
            if plugin_obj.entry_point and plugin_obj.entry_point.default_init_args:
                combined_args.update(plugin_obj.entry_point.default_init_args)

            # Overlay with validated plugin-specific configuration (highest precedence)
            if plugin_obj.plugin_specific_config: # This now comes from validator
                combined_args.update(plugin_obj.plugin_specific_config)

            for name, value in combined_args.items():
                if name in available_params:
                    init_args[name] = value
            
            logger.info(f"Prepared init args for {plugin_obj.id}: {init_args}")
            return init_args
        except Exception as e: # Broad catch for unexpected inspection issues
            self._add_error("PLUGIN_INIT_ARGS_PREP_ERROR", f"Error preparing __init__ arguments for plugin '{plugin_obj.id}': {e}", plugin_obj)
            logger.exception(f"PLUGIN_INIT_ARGS_PREP_ERROR: Error preparing __init__ arguments for plugin '{plugin_obj.id}'.")
            return {} # Return empty, likely leading to instantiation failure if args were crucial

    def _instantiate_plugin(self, plugin_class: Type[Any], init_args: Dict[str, Any], plugin_obj: Plugin) -> Optional[Any]:
        """Instantiates the plugin class with the given arguments."""
        try:
            instance = plugin_class(**init_args)
            logger.info(f"Successfully instantiated plugin '{plugin_obj.id}'.")
            return instance
        except TypeError as e:
            self._add_error("PLUGIN_INSTANTIATION_TYPE_ERROR", f"TypeError instantiating plugin '{plugin_obj.id}' (check __init__ args): {e}", plugin_obj)
            logger.error(f"PLUGIN_INSTANTIATION_TYPE_ERROR: TypeError instantiating plugin '{plugin_obj.id}': {e}")
        except Exception as e:
            self._add_error("PLUGIN_INSTANTIATION_ERROR", f"Failed to instantiate plugin '{plugin_obj.id}': {e}", plugin_obj)
            logger.exception(f"PLUGIN_INSTANTIATION_ERROR: Failed to instantiate plugin '{plugin_obj.id}'.")
        return None

    def _load_and_instantiate_plugin(self, plugin_obj: Plugin) -> Optional[Any]:
        """
        Dynamically loads and instantiates the plugin's entry point class.
        Orchestrates calls to helper methods for modularity.
        Grammar definition plugins do not require instantiation by the PluginManager.
        """
        if plugin_obj.plugin_type == "grammar_definition":
            logger.info(f"Plugin '{plugin_obj.id}' is a grammar_definition type, no instance creation needed by PluginManager.")
            return None # Grammar plugins don't have an instance managed this way

        if not plugin_obj.entry_point:
            self._add_error("PLUGIN_NO_ENTRY_POINT", f"Plugin '{plugin_obj.id}' has no entry_point defined.", plugin_obj)
            return None

        # If entry point type is not 'module', no Python instance is loaded/created by PluginManager
        if plugin_obj.entry_point.type != 'module':
            logger.info(f"Plugin '{plugin_obj.id}' entry point type is '{plugin_obj.entry_point.type}', no Python module instantiation required by PluginManager.")
            return None # For types like 'cli', instance is not managed this way

        # Check for missing module_path or class_name for 'module' type plugins
        if not plugin_obj.entry_point.module_path or not plugin_obj.entry_point.class_name:
            self._add_error(
                "MODULE_PATH_OR_CLASS_NAME_MISSING",
                f"Plugin '{plugin_obj.id}' of type 'module' is missing module_path or class_name in its entry_point.",
                plugin_obj
            )
            return None

        plugin_id_for_logging = plugin_obj.id or "UNKNOWN_PLUGIN"
        
        # plugin_obj.manifest_path should be a Path object
        # plugin_root_dir is the directory containing the manifest
        plugin_root_dir = plugin_obj.manifest_path.parent if plugin_obj.manifest_path else Path(".") 

        module = self._import_plugin_module(plugin_obj.entry_point, plugin_root_dir, plugin_id_for_logging)
        if not module:
            return None

        plugin_class = self._find_plugin_class(module, plugin_obj.entry_point.class_name, plugin_id_for_logging)
        if not plugin_class:
            return None

        init_args = self._prepare_plugin_init_args(plugin_class, plugin_obj)
        
        instance = self._instantiate_plugin(plugin_class, init_args, plugin_obj)
        
        return instance

    def _process_manifest(self, manifest_path: Path, plugin_dir: Path) -> Optional[Plugin]:
        """Process a plugin manifest file and create a Plugin instance."""
        manifest_data = self._load_manifest_data(manifest_path)
        if not manifest_data:
            return None

        plugin_candidate = self._create_plugin_candidate(manifest_data, manifest_path, plugin_dir)
        if not plugin_candidate:
            return None

        if not self._validate_plugin_manifest(plugin_candidate, manifest_data, plugin_dir):
            return None

        if not self._is_ilr_version_compatible(plugin_candidate):
            logger.warning(f"Plugin {plugin_candidate.id} from {manifest_path} is not ILR compatible. Not loading.")
            return None

        if not self._instantiate_plugin_if_needed(plugin_candidate):
            return None

        logger.info(f"Successfully processed and loaded plugin '{plugin_candidate.id}' from {manifest_path}.")
        return plugin_candidate

    def _load_manifest_data(self, manifest_path: Path) -> Optional[Dict[str, Any]]:
        """Load and parse manifest JSON data."""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self._add_error("MANIFEST_NOT_FOUND", f"Manifest file not found at {manifest_path}.", None)
        except json.JSONDecodeError as e:
            self._add_error("MANIFEST_JSON_MALFORMED", f"Error decoding JSON from manifest {manifest_path}: {e}.", None)
        except Exception as e:
            self._add_error("MANIFEST_READ_ERROR", f"Error reading manifest file {manifest_path}: {e}.", None)
        return None

    def _create_plugin_candidate(self, manifest_data: Dict[str, Any], manifest_path: Path, plugin_dir: Path) -> Optional[Plugin]:
        """Create a Plugin object from manifest data."""
        try:
            plugin_candidate = Plugin.from_manifest(manifest_data, manifest_path, plugin_dir)
            if plugin_candidate is None:
                self._add_error("PLUGIN_OBJECT_CREATION_FAILED",
                              f"Plugin.from_manifest returned None for {manifest_path}. Manifest might be critically malformed.", None)
                return None
            return plugin_candidate
        except Exception as e:
            self._add_error("PLUGIN_OBJECT_CREATION_EXCEPTION",
                          f"Exception creating Plugin object from manifest {manifest_path}: {e}. Manifest might be critically malformed.", None)
            logger.exception(f"Exception during Plugin.from_manifest for {manifest_path}")
            return None

    def _validate_plugin_manifest(self, plugin_candidate: Plugin, manifest_data: Dict[str, Any], plugin_dir: Path) -> bool:
        """Validate plugin manifest using appropriate validator."""
        plugin_type = manifest_data.get("plugin_type")
        plugin_id = plugin_candidate.id

        if not plugin_type:
            self._add_error("PLUGIN_TYPE_MISSING", f"Manifest for {plugin_id} is missing 'plugin_type'.", plugin_candidate)
            return False

        # Try type-specific validation first
        validation_result = self._try_type_specific_validation(plugin_candidate, manifest_data, plugin_dir, plugin_type)
        if validation_result.success:
            plugin_candidate.plugin_specific_config = validation_result.config
            return True

        # Fall back to generic validation for unknown types
        if plugin_type not in ["grammar_definition", "semantic_construct"]:
            return self._try_generic_validation(plugin_candidate, manifest_data, plugin_dir)

        logger.warning(f"Type-specific validation failed for {plugin_id} and it's a known type. Plugin will not be loaded.")
        return False

    def _instantiate_plugin_if_needed(self, plugin_candidate: Plugin) -> bool:
        """Instantiate plugin if it's a module type that requires instantiation."""
        instantiation_result = self._load_and_instantiate_plugin(plugin_candidate)

        # Check if instantiation was required but failed
        if (instantiation_result is None and
            plugin_candidate.entry_point and
            plugin_candidate.entry_point.type == 'module'):
            logger.warning(f"Failed to load or instantiate module plugin '{plugin_candidate.id}'. Not loading.")
            return False

        return True

    def _try_type_specific_validation(self, plugin_candidate: Plugin, manifest_data: Dict[str, Any],
                                    plugin_dir: Path, plugin_type: str) -> ValidationResult:
        """Try type-specific validation for known plugin types."""
        validator = self.plugin_validators.get(plugin_type)
        if not validator:
            self._add_error("VALIDATOR_NOT_FOUND",
                          f"No validator registered for plugin_type '{plugin_type}' for plugin {plugin_candidate.id}.",
                          plugin_candidate)
            return ValidationResult(success=False)

        try:
            is_valid, parsed_info, type_specific_errors = validator.validate_manifest(manifest_data, plugin_dir)
            if is_valid:
                logger.info(f"{plugin_type} validation successful for {plugin_candidate.id}.")
                return ValidationResult(success=True, config=parsed_info)
            else:
                for error_msg in type_specific_errors:
                    self._add_error(f"{plugin_type.upper()}_VALIDATION_ERROR", f"{error_msg}", plugin_candidate)
                logger.warning(f"{plugin_type} validation failed for {plugin_candidate.id}: {type_specific_errors}")
                return ValidationResult(success=False, errors=type_specific_errors)
        except Exception as e:
            self._add_error("VALIDATION_EXCEPTION", f"Exception during {plugin_type} validation: {e}", plugin_candidate)
            return ValidationResult(success=False, errors=[str(e)])

    def _try_generic_validation(self, plugin_candidate: Plugin, manifest_data: Dict[str, Any], plugin_dir: Path) -> bool:
        """Try generic validation as fallback for unknown plugin types."""
        generic_validator = self.plugin_validators.get("generic")
        if not generic_validator:
            logger.warning(f"Plugin {plugin_candidate.id} has unknown type and no generic validator available. Plugin will not be loaded.")
            return False

        logger.info(f"Attempting generic validation for {plugin_candidate.id} of type {manifest_data.get('plugin_type')}.")
        try:
            is_valid_generic, parsed_config_generic, generic_errors = generic_validator.validate_manifest(manifest_data, plugin_dir)
            if is_valid_generic:
                plugin_candidate.plugin_specific_config = parsed_config_generic
                logger.info(f"Generic manifest validation successful for {plugin_candidate.id}.")
                return True
            else:
                for error_msg in generic_errors:
                    self._add_error("GENERIC_VALIDATION_ERROR", f"{error_msg}", plugin_candidate)
                logger.warning(f"Generic manifest validation failed for {plugin_candidate.id}: {generic_errors}")
                return False
        except Exception as e:
            self._add_error("GENERIC_VALIDATION_EXCEPTION", f"Exception during generic validation: {e}", plugin_candidate)
            return False

    def discover_plugins(self):
        """Discovers plugins from the specified directories."""
        self.plugins.clear()
        self.errors.clear()
        logger.info(f"Starting plugin discovery in root directories: {self.plugin_roots} for core ILR {self.core_ilr_version_str}")

        for plugin_root_dir in self.plugin_roots:
            if not plugin_root_dir.exists() or not plugin_root_dir.is_dir():
                self._add_error(
                    "PLUGIN_DIR_INVALID", 
                    f"Plugin directory {plugin_root_dir} does not exist or is not a directory. Skipping.",
                    None
                )
                continue
            
            logger.info(f"Scanning for plugins in: {plugin_root_dir}")
            # Recursively find all manifest.json files
            manifest_paths_found = list(plugin_root_dir.rglob("manifest.json"))
            logger.info(f"Manifests found in {plugin_root_dir}: {manifest_paths_found}")

            for manifest_path in manifest_paths_found:
                logger.info(f"Processing manifest_path: {manifest_path}")
                plugin_candidate_dir = manifest_path.parent
                logger.info(f"Found potential plugin manifest: {manifest_path} in dir {plugin_candidate_dir}")

                plugin_candidate = self._process_manifest(manifest_path, plugin_candidate_dir)

                if plugin_candidate:
                    # If _process_manifest returned a plugin_candidate, it means:
                    # 1. Manifest was valid and parsed.
                    # 2. Type-specific or generic validation passed.
                    # 3. It IS ILR compatible.
                    # 4. plugin_candidate.instance is correctly set (actual instance or None).

                    if plugin_candidate.id in self.plugins:
                        logger.warning(f"DUPLICATE_PLUGIN_ID: Plugin ID '{plugin_candidate.id}' from {manifest_path} already loaded from {self.plugins[plugin_candidate.id].manifest_path}. Skipping.")
                        self._add_error(
                            "DUPLICATE_PLUGIN_ID", 
                            f"Plugin ID '{plugin_candidate.id}' from manifest {manifest_path} already loaded from {self.plugins[plugin_candidate.id].manifest_path}. Skipping.", 
                            plugin_candidate
                        )
                    else:
                        # All checks passed in _process_manifest, plugin_candidate is ready.
                        self.plugins[plugin_candidate.id] = plugin_candidate
                        instance_status = "instantiated" if plugin_candidate.instance else "no instance required/created"
                        logger.info(f"PLUGIN_REGISTERED: Plugin '{plugin_candidate.id}' (Type: {plugin_candidate.plugin_type}, Instance: {instance_status}) from {manifest_path} registered.")
                else:
                    # _process_manifest returned None, meaning some validation/check failed.
                    # Errors would have been logged by _process_manifest or its sub-methods.
                    logger.info(f"_process_manifest returned None for {manifest_path}. Plugin not loaded.")

        if not self.plugins:
            logger.warning("No plugins were loaded after discovery.")
        
        return self.plugins

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        return self.plugins.get(plugin_id)

    def get_all_plugins(self) -> List[Plugin]:
        return list(self.plugins.values())

    def get_errors(self) -> List[PluginError]: # Changed return type
        return self.errors

    def invoke_translation(self, plugin_id: str, tau_source: str) -> Optional[Dict[str, Any]]:
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            logger.error(f"Plugin '{plugin_id}' not found.")
            self.errors.append(PluginError(code="PLUGIN_NOT_FOUND", message=f"Plugin '{plugin_id}' not found for translation."))
            return None

        if not plugin.instance:
            logger.error(f"Plugin '{plugin_id}' instance is still None after instantiation attempt.")
            self._add_error("PLUGIN_NO_INSTANCE_INVOKE", f"Plugin '{plugin_id}' has no active instance; cannot invoke translation.", plugin)
            return None

        translate_method = getattr(plugin.instance, 'translate_to_ilr', None)
        if not callable(translate_method):
            logger.error(f"Plugin '{plugin_id}' instance does not have a callable 'translate_to_ilr' method.")
            self.errors.append(PluginError(code="PLUGIN_MISSING_TRANSLATE_METHOD", message=f"Plugin '{plugin_id}': Missing callable 'translate_to_ilr' method."))
            return None
        try:
            return translate_method(tau_source)
        except Exception as e:
            logger.exception(f"Error invoking 'translate_to_ilr' on plugin '{plugin_id}': {e}") # logger.exception for stack trace
            self.errors.append(PluginError(code="PLUGIN_RUNTIME_ERROR", message=f"Runtime error in plugin '{plugin_id}': {e}"))
            return None

    def _load_plugin_from_manifest_data(self, manifest_path: Path, manifest_data: Dict[str, Any], plugin_dir: Path) -> Optional[Plugin]:
        """Loads, validates, and prepares a single plugin object from manifest data."""
        try:
            # Add manifest_path and plugin_dir to the data for Plugin object creation
            data_for_plugin_obj = manifest_data.copy()
            data_for_plugin_obj['manifest_path'] = manifest_path
            data_for_plugin_obj['plugin_dir'] = plugin_dir
            data_for_plugin_obj['manifest_data'] = manifest_data # Store raw manifest

            plugin_obj = Plugin(**data_for_plugin_obj)
        except Exception as e: # Catch potential errors during Plugin instantiation (e.g. Pydantic validation)
            self._add_error(
                "PLUGIN_OBJECT_CREATION_ERROR",
                f"Failed to create Plugin object from manifest {manifest_path}: {e}",
                None  # Cannot create plugin object for context since creation failed
            )
            logger.error(f"PLUGIN_OBJECT_CREATION_ERROR: Failed to create Plugin object from manifest {manifest_path}: {e}")
            return None

        if not self._validate_manifest(plugin_obj, manifest_data):
            # Errors are added by _validate_manifest
            logger.warning(f"Manifest validation failed for plugin '{plugin_obj.id}' from {manifest_path}. Not loading.")
            return None

        if not self._is_ilr_version_compatible(plugin_obj):
            logger.warning(f"Plugin '{plugin_obj.id}' (ILR specifiers: {plugin_obj.ilr_versions_supported}) from {manifest_path} is not compatible with core ILR version '{self.core_ilr_version_str}'. Not loading.")
            # Errors are added by _is_ilr_version_compatible
            return None

        self._register_plugin(plugin_obj) # This attempts to register and potentially instantiate

        # Check if registration was successful by seeing if it's in self.plugins
        if plugin_obj.id not in self.plugins:
            logger.info(f"Plugin '{plugin_obj.id}' was not added to manager.plugins after registration attempt. This typically means instantiation or a sub-step within registration failed (e.g., _load_and_instantiate_plugin returned None). Check previous logs for specific errors related to this plugin.")
            return None # Explicitly return None if not actually registered

        return plugin_obj
