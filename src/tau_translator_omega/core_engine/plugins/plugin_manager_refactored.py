"""
Plugin Manager following the Intentional Disclosure Principle.

This module orchestrates plugin operations with complete transparency:
- All I/O operations explicitly isolated in repositories
- Domain types replace primitive obsession
- Business logic separated from infrastructure
- Every method under 10 lines with single responsibility

Copyright: DarkLightX / Dana Edwards
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any, Type, Union, NewType, Literal, Tuple, Protocol
from datetime import datetime
import json
import sys
import inspect
import importlib

# Import functional programming utilities
from returns.result import Result, Success, Failure
from returns.maybe import Maybe, Some, Nothing
from returns.functions import tap
from toolz import pipe, compose, curry, memoize

# Import existing types
from ..plugin import Plugin, PluginEntryPoint, BasePluginValidator
from ..version_handler import VersionHandler
from .grammar_plugin_validator import GrammarPluginValidator
from ..semantic_construct_plugin_validator import SemanticConstructPluginValidator
from .generic_plugin_validator import GenericPluginValidator

# =======================
# Domain Types (Rule 3: Maximize Disclosure via Type System)
# =======================

PluginId = NewType("PluginId", str)
ModulePath = NewType("ModulePath", str)
ClassName = NewType("ClassName", str)
ManifestPath = NewType("ManifestPath", Path)
PluginDirectory = NewType("PluginDirectory", Path)
ErrorCode = NewType("ErrorCode", str)
ErrorMessage = NewType("ErrorMessage", str)
VersionString = NewType("VersionString", str)
PluginType = Literal["grammar_definition", "semantic_construct", "module", "cli", "generic"]

@dataclass(frozen=True)
class PluginError:
    """Immutable plugin error with structured information."""
    code: ErrorCode
    message: ErrorMessage
    plugin_id: Optional[PluginId] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return f"[{self.timestamp.isoformat()}] {self.code} (Plugin: {self.plugin_id or 'N/A'}): {self.message}"

@dataclass(frozen=True)
class ValidationResult:
    """Result of plugin validation."""
    success: bool
    config: Dict[str, Any] = field(default_factory=dict)
    errors: List[ErrorMessage] = field(default_factory=list)

@dataclass(frozen=True)
class LoadResult:
    """Result of plugin loading operation."""
    success: bool
    plugin: Optional[Plugin] = None
    error: Optional[PluginError] = None

@dataclass(frozen=True)
class ImportResult:
    """Result of module import operation."""
    success: bool
    module: Optional[Any] = None
    error: Optional[PluginError] = None

@dataclass(frozen=True)
class InstantiationResult:
    """Result of plugin instantiation."""
    success: bool
    instance: Optional[Any] = None
    error: Optional[PluginError] = None

# Type helpers for Result monad
from typing import TypeVar

T = TypeVar('T')

# =======================
# Infrastructure Layer (Rule 4: Isolate Impurity)
# =======================

class ManifestFileRepository:
    """Handles all manifest file I/O operations."""
    
    @staticmethod
    def scan_for_manifests(directory: PluginDirectory) -> Result[List[ManifestPath], PluginError]:
        """Scan directory recursively for manifest.json files."""
        try:
            if not directory.exists() or not directory.is_dir():
                return Failure(PluginError(
                    code=ErrorCode("INVALID_DIRECTORY"),
                    message=ErrorMessage(f"Directory {directory} does not exist or is not a directory")
                ))
            
            manifests = [ManifestPath(p) for p in directory.rglob("manifest.json")]
            return Success(manifests)
        except Exception as e:
            return Failure(PluginError(
                code=ErrorCode("SCAN_ERROR"),
                message=ErrorMessage(f"Error scanning directory: {e}")
            ))
    
    @staticmethod
    def read_manifest(path: ManifestPath) -> Result[Dict[str, Any], PluginError]:
        """Read and parse manifest JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Success(data)
        except FileNotFoundError:
            return Failure(PluginError(
                code=ErrorCode("MANIFEST_NOT_FOUND"),
                message=ErrorMessage(f"Manifest not found: {path}")
            ))
        except json.JSONDecodeError as e:
            return Failure(PluginError(
                code=ErrorCode("MANIFEST_MALFORMED"),
                message=ErrorMessage(f"Invalid JSON in {path}: {e}")
            ))
        except Exception as e:
            return Failure(PluginError(
                code=ErrorCode("MANIFEST_READ_ERROR"),
                message=ErrorMessage(f"Error reading {path}: {e}")
            ))
    
    @staticmethod
    def load_schema(schema_path: Path) -> Result[Dict[str, Any], PluginError]:
        """Load plugin manifest schema."""
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            return Success(schema)
        except Exception as e:
            return Failure(PluginError(
                code=ErrorCode("SCHEMA_LOAD_ERROR"),
                message=ErrorMessage(f"Failed to load schema: {e}")
            ))

