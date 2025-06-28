Module src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored
=============================================================================
Plugin Manager following the Intentional Disclosure Principle.

This module orchestrates plugin operations with complete transparency:
- All I/O operations explicitly isolated in repositories
- Domain types replace primitive obsession
- Business logic separated from infrastructure
- Every method under 10 lines with single responsibility

Copyright: DarkLightX / Dana Edwards

Classes
-------

`ErrorCollector()`
:   Collects and manages errors.

    ### Methods

    `add_error(self, error: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError) ‑> None`
    :   Add an error to the collection.

    `clear(self) ‑> None`
    :   Clear all errors.

    `get_errors(self) ‑> List[src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError]`
    :   Get all collected errors.

`ImportResult(success: bool, module: Any | None = None, error: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError | None = None)`
:   Result of module import operation.

    ### Instance variables

    `error: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError | None`
    :

    `module: Any | None`
    :

    `success: bool`
    :

`InstantiationResult(success: bool, instance: Any | None = None, error: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError | None = None)`
:   Result of plugin instantiation.

    ### Instance variables

    `error: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError | None`
    :

    `instance: Any | None`
    :

    `success: bool`
    :

`LoadResult(success: bool, plugin: src.tau_translator_omega.core_engine.plugin.Plugin | None = None, error: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError | None = None)`
:   Result of plugin loading operation.

    ### Instance variables

    `error: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError | None`
    :

    `plugin: src.tau_translator_omega.core_engine.plugin.Plugin | None`
    :

    `success: bool`
    :

`ManifestFileRepository()`
:   Handles all manifest file I/O operations.

    ### Static methods

    `load_schema(schema_path: pathlib.Path) ‑> returns.result.Result[typing.Dict[str, typing.Any], src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError]`
    :   Load plugin manifest schema.

    `read_manifest(path: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ManifestPath) ‑> returns.result.Result[typing.Dict[str, typing.Any], src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError]`
    :   Read and parse manifest JSON file.

    `scan_for_manifests(directory: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginDirectory) ‑> returns.result.Result[typing.List[src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ManifestPath], src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError]`
    :   Scan directory recursively for manifest.json files.

`ModuleImporter()`
:   Handles Python module importing operations.

    ### Static methods

    `import_plugin_module(module_path: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ModulePath, plugin_dir: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginDirectory, plugin_id: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginId) ‑> returns.result.Result[typing.Any, src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError]`
    :   Import plugin module with sys.path management.

`PluginDiscoveryService(manifest_repo: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ManifestFileRepository, error_collector: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ErrorCollector)`
:   Orchestrates plugin discovery operations.

    ### Methods

    `discover_plugins_in_directory(self, directory: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginDirectory) ‑> List[Tuple[src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ManifestPath, Dict[str, Any]]]`
    :   Discover all plugins in a directory.

`PluginError(code: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ErrorCode, message: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ErrorMessage, plugin_id: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginId | None = None, timestamp: datetime.datetime = <factory>)`
:   Immutable plugin error with structured information.

    ### Instance variables

    `code: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ErrorCode`
    :

    `message: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ErrorMessage`
    :

    `plugin_id: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginId | None`
    :

    `timestamp: datetime.datetime`
    :

`PluginInstantiator()`
:   Handles plugin class instantiation.

    ### Static methods

    `find_plugin_class(module: Any, class_name: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ClassName, plugin_id: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginId) ‑> returns.result.Result[typing.Type[typing.Any], src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError]`
    :   Find and validate plugin class in module.

    `instantiate(plugin_class: Type[Any], init_args: Dict[str, Any], plugin_id: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginId) ‑> returns.result.Result[typing.Any, src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError]`
    :   Instantiate plugin class.

    `prepare_init_args(plugin_class: Type[Any], default_args: Dict[str, Any], plugin_config: Dict[str, Any]) ‑> Dict[str, Any]`
    :   Prepare initialization arguments for plugin class.

`PluginLoadingService(module_importer: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ModuleImporter, instantiator: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginInstantiator, error_collector: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ErrorCollector)`
:   Orchestrates plugin loading operations.

    ### Methods

    `load_plugin_instance(self, plugin: src.tau_translator_omega.core_engine.plugin.Plugin) ‑> Any | None`
    :   Load and instantiate plugin if needed.

`PluginManager(plugin_dirs: str | List[str] | pathlib.Path | List[pathlib.Path], core_ilr_version: str = '1.0.0', default_init_args: Dict[str, Any] | None = None)`
:   Plugin manager orchestrating all plugin operations.
    
    Initialize plugin manager with directories and configuration.

    ### Methods

    `discover_plugins(self) ‑> Dict[str, src.tau_translator_omega.core_engine.plugin.Plugin]`
    :   Discover and load all plugins.

    `get_all_plugins(self) ‑> List[src.tau_translator_omega.core_engine.plugin.Plugin]`
    :   Get all loaded plugins.

    `get_errors(self) ‑> List[src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError]`
    :   Get all errors encountered.

    `get_plugin(self, plugin_id: str) ‑> src.tau_translator_omega.core_engine.plugin.Plugin | None`
    :   Get plugin by ID.

    `invoke_translation(self, plugin_id: str, tau_source: str) ‑> Dict[str, Any] | None`
    :   Invoke translation on a plugin.

`PluginRegistry()`
:   Manages plugin registration and storage.

    ### Methods

    `clear(self) ‑> None`
    :   Clear all plugins.

    `get(self, plugin_id: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginId) ‑> src.tau_translator_omega.core_engine.plugin.Plugin | None`
    :   Get plugin by ID.

    `get_all(self) ‑> List[src.tau_translator_omega.core_engine.plugin.Plugin]`
    :   Get all registered plugins.

    `register(self, plugin: src.tau_translator_omega.core_engine.plugin.Plugin) ‑> returns.result.Result[None, src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginError]`
    :   Register a plugin.

`PluginValidator(validators: Dict[str, src.tau_translator_omega.core_engine.plugin.BasePluginValidator])`
:   Validates plugin configurations.

    ### Methods

    `validate_plugin(self, plugin: src.tau_translator_omega.core_engine.plugin.Plugin, manifest_data: Dict[str, Any], plugin_dir: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.PluginDirectory) ‑> src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ValidationResult`
    :   Validate plugin using appropriate validator.

`ValidationResult(success: bool, config: Dict[str, Any] = <factory>, errors: List[src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ErrorMessage] = <factory>)`
:   Result of plugin validation.

    ### Instance variables

    `config: Dict[str, Any]`
    :

    `errors: List[src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ErrorMessage]`
    :

    `success: bool`
    :

`VersionCompatibilityChecker(version_handler: src.tau_translator_omega.core_engine.version_handler.VersionHandler, core_version: src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.VersionString)`
:   Checks plugin version compatibility.

    ### Methods

    `is_compatible(self, plugin: src.tau_translator_omega.core_engine.plugin.Plugin) ‑> Tuple[bool, List[src.tau_translator_omega.core_engine.plugins.plugin_manager_refactored.ErrorMessage]]`
    :   Check if plugin is compatible with core version.