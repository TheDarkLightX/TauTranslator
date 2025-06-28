Module src.tau_translator_omega.core_engine.parsers.grammar_driven_parser
=========================================================================
Grammar-Driven Parser for Dynamic Tau Translation
=================================================

This module implements a parser that uses user-provided grammar files
to perform translation between Tau and natural language.

Author: DarkLightX / Dana Edwards

Functions
---------

`demonstrate_grammar_driven_parser()`
:   Demonstrate the grammar-driven parser

Classes
-------

`GrammarDrivenParser(grammar_service: src.tau_translator_omega.core_engine.grammar_processing.TGFGrammarService | None = None)`
:   Parser that uses dynamically loaded grammars for translation.
    
    This parser can adapt to different Tau dialects or language variations
    by loading different grammar files.

    ### Methods

    `get_available_grammars(self) ‑> List[str]`
    :   Get list of available grammar files

    `get_grammar_info(self) ‑> Dict[str, Any] | None`
    :   Get information about current grammar

    `parse(self, text: str, mode: src.tau_translator_omega.core_engine.parsers.grammar_driven_parser.TranslationMode = TranslationMode.TAU_TO_NATURAL) ‑> src.tau_translator_omega.core_engine.parsers.grammar_driven_parser.ParseResult`
    :   Parse text using current grammar

    `set_grammar(self, grammar: src.tau_translator_omega.core_engine.grammar_processing.LoadedGrammar) ‑> bool`
    :   Set the grammar to use for parsing

    `switch_grammar(self, filename: str) ‑> bool`
    :   Switch to a different grammar

    `translate(self, text: str, source_lang: str, target_lang: str) ‑> Tuple[bool, str]`
    :   High-level translation interface

    `validate_grammar(self, grammar_content: str) ‑> Tuple[bool, str | None]`
    :   Validate a grammar without loading it

`GrammarDrivenTransformer(grammar: src.tau_translator_omega.core_engine.grammar_processing.LoadedGrammar, mode: src.tau_translator_omega.core_engine.parsers.grammar_driven_parser.TranslationMode)`
:   Transforms parse trees based on loaded grammar rules

    ### Ancestors (in MRO)

    * lark.visitors.Transformer
    * lark.visitors._Decoratable
    * abc.ABC
    * typing.Generic

    ### Methods

    `transform_tree(self, tree: lark.tree.Tree) ‑> str`
    :   Transform a parse tree into target format

`GrammarDrivenTranslationStrategy()`
:   Translation strategy that uses grammar-driven parsing.
    
    This can be used as an alternative to pattern-based translation
    when a formal grammar is available.

    ### Ancestors (in MRO)

    * src.tau_translator_omega.lmql_engine.translation_strategies.TranslationStrategy
    * abc.ABC

    ### Methods

    `get_availability_reason(self) ‑> str`
    :   Returns a string explaining why the strategy is not available, if applicable.

    `is_available(self) ‑> bool`
    :   Check if grammar-driven translation is available.

    `translate(self, source_text: str, source_lang: str = 'tau', target_lang: str = 'english') ‑> Dict[str, Any]`
    :   Translate using grammar-driven approach

`ParseResult(success: bool, ast: lark.tree.Tree | None = None, error: str | None = None, warnings: List[str] = None)`
:   Result of grammar-driven parsing

    ### Instance variables

    `ast: lark.tree.Tree | None`
    :

    `error: str | None`
    :

    `success: bool`
    :

    `warnings: List[str]`
    :

`TranslationMode(*args, **kwds)`
:   Direction of translation

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `NATURAL_TO_TAU`
    :

    `TAU_TO_NATURAL`
    :

`TranslationRule(rule_name: str, pattern: str, template: str, variables: List[str], priority: int = 0)`
:   Rule for translating between parse tree and natural language

    ### Instance variables

    `pattern: str`
    :

    `priority: int`
    :

    `rule_name: str`
    :

    `template: str`
    :

    `variables: List[str]`
    :