class ModuleImporter:
    """Handles Python module importing operations."""
    
    @staticmethod
    def import_plugin_module(
        module_path: ModulePath,
        plugin_dir: PluginDirectory,
        plugin_id: PluginId
    ) -> Result[Any, PluginError]:
        """Import plugin module with sys.path management."""
        module_name = ModuleImporter._prepare_module_name(module_path)
        original_path = list(sys.path)
        
        try:
            sys.path.insert(0, str(plugin_dir.resolve()))
            return ModuleImporter._perform_import(module_name, module_path, plugin_dir, plugin_id)
        finally:
            sys.path[:] = original_path
    
    @staticmethod
    def _prepare_module_name(module_path: ModulePath) -> str:
        """Convert module path to importable name."""
        name = str(module_path)
        return name[:-3] if name.endswith('.py') else name
    
    @staticmethod
    def _perform_import(
        module_name: str,
        module_path: ModulePath,
        plugin_dir: PluginDirectory,
        plugin_id: PluginId
    ) -> Result[Any, PluginError]:
        """Perform the actual import with cache management."""
        expected_path = (plugin_dir / module_path).resolve()
        
        if module_name in sys.modules:
            result = ModuleImporter._handle_cached_module(module_name, expected_path, plugin_id)
            if isinstance(result, Failure):
                return result
        
        try:
            module = importlib.import_module(module_name)
            return Success(module)
        except ImportError as e:
            return Failure(PluginError(
                code=ErrorCode("IMPORT_ERROR"),
                message=ErrorMessage(f"Failed to import {module_name}: {e}"),
                plugin_id=plugin_id
            ))
        except Exception as e:
            return Failure(PluginError(
                code=ErrorCode("IMPORT_UNEXPECTED_ERROR"),
                message=ErrorMessage(f"Unexpected error importing {module_name}: {e}"),
                plugin_id=plugin_id
            ))
    
    @staticmethod
    def _handle_cached_module(
        module_name: str,
        expected_path: Path,
        plugin_id: PluginId
    ) -> Result[None, PluginError]:
        """Handle already-imported modules."""
        existing = sys.modules[module_name]
        existing_file = getattr(existing, '__file__', None)
        
        if existing_file and Path(existing_file).resolve() != expected_path:
            del sys.modules[module_name]
        
        return Success(None)

# =======================
# Core Business Logic (Pure Functions)
# =======================

class PluginValidator:
    """Validates plugin configurations."""
    
    def __init__(self, validators: Dict[str, BasePluginValidator]):
        self._validators = validators
    
    def validate_plugin(
        self,
        plugin: Plugin,
        manifest_data: Dict[str, Any],
        plugin_dir: PluginDirectory
    ) -> ValidationResult:
        """Validate plugin using appropriate validator."""
        plugin_type = manifest_data.get("plugin_type")
        
        if not plugin_type:
            return ValidationResult(
                success=False,
                errors=[ErrorMessage("Missing plugin_type in manifest")]
            )
        
        validator = self._get_validator_for_type(plugin_type)
        if not validator:
            return self._try_generic_validation(plugin, manifest_data, plugin_dir)
        
        return self._perform_validation(validator, manifest_data, plugin_dir, plugin_type)
    
    def _get_validator_for_type(self, plugin_type: str) -> Optional[BasePluginValidator]:
        """Get validator for plugin type."""
        return self._validators.get(plugin_type)
    
    def _perform_validation(
        self,
        validator: BasePluginValidator,
        manifest_data: Dict[str, Any],
        plugin_dir: PluginDirectory,
        plugin_type: str
    ) -> ValidationResult:
        """Perform type-specific validation."""
        try:
            is_valid, config, errors = validator.validate_manifest(manifest_data, plugin_dir)
            return ValidationResult(
                success=is_valid,
                config=config if is_valid else {},
                errors=[ErrorMessage(e) for e in errors]
            )
        except Exception as e:
            return ValidationResult(
                success=False,
                errors=[ErrorMessage(f"Validation exception: {e}")]
            )
    
    def _try_generic_validation(
        self,
        plugin: Plugin,
        manifest_data: Dict[str, Any],
        plugin_dir: PluginDirectory
    ) -> ValidationResult:
        """Try generic validation for unknown types."""
        generic_validator = self._validators.get("generic")
        if not generic_validator:
            return ValidationResult(
                success=False,
                errors=[ErrorMessage("No validator available for plugin type")]
            )
        
        return self._perform_validation(generic_validator, manifest_data, plugin_dir, "generic")

