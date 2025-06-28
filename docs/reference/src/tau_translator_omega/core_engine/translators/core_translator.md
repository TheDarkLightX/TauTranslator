Module src.tau_translator_omega.core_engine.translators.core_translator
=======================================================================
Core TCE to TAU Translator
==========================

Core implementation for TCE to TAU translation with BDD testing support.

Classes
-------

`CoreAST(text: str, language: str)`
:   Core Abstract Syntax Tree representation.

`CoreParser()`
:   Core parser for TCE and TAU input.

    ### Methods

    `parse(self, text: str, language: str = 'TCE') ‑> SimpleAST`
    :   Parse TCE or TAU text into AST.

`CoreSemanticAnalyzer(vocabulary: Dict[str, Any] | None = None)`
:   Core semantic analyzer for TCE/TAU validation.

    ### Methods

    `analyze(self, ast: src.tau_translator_omega.core_engine.translators.core_translator.CoreAST) ‑> tuple[src.tau_translator_omega.core_engine.translators.core_translator.CoreAST, list]`
    :   Analyze AST and return analyzed AST with errors.

`TCEToTauTranslator()`
:   Bidirectional translator between TCE and TAU.
    
    Initializes the translator with a parser and semantic analyzer.

    ### Methods

    `translate_nl_to_tau(self, nl_text: str) ‑> str`
    :   Public method to translate a Natural Language string to a TAU string.

    `translate_to_tau(self, text: str) ‑> str`
    :   Public method to translate a TCE string to a TAU string.
        This method handles parsing and then delegates to the AST translator.

    `translate_to_tce(self, ast: src.tau_translator_omega.core_engine.translators.core_translator.CoreAST) ‑> str`
    :   Translate AST to TCE.