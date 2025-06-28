Module src.tau_translator_omega.core_engine.plugins.grammar_plugin_validator
============================================================================
Validates 'grammar_definition' type plugin manifests for TauTranslatorOmega
using a JSON schema.

Classes
-------

`GrammarPluginValidator(core_ilr_version: str, logger_instance)`
:   Validates the manifest of a 'grammar_definition' plugin against a JSON schema.
    
    Initializes the validator, loading the JSON schema.
    Args:
        core_ilr_version: The core ILR version string.
        logger_instance: The logger instance to use.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.plugin.BasePluginValidator

    ### Methods

    `validate_manifest(self, manifest_data: Dict[str, Any], plugin_dir: pathlib.Path) ‑> Tuple[bool, Dict[str, Any], List[str]]`
    :   Validates the provided manifest data against the loaded JSON schema and checks for grammar file existence.
        
        Args:
            manifest_data: The plugin manifest data as a dictionary.
            plugin_dir: The Path object representing the plugin's base directory.
        
        Returns:
            A tuple: (is_valid: bool, parsed_config: Dict[str, Any], errors: List[str])