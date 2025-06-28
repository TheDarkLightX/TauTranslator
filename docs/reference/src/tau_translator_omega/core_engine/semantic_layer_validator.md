Module src.tau_translator_omega.core_engine.semantic_layer_validator
====================================================================

Classes
-------

`SemanticLayerValidator(project_root_path: str)`
:   

    ### Methods

    `get_schema_by_key(self, key: str)`
    :   Helper to get a schema by its short key (e.g., 'concept') if needed.

    `validate_plugin_semantic_layer(self, plugin_manifest: dict, plugin_root_path: str) ‑> tuple[bool, dict, list[str]]`
    :