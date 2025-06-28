Module src.tau_translator_omega.core_engine.plugins.grammar_plugin_validator_v2
===============================================================================
Refactored Grammar Plugin Validator using validation pipeline pattern.

This is a demonstration of how the validation pipeline can reduce complexity
and improve maintainability of the validation logic.

Functions
---------

`create_grammar_validator(core_ilr_version: str, logger: logging.Logger) ‑> src.tau_translator_omega.core_engine.plugins.grammar_plugin_validator_v2.GrammarPluginValidatorV2`
:   Create a new grammar plugin validator instance.

Classes
-------

`GrammarDetailsStage()`
:   Validates and extracts grammar-specific details.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationStage
    * abc.ABC

    ### Methods

    `validate(self, context: src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationContext) ‑> src.tau_translator_omega.core_engine.utils.validation_pipeline.StageResult`
    :   Validate grammar details and extract configuration.

`GrammarPluginValidatorV2(core_ilr_version: str, logger: logging.Logger)`
:   Refactored Grammar Plugin Validator using validation pipeline pattern.
    
    This demonstrates how complex validation logic can be broken down into
    focused, testable stages with clear separation of concerns.
    
    Initializes the base validator.
    
    Args:
        core_ilr_version: The core ILR version string.
        logger: The logger instance.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.plugin.BasePluginValidator

    ### Methods

    `validate_manifest(self, manifest_data: Dict[str, Any], plugin_dir: pathlib.Path) ‑> Tuple[bool, Dict[str, Any], List[str]]`
    :   Validate a grammar plugin manifest using the validation pipeline.
        
        Returns:
            Tuple of (is_valid, parsed_config, errors_list)

`ILRMappingsStage()`
:   Validates ILR construct mappings schema if present.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationStage
    * abc.ABC

    ### Methods

    `validate(self, context: src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationContext) ‑> src.tau_translator_omega.core_engine.utils.validation_pipeline.StageResult`
    :   Validate ILR mappings schema file if specified.