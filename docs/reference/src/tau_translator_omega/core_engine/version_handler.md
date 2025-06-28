Module src.tau_translator_omega.core_engine.version_handler
===========================================================

Classes
-------

`VersionHandler()`
:   Handles semantic version parsing and compatibility checks.

    ### Methods

    `check_ilr_compatibility(self, core_ilr_semver: semver.version.Version | None, core_ilr_version_str: str, plugin: Any) ‑> Tuple[bool, List[str]]`
    :   Checks if the plugin's supported ILR versions are compatible with the core version.
        Relies on plugin object having 'id' and 'ilr_versions_supported: List[str]' attributes.
        Returns a tuple: (is_compatible: bool, error_messages: List[str]).

    `parse_semver(self, version_string: str | None, context: str, plugin_id: str | None = None) ‑> semver.version.Version | None`
    :