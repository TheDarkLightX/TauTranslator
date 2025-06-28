Module src.tau_translator_omega.core_engine.grammar_processing
==============================================================
TGF Grammar Domain Logic
========================

This module contains the core domain logic for processing TGF (Tau Grammar
Format) data. It is responsible for parsing grammar content and converting it
into a format usable by the translation engine's parser (e.g., Lark).

This module is intentionally pure and has no knowledge of the file system.
All I/O operations are handled by an injected `GrammarRepository` from the
infrastructure layer, following the Functional Core, Imperative Shell pattern.

Classes
-------

`LoadedGrammar(filename: str, original_name: str, type: str, content: str, is_active: bool, rules: Dict[str, Any] = <factory>, terminals: List[str] = <factory>, non_terminals: List[str] = <factory>, directives: List[Tuple[str, str]] = <factory>)`
:   Represents a loaded grammar with its metadata and content.

    ### Instance variables

    `content: str`
    :

    `directives: List[Tuple[str, str]]`
    :

    `filename: str`
    :

    `is_active: bool`
    :

    `non_terminals: List[str]`
    :

    `original_name: str`
    :

    `rules: Dict[str, Any]`
    :

    `terminals: List[str]`
    :

    `type: str`
    :

`TGFGrammarConverter()`
:   Contains pure static methods for converting grammar formats.

    ### Static methods

    `to_lark_grammar(grammar: src.tau_translator_omega.core_engine.grammar_processing.LoadedGrammar) ‑> Tuple[str, str]`
    :   Convert loaded TGF grammar to Lark format for the parser

`TGFGrammarParser()`
:   Contains pure static methods for parsing TGF grammar content.

    ### Class variables

    `KNOWN_OPERATORS`
    :

    ### Static methods

    `parse_tgf_content(content: str) ‑> Tuple[Dict[str, Any], List[str], List[str], List[Tuple[str, str]]]`
    :   Parse TGF content to extract rules, terminals, non-terminals, and directives.

`TGFGrammarService(repository: src.tau_translator_omega.infrastructure.grammar_io.GrammarRepository)`
:   Orchestrates grammar loading and processing using a repository for I/O.
    This acts as an application service.

    ### Methods

    `get_grammar_for_parser(self) ‑> Tuple[str, str] | None`
    :   Gets the active grammar in a format suitable for the parser (Lark).

    `load_and_parse_all_grammars(self) ‑> returns.result.Result[None, str]`
    :   Loads all grammars specified in the config, reads their content,
        and parses them.

    `set_active_grammar(self, filename: str) ‑> returns.result.Result[None, str]`
    :   Sets a grammar as active and persists the change via the repository.