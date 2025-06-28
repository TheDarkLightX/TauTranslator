Module src.tau_translator_omega.core_engine.tgf_preprocessor
============================================================

Classes
-------

`TGFPreprocessor(initial_input: str | pathlib.Path, base_path: pathlib.Path | None = None)`
:   

    ### Class variables

    `IDENTIFIER_RE`
    :

    `MAX_MACRO_EXPANSION_DEPTH`
    :

    ### Methods

    `is_current_block_active(self) ‑> bool`
    :   Determines if the current lines should be processed or skipped based on conditional directives.

    `preprocess(self, input_content: str | pathlib.Path | None = None, base_path_override: pathlib.Path | None = None) ‑> str`
    :   Main method to preprocess the TGF input and return the final Lark grammar string.

    `to_lark(self, current_input_source: str | pathlib.Path) ‑> str`
    :   Converts the TGF input (after macro expansion and directive handling) to a Lark-compatible grammar string.