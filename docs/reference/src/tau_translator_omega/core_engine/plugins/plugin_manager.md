Module src.tau_translator_omega.core_engine.plugins.plugin_manager
==================================================================

Classes
-------

`PluginError(code: str, message: str, plugin_id: str | None = None, timestamp: str = <factory>)`
:   Represents a structured error encountered by the PluginManager.

    ### Instance variables

    `code: str`
    :

    `message: str`
    :

    `plugin_id: str | None`
    :

    `timestamp: str`
    :

`PluginManager(plugin_dirs: str | List[str] | pathlib.Path | List[pathlib.Path], core_ilr_version: str = '1.0.0', default_init_args: Dict[str, Any] | None = None)`
:   Manages discovery, loading, and interaction with plugins.
    
    Initialize PluginManager with plugin directories and configuration.

    ### Class variables

    `CORE_ILR_VERSION`
    :

    ### Methods

    `discover_plugins(self)`
    :   Discovers plugins from the specified directories.

    `get_all_plugins(self) ‑> List[src.tau_translator_omega.core_engine.plugin.Plugin]`
    :

    `get_errors(self) ‑> List[src.tau_translator_omega.core_engine.plugins.plugin_manager.PluginError]`
    :

    `get_plugin(self, plugin_id: str) ‑> src.tau_translator_omega.core_engine.plugin.Plugin | None`
    :

    `invoke_translation(self, plugin_id: str, tau_source: str) ‑> Dict[str, Any] | None`
    :

`ValidationResult(success: bool, config: Dict[str, Any] = <factory>, errors: List[str] = <factory>)`
:   Result of plugin validation with success status and configuration.

    ### Instance variables

    `config: Dict[str, Any]`
    :

    `errors: List[str]`
    :

    `success: bool`
    :