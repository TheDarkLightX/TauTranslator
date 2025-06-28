Module src.tau_translator_omega.core_engine.parsers.parser.domain.error_recovery
================================================================================
Error recovery mechanisms for parser following the Intentional Disclosure Principle.

Implements various strategies for recovering from parse errors to provide
better error messages and continue parsing when possible.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`ErrorMessageBuilder()`
:   Builds helpful error messages with recovery hints.

    ### Methods

    `build_error_message(self, error: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseError, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext, recovery: src.tau_translator_omega.core_engine.parsers.parser.domain.types.RecoveryResult | None = None) ‑> str`
    :   Build comprehensive error message.

`ErrorRecoveryStrategy()`
:   Base class for error recovery strategies.
    Each strategy attempts to recover from specific error patterns.

    ### Descendants

    * src.tau_translator_omega.core_engine.parsers.parser.domain.error_recovery.TauSpecificRecovery

    ### Methods

    `attempt_recovery(self, error: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParseError, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> returns.result.Result[src.tau_translator_omega.core_engine.parsers.parser.domain.types.RecoveryResult, str]`
    :   Attempt to recover from parse error.

`IncrementalRecovery()`
:   Supports incremental parsing with error recovery.
    Maintains parse state for efficient re-parsing.
    
    Initialize incremental recovery.

    ### Methods

    `add_checkpoint(self, context: src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext) ‑> None`
    :   Add parsing checkpoint for recovery.

    `can_reuse_parse(self, start: int, end: int) ‑> bool`
    :   Check if parse results can be reused for range.

    `clear_checkpoints_after(self, position: int) ‑> None`
    :   Clear checkpoints after given position.

    `clear_error_regions(self) ‑> None`
    :   Clear all error regions.

    `find_recovery_checkpoint(self, error_position: int) ‑> src.tau_translator_omega.core_engine.parsers.parser.domain.types.ParserContext | None`
    :   Find best checkpoint for recovery.

    `mark_error_region(self, start: int, end: int) ‑> None`
    :   Mark region containing errors.

`TauSpecificRecovery()`
:   Recovery strategy specific to Tau language constructs.
    Handles Tau-specific error patterns.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.parsers.parser.domain.error_recovery.ErrorRecoveryStrategy