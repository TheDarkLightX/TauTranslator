Module src.tau_translator_omega.core_engine.parsers.parser_refactored
=====================================================================
Grammar-driven parser following the Intentional Disclosure Principle.

Main API that composes all parser modules into a cohesive parser.
All methods under 10 lines with single responsibility.

Copyright: DarkLightX / Dana Edwards

Classes
-------

`GrammarDrivenParser(grammar_plugin)`
:   Parses source code using a grammar definition provided by a plugin
    and transforms the resulting CST into a project-specific AST.
    
    Initialize parser with a loaded grammar plugin.

    ### Methods

    `parse(self, source_code: str) ‑> Any`
    :   Parse source code and return AST or CST.

    `transform(self, cst: lark.tree.Tree) ‑> Any`
    :   Transform CST to AST using loaded transformer.