Module src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers
====================================================================
ILR Pattern Handlers
====================

Handles specific pattern translations for the ILR translator.
Extracted to reduce complexity and improve maintainability.

Author: DarkLightX/Dana Edwards

Classes
-------

`AssignmentHandler()`
:   Handles assignment patterns.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.PatternHandler
    * abc.ABC

    ### Methods

    `analyze(self, text: str) ‑> Dict[str, Any]`
    :   Extract variable and value.

    `can_handle(self, text: str) ‑> bool`
    :   Check for assignment pattern.

    `generate_ilr(self, data: Dict[str, Any]) ‑> Dict[str, Any]`
    :   Generate ILR for assignment.

`BooleanOperationHandler()`
:   Handles boolean operation patterns.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.PatternHandler
    * abc.ABC

    ### Methods

    `analyze(self, text: str) ‑> Dict[str, Any]`
    :   Extract operator and operands.

    `can_handle(self, text: str) ‑> bool`
    :   Check for boolean operation pattern.

    `generate_ilr(self, data: Dict[str, Any]) ‑> Dict[str, Any]`
    :   Generate ILR for boolean operation.

`ConditionalHandler()`
:   Handles conditional patterns (if-then-else).

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.PatternHandler
    * abc.ABC

    ### Methods

    `analyze(self, text: str) ‑> Dict[str, Any]`
    :   Extract condition, then branch, and optional else branch.

    `can_handle(self, text: str) ‑> bool`
    :   Check for conditional pattern.

    `generate_ilr(self, data: Dict[str, Any]) ‑> Dict[str, Any]`
    :   Generate ILR for conditional.

`PatternHandler()`
:   Abstract base class for pattern handlers.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.AssignmentHandler
    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.BooleanOperationHandler
    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.ConditionalHandler
    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.SBFInputHandler
    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.SBFOutputHandler
    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.StreamRuleHandler
    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.TemporalAlwaysHandler

    ### Methods

    `analyze(self, text: str) ‑> Dict[str, Any]`
    :   Analyze the text and extract relevant data.

    `can_handle(self, text: str) ‑> bool`
    :   Check if this handler can process the given text.

    `generate_ilr(self, data: Dict[str, Any]) ‑> Dict[str, Any]`
    :   Generate ILR structure from analyzed data.

`PatternHandlerRegistry()`
:   Registry for pattern handlers.
    
    Initialize with default handlers.

    ### Methods

    `find_handler(self, text: str) ‑> src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.PatternHandler | None`
    :   Find appropriate handler for the given text.

    `register_handler(self, handler: src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.PatternHandler)`
    :   Register a new pattern handler.

`SBFInputHandler()`
:   Handles SBF input patterns like 'SBF X takes Y'.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.PatternHandler
    * abc.ABC

    ### Methods

    `analyze(self, text: str) ‑> Dict[str, Any]`
    :   Extract SBF name and input variable.

    `can_handle(self, text: str) ‑> bool`
    :   Check for SBF input pattern.

    `generate_ilr(self, data: Dict[str, Any]) ‑> Dict[str, Any]`
    :   Generate ILR for SBF input declaration.

`SBFOutputHandler()`
:   Handles SBF output patterns like 'SBF X produces Y'.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.PatternHandler
    * abc.ABC

    ### Methods

    `analyze(self, text: str) ‑> Dict[str, Any]`
    :   Extract SBF name and output variable.

    `can_handle(self, text: str) ‑> bool`
    :   Check for SBF output pattern.

    `generate_ilr(self, data: Dict[str, Any]) ‑> Dict[str, Any]`
    :   Generate ILR for SBF output declaration.

`StreamRuleHandler()`
:   Handles stream rule patterns.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.PatternHandler
    * abc.ABC

    ### Methods

    `analyze(self, text: str) ‑> Dict[str, Any]`
    :   Extract stream name and expression.

    `can_handle(self, text: str) ‑> bool`
    :   Check for stream rule pattern.

    `generate_ilr(self, data: Dict[str, Any]) ‑> Dict[str, Any]`
    :   Generate ILR for stream rule.

`TemporalAlwaysHandler()`
:   Handles temporal always patterns.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.core_engine.ilr.ilr_pattern_handlers.PatternHandler
    * abc.ABC

    ### Methods

    `analyze(self, text: str) ‑> Dict[str, Any]`
    :   Extract the condition.

    `can_handle(self, text: str) ‑> bool`
    :   Check for temporal always pattern.

    `generate_ilr(self, data: Dict[str, Any]) ‑> Dict[str, Any]`
    :   Generate ILR for temporal always.