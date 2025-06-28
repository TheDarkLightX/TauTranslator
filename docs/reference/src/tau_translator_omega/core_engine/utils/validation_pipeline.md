Module src.tau_translator_omega.core_engine.utils.validation_pipeline
=====================================================================
Validation pipeline for plugin manifest processing.

This module implements a pipeline pattern for validating plugin manifests,
breaking down complex validation logic into focused, testable stages.

Classes
-------

`FileExistenceStage(file_fields: List[str])`
:   Validates that required files exist.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationStage
    * abc.ABC

    ### Methods

    `validate(self, context: src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationContext) ‑> src.tau_translator_omega.core_engine.utils.validation_pipeline.StageResult`
    :   Validate that required files exist.

`SchemaValidationStage(schema: Dict[str, Any] | None = None)`
:   Validates manifest against JSON schema.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationStage
    * abc.ABC

    ### Methods

    `validate(self, context: src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationContext) ‑> src.tau_translator_omega.core_engine.utils.validation_pipeline.StageResult`
    :   Validate manifest against JSON schema.

`StageResult(success: bool, data: Dict[str, Any] = <factory>, errors: List[str] = <factory>)`
:   Result of a validation stage.

    ### Static methods

    `failure_with_errors(errors: List[str]) ‑> src.tau_translator_omega.core_engine.utils.validation_pipeline.StageResult`
    :   Create a failed result with errors.

    `success_with_data(data: Dict[str, Any]) ‑> src.tau_translator_omega.core_engine.utils.validation_pipeline.StageResult`
    :   Create a successful result with data.

    ### Instance variables

    `data: Dict[str, Any]`
    :

    `errors: List[str]`
    :

    `success: bool`
    :

`ValidationContext(manifest_data: Dict[str, Any], plugin_dir: pathlib.Path, config: Dict[str, Any] = <factory>, errors: List[str] = <factory>, plugin_id: str | None = None)`
:   Context object passed through validation pipeline stages.

    ### Instance variables

    `config: Dict[str, Any]`
    :

    `errors: List[str]`
    :

    `manifest_data: Dict[str, Any]`
    :

    `plugin_dir: pathlib.Path`
    :

    `plugin_id: str | None`
    :

    ### Methods

    `add_error(self, error: str) ‑> None`
    :   Add an error to the context.

    `update_config(self, updates: Dict[str, Any]) ‑> None`
    :   Update the configuration with new values.

`ValidationPipeline(stages: List[src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationStage])`
:   Pipeline for running validation stages in sequence.

    ### Methods

    `validate(self, manifest_data: Dict[str, Any], plugin_dir: pathlib.Path) ‑> src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationContext`
    :   Run all validation stages and return the final context.

`ValidationStage(name: str)`
:   Abstract base class for validation pipeline stages.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.plugins.grammar_plugin_validator_v2.GrammarDetailsStage
    * src.tau_translator_omega.core_engine.plugins.grammar_plugin_validator_v2.ILRMappingsStage
    * src.tau_translator_omega.core_engine.utils.validation_pipeline.FileExistenceStage
    * src.tau_translator_omega.core_engine.utils.validation_pipeline.SchemaValidationStage

    ### Methods

    `validate(self, context: src.tau_translator_omega.core_engine.utils.validation_pipeline.ValidationContext) ‑> src.tau_translator_omega.core_engine.utils.validation_pipeline.StageResult`
    :   Validate the context and return a result.