class VersionCompatibilityChecker:
    """Checks plugin version compatibility."""
    
    def __init__(self, version_handler: VersionHandler, core_version: VersionString):
        self._version_handler = version_handler
        self._core_version = core_version
        self._core_semver = version_handler.parse_semver(core_version, "Core ILR")
    
    def is_compatible(self, plugin: Plugin) -> Tuple[bool, List[ErrorMessage]]:
        """Check if plugin is compatible with core version."""
        if self._core_semver is None:
            return False, [ErrorMessage(f"Invalid core version: {self._core_version}")]
        
        is_compatible, errors = self._version_handler.check_ilr_compatibility(
            core_ilr_semver=self._core_semver,
            core_ilr_version_str=self._core_version,
            plugin=plugin
        )
        
        return is_compatible, [ErrorMessage(e) for e in errors]

class PluginInstantiator:
    """Handles plugin class instantiation."""
    
    @staticmethod
    def find_plugin_class(
        module: Any,
        class_name: ClassName,
        plugin_id: PluginId
    ) -> Result[Type[Any], PluginError]:
        """Find and validate plugin class in module."""
        try:
            plugin_class = getattr(module, class_name)
            if not inspect.isclass(plugin_class):
                return Failure(PluginError(
                    code=ErrorCode("NOT_A_CLASS"),
                    message=ErrorMessage(f"{class_name} is not a class"),
                    plugin_id=plugin_id
                ))
            return Success(plugin_class)
        except AttributeError:
            return Failure(PluginError(
                code=ErrorCode("CLASS_NOT_FOUND"),
                message=ErrorMessage(f"Class {class_name} not found in module"),
                plugin_id=plugin_id
            ))
        except Exception as e:
            return Failure(PluginError(
                code=ErrorCode("CLASS_LOOKUP_ERROR"),
                message=ErrorMessage(f"Error finding class: {e}"),
                plugin_id=plugin_id
            ))
    
    @staticmethod
    def prepare_init_args(
        plugin_class: Type[Any],
        default_args: Dict[str, Any],
        plugin_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare initialization arguments for plugin class."""
        try:
            sig = inspect.signature(plugin_class.__init__)
            available_params = set(sig.parameters.keys())
            
            combined_args = {**default_args, **plugin_config}
            
            return {
                name: value
                for name, value in combined_args.items()
                if name in available_params
            }
        except Exception:
            return {}
    
    @staticmethod
    def instantiate(
        plugin_class: Type[Any],
        init_args: Dict[str, Any],
        plugin_id: PluginId
    ) -> Result[Any, PluginError]:
        """Instantiate plugin class."""
        try:
            instance = plugin_class(**init_args)
            return Success(instance)
        except TypeError as e:
            return Failure(PluginError(
                code=ErrorCode("INSTANTIATION_TYPE_ERROR"),
                message=ErrorMessage(f"Type error in instantiation: {e}"),
                plugin_id=plugin_id
            ))
        except Exception as e:
            return Failure(PluginError(
                code=ErrorCode("INSTANTIATION_ERROR"),
                message=ErrorMessage(f"Failed to instantiate: {e}"),
                plugin_id=plugin_id
            ))

class PluginRegistry:
    """Manages plugin registration and storage."""
    
    def __init__(self):
        self._plugins: Dict[PluginId, Plugin] = {}
    
    def register(self, plugin: Plugin) -> Result[None, PluginError]:
        """Register a plugin."""
        plugin_id = PluginId(plugin.id)
        
        if plugin_id in self._plugins:
            return Failure(PluginError(
                code=ErrorCode("DUPLICATE_PLUGIN"),
                message=ErrorMessage(f"Plugin {plugin_id} already registered"),
                plugin_id=plugin_id
            ))
        
        self._plugins[plugin_id] = plugin
        return Success(None)
    
    def get(self, plugin_id: PluginId) -> Optional[Plugin]:
        """Get plugin by ID."""
        return self._plugins.get(plugin_id)
    
    def get_all(self) -> List[Plugin]:
        """Get all registered plugins."""
        return list(self._plugins.values())
    
    def clear(self) -> None:
        """Clear all plugins."""
        self._plugins.clear()

class ErrorCollector:
    """Collects and manages errors."""
    
    def __init__(self):
        self._errors: List[PluginError] = []
    
    def add_error(self, error: PluginError) -> None:
        """Add an error to the collection."""
        self._errors.append(error)
        logging.error(str(error))
    
    def get_errors(self) -> List[PluginError]:
        """Get all collected errors."""
        return self._errors.copy()
    
    def clear(self) -> None:
        """Clear all errors."""
        self._errors.clear()

# =======================
# Service Layer (Orchestration)
# =======================

class PluginDiscoveryService:
    """Orchestrates plugin discovery operations."""
    
    def __init__(
        self,
        manifest_repo: ManifestFileRepository,
        error_collector: ErrorCollector
    ):
        self._manifest_repo = manifest_repo
        self._error_collector = error_collector
    
    def discover_plugins_in_directory(
        self,
        directory: PluginDirectory
    ) -> List[Tuple[ManifestPath, Dict[str, Any]]]:
        """Discover all plugins in a directory."""
        manifests_result = self._manifest_repo.scan_for_manifests(directory)
        
        if isinstance(manifests_result, Failure):
            self._error_collector.add_error(manifests_result.failure())
            return []
        
        discovered = []
        for manifest_path in manifests_result.unwrap():
            manifest_data = self._load_manifest_data(manifest_path)
            if manifest_data:
                discovered.append((manifest_path, manifest_data))
        
        return discovered
    
    def _load_manifest_data(self, manifest_path: ManifestPath) -> Optional[Dict[str, Any]]:
        """Load manifest data from file."""
        result = self._manifest_repo.read_manifest(manifest_path)
        
        if isinstance(result, Failure):
            self._error_collector.add_error(result.failure())
            return None
        
        return result.unwrap()

class PluginLoadingService:
    """Orchestrates plugin loading operations."""
    
    def __init__(
        self,
        module_importer: ModuleImporter,
        instantiator: PluginInstantiator,
        error_collector: ErrorCollector
    ):
        self._module_importer = module_importer
        self._instantiator = instantiator
        self._error_collector = error_collector
    
    def load_plugin_instance(self, plugin: Plugin) -> Optional[Any]:
        """Load and instantiate plugin if needed."""
        if not self._requires_instantiation(plugin):
            return None
        
        entry_point = plugin.entry_point
        if not entry_point or not self._validate_entry_point(entry_point, plugin):
            return None
        
        plugin_dir = PluginDirectory(plugin.manifest_path.parent)
        module = self._import_module(entry_point.module_path, plugin_dir, plugin.id)
        if not module:
            return None
        
        return self._create_instance(module, entry_point.class_name, plugin)
    
    def _requires_instantiation(self, plugin: Plugin) -> bool:
        """Check if plugin requires instantiation."""
        if plugin.plugin_type == "grammar_definition":
            return False
        
        if not plugin.entry_point:
            return False
        
        return plugin.entry_point.type == 'module'
    
    def _validate_entry_point(self, entry_point: PluginEntryPoint, plugin: Plugin) -> bool:
        """Validate entry point has required fields."""
        if not entry_point.module_path or not entry_point.class_name:
            self._error_collector.add_error(PluginError(
                code=ErrorCode("INVALID_ENTRY_POINT"),
                message=ErrorMessage("Missing module_path or class_name"),
                plugin_id=PluginId(plugin.id)
            ))
            return False
        return True
    
    def _import_module(
        self,
        module_path: str,
        plugin_dir: PluginDirectory,
        plugin_id: str
    ) -> Optional[Any]:
        """Import plugin module."""
        result = self._module_importer.import_plugin_module(
            ModulePath(module_path),
            plugin_dir,
            PluginId(plugin_id)
        )
        
        if isinstance(result, Failure):
            self._error_collector.add_error(result.failure())
            return None
        
        return result.unwrap()
    
    def _create_instance(
        self,
        module: Any,
        class_name: str,
        plugin: Plugin
    ) -> Optional[Any]:
        """Create plugin instance from module."""
        class_result = self._instantiator.find_plugin_class(
            module,
            ClassName(class_name),
            PluginId(plugin.id)
        )
        
        if isinstance(class_result, Failure):
            self._error_collector.add_error(class_result.failure())
            return None
        
        init_args = self._instantiator.prepare_init_args(
            class_result.unwrap(),
            plugin.entry_point.default_init_args or {},
            plugin.plugin_specific_config or {}
        )
        
        instance_result = self._instantiator.instantiate(
            class_result.unwrap(),
            init_args,
            PluginId(plugin.id)
        )
        
        if isinstance(instance_result, Failure):
            self._error_collector.add_error(instance_result.failure())
            return None
        
        return instance_result.unwrap()

# =======================
# Main Plugin Manager (Orchestration Only)
# =======================

class PluginManager:
    """Plugin manager orchestrating all plugin operations."""
    
    def __init__(
        self,
        plugin_dirs: Union[str, List[str], Path, List[Path]],
        core_ilr_version: str = "1.0.0",
        default_init_args: Optional[Dict[str, Any]] = None
    ):
        """Initialize plugin manager with directories and configuration."""
        # Initialize infrastructure
        self._error_collector = ErrorCollector()
        self._registry = PluginRegistry()
        
        # Initialize configuration
        self._plugin_roots = self._prepare_plugin_roots(plugin_dirs)
        self._core_version = VersionString(core_ilr_version)
        self._default_init_args = default_init_args or {}
        
        # Initialize services
        self._initialize_services()
    
    def _prepare_plugin_roots(
        self,
        plugin_dirs: Union[str, List[str], Path, List[Path]]
    ) -> List[PluginDirectory]:
        """Prepare plugin root directories."""
        if isinstance(plugin_dirs, (str, Path)):
            return [PluginDirectory(Path(plugin_dirs))]
        elif isinstance(plugin_dirs, list):
            return [PluginDirectory(Path(p)) for p in plugin_dirs]
        else:
            raise TypeError("plugin_dirs must be a string, Path, or list")
    
    def _initialize_services(self) -> None:
        """Initialize all services."""
        # Version handling
        version_handler = VersionHandler()
        self._version_checker = VersionCompatibilityChecker(version_handler, self._core_version)
        
        # Validators
        validators = self._create_validators()
        self._plugin_validator = PluginValidator(validators)
        
        # Discovery and loading
        manifest_repo = ManifestFileRepository()
        self._discovery_service = PluginDiscoveryService(manifest_repo, self._error_collector)
        
        module_importer = ModuleImporter()
        instantiator = PluginInstantiator()
        self._loading_service = PluginLoadingService(
            module_importer,
            instantiator,
            self._error_collector
        )
    
    def _create_validators(self) -> Dict[str, BasePluginValidator]:
        """Create plugin validators."""
        return {
            "grammar_definition": GrammarPluginValidator(self._core_version, logging.getLogger()),
            "semantic_construct": SemanticConstructPluginValidator(self._core_version, logging.getLogger()),
            "generic": GenericPluginValidator(self._core_version, logging.getLogger())
        }
    
    def discover_plugins(self) -> Dict[str, Plugin]:
        """Discover and load all plugins."""
        self._registry.clear()
        self._error_collector.clear()
        
        for plugin_root in self._plugin_roots:
            self._discover_in_directory(plugin_root)
        
        return {p.id: p for p in self._registry.get_all()}
    
    def _discover_in_directory(self, directory: PluginDirectory) -> None:
        """Discover plugins in a single directory."""
        discovered = self._discovery_service.discover_plugins_in_directory(directory)
        
        for manifest_path, manifest_data in discovered:
            self._process_discovered_plugin(manifest_path, manifest_data)
    
    def _process_discovered_plugin(
        self,
        manifest_path: ManifestPath,
        manifest_data: Dict[str, Any]
    ) -> None:
        """Process a discovered plugin."""
        plugin = self._create_plugin_from_manifest(manifest_path, manifest_data)
        if not plugin:
            return
        
        if not self._validate_and_prepare_plugin(plugin, manifest_data):
            return
        
        self._register_plugin(plugin)
    
    def _create_plugin_from_manifest(
        self,
        manifest_path: ManifestPath,
        manifest_data: Dict[str, Any]
    ) -> Optional[Plugin]:
        """Create plugin object from manifest."""
        try:
            plugin_dir = PluginDirectory(manifest_path.parent)
            plugin = Plugin.from_manifest(manifest_data, manifest_path, plugin_dir)
            return plugin
        except Exception as e:
            self._error_collector.add_error(PluginError(
                code=ErrorCode("PLUGIN_CREATION_ERROR"),
                message=ErrorMessage(f"Failed to create plugin: {e}")
            ))
            return None
    
    def _validate_and_prepare_plugin(
        self,
        plugin: Plugin,
        manifest_data: Dict[str, Any]
    ) -> bool:
        """Validate and prepare plugin for registration."""
        # Validate manifest
        plugin_dir = PluginDirectory(plugin.manifest_path.parent)
        validation_result = self._plugin_validator.validate_plugin(plugin, manifest_data, plugin_dir)
        
        if not validation_result.success:
            for error_msg in validation_result.errors:
                self._error_collector.add_error(PluginError(
                    code=ErrorCode("VALIDATION_ERROR"),
                    message=error_msg,
                    plugin_id=PluginId(plugin.id)
                ))
            return False
        
        plugin.plugin_specific_config = validation_result.config
        
        # Check version compatibility
        is_compatible, errors = self._version_checker.is_compatible(plugin)
        if not is_compatible:
            for error_msg in errors:
                self._error_collector.add_error(PluginError(
                    code=ErrorCode("VERSION_INCOMPATIBLE"),
                    message=error_msg,
                    plugin_id=PluginId(plugin.id)
                ))
            return False
        
        # Load instance if needed
        instance = self._loading_service.load_plugin_instance(plugin)
        plugin.instance = instance
        
        return True
    
    def _register_plugin(self, plugin: Plugin) -> None:
        """Register plugin in registry."""
        result = self._registry.register(plugin)
        if isinstance(result, Failure):
            self._error_collector.add_error(result.failure())
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get plugin by ID."""
        return self._registry.get(PluginId(plugin_id))
    
    def get_all_plugins(self) -> List[Plugin]:
        """Get all loaded plugins."""
        return self._registry.get_all()
    
    def get_errors(self) -> List[PluginError]:
        """Get all errors encountered."""
        return self._error_collector.get_errors()
    
    def invoke_translation(self, plugin_id: str, tau_source: str) -> Optional[Dict[str, Any]]:
        """Invoke translation on a plugin."""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            self._error_collector.add_error(PluginError(
                code=ErrorCode("PLUGIN_NOT_FOUND"),
                message=ErrorMessage(f"Plugin {plugin_id} not found"),
                plugin_id=PluginId(plugin_id)
            ))
            return None
        
        return self._invoke_plugin_method(plugin, tau_source)
    
    def _invoke_plugin_method(self, plugin: Plugin, tau_source: str) -> Optional[Dict[str, Any]]:
        """Invoke translate_to_ilr method on plugin."""
        if not plugin.instance:
            self._error_collector.add_error(PluginError(
                code=ErrorCode("NO_INSTANCE"),
                message=ErrorMessage("Plugin has no instance"),
                plugin_id=PluginId(plugin.id)
            ))
            return None
        
        translate_method = getattr(plugin.instance, 'translate_to_ilr', None)
        if not callable(translate_method):
            self._error_collector.add_error(PluginError(
                code=ErrorCode("NO_TRANSLATE_METHOD"),
                message=ErrorMessage("Plugin missing translate_to_ilr method"),
                plugin_id=PluginId(plugin.id)
            ))
            return None
        
        try:
            return translate_method(tau_source)
        except Exception as e:
            self._error_collector.add_error(PluginError(
                code=ErrorCode("TRANSLATION_ERROR"),
                message=ErrorMessage(f"Translation failed: {e}"),
                plugin_id=PluginId(plugin.id)
            ))
            return None