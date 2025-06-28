Module src.tau_translator_omega.core_engine.semantic_construct_plugin_validator
===============================================================================

Classes
-------

`SemanticConstructPluginValidator(core_ilr_version: str, logger_instance: logging.Logger)`
:   Base class for plugin manifest validators.
    
    Initializes the base validator.
    
    Args:
        core_ilr_version: The core ILR version string.
        logger: The logger instance.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.plugin.BasePluginValidator

    ### Class variables

    `SUPPORTED_DPD_FORMATS`
    :

    `SUPPORTED_ILR_VERSIONS`
    :

    ### Methods

    `validate_manifest(self, manifest_data: Dict[str, Any], plugin_dir: pathlib.Path) ‑> Tuple[bool, Dict[str, Any], List[str]]`
    :   Validate semantic construct plugin manifest using modular validation approach.