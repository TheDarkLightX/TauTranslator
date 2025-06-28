Module src.tau_translator_omega.core_engine.utils.logging_config
================================================================
Centralized logging configuration for TauTranslatorOmega.

This module provides consistent logging setup across all components,
replacing debug print statements with proper structured logging.

Functions
---------

`get_component_logger(component_name: str) ‑> logging.Logger`
:   Get a logger for a specific component (convenience function).

Classes
-------

`TauLogger()`
:   Centralized logger factory for TauTranslatorOmega components.

    ### Static methods

    `configure(log_level: int = 20, log_file: pathlib.Path | None = None) ‑> None`
    :   Configure logging for the entire application.

    `get_logger(name: str) ‑> logging.Logger`
    :   Get a logger for a specific component.