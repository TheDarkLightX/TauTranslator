Module src.tau_translator_omega.core_engine.plugins.generic_plugin_validator
============================================================================

Classes
-------

`GenericPluginValidator(core_ilr_version: str, logger, schema_path: pathlib.Path | None = None)`
:   Validator for 'generic' plugin types.
    
    Initializes the GenericPluginValidator.
    
    Args:
        core_ilr_version: The core ILR version string.
        logger: The logger instance.
        schema_path: Optional path to a specific JSON schema for generic plugins.
                     If None, no specific schema validation beyond the main one is performed.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.plugin.BasePluginValidator

    ### Methods

    `validate_manifest(self, manifest_data: Dict[str, Any], plugin_dir: pathlib.Path) ‑> Tuple[bool, Dict[str, Any], List[str]]`
    :   Validates a 'generic' plugin manifest.
        
        For generic plugins, this implementation assumes that the main manifest schema
        validation (performed by PluginManager._process_manifest before calling this)
        is largely sufficient. This method can be expanded to include checks
        specific to the 'generic' plugin type if any arise.
        
        Args:
            manifest_data: The plugin manifest data as a dictionary.
            plugin_dir: The Path object representing the plugin's base directory.
        
        Returns:
            A tuple (is_valid, parsed_config, errors_list).