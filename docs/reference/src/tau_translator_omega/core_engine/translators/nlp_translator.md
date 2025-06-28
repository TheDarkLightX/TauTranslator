Module src.tau_translator_omega.core_engine.translators.nlp_translator
======================================================================
Natural Language Processing Translator
======================================

Handles translation between natural language, TCE, and TAU formats.

Classes
-------

`NLPPatternMatcher(vocabulary: Dict[str, Any] | None = None)`
:   Pattern matching for natural language to formal logic conversion.

    ### Methods

    `match_pattern(self, text: str) ‑> Tuple[str, str, re.Match] | None`
    :   Match text against known patterns.

`NaturalLanguageTranslator(vocabulary: Dict[str, Any] | None = None)`
:   Translator for natural language to TCE/TAU.

    ### Methods

    `translate_to_natural(self, tce_text: str) ‑> str`
    :   Translate TCE back to natural language.

    `translate_to_tce(self, nl_text: str) ‑> str`
    :   Translate natural language to TCE.

`TCEToTauNLPTranslator(vocabulary: Dict[str, Any] | None = None)`
:   Enhanced TCE to TAU translator with NLP support.

    ### Methods

    `translate_nl_to_tau(self, nl_text: str) ‑> str`
    :   Translate natural language directly to TAU.

    `translate_tce_to_tau(self, tce_text: str) ‑> str`
    :   Enhanced TCE to TAU translation with logic symbols.