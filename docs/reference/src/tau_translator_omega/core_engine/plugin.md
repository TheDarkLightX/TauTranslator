Module src.tau_translator_omega.core_engine.plugin
==================================================

Classes
-------

`BasePluginValidator(core_ilr_version: str, logger)`
:   Base class for plugin manifest validators.
    
    Initializes the base validator.
    
    Args:
        core_ilr_version: The core ILR version string.
        logger: The logger instance.

    ### Descendants

    * src.tau_translator_omega.core_engine.plugins.generic_plugin_validator.GenericPluginValidator
    * src.tau_translator_omega.core_engine.plugins.grammar_plugin_validator.GrammarPluginValidator
    * src.tau_translator_omega.core_engine.plugins.grammar_plugin_validator_v2.GrammarPluginValidatorV2
    * src.tau_translator_omega.core_engine.semantic_construct_plugin_validator.SemanticConstructPluginValidator

    ### Methods

    `validate_manifest(self, manifest_data: Dict[str, Any], plugin_dir: pathlib.Path) ‑> Tuple[bool, List[str]]`
    :   Validates a plugin manifest.
        
        This method should be implemented by subclasses for specific plugin types.
        
        Args:
            manifest_data: The plugin manifest data as a dictionary.
            plugin_dir: The Path object representing the plugin's base directory.
        
        Returns:
            A tuple (is_valid, errors_list).

`Plugin(id: str, name: str, version: str, description: str, entry_point: src.tau_translator_omega.core_engine.plugin.PluginEntryPoint, manifest_path: pathlib.Path, plugin_dir: pathlib.Path, manifest_data: Dict[str, Any], plugin_type: str = 'generic', ilr_versions_supported: List[str] = <factory>, manifest_version: str = '1.0', author: str | None = None, license: str | None = None, tags: List[str] = <factory>, dependencies: List[str] = <factory>, target_grammar: src.tau_translator_omega.core_engine.plugin.PluginTargetGrammar | None = None, output_details: src.tau_translator_omega.core_engine.plugin.PluginOutputDetails | None = None, configuration_schema: Dict[str, Any] | None = None, default_init_args: Dict[str, Any] | None = None, instance: Any | None = None, ilr_versions_parse_error: str | None = None, plugin_specific_config: Dict[str, Any] = <factory>)`
:   Represents a discovered plugin and its metadata.

    ### Static methods

    `from_manifest(manifest_data: Dict[str, Any], manifest_path: pathlib.Path, plugin_dir: pathlib.Path) ‑> src.tau_translator_omega.core_engine.plugin.Plugin`
    :   Creates a Plugin instance from manifest data.

    ### Instance variables

    `author: str | None`
    :

    `configuration_schema: Dict[str, Any] | None`
    :

    `default_init_args: Dict[str, Any] | None`
    :

    `dependencies: List[str]`
    :

    `description: str`
    :

    `entry_point: src.tau_translator_omega.core_engine.plugin.PluginEntryPoint`
    :

    `id: str`
    :

    `ilr_versions_parse_error: str | None`
    :

    `ilr_versions_supported: List[str]`
    :

    `instance: Any | None`
    :

    `license: str | None`
    :

    `manifest_data: Dict[str, Any]`
    :

    `manifest_path: pathlib.Path`
    :

    `manifest_version: str`
    :

    `name: str`
    :

    `output_details: src.tau_translator_omega.core_engine.plugin.PluginOutputDetails | None`
    :

    `plugin_dir: pathlib.Path`
    :

    `plugin_specific_config: Dict[str, Any]`
    :

    `plugin_type: str`
    :

    `tags: List[str]`
    :

    `target_grammar: src.tau_translator_omega.core_engine.plugin.PluginTargetGrammar | None`
    :

    `version: str`
    :

`PluginEntryPoint(type: str, module_path: str | None = None, class_name: str | None = None, command: str | None = None, url: str | None = None, default_init_args: Dict[str, Any] | None = None)`
:   Defines the entry point for a plugin.

    ### Instance variables

    `class_name: str | None`
    :

    `command: str | None`
    :

    `default_init_args: Dict[str, Any] | None`
    :

    `module_path: str | None`
    :

    `type: str`
    :

    `url: str | None`
    :

`PluginOutputDetails(format_mime_type: str, file_extension_suggestion: str | None = None)`
:   Defines the output details for a plugin.

    ### Instance variables

    `file_extension_suggestion: str | None`
    :

    `format_mime_type: str`
    :

`PluginTargetGrammar(grammar_name: str, version_constraint: str | None = None)`
:   Defines the target grammar details for a plugin.

    ### Instance variables

    `grammar_name: str`
    :

    `version_constraint: str | None`
